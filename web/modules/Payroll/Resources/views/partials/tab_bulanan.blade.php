@use('App\Helpers\Format')
@php($b = $tampil->bulanan())
<div class="row g-2">
    <div class="col-12">
        <div class="card mdka-border-gray-200">
            <div class="card-body p-3">
                <h4 class="mb-2">PPh 21 per bulan</h4>
                <div id="grafikPph" style="min-height: 280px"></div>
                <p class="text-muted small mb-0">Masa pajak terakhir menghitung ulang setahun dengan tarif Pasal 17, sehingga nilainya bisa jauh berbeda (negatif = lebih bayar).</p>
            </div>
        </div>
    </div>
    <div class="col-12">
        <div class="card overflow-hidden mdka-border-gray-200">
            <div class="card-body table-responsive p-0">
                <table class="table table-vcenter mb-0 text-nowrap">
                    <thead>
                        <tr class="mdka-bg-gray-50">
                            <th class="py-3">Bulan</th>
                            <th class="py-3 text-end">Bruto</th>
                            <th class="py-3">TER</th>
                            <th class="py-3 text-end">PPh 21</th>
                            @if ($b['dtp'])<th class="py-3 text-end">DTP</th>@endif
                            @if ($b['tunjangan_pajak'])<th class="py-3 text-end">Tunjangan pajak</th>@endif
                            <th class="py-3 text-end">Take home pay</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($b['baris'] as $r)
                            <tr>
                                <td class="fw-medium">{{ Format::bulan($r['bulan'], true) }}</td>
                                <td class="angka">{{ Format::rp($r['bruto'], false) }}</td>
                                <td class="text-muted">{{ $r['ter'] }}</td>
                                <td class="angka fw-bold">{{ Format::rp($r['pph21'], false) }}</td>
                                @if ($b['dtp'])<td class="angka">{{ Format::rp($r['dtp'], false) }}</td>@endif
                                @if ($b['tunjangan_pajak'])<td class="angka">{{ Format::rp($r['tunjangan_pajak'], false) }}</td>@endif
                                <td class="angka">{{ Format::rp($r['thp'], false) }}</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

@push('javascript')
    <script src="{{ asset('assets/libs/apexcharts/apexcharts.min.js') }}"></script>
    <script>
        $(function() {
            const baris = @json($b['baris']);
            const namaBulan = @json(Format::BULAN);
            const seri = [{
                name: 'PPh 21',
                data: baris.map(r => r.pph21 ?? 0)
            }];
            @if ($b['dtp'])
                seri.push({
                    name: 'Ditanggung pemerintah',
                    data: baris.map(r => r.dtp ?? 0)
                });
            @endif
            new ApexCharts(document.querySelector('#grafikPph'), {
                chart: {
                    type: 'bar',
                    height: 280,
                    toolbar: {
                        show: false
                    },
                    fontFamily: 'inherit',
                    stacked: seri.length > 1
                },
                series: seri,
                colors: ['#3b82f6', '#f97316'],
                plotOptions: {
                    bar: {
                        borderRadius: 4,
                        columnWidth: '55%'
                    }
                },
                dataLabels: {
                    enabled: false
                },
                xaxis: {
                    categories: baris.map(r => namaBulan[r.bulan])
                },
                yaxis: {
                    labels: {
                        formatter: v => formatRupiah(Math.round(v))
                    }
                },
                tooltip: {
                    y: {
                        formatter: v => formatRupiah(v, true)
                    }
                },
                grid: {
                    strokeDashArray: 4
                },
                legend: {
                    position: 'top',
                    horizontalAlign: 'right'
                },
            }).render();
        });
    </script>
@endpush
