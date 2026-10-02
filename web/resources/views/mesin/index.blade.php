@extends('layouts.app', ['judul' => 'Mesin'])

@section('isi')
    <h1 class="text-2xl font-semibold">Mesin perhitungan</h1>
    <p class="mt-1 mb-5 max-w-3xl text-sm text-slate-500">
        Aplikasi ini tidak menghitung pajak sendiri. Setiap angka dihitung oleh engine knowledge base (Python) di repositori induk,
        dipanggil lewat jembatan JSON. Aturan pajak dan kebijakan perusahaan berada di berkas KB, bukan di kode aplikasi.
    </p>

    @if ($galat)
        <div class="mb-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm whitespace-pre-line text-red-800" role="alert">
            <strong>Engine tidak dapat dipanggil.</strong> {{ $galat }}
        </div>
    @else
        <div class="mb-5 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">Engine siap.</div>
    @endif

    <div class="grid gap-5 lg:grid-cols-2">
        <section class="card p-5">
            <h2 class="mb-3 font-semibold">Konfigurasi</h2>
            <dl class="space-y-2 text-sm">
                @foreach ($konfigurasi as $k => $v)
                    <div><dt class="text-slate-500">{{ $k }}</dt><dd class="font-mono text-xs break-all">{{ $v }}</dd></div>
                @endforeach
            </dl>
            <p class="bantu mt-3">Diatur di <code>web/.env</code>.</p>
        </section>

        @if ($info)
            <section class="card p-5">
                <h2 class="mb-3 font-semibold">Versi knowledge base</h2>
                <dl class="mb-4 grid grid-cols-2 gap-2 text-sm">
                    <div><dt class="text-slate-500">Engine</dt><dd class="font-medium">{{ $info['versi_engine'] }}</dd></div>
                    <div><dt class="text-slate-500">Kebaruan KB</dt><dd class="font-medium">{{ $info['tanggal_kebaruan_kb'] }}</dd></div>
                    <div class="col-span-2"><dt class="text-slate-500">Commit KB</dt><dd class="font-mono text-xs break-all">{{ $info['versi_kb'] }}</dd></div>
                </dl>
                <table class="tbl">
                    <thead><tr><th>Tabel parameter</th><th>Verifikasi</th><th>SHA-256</th></tr></thead>
                    <tbody>
                    @foreach ($info['hash_tabel'] as $tabel => $hash)
                        @php($status = $info['status_verifikasi_tabel'][$tabel] ?? '-')
                        <tr>
                            <td>{{ $tabel }}</td>
                            <td><span class="lencana {{ $status === 'double_entry' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800' }}">{{ str_replace('_', ' ', $status) }}</span></td>
                            <td class="font-mono text-xs text-slate-500">{{ substr($hash, 0, 16) }}…</td>
                        </tr>
                    @endforeach
                    </tbody>
                </table>
                <p class="bantu mt-2">"double entry" = tabel diekstraksi dua kali dari PDF regulasi dan dicocokkan sel per sel.</p>
            </section>
        @endif
    </div>
@endsection
