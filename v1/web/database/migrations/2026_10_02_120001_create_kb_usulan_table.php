<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
| Usulan berkas KB dari dokumen peraturan (PDF) yang dibaca LLM. Alur status:
| antre -> diproses -> siap_tinjau | tidak_dapat_dikodifikasi | gagal; siap_tinjau -> diterapkan | ditolak.
| Berkas yang diterapkan ditulis ke kb/tambahan/ dan ikut dimuat engine selama `aktif`.
*/
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('kb_usulan', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->constrained('users')->nullOnDelete();
            $table->string('judul');
            $table->string('lapisan', 16);
            $table->text('catatan')->nullable();
            $table->string('nama_pdf');
            $table->string('path_pdf');
            $table->unsignedBigInteger('ukuran_pdf');
            $table->string('status', 32)->default('antre');
            $table->text('pesan_galat')->nullable();
            $table->longText('usulan')->nullable();
            $table->longText('yaml')->nullable();
            $table->longText('validasi')->nullable();
            $table->boolean('valid')->nullable();
            $table->text('info_llm')->nullable();
            $table->string('nama_berkas')->nullable();
            $table->boolean('aktif')->default(false);
            $table->timestamp('diterapkan_pada')->nullable();
            $table->foreignId('diterapkan_oleh')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamps();
            $table->index(['aktif', 'diterapkan_pada']);
        });

        Schema::table('perhitungan', function (Blueprint $table) {
            // sidik isi berkas KB tambahan yang aktif saat dihitung ('' = tanpa berkas tambahan)
            $table->string('sidik_kb', 16)->nullable()->after('versi_kb');
        });
    }

    public function down(): void
    {
        Schema::table('perhitungan', fn (Blueprint $table) => $table->dropColumn('sidik_kb'));
        Schema::dropIfExists('kb_usulan');
    }
};
