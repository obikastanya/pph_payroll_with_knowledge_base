@use('App\Helpers\Format')
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <title>Slip gaji {{ $payroll->pegawai->nomor_induk }} {{ Format::bulan($bulan, true) }} {{ $payroll->tahun }}</title>
    <link href="{{ asset('assets/css/fonts/fonts.css') }}" rel="stylesheet" />
    <style>
        body { font: 13px/1.45 InterVariable, system-ui, -apple-system, 'Segoe UI', sans-serif; color: #111; margin: 32px auto; max-width: 720px; padding: 0 16px; }
        h1 { font-size: 18px; margin: 0 0 2px; }
        .meta { color: #555; margin-bottom: 18px; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 5px 6px; border-bottom: 1px solid #e5e5e5; vertical-align: top; }
        td.n { text-align: right; white-space: nowrap; font-variant-numeric: tabular-nums; width: 140px; }
        td.d { color: #666; font-size: 11px; width: 200px; }
        tr.judul td { background: #f3f3f3; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: .03em; padding-top: 8px; }
        tr.tebal td { font-weight: 700; }
        .kaki { margin-top: 18px; color: #666; font-size: 11px; }
        .aksi { margin-bottom: 16px; }
        .usang { border: 2px solid #b45309; background: #fef3c7; color: #78350f; padding: 8px 10px; margin-bottom: 14px; font-weight: 600; }
        @media print { .aksi { display: none; } body { margin: 0 auto; } }
    </style>
</head>
<body>
    <div class="aksi"><button onclick="window.print()">Cetak</button></div>
    <h1>Slip gaji · {{ Format::bulan($bulan, true) }} {{ $payroll->tahun }}</h1>
    <div class="meta">
        {{ $payroll->pegawai->nama }} ({{ $payroll->pegawai->nomor_induk }}) · PTKP {{ $payroll->status_ptkp }}
    </div>
    {{-- banner ikut tercetak: slip dari hasil usang tidak boleh terlihat seperti slip final --}}
    @if (($kedaluwarsa ?? null) === 'data')
        <div class="usang" role="status">Hasil usang: data HR berubah sejak perhitungan ini. Hitung ulang sebelum slip dipakai.</div>
    @elseif (($kedaluwarsa ?? null) === 'kb')
        <div class="usang" role="status">Hasil usang: aturan knowledge base berubah sejak perhitungan ini. Hitung ulang sebelum slip dipakai.</div>
    @endif
    <table>
        @foreach ($tampil->slip($bulan) as $r)
            @if ($r['judul'])
                <tr class="judul"><td colspan="3">{{ $r['uraian'] }}</td></tr>
            @else
                <tr class="{{ $r['tebal'] ? 'tebal' : '' }}">
                    <td>{{ $r['uraian'] }}</td>
                    <td class="n">{{ is_int($r['nilai']) ? $r['tanda'].Format::rp($r['nilai'], false) : Format::nilai($r['nilai']) }}</td>
                    <td class="d">{{ $r['dasar']['pendek'] ?? '' }}</td>
                </tr>
            @endif
        @endforeach
    </table>
    <p class="kaki">
        Dihitung {{ $perhitungan->created_at->format('d/m/Y H:i') }} oleh engine knowledge base {{ $perhitungan->versi_engine }}
        (KB {{ $perhitungan->versiKbRingkas() }}@if ($perhitungan->sidik_kb) + berkas KB tambahan {{ $perhitungan->sidik_kb }}@endif). Kolom kanan menunjukkan aturan KB yang menghasilkan angka.
    </p>
</body>
</html>
