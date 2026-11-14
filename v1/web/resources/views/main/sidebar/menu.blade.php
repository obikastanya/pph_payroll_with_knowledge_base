<!--
    Item sidebar dibaca dari config/menu.php (Base-Apps-Merdeka: tabel `menu`), dirender dengan markup yang sama.
-->
@php($lastSection = null)
@foreach (config('menu') as $menu)
    @if (($menu['section'] ?? null) && $menu['section'] !== $lastSection)
        <li class="nav-item menu-section-header">
            <span class="subheader text-wrap sidebar-control">{{ $menu['section'] }}</span>
        </li>
        @php($lastSection = $menu['section'])
    @endif
    @include('main.sidebar.menu-item', ['menu' => $menu, 'isRoot' => true])
@endforeach
