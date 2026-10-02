{{-- Lencana hasil cek silang E12 (engine KB vs kalkulator tanpa KB), gaya `status` Tabler seperti status-badge Merdeka. --}}
@props(['status' => null])
@php
    [$warna, $label] = match ($status) {
        'identik' => ['green', 'identik'],
        'sah_titik_tetap_ganda' => ['blue', 'beda, keduanya sah'],
        'berbeda' => ['red', 'BERBEDA'],
        'galat' => ['gray', 'tidak dapat dicek'],
        default => [null, null],
    };
@endphp
@if ($warna)
    <span {{ $attributes->merge(['class' => "status status-{$warna}"]) }}>{{ $label }}</span>
@endif
