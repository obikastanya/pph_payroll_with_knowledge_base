{{-- Notifikasi global (success, error, warning) via SweetAlert, pola Base-Apps-Merdeka. Teks di-encode JSON. --}}
@foreach (['success' => 'Berhasil', 'error' => 'Gagal', 'warning' => 'Perhatian'] as $jenis => $judul)
    @if (session()->has($jenis))
        <script>
            Swal.fire({
                icon: @json($jenis),
                title: @json($judul),
                text: @json(session($jenis)),
                showConfirmButton: {{ $jenis === 'success' ? 'false' : 'true' }},
                timerProgressBar: {{ $jenis === 'success' ? 'true' : 'false' }},
                timer: {{ $jenis === 'success' ? 3000 : 'undefined' }},
            });
        </script>
    @endif
@endforeach
