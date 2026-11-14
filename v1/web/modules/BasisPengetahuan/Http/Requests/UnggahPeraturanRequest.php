<?php

namespace Modules\BasisPengetahuan\Http\Requests;

use App\Models\Kb\UsulanKb;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

/**
 * Unggahan dokumen peraturan untuk dibaca LLM. Batas 20 MB mengikuti batas dokumen asisten KB (asisten_kb/llm.py);
 * batas PHP (upload_max_filesize, post_max_size) bisa lebih kecil dan berlaku lebih dulu.
 */
class UnggahPeraturanRequest extends FormRequest
{
    public const BATAS_KB = 20480;

    public function rules(): array
    {
        return [
            'judul' => ['required', 'string', 'max:150'],
            'lapisan' => ['required', Rule::in(array_keys(UsulanKb::LAPISAN))],
            'catatan' => ['nullable', 'string', 'max:2000'],
            'pdf' => ['required', 'file', 'mimes:pdf', 'max:'.self::BATAS_KB],
        ];
    }

    public function attributes(): array
    {
        return ['judul' => 'judul dokumen', 'lapisan' => 'jenis peraturan', 'catatan' => 'catatan untuk LLM', 'pdf' => 'berkas PDF'];
    }

    public function messages(): array
    {
        return [
            'pdf.mimes' => 'Berkas harus PDF.',
            'pdf.max' => 'PDF paling besar 20 MB; pecah dokumen bila lebih besar.',
            'pdf.uploaded' => 'PDF gagal diunggah. Biasanya karena melebihi batas PHP di server (upload_max_filesize = '
                .(ini_get('upload_max_filesize') ?: '?').', post_max_size = '.(ini_get('post_max_size') ?: '?')
                .'); naikkan keduanya di php.ini atau pecah dokumen.',
        ];
    }

    /** Batas unggahan yang benar-benar berlaku (bita): yang terkecil dari 20 MB dan batas PHP di php.ini. */
    public static function batasEfektif(): int
    {
        $batas = [self::BATAS_KB * 1024];
        foreach (['upload_max_filesize', 'post_max_size'] as $kunci) {
            $b = self::bita((string) ini_get($kunci));
            if ($b > 0) {        // 0 = tanpa batas
                $batas[] = $b;
            }
        }

        return min($batas);
    }

    /** Nilai ukuran php.ini ("8M", "2G", "512K", "1048576") -> bita. */
    public static function bita(string $nilai): int
    {
        $nilai = trim($nilai);
        if ($nilai === '' || ! preg_match('/^(\d+)\s*([KMG]?)/i', $nilai, $m)) {
            return 0;
        }

        return (int) $m[1] * match (strtoupper($m[2])) {
            'K' => 1024,
            'M' => 1024 ** 2,
            'G' => 1024 ** 3,
            default => 1,
        };
    }
}
