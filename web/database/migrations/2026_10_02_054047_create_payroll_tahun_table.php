<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
| Data HR satu pegawai untuk satu tahun pajak = `data_hr` pada kasus kanonik (lapisan Perusahaan X).
| Nominal rupiah disimpan sebagai bilangan bulat; persen sebagai teks desimal (tanpa float).
*/
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payroll_tahun', function (Blueprint $table) {
            $table->id();
            $table->foreignId('pegawai_id')->constrained('pegawai')->cascadeOnDelete();
            $table->unsignedSmallInteger('tahun');
            $table->string('status_ptkp', 8);
            $table->string('metode', 32);
            $table->unsignedBigInteger('gaji_pokok');
            $table->unsignedBigInteger('kenaikan_nominal')->default(0);
            $table->date('kenaikan_tanggal');
            $table->unsignedTinyInteger('kenaikan_hk_sebelum')->default(0);
            $table->unsignedTinyInteger('kenaikan_hk_sesudah')->default(0);
            $table->unsignedTinyInteger('kenaikan_hari_sebelum')->default(0);
            $table->unsignedTinyInteger('kenaikan_hari_sesudah')->default(0);
            $table->unsignedBigInteger('tunjangan_tetap_lama')->default(0);
            $table->unsignedBigInteger('tunjangan_prorata_lama')->default(0);
            $table->unsignedBigInteger('tunjangan_tetap_baru')->default(0);
            $table->unsignedBigInteger('tunjangan_prorata_baru')->default(0);
            $table->date('tanggal_lebaran');
            $table->date('tanggal_thr_bayar');
            $table->unsignedTinyInteger('bpjs_tk_mulai_bulan')->default(1);
            $table->unsignedTinyInteger('bpjs_kes_mulai_bulan')->default(1);
            $table->string('kelas_jkk_persen', 16);
            $table->timestamps();
            $table->unique(['pegawai_id', 'tahun']);
            $table->index('tahun');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payroll_tahun');
    }
};
