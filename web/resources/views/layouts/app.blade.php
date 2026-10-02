<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ isset($judul) ? $judul.' · ' : '' }}{{ config('app.name') }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="min-h-screen bg-slate-50 text-slate-900 antialiased">
    <header class="border-b border-slate-200 bg-white">
        <div class="mx-auto flex max-w-7xl flex-wrap items-center gap-x-8 gap-y-2 px-4 py-3">
            <a href="{{ route('rekap') }}" class="leading-tight">
                <span class="block font-semibold text-slate-900">{{ config('app.name') }}</span>
                <span class="block text-xs text-slate-500">Dihitung oleh engine knowledge base</span>
            </a>
            <nav class="flex flex-1 gap-1 text-sm">
                @foreach (['rekap' => 'Rekap', 'pegawai.index' => 'Pegawai', 'mesin' => 'Mesin'] as $rute => $teks)
                    @php($aktif = request()->routeIs(str_replace('.index', '', $rute).'*') || ($rute === 'pegawai.index' && request()->routeIs('payroll.*')))
                    <a href="{{ route($rute) }}"
                       class="rounded-md px-3 py-1.5 {{ $aktif ? 'bg-slate-100 font-medium text-slate-900' : 'text-slate-600 hover:bg-slate-50' }}">{{ $teks }}</a>
                @endforeach
            </nav>
            <div class="flex items-center gap-3 text-sm text-slate-600">
                <span>{{ auth()->user()->name }}</span>
                <form method="POST" action="{{ route('logout') }}">
                    @csrf
                    <button class="btn btn-secondary py-1">Keluar</button>
                </form>
            </div>
        </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-6">
        @if (session('sukses'))
            <div class="mb-4 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800" role="status">{{ session('sukses') }}</div>
        @endif
        @if (session('galat'))
            <div class="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm whitespace-pre-line text-red-800" role="alert">{{ session('galat') }}</div>
        @endif
        @yield('isi')
    </main>
</body>
</html>
