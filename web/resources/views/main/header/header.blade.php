{{-- Breadcrumb dari $menuItems yang dikirim controller (pola Base-Apps-Merdeka). --}}
@if (isset($menuItems) && count($menuItems) > 1)
    <div class="page-header d-print-none mt-2">
        <div class="container-xl" style="max-width: 1440px">
            <ol class="breadcrumb breadcrumb-arrows" aria-label="breadcrumbs">
                @foreach ($menuItems as $key => $menuItem)
                    <li class="breadcrumb-item {{ $menuItem['active'] ? 'active' : '' }} d-flex align-items-center">
                        @if ($key === 0)
                            <i class="ti ti-home me-1"></i>
                        @endif
                        @if ($menuItem['active'])
                            <span aria-current="page">{{ $menuItem['label'] }}</span>
                        @else
                            <a href="{{ url($menuItem['url']) }}">{{ $menuItem['label'] }}</a>
                        @endif
                    </li>
                @endforeach
            </ol>
        </div>
    </div>
@endif
