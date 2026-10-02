<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
@include('main.components.license.license')

<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta content="width=device-width, initial-scale=1" name="viewport">
    <title>@yield('page-title', 'Payroll') | {{ config('app.name') }}</title>
    <meta name="description" content="Payroll & PPh 21 berbasis knowledge base" />
    <link rel="icon" type="image/svg+xml" href="{{ asset('assets/img/favicon.svg') }}" />
    <!--  Main Style -->
    @include('main.components.style.style')
    <meta name="theme-color" content="#3b82f6">
</head>

<body class="layout-fluid">
    <div class="page">
        <!--  Sidebar -->
        @include('main.sidebar.sidebar')
        <!--  Navbar -->
        @include('main.navbar.navbar')

        <div class="page-wrapper">
            <!-- Page header -->
            @include('main.header.header')

            <!--  Main Page -->
            <div class="page-body mt-1">
                <div class="container-xl" style="max-width: 1440px">
                    @yield('content')
                </div>
            </div>
            <!--  End OF Main Page -->
            @include('main.footer.footer')
        </div>
    </div>

    <!--  Main Javasript -->
    @include('main.components.js.js')

    <!-- Global Alert -->
    @include('main.modal.alert')
</body>

</html>
