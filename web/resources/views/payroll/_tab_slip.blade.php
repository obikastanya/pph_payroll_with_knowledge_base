@use('App\Support\Format')
<div class="mb-3 flex flex-wrap items-center justify-between gap-3">
    <div class="flex flex-wrap gap-1" role="group" aria-label="Pilih bulan">
        @foreach ($tampil->bulan() as $b)
            <a href="{{ route('payroll.show', [$payroll, 'tab' => 'slip', 'bulan' => $b]) }}"
               class="rounded-md px-2.5 py-1 text-sm {{ $b === $bulanSlip ? 'bg-blue-700 text-white' : 'bg-white text-slate-700 ring-1 ring-slate-200 hover:bg-slate-50' }}">{{ Format::bulan($b) }}</a>
        @endforeach
    </div>
    <a href="{{ route('payroll.slip', [$payroll, $bulanSlip]) }}" target="_blank" class="btn btn-secondary">Cetak slip {{ Format::bulan($bulanSlip, true) }}</a>
</div>
<div class="card overflow-x-auto">
    <table class="tbl">
        <thead><tr><th class="w-80">Uraian</th><th class="text-right whitespace-nowrap">Jumlah (Rp)</th><th>Dasar</th></tr></thead>
        <tbody>
        @foreach ($tampil->slip($bulanSlip) as $r)
            @if ($r['judul'])
                <tr><td colspan="3" class="bg-slate-50 pt-3 text-xs font-semibold tracking-wide text-slate-600 uppercase">{{ $r['uraian'] }}</td></tr>
            @else
                <tr class="{{ $r['tebal'] ? 'font-semibold' : '' }}">
                    <td>{{ $r['uraian'] }}</td>
                    <td class="angka">{{ is_int($r['nilai']) ? $r['tanda'].Format::rp($r['nilai'], false) : Format::nilai($r['nilai']) }}</td>
                    <td class="font-normal">@include('payroll._dasar', ['d' => $r['dasar']])</td>
                </tr>
            @endif
        @endforeach
        </tbody>
    </table>
</div>
<p class="mt-2 text-xs text-slate-500">
    Kolom <strong>Dasar</strong> menunjukkan aturan di knowledge base yang menghasilkan angka:
    <span class="lencana bg-sky-100 text-sky-800">Regulasi</span> dari peraturan perpajakan/BPJS,
    <span class="lencana bg-violet-100 text-violet-800">Perusahaan</span> dari kebijakan perusahaan, beserta pasal sumbernya.
</p>
