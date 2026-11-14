<!DOCTYPE html>
<html lang="id">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>@yield('kode') | {{ config('app.name') }}</title>
    <link rel="icon" type="image/svg+xml" href="{{ asset('assets/img/favicon.svg') }}" />
    <link href="{{ asset('assets/css/apps.min.css') }}" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.36.0/tabler-icons.min.css">
    <link href="{{ asset('assets/css/fonts/fonts.css') }}" rel="stylesheet" />
    <link href="{{ asset('assets/css/custom.css') }}" rel="stylesheet" />
</head>

<body class="border-top-wide border-primary d-flex flex-column">
    <div class="page page-center">
        <div class="container-tight py-4">
            <div class="empty">
                <div class="empty-header">@yield('kode')</div>
                <p class="empty-title">@yield('judul')</p>
                <p class="empty-subtitle text-secondary">@yield('pesan')</p>
                <div class="empty-action">
                    <a href="{{ url('/') }}" class="btn mdka-btn-blue-500 text-white border-0">
                        <i class="ti ti-arrow-left me-2"></i> Kembali ke dashboard
                    </a>
                </div>
            </div>
        </div>
    </div>
</body>

</html>
