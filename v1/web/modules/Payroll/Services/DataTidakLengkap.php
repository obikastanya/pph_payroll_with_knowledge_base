<?php

namespace Modules\Payroll\Services;

use RuntimeException;

/** Data HR di database belum cukup untuk menyusun kasus kanonik (mis. hari kerja bulan tertentu kosong). */
class DataTidakLengkap extends RuntimeException {}
