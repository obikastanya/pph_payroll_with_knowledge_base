<link href="{{ asset('assets/css/apps.min.css') }}" rel="stylesheet" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.36.0/tabler-icons.min.css">
<link href="{{ asset('assets/css/fonts/fonts.css') }}" rel="stylesheet" />
<link href="{{ asset('assets/css/custom.css') }}" rel="stylesheet" />
<style>
    body {
        margin: 0;
        padding: 0;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        min-height: 100vh;
        font-size: 13px;
    }

    body::before {
        content: "";
        position: fixed;
        inset: -16px;
        background-image: url({{ asset('assets/img/bg-auth/auth-bg.jpg') }});
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        filter: brightness(45%) blur(3px);
        z-index: -1;
    }

    .btn-login {
        color: #000;
        background-color: #fff;
        border-color: #4299e1;
    }

    .btn-login:hover {
        color: #000;
        background-color: #ecf5fc;
        border-color: #4299e1;
    }

    @media (min-width: 768px) {
        .gradient-form {
            height: 100vh !important;
            background-attachment: fixed;
        }
    }

    @media (min-width: 992px) {
        .carousel-login {
            min-height: 560px;
        }
    }

    .carousel-login .carousel-item img {
        object-fit: cover;
    }

    .carousel-login .carousel-caption {
        left: 0;
        right: 0;
        bottom: 0;
        padding: 3.5rem 2rem 6.5rem;
        text-align: left;
        background: linear-gradient(to top, rgba(15, 23, 42, .85), rgba(15, 23, 42, 0));
    }

    .carousel-login .carousel-indicators-thumb {
        margin-bottom: 1.25rem;
    }

    .carousel-login .carousel-indicators-thumb [data-bs-target] {
        width: 3.25rem;
        border-radius: .375rem;
        background-size: cover;
        background-position: center;
        border: 2px solid rgba(255, 255, 255, .6);
    }

    .carousel-login .carousel-indicators-thumb .active {
        border-color: #fff;
    }
</style>
@stack('style')
