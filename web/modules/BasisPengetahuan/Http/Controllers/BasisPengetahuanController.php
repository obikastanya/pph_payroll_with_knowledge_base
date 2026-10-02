<?php

namespace Modules\BasisPengetahuan\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Kb\UsulanKb;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\View\View;
use Modules\BasisPengetahuan\Http\Requests\UnggahPeraturanRequest;
use Modules\BasisPengetahuan\Jobs\ProsesUsulanKb;
use Modules\BasisPengetahuan\Repositories\UsulanKbInterface;
use Modules\BasisPengetahuan\Services\PenerapanKb;
use Modules\Payroll\Services\KbTambahan;
use Modules\Payroll\Services\MesinTidakTersedia;
use Symfony\Component\HttpFoundation\StreamedResponse;

/**
 * Basis pengetahuan: unggah peraturan (PDF) -> LLM menyusun rancangan berkas KB -> engine memvalidasi & menyimulasikan
 * -> admin meninjau, mengubah bila perlu, lalu menerapkan. Rumus di kode tidak berubah; aturan baru masuk sebagai
 * berkas KB tambahan, dan isian baru yang dimintanya muncul otomatis di form data HR.
 */
class BasisPengetahuanController extends Controller
{
    protected $pageTitle;

    protected $menuItems;

    public function __construct(private UsulanKbInterface $usulan, private PenerapanKb $penerapan)
    {
        $this->pageTitle = 'Basis pengetahuan';
        $this->menuItems = [
            ['url' => '/dashboard', 'label' => 'Dashboard', 'active' => false],
            ['url' => '/kb', 'label' => 'Basis pengetahuan', 'active' => true],
        ];
    }

    public function index(KbTambahan $kb): View
    {
        return view('BasisPengetahuan::index', [
            'pageTitle' => $this->pageTitle,
            'menuItems' => $this->menuItems,
            'aktif' => $this->usulan->aktif(),
            'sidik' => $kb->sidik(),
            'llmSiap' => (bool) config('payroll.llm_kunci'),
        ]);
    }

    public function list(Request $request): JsonResponse
    {
        $data = $this->usulan->daftar($request->only(['search', 'status', 'lapisan', 'paginated']));

        return response()->json([
            'data' => $data->getCollection()->map(function (UsulanKb $u) {
                [$label, $warna] = $u->labelStatus();

                return [
                    'id' => $u->id,
                    'judul' => $u->judul,
                    'lapisan' => UsulanKb::LAPISAN[$u->lapisan] ?? $u->lapisan,
                    'nama_pdf' => $u->nama_pdf,
                    'status' => $label,
                    'warna' => $warna,
                    'diproses' => $u->sedangDiproses(),
                    'valid' => $u->valid,
                    'aturan' => $u->validasi['ringkasan']['aturan'] ?? null,
                    'masukan' => count($u->validasi['masukan'] ?? []),
                    'dibuat' => $u->created_at->format('d/m/Y H:i'),
                    'oleh' => $u->user?->name ?? '-',
                    'url' => route('kb.show', $u),
                ];
            }),
            'meta' => [
                'current_page' => $data->currentPage(),
                'from' => $data->firstItem(),
                'last_page' => $data->lastPage(),
                'per_page' => $data->perPage(),
                'to' => $data->lastItem(),
                'total' => $data->total(),
            ],
        ]);
    }

    public function store(UnggahPeraturanRequest $request): RedirectResponse
    {
        $pdf = $request->file('pdf');
        $u = $this->usulan->buat([
            'user_id' => $request->user()->id,
            'judul' => $request->validated('judul'),
            'lapisan' => $request->validated('lapisan'),
            'catatan' => $request->validated('catatan'),
            'nama_pdf' => mb_substr($pdf->getClientOriginalName(), 0, 250),
            'path_pdf' => $pdf->store('kb_usulan', 'local'),
            'ukuran_pdf' => $pdf->getSize(),
            'status' => 'antre',
        ]);
        ProsesUsulanKb::dispatch($u->id);

        return redirect()->route('kb.show', $u)->with('success', 'PDF diunggah. LLM sedang membaca dokumen; halaman ini diperbarui otomatis.');
    }

    public function show(UsulanKb $usulan): View
    {
        $usulan->load('user', 'penerap');

        return view('BasisPengetahuan::show', [
            'pageTitle' => $this->pageTitle,
            'menuItems' => [...array_map(fn ($m) => ['active' => false] + $m, $this->menuItems),
                ['url' => '#', 'label' => $usulan->judul, 'active' => true]],
            'u' => $usulan,
            'namaBerkas' => $this->penerapan->namaBerkas($usulan),
            'rujukan' => collect($usulan->usulan['rujukan'] ?? [])->groupBy('bagian')->all(),
        ]);
    }

    public function status(UsulanKb $usulan): JsonResponse
    {
        [$label, $warna] = $usulan->labelStatus();

        return response()->json(['status' => $usulan->status, 'label' => $label, 'warna' => $warna, 'selesai' => ! $usulan->sedangDiproses(),
            'menunggu_detik' => $usulan->status === 'antre' ? (int) $usulan->updated_at->diffInSeconds(now()) : 0]);
    }

    public function simpanYaml(Request $request, UsulanKb $usulan): RedirectResponse
    {
        abort_unless($this->bolehUbah($usulan), 409, 'Rancangan ini tidak dapat diubah pada status sekarang.');
        $request->validate(['yaml' => ['required', 'string', 'max:200000']], [], ['yaml' => 'isi berkas KB']);

        return $this->denganMesin(function () use ($request, $usulan) {
            $v = $this->penerapan->validasi($usulan, $request->input('yaml'));

            return back()->with($v['ok'] ? 'success' : 'warning', $v['ok'] ? 'Rancangan disimpan dan lolos validasi engine.'
                : 'Rancangan disimpan, tetapi belum lolos validasi engine ('.count($v['galat']).' galat).');
        });
    }

    public function terapkan(Request $request, UsulanKb $usulan): RedirectResponse
    {
        abort_unless($usulan->status === 'siap_tinjau', 409, 'Hanya rancangan yang menunggu tinjauan yang dapat diterapkan.');

        return $this->denganMesin(function () use ($request, $usulan) {
            $v = $this->penerapan->terapkan($usulan, $request->user());

            return $v['ok']
                ? back()->with('success', "Diterapkan sebagai kb/tambahan/{$usulan->nama_berkas}. Perhitungan berikutnya memakai aturan ini; "
                    .'hasil lama ditandai perlu dihitung ulang.')
                : back()->with('error', 'Tidak diterapkan: rancangan belum lolos validasi engine terhadap KB yang aktif sekarang.');
        });
    }

    public function tolak(UsulanKb $usulan): RedirectResponse
    {
        abort_unless(in_array($usulan->status, ['siap_tinjau', 'tidak_dapat_dikodifikasi', 'gagal'], true), 409);
        $usulan->update(['status' => 'ditolak']);

        return back()->with('success', 'Usulan ditolak. Aturan di dalamnya tidak dipakai engine.');
    }

    public function aktif(Request $request, UsulanKb $usulan): RedirectResponse
    {
        abort_unless($usulan->status === 'diterapkan', 409);

        return $this->denganMesin(function () use ($request, $usulan) {
            if ($usulan->aktif) {
                $this->penerapan->nonaktifkan($usulan);

                return back()->with('success', 'Berkas KB dinonaktifkan; engine tidak lagi memuatnya.');
            }
            $v = $this->penerapan->aktifkan($usulan, $request->user());

            return $v['ok'] ? back()->with('success', 'Berkas KB diaktifkan kembali.')
                : back()->with('error', 'Tidak dapat diaktifkan: bertentangan dengan KB yang aktif sekarang (lihat hasil validasi).');
        }, 'KB tanpa berkas ini tidak dapat dimuat engine (berkas lain mungkin bergantung padanya): ');
    }

    public function ulang(UsulanKb $usulan): RedirectResponse
    {
        abort_unless(in_array($usulan->status, ['gagal', 'ditolak', 'tidak_dapat_dikodifikasi', 'siap_tinjau'], true), 409);
        $usulan->update(['status' => 'antre', 'pesan_galat' => null, 'usulan' => null, 'yaml' => null, 'validasi' => null, 'valid' => null,
            'info_llm' => null]);
        ProsesUsulanKb::dispatch($usulan->id);

        return back()->with('success', 'Dokumen dikirim ulang ke LLM.');
    }

    public function pdf(UsulanKb $usulan): StreamedResponse
    {
        return Storage::disk('local')->download($usulan->path_pdf, $usulan->nama_pdf);
    }

    public function unduh(UsulanKb $usulan): StreamedResponse
    {
        abort_if($usulan->yaml === null, 404);
        $nama = $this->penerapan->namaBerkas($usulan);

        return response()->streamDownload(fn () => print ($usulan->yaml), $nama, ['Content-Type' => 'application/yaml; charset=UTF-8']);
    }

    public function destroy(UsulanKb $usulan): RedirectResponse
    {
        abort_if($usulan->aktif || $usulan->sedangDiproses(), 409, 'Nonaktifkan berkas atau tunggu proses selesai sebelum menghapus.');
        $this->penerapan->hapus($usulan);

        return redirect()->route('kb.index')->with('success', "Usulan \"{$usulan->judul}\" dihapus.");
    }

    public static function bolehUbah(UsulanKb $u): bool
    {
        return ! $u->aktif && $u->yaml !== null && in_array($u->status, ['siap_tinjau', 'diterapkan'], true);
    }

    /** Jalankan aksi yang memanggil engine; galat engine/KB jadi pesan, bukan halaman 500. */
    private function denganMesin(callable $aksi, string $awalan = 'Engine tidak dapat dipanggil: '): RedirectResponse
    {
        try {
            return $aksi();
        } catch (MesinTidakTersedia $e) {
            return back()->with('error', $awalan.$e->getMessage());
        }
    }

    public static function ukuran(int $bita): string
    {
        if ($bita < 1048576) {
            return max(1, intdiv($bita, 1024)).' KB';
        }
        $persepuluh = intdiv($bita * 10, 1048576);

        return intdiv($persepuluh, 10).','.($persepuluh % 10).' MB';
    }
}
