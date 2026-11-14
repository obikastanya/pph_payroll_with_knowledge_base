<?php

namespace Tests\Unit;

use App\Helpers\Desimal;
use App\Helpers\Format;
use InvalidArgumentException;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

class DesimalTest extends TestCase
{
    public static function persen(): array
    {
        return [['10', '0.1'], ['12,5', '0.125'], ['100', '1'], ['5', '0.05'], ['0', '0'], ['0.000001', '0.00000001'], ['250', '2.5']];
    }

    #[DataProvider('persen')]
    public function test_persen_bolak_balik_eksak(string $persen, string $pecahan): void
    {
        $this->assertSame($pecahan, Desimal::persenKePecahan($persen));
        $this->assertSame(Desimal::normal($persen), Desimal::pecahanKePersen($pecahan));
    }

    public function test_normal(): void
    {
        $this->assertSame('0.24', Desimal::normal(' 0,240 '));
        $this->assertSame('7', Desimal::normal('007'));
        $this->assertNull(Desimal::normal(''));
        $this->assertSame(3, Desimal::digitDesimal('1.125'));
    }

    public function test_menolak_bukan_angka(): void
    {
        $this->expectException(InvalidArgumentException::class);
        Desimal::normal('-1');
    }

    public function test_format_tarif_dan_rupiah(): void
    {
        $this->assertSame('1,5%', Format::persen('3/200'));
        $this->assertSame('2,5%', Format::persen('1/40'));
        $this->assertSame('≈ 33,3333%', Format::persen('1/3'));
        $this->assertSame('Rp7.341.750', Format::rp(7_341_750));
        $this->assertSame('-209.880', Format::rp(-209_880, false));
        $this->assertSame('ya', Format::nilai(true));
    }
}
