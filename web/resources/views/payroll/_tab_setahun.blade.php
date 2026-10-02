@use('App\Support\Format')
@php($rows = $tampil->setahun())
@if ($rows === [])
    <div class="card p-6 text-sm text-slate-600">Engine tidak menghasilkan perhitungan setahun untuk kasus ini.</div>
@else
    <div class="card overflow-x-auto">
        <table class="tbl">
            <thead><tr><th class="w-96">Perhitungan setahun (gaya 1721-A1)</th><th class="text-right whitespace-nowrap">Jumlah (Rp)</th><th>Dasar</th></tr></thead>
            <tbody>
            @foreach ($rows as $r)
                <tr class="{{ $r['tebal'] ? 'font-semibold' : '' }} {{ ($r['sub'] ?? false) ? 'text-slate-600' : '' }}">
                    <td class="{{ ($r['sub'] ?? false) ? 'pl-8 text-sm' : '' }}">{{ $r['uraian'] }}</td>
                    <td class="angka">{{ is_int($r['nilai']) ? $r['tanda'].Format::rp($r['nilai'], false) : Format::nilai($r['nilai']) }}</td>
                    <td class="font-normal">@include('payroll._dasar', ['d' => $r['dasar']])</td>
                </tr>
            @endforeach
            </tbody>
        </table>
    </div>
@endif
