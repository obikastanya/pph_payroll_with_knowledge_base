@use('App\Support\Format')
@php
    $b = $tampil->bulanan();
    $maks = max(1, ...array_map(fn ($r) => max(0, $r['pph21'] ?? 0) + ($r['dtp'] ?? 0), $b['baris']));
@endphp
<div class="card overflow-x-auto">
    <table class="tbl">
        <thead>
        <tr>
            <th>Bulan</th><th class="text-right">Bruto</th><th>TER</th><th class="text-right">PPh 21</th>
            @if ($b['dtp'])<th class="text-right">DTP</th>@endif
            @if ($b['tunjangan_pajak'])<th class="text-right">Tunjangan pajak</th>@endif
            <th class="text-right">Take home pay</th><th class="w-1/4"><span class="sr-only">Grafik PPh 21</span></th>
        </tr>
        </thead>
        <tbody>
        @foreach ($b['baris'] as $r)
            <tr>
                <td class="font-medium">{{ Format::bulan($r['bulan'], true) }}</td>
                <td class="angka">{{ Format::rp($r['bruto'], false) }}</td>
                <td class="whitespace-nowrap text-slate-600">{{ $r['ter'] }}</td>
                <td class="angka font-medium">{{ Format::rp($r['pph21'], false) }}</td>
                @if ($b['dtp'])<td class="angka">{{ Format::rp($r['dtp'], false) }}</td>@endif
                @if ($b['tunjangan_pajak'])<td class="angka">{{ Format::rp($r['tunjangan_pajak'], false) }}</td>@endif
                <td class="angka">{{ Format::rp($r['thp'], false) }}</td>
                <td class="align-middle">
                    <div class="flex h-3 overflow-hidden rounded-sm bg-slate-100" aria-hidden="true">
                        <div class="bg-blue-600" style="width: {{ intdiv(max(0, $r['pph21'] ?? 0) * 100, $maks) }}%"></div>
                        @if ($b['dtp'])<div class="bg-orange-500" style="width: {{ intdiv(($r['dtp'] ?? 0) * 100, $maks) }}%"></div>@endif
                    </div>
                </td>
            </tr>
        @endforeach
        </tbody>
    </table>
</div>
<p class="mt-2 text-xs text-slate-500">
    Batang biru = PPh 21 dipotong per bulan{{ $b['dtp'] ? '; oranye = PPh 21 ditanggung pemerintah' : '' }}.
    Masa pajak terakhir menghitung ulang setahun dengan tarif Pasal 17, sehingga nilainya bisa berbeda jauh (bahkan negatif = lebih bayar).
</p>
