<?php

namespace Modules\Dashboard\Http\Controllers;

use App\Http\Controllers\Controller;
use App\Models\Payroll\PayrollTahun;
use Exception;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Modules\Payroll\Repositories\PayrollInterface;
use Modules\Payroll\Services\HitungTerhenti;
use Modules\Payroll\Services\KunciHitungSemua;
use Modules\Payroll\Services\Penghitung;
use Symfony\Component\HttpFoundation\StreamedResponse;

/** Rekap payroll satu tahun pajak: ringkasan, tabel pegawai (AJAX), hitung semua, ekspor CSV. */
class DashboardController extends Controller
{
    /** Kolom status rekap CSV. */
    public const STATUS_CSV = ['berhasil' => 'berhasil', 'usang_data' => 'usang (data)', 'usang_kb' => 'usang (aturan KB)',
        'galat' => 'galat', 'belum' => 'belum'];

    protected $pageTitle;

    protected $menuItems;

    public function __construct(private PayrollInterface $payroll)
    {
        $this->pageTitle = 'Dashboard';
        $this->menuItems = [
            ['url' => '/', 'label' => 'Home', 'active' => false],
            ['url' => '/dashboard', 'label' => 'Dashboard', 'active' => true],
        ];
    }

    /** ?tahun yang tidak sah jatuh ke tahun terbaru yang punya data HR (angka liar tidak pernah sampai ke query). */
    private function tahun(Request $request): int
    {
        return self::tahunSah($request->query('tahun', $request->input('tahun')))
            ?? $this->payroll->tahunAda()[0] ?? config('payroll.tahun_max');
    }

    /** Bilangan bulat di rentang tahun pajak yang dibuka (payroll.tahun_min..tahun_max), selain itu null. */
    private static function tahunSah(mixed $tahun): ?int
    {
        $t = filter_var($tahun, FILTER_VALIDATE_INT,
            ['options' => ['min_range' => config('payroll.tahun_min'), 'max_range' => config('payroll.tahun_max')]]);

        return $t === false ? null : $t;
    }

    /**
     * Status hasil terakhir satu baris: belum | galat | berhasil | usang_data | usang_kb. alasanKedaluwarsa menyusun
     * ulang kasus (mahal), jadi dipanggil sekali per baris.
     */
    private static function status(PayrollTahun $pt, Penghitung $penghitung): string
    {
        $p = $pt->perhitunganTerakhir;
        if ($p === null) {
            return 'belum';
        }
        if (! $p->berhasil) {
            return 'galat';
        }

        return match ($penghitung->alasanKedaluwarsa($pt, $p)) {
            'data' => 'usang_data',
            'kb' => 'usang_kb',
            default => 'berhasil',
        };
    }

    public function index(Request $request, Penghitung $penghitung): View
    {
        $tahun = $this->tahun($request);
        $daftar = $this->payroll->daftarTahun($tahun);
        $berhasil = $daftar->map->perhitunganTerakhir->filter(fn ($p) => $p?->berhasil);
        $status = $daftar->map(fn (PayrollTahun $pt) => self::status($pt, $penghitung));

        try {
            return view('Dashboard::index', [
                'pageTitle' => $this->pageTitle,
                'menuItems' => $this->menuItems,
                'tahun' => $tahun,
                'tahunAda' => collect($this->payroll->tahunAda())->push($tahun)->unique()->sortDesc()->values()->all(),
                'jumlah' => $daftar->count(),
                // hasil usang ikut dihitung: angkanya tidak lagi mengikuti data HR / aturan KB sekarang
                'belumDihitung' => $status->filter(fn (string $s) => $s !== 'berhasil')->count(),
                'usang' => $status->filter(fn (string $s) => str_starts_with($s, 'usang_'))->count(),
                'ukuranBatch' => $penghitung->ukuranBatch(),
                'total' => [
                    'bruto' => $berhasil->sum('bruto_setahun'),
                    'pph21' => $berhasil->sum('pph21_setahun'),
                    'thp' => $berhasil->sum('thp_setahun'),
                ],
            ]);
        } catch (Exception $e) {
            throw $e;
        }
    }

    public function list(Request $request, Penghitung $penghitung): JsonResponse
    {
        $daftar = $this->payroll->daftarTahun($this->tahun($request), $request->get('search'));
        $perHalaman = min(max((int) $request->get('paginated', 10), 1), 100);
        $halaman = max((int) $request->get('page', 1), 1);
        $total = $daftar->count();
        $potong = $daftar->forPage($halaman, $perHalaman)->values();

        $data = $potong->map(function (PayrollTahun $pt) use ($penghitung) {
            $p = $pt->perhitunganTerakhir;
            $status = self::status($pt, $penghitung);

            return [
                'id' => $pt->id,
                'nomor_induk' => $pt->pegawai->nomor_induk,
                'nama' => $pt->pegawai->nama,
                'status_ptkp' => $pt->status_ptkp,
                'metode' => $pt->metode,
                'bruto_setahun' => $p?->berhasil ? $p->bruto_setahun : null,
                'pph21_setahun' => $p?->berhasil ? $p->pph21_setahun : null,
                'thp_setahun' => $p?->berhasil ? $p->thp_setahun : null,
                'cek_silang' => $p?->cek_silang,
                'status' => str_starts_with($status, 'usang_') ? 'kedaluwarsa' : $status,
                'alasan' => match ($status) {
                    'usang_data' => 'data',
                    'usang_kb' => 'kb',
                    default => null,
                },
                'pesan' => $p?->berhasil === false ? $p->pesan : null,
                'dihitung' => $p?->created_at?->format('d/m/Y H:i'),
                'url' => route('payroll.show', $pt),
            ];
        });

        return response()->json([
            'data' => $data,
            'meta' => [
                'current_page' => $halaman,
                'from' => $total ? ($halaman - 1) * $perHalaman + 1 : null,
                'last_page' => max((int) ceil($total / $perHalaman), 1),
                'per_page' => $perHalaman,
                'to' => $total ? ($halaman - 1) * $perHalaman + $potong->count() : null,
                'total' => $total,
            ],
        ]);
    }

    /**
     * Hitung semua per batch (Penghitung::hitungSemua). Bila engine gagal di tengah jalan, batch yang sudah selesai tetap
     * tercatat dan pesannya menyebut berapa pegawai yang sudah dihitung. Satu tahun pajak hanya dihitung oleh satu proses
     * pada satu waktu (KunciHitungSemua); permintaan kedua ditolak tanpa memanggil engine.
     */
    public function hitung(Request $request, Penghitung $penghitung): RedirectResponse
    {
        $tahun = self::tahunSah($request->input('tahun'));
        if ($tahun === null) {
            return back()->with('error', 'Tahun pajak tidak valid (pilih '.config('payroll.tahun_min').'–'.config('payroll.tahun_max').').');
        }
        $jumlah = $this->payroll->jumlahTahun($tahun);
        if ($jumlah === 0) {
            return back()->with('warning', "Belum ada data HR untuk tahun {$tahun}.");
        }
        $kunci = KunciHitungSemua::ambil($tahun);
        if ($kunci === null) {
            return back()->with('warning', KunciHitungSemua::pesanTerkunci($tahun));
        }
        try {
            $hasil = $penghitung->hitungSemua($this->payroll->daftarHitung($tahun, $penghitung->ukuranBatch()), $request->user(),
                fn () => $kunci->perpanjang());
        } catch (HitungTerhenti $e) {
            return back()->with('error', ($e->dicatat > 0 ? "Engine gagal setelah {$e->dicatat} dari {$jumlah} pegawai dihitung: "
                : 'Engine tidak dapat dipanggil: ').$e->getMessage());
        } finally {
            $kunci->lepas();
        }
        $pesan = "{$hasil['dihitung']} pegawai dihitung.";

        return $hasil['gagal']
            ? back()->with('warning', $pesan.' '.$hasil['gagal'].' gagal; lihat kolom status.')
            : back()->with('success', $pesan.' Semua berhasil.');
    }

    public function ekspor(Request $request, Penghitung $penghitung): StreamedResponse
    {
        $tahun = $this->tahun($request);
        $daftar = $this->payroll->daftarTahun($tahun);
        // status dihitung sebelum streaming: galat engine/DB tidak boleh terjadi di tengah unduhan
        $status = $daftar->map(fn (PayrollTahun $pt) => self::status($pt, $penghitung))->all();

        return response()->streamDownload(function () use ($daftar, $status) {
            $out = fopen('php://output', 'w');
            // kolom lama tetap di posisinya; sidik_kb & pesan ditambahkan di akhir
            fputcsv($out, ['nomor_induk', 'nama', 'tahun', 'status_ptkp', 'metode', 'bruto_setahun', 'pph21_setahun', 'thp_setahun',
                'cek_silang', 'versi_kb', 'dihitung_pada', 'status', 'sidik_kb', 'pesan']);
            foreach ($daftar as $i => $pt) {
                $p = $pt->perhitunganTerakhir;
                fputcsv($out, [self::teks($pt->pegawai->nomor_induk), self::teks($pt->pegawai->nama), $pt->tahun, $pt->status_ptkp,
                    $pt->metode, $p?->bruto_setahun, $p?->pph21_setahun, $p?->thp_setahun, $p?->cek_silang, $p?->versi_kb,
                    $p?->created_at?->toDateTimeString(), self::STATUS_CSV[$status[$i]], $p?->sidik_kb,
                    $p?->berhasil === false ? self::teks((string) $p->pesan) : null]);
            }
            fclose($out);
        }, "rekap_payroll_{$tahun}.csv", ['Content-Type' => 'text/csv; charset=UTF-8']);
    }

    /** Teks bebas isian pengguna: cegah dibaca sebagai rumus oleh spreadsheet (CSV injection). */
    private static function teks(string $s): string
    {
        return preg_match('/^[=+\-@\t\r]/', $s) ? "'".$s : $s;
    }
}
