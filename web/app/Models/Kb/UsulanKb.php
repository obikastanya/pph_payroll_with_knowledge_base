<?php

namespace App\Models\Kb;

use App\Models\User;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Usulan berkas KB dari dokumen peraturan. `usulan` = keluaran terstruktur LLM (apa adanya), `yaml` = rancangan
 * berkas yang ditinjau/diubah admin, `validasi` = hasil validasi engine terakhir atas `yaml`.
 */
#[Table('kb_usulan')]
#[Fillable([
    'user_id', 'judul', 'lapisan', 'catatan', 'nama_pdf', 'path_pdf', 'ukuran_pdf', 'status', 'pesan_galat', 'usulan', 'yaml',
    'validasi', 'valid', 'info_llm', 'nama_berkas', 'aktif', 'diterapkan_pada', 'diterapkan_oleh',
])]
class UsulanKb extends Model
{
    public const STATUS = [
        'antre' => ['menunggu antrean', 'gray'],
        'diproses' => ['dibaca LLM', 'blue'],
        'gagal' => ['gagal', 'red'],
        'tidak_dapat_dikodifikasi' => ['tidak ada aturan', 'gray'],
        'siap_tinjau' => ['perlu ditinjau', 'yellow'],
        'diterapkan' => ['diterapkan', 'green'],
        'ditolak' => ['ditolak', 'red'],
    ];

    public const LAPISAN = [
        'perusahaan' => 'Peraturan perusahaan',
        'regulasi' => 'Peraturan pemerintah',
    ];

    protected function casts(): array
    {
        return [
            'usulan' => 'json',
            'validasi' => 'json',
            'info_llm' => 'json',
            'valid' => 'boolean',
            'aktif' => 'boolean',
            'ukuran_pdf' => 'integer',
            'diterapkan_pada' => 'datetime',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function penerap(): BelongsTo
    {
        return $this->belongsTo(User::class, 'diterapkan_oleh');
    }

    /** Berkas yang sedang dimuat engine, urut waktu diterapkan (urutan berpengaruh pada amandemen parameter). */
    public function scopeAktif(Builder $q): Builder
    {
        return $q->where('status', 'diterapkan')->where('aktif', true)->orderBy('diterapkan_pada')->orderBy('id');
    }

    public function sedangDiproses(): bool
    {
        return in_array($this->status, ['antre', 'diproses'], true);
    }

    public function labelStatus(): array
    {
        if ($this->status === 'diterapkan' && ! $this->aktif) {
            return ['diterapkan, nonaktif', 'gray'];
        }

        return self::STATUS[$this->status] ?? [$this->status, 'gray'];
    }
}
