<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
@include('main.components.license.license')

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Masuk | {{ config('app.name') }}</title>
    <link rel="icon" type="image/svg+xml" href="{{ asset('assets/img/favicon.svg') }}" />
    <link href="{{ asset('assets/css/apps.min.css') }}" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.36.0/tabler-icons.min.css">
    <link href="{{ asset('assets/css/fonts/fonts.css') }}" rel="stylesheet" />
    <link href="{{ asset('assets/css/custom.css') }}" rel="stylesheet" />
    <style>
        body {
            min-height: 100vh;
            font-size: 13px;
            background: linear-gradient(135deg, var(--mdka-blue-900) 0%, var(--mdka-blue-600) 55%, var(--mdka-purple-600) 100%);
        }

        .panel-merek {
            background: linear-gradient(160deg, var(--mdka-blue-600), var(--mdka-blue-800));
        }

        .panel-merek .fitur i {
            width: 36px;
            height: 36px;
            border-radius: .5rem;
            background: rgba(255, 255, 255, .14);
        }
    </style>
    <meta name="theme-color" content="#3b82f6">
</head>

<body>
    @yield('content')
    <script src="{{ asset('assets/js/apps.min.js') }}" defer></script>
</body>

</html>
