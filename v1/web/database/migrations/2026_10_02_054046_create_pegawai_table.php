<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('pegawai', function (Blueprint $table) {
            $table->id();
            $table->string('nomor_induk', 32)->unique();
            $table->string('nama');
            $table->string('jenis_kelamin', 1);
            $table->boolean('punya_npwp')->default(true);
            $table->date('tanggal_masuk');
            $table->date('tanggal_berhenti')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('pegawai');
    }
};
