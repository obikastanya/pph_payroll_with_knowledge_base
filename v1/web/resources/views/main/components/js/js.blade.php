<script src="{{ asset('assets/js/apps.min.js') }}" defer></script>
<script src="{{ asset('vendor/sweetalert/sweetalert.all.js') }}"></script>
<script src="{{ asset('assets/libs/jquery/jquery.min.js') }}"></script>
<script type="text/javascript">
    let csrf = '{{ csrf_token() }}';
    $.ajaxSetup({
        headers: {
            'X-CSRF-TOKEN': csrf,
            'Accept': 'application/json',
        }
    });
</script>

{{-- Utils --}}
<script>
    function debounce(func, timeout = 350) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), timeout);
        };
    }

    /** Teks dari server/isian pengguna sebelum disisipkan ke HTML. */
    function escapeHtml(value) {
        return String(value ?? '').replace(/[&<>"']/g, c => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        } [c]));
    }

    /** Rupiah bulat (int) -> "1.234.567"; tanpa float, angka tetap dari server. */
    function formatRupiah(value, awalan = false) {
        if (value === null || value === undefined || value === '') return '-';
        const n = String(value);
        const negatif = n.startsWith('-');
        const digit = negatif ? n.slice(1) : n;
        const teks = digit.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return (negatif ? '-' : '') + (awalan ? 'Rp' : '') + teks;
    }

    /** Galat dari respons AJAX Laravel (422 validasi, 4xx/5xx lain). */
    const showError = (xhr) => {
        const json = xhr?.responseJSON ?? {};
        let pesan = [];
        if (json.errors) {
            pesan = Object.values(json.errors).flat();
        } else if (json.message) {
            pesan = [json.message];
        } else {
            pesan = ['Terjadi kesalahan. Silakan coba lagi.'];
        }
        Swal.fire({
            icon: 'error',
            title: 'Maaf!',
            html: pesan.map(escapeHtml).join('<br>'),
        });
    };

    /** Konfirmasi SweetAlert sebelum form dikirim: <form data-konfirmasi="Teks?" data-konfirmasi-tombol="Hapus"> */
    $(document).on('submit', 'form[data-konfirmasi]', function(e) {
        const form = this;
        if (form.dataset.terkonfirmasi) return;
        e.preventDefault();
        Swal.fire({
            title: form.dataset.konfirmasi,
            text: form.dataset.konfirmasiTeks || '',
            icon: form.dataset.konfirmasiIkon || 'question',
            showCancelButton: true,
            confirmButtonText: form.dataset.konfirmasiTombol || 'Ya, lanjutkan',
            cancelButtonText: 'Batal',
            reverseButtons: true,
        }).then(result => {
            if (result.isConfirmed) {
                form.dataset.terkonfirmasi = '1';
                // form.submit() tidak memicu event submit, jadi pemuat data-proses dipasang di sini
                if (form.dataset.proses) {
                    kunciTombolProses(form);
                } else {
                    $(form).find('button[type="submit"]').prop('disabled', true);
                }
                form.submit();
            }
        });
    });

    function kunciTombolProses(form) {
        $(form).find('button[type="submit"]').prop('disabled', true)
            .html('<span class="spinner-border spinner-border-sm me-2"></span>' + escapeHtml(form.dataset.proses));
    }

    /** Tombol proses panjang (memanggil engine): kunci tombol & tampilkan memuat. */
    $(document).on('submit', 'form[data-proses]', function() {
        // form yang juga meminta konfirmasi: tunggu jawaban dialog; bila dibatalkan tombol tidak boleh terkunci
        if (this.dataset.konfirmasi !== undefined && !this.dataset.terkonfirmasi) return;
        kunciTombolProses(this);
    });
</script>

{{-- Tabel AJAX (pola Base-Apps-Merdeka): renderTableWithFeatures + pagination + sorting --}}
<script>
    function renderTableWithFeatures({
        container,
        data = [],
        columns = [],
        currentPage = 1,
        limit = 10,
        emptyText = 'Data tidak ditemukan',
        loading = false,
        meta = null,
        onPageChange = () => {},
        onLimitChange = () => {},
        onSortChange = () => {},
        currentSortKey = null,
        currentSortDir = 'asc',
        paginationContainer = '.pagination-container',
    }) {
        renderTable({
            container,
            data,
            columns,
            currentPage,
            limit,
            emptyText,
            loading
        });

        if (!loading && meta) {
            renderPagination({
                meta,
                limit,
                container: paginationContainer,
                onPageChange,
                onLimitChange
            });
        }

        if (!loading) {
            initSorting({
                container,
                columns,
                currentSortKey,
                currentSortDir,
                onSortChange
            });
        }
    }

    /**
     * columns: 'index' | 'kunci' | { key, className, render(item, index) }.
     * Nilai tanpa render di-escape; render() bertanggung jawab meng-escape isian pengguna (escapeHtml).
     */
    function renderTable({
        container,
        data = [],
        columns = [],
        currentPage = 1,
        limit = 10,
        emptyText = 'Data tidak ditemukan',
        loading = false
    }) {
        const tbody = $(`${container} tbody`);

        if (loading) {
            tbody.html(`<tr><td colspan="${columns.length}" class="text-center text-muted py-4">
                <span class="spinner-border spinner-border-sm me-2"></span>Memuat…</td></tr>`);
            return;
        }

        if (!data || data.length == 0) {
            tbody.html(`<tr><td colspan="${columns.length}" class="text-center text-muted py-4">${escapeHtml(emptyText)}</td></tr>`);
            return;
        }

        const startNumber = (currentPage - 1) * limit + 1;
        let html = '';
        data.forEach((item, index) => {
            html += '<tr>';
            columns.forEach(col => {
                if (col === 'index') {
                    html += `<td class="text-center">${startNumber + index}</td>`;
                } else if (typeof col === 'object') {
                    const value = typeof col.render === 'function' ? col.render(item, index) : escapeHtml(item[col.key]);
                    html += `<td class="${col.className || ''}">${value}</td>`;
                } else {
                    html += `<td>${escapeHtml(item[col])}</td>`;
                }
            });
            html += '</tr>';
        });
        tbody.html(html);
    }

    function renderPagination({
        meta,
        container = '.pagination-container',
        onPageChange = () => {},
        onLimitChange = () => {},
        limit = 10
    }) {
        const el = $(container);
        if (!meta || meta.total === 0) {
            return el.hide();
        }

        let html = `<div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
            <div class="d-flex flex-row justify-content-start align-items-center gap-2">`;
        const prevDisabled = meta.current_page <= 1 ? 'pe-none disabled text-muted' : 'cursor-pointer';
        html += `<a class="btn-previous text-decoration-none ${prevDisabled}" data-page="${meta.current_page - 1}"><i class="ti ti-chevron-left"></i></a>`;
        html += `<a data-page="1" class="btn-pagination cursor-pointer text-decoration-none ${meta.current_page === 1 ? 'mdka-btn-blue-500 text-white' : ''}">1</a>`;
        if (meta.current_page > 4) html += `<span>…</span>`;
        if (meta.last_page > 2) {
            const start = Math.max(meta.current_page - 2, 2);
            const end = Math.min(meta.current_page + 2, meta.last_page - 1);
            for (let i = start; i <= end; i++) {
                html += `<a data-page="${i}" class="btn-pagination cursor-pointer text-decoration-none ${meta.current_page === i ? 'mdka-btn-blue-500 text-white' : ''}">${i}</a>`;
            }
        }
        if (meta.current_page < meta.last_page - 3) html += `<span>…</span>`;
        if (meta.last_page > 1) {
            html += `<a data-page="${meta.last_page}" class="btn-pagination cursor-pointer text-decoration-none ${meta.current_page === meta.last_page ? 'mdka-btn-blue-500 text-white' : ''}">${meta.last_page}</a>`;
        }
        const nextDisabled = meta.current_page >= meta.last_page ? 'pe-none disabled text-muted' : 'cursor-pointer';
        html += `<a class="btn-next text-decoration-none ${nextDisabled}" data-page="${meta.current_page + 1}"><i class="ti ti-chevron-right"></i></a>`;
        html += `</div>
            <div class="d-flex flex-row justify-content-end align-items-center gap-2 text-muted">
                <div class="mb-0 text-nowrap">Menampilkan ${meta.from || 0}–${meta.to || 0} dari ${meta.total}</div>
                <div class="mb-0 text-nowrap">Tampil:</div>
                <select class="form-select form-select-sm pagination-limit">
                    ${[10, 25, 50, 100].map(n => `<option value="${n}" ${limit == n ? 'selected' : ''}>${n}</option>`).join('')}
                </select>
            </div>
        </div>`;

        el.html(html).show();
        el.find('.btn-pagination, .btn-previous, .btn-next').off('click').on('click', function() {
            const page = $(this).data('page');
            if (page) onPageChange(page);
        });
        el.find('.pagination-limit').off('change').on('change', function() {
            onLimitChange(parseInt($(this).val(), 10));
        });
    }

    function initSorting({
        container,
        columns = [],
        currentSortKey = null,
        currentSortDir = 'asc',
        onSortChange = () => {}
    }) {
        const table = $(container);
        columns.forEach(col => {
            if (typeof col === 'object' && col.key && col.sortable) {
                const th = table.find(`th[data-key="${col.key}"]`);
                if (!th.length) return;
                if (!th.data('label')) th.data('label', th.text().trim());
                let icon = '<i class="ti ti-selector text-muted"></i>';
                if (currentSortKey === col.key) {
                    icon = currentSortDir === 'asc' ? '<i class="ti ti-chevron-up"></i>' : '<i class="ti ti-chevron-down"></i>';
                }
                th.html(`<div class="d-flex align-items-center w-100 cursor-pointer gap-1">
                    <span class="flex-grow-1 text-wrap ${col.headerClassName || ''}">${escapeHtml(th.data('label'))}</span>
                    <span class="sort-icon small">${icon}</span></div>`);
                th.addClass('sortable').off('click').on('click', () => {
                    const newDir = (currentSortKey === col.key && currentSortDir === 'asc') ? 'desc' : 'asc';
                    onSortChange(col.key, newDir);
                });
            }
        });
    }
</script>

<script>
    $(function() {
        $('[data-bs-toggle="tooltip"]').tooltip({
            trigger: 'hover'
        });
        $(document).on('click', '[data-bs-toggle="tooltip"]', function() {
            $(this).tooltip('hide');
        });
    });
</script>

@stack('javascript')
