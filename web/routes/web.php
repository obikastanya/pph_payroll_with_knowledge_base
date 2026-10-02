<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\MesinController;
use App\Http\Controllers\PayrollTahunController;
use App\Http\Controllers\PegawaiController;
use App\Http\Controllers\RekapController;
use Illuminate\Support\Facades\Route;

Route::middleware('guest')->group(function () {
    Route::get('/login', [AuthController::class, 'form'])->name('login');
    Route::post('/login', [AuthController::class, 'masuk'])->middleware('throttle:10,1');
});

Route::middleware('auth')->group(function () {
    Route::post('/logout', [AuthController::class, 'keluar'])->name('logout');

    Route::get('/', [RekapController::class, 'index'])->name('rekap');
    Route::post('/rekap/hitung', [RekapController::class, 'hitung'])->name('rekap.hitung');
    Route::get('/rekap/ekspor', [RekapController::class, 'ekspor'])->name('rekap.ekspor');

    Route::resource('pegawai', PegawaiController::class);

    Route::get('/pegawai/{pegawai}/payroll/create', [PayrollTahunController::class, 'create'])->name('payroll.create');
    Route::post('/pegawai/{pegawai}/payroll', [PayrollTahunController::class, 'store'])->name('payroll.store');
    Route::controller(PayrollTahunController::class)->prefix('/payroll/{payroll}')->name('payroll.')->group(function () {
        Route::get('/', 'show')->name('show');
        Route::get('/edit', 'edit')->name('edit');
        Route::put('/', 'update')->name('update');
        Route::delete('/', 'destroy')->name('destroy');
        Route::post('/hitung', 'hitung')->name('hitung');
        Route::get('/slip/{bulan}', 'slip')->whereNumber('bulan')->name('slip');
        Route::get('/ekspor', 'ekspor')->name('ekspor');
    });

    Route::get('/mesin', [MesinController::class, 'index'])->name('mesin');
});
