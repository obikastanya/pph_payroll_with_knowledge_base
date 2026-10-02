<?php

use Illuminate\Support\Facades\Route;
use Modules\Pegawai\Http\Controllers\PegawaiController;

Route::middleware(['web', 'auth'])->prefix('pegawai')->name('pegawai.')->controller(PegawaiController::class)->group(function () {
    Route::get('/', 'index')->name('index');
    Route::get('list', 'list')->name('list');
    Route::post('/', 'store')->name('store');
    Route::get('{pegawai}', 'show')->whereNumber('pegawai')->name('show');
    Route::get('{pegawai}/detail', 'detail')->whereNumber('pegawai')->name('detail');
    Route::put('{pegawai}', 'update')->whereNumber('pegawai')->name('update');
    Route::delete('{pegawai}', 'destroy')->whereNumber('pegawai')->name('destroy');
});
