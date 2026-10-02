<?php

namespace Modules\Pegawai\Http\Controllers;

use App\Helpers\Format;
use App\Http\Controllers\Controller;
use App\Models\Payroll\Pegawai;
use Exception;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Modules\Pegawai\Http\Requests\PegawaiRequest;
use Modules\Pegawai\Repositories\PegawaiInterface;

/**
 * Pegawai tetap: halaman daftar (tabel AJAX), endpoint JSON untuk tabel & modal, dan halaman detail per pegawai.
 */
class PegawaiController extends Controller
{
    protected $pageTitle;

    protected $menuItems;

    public function __construct(private PegawaiInterface $pegawai)
    {
        $this->pageTitle = 'Pegawai & data HR';
        $this->menuItems = [
            ['url' => '/dashboard', 'label' => 'Dashboard', 'active' => false],
            ['url' => '/pegawai', 'label' => 'Pegawai', 'active' => true],
        ];
    }

    public function index(): View
    {
        try {
            return view('Pegawai::index', [
                'pageTitle' => $this->pageTitle,
                'menuItems' => $this->menuItems,
            ]);
        } catch (Exception $e) {
            throw $e;
        }
    }

    public function list(Request $request): JsonResponse
    {
        $data = $this->pegawai->daftar($request->only(['search', 'status', 'jenis_kelamin', 'orderBy', 'orderDir', 'paginated']));

        $formatted = $data->getCollection()->map(fn (Pegawai $p) => [
            'id' => $p->id,
            'nomor_induk' => $p->nomor_induk,
            'nama' => $p->nama,
            'jenis_kelamin' => $p->jenis_kelamin,
            'tanggal_masuk' => Format::tanggal($p->tanggal_masuk),
            'tanggal_berhenti' => $p->tanggal_berhenti ? Format::tanggal($p->tanggal_berhenti) : null,
            'berhenti' => $p->tanggal_berhenti?->lt(today()) ?? false,
            'data_hr_terakhir' => $p->payrollTerakhir ? [
                'tahun' => $p->payrollTerakhir->tahun,
                'status_ptkp' => $p->payrollTerakhir->status_ptkp,
                'url' => route('payroll.show', $p->payrollTerakhir),
            ] : null,
            'url_detail' => route('pegawai.detail', $p),
        ]);

        return response()->json([
            'data' => $formatted,
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

    /** Data satu pegawai untuk modal ubah. */
    public function show(Pegawai $pegawai): JsonResponse
    {
        return response()->json([
            'message' => 'Data pegawai berhasil diambil',
            'data' => [
                'id' => $pegawai->id,
                'nomor_induk' => $pegawai->nomor_induk,
                'nama' => $pegawai->nama,
                'jenis_kelamin' => $pegawai->jenis_kelamin,
                'punya_npwp' => $pegawai->punya_npwp,
                'tanggal_masuk' => $pegawai->tanggal_masuk->toDateString(),
                'tanggal_berhenti' => $pegawai->tanggal_berhenti?->toDateString(),
            ],
        ]);
    }

    /** Halaman detail: identitas + data HR per tahun pajak. */
    public function detail(Pegawai $pegawai): View
    {
        $pegawai->load('payrollTahun.perhitunganTerakhir');

        return view('Pegawai::detail', [
            'pageTitle' => $pegawai->nama,
            'menuItems' => [
                ...array_map(fn ($m) => ['active' => false] + $m, $this->menuItems),
                ['url' => '#', 'label' => $pegawai->nama, 'active' => true],
            ],
            'pegawai' => $pegawai,
        ]);
    }

    public function store(PegawaiRequest $request): JsonResponse
    {
        $pegawai = $this->pegawai->simpan($request->dataPegawai());

        return response()->json(['message' => 'Pegawai ditambahkan.', 'data' => ['id' => $pegawai->id, 'url_detail' => route('pegawai.detail', $pegawai)]]);
    }

    public function update(PegawaiRequest $request, Pegawai $pegawai): JsonResponse
    {
        $this->pegawai->simpan($request->dataPegawai(), $pegawai);

        return response()->json(['message' => 'Data pegawai disimpan.']);
    }

    public function destroy(Pegawai $pegawai): JsonResponse
    {
        $this->pegawai->hapus($pegawai);

        return response()->json(['message' => "Pegawai {$pegawai->nama} dihapus beserta data payroll dan riwayat perhitungannya."]);
    }
}
