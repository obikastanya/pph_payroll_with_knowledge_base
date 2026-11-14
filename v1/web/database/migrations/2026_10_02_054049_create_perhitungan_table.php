<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
| Riwayat perhitungan (audit trail): kasus yang dikirim ke engine, keluaran engine apa adanya, versi KB, dan
| siapa yang menghitung. Baris lama tidak pernah diubah; menghitung ulang menambah baris baru.
*/
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('perhitungan', function (Blueprint $table) {
            $table->id();
            $table->foreignId('payroll_tahun_id')->constrained('payroll_tahun')->cascadeOnDelete();
            $table->foreignId('user_id')->nullable()->constrained('users')->nullOnDelete();
            $table->boolean('berhasil');
            $table->string('jenis_galat', 64)->nullable();
            $table->text('pesan')->nullable();
            $table->longText('kasus');
            $table->longText('hasil')->nullable();
            $table->string('cek_silang', 32)->nullable();
            $table->longText('cek_silang_rinci')->nullable();
            $table->string('versi_engine', 64)->nullable();
            $table->string('versi_kb', 64)->nullable();
            $table->bigInteger('bruto_setahun')->nullable();
            $table->bigInteger('pph21_setahun')->nullable();
            $table->bigInteger('thp_setahun')->nullable();
            $table->timestamps();
            $table->index(['payroll_tahun_id', 'id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('perhitungan');
    }
};
