<?php

namespace Modules\BasisPengetahuan\Http\Requests;

use App\Models\Kb\UsulanKb;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

/** Unggahan dokumen peraturan untuk dibaca LLM. Batas 30 MB mengikuti batas dokumen PDF API (asisten_kb/llm.py). */
class UnggahPeraturanRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'judul' => ['required', 'string', 'max:150'],
            'lapisan' => ['required', Rule::in(array_keys(UsulanKb::LAPISAN))],
            'catatan' => ['nullable', 'string', 'max:2000'],
            'pdf' => ['required', 'file', 'mimes:pdf', 'max:30720'],
        ];
    }

    public function attributes(): array
    {
        return ['judul' => 'judul dokumen', 'lapisan' => 'jenis peraturan', 'catatan' => 'catatan untuk LLM', 'pdf' => 'berkas PDF'];
    }

    public function messages(): array
    {
        return ['pdf.mimes' => 'Berkas harus PDF.', 'pdf.max' => 'PDF paling besar 30 MB; pecah dokumen bila lebih besar.'];
    }
}
