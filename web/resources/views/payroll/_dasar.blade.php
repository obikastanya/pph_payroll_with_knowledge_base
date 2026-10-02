{{-- Sel "Dasar": aturan KB yang menghasilkan angka + pasal/kebijakan sumbernya. Variabel: $d (array|null). --}}
@if ($d)
    <span class="lencana {{ $d['lapisan'] === 'perusahaan' ? 'bg-violet-100 text-violet-800' : 'bg-sky-100 text-sky-800' }}">{{ $d['pendek'] }}</span>
    <div class="mt-0.5 text-xs text-slate-500">{{ $d['panjang'] }}</div>
@else
    <span class="text-xs text-slate-400">—</span>
@endif
