<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
@include('main.components.license.license')

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Masuk | {{ config('app.name') }}</title>
    <meta name="description" content="Payroll & PPh 21 berbasis knowledge base" />
    <link rel="icon" type="image/svg+xml" href="{{ asset('assets/img/favicon.svg') }}" />
    {{-- Main Style --}}
    @include('auth.components.style.style')
    <meta name="theme-color" content="#3b82f6">
</head>

<body>
    {{-- Main Page --}}
    @yield('content')
    {{-- End OF Main Page --}}

    {{-- Main Javasript --}}
    @include('auth.components.js.js')
    @include('main.modal.alert')
</body>

</html>
