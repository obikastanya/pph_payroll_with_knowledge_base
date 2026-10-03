<?php

namespace App\Http\Middleware;

use Illuminate\Foundation\Http\Middleware\TransformsRequest;

/**
 * Teks isian yang ditolak PostgreSQL (galat 500 saat menyimpan atau mencari dengan LIKE): byte NUL dibuang dan UTF-8
 * yang tidak sah diganti (mb_scrub). Berlaku untuk query dan isi form/JSON termasuk larik bersarang, tidak untuk berkas
 * unggahan. Kata sandi tidak diubah, sama dengan pengecualian TrimStrings.
 */
class BersihkanTeks extends TransformsRequest
{
    public const KECUALI = ['current_password', 'password', 'password_confirmation'];

    protected function transform($key, $value)
    {
        if (! is_string($value) || in_array($key, self::KECUALI, true)) {
            return $value;
        }

        return str_replace("\0", '', mb_scrub($value, 'UTF-8'));
    }
}
