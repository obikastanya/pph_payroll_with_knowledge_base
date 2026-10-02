@extends('auth.main.app')
@php
    $slide = [
        ['auth-1', 'Payroll tanpa rumus tersembunyi', 'Gaji, BPJS, THR, dan PPh 21 pegawai tetap dihitung oleh engine knowledge base, bukan rumus di spreadsheet.'],
        ['auth-2', 'Setiap angka punya dasar', 'Slip gaji menunjuk aturan dan pasal sumber untuk setiap angka: regulasi pemerintah atau kebijakan perusahaan.'],
        ['auth-3', 'Konflik kebijakan terdeteksi', 'Aturan pajak dan kebijakan perusahaan dipisah dua lapis; bila bertentangan, aturan wajib yang dipakai.'],
        ['auth-4', 'Dicek silang otomatis', 'Hasil dibandingkan dengan kalkulator independen tanpa knowledge base, sampai rupiah.'],
    ];
@endphp
@section('content')
    <section class="h-100 gradient-form">
        <div class="container py-5 h-100">
            <div class="row d-flex justify-content-center align-items-center h-100">
                <div class="col-xl-10">
                    <div class="card rounded-4 text-black" style="box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.55); border-radius: 20px; overflow: hidden;">
                        <div class="row g-0">
                            <div class="col-lg-7 d-none d-lg-flex align-items-stretch">
                                <div id="carousel-indicators-thumb" class="carousel slide carousel-fade carousel-login w-100" data-bs-ride="carousel"
                                    data-bs-interval="5000">
                                    <div class="carousel-indicators carousel-indicators-thumb">
                                        @foreach ($slide as $i => [$gambar, $judul])
                                            <button type="button" data-bs-target="#carousel-indicators-thumb" data-bs-slide-to="{{ $i }}"
                                                class="ratio ratio-4x3 {{ $i === 0 ? 'active' : '' }}" @if ($i === 0) aria-current="true" @endif
                                                aria-label="{{ $judul }}" style="background-image: url({{ asset("assets/img/bg-auth/{$gambar}-thumb.jpg") }})"></button>
                                        @endforeach
                                    </div>
                                    <div class="carousel-inner h-100">
                                        @foreach ($slide as $i => [$gambar, $judul, $teks])
                                            <div class="carousel-item h-100 {{ $i === 0 ? 'active' : '' }}">
                                                <img class="d-block w-100 h-100" alt="" src="{{ asset("assets/img/bg-auth/{$gambar}.jpg") }}">
                                                <div class="carousel-caption d-none d-md-block">
                                                    <h3 class="text-white mb-1">{{ $judul }}</h3>
                                                    <p class="mb-0 opacity-75">{{ $teks }}</p>
                                                </div>
                                            </div>
                                        @endforeach
                                    </div>
                                </div>
                            </div>
                            <div class="col-lg-5 d-flex flex-column justify-content-between">
                                <div class="p-4 p-md-5 mx-md-3 mb-0 d-flex justify-content-between align-items-center">
                                    <div class="d-flex align-items-center gap-2">
                                        <img src="{{ asset('assets/img/favicon.svg') }}" height="38" alt="">
                                        <div class="lh-1">
                                            <div class="fw-bold fs-3">{{ config('app.name') }}</div>
                                            <small class="text-muted">Berbasis knowledge base</small>
                                        </div>
                                    </div>
                                    <span class="badge mdka-bg-purple-100 mdka-text-purple-600 fs-6"><i class="ti ti-building me-1"></i>{{ config('payroll.nama_perusahaan') }}</span>
                                </div>
                                <div class="card-body px-md-5 pt-0 mx-md-3">
                                    <div class="text-center mt-2">
                                        <h1 class="text-secondary">Payroll &amp; PPh 21</h1>
                                    </div>
                                    <hr class="my-3">
                                    <div class="text-center">
                                        <span class="text-muted w-100" style="font-size: 15px">Masuk dengan akun admin finance</span>
                                    </div>
                                    <form id="loginForm" class="p-3 rounded" method="POST" action="{{ route('login') }}">
                                        @csrf
                                        <div class="row g-3">
                                            <div class="col-12">
                                                <label for="email" class="form-label">Email</label>
                                                <input type="email" class="form-control @error('email') is-invalid @enderror" id="email" name="email"
                                                    value="{{ old('email') }}" placeholder="Email" required autofocus autocomplete="username">
                                            </div>
                                            <div class="col-12">
                                                <div class="d-flex justify-content-between">
                                                    <label for="password" class="form-label">Kata sandi</label>
                                                    <a href="#" class="text-primary" data-bs-toggle="modal" data-bs-target="#accessLoginGuide">Lupa kata sandi?</a>
                                                </div>
                                                <input type="password" class="form-control" id="password" name="password" placeholder="Kata sandi" required
                                                    autocomplete="current-password">
                                            </div>
                                            <div class="col-12">
                                                <label class="form-check mb-0">
                                                    <input type="checkbox" class="form-check-input" name="ingat" value="1">
                                                    <span class="form-check-label">Ingat saya</span>
                                                </label>
                                            </div>
                                            <div class="col-12">
                                                <button type="submit" class="btn btn-primary w-100"><i class="ti ti-login me-2"></i>Masuk</button>
                                            </div>
                                        </div>
                                    </form>
                                    <br>
                                    <div class="text-center">
                                        Panduan masuk :
                                        <button type="button" class="btn btn-sm btn-info rounded" data-bs-toggle="modal" data-bs-target="#accessLoginGuide">
                                            Klik di sini</button>
                                    </div>
                                </div>

                                <div class="d-flex justify-content-center pb-2">
                                    <small class="text-muted">&copy; {{ config('app.name') }} {{ date('Y') }}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Modal -->
    <div class="modal fade" id="accessLoginGuide" tabindex="-1" aria-labelledby="accessLoginGuideTitle" aria-hidden="true">
        <div class="modal-dialog modal-xl modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title" id="accessLoginGuideTitle">Panduan masuk</h3>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Tutup"></button>
                </div>
                <div class="modal-body p-3">
                    <div class="row row-deck g-3">
                        <div class="col-md">
                            <div class="px-3 py-5 w-100 border rounded d-flex flex-column gap-3">
                                <div class="d-flex justify-content-center align-items-center gap-2">
                                    <span class="avatar avatar-md rounded-3 mdka-bg-blue-100 mdka-text-blue-600"><i class="ti ti-user-shield fs-2"></i></span>
                                    <div><span class="display-6 text-secondary fw-light">|</span></div>
                                    <span class="avatar avatar-md rounded-3 mdka-bg-blue-100 mdka-text-blue-600"><i class="ti ti-mail fs-2"></i></span>
                                </div>
                                <div class="text-center">
                                    Akun admin finance
                                    <br><span class="text-warning small">email + kata sandi</span>
                                    <br>dibuat oleh admin sistem lewat
                                    <br><code>php artisan payroll:pengguna</code>
                                </div>
                            </div>
                        </div>
                        <div class="col-md">
                            <div class="px-3 py-5 w-100 border rounded d-flex flex-column gap-3">
                                <div class="d-flex justify-content-center align-items-center gap-2">
                                    <span class="avatar avatar-md rounded-3 mdka-bg-orange-100 mdka-text-orange-600"><i class="ti ti-key fs-2"></i></span>
                                    <div><span class="display-6 text-secondary fw-light">|</span></div>
                                    <span class="avatar avatar-md rounded-3 mdka-bg-orange-100 mdka-text-orange-600"><i class="ti ti-refresh fs-2"></i></span>
                                </div>
                                <div class="text-center">
                                    Lupa kata sandi
                                    <br><span class="text-warning small">tidak ada reset lewat email</span>
                                    <br>minta admin sistem menjalankan perintah yang sama
                                    <br>untuk <span class="text-primary fw-bold">mengganti kata sandi</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-md">
                            <div class="px-3 py-5 w-100 border rounded d-flex flex-column gap-3">
                                <div class="d-flex justify-content-center align-items-center gap-2">
                                    <h3 class="mb-0">Setelah masuk</h3>
                                </div>
                                <div class="text-center">
                                    <span><strong>Dashboard</strong> menampilkan rekap payroll per tahun pajak. Data pegawai dan data HR (gaji,
                                        tunjangan, kehadiran) diisi di menu <strong>Pegawai &amp; data HR</strong>, lalu tekan <strong>Hitung</strong>.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection

@push('javascript')
    @if ($errors->any())
        <script>
            Swal.fire({
                icon: 'error',
                title: 'Gagal masuk',
                html: @json(collect($errors->all())->map(fn ($e) => e($e))->implode('<br>')),
            });
        </script>
    @endif
@endpush
