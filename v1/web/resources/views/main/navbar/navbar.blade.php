<!-- Navbar -->
<header class="navbar navbar-expand-md bg-white d-none d-lg-flex d-print-none sticky-top border-bottom">
    <div class="container-xl">
        <div class="d-flex align-items-center gap-2">
            <button id="sidebarControl" type="button" class="btn bg-secondary-lt p-1 d-none d-md-flex align-items-center"
                data-bs-toggle="tooltip" data-bs-title="Ciutkan / lebarkan sidebar" aria-label="Ciutkan sidebar">
                <i class="ti ti-layout-sidebar text-dark h2 mb-0"></i>
            </button>
            <div class="fw-bolder mdka-text-brand-500 h3 mb-0">
                @yield('page-title')
            </div>
        </div>
        <div class="navbar-nav flex-row order-md-last align-items-center gap-3">
            <span class="badge mdka-bg-purple-100 mdka-text-purple-600 d-none d-md-inline-flex" data-bs-toggle="tooltip"
                data-bs-title="Lapisan kebijakan perusahaan yang dipakai engine">
                <i class="ti ti-building me-1"></i> {{ config('payroll.nama_perusahaan') }}
            </span>
            <div class="nav-item dropdown">
                <a href="#" class="nav-link d-flex lh-1 text-reset p-0" data-bs-toggle="dropdown" aria-label="Menu pengguna">
                    <span class="avatar avatar-sm rounded-circle mdka-bg-blue-100 mdka-text-blue-600 position-relative">
                        {{ \Illuminate\Support\Str::of(auth()->user()->name)->explode(' ')->take(2)->map(fn ($s) => mb_substr($s, 0, 1))->implode('') }}
                        <span class="status-dot status-dot-animated bg-green position-absolute bottom-0 end-0 d-block"></span>
                    </span>
                    <div class="d-none d-xl-block ps-2">
                        <div>{{ auth()->user()->name }}</div>
                        <div class="mt-1 small text-muted">{{ auth()->user()->email }}</div>
                    </div>
                </a>
                <div class="dropdown-menu dropdown-menu-end dropdown-menu-arrow">
                    <a href="#" class="dropdown-item" onclick="event.preventDefault(); document.getElementById('logout-form').submit();">
                        <i class="ti ti-logout me-2"></i> Keluar
                    </a>
                </div>
            </div>
        </div>
    </div>
</header>
<form id="logout-form" action="{{ route('logout') }}" method="POST" class="d-none">
    @csrf
</form>
