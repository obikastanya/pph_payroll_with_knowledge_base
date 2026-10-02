<?php

namespace App\Http\Requests;

use App\Payroll\Label;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class PegawaiRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'nomor_induk' => ['required', 'string', 'max:32', Rule::unique('pegawai')->ignore($this->route('pegawai'))],
            'nama' => ['required', 'string', 'max:255'],
            'jenis_kelamin' => ['required', Rule::in(array_keys(Label::JENIS_KELAMIN))],
            'punya_npwp' => ['boolean'],
            'tanggal_masuk' => ['required', 'date'],
            'tanggal_berhenti' => ['nullable', 'date', 'after_or_equal:tanggal_masuk'],
        ];
    }

    public function attributes(): array
    {
        return ['nomor_induk' => 'nomor induk', 'jenis_kelamin' => 'jenis kelamin', 'punya_npwp' => 'NPWP/NIK',
            'tanggal_masuk' => 'tanggal masuk', 'tanggal_berhenti' => 'tanggal berhenti'];
    }

    public function dataPegawai(): array
    {
        return ['punya_npwp' => $this->boolean('punya_npwp')] + $this->validated();
    }
}
