{{-- Isian bilangan bulat (rupiah atau hari). Variabel: $f, $lbl, opsional $bantu, $wajib, $min, $max. --}}
<div>
    <label for="{{ $f }}" class="label">{{ $lbl }}</label>
    <input id="{{ $f }}" name="{{ $f }}" type="number" step="1" min="{{ $min ?? 0 }}" @isset($max) max="{{ $max }}" @endisset
           value="{{ old($f, $payroll->{$f}) }}" @if ($wajib ?? false) required @endif
           class="input tabular-nums {{ $errors->has($f) ? 'input-error' : '' }}">
    @if ($bantu ?? false)<p class="bantu">{{ $bantu }}</p>@endif
</div>
