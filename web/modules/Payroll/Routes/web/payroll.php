<?php

use Illuminate\Support\Facades\Route;
use Modules\Payroll\Http\Controllers\PayrollController;

Route::middleware(['web', 'auth'])->group(function () {
    Route::get('pegawai/{pegawai}/payroll/create', [PayrollController::class, 'create'])->name('payroll.create');
    Route::post('pegawai/{pegawai}/payroll', [PayrollController::class, 'store'])->name('payroll.store');

    Route::prefix('payroll/{payroll}')->name('payroll.')->controller(PayrollController::class)->group(function () {
        Route::get('/', 'show')->name('show');
        Route::get('edit', 'edit')->name('edit');
        Route::put('/', 'update')->name('update');
        Route::delete('/', 'destroy')->name('destroy');
        Route::post('hitung', 'hitung')->name('hitung');
        Route::get('slip/{bulan}', 'slip')->whereNumber('bulan')->name('slip');
        Route::get('ekspor', 'ekspor')->name('ekspor');
    });
});
