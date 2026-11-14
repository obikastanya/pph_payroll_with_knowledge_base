{{-- Isian tambahan yang diminta berkas KB tambahan (deklarasi `masukan`), dibangun dari SkemaMasukan: aturan baru yang
     meminta input baru langsung muncul di sini tanpa mengubah kode. Variabel: $masukan, $galatMasukan, $isianMasukan. --}}
@use('App\Helpers\Format')
@use('Modules\Payroll\Services\SkemaMasukan')
@php
    $tahunan = array_values(array_filter($masukan, fn ($m) => $m['lingkup'] === 'tahun'));
    $bulanan = array_values(array_filter($masukan, fn ($m) => $m['lingkup'] === 'bulan'));
    $teks = fn (mixed $v) => match (true) { $v === null => '', is_bool($v) => $v ? '1' : '0', default => (string) $v };
    $satuan = ['rupiah' => ' (Rp)', 'persen' => ' (%)'];
    $bawaan = fn (array $m) => $m['bawaan'] === null ? null : match ($m['tipe']) {
        'rupiah' => Format::rp($m['bawaan']), 'persen' => str_replace('.', ',', (string) $m['bawaan']).'%',
        'ya_tidak' => $m['bawaan'] ? 'ya' : 'tidak', default => (string) $m['bawaan'] };
@endphp

@if ($galatMasukan)
    <div class="col-12">
        <div class="alert alert-danger mb-0" role="alert">
            <div class="d-flex gap-2"><i class="ti ti-books-off fs-2"></i>
                <div><strong>Isian tambahan dari knowledge base tidak dapat dimuat.</strong>
                    <div class="text-wrap" style="white-space: pre-line">{{ $galatMasukan }}</div>
                </div>
            </div>
        </div>
    </div>
@endif

@if ($masukan !== [])
    <div class="col-12">
        <div class="card mdka-border-purple-200">
            <div class="card-header p-3 d-block">
                <h4 class="card-title mb-1"><i class="ti ti-books me-2 mdka-text-purple-600"></i>Isian tambahan dari knowledge base</h4>
                <div class="text-muted small">Diminta aturan di berkas KB tambahan (menu <a href="{{ route('kb.index') }}">Basis pengetahuan</a>).
                    Isian kosong memakai nilai bawaan aturan bila ada.</div>
            </div>
            @if ($tahunan !== [])
                <div class="card-body p-3 row g-3">
                    @foreach ($tahunan as $m)
                        @php($nama = "masukan[{$m['kunci']}]")
                        <div class="col-md-4">
                            <label for="masukan_{{ $m['kunci'] }}" class="form-label {{ $m['wajib'] ? 'required' : '' }}">{{ $m['label'] }}{{ $satuan[$m['tipe']] ?? '' }}</label>
                            @include('Payroll::partials.masukan_input', ['m' => $m, 'nama' => $nama, 'id' => "masukan_{$m['kunci']}",
                                'kunciGalat' => "masukan.{$m['kunci']}", 'nilai' => old("masukan.{$m['kunci']}", $teks($isianMasukan['tahun'][$m['kunci']] ?? null))])
                            <small class="form-hint">
                                {{ $m['keterangan'] !== '' ? rtrim($m['keterangan'], '. ').'.' : '' }}
                                @if ($bawaan($m) !== null)
                                    Bawaan: {{ $bawaan($m) }}.
                                @endif
                                @if ($m['sumber'])
                                    <span class="d-block text-muted"><i class="ti ti-gavel me-1"></i>{{ $m['sumber'] }}</span>
                                @endif
                            </small>
                        </div>
                    @endforeach
                </div>
            @endif
            @if ($bulanan !== [] && $rentang)
                <div class="card-body table-responsive p-0 {{ $tahunan !== [] ? 'border-top' : '' }}">
                    <table class="table table-vcenter table-sm mb-0 text-nowrap">
                        <thead>
                            <tr class="mdka-bg-gray-50">
                                <th class="py-2 ps-3">Bulan</th>
                                @foreach ($bulanan as $m)
                                    <th class="py-2" title="{{ $m['keterangan'] }} {{ $m['sumber'] }}">
                                        <span class="{{ $m['wajib'] ? 'required' : '' }}">{{ $m['label'] }}{{ $satuan[$m['tipe']] ?? '' }}</span>
                                        @if ($bawaan($m) !== null)
                                            <span class="d-block text-muted fw-normal small">bawaan {{ $bawaan($m) }}</span>
                                        @endif
                                    </th>
                                @endforeach
                            </tr>
                        </thead>
                        <tbody>
                            @foreach (range($rentang[0], $rentang[1]) as $b)
                                <tr>
                                    <td class="ps-3 fw-medium">{{ Format::bulan($b, true) }}</td>
                                    @foreach ($bulanan as $m)
                                        <td>
                                            @if (SkemaMasukan::berlakuBulan($m, $payroll->tahun, $b))
                                                @include('Payroll::partials.masukan_input', ['m' => $m, 'nama' => "masukan_bulan[{$b}][{$m['kunci']}]",
                                                    'id' => "masukan_bulan_{$b}_{$m['kunci']}", 'kunciGalat' => "masukan_bulan.{$b}.{$m['kunci']}", 'kecil' => true,
                                                    'label' => $m['label'].' '.Format::bulan($b, true),
                                                    'nilai' => old("masukan_bulan.{$b}.{$m['kunci']}", $teks($isianMasukan['bulan'][$b][$m['kunci']] ?? null))])
                                            @else
                                                <span class="text-muted" title="Aturan belum/tidak berlaku di bulan ini">—</span>
                                            @endif
                                        </td>
                                    @endforeach
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </div>
    </div>
@endif
