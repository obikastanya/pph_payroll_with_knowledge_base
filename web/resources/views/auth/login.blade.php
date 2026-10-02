@extends('auth.main.app')
@section('content')
    <section class="h-100">
        <div class="container py-5">
            <div class="row d-flex justify-content-center align-items-center" style="min-height: calc(100vh - 6rem)">
                <div class="col-xl-10">
                    <div class="card rounded-4 text-black overflow-hidden" style="box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.45);">
                        <div class="row g-0">
                            <div class="col-lg-7 panel-merek text-white p-5 d-none d-lg-flex flex-column justify-content-between">
                                <div>
                                    <span class="avatar avatar-lg bg-white mdka-text-blue-600 rounded-3 mb-4"><i class="ti ti-receipt-tax" style="font-size: 2.25rem"></i></span>
                                    <h1 class="display-6 fw-bold mb-2">{{ config('app.name') }}</h1>
                                    <p class="fs-3 opacity-75 mb-0">Payroll, BPJS, THR, dan PPh 21 pegawai tetap, dihitung oleh engine knowledge base.</p>
                                </div>
                                <div class="d-flex flex-column gap-3 my-5 fitur">
                                    <div class="d-flex align-items-center gap-3"><i class="ti ti-scale fs-2 d-flex align-items-center justify-content-center"></i>
                                        <span>Aturan pajak &amp; kebijakan perusahaan dipisah dua lapis; konflik terdeteksi otomatis.</span></div>
                                    <div class="d-flex align-items-center gap-3"><i class="ti ti-file-certificate fs-2 d-flex align-items-center justify-content-center"></i>
                                        <span>Setiap angka di slip gaji menunjuk aturan dan pasal sumbernya.</span></div>
                                    <div class="d-flex align-items-center gap-3"><i class="ti ti-arrows-exchange fs-2 d-flex align-items-center justify-content-center"></i>
                                        <span>Dicek silang dengan kalkulator independen tanpa knowledge base.</span></div>
                                </div>
                                <small class="opacity-50">Tahun pajak {{ config('payroll.tahun_min') }}–{{ config('payroll.tahun_max') }} · rezim PER-16 &amp; TER (PMK 168/2023)</small>
                            </div>
                            <div class="col-lg-5 d-flex flex-column justify-content-between">
                                <div class="card-body p-4 p-md-5">
                                    <div class="text-center mb-4 d-lg-none">
                                        <span class="avatar avatar-lg mdka-btn-blue-500 text-white rounded-3"><i class="ti ti-receipt-tax fs-1"></i></span>
                                    </div>
                                    <h2 class="text-secondary text-center mb-1">Selamat datang</h2>
                                    <div class="text-center text-muted mb-4">Masuk dengan akun admin finance</div>
                                    <hr class="my-3">
                                    <form id="loginForm" class="p-1" method="POST" action="{{ route('login') }}">
                                        @csrf
                                        <div class="row g-3">
                                            <div class="col-12">
                                                <label for="email" class="form-label">Email</label>
                                                <input type="email" class="form-control @error('email') is-invalid @enderror" id="email" name="email"
                                                    value="{{ old('email') }}" placeholder="nama@perusahaan.co.id" required autofocus autocomplete="username">
                                                @error('email')<div class="invalid-feedback">{{ $message }}</div>@enderror
                                            </div>
                                            <div class="col-12">
                                                <label for="password" class="form-label">Kata sandi</label>
                                                <input type="password" class="form-control" id="password" name="password" placeholder="Kata sandi" required
                                                    autocomplete="current-password">
                                            </div>
                                            <div class="col-12">
                                                <label class="form-check">
                                                    <input type="checkbox" class="form-check-input" name="ingat" value="1">
                                                    <span class="form-check-label">Ingat saya</span>
                                                </label>
                                            </div>
                                            <div class="col-12">
                                                <button type="submit" class="btn btn-primary w-100"><i class="ti ti-login me-2"></i>Masuk</button>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                                <div class="d-flex justify-content-center pb-3">
                                    <small class="text-muted">&copy; {{ date('Y') }} {{ config('app.name') }}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
@endsection
