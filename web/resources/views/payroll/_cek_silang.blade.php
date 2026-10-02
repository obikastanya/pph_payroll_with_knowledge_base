@use('App\Support\Format')
@use('App\Payroll\Label')
@php($selisih = $p->selisihCekSilang())
@switch($p->cek_silang)
    @case('identik')
        <div class="mb-4 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
            <strong>Cek silang:</strong> kalkulator independen tanpa knowledge base memberi hasil <strong>identik sampai rupiah</strong>.
        </div>
        @break
    @case('sah_titik_tetap_ganda')
        <div class="mb-4 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            <strong>Cek silang:</strong> kalkulator tanpa KB berbeda di {{ count($selisih) }} angka, tetapi <strong>keduanya sah</strong>:
            gross-up di sini punya lebih dari satu tunjangan pajak yang memenuhi persamaan (adjudikasi A-02). Engine KB memilih yang terkecil.
        </div>
        @break
    @case('berbeda')
        <div class="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800" role="alert">
            <strong>Cek silang: hasil berbeda dari kalkulator tanpa KB.</strong> Jangan dipakai sebelum diperiksa.
            <ul class="mt-1 list-disc pl-5">
                @foreach (array_slice($selisih, 0, 5) as $s)
                    <li>{{ Label::fakta($s['fakta']) }} {{ Format::bulan($s['bulan'], true) }}: {{ Format::nilai($s['kb']) }} vs {{ Format::nilai($s['tanpa_kb']) }}</li>
                @endforeach
            </ul>
        </div>
        @break
    @case('galat')
        <div class="mb-4 rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <strong>Cek silang tidak dapat dijalankan</strong> untuk isian ini; hasil engine KB tetap ditampilkan.
        </div>
        @break
@endswitch
