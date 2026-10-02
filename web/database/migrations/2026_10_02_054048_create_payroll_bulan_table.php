<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
| Kehadiran & penghasilan variabel per bulan = `data_hr.per_masa`. Kolom variabel nullable: kosong berarti
| tidak diisi (kunci tidak dikirim ke engine), berbeda dari 0 yang diisi eksplisit.
*/
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payroll_bulan', function (Blueprint $table) {
            $table->id();
            $table->foreignId('payroll_tahun_id')->constrained('payroll_tahun')->cascadeOnDelete();
            $table->unsignedTinyInteger('bulan');
            $table->unsignedTinyInteger('hk_penuh')->nullable();
            $table->unsignedTinyInteger('hk_aktual')->nullable();
            $table->string('kompensasi_persen', 16)->nullable();
            $table->unsignedBigInteger('ota')->nullable();
            $table->unsignedBigInteger('lembur')->nullable();
            $table->unsignedBigInteger('komisi')->nullable();
            $table->timestamps();
            $table->unique(['payroll_tahun_id', 'bulan']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payroll_bulan');
    }
};
