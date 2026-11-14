{{-- Kartu ringkasan (Base-Apps-Merdeka): ikon berwarna + judul + nilai. --}}
@props([
    'value_id' => null,
    'value' => '',
    'title' => '',
    'icon' => '',
    'color' => 'gray',
    'size' => 'md',
    'keterangan' => null,
])

@php
    [$text_color, $bg_color, $clip_color] = match ($color) {
        'red' => ['mdka-text-red-600', 'mdka-bg-red-100', 'mdka-bg-red-300'],
        'blue' => ['mdka-text-blue-500', 'mdka-bg-blue-50', 'mdka-bg-blue-200'],
        'green' => ['mdka-text-green-600', 'mdka-bg-green-100', 'mdka-bg-green-300'],
        'yellow' => ['mdka-text-yellow-500', 'mdka-bg-yellow-50', 'mdka-bg-yellow-200'],
        'purple' => ['mdka-text-purple-600', 'mdka-bg-purple-100', 'mdka-bg-purple-300'],
        'pink' => ['mdka-text-pink-600', 'mdka-bg-pink-100', 'mdka-bg-pink-300'],
        'orange' => ['mdka-text-orange-600', 'mdka-bg-orange-100', 'mdka-bg-orange-300'],
        'lime' => ['mdka-text-lime-600', 'mdka-bg-lime-100', 'mdka-bg-lime-300'],
        'brand' => ['mdka-text-brand-600', 'mdka-bg-brand-100', 'mdka-bg-brand-300'],
        default => ['mdka-text-gray-600', 'mdka-bg-gray-100', 'mdka-bg-gray-300'],
    };
    [$value_size, $title_size, $card_padding] = match ($size) {
        'sm' => ['1em', '0.8em', 'p-2'],
        'lg' => ['2em', '1.2em', 'p-3'],
        default => ['1.4em', '0.9em', 'p-3'],
    };
@endphp

@once
    @push('style')
        <style>
            .summary-icon {
                position: relative;
                width: 48px;
                height: 48px;
                flex: 0 0 48px;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
                font-size: 1.5rem;
            }

            .summary-icon-clip {
                position: absolute;
                width: 20px;
                height: 20px;
                border-radius: 25%;
                right: -5px;
                bottom: -5px;
            }
        </style>
    @endpush
@endonce

<div {{ $attributes->merge(['class' => 'card h-100 rounded-3']) }} @if ($keterangan) title="{{ $keterangan }}" @endif>
    <div class="card-body {{ $card_padding }}">
        <div class="d-flex h-100 w-100 align-items-center gap-3">
            <div class="summary-icon rounded-3 {{ $text_color }} {{ $bg_color }}">
                {{ $icon }}
                <span class="summary-icon-clip {{ $clip_color }}"></span>
            </div>
            <div class="d-flex flex-column min-w-0">
                <span class="fw-medium text-muted text-truncate" style="font-size: {{ $title_size }}">{{ $title }}</span>
                <span @if ($value_id) id="{{ $value_id }}" @endif class="fw-bolder tabular-nums text-nowrap" style="font-size: {{ $value_size }}">{{ $value }}</span>
            </div>
        </div>
    </div>
</div>
