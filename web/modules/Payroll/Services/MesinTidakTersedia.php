<?php

namespace Modules\Payroll\Services;

use RuntimeException;

/** Engine Python tidak dapat dipanggil atau jawabannya tidak dapat dibaca (bukan galat isian per pegawai). */
class MesinTidakTersedia extends RuntimeException {}
