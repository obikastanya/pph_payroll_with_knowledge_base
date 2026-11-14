<div class="card" id="pegawaiFilterCard" style="display: none;">
    <div class="card-header p-2">
        <h4 class="mb-0">Filter</h4>
    </div>
    <div class="card-body p-2">
        <div class="row g-2">
            <div class="col-md-3">
                <label for="statusFilter" class="form-label">Status kerja</label>
                <select id="statusFilter" class="form-select">
                    <option value="">Semua</option>
                    <option value="aktif">Masih bekerja</option>
                    <option value="berhenti">Sudah berhenti</option>
                </select>
            </div>
            <div class="col-md-3">
                <label for="jenisKelaminFilter" class="form-label">Jenis kelamin</label>
                <select id="jenisKelaminFilter" class="form-select">
                    <option value="">Semua</option>
                    @foreach (\Modules\Payroll\Services\Label::JENIS_KELAMIN as $k => $v)
                        <option value="{{ $k }}">{{ $v }}</option>
                    @endforeach
                </select>
            </div>
            <div class="col-12 mt-3 d-flex justify-content-start gap-2">
                <x-global.btn-detail label="" color="red" size="sm" outline="true" data-bs-toggle="tooltip" onclick="resetFilter()" data-bs-title="Kosongkan">
                    <x-slot:icon><i class="ti ti-x"></i></x-slot:icon>
                </x-global.btn-detail>
                <x-global.btn-detail label="" color="green" size="sm" outline="true" data-bs-toggle="tooltip" onclick="applyFilter()" data-bs-title="Terapkan filter">
                    <x-slot:icon><i class="ti ti-check"></i></x-slot:icon>
                </x-global.btn-detail>
            </div>
        </div>
    </div>
</div>

@push('javascript')
    {{-- Filter --}}
    <script>
        let filterList = {
            status: null,
            jenis_kelamin: null,
        };

        const applyFilter = () => {
            filterList = {
                status: $('#statusFilter').val() || null,
                jenis_kelamin: $('#jenisKelaminFilter').val() || null,
            };
            currentPage = 1;
            pegawaiTable();
        };

        const resetFilter = () => {
            $('#statusFilter, #jenisKelaminFilter').val('');
            applyFilter();
        };
    </script>
@endpush
