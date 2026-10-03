<?php

/*
| Penghubung ke engine KB (Python). Aplikasi web tidak menghitung pajak sendiri: setiap angka berasal dari
| engine/ lewat jembatan JSON (`python -m jembatan`, dijalankan dari folder repositori induk).
*/

$root = env('PAYROLL_ROOT') ?: dirname(base_path());
$modelLlm = env('PAYROLL_LLM_MODEL') ?: 'gpt-5.6-sol';
// penyedia mengikuti nama model (asisten_kb/llm.py): claude-... = Anthropic, selain itu OpenAI
$kunciLlm = str_starts_with($modelLlm, 'claude') ? 'ANTHROPIC_API_KEY' : 'OPENAI_API_KEY';

return [
    // folder repositori induk (berisi engine/, kb/, jembatan/)
    'root' => $root,

    // interpreter Python dari venv repositori induk
    'python' => env('PAYROLL_PYTHON') ?: $root.(PHP_OS_FAMILY === 'Windows' ? '\\env\\Scripts\\python.exe' : '/env/bin/python'),

    // batas waktu satu panggilan engine (detik); satu panggilan berisi paling banyak `ukuran_batch` pegawai
    'timeout' => (int) env('PAYROLL_TIMEOUT', 300),

    // pegawai per panggilan engine saat Hitung semua; hasil setiap batch dicatat dalam transaksinya sendiri
    'ukuran_batch' => max(1, (int) env('PAYROLL_UKURAN_BATCH', 50)),

    // nama lapisan kebijakan perusahaan (kb/perusahaan/perusahaan_x.yaml), ditampilkan di navbar
    'nama_perusahaan' => env('PAYROLL_NAMA_PERUSAHAAN', 'Perusahaan X'),

    // KLU pemberi kerja (menentukan fasilitas PPh 21 DTP 2025-2026); kosong = tidak diketahui
    'klu' => env('PAYROLL_KLU') ?: null,

    // tahun pajak yang dibuka untuk data HR: rentang yang sudah diuji E12 (README induk §5)
    'tahun_min' => 2023,
    'tahun_max' => 2026,

    // berkas KB tambahan yang sudah disetujui di menu Basis pengetahuan (relatif terhadap root; harus di bawah kb/)
    'kb_tambahan_dir' => 'kb/tambahan',

    // asisten KB: PDF peraturan -> rancangan berkas KB lewat LLM (bawaan gpt-5.6-sol). Rancangan selalu divalidasi
    // engine dan ditinjau admin sebelum berlaku; tanpa kunci API, menu Basis pengetahuan tetap bisa untuk meninjau.
    'llm_model' => $modelLlm,
    'llm_kunci_env' => $kunciLlm,       // nama variabel .env yang dibutuhkan model ini
    'llm_kunci' => env($kunciLlm),
    'llm_timeout' => (int) env('PAYROLL_LLM_TIMEOUT', 900),
];
