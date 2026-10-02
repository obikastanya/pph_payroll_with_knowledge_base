<?php

namespace App\Support;

use InvalidArgumentException;

/**
 * Bilangan desimal sebagai teks, digeser lewat manipulasi digit: eksak, tanpa float (kontrak presisi induk §6.9).
 * Dipakai untuk persen kompensasi ("10" persen <-> "0.1" pecahan untuk engine) dan tarif JKK ("0,24" -> "0.24").
 */
final class Desimal
{
    /** Teks desimal kanonik ("0,240" -> "0.24", "007" -> "7"); kosong -> null; selain angka >= 0 ditolak. */
    public static function normal(?string $teks): ?string
    {
        $s = str_replace(',', '.', trim((string) $teks));
        if ($s === '') {
            return null;
        }
        if (! preg_match('/^(\d+)(?:\.(\d+))?$/', $s, $m)) {
            throw new InvalidArgumentException("'{$teks}' bukan angka desimal");
        }

        return self::susun($m[1], $m[2] ?? '');
    }

    /** "10" (persen) -> "0.1"; "12,5" -> "0.125". */
    public static function persenKePecahan(string $persen): string
    {
        return self::geser(self::normal($persen) ?? '0', -2);
    }

    /** "0.1" -> "10"; "0.125" -> "12.5". */
    public static function pecahanKePersen(string $pecahan): string
    {
        return self::geser(self::normal($pecahan) ?? '0', 2);
    }

    /** Jumlah digit di belakang koma. */
    public static function digitDesimal(string $teks): int
    {
        $n = self::normal($teks) ?? '0';
        $titik = strpos($n, '.');

        return $titik === false ? 0 : strlen($n) - $titik - 1;
    }

    private static function geser(string $normal, int $langkah): string
    {
        [$bulat, $pecahan] = array_pad(explode('.', $normal, 2), 2, '');
        $digit = $bulat.$pecahan;
        $posisi = strlen($bulat) + $langkah;
        if ($posisi <= 0) {
            return self::susun('0', str_repeat('0', -$posisi).$digit);
        }
        if ($posisi >= strlen($digit)) {
            return self::susun($digit.str_repeat('0', $posisi - strlen($digit)), '');
        }

        return self::susun(substr($digit, 0, $posisi), substr($digit, $posisi));
    }

    private static function susun(string $bulat, string $pecahan): string
    {
        $bulat = ltrim($bulat, '0');
        $pecahan = rtrim($pecahan, '0');

        return ($bulat === '' ? '0' : $bulat).($pecahan === '' ? '' : '.'.$pecahan);
    }
}
