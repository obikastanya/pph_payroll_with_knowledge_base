<?php

/*
| Penghubung ke engine KB (Python). Aplikasi web tidak menghitung pajak sendiri: setiap angka berasal dari
| engine/ lewat jembatan JSON (`python -m jembatan`, dijalankan dari folder repositori induk).
*/

$root = env('PAYROLL_ROOT') ?: dirname(base_path());

return [
    // folder repositori induk (berisi engine/, kb/, jembatan/)
    'root' => $root,

    // interpreter Python dari venv repositori induk
    'python' => env('PAYROLL_PYTHON') ?: $root.(PHP_OS_FAMILY === 'Windows' ? '\\env\\Scripts\\python.exe' : '/env/bin/python'),

    // batas waktu satu panggilan engine (detik); satu panggilan bisa berisi banyak pegawai
    'timeout' => (int) env('PAYROLL_TIMEOUT', 300),

    // nama lapisan kebijakan perusahaan (kb/perusahaan/perusahaan_x.yaml), ditampilkan di navbar
    'nama_perusahaan' => env('PAYROLL_NAMA_PERUSAHAAN', 'Perusahaan X'),

    // KLU pemberi kerja (menentukan fasilitas PPh 21 DTP 2025-2026); kosong = tidak diketahui
    'klu' => env('PAYROLL_KLU') ?: null,

    // tahun pajak yang dibuka untuk data HR: rentang yang sudah diuji E12 (README induk §5)
    'tahun_min' => 2023,
    'tahun_max' => 2026,
];
