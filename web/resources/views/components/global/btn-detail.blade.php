{{-- Tombol standar (Base-Apps-Merdeka): label + ikon Tabler, warna mdka-btn-{color}-500 atau btn-outline-{color}. --}}
@props([
    'label' => '',
    'icon' => '',
    'disabled' => false,
    'size' => 'md',
    'color' => 'brand',
    'iconPosition' => 'left',
    'outline' => false,
    'href' => null,
    'type' => 'button',
])

@php
    $sizeClass = match ($size) {
        'xs' => 'px-1 py-0',
        'sm' => 'px-2 py-1',
        'lg' => 'px-4 py-3',
        'xl' => 'px-5 py-4',
        default => 'px-3 py-2',
    };

    $baseClass = 'd-inline-flex align-items-center justify-content-center gap-2 btn btn-sm '.$sizeClass.' rounded-2 ';

    $colorClass = $disabled ? 'disabled' : ($outline ? 'btn-outline-'.$color : 'mdka-btn-'.$color.'-500 text-white border-0');

    $iconClass = ($icon ? ' btn-icon' : '').($iconPosition == 'left' ? ' flex-row-reverse' : ' flex-row');

    $commonAttributes = $attributes->merge(['class' => $baseClass.$colorClass.$iconClass, 'style' => 'z-index: 1']);
@endphp

@if ($href)
    <a href="{{ $href }}" {{ $commonAttributes }}>
        @if ($label !== '')<span>{{ $label }}</span>@endif
        {!! $icon !!}
    </a>
@else
    <button type="{{ $type }}" {{ $commonAttributes }} @disabled($disabled)>
        @if ($label !== '')<span>{{ $label }}</span>@endif
        {!! $icon !!}
    </button>
@endif
