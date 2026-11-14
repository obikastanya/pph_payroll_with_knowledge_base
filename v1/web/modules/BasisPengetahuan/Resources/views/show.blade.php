@extends('main.index')
@use('App\Helpers\Format')
@use('App\Models\Kb\UsulanKb')
@use('Modules\BasisPengetahuan\Http\Controllers\BasisPengetahuanController')

@php
    // usulan (keluaran LLM) dan validasi (jawaban engine atas YAML yang bisa ditulis admin) bisa berbentuk apa saja:
    // setiap akses bersarang dijaga agar halaman tinjau tidak pernah HTTP 500
    [$labelStatus, $warnaStatus] = $u->labelStatus();
    $teks = fn ($x, string $bawaan = '') => is_scalar($x) ? (is_bool($x) ? ($x ? 'ya' : 'tidak') : (string) $x) : $bawaan;
    $daftar = fn ($x) => is_array($x) ? array_values(array_filter($x, 'is_array')) : [];
    $daftarTeks = fn ($x) => is_array($x) ? array_values(array_map($teks, array_filter($x, 'is_scalar'))) : [];
    $nilai = fn ($x, bool $awalan = false) => $x === null || is_scalar($x) ? Format::rp($x, $awalan) : '?';
    $berlaku = fn ($b = null) => is_array($b) ? $teks($b['mulai'] ?? null, '?').' – '.$teks($b['sampai'] ?? null, 'seterusnya') : '?';
    $usulan = is_array($u->usulan) ? $u->usulan : [];
    $v = is_array($u->validasi) ? $u->validasi : [];
    $lolos = ($v['ok'] ?? false) === true;
    // tabel isi berkas hanya dari validasi yang lolos: isi berkas yang gagal dimuat bisa berbentuk apa pun ({} di kontrak)
    $isi = $lolos && is_array($v['isi'] ?? null) ? $v['isi'] : [];
    $ringkasan = is_array($v['ringkasan'] ?? null) ? $v['ringkasan'] : [];
    $galat = $daftarTeks($v['galat'] ?? []);
    $peringatan = $daftarTeks($v['peringatan'] ?? []);
    $perubahan = $daftar($v['perubahan'] ?? []);
    $belumTeruji = $daftar($v['belum_teruji'] ?? []);
    $masukan = $daftar($v['masukan'] ?? []);
    $dampak = $daftar($v['dampak'] ?? []);
    $perluDiperiksa = count($peringatan) + count($belumTeruji);
    $lapisanBerkas = $teks($ringkasan['lapisan'] ?? null);
    $lapisanBeda = $lapisanBerkas !== '' && $lapisanBerkas !== $u->lapisan;
    $jenisUbah = ['aturan' => 'aturan', 'parameter' => 'parameter', 'klasifikasi' => 'klasifikasi wajib'];
    $ringkasUbah = collect($perubahan)->countBy(fn ($p) => $teks($p['jenis'] ?? null, 'lainnya'))
        ->map(fn ($n, $j) => $n.' '.($jenisUbah[$j] ?? $j))->values()->implode(', ');
    $aturanIsi = $daftar($isi['aturan'] ?? []);
    $komponenIsi = $daftar($isi['komponen'] ?? []);
    $parameterIsi = $daftar($isi['parameter'] ?? []);
    $klasifikasiIsi = $daftar($isi['klasifikasi_wajib'] ?? []);
    $pembulatanIsi = $daftar($isi['pembulatan'] ?? []);
    $infoLlm = is_array($u->info_llm) ? $u->info_llm : [];
    $bolehUbah = BasisPengetahuanController::bolehUbah($u);
    $berjalan = $u->sedangDiproses() ? $u->detikSejakBerubah() : 0;
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
                                @if ($lapisanBeda)
                                    <span class="badge mdka-bg-orange-100 mdka-text-orange-600" data-bs-toggle="tooltip"
                                        data-bs-title="Engine memuat berkas menurut lapisan yang tertulis di dalamnya, bukan menurut pilihan saat unggah.">
                                        <i class="ti ti-alert-triangle me-1"></i>Lapisan di berkas: {{ $lapisanBerkas }} (berbeda dari pilihan unggah)</span>
                                @endif
                                <a href="{{ route('kb.pdf', $u) }}" class="small"><i class="ti ti-file-type-pdf me-1"></i>{{ $u->nama_pdf }}
                                    ({{ BasisPengetahuanController::ukuran($u->ukuran_pdf) }})</a>
                                <span class="text-muted small">diunggah {{ $u->created_at->format('d/m/Y H:i') }} oleh {{ $u->user?->name ?? '-' }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                        @if ($u->status === 'siap_tinjau')
                            <form method="POST" action="{{ route('kb.terapkan', $u) }}" data-konfirmasi="Terapkan aturan ini ke knowledge base?"
                                data-konfirmasi-teks="{{ $perubahan ? 'Rancangan ini mengubah '.count($perubahan).' hal yang sudah ada di KB ('.$ringkasUbah.'). ' : '' }}Engine akan memakainya pada perhitungan berikutnya. Pastikan rancangan sudah Anda cocokkan dengan dokumen."
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
                        @if ($u->status === 'antre')
                            <form method="POST" action="{{ route('kb.destroy', $u) }}" data-konfirmasi="Batalkan unggahan ini?"
                                data-konfirmasi-teks="Dokumen belum dibaca LLM. PDF dan usulannya dihapus." data-konfirmasi-ikon="warning" data-konfirmasi-tombol="Batalkan">
                                @csrf
                                @method('DELETE')
                                <x-global.btn-detail label="Batalkan" color="red" outline="true" type="submit">
                                    <x-slot:icon><i class="ti ti-x"></i></x-slot:icon>
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
                        <p class="text-warning small mt-3 mb-0 {{ $u->status === 'antre' && $berjalan >= 45 ? '' : 'd-none' }}" id="petunjukAntrean">
                            <i class="ti ti-alert-triangle me-1"></i>Masih menunggu antrean. Pastikan pekerja antrean berjalan:
                            <code>php artisan queue:listen --timeout=960</code></p>
                        <p class="text-warning small mt-3 mb-0 {{ $u->status === 'diproses' && $berjalan > 120 ? '' : 'd-none' }}" id="petunjukLama">
                            <i class="ti ti-alert-triangle me-1"></i>Sudah lebih dari 2 menit. Pastikan pekerja antrean masih berjalan
                            (<code>php artisan queue:listen --timeout=960</code>); bila pekerja berhenti, proses ini ditandai gagal setelah batas waktu
                            dan dapat dibaca ulang.</p>
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
            @php($dapat = ($usulan['dapat_dikodifikasi'] ?? true) !== false)
            @php($alasan = $teks($usulan['alasan'] ?? null))
            @php($catatanPeninjau = $daftarTeks($usulan['catatan_peninjau'] ?? []))
            {{-- Ringkasan LLM --}}
            <div class="col-lg-7">
                <div class="card h-100">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-sparkles me-2 mdka-text-purple-600"></i>Yang dibaca LLM dari dokumen</h4>
                    </div>
                    <div class="card-body p-3">
                        <p class="mb-2">{{ $teks($usulan['ringkasan'] ?? null) }}</p>
                        @if (! $dapat || $alasan !== '')
                            <div class="alert {{ $dapat ? 'alert-info' : 'alert-warning' }} mb-2">
                                <strong>{{ $dapat ? 'Catatan:' : 'Tidak dapat dijadikan aturan KB:' }}</strong> {{ $alasan }}
                            </div>
                        @endif
                        @if ($catatanPeninjau)
                            <div class="fw-medium mb-1"><i class="ti ti-flag me-1 mdka-text-orange-600"></i>Perlu Anda periksa</div>
                            <ul class="mb-0 ps-3">
                                @foreach ($catatanPeninjau as $c)
                                    <li>{{ $c }}</li>
                                @endforeach
                            </ul>
                        @endif
                    </div>
                    @if ($infoLlm)
                        <div class="card-footer p-3 text-muted small">
                            Model <code>{{ $teks($infoLlm['model'] ?? null, '-') }}</code> · {{ $nilai($infoLlm['token_masuk'] ?? 0) }} token masuk
                            ({{ $nilai($infoLlm['token_cache_baca'] ?? 0) }} dari cache) · {{ $nilai($infoLlm['token_keluar'] ?? 0) }} token keluar
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
                        @elseif ($lolos && $perluDiperiksa === 0)
                            <div class="alert alert-success mb-2"><i class="ti ti-checks me-1"></i><strong>Lolos.</strong> Skema, verifikasi statis KB, dan simulasi pegawai contoh berhasil.</div>
                        @elseif ($lolos)
                            <div class="alert alert-warning mb-2"><i class="ti ti-alert-triangle me-1"></i><strong>Lolos pemeriksaan bentuk, tetapi ada
                                    {{ $perluDiperiksa }} hal yang perlu diperiksa sebelum menerapkan.</strong></div>
                        @else
                            <div class="alert alert-danger mb-2" role="alert"><strong>Belum lolos — tidak dapat diterapkan.</strong>
                                <ul class="mb-0 ps-3">
                                    @forelse ($galat as $g)
                                        <li class="text-break">{{ $g }}</li>
                                    @empty
                                        <li>engine tidak memberi keterangan</li>
                                    @endforelse
                                </ul>
                            </div>
                        @endif
                        @foreach ($peringatan as $p)
                            <div class="alert alert-warning mb-2 text-break"><i class="ti ti-alert-triangle me-1"></i>{{ $p }}</div>
                        @endforeach
                        @if ($v)
                            <div class="d-flex flex-wrap gap-1">
                                @foreach (['aturan' => 'aturan', 'komponen' => 'komponen gaji', 'masukan' => 'isian baru', 'parameter' => 'parameter', 'pembulatan' => 'pembulatan'] as $k => $lbl)
                                    @if (is_int($ringkasan[$k] ?? null) && $ringkasan[$k] > 0)
                                        <span class="badge mdka-bg-gray-100 mdka-text-gray-700">{{ $ringkasan[$k] }} {{ $lbl }}</span>
                                    @endif
                                @endforeach
                                @if ($lapisanBerkas !== '')
                                    <span class="badge {{ $lapisanBeda ? 'mdka-bg-orange-100 mdka-text-orange-600' : 'mdka-bg-gray-100 mdka-text-gray-700' }}">lapisan {{ $lapisanBerkas }}</span>
                                @endif
                            </div>
                            <p class="text-muted small mt-2 mb-0">Validasi memeriksa bentuk dan konsistensi, bukan kebenaran isi terhadap dokumen. Cocokkan tiap aturan dengan kutipan dan halaman PDF-nya.</p>
                        @endif
                    </div>
                </div>
            </div>
        @endif

        {{-- Yang diubah rancangan ini --}}
        @if ($perubahan || $belumTeruji)
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3 d-block">
                        <h4 class="card-title mb-1"><i class="ti ti-arrows-diff me-2 mdka-text-orange-600"></i>Yang diubah rancangan ini</h4>
                        <div class="text-muted small">Aturan, parameter, atau klasifikasi yang sudah ada di KB dan berubah bila rancangan ini diterapkan.</div>
                    </div>
                    <div class="card-body p-3">
                        @if ($perubahan)
                            <ul class="list-unstyled mb-0">
                                @foreach ($perubahan as $p)
                                    @php($jenisP = $teks($p['jenis'] ?? null, 'lainnya'))
                                    <li class="d-flex gap-2 align-items-start mb-1">
                                        <span class="badge mdka-bg-orange-100 mdka-text-orange-600 text-nowrap">{{ $jenisUbah[$jenisP] ?? $jenisP }}</span>
                                        <span class="text-break">{{ $teks($p['teks'] ?? null, '-') }}</span>
                                    </li>
                                @endforeach
                            </ul>
                        @else
                            <p class="text-muted mb-0">Tidak ada aturan, parameter, atau klasifikasi yang sudah ada yang diubah.</p>
                        @endif
                        @if ($belumTeruji)
                            <div class="fw-medium mt-3 mb-1"><i class="ti ti-flask-off me-1 mdka-text-orange-600"></i>Aturan belum teruji</div>
                            <div class="text-muted small mb-1">Simulasi pegawai contoh tidak menjalankan aturan berikut; periksa rumusnya secara manual.</div>
                            <ul class="mb-0 ps-3">
                                @foreach ($belumTeruji as $b)
                                    <li><span class="font-monospace fw-medium">{{ $teks($b['aturan'] ?? null, '?') }}</span>: {{ $teks($b['alasan'] ?? null, '-') }}</li>
                                @endforeach
                            </ul>
                        @endif
                    </div>
                </div>
            </div>
        @endif

        {{-- Isian baru --}}
        @if ($masukan)
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
                                @foreach ($masukan as $m)
                                    @php($tipeM = $teks($m['tipe'] ?? null))
                                    @php($pilihan = $daftarTeks($m['pilihan'] ?? []))
                                    @php($keterangan = $teks($m['keterangan'] ?? null))
                                    <tr>
                                        <td><span class="fw-medium">{{ $teks($m['label'] ?? null) }}</span>
                                            <div class="text-muted small font-monospace">{{ $teks($m['kunci'] ?? null, '?') }}</div>
                                            @if ($keterangan !== '')
                                                <div class="text-muted small">{{ $keterangan }}</div>
                                            @endif
                                            @if (($m['dideklarasikan'] ?? true) === false)
                                                <span class="status status-red">belum dideklarasikan</span>
                                            @endif
                                        </td>
                                        <td class="text-nowrap">{{ $tipe[$tipeM] ?? $tipeM }}@if ($pilihan): {{ implode(', ', $pilihan) }}@endif</td>
                                        <td class="text-nowrap">{{ ($m['lingkup'] ?? null) === 'tahun' ? 'sekali setahun' : 'tiap bulan' }}</td>
                                        <td>{{ ($m['wajib'] ?? false) === true ? 'ya' : 'tidak' }}</td>
                                        <td class="tabular-nums">{{ $nilai($m['bawaan'] ?? null) }}</td>
                                        <td class="font-monospace small">{{ implode(', ', $daftarTeks($m['aturan'] ?? [])) }}</td>
                                        <td class="small text-muted">{{ $teks($m['sumber'] ?? null) ?: '-' }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        @endif

        {{-- Aturan --}}
        @if ($aturanIsi)
            <div class="col-12">
                <div class="card">
                    <div class="card-header p-3">
                        <h4 class="card-title mb-0"><i class="ti ti-gavel me-2 mdka-text-blue-500"></i>Aturan yang diusulkan ({{ count($aturanIsi) }})</h4>
                    </div>
                    <div class="card-body table-responsive p-0">
                        <table class="table table-vcenter mb-0">
                            <thead>
                                <tr class="mdka-bg-gray-50">
                                    <th class="py-3">Aturan</th><th class="py-3">Menghasilkan</th><th class="py-3">Rumus</th><th class="py-3">Dasar di dokumen</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach ($aturanIsi as $a)
                                    @php($idAturan = $teks($a['id'] ?? null, '?'))
                                    @php($jika = $teks($a['jika'] ?? null))
                                    @php($pembulatanA = $teks($a['pembulatan'] ?? null))
                                    @php($catatanA = $teks($a['catatan'] ?? null))
                                    <tr>
                                        <td class="text-nowrap align-top">
                                            <span class="font-monospace fw-medium">{{ $idAturan }}</span>
                                            <div class="text-muted small">{{ $teks($a['sifat'] ?? null) }} · {{ $berlaku($a['berlaku'] ?? null) }}</div>
                                        </td>
                                        <td class="text-nowrap align-top"><span class="font-monospace">{{ $teks($a['menghasilkan'] ?? null, '?') }}</span>
                                            <div class="text-muted small">per {{ ($a['lingkup'] ?? '') === 'masa' ? 'bulan' : 'tahun' }} · {{ $teks($a['tipe_hasil'] ?? null) }}{{ $pembulatanA !== '' ? ' · '.$pembulatanA : '' }}</div>
                                        </td>
                                        <td class="align-top">
                                            @if ($jika !== '')
                                                <div class="small text-muted">jika</div>
                                                <code class="d-block text-wrap text-break mb-1">{{ $jika }}</code>
                                                <div class="small text-muted">maka</div>
                                            @endif
                                            <code class="d-block text-wrap text-break">{{ $teks($a['maka'] ?? null) }}</code>
                                        </td>
                                        <td class="align-top small" style="min-width: 260px">
                                            {{ $teks($a['sumber'] ?? null) }}
                                            @foreach ($rujukan[$idAturan] ?? [] as $r)
                                                <blockquote class="border-start ps-2 my-1 text-muted">“{{ $teks($r['kutipan'] ?? null) }}” <span class="text-nowrap">— hlm. {{ $teks($r['halaman'] ?? null, '?') }}</span></blockquote>
                                            @endforeach
                                            @if ($catatanA !== '')
                                                <div class="text-muted">{{ $catatanA }}</div>
                                            @endif
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
        @if ($komponenIsi || $parameterIsi || $klasifikasiIsi || $pembulatanIsi)
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
                                @foreach ($komponenIsi as $k)
                                    <tr>
                                        <td>Komponen gaji</td>
                                        <td><span class="fw-medium">{{ $teks($k['label'] ?? null) ?: $teks($k['fakta'] ?? null, '?') }}</span>
                                            <span class="font-monospace text-muted small">{{ $teks($k['fakta'] ?? null) }}</span></td>
                                        <td>kategori pajak: {{ str_replace('_', ' ', $teks($k['kategori'] ?? null, '?')) }} · jenis {{ $teks($k['jenis'] ?? null, '?') }}</td>
                                        <td class="small text-muted">-</td>
                                    </tr>
                                @endforeach
                                @foreach ($parameterIsi as $p)
                                    @php($namaP = $teks($p['nama'] ?? null, '?'))
                                    <tr>
                                        <td>Parameter</td>
                                        <td class="font-monospace">{{ $namaP }}</td>
                                        <td class="tabular-nums">{{ $nilai($p['nilai'] ?? null, true) }} · {{ $berlaku($p['berlaku'] ?? null) }}</td>
                                        <td class="small">{{ $teks($p['sumber'] ?? null) }}
                                            @foreach ($rujukan[$namaP] ?? [] as $r)
                                                <blockquote class="border-start ps-2 my-1 text-muted">“{{ $teks($r['kutipan'] ?? null) }}” — hlm. {{ $teks($r['halaman'] ?? null, '?') }}</blockquote>
                                            @endforeach
                                        </td>
                                    </tr>
                                @endforeach
                                @foreach ($klasifikasiIsi as $k)
                                    <tr>
                                        <td>Klasifikasi wajib</td>
                                        <td class="font-monospace">{{ $teks($k['jenis'] ?? null, '?') }}</td>
                                        <td>{{ str_replace('_', ' ', $teks($k['kategori'] ?? null, '?')) }} · {{ $berlaku($k['berlaku'] ?? null) }}</td>
                                        <td class="small">{{ $teks($k['sumber'] ?? null) }}</td>
                                    </tr>
                                @endforeach
                                @foreach ($pembulatanIsi as $p)
                                    <tr>
                                        <td>Pembulatan</td>
                                        <td class="font-monospace">{{ $teks($p['id'] ?? null, '?') }}</td>
                                        <td>{{ $teks($p['titik'] ?? null) }} · {{ str_replace('_', ' ', $teks($p['mode'] ?? null)) }} ke {{ $nilai($p['satuan'] ?? 1, true) }}</td>
                                        <td class="small">{{ $teks($p['dasar'] ?? null) }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        @endif

        {{-- Simulasi dampak --}}
        @if ($dampak)
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
                                @foreach ($dampak as $d)
                                    @php($sebelum = is_array($d['sebelum'] ?? null) ? $d['sebelum'] : [])
                                    @php($sesudah = is_array($d['sesudah'] ?? null) ? $d['sesudah'] : [])
                                    <tr>
                                        <td class="fw-medium">{{ $teks($d['tahun'] ?? null, '?') }}</td>
                                        <td class="small">
                                            @forelse (is_array($d['nilai_contoh'] ?? null) ? $d['nilai_contoh'] : [] as $k => $n)
                                                <div><span class="font-monospace">{{ $k }}</span> = {{ $nilai($n) }}</div>
                                            @empty
                                                -
                                            @endforelse
                                        </td>
                                        <td class="small">
                                            @foreach (is_array($d['fakta_baru'] ?? null) ? $d['fakta_baru'] : [] as $f => $n)
                                                <div><span class="font-monospace">{{ $f }}</span> = {{ $nilai($n, true) }}</div>
                                            @endforeach
                                        </td>
                                        @foreach (['bruto_setahun', 'pph21_setahun', 'thp_setahun'] as $f)
                                            @php($selisih = is_int($sesudah[$f] ?? null) && is_int($sebelum[$f] ?? null) ? $sesudah[$f] - $sebelum[$f] : null)
                                            <td class="angka">
                                                {{ $nilai($sesudah[$f] ?? null) }}
                                                @if ($selisih !== null)
                                                    <div class="small {{ $selisih === 0 ? 'text-muted' : ($selisih > 0 ? 'text-success' : 'text-danger') }}">
                                                        {{ $selisih === 0 ? 'tetap' : ($selisih > 0 ? '+' : '').Format::rp($selisih, false) }}</div>
                                                @endif
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
                        $('#petunjukAntrean').toggleClass('d-none', res.status !== 'antre' || res.menunggu_detik < 45);
                        $('#petunjukLama').toggleClass('d-none', res.status !== 'diproses' || res.berjalan_detik <= 120);
                    })
                    .always(() => setTimeout(pantau, 5000));
            })();
        </script>
    @endpush
@endif
