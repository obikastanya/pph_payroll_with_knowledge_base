<footer class="footer footer-transparent d-print-none">
    <div class="container-xl">
        <div class="row text-center align-items-center flex-row-reverse">
            <div class="hr mb-3 mt-0"></div>
            <div class="col-12 text-center d-flex flex-wrap justify-content-center align-items-center gap-1">
                Copyright &copy; {{ date('Y') }}, {{ config('app.name') }}. Angka dihitung oleh engine knowledge base.
                <a href="{{ route('mesin.index') }}" class="badge mdka-bg-gray-700 text-white rounded-2 ms-2">v1.0.0</a>
            </div>
        </div>
    </div>
</footer>
