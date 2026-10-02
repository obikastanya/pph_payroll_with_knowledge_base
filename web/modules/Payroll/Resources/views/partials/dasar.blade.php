{{-- Sel "Dasar": aturan KB yang menghasilkan angka + pasal/kebijakan sumbernya. Variabel: $d (array|null). --}}
@if ($d)
    <span class="badge {{ $d['lapisan'] === 'perusahaan' ? 'mdka-bg-purple-100 mdka-text-purple-600' : 'mdka-bg-blue-100 mdka-text-blue-600' }}">{{ $d['pendek'] }}</span>
    <div class="mt-1 text-muted" style="font-size: .7rem">{{ $d['panjang'] }}</div>
@else
    <span class="text-muted">—</span>
@endif
