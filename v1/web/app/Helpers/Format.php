<?php

namespace App\Helpers;

use Carbon\CarbonInterface;

/** Format tampilan (padanan ui/data.py di induk). Hanya memformat; tidak menghitung angka pajak. */
final class Format
{
    public const BULAN = [1 => 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];

    public const BULAN_PANJANG = [1 => 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September',
        'Oktober', 'November', 'Desember'];

    public static function rp(mixed $v, bool $awalan = true): string
    {
        if ($v === null) {
            return '-';
        }
        if (is_bool($v)) {
            return $v ? 'ya' : 'tidak';
        }
        if (! is_int($v)) {
            return (string) $v;
        }
        $s = ($awalan ? 'Rp' : '').number_format(abs($v), 0, ',', '.');

        return $v < 0 ? '-'.$s : $s;
    }

    /** Tarif pecahan dari engine ("3/200") -> "1,5%". Eksak sampai 4 digit desimal; selebihnya ditandai "≈". */
    public static function persen(mixed $tarif): string
    {
        if ($tarif === null || $tarif === '') {
            return '-';
        }
        $s = (string) $tarif;
        if (preg_match('/^(-?\d+)\/(\d+)$/', $s, $m)) {
            return self::desimal((int) $m[1] * 100, (int) $m[2]).'%';
        }
        if (preg_match('/^-?\d+(\.\d+)?$/', $s)) {
            return str_replace('.', ',', Desimal::pecahanKePersen(ltrim($s, '-'))).'%';
        }

        return $s;
    }

    /** a / b dalam persen, mis. tarif efektif. */
    public static function rasio(?int $a, ?int $b, int $maks = 2): string
    {
        return ($a === null || ! $b) ? '-' : self::desimal($a * 100, $b, $maks).'%';
    }

    /** Nilai fakta engine apa pun: rupiah, tarif pecahan, bool, teks. */
    public static function nilai(mixed $v): string
    {
        if (is_string($v) && str_contains($v, '/')) {
            return self::persen($v);
        }

        return self::rp($v, false);
    }

    public static function bulan(?int $b, bool $panjang = false): string
    {
        if ($b === null) {
            return 'setahun';
        }

        return ($panjang ? self::BULAN_PANJANG : self::BULAN)[$b] ?? (string) $b;
    }

    public static function tanggal(?CarbonInterface $t): string
    {
        return $t ? $t->format('d/m/Y') : '-';
    }

    private static function desimal(int $pembilang, int $penyebut, int $maks = 4): string
    {
        $tanda = ($pembilang < 0) !== ($penyebut < 0) && $pembilang !== 0 ? '-' : '';
        $pembilang = abs($pembilang);
        $penyebut = abs($penyebut);
        $bulat = intdiv($pembilang, $penyebut);
        $sisa = $pembilang % $penyebut;
        $digit = '';
        for ($i = 0; $i < $maks && $sisa !== 0; $i++) {
            $sisa *= 10;
            $digit .= intdiv($sisa, $penyebut);
            $sisa %= $penyebut;
        }
        $teks = number_format($bulat, 0, ',', '.').($digit === '' ? '' : ','.$digit);

        return ($sisa !== 0 ? '≈ ' : '').$tanda.$teks;
    }
}
