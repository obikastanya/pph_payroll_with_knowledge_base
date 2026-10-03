<?php

use Illuminate\Support\Facades\Route;
use Modules\Pegawai\Http\Controllers\PegawaiController;

// {pegawai} hanya cocok dengan id angka (pola global di AppServiceProvider), jadi 'list' tidak tertangkap sebagai id
Route::middleware(['web', 'auth'])->prefix('pegawai')->name('pegawai.')->controller(PegawaiController::class)->group(function () {
    Route::get('/', 'index')->name('index');
    Route::get('list', 'list')->name('list');
    Route::post('/', 'store')->name('store');
    Route::get('{pegawai}', 'show')->name('show');
    Route::get('{pegawai}/detail', 'detail')->name('detail');
    Route::put('{pegawai}', 'update')->name('update');
    Route::delete('{pegawai}', 'destroy')->name('destroy');
});
