@extends('main.index')
@use('App\Helpers\Format')
@use('App\Models\Kb\UsulanKb')
@use('Modules\BasisPengetahuan\Http\Controllers\BasisPengetahuanController')

@php
    [$labelStatus, $warnaStatus] = $u->labelStatus();
    $usulan = $u->usulan ?? [];
    $v = $u->validasi ?? [];
    $isi = $v['isi'] ?? [];
    $bolehUbah = BasisPengetahuanController::bolehUbah($u);
    $berlaku = fn (array $b) => ($b['mulai'] ?? '?').' – '.($b['sampai'] ?? 'seterusnya');
    $tipe = ['rupiah' => 'rupiah', 'bilangan' => 'bilangan bulat', 'persen' => 'persen', 'desimal' => 'desimal', 'tanggal' => 'tanggal',
        'pilihan' => 'pilihan', 'ya_tidak' => 'ya / tidak'];
@endphp

@section('page-title', 'Tinjau usulan KB')

@section('content')
    <div class="row g-2">
        {{-- Identitas & aksi --}}
        <div class="col-12">
            <div class="card">
                <div class="card-body p-3 d-flex flex-wrap justify-content-between align-items-center gap-3">
                    <div class="d-flex align-items-center gap-3">
                        <span class="avatar avatar-md rounded-3 mdka-bg-blue-100 mdka-text-blue-600"><i class="ti ti-file-text fs-2"></i></span>
                        <div>
                            <h3 class="mb-1">{{ $u->judul }}</h3>
                            <div class="d-flex flex-wrap align-items-center gap-2">
                                <span class="status status-{{ $warnaStatus }}" id="statusUsulan">{{ $labelStatus }}</span>
                                <span class="badge mdka-bg-gray-100 mdka-text-gray-700">{{ UsulanKb::LAPISAN[$u->lapisan] ?? $u->lapisan }}</span>
                                <a href="{{ route('kb.pdf', $u) }}" class="small"><i class="ti ti-file-type-pdf me-1"></i>{{ $u->nama_pdf }}
                                    ({{ BasisPengetahuanController::ukuran($u->ukuran_pdf) }})</a>
                                <span class="text-muted small">diunggah {{ $u->created_at->format('d/m/Y H:i') }} oleh {{ $u->user?->name ?? '-' }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                        @if ($u->status === 'siap_tinjau')
                            <form method="POST" action="{{ route('kb.terapkan', $u) }}" data-konfirmasi="Terapkan aturan ini ke knowledge base?"
                                data-konfirmasi-teks="Engine akan memakainya pada perhitungan berikutnya. Pastikan rancangan sudah Anda cocokkan dengan dokumen."
                                data-konfirmasi-tombol="Terapkan">
                                @csrf
                                <x-global.btn-detail label="Terapkan ke KB" color="green" type="submit" :disabled="! $u->valid">
                                    <x-slot:icon><i class="ti ti-check"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </form>
                        @endif
                        @if ($u->status === 'diterapkan')
                            <form method="POST" action="{{ route('kb.aktif', $u) }}" data-proses="Memeriksa…"
                                @if ($u->aktif) data-konfirmasi="Nonaktifkan berkas KB ini?" data-konfirmasi-teks="Engine tidak lagi memuat aturannya; hasil payroll perlu dihitung ulang." data-konfirmasi-ikon="warning" data-konfirmasi-tombol="Nonaktifkan" @endif>
                                @csrf
                                <x-global.btn-detail :label="$u->aktif ? 'Nonaktifkan' : 'Aktifkan kembali'" :color="$u->aktif ? 'orange' : 'green'" outline="true" type="submit">
                                    <x-slot:icon><i class="ti ti-{{ $u->aktif ? 'player-pause' : 'player-play' }}"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </form>
                        @endif
                        @if (in_array($u->status, ['siap_tinjau', 'tidak_dapat_dikodifikasi', 'gagal'], true))
                            <form method="POST" action="{{ route('kb.tolak', $u) }}" data-konfirmasi="Tolak usulan ini?" data-konfirmasi-tombol="Tolak" data-konfirmasi-ikon="warning">
                                @csrf
                                <x-global.btn-detail label="Tolak" color="red" outline="true" type="submit">
                                    <x-slot:icon><i class="ti ti-x"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </form>
                        @endif
                        @if (in_array($u->status, ['gagal', 'ditolak', 'tidak_dapat_dikodifikasi', 'siap_tinjau'], true))
                            <form method="POST" action="{{ route('kb.ulang', $u) }}" data-konfirmasi="Baca ulang dokumen dengan LLM?"
                                data-konfirmasi-teks="Rancangan sekarang (termasuk perubahan Anda) diganti dengan hasil baru." data-konfirmasi-tombol="Baca ulang">
                                @csrf
                                <x-global.btn-detail label="Baca ulang" color="blue" outline="true" type="submit">
                                    <x-slot:icon><i class="ti ti-refresh"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </form>
                        @endif
                        @if (! $u->aktif && ! $u->sedangDiproses())
                            <form method="POST" action="{{ route('kb.destroy', $u) }}" data-konfirmasi="Hapus usulan ini?"
                                data-konfirmasi-teks="PDF dan rancangannya dihapus permanen." data-konfirmasi-ikon="warning" data-konfirmasi-tombol="Hapus">
                                @csrf
                                @method('DELETE')
                                <x-global.btn-detail label="" color="red" outline="true" type="submit" data-bs-toggle="tooltip" data-bs-title="Hapus usulan">
                                    <x-slot:icon><i class="ti ti-trash"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </form>
                        @endif
                    </div>
                </div>
                @if ($u->catatan)
                    <div class="card-footer p-3 text-muted small"><strong>Catatan untuk LLM:</strong> {{ $u->catatan }}</div>
                @endif
            </div>
        </div>

        {{-- Sedang diproses --}}
        @if ($u->sedangDiproses())
            <div class="col-12">
                <div class="card">
                    <div class="empty py-5">
                        <div class="empty-icon"><span class="spinner-border mdka-text-blue-500" role="status"></span></div>
                        <p class="empty-title">LLM sedang membaca dokumen…</p>
                        <p class="empty-subtitle text-muted mb-0">Biasanya 1–5 menit, tergantung panjang dokumen. Halaman ini diperbarui otomatis; Anda boleh meninggalkannya.</p>
                        <p class="text-warning small mt-3 mb-0 d-none" id="petunjukAntrean"><i class="ti ti-alert-triangle me-1"></i>Masih menunggu antrean.
                            Pastikan pekerja antrean berjalan: <code>php artisan queue:work --timeout=960</code></p>
                    </div>
                </div>
            </div>
        @endif

        @if ($u->status === 'gagal')
            <div class="col-12">
                <div class="alert alert-danger mb-0" role="alert">
                    <div class="d-flex gap-2"><i class="ti ti-alert-triangle fs-2"></i>
                        <div><strong>Dokumen gagal dibaca.</strong>
                            <div class="text-wrap" style="white-space: pre-line">{{ $u->pesan_galat }}</div>
                        </div>
                    </div>
                </div>
            </div>
        @endif

        @if ($usulan)
            {{-- Ringkasan LLM --}}
            <div class="col-lg-7">
                <div class="card h-100">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-sparkles me-2 mdka-text-purple-600"></i>Yang dibaca LLM dari dokumen</h4>
                    </div>
                    <div class="card-body p-3">
                        <p class="mb-2">{{ $usulan['ringkasan'] ?? '' }}</p>
                        @if (! ($usulan['dapat_dikodifikasi'] ?? true) || ($usulan['alasan'] ?? '') !== '')
                            <div class="alert {{ ($usulan['dapat_dikodifikasi'] ?? true) ? 'alert-info' : 'alert-warning' }} mb-2">
                                <strong>{{ ($usulan['dapat_dikodifikasi'] ?? true) ? 'Catatan:' : 'Tidak dapat dijadikan aturan KB:' }}</strong> {{ $usulan['alasan'] ?? '' }}
                            </div>
                        @endif
                        @if (! empty($usulan['catatan_peninjau']))
                            <div class="fw-medium mb-1"><i class="ti ti-flag me-1 mdka-text-orange-600"></i>Perlu Anda periksa</div>
                            <ul class="mb-0 ps-3">
                                @foreach ($usulan['catatan_peninjau'] as $c)
                                    <li>{{ $c }}</li>
                                @endforeach
                            </ul>
                        @endif
                    </div>
                    @if ($u->info_llm)
                        <div class="card-footer p-3 text-muted small">
                            Model <code>{{ $u->info_llm['model'] ?? '-' }}</code> · {{ Format::rp($u->info_llm['token_masuk'] ?? 0, false) }} token masuk
                            ({{ Format::rp($u->info_llm['token_cache_baca'] ?? 0, false) }} dari cache) · {{ Format::rp($u->info_llm['token_keluar'] ?? 0, false) }} token keluar
                        </div>
                    @endif
                </div>
            </div>

            {{-- Validasi engine --}}
            <div class="col-lg-5">
                <div class="card h-100">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-shield-check me-2 mdka-text-green-600"></i>Validasi engine</h4>
                    </div>
                    <div class="card-body p-3">
                        @if (! $v)
                            <p class="text-muted mb-0">Tidak ada rancangan untuk divalidasi.</p>
                        @elseif ($v['ok'])
                            <div class="alert alert-success mb-2"><i class="ti ti-checks me-1"></i><strong>Lolos.</strong> Skema, verifikasi statis KB, dan simulasi pegawai contoh berhasil.</div>
                        @else
                            <div class="alert alert-danger mb-2" role="alert"><strong>Belum lolos — tidak dapat diterapkan.</strong>
                                <ul class="mb-0 ps-3">
                                    @foreach ($v['galat'] as $g)
                                        <li class="text-break">{{ $g }}</li>
                                    @endforeach
                                </ul>
                            </div>
                        @endif
                        @foreach ($v['peringatan'] ?? [] as $p)
                            <div class="alert alert-warning mb-2 text-break"><i class="ti ti-alert-triangle me-1"></i>{{ $p }}</div>
                        @endforeach
                        @if ($v)
                            <div class="d-flex flex-wrap gap-1">
                                @foreach (['aturan' => 'aturan', 'komponen' => 'komponen gaji', 'masukan' => 'isian baru', 'parameter' => 'parameter', 'pembulatan' => 'pembulatan'] as $k => $lbl)
                                    @if ($v['ringkasan'][$k] ?? 0)
                                        <span class="badge mdka-bg-gray-100 mdka-text-gray-700">{{ $v['ringkasan'][$k] }} {{ $lbl }}</span>
                                    @endif
                                @endforeach
                            </div>
                            <p class="text-muted small mt-2 mb-0">Validasi memeriksa bentuk dan konsistensi, bukan kebenaran isi terhadap dokumen. Cocokkan tiap aturan dengan kutipan dan halaman PDF-nya.</p>
                        @endif
                    </div>
                </div>
            </div>
        @endif

        {{-- Isian baru --}}
        @if (! empty($v['masukan']))
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3 d-block">
                        <h4 class="card-title mb-1"><i class="ti ti-forms me-2 mdka-text-purple-600"></i>Isian baru di form data HR</h4>
                        <div class="text-muted small">Aturan ini membutuhkan data yang belum ada di aplikasi. Setelah diterapkan, isian berikut muncul otomatis di form data HR pegawai.</div>
                    </div>
                    <div class="card-body table-responsive p-0">
                        <table class="table table-vcenter mb-0">
                            <thead>
                                <tr class="mdka-bg-gray-50">
                                    <th class="py-3">Isian</th><th class="py-3">Tipe</th><th class="py-3">Diisi</th><th class="py-3">Wajib</th>
                                    <th class="py-3">Bawaan</th><th class="py-3">Dipakai aturan</th><th class="py-3">Dasar</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach ($v['masukan'] as $m)
                                    <tr>
                                        <td><span class="fw-medium">{{ $m['label'] }}</span>
                                            <div class="text-muted small font-monospace">{{ $m['kunci'] }}</div>
                                            @if ($m['keterangan'])
                                                <div class="text-muted small">{{ $m['keterangan'] }}</div>
                                            @endif
                                            @unless ($m['dideklarasikan'])
                                                <span class="status status-red">belum dideklarasikan</span>
                                            @endunless
                                        </td>
                                        <td class="text-nowrap">{{ $tipe[$m['tipe']] ?? $m['tipe'] }}@if ($m['pilihan']): {{ implode(', ', $m['pilihan']) }}@endif</td>
                                        <td class="text-nowrap">{{ $m['lingkup'] === 'tahun' ? 'sekali setahun' : 'tiap bulan' }}</td>
                                        <td>{{ $m['wajib'] ? 'ya' : 'tidak' }}</td>
                                        <td class="tabular-nums">{{ $m['bawaan'] === null ? '-' : (is_bool($m['bawaan']) ? ($m['bawaan'] ? 'ya' : 'tidak') : (is_int($m['bawaan']) ? Format::rp($m['bawaan'], false) : $m['bawaan'])) }}</td>
                                        <td class="font-monospace small">{{ implode(', ', $m['aturan']) }}</td>
                                        <td class="small text-muted">{{ $m['sumber'] ?: '-' }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        @endif

        {{-- Aturan --}}
        @if (! empty($isi['aturan']))
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-gavel me-2 mdka-text-blue-500"></i>Aturan yang diusulkan ({{ count($isi['aturan']) }})</h4>
                    </div>
                    <div class="card-body table-responsive p-0">
                        <table class="table table-vcenter mb-0">
                            <thead>
                                <tr class="mdka-bg-gray-50">
                                    <th class="py-3">Aturan</th><th class="py-3">Menghasilkan</th><th class="py-3">Rumus</th><th class="py-3">Dasar di dokumen</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach ($isi['aturan'] as $a)
                                    <tr>
                                        <td class="text-nowrap align-top">
                                            <span class="font-monospace fw-medium">{{ $a['id'] ?? '?' }}</span>
                                            <div class="text-muted small">{{ $a['sifat'] ?? '' }} · {{ $berlaku($a['berlaku'] ?? []) }}</div>
                                        </td>
                                        <td class="text-nowrap align-top"><span class="font-monospace">{{ $a['menghasilkan'] ?? '?' }}</span>
                                            <div class="text-muted small">per {{ ($a['lingkup'] ?? '') === 'masa' ? 'bulan' : 'tahun' }} · {{ $a['tipe_hasil'] ?? '' }}{{ isset($a['pembulatan']) ? ' · '.$a['pembulatan'] : '' }}</div>
                                        </td>
                                        <td class="align-top">
                                            @isset($a['jika'])
                                                <div class="small text-muted">jika</div>
                                                <code class="d-block text-wrap text-break mb-1">{{ $a['jika'] }}</code>
                                                <div class="small text-muted">maka</div>
                                            @endisset
                                            <code class="d-block text-wrap text-break">{{ $a['maka'] ?? '' }}</code>
                                        </td>
                                        <td class="align-top small" style="min-width: 260px">
                                            {{ $a['sumber'] ?? '' }}
                                            @foreach ($rujukan[$a['id'] ?? ''] ?? [] as $r)
                                                <blockquote class="border-start ps-2 my-1 text-muted">“{{ $r['kutipan'] }}” <span class="text-nowrap">— hlm. {{ $r['halaman'] }}</span></blockquote>
                                            @endforeach
                                            @isset($a['catatan'])
                                                <div class="text-muted">{{ $a['catatan'] }}</div>
                                            @endisset
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        @endif

        {{-- Komponen, parameter, klasifikasi --}}
        @if (! empty($isi['komponen']) || ! empty($isi['parameter']) || ! empty($isi['klasifikasi_wajib']) || ! empty($isi['pembulatan']))
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-adjustments me-2 mdka-text-orange-600"></i>Komponen gaji &amp; parameter</h4>
                    </div>
                    <div class="card-body table-responsive p-0">
                        <table class="table table-vcenter mb-0">
                            <thead>
                                <tr class="mdka-bg-gray-50"><th class="py-3">Jenis</th><th class="py-3">Nama</th><th class="py-3">Isi</th><th class="py-3">Dasar</th></tr>
                            </thead>
                            <tbody>
                                @foreach ($isi['komponen'] ?? [] as $k)
                                    <tr>
                                        <td>Komponen gaji</td>
                                        <td><span class="fw-medium">{{ $k['label'] ?? $k['fakta'] }}</span> <span class="font-monospace text-muted small">{{ $k['fakta'] }}</span></td>
                                        <td>kategori pajak: {{ str_replace('_', ' ', $k['kategori']) }} · jenis {{ $k['jenis'] }}</td>
                                        <td class="small text-muted">-</td>
                                    </tr>
                                @endforeach
                                @foreach ($isi['parameter'] ?? [] as $p)
                                    <tr>
                                        <td>Parameter</td>
                                        <td class="font-monospace">{{ $p['nama'] }}</td>
                                        <td class="tabular-nums">{{ is_int($p['nilai']) ? Format::rp($p['nilai']) : $p['nilai'] }} · {{ $berlaku($p['berlaku'] ?? []) }}</td>
                                        <td class="small">{{ $p['sumber'] ?? '' }}
                                            @foreach ($rujukan[$p['nama']] ?? [] as $r)
                                                <blockquote class="border-start ps-2 my-1 text-muted">“{{ $r['kutipan'] }}” — hlm. {{ $r['halaman'] }}</blockquote>
                                            @endforeach
                                        </td>
                                    </tr>
                                @endforeach
                                @foreach ($isi['klasifikasi_wajib'] ?? [] as $k)
                                    <tr>
                                        <td>Klasifikasi wajib</td>
                                        <td class="font-monospace">{{ $k['jenis'] }}</td>
                                        <td>{{ str_replace('_', ' ', $k['kategori']) }} · {{ $berlaku($k['berlaku'] ?? []) }}</td>
                                        <td class="small">{{ $k['sumber'] ?? '' }}</td>
                                    </tr>
                                @endforeach
                                @foreach ($isi['pembulatan'] ?? [] as $p)
                                    <tr>
                                        <td>Pembulatan</td>
                                        <td class="font-monospace">{{ $p['id'] }}</td>
                                        <td>{{ $p['titik'] ?? '' }} · {{ str_replace('_', ' ', $p['mode'] ?? '') }} ke {{ Format::rp($p['satuan'] ?? 1) }}</td>
                                        <td class="small">{{ $p['dasar'] ?? '' }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        @endif

        {{-- Simulasi dampak --}}
        @if (! empty($v['dampak']))
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3 d-block">
                        <h4 class="card-title mb-1"><i class="ti ti-chart-arrows-vertical me-2 mdka-text-green-600"></i>Simulasi dampak pada pegawai contoh</h4>
                        <div class="text-muted small">Karyawan A (dataset contoh) dihitung dengan KB sekarang dan dengan rancangan ini. Isian baru diisi nilai contoh, bukan data nyata.</div>
                    </div>
                    <div class="card-body table-responsive p-0">
                        <table class="table table-vcenter mb-0 text-nowrap">
                            <thead>
                                <tr class="mdka-bg-gray-50">
                                    <th class="py-3">Tahun</th><th class="py-3">Nilai contoh</th><th class="py-3">Hasil aturan baru (setahun)</th>
                                    <th class="py-3 text-end">Bruto</th><th class="py-3 text-end">PPh 21</th><th class="py-3 text-end">Take home pay</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach ($v['dampak'] as $d)
                                    <tr>
                                        <td class="fw-medium">{{ $d['tahun'] }}</td>
                                        <td class="small">
                                            @forelse ($d['nilai_contoh'] as $k => $n)
                                                <div><span class="font-monospace">{{ $k }}</span> = {{ is_int($n) ? Format::rp($n, false) : (is_bool($n) ? ($n ? 'ya' : 'tidak') : $n) }}</div>
                                            @empty
                                                -
                                            @endforelse
                                        </td>
                                        <td class="small">
                                            @foreach ($d['fakta_baru'] as $f => $n)
                                                <div><span class="font-monospace">{{ $f }}</span> = {{ is_int($n) ? Format::rp($n) : ($n ?? '-') }}</div>
                                            @endforeach
                                        </td>
                                        @foreach (['bruto_setahun', 'pph21_setahun', 'thp_setahun'] as $f)
                                            @php($selisih = ($d['sesudah'][$f] ?? 0) - ($d['sebelum'][$f] ?? 0))
                                            <td class="angka">
                                                {{ Format::rp($d['sesudah'][$f] ?? null, false) }}
                                                <div class="small {{ $selisih === 0 ? 'text-muted' : ($selisih > 0 ? 'text-success' : 'text-danger') }}">
                                                    {{ $selisih === 0 ? 'tetap' : ($selisih > 0 ? '+' : '').Format::rp($selisih, false) }}</div>
                                            </td>
                                        @endforeach
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        @endif

        {{-- Berkas KB (YAML) --}}
        @if ($u->yaml !== null)
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3 d-flex flex-wrap justify-content-between align-items-center gap-2">
                        <div>
                            <h4 class="card-title mb-1"><i class="ti ti-code me-2 mdka-text-gray-600"></i>Berkas KB <span class="font-monospace fw-normal">kb/tambahan/{{ $namaBerkas }}</span></h4>
                            <div class="text-muted small">
                                @if ($bolehUbah)
                                    Boleh Anda ubah sebelum diterapkan; setiap simpan divalidasi ulang oleh engine.
                                @elseif ($u->aktif)
                                    Sedang dimuat engine. Nonaktifkan dulu untuk mengubah.
                                @else
                                    Hanya baca pada status ini.
                                @endif
                            </div>
                        </div>
                        <x-global.btn-detail label="Unduh" color="blue" size="sm" outline="true" href="{{ route('kb.unduh', $u) }}">
                            <x-slot:icon><i class="ti ti-download"></i></x-slot:icon>
                        </x-global.btn-detail>
                    </div>
                    <div class="card-body p-3">
                        <form method="POST" action="{{ route('kb.yaml', $u) }}" data-proses="Memvalidasi…">
                            @csrf
                            @method('PUT')
                            <label for="yaml" class="visually-hidden">Isi berkas KB (YAML)</label>
                            <textarea id="yaml" name="yaml" rows="{{ min(40, max(12, substr_count($u->yaml, "\n") + 2)) }}" spellcheck="false" @readonly(! $bolehUbah)
                                class="form-control font-monospace @error('yaml') is-invalid @enderror" style="font-size: .8rem; white-space: pre; overflow-x: auto">{{ old('yaml', $u->yaml) }}</textarea>
                            @error('yaml')
                                <div class="invalid-feedback">{{ $message }}</div>
                            @enderror
                            @if ($bolehUbah)
                                <div class="d-flex justify-content-end mt-2">
                                    <x-global.btn-detail label="Simpan & validasi ulang" color="blue" type="submit">
                                        <x-slot:icon><i class="ti ti-device-floppy"></i></x-slot:icon>
                                    </x-global.btn-detail>
                                </div>
                            @endif
                        </form>
                    </div>
                    @if ($u->status === 'diterapkan')
                        <div class="card-footer p-3 text-muted small">
                            Diterapkan {{ $u->diterapkan_pada?->format('d/m/Y H:i') }} oleh {{ $u->penerap?->name ?? '-' }}.
                        </div>
                    @endif
                </div>
            </div>
        @endif
    </div>
@endsection

@if ($u->sedangDiproses())
    @push('javascript')
        <script>
            // tunggu LLM selesai, lalu muat ulang halaman untuk menampilkan rancangan
            (function pantau() {
                $.getJSON(@json(route('kb.status', $u)))
                    .done(res => {
                        if (res.selesai) return location.reload();
                        $('#statusUsulan').text(res.label).attr('class', `status status-${res.warna}`);
                        $('#petunjukAntrean').toggleClass('d-none', res.menunggu_detik < 45);
                    })
                    .always(() => setTimeout(pantau, 5000));
            })();
        </script>
    @endpush
@endif
