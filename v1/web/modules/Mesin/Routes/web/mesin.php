<?php

use Illuminate\Support\Facades\Route;
use Modules\Mesin\Http\Controllers\MesinController;

Route::middleware(['web', 'auth'])->group(function () {
    Route::get('mesin', [MesinController::class, 'index'])->name('mesin.index');
});
