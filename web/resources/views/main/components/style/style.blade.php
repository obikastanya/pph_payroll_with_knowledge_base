<link href="{{ asset('assets/css/apps.min.css') }}" rel="stylesheet" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@2.36.0/tabler-icons.min.css">
<link href="{{ asset('assets/css/fonts/fonts.css') }}" rel="stylesheet" />
<link href="{{ asset('assets/css/custom.css') }}" rel="stylesheet" />
@stack('style')
<style>
    body {
        font-feature-settings: "cv03", "cv04", "cv11";
        font-size: 13px;
    }

    tbody {
        font-size: 0.75rem !important;
    }

    .form-control,
    .form-control-plaintext,
    .form-select,
    .input-group-text,
    .col-form-label {
        padding: .375rem .75rem;
        background-position: right .35rem center;
        background-size: 14px 9px;
    }

    .form-select {
        padding-right: 2rem;
    }

    .table thead th {
        font-weight: bolder;
        color: #000;
        font-size: 0.75rem;
        text-transform: capitalize !important;
    }

    .form-control,
    .form-select,
    .form-control-plaintext,
    .input-group-text,
    .form-check-input,
    .form-check-label,
    input[type="date"] {
        font-size: 0.75rem;
    }

    .form-label,
    .col-form-label {
        font-size: 0.75rem;
    }

    input::placeholder,
    textarea::placeholder {
        font-style: italic !important;
    }

    .form-check-label {
        padding-top: 0.175rem;
    }

    .btn-pagination,
    .btn-previous,
    .btn-next {
        min-width: 28px;
        height: 28px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: .375rem;
        color: var(--mdka-gray-700);
        font-size: .75rem;
    }

    .pagination-limit {
        width: 68px !important;
    }

    .dropdown-item {
        font-size: 0.8rem;
    }

    .navbar-vertical {
        overflow: auto !important;
    }

    .navbar-expand-lg {
        transition: width 0.2s ease-in-out;
    }

    .page-wrapper,
    .navbar-expand-md {
        transition: margin-left 0.2s ease-in-out;
    }

    .brand-teks {
        line-height: 1.15;
    }

    /* Tabel angka rupiah: rata kanan, digit sejajar */
    .angka {
        text-align: right;
        white-space: nowrap;
        font-variant-numeric: tabular-nums;
    }

    .baris-judul td {
        background: var(--mdka-gray-50);
        font-size: .65rem;
        font-weight: 700;
        letter-spacing: .04em;
        text-transform: uppercase;
        color: var(--mdka-gray-600);
    }

    .cursor-pointer {
        cursor: pointer;
    }
</style>
