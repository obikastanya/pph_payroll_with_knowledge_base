@use('App\Support\Format')
@use('App\Payroll\Label')
@php($n = $tampil->jumlahAturan())
<p class="mb-3 max-w-3xl text-sm text-slate-700">
    Mesin inferensi membaca <strong>{{ $n['regulasi'] }} aturan regulasi</strong> dan <strong>{{ $n['perusahaan'] }} aturan kebijakan perusahaan</strong>
    dari berkas knowledge base (YAML), menyusun urutan hitung dari ketergantungan antar-angka, lalu mengevaluasinya (forward chaining).
    Bila kebijakan perusahaan bertentangan dengan aturan wajib, aturan regulasi yang dipakai (<em>lex superior</em>) dan aturan yang
    ditolak tercatat di kolom terakhir. Mengubah aturan berarti mengubah berkas KB, bukan kode aplikasi ini.
</p>
<div class="card max-h-[36rem] overflow-auto">
    <table class="tbl">
        <thead class="sticky top-0"><tr><th>Angka</th><th>Masa</th><th class="text-right">Nilai</th><th>Aturan</th><th>Dasar hukum / kebijakan</th><th>Aturan ditolak</th></tr></thead>
        <tbody>
        @foreach ($tampil->jejak() as $j)
            <tr>
                <td>{{ Label::fakta($j['fakta']) }}</td>
                <td class="whitespace-nowrap">{{ Format::bulan($j['bulan']) }}</td>
                <td class="angka">{{ Format::nilai($j['nilai']) }}</td>
                <td class="whitespace-nowrap">
                    <span class="lencana {{ $j['lapisan'] === 'perusahaan' ? 'bg-violet-100 text-violet-800' : 'bg-sky-100 text-sky-800' }}">{{ $j['aturan'] }}</span>
                </td>
                <td class="text-xs text-slate-600">{{ $j['sumber'] }}</td>
                <td class="text-xs text-red-700">
                    @if ($j['ditolak']){{ implode(', ', $j['ditolak']) }} ({{ implode(', ', $j['alasan']) }})@endif
                </td>
            </tr>
        @endforeach
        </tbody>
    </table>
</div>
