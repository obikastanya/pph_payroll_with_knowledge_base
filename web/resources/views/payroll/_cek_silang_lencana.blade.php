@php
    $warna = ['identik' => 'bg-green-100 text-green-800', 'sah_titik_tetap_ganda' => 'bg-blue-100 text-blue-800',
        'berbeda' => 'bg-red-100 text-red-800', 'galat' => 'bg-slate-100 text-slate-600'];
@endphp
@if ($status)
    <span class="lencana {{ $warna[$status] ?? 'bg-slate-100 text-slate-600' }}">{{ \App\Payroll\Label::CEK_SILANG[$status] ?? $status }}</span>
@endif
