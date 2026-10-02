<?php

/*
| Menu sidebar. Base-Apps-Merdeka menyimpan menu di tabel `menu` + role; aplikasi ini cukup satu peran
| (admin finance), jadi menu ditulis di sini dengan bentuk yang sama: section, title, icon (Tabler Icons,
| tanpa awalan "ti-"), route, children. `aktif` = pola nama route yang menandai menu sedang dibuka.
*/

return [
    ['section' => 'Payroll', 'title' => 'Dashboard', 'icon' => 'layout-dashboard', 'route' => 'dashboard.index', 'aktif' => ['dashboard.*']],
    ['section' => 'Payroll', 'title' => 'Pegawai & data HR', 'icon' => 'users', 'route' => 'pegawai.index', 'aktif' => ['pegawai.*', 'payroll.*']],
    ['section' => 'Sistem', 'title' => 'Basis pengetahuan', 'icon' => 'books', 'route' => 'kb.index', 'aktif' => ['kb.*']],
    ['section' => 'Sistem', 'title' => 'Mesin perhitungan', 'icon' => 'cpu', 'route' => 'mesin.index', 'aktif' => ['mesin.*']],
];
