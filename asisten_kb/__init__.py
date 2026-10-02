"""Asisten penyusun knowledge base: dokumen peraturan (PDF) -> rancangan berkas KB, lewat LLM (bawaan gpt-5.6-sol).

Paket ini SENGAJA terpisah dari engine/: engine tetap bebas LLM (research_plan.md §4.3), dan setiap rancangan
dari LLM hanyalah usulan. Usulan baru berlaku setelah (1) lolos validasi yang sama dengan KB biasa (skema,
verifikasi statis, simulasi pada pegawai contoh) dan (2) disetujui manusia di aplikasi web.
"""
