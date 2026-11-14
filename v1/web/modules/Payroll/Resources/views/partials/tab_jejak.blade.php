@use('App\Helpers\Format')
@use('Modules\Payroll\Services\Label')
@php($n = $tampil->jumlahAturan())
<div class="row g-2 mb-2">
    <div class="col-md-4">
        <x-global.summary-card title="Aturan regulasi dipakai" :value="$n['regulasi']" color="blue" size="sm">
            <x-slot:icon><i class="ti ti-scale"></i></x-slot:icon>
        </x-global.summary-card>
    </div>
    <div class="col-md-4">
        <x-global.summary-card title="Aturan kebijakan perusahaan" :value="$n['perusahaan']" color="purple" size="sm">
            <x-slot:icon><i class="ti ti-building"></i></x-slot:icon>
        </x-global.summary-card>
    </div>
    <div class="col-md-4">
        <x-global.summary-card title="Angka di jejak inferensi" :value="count($tampil->jejak())" color="gray" size="sm">
            <x-slot:icon><i class="ti ti-route"></i></x-slot:icon>
        </x-global.summary-card>
    </div>
</div>
<div class="alert alert-info">
    Mesin inferensi membaca aturan dari berkas knowledge base (YAML), menyusun urutan hitung dari ketergantungan antar-angka, lalu
    mengevaluasinya (<em>forward chaining</em>). Bila kebijakan perusahaan bertentangan dengan aturan wajib, aturan regulasi yang dipakai
    (<em>lex superior</em>) dan aturan yang ditolak tercatat di kolom terakhir, begitu pula aturan lama yang dicabut oleh aturan
    pengganti (<code>menggantikan</code>).
</div>
<div class="card overflow-hidden mdka-border-gray-200">
    <div class="card-body table-responsive p-0" style="max-height: 36rem">
        <table class="table table-vcenter mb-0">
            <thead class="sticky-top">
                <tr class="mdka-bg-gray-50">
                    <th class="py-3">Angka</th>
                    <th class="py-3">Masa</th>
                    <th class="py-3 text-end">Nilai</th>
                    <th class="py-3">Aturan</th>
                    <th class="py-3">Dasar hukum / kebijakan</th>
                    <th class="py-3">Aturan ditolak</th>
                </tr>
            </thead>
            <tbody>
                @foreach ($tampil->jejak() as $j)
                    <tr>
                        <td>{{ $tampil->label($j['fakta']) }}</td>
                        <td class="text-nowrap">{{ Format::bulan($j['bulan']) }}</td>
                        <td class="angka">{{ Format::nilai($j['nilai']) }}</td>
                        <td class="text-nowrap">
                            <span class="badge {{ $j['lapisan'] === 'perusahaan' ? 'mdka-bg-purple-100 mdka-text-purple-600' : 'mdka-bg-blue-100 mdka-text-blue-600' }}">{{ $j['aturan'] }}</span>
                        </td>
                        <td class="text-muted" style="font-size: .7rem">{{ $j['sumber'] }}</td>
                        <td class="mdka-text-red-600" style="font-size: .7rem">
                            @if ($j['ditolak'])
                                {{ implode(', ', $j['ditolak']) }} ({{ implode(', ', $j['alasan']) }})
                            @endif
                            @foreach ($tampil::dicabut($j) as $oleh => $dicabut)
                                <div class="text-muted">Dicabut: {{ implode(', ', $dicabut) }}{{ $oleh !== '' ? ' (oleh '.$oleh.')' : '' }}</div>
                            @endforeach
                        </td>
                    </tr>
                @endforeach
            </tbody>
        </table>
    </div>
</div>
