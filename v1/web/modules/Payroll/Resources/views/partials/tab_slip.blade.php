@use('App\Helpers\Format')
<div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-2">
    <ul class="mdka-nav-btn flex-wrap" aria-label="Pilih bulan">
        @foreach ($tampil->bulan() as $b)
            <li class="mdka-nav-btn-item">
                <a href="{{ route('payroll.show', [$payroll, 'tab' => 'slip', 'bulan' => $b]) }}"
                    class="mdka-nav-btn-link {{ $b === $bulanSlip ? 'active' : '' }}" @if ($b === $bulanSlip) aria-current="page" @endif>{{ Format::bulan($b) }}</a>
            </li>
        @endforeach
    </ul>
    <x-global.btn-detail label="Cetak slip {{ Format::bulan($bulanSlip, true) }}" color="blue" size="sm" outline="true"
        href="{{ route('payroll.slip', [$payroll, $bulanSlip]) }}" target="_blank">
        <x-slot:icon><i class="ti ti-printer"></i></x-slot:icon>
    </x-global.btn-detail>
</div>
<div class="card overflow-hidden mdka-border-gray-200">
    <div class="card-body table-responsive p-0">
        <table class="table table-vcenter mb-0">
            <thead>
                <tr class="mdka-bg-gray-50">
                    <th class="py-3" style="width: 34%">Uraian</th>
                    <th class="py-3 text-end text-nowrap" style="width: 16%">Jumlah (Rp)</th>
                    <th class="py-3">Dasar</th>
                </tr>
            </thead>
            <tbody>
                @foreach ($tampil->slip($bulanSlip) as $r)
                    @if ($r['judul'])
                        <tr class="baris-judul"><td colspan="3">{{ $r['uraian'] }}</td></tr>
                    @else
                        <tr class="{{ $r['tebal'] ? 'fw-bold' : '' }}">
                            <td>{{ $r['uraian'] }}</td>
                            <td class="angka">{{ is_int($r['nilai']) ? $r['tanda'].Format::rp($r['nilai'], false) : Format::nilai($r['nilai']) }}</td>
                            <td class="fw-normal">@include('Payroll::partials.dasar', ['d' => $r['dasar']])</td>
                        </tr>
                    @endif
                @endforeach
            </tbody>
        </table>
    </div>
</div>
<p class="text-muted small mt-2 mb-0">
    Kolom <strong>Dasar</strong> menunjukkan aturan knowledge base yang menghasilkan angka:
    <span class="badge mdka-bg-blue-100 mdka-text-blue-600">Regulasi</span> dari peraturan perpajakan/BPJS,
    <span class="badge mdka-bg-purple-100 mdka-text-purple-600">Perusahaan</span> dari kebijakan perusahaan, beserta pasal sumbernya.
</p>
