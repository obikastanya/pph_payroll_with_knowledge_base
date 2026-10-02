@php
    $children = $menu['children'] ?? [];
    $hasChildren = $children !== [];
    $menuHref = isset($menu['route']) && \Illuminate\Support\Facades\Route::has($menu['route']) ? route($menu['route']) : '#';
    $isActive = request()->routeIs(...($menu['aktif'] ?? [$menu['route'] ?? '-']));
    $isDescendantActive = $hasChildren && collect($children)->contains(fn ($c) => request()->routeIs(...($c['aktif'] ?? [$c['route'] ?? '-'])));
@endphp
@if ($hasChildren)
    <li class="nav-item dropdown {{ $isDescendantActive ? 'active-mdka-nav' : '' }}">
        <a class="nav-link dropdown-toggle {{ $isDescendantActive ? 'active show' : '' }}" href="#" data-bs-toggle="dropdown"
            data-bs-auto-close="false" role="button" aria-expanded="{{ $isDescendantActive ? 'true' : 'false' }}">
            @if ($menu['icon'] ?? null)
                <span class="nav-link-icon d-md-none d-lg-inline-block"><i class="ti ti-{{ $menu['icon'] }}"></i></span>
            @endif
            <span class="nav-link-title sidebar-control">{{ $menu['title'] }}</span>
        </a>
        <div class="dropdown-menu {{ $isDescendantActive ? 'show' : '' }}">
            <div class="dropdown-menu-columns">
                <div class="dropdown-menu-column">
                    @foreach ($children as $child)
                        @php($childActive = request()->routeIs(...($child['aktif'] ?? [$child['route'] ?? '-'])))
                        <a class="dropdown-item sidebar-item {{ $childActive ? 'active-mdka-nav' : '' }}" href="{{ route($child['route']) }}">
                            <span class="nav-link-title sidebar-control">{{ $child['title'] }}</span>
                        </a>
                    @endforeach
                </div>
            </div>
        </div>
    </li>
@else
    <li class="nav-item {{ $isActive ? 'active-mdka-nav' : '' }}">
        <a class="nav-link {{ $isActive ? 'active-mdka-nav' : '' }}" href="{{ $menuHref }}" @if ($isActive) aria-current="page" @endif>
            @if ($menu['icon'] ?? null)
                <span class="nav-link-icon d-md-none d-lg-inline-block"><i class="ti ti-{{ $menu['icon'] }}"></i></span>
            @endif
            <span class="nav-link-title sidebar-control">{{ $menu['title'] }}</span>
        </a>
    </li>
@endif
