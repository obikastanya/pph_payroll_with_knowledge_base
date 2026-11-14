<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/*
| Isian tambahan yang diminta berkas KB tambahan (deklarasi `masukan`), di luar kolom tetap payroll_tahun /
| payroll_bulan. Satu baris = satu nilai: bulan 0 = sekali setahun (hr('kunci')), 1-12 = per bulan
| (hr_masa('kunci')). `nilai` disimpan sebagai JSON agar tipenya utuh (bilangan bulat, teks desimal, tanggal, ya/tidak).
*/
return new class extends Migration
{
    public function up(): void
    {
        Schema::create('payroll_masukan', function (Blueprint $table) {
            $table->id();
            $table->foreignId('payroll_tahun_id')->constrained('payroll_tahun')->cascadeOnDelete();
            $table->string('kunci', 64);
            $table->unsignedTinyInteger('bulan')->default(0);
            $table->text('nilai');
            $table->timestamps();
            $table->unique(['payroll_tahun_id', 'kunci', 'bulan']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('payroll_masukan');
    }
};
