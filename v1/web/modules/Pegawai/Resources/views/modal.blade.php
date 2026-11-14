@use('Modules\Payroll\Services\Label')
<div class="modal fade" data-bs-backdrop="static" data-bs-keyboard="false" id="pegawaiModal" tabindex="-1" aria-labelledby="pegawaiModalTitle" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-fullscreen-lg-down modal-dialog-centered">
        <div class="modal-content p-3">
            <button type="button" class="btn-close btn-pinned" data-bs-dismiss="modal" aria-label="Tutup"></button>
            <div class="modal-body p-0">
                <div class="mb-2">
                    <h3 class="modal-title mb-2" id="pegawaiModalTitle">Pegawai</h3>
                </div>
                <form id="pegawaiForm" novalidate>
                    <input type="hidden" name="id" id="pegawaiId">
                    <div class="row g-2">
                        <div class="col-12">
                            <div class="row">
                                <label for="nomor_induk" class="col-md-4 col-form-label required">Nomor induk</label>
                                <div class="col-md-5">
                                    <input type="text" id="nomor_induk" class="form-control" name="nomor_induk" placeholder="Nomor induk.." maxlength="32" required>
                                </div>
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="row">
                                <label for="nama" class="col-md-4 col-form-label required">Nama</label>
                                <div class="col-md-8">
                                    <input type="text" id="nama" class="form-control" name="nama" placeholder="Nama lengkap.." required>
                                </div>
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="row">
                                <label for="jenis_kelamin" class="col-md-4 col-form-label required">Jenis kelamin</label>
                                <div class="col-md-5">
                                    <select id="jenis_kelamin" name="jenis_kelamin" class="form-select" required>
                                        @foreach (Label::JENIS_KELAMIN as $k => $v)
                                            <option value="{{ $k }}">{{ $v }}</option>
                                        @endforeach
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="row">
                                <label for="tanggal_masuk" class="col-md-4 col-form-label required">Tanggal masuk kerja</label>
                                <div class="col-md-5">
                                    <input type="date" id="tanggal_masuk" class="form-control" name="tanggal_masuk" required>
                                </div>
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="row">
                                <label for="tanggal_berhenti" class="col-md-4 col-form-label">Tanggal berhenti</label>
                                <div class="col-md-5">
                                    <input type="date" id="tanggal_berhenti" class="form-control" name="tanggal_berhenti">
                                    <small class="form-hint">Kosongkan bila masih bekerja.</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="row">
                                <span class="col-md-4 col-form-label">NPWP / NIK</span>
                                <div class="col-md-8 pt-1">
                                    <label class="form-check form-switch mb-0">
                                        <input class="form-check-input" type="checkbox" id="punya_npwp" name="punya_npwp" value="1" checked>
                                        <span class="form-check-label">Punya NPWP / NIK valid</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div class="col-12 mt-3">
                            <div class="d-flex justify-content-end gap-2">
                                <x-global.btn-detail label="Perbarui" color="orange" size="sm" type="submit" id="pegawaiModalUpdateButton">
                                    <x-slot:icon><i class="ti ti-device-floppy"></i></x-slot:icon>
                                </x-global.btn-detail>
                                <x-global.btn-detail label="Simpan" color="blue" size="sm" type="submit" id="pegawaiModalSubmitButton">
                                    <x-slot:icon><i class="ti ti-device-floppy"></i></x-slot:icon>
                                </x-global.btn-detail>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

@push('javascript')
    <script>
        const urlPegawai = @json(url('pegawai'));
        let modePegawai = 'add';

        function bukaModalPegawai(mode, id) {
            modePegawai = mode;
            const form = $('#pegawaiForm');
            form[0].reset();
            form.find('.is-invalid').removeClass('is-invalid');
            $('#pegawaiId').val('');
            $('#pegawaiModalTitle').text(mode === 'add' ? 'Tambah pegawai' : 'Ubah data pegawai');
            $('#pegawaiModalSubmitButton').toggleClass('d-none', mode !== 'add');
            $('#pegawaiModalUpdateButton').toggleClass('d-none', mode === 'add');

            if (mode === 'edit') {
                $.get(`${urlPegawai}/${id}`).done(res => {
                    const d = res.data;
                    $('#pegawaiId').val(d.id);
                    ['nomor_induk', 'nama', 'jenis_kelamin', 'tanggal_masuk'].forEach(f => $(`#${f}`).val(d[f]));
                    $('#tanggal_berhenti').val(d.tanggal_berhenti || '');
                    $('#punya_npwp').prop('checked', !!d.punya_npwp);
                    bootstrap.Modal.getOrCreateInstance('#pegawaiModal').show();
                }).fail(showError);
            } else {
                bootstrap.Modal.getOrCreateInstance('#pegawaiModal').show();
            }
        }

        $('#pegawaiForm').on('submit', function(e) {
            e.preventDefault();
            const id = $('#pegawaiId').val();
            const data = {
                nomor_induk: $('#nomor_induk').val(),
                nama: $('#nama').val(),
                jenis_kelamin: $('#jenis_kelamin').val(),
                tanggal_masuk: $('#tanggal_masuk').val(),
                tanggal_berhenti: $('#tanggal_berhenti').val() || null,
                punya_npwp: $('#punya_npwp').is(':checked') ? 1 : 0,
            };
            const tombol = $(this).find('button[type="submit"]').prop('disabled', true);
            $(this).find('.is-invalid').removeClass('is-invalid');

            $.ajax({
                url: modePegawai === 'add' ? urlPegawai : `${urlPegawai}/${id}`,
                type: modePegawai === 'add' ? 'POST' : 'PUT',
                data,
                success: res => {
                    bootstrap.Modal.getOrCreateInstance('#pegawaiModal').hide();
                    Swal.fire({
                        icon: 'success',
                        title: 'Berhasil',
                        text: res.message,
                        timer: 2500,
                        showConfirmButton: false
                    });
                    if (typeof window.setelahSimpanPegawai === 'function') window.setelahSimpanPegawai(res);
                },
                error: xhr => {
                    Object.keys(xhr.responseJSON?.errors ?? {}).forEach(f => $(`#pegawaiForm [name="${f}"]`).addClass('is-invalid'));
                    showError(xhr);
                },
                complete: () => tombol.prop('disabled', false),
            });
        });
    </script>
@endpush
