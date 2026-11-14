"""Jembatan JSON stdin/stdout antara aplikasi web (web/, Laravel) dan engine KB.

Tidak ada pengetahuan pajak di sini: modul ini hanya membaca kasus kanonik, memanggil engine.kalkulator.hitung,
dan mengembalikan keluarannya apa adanya. Engine dan KB tidak diubah, sehingga bukti verifikasi (V1-V3, E3-E12)
tetap berlaku untuk angka yang ditampilkan aplikasi web.
"""
