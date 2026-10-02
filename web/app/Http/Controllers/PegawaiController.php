<?php

namespace App\Http\Controllers;

use App\Http\Requests\PegawaiRequest;
use App\Models\Pegawai;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class PegawaiController extends Controller
{
    public function index(Request $request): View
    {
        $cari = trim((string) $request->query('cari'));
        $pegawai = Pegawai::query()
            ->with('payrollTerakhir')
            ->when($cari !== '', fn ($q) => $q->where(fn ($q) => $q->where('nama', 'like', "%{$cari}%")->orWhere('nomor_induk', 'like', "%{$cari}%")))
            ->orderBy('nomor_induk')
            ->paginate(25)
            ->withQueryString();

        return view('pegawai.index', compact('pegawai', 'cari'));
    }

    public function create(): View
    {
        return view('pegawai.form', ['pegawai' => new Pegawai(['jenis_kelamin' => 'L', 'punya_npwp' => true])]);
    }

    public function store(PegawaiRequest $request): RedirectResponse
    {
        $pegawai = Pegawai::create($request->dataPegawai());

        return redirect()->route('pegawai.show', $pegawai)->with('sukses', 'Pegawai ditambahkan. Lanjutkan dengan mengisi data HR per tahun pajak.');
    }

    public function show(Pegawai $pegawai): View
    {
        $pegawai->load('payrollTahun.perhitunganTerakhir');

        return view('pegawai.show', compact('pegawai'));
    }

    public function edit(Pegawai $pegawai): View
    {
        return view('pegawai.form', compact('pegawai'));
    }

    public function update(PegawaiRequest $request, Pegawai $pegawai): RedirectResponse
    {
        $pegawai->update($request->dataPegawai());

        return redirect()->route('pegawai.show', $pegawai)->with('sukses', 'Data pegawai disimpan.');
    }

    public function destroy(Pegawai $pegawai): RedirectResponse
    {
        $pegawai->delete();

        return redirect()->route('pegawai.index')->with('sukses', "Pegawai {$pegawai->nama} dihapus beserta data payroll dan riwayat perhitungannya.");
    }
}
