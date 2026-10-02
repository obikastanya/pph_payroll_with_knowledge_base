<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Validation\ValidationException;
use Illuminate\View\View;

class LoginController extends Controller
{
    public function showLoginForm(): View
    {
        return view('auth.login');
    }

    public function login(Request $request): RedirectResponse
    {
        $kredensial = $request->validate(['email' => ['required', 'email'], 'password' => ['required']]);
        if (! Auth::attempt($kredensial, $request->boolean('ingat'))) {
            throw ValidationException::withMessages(['email' => 'Email atau kata sandi salah.']);
        }
        $request->session()->regenerate();

        return redirect()->intended(route('dashboard.index'))->with('success', 'Selamat datang, '.Auth::user()->name.'.');
    }

    public function logout(Request $request): RedirectResponse
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('login');
    }
}
