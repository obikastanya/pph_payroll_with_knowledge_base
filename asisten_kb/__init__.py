"""Asisten penyusun knowledge base: dokumen peraturan (PDF) -> rancangan berkas KB, lewat LLM (bawaan gpt-5.6-sol).

Paket ini SENGAJA terpisah dari engine/: engine tetap bebas LLM, dan setiap rancangan
dari LLM hanyalah usulan. Usulan baru berlaku setelah (1) lolos validasi yang sama dengan KB biasa (skema,
verifikasi statis, simulasi pada pegawai contoh) dan (2) disetujui manusia di aplikasi web.
Rencana riset yang dikunci menaruh LLM dalam bentuk apa pun di luar lingkup (D6, §4.3); paket ini menyimpang dari itu,
dan batasnya dicatat di Adendum A.2 research_plan.md.
"""
