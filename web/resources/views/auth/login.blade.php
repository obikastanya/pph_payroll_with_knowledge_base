<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Masuk · {{ config('app.name') }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="flex min-h-screen items-center justify-center bg-slate-50 px-4 text-slate-900 antialiased">
    <main class="w-full max-w-sm">
        <h1 class="text-xl font-semibold">{{ config('app.name') }}</h1>
        <p class="mt-1 mb-6 text-sm text-slate-500">Masuk untuk mengelola payroll dan PPh 21 pegawai.</p>
        <form method="POST" action="{{ route('login') }}" class="card space-y-4 p-6">
            @csrf
            <div>
                <label for="email" class="label">Email</label>
                <input id="email" name="email" type="email" value="{{ old('email') }}" required autofocus autocomplete="username"
                       class="input @error('email') input-error @enderror">
                @error('email')<p class="galat">{{ $message }}</p>@enderror
            </div>
            <div>
                <label for="password" class="label">Kata sandi</label>
                <input id="password" name="password" type="password" required autocomplete="current-password" class="input">
            </div>
            <label class="flex items-center gap-2 text-sm text-slate-600">
                <input type="checkbox" name="ingat" value="1" class="rounded border-slate-300"> Ingat saya
            </label>
            <button class="btn btn-primary w-full">Masuk</button>
        </form>
    </main>
</body>
</html>
