@use('App\Helpers\Format')
@use('Modules\Payroll\Services\Label')
@php($selisih = $p->selisihCekSilang())
@switch($p->cek_silang)
    @case('identik')
        <div class="alert alert-success mb-0">
            <div class="d-flex gap-2"><i class="ti ti-checks fs-2"></i>
                <div><strong>Cek silang:</strong> kalkulator independen tanpa knowledge base memberi hasil <strong>identik sampai rupiah</strong>.</div>
            </div>
        </div>
    @break

    @case('sah_titik_tetap_ganda')
        <div class="alert alert-info mb-0">
            <div class="d-flex gap-2"><i class="ti ti-arrows-split-2 fs-2"></i>
                <div><strong>Cek silang:</strong> kalkulator tanpa KB berbeda di {{ count($selisih) }} angka, tetapi <strong>keduanya sah</strong>:
                    gross-up di sini punya lebih dari satu tunjangan pajak yang memenuhi persamaan (adjudikasi A-02). Engine KB memilih yang terkecil.</div>
            </div>
        </div>
    @break

    @case('berbeda')
        <div class="alert alert-danger mb-0" role="alert">
            <div class="d-flex gap-2"><i class="ti ti-alert-octagon fs-2"></i>
                <div>
                    <strong>Cek silang: hasil berbeda dari kalkulator tanpa KB.</strong> Jangan dipakai sebelum diperiksa.
                    <ul class="mb-0 ps-3">
                        @foreach (array_slice($selisih, 0, 5) as $s)
                            <li>{{ Label::fakta($s['fakta']) }} {{ Format::bulan($s['bulan'], true) }}: {{ Format::nilai($s['kb']) }} vs {{ Format::nilai($s['tanpa_kb']) }}</li>
                        @endforeach
                    </ul>
                </div>
            </div>
        </div>
    @break

    @case('galat')
        <div class="alert alert-secondary mb-0">
            <strong>Cek silang tidak dapat dijalankan</strong> untuk isian ini; hasil engine KB tetap ditampilkan.
        </div>
    @break
@endswitch
