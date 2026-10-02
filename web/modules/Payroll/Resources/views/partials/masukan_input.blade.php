{{-- Satu isian tambahan dari KB menurut tipenya. Variabel: $m (deklarasi masukan), $nama (atribut name), $kunciGalat
     (kunci error bag), $nilai (teks isian), opsional $kecil (sel tabel), $label (aria-label). --}}
@php($kelas = 'form-control'.(($kecil ?? false) ? ' form-control-sm' : '').' tabular-nums'.($errors->has($kunciGalat) ? ' is-invalid' : ''))
@php($kelasPilih = 'form-select'.(($kecil ?? false) ? ' form-select-sm' : '').($errors->has($kunciGalat) ? ' is-invalid' : ''))
@switch($m['tipe'])
    @case('rupiah')
    @case('bilangan')
        <input id="{{ $id ?? $nama }}" name="{{ $nama }}" value="{{ $nilai }}" type="number" step="1" aria-label="{{ $label ?? $m['label'] }}"
            @if (($m['wajib'] ?? false) && ! ($kecil ?? false)) required @endif class="{{ $kelas }}" @if ($kecil ?? false) style="width: 150px" @endif>
    @break

    @case('persen')
    @case('desimal')
        <input id="{{ $id ?? $nama }}" name="{{ $nama }}" value="{{ $nilai }}" inputmode="decimal" aria-label="{{ $label ?? $m['label'] }}"
            placeholder="{{ $m['tipe'] === 'persen' ? 'mis. 10' : 'mis. 0,24' }}"
            @if (($m['wajib'] ?? false) && ! ($kecil ?? false)) required @endif class="{{ $kelas }}" @if ($kecil ?? false) style="width: 110px" @endif>
    @break

    @case('tanggal')
        <input id="{{ $id ?? $nama }}" name="{{ $nama }}" value="{{ $nilai }}" type="date" aria-label="{{ $label ?? $m['label'] }}"
            @if (($m['wajib'] ?? false) && ! ($kecil ?? false)) required @endif class="{{ $kelas }}">
    @break

    @case('pilihan')
    @case('ya_tidak')
        @php($opsi = $m['tipe'] === 'ya_tidak' ? ['1' => 'Ya', '0' => 'Tidak'] : array_combine($m['pilihan'], $m['pilihan']))
        <select id="{{ $id ?? $nama }}" name="{{ $nama }}" aria-label="{{ $label ?? $m['label'] }}" class="{{ $kelasPilih }}">
            <option value="">{{ $m['bawaan'] !== null ? '— bawaan —' : '— pilih —' }}</option>
            @foreach ($opsi as $v => $teks)
                <option value="{{ $v }}" @selected((string) $nilai === (string) $v)>{{ $teks }}</option>
            @endforeach
        </select>
    @break
@endswitch
