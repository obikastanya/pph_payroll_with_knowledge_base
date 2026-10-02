@extends('layouts.app', ['judul' => $pegawai->exists ? 'Ubah pegawai' : 'Tambah pegawai'])
@use('App\Payroll\Label')

@section('isi')
    <h1 class="mb-5 text-2xl font-semibold">{{ $pegawai->exists ? 'Ubah data pegawai' : 'Tambah pegawai' }}</h1>

    <form method="POST" action="{{ $pegawai->exists ? route('pegawai.update', $pegawai) : route('pegawai.store') }}" class="card max-w-2xl space-y-5 p-6">
        @csrf
        @if ($pegawai->exists) @method('PUT') @endif

        <div class="grid gap-4 sm:grid-cols-3">
            <div>
                <label for="nomor_induk" class="label">Nomor induk</label>
                <input id="nomor_induk" name="nomor_induk" value="{{ old('nomor_induk', $pegawai->nomor_induk) }}" required
                       class="input @error('nomor_induk') input-error @enderror">
                @error('nomor_induk')<p class="galat">{{ $message }}</p>@enderror
            </div>
            <div class="sm:col-span-2">
                <label for="nama" class="label">Nama</label>
                <input id="nama" name="nama" value="{{ old('nama', $pegawai->nama) }}" required class="input @error('nama') input-error @enderror">
                @error('nama')<p class="galat">{{ $message }}</p>@enderror
            </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-3">
            <div>
                <label for="jenis_kelamin" class="label">Jenis kelamin</label>
                <select id="jenis_kelamin" name="jenis_kelamin" class="input">
                    @foreach (Label::JENIS_KELAMIN as $k => $v)
                        <option value="{{ $k }}" @selected(old('jenis_kelamin', $pegawai->jenis_kelamin) === $k)>{{ $v }}</option>
                    @endforeach
                </select>
            </div>
            <div>
                <label for="tanggal_masuk" class="label">Tanggal masuk kerja</label>
                <input id="tanggal_masuk" name="tanggal_masuk" type="date" required
                       value="{{ old('tanggal_masuk', $pegawai->tanggal_masuk?->toDateString()) }}"
                       class="input @error('tanggal_masuk') input-error @enderror">
                @error('tanggal_masuk')<p class="galat">{{ $message }}</p>@enderror
            </div>
            <div>
                <label for="tanggal_berhenti" class="label">Tanggal berhenti</label>
                <input id="tanggal_berhenti" name="tanggal_berhenti" type="date"
                       value="{{ old('tanggal_berhenti', $pegawai->tanggal_berhenti?->toDateString()) }}"
                       class="input @error('tanggal_berhenti') input-error @enderror">
                @error('tanggal_berhenti')<p class="galat">{{ $message }}</p>@enderror
                <p class="bantu">Kosongkan bila masih bekerja.</p>
            </div>
        </div>

        <label class="flex items-center gap-2 text-sm">
            <input type="hidden" name="punya_npwp" value="0">
            <input type="checkbox" name="punya_npwp" value="1" class="rounded border-slate-300" @checked(old('punya_npwp', $pegawai->punya_npwp))>
            Punya NPWP / NIK valid
        </label>

        <div class="flex gap-2 border-t border-slate-100 pt-5">
            <button class="btn btn-primary">Simpan</button>
            <a href="{{ $pegawai->exists ? route('pegawai.show', $pegawai) : route('pegawai.index') }}" class="btn btn-secondary">Batal</a>
        </div>
    </form>
@endsection
