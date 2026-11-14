<!-- Sidebar -->
<aside class="navbar navbar-vertical navbar-expand-lg mdka-bg-gray-50" data-bs-theme="light">
    <div class="container-fluid overflow-x-hidden">
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#sidebar-menu"
            aria-controls="sidebar-menu" aria-expanded="false" aria-label="Buka menu">
            <span class="navbar-toggler-icon"></span>
        </button>
        <h1 class="navbar-brand navbar-brand-autodark">
            <a href="{{ route('dashboard.index') }}" class="d-flex align-items-center gap-2 link-underline link-underline-opacity-0 text-reset">
                <span class="avatar avatar-sm mdka-btn-blue-500 text-white rounded-2"><i class="ti ti-receipt-tax fs-2"></i></span>
                <span class="brand-teks text-start navbar-brand-image">
                    <span class="d-block fw-bold" style="font-size: .95rem">{{ config('app.name') }}</span>
                    <span class="d-block text-muted fw-normal" style="font-size: .7rem">Berbasis knowledge base</span>
                </span>
            </a>
        </h1>

        <div class="navbar-nav flex-row d-lg-none">
            <div class="nav-item dropdown">
                <a href="#" class="nav-link d-flex lh-1 text-reset p-0" data-bs-toggle="dropdown" aria-label="Menu pengguna">
                    <span class="avatar avatar-sm rounded-circle mdka-bg-blue-100 mdka-text-blue-600">{{ \Illuminate\Support\Str::of(auth()->user()->name)->explode(' ')->take(2)->map(fn ($s) => mb_substr($s, 0, 1))->implode('') }}</span>
                </a>
                <div class="dropdown-menu dropdown-menu-end dropdown-menu-arrow">
                    <span class="dropdown-header">{{ auth()->user()->name }}</span>
                    <a href="#" class="dropdown-item" onclick="event.preventDefault(); document.getElementById('logout-form').submit();">
                        <i class="ti ti-logout me-2"></i> Keluar
                    </a>
                </div>
            </div>
        </div>
        <div class="collapse navbar-collapse" id="sidebar-menu">
            <ul class="navbar-nav py-lg-3">
                @include('main.sidebar.menu')
            </ul>
        </div>
    </div>
</aside>

@push('javascript')
    <script>
        // Sidebar bisa diciutkan (pola Base-Apps-Merdeka); status disimpan di localStorage
        $(function() {
            let savedState = null;
            try {
                savedState = localStorage.getItem('sidebarState');
            } catch (e) {}
            savedState === 'collapsed' ? collapseSidebar() : expandSidebar();

            $('#sidebarControl').on('click', function() {
                const collapsed = $('.navbar-expand-lg').hasClass('collapsed');
                collapsed ? expandSidebar() : collapseSidebar();
                try {
                    localStorage.setItem('sidebarState', collapsed ? 'expanded' : 'collapsed');
                } catch (e) {}
            });
        });

        function expandSidebar() {
            const navbar = $('.navbar-expand-lg');
            navbar.removeClass('collapsed').css({
                width: '',
                'overflow-y': 'auto'
            });
            $('.navbar-nav').css('gap', '');
            $('.sidebar-control').removeClass('d-none');
            $('.navbar-brand-image').removeClass('d-none');
            $('.nav-link-icon').css({
                'padding-left': '0',
                transform: 'scale(1)'
            });
            if (window.innerWidth >= 992) {
                $('.navbar-expand-md, .page-wrapper').css('margin-left', '15rem');
            }
        }

        function collapseSidebar() {
            const navbar = $('.navbar-expand-lg');
            navbar.addClass('collapsed').css({
                width: '80px',
                'overflow-y': 'auto'
            });
            $('.navbar-nav').css('gap', '0.5rem');
            $('.sidebar-control').addClass('d-none');
            $('.navbar-brand-image').addClass('d-none');
            $('.nav-link-icon').css({
                'padding-left': '10px',
                transform: 'scale(1.2)'
            });
            if (window.innerWidth >= 992) {
                $('.navbar-expand-md, .page-wrapper').css('margin-left', '80px');
            }
        }
    </script>
@endpush
