<?php

use App\Http\Controllers\Auth\LoginController;
use Illuminate\Support\Facades\Route;

/*
| Route aplikasi ada di setiap module (modules/{Nama}/Routes/web/*.php), dimuat oleh ServiceProvider module
| lewat ModuleServiceProvider. Di sini hanya autentikasi dan halaman awal.
*/

// AUTHENTICATION
Route::middleware('guest')->group(function () {
    Route::get('login', [LoginController::class, 'showLoginForm'])->name('login');
    Route::post('login', [LoginController::class, 'login'])->middleware('throttle:10,1');
});
Route::post('logout', [LoginController::class, 'logout'])->middleware('auth')->name('logout');

Route::middleware('auth')->get('/', fn () => redirect()->route('dashboard.index'));
