<?php

namespace Modules\Payroll\Services;

use App\Helpers\Format;

/**
 * Menata keluaran engine untuk halaman hasil (padanan ui/hasil.py di induk). Semua angka dibaca dari keluaran
 * engine; di sini hanya pemilihan baris, label, dan penunjukan dasar aturan/pasal dari jejak inferensi.
 */
final class TampilanHasil
{
    private array $jejakIndeks = [];

    public function __construct(public readonly array $h, public readonly array $kasus)
    {
        foreach ($h['jejak'] ?? [] as $j) {
            $this->jejakIndeks[$j['fakta'].'|'.($j['bulan'] ?? '-')] ??= $j;
        }
    }

    public function bulan(): array
    {
        $b = array_keys($this->h['per_masa']);
        sort($b);

        return $b;
    }

    public function masa(int $b): array
    {
        return $this->h['per_masa'][$b] ?? [];
    }

    /** Dasar sebuah angka: aturan KB yang menghasilkannya + pasal/kebijakan sumbernya. */
    public function dasar(string $fakta, ?int $bulan): ?array
    {
        $j = $this->jejakIndeks[$fakta.'|'.($bulan ?? '-')] ?? null;
        if ($j === null) {
            return $bulan !== null ? $this->dasar($fakta, null) : null;
        }

        return [
            'pendek' => ($j['lapisan'] === 'perusahaan' ? 'Perusahaan' : 'Regulasi').' · '.$j['aturan'],
            'panjang' => $j['sumber'],
            'lapisan' => $j['lapisan'],
        ];
    }

    public function ringkasan(): array
    {
        $t = $this->h['tahunan'];
        $pm = $this->h['per_masa'];
        $jumlah = fn (string $f) => array_sum(array_map(fn ($m) => $m[$f] ?? 0, $pm));
        $kartu = [
            ['PPh 21 setahun', Format::rp($t['pph21_setahun'] ?? $jumlah('pph21')), 'PPh 21 terutang satu tahun pajak'],
            ['Take home pay setahun', Format::rp($jumlah('px_thp')), 'Penghasilan tunai - iuran pegawai - PPh 21 dipotong'],
            ['Penghasilan bruto', Format::rp($t['bruto_setahun'] ?? null), 'Dasar pengenaan pajak, termasuk premi BPJS yang dibayar perusahaan'],
            ['Tarif efektif', Format::rasio($t['pph21_setahun'] ?? null, $t['bruto_setahun'] ?? null), 'PPh 21 setahun / penghasilan bruto'],
        ];
        if ($dtp = $jumlah('pph21_dtp')) {
            $kartu[] = ['Ditanggung pemerintah (DTP)', Format::rp($dtp), 'PPh 21 DTP dibayarkan tunai ke pegawai'];
        }

        return $kartu;
    }

    /** Baris slip gaji satu bulan: {uraian, nilai, tanda, dasar, judul, tebal}. */
    public function slip(int $b): array
    {
        $m = $this->masa($b);
        $hr = $this->kasus['data_hr']['per_masa'][$b] ?? $this->kasus['data_hr']['per_masa'][(string) $b] ?? [];
        $rows = [];
        $judul = function (string $teks) use (&$rows) {
            $rows[] = ['uraian' => $teks, 'judul' => true];
        };
        $baris = function (string $uraian, ?string $fakta, string $tanda = '', bool $tebal = false) use (&$rows, $m, $b) {
            $rows[] = ['uraian' => $uraian, 'nilai' => $fakta ? ($m[$fakta] ?? null) : null, 'tanda' => $tanda,
                'dasar' => $fakta ? $this->dasar($fakta, $b) : null, 'judul' => false, 'tebal' => $tebal];
        };

        $judul('Penghasilan');
        $hadir = ($hr['hk_aktual'] ?? null) !== ($hr['hk_penuh'] ?? null) ? " ({$hr['hk_aktual']}/{$hr['hk_penuh']} hari kerja)" : '';
        $baris("Gaji{$hadir}", 'px_gaji');
        foreach (['px_tunjangan' => 'Tunjangan', 'px_thr' => 'THR', 'px_kompensasi' => 'Kompensasi', 'px_ota' => 'Insentif OTA',
            'px_lembur' => 'Lembur', 'px_komisi' => 'Komisi', 'tunjangan_pajak' => 'Tunjangan pajak (gross-up)'] as $f => $lbl) {
            if (! empty($m[$f])) {
                $baris($lbl, $f);
            }
        }
        $judul('Ditanggung perusahaan (menambah bruto, tidak dibayar tunai)');
        foreach (['px_premi_jkk' => 'Premi JKK', 'px_premi_jkm' => 'Premi JKM', 'px_premi_kes' => 'Premi BPJS Kesehatan'] as $f => $lbl) {
            $baris($lbl, $f);
        }
        $baris('Penghasilan bruto (dasar pajak)', array_key_exists('bruto_total_masa', $m) ? 'bruto_total_masa' : 'bruto', '', true);
        $judul('Potongan');
        foreach (['px_iuran_jht_pg' => 'Iuran JHT pegawai', 'px_iuran_jp_pg' => 'Iuran JP pegawai',
            'px_iuran_kes_pg' => 'Iuran BPJS Kesehatan pegawai'] as $f => $lbl) {
            $baris($lbl, $f, '-');
        }
        $baris($this->keteranganPph($m, $b), 'pph21', ($m['pph21'] ?? 0) >= 0 ? '-' : '');
        if (! empty($m['pph21_dtp'])) {
            $baris('PPh 21 ditanggung pemerintah (dibayar tunai)', 'pph21_dtp', '+');
        }
        $baris('Take home pay', 'px_thp', '', true);

        return $rows;
    }

    private function keteranganPph(array $m, int $b): string
    {
        if (! empty($m['tarif_ter'])) {
            return 'PPh 21 (TER kategori '.($m['kategori_ter'] ?? '').' '.Format::persen($m['tarif_ter']).' × bruto)';
        }
        $terakhir = $this->kasus['pegawai']['bulan_terakhir_bekerja'] ?? 12;
        if ($b === $terakhir && array_key_exists('pph21_setahun', $this->h['tahunan'])) {
            return 'PPh 21 masa terakhir (PPh setahun - yang sudah dipotong)';
        }

        return 'PPh 21';
    }

    /** Perhitungan setahun gaya 1721-A1, termasuk rincian Pasal 17 per lapisan. */
    public function setahun(): array
    {
        $t = $this->h['tahunan'];
        $rows = [];
        $tambah = function (string $uraian, string $f, string $tanda = '', bool $tebal = false) use (&$rows, $t) {
            if (array_key_exists($f, $t)) {
                $rows[] = ['uraian' => $uraian, 'nilai' => $t[$f], 'tanda' => $tanda, 'dasar' => $this->dasar($f, null), 'tebal' => $tebal];
            }
        };
        $tambah('Penghasilan bruto setahun', 'bruto_setahun', '', true);
        $tambah('Biaya jabatan (5%, maks. Rp500.000 sebulan)', 'biaya_jabatan', '-');
        $tambah('Iuran pensiun/JHT/JP pegawai', 'iuran_pengurang', '-');
        if (! empty($t['zakat'])) {
            $tambah('Zakat / sumbangan keagamaan wajib', 'zakat', '-');
        }
        $tambah('Penghasilan neto', 'neto_setahun', '', true);
        if (isset($t['neto_disetahunkan']) && $t['neto_disetahunkan'] !== ($t['neto_setahun'] ?? null)) {
            $tambah('Penghasilan neto disetahunkan', 'neto_disetahunkan');
        }
        $tambah('PTKP ('.($t['status_ptkp_efektif'] ?? $this->kasus['pegawai']['status_ptkp']).')', 'ptkp', '-');
        $tambah('Penghasilan kena pajak (dibulatkan ke bawah ribuan)', 'pkp', '', true);
        $faktaP17 = array_key_exists('pph21_disetahunkan', $t) ? 'pph21_disetahunkan' : 'pph21_setahun';
        foreach ($this->rincianPasal17()['lapisan'] ?? [] as $l) {
            $atas = $l['atas'] === null ? '∞' : Format::rp($l['atas'], false);
            $rows[] = ['uraian' => 'Pasal 17: '.Format::persen($l['tarif']).' × '.Format::rp($l['dasar'], false)
                .' (lapisan '.Format::rp($l['bawah'], false).' – '.$atas.')', 'nilai' => $l['pajak'], 'tanda' => '',
                'dasar' => ['pendek' => $this->dasar($faktaP17, null)['pendek'] ?? '', 'panjang' => 'UU PPh Ps. 17(1)a (tarif progresif per lapisan)',
                    'lapisan' => 'regulasi'], 'tebal' => false, 'sub' => true];
        }
        $tambah('PPh 21 atas penghasilan disetahunkan', 'pph21_disetahunkan');
        $tambah('PPh 21 terutang setahun', 'pph21_setahun', '', true);
        $tambah('Sudah dipotong masa sebelumnya', 'pph21_dipotong_sebelumnya', '-');
        $tambah('PPh 21 masa pajak terakhir (negatif = lebih bayar)', 'pph21_masa_terakhir', '', true);
        if (! empty($t['lebih_bayar_dikembalikan'])) {
            $tambah('Lebih bayar dikembalikan ke pegawai', 'lebih_bayar_dikembalikan');
        }

        return $rows;
    }

    public function rincianPasal17(): ?array
    {
        foreach ($this->h['rincian_pasal17'] ?? [] as $r) {
            if ($r['bulan'] === null && in_array($r['fakta'], ['pph21_disetahunkan', 'pph21_setahun'], true)) {
                return $r;
            }
        }

        return null;
    }

    /** Ringkasan 12 bulan: kolom DTP & tunjangan pajak hanya bila ada. */
    public function bulanan(): array
    {
        $pm = $this->h['per_masa'];
        $adaDtp = (bool) array_filter($pm, fn ($m) => ! empty($m['pph21_dtp']));
        $adaTunj = (bool) array_filter($pm, fn ($m) => ! empty($m['tunjangan_pajak']));
        $rows = [];
        foreach ($this->bulan() as $b) {
            $m = $pm[$b];
            $rows[] = [
                'bulan' => $b,
                'bruto' => $m['bruto_total_masa'] ?? $m['bruto'] ?? null,
                'ter' => ! empty($m['tarif_ter']) ? trim(($m['kategori_ter'] ?? '').' '.Format::persen($m['tarif_ter'])) : '-',
                'pph21' => $m['pph21'] ?? null,
                'dtp' => $adaDtp ? ($m['pph21_dtp'] ?? 0) : null,
                'tunjangan_pajak' => $adaTunj ? ($m['tunjangan_pajak'] ?? 0) : null,
                'thp' => $m['px_thp'] ?? null,
            ];
        }

        return ['baris' => $rows, 'dtp' => $adaDtp, 'tunjangan_pajak' => $adaTunj];
    }

    /** Peringatan engine dalam bahasa admin: [{jenis: warning|info, teks}]. */
    public function peringatan(): array
    {
        $hasil = [];
        $tidakDiatur = [];
        foreach ($this->h['peringatan'] ?? [] as $p) {
            $kode = $p['kode'] ?? '';
            if ($kode === 'KLASIFIKASI_TIDAK_DIATUR') {
                $tidakDiatur[] = Label::fakta($p['fakta']).' ('.str_replace('_', ' ', $p['kategori_perusahaan']).')';

                continue;
            }
            $hasil[] = match ($kode) {
                'KONFLIK_WAJIB' => ['jenis' => 'warning', 'judul' => 'Konflik kebijakan perusahaan dengan aturan wajib',
                    'teks' => 'Komponen '.Label::fakta($p['fakta']).' dikategorikan perusahaan sebagai penghasilan '
                        .str_replace('_', ' ', $p['kategori_perusahaan']).', padahal regulasi menetapkan '
                        .str_replace('_', ' ', $p['kategori_wajib']).' ('.($p['sumber'] ?? '').'). Kalkulator memakai aturan regulasi.'],
                'GROSSUP_GANDA' => ['jenis' => 'info', 'judul' => 'Gross-up punya dua jawaban sah',
                    'teks' => Format::bulan($p['bulan'] ?? null, true).': tunjangan pajak '.Format::rp($p['terkecil']).' atau '
                        .Format::rp($p['terbesar']).'; dipakai yang '.($p['dipilih'] ?? 'terkecil').'.'],
                'TRANSAKSI_TAHUN_LAIN' => ['jenis' => 'info', 'judul' => 'Transaksi masuk tahun pajak lain',
                    'teks' => json_encode($p, JSON_UNESCAPED_UNICODE)],
                default => ['jenis' => 'info', 'judul' => $kode, 'teks' => json_encode($p, JSON_UNESCAPED_UNICODE)],
            };
        }
        $hasil = array_values(array_unique($hasil, SORT_REGULAR));
        if ($tidakDiatur) {
            $hasil[] = ['jenis' => 'info', 'judul' => 'Klasifikasi mengikuti kebijakan perusahaan',
                'teks' => 'Regulasi tidak mengatur tegas: '.implode(', ', array_unique($tidakDiatur)).'.'];
        }

        return $hasil;
    }

    /** Jejak inferensi tanpa fakta antara (berawalan "_"). */
    public function jejak(): array
    {
        return array_values(array_filter($this->h['jejak'] ?? [], fn ($j) => ! str_starts_with($j['fakta'], '_')));
    }

    /** Jumlah aturan berbeda yang dipakai, per lapisan. */
    public function jumlahAturan(): array
    {
        $unik = [];
        foreach ($this->h['jejak'] ?? [] as $j) {
            $unik[$j['lapisan']][$j['aturan']] = true;
        }

        return ['regulasi' => count($unik['regulasi'] ?? []), 'perusahaan' => count($unik['perusahaan'] ?? [])];
    }
}
