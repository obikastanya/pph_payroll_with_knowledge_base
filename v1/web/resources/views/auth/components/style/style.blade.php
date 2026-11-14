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
        padding: 4rem 2.5rem 4rem;
        text-align: left;
        background: linear-gradient(to top, rgba(15, 23, 42, .85), rgba(15, 23, 42, 0));
    }

    /* Indikator garis: rata kiri sejajar keterangan; garis aktif lebih panjang dan terisi selama slide tampil */
    .carousel-login .indikator-garis {
        justify-content: flex-start;
        margin: 0 2.5rem 2rem;
        gap: .5rem;
    }

    .carousel-login .indikator-garis [data-bs-target] {
        position: relative;
        flex: 0 0 auto;
        width: 1.75rem;
        height: 4px;
        margin: 0;
        padding: 0;
        border: 0;
        border-radius: 999px;
        background-color: rgba(255, 255, 255, .35);
        opacity: 1;
        overflow: hidden;
        transition: width .4s ease, background-color .2s ease;
    }

    .carousel-login .indikator-garis [data-bs-target]:hover {
        background-color: rgba(255, 255, 255, .6);
    }

    .carousel-login .indikator-garis .active {
        width: 3.5rem;
    }

    .carousel-login.berjalan .indikator-garis .active::after {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background-color: #fff;
        transform-origin: left center;
        animation: isi-garis var(--durasi-slide, 5s) linear forwards;
    }

    @keyframes isi-garis {
        from {
            transform: scaleX(0);
        }

        to {
            transform: scaleX(1);
        }
    }

    /* Tanpa animasi (preferensi pengguna): garis aktif langsung penuh */
    @media (prefers-reduced-motion: reduce) {
        .carousel-login.berjalan .indikator-garis .active::after {
            animation: none;
        }
    }
</style>
@stack('style')
