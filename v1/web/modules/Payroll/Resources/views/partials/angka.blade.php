{{-- Isian bilangan bulat (rupiah atau hari). Variabel: $f, $lbl, opsional $bantu, $wajib, $min, $max, $kolom. --}}
<div class="{{ $kolom ?? 'col-md-3' }}">
    <label for="{{ $f }}" class="form-label {{ ($wajib ?? false) ? 'required' : '' }}">{{ $lbl }}</label>
    <input id="{{ $f }}" name="{{ $f }}" type="number" step="1" min="{{ $min ?? 0 }}" @isset($max) max="{{ $max }}" @endisset
        value="{{ old($f, $payroll->{$f}) }}" @if ($wajib ?? false) required @endif
        class="form-control tabular-nums @error($f) is-invalid @enderror">
    @if ($bantu ?? false)
        <small class="form-hint">{{ $bantu }}</small>
    @endif
</div>
