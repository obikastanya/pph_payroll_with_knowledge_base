@use('App\Helpers\Format')
@php($rows = $tampil->setahun())
@if ($rows === [])
    <div class="alert alert-info mb-0">Engine tidak menghasilkan perhitungan setahun untuk kasus ini.</div>
@else
    <div class="card overflow-hidden mdka-border-gray-200">
        <div class="card-body table-responsive p-0">
            <table class="table table-vcenter mb-0">
                <thead>
                    <tr class="mdka-bg-gray-50">
                        <th class="py-3" style="width: 40%">Perhitungan setahun (gaya 1721-A1)</th>
                        <th class="py-3 text-end text-nowrap" style="width: 16%">Jumlah (Rp)</th>
                        <th class="py-3">Dasar</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($rows as $r)
                        <tr class="{{ $r['tebal'] ? 'fw-bold' : '' }} {{ ($r['sub'] ?? false) ? 'text-muted' : '' }}">
                            <td class="{{ ($r['sub'] ?? false) ? 'ps-5' : '' }}">{{ $r['uraian'] }}</td>
                            <td class="angka">{{ is_int($r['nilai']) ? $r['tanda'].Format::rp($r['nilai'], false) : Format::nilai($r['nilai']) }}</td>
                            <td class="fw-normal">@include('Payroll::partials.dasar', ['d' => $r['dasar']])</td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>
@endif
