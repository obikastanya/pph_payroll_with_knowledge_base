<?php

use Illuminate\Support\Facades\Route;
use Modules\BasisPengetahuan\Http\Controllers\BasisPengetahuanController;

Route::middleware(['web', 'auth'])->prefix('kb')->name('kb.')->controller(BasisPengetahuanController::class)->group(function () {
    Route::get('/', 'index')->name('index');
    Route::get('list', 'list')->name('list');
    Route::post('/', 'store')->name('store');

    Route::prefix('{usulan}')->group(function () {
        Route::get('/', 'show')->name('show');
        Route::get('status', 'status')->name('status');
        Route::get('pdf', 'pdf')->name('pdf');
        Route::get('unduh', 'unduh')->name('unduh');
        Route::put('yaml', 'simpanYaml')->name('yaml');
        Route::post('terapkan', 'terapkan')->name('terapkan');
        Route::post('tolak', 'tolak')->name('tolak');
        Route::post('aktif', 'aktif')->name('aktif');
        Route::post('ulang', 'ulang')->name('ulang');
        Route::delete('/', 'destroy')->name('destroy');
    });
});
