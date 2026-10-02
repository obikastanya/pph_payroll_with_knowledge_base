<?php

use Illuminate\Support\Facades\Route;
use Modules\Dashboard\Http\Controllers\DashboardController;

Route::middleware(['web', 'auth'])->prefix('dashboard')->name('dashboard.')->controller(DashboardController::class)->group(function () {
    Route::get('/', 'index')->name('index');
    Route::get('list', 'list')->name('list');
    Route::post('hitung', 'hitung')->name('hitung');
    Route::get('ekspor', 'ekspor')->name('ekspor');
});
