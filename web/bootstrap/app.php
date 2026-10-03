<?php

use Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse;
use Illuminate\Cookie\Middleware\EncryptCookies;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Foundation\Http\Middleware\PreventRequestForgery;
use Illuminate\Http\Exceptions\PostTooLargeException;
use Illuminate\Http\Middleware\ValidatePostSize;
use Illuminate\Http\Request;
use Illuminate\Routing\Middleware\SubstituteBindings;
use Illuminate\Session\Middleware\StartSession;
use Illuminate\View\Middleware\ShareErrorsFromSession;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        // Unggahan yang melebihi post_max_size: PHP membuang seluruh isi POST (termasuk token CSRF). Pemeriksaan
        // ukuran dipindah dari middleware global ke grup web sesudah StartSession dan sebelum pemeriksaan CSRF, agar
        // galatnya dapat dikembalikan sebagai pesan flash (sesi tersimpan) dan bukan halaman 413/419.
        $middleware->remove(ValidatePostSize::class);
        $middleware->group('web', [
            EncryptCookies::class,
            AddQueuedCookiesToResponse::class,
            StartSession::class,
            ValidatePostSize::class,
            ShareErrorsFromSession::class,
            PreventRequestForgery::class,
            SubstituteBindings::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );
        $exceptions->render(function (PostTooLargeException $e, Request $request) {
            if ($request->expectsJson()) {
                return null;
            }

            return back()->with('error', 'Berkas yang diunggah terlalu besar untuk server (batas PHP post_max_size = '
                .(ini_get('post_max_size') ?: '?').'). Perkecil atau pecah berkas, atau naikkan upload_max_filesize dan '
                .'post_max_size di php.ini.');
        });
    })->create();
