# Panduan Revisi Teks 2: Pelajaran dari Sesi Revisi Naskah StaticKD

Pelengkap [ai_text_revision_guide.md](ai_text_revision_guide.md) (selanjutnya "panduan 1"). Panduan 1 memuat daftar kata, pola umum, dan kebijakan IEEE. File ini mencatat apa yang **terbukti** dari sesi revisi 18 Oktober 2026: kalimat mana yang ditandai detektor, perbaikan mana yang diterima atau ditolak penulis, dan kesalahan yang dibuat agent. Isinya berlaku untuk naskah lain, bukan hanya StaticKD. Contoh diambil dari [paper_final/main.tex](../paper_final/main.tex).

- **Diperbarui:** 18 Oktober 2026
- **Cara pakai:** baca bagian 1 sebelum menyentuh teks. Bagian 2–5 adalah katalog. Bagian 6 adalah alur kerja, dan bagian 8 adalah daftar cek.
- **Pembaruan:** setiap pola baru yang ditandai detektor dicatat di bagian 2, lengkap dengan tanggal, kalimat asli, dan perbaikan yang diterima.

---

## 1. Prinsip yang terbukti

1. **Ubah sesedikit mungkin.** Hanya kalimat yang ditandai detektor atau yang memang salah yang diubah. Kalimat lain dibiarkan persis seperti tulisan penulis.
   - *Kasus:* penulis meminta versi yang "natural dan lolos detektor". Agent menulis ulang seluruh paragraf, dan skor detektor justru **memburuk**. Teks yang dipoles model bahasa makin mirip teks model bahasa.
   - *Yang akhirnya diterima:* dua kalimat yang ditandai diganti, dua kalimat lain tetap utuh.
2. **Jangan menebak kalimat mana yang terdeteksi.** Minta sorotan dari detektor penulis.
   - *Kasus:* agent menilai kalimat "…, so hard labels work as well as soft labels" berisiko tinggi. Ternyata yang ditandai detektor hanya kalimat yang diawali "When …" dan kalimat sesudahnya. Tebakan berdasarkan pola bisa salah.
3. **Tidak ada versi yang dijamin lolos.** Teks yang ditulis agent tetap teks AI. Kalau dipakai apa adanya, pernyataan penggunaan AI di Acknowledgment harus mencakupnya (panduan 1 §10). Sampaikan hal ini sekali, singkat.
4. **Jangan menambah tafsiran supaya kalimat terdengar alami.**
   - *Kasus:* "Data size matters little" hanya benar untuk macro-F1 test. Pada set yang sama, skor development dan held-out agreement turun signifikan. Tafsiran tambahan harus dicek ke **semua** metrik yang dilaporkan.
5. **Usulkan dulu, baru terapkan.** Untuk review atau perubahan gaya, tampilkan usulan beserta nomor baris, lalu tunggu persetujuan. Terapkan hanya nomor yang disetujui.

## 2. Pola yang terbukti ditandai detektor (★)

### ★ 2.1 Kerangka pelaporan hasil dengan klausa syarat (18 Okt 2026)

Kalimat yang ditandai:

> When the data are reduced to 130 thousand documents, the test macro-F1 shifts by −0.002 (p=1.000). The difference is +0.001 (p=1.000) when token dropout is removed and +0.009 (p=0.281) with an MLP head that cannot be folded.

Cirinya:
- klausa syarat "When X," di depan, disambung koma ke klausa utama;
- pasif di dalam klausa syarat ("are reduced");
- kata kerja netral (*shifts, changes, is*) diikuti angka bertanda;
- subjek tiruan "The difference is …" yang dipakai untuk beberapa hasil sekaligus;
- keterangan yang tidak sejajar ("when …" dan "with …");
- frasa metrik ("test macro-F1") diulang di setiap kalimat.

Perbaikan yang **diterima** penulis:

> Reducing the data to 130 thousand documents lowers the test score by 0.002 (p=1.000). Removing token dropout gives +0.001 (p=1.000) and an MLP head that cannot be folded +0.009 (p=0.281).

- Aksi dijadikan subjek (gerund), sehingga kalimat menjadi satu klausa tanpa koma.
- Kata kerja berarah (*lowers*). Tanda minus dibuang karena arahnya sudah ada di kata kerja (lihat 3.1).
- Dua subjek sejajar dengan **gapping**: kata kerja kedua dihilangkan ("… gives +0.001 and an MLP head … +0.009").
- **Bentuknya harus divariasikan.** Kalau setiap hasil ditulis "Gerund … lowers …", itu menjadi templat baru.

### ★ 2.2 Rangkaian klausa yang dipisah koma

Temuan penulis: pola khasnya adalah 2–3 klausa dalam satu kalimat yang disambung koma, lalu diulang di kalimat-kalimat berikutnya.
- "X, so Y"
- "When X, Y"
- "X, and Y"

Satu kemunculan belum tentu ditandai, tetapi deretannya ditandai.

Cara memecahnya tanpa membuat semua kalimat pendek:
- Pakai satu klausa per kalimat, dengan objek ganda yang disambung "and" tanpa koma: "change it by +0.005 and the development score by −0.006".
- Jadikan kesimpulan kalimat sendiri: "Hard labels therefore work as well as soft labels."
- Ganti klausa "When …," dengan subjek gerund.
- Pertahankan variasi panjang kalimat. Deretan kalimat yang sama pendek juga merupakan pola (panduan 1 §4).

## 3. Kesalahan penulisan yang ditemukan dan diperbaiki

| # | Kesalahan | Contoh salah | Perbaikan |
|---|---|---|---|
| 3.1 | Negatif ganda: kata kerja turun + angka bertanda minus | "lowers the test macro-F1 by −0.051" | "lowers … by 0.051". Kalau CI-nya bertanda, pakai bentuk netral: "Δmacro-F1 is −0.053 [−0.065, −0.033]" |
| 3.2 | Preposisi | "its difference to X" | "the difference from X" |
| 3.3 | Proporsi dan persen dicampur | "agrees on 0.811 of the documents"; "only 0.45 of … articles, with conflict (29%)" | "81.1% of the documents"; "45%" |
| 3.4 | Rujukan ambigu setelah kalimat yang menyebut himpunan sebaliknya | "at most 32% … come from tokens seen at least 10 times. … removes **those tokens**" (maksudnya token yang jarang) | Ubah kalimat sebelumnya ke himpunan yang dirujuk: "at least 68% … fewer than 10 times … removes these rare tokens" |
| 3.5 | Singkatan dari gambar dipakai di prosa; format label tidak konsisten | "human int.", daftar dipisah titik koma, label tidak di-`\emph` | "human interest", koma + "and", `\emph{}` seperti di bagian lain; "(20% each)" untuk angka yang sama |
| 3.6 | Penghubung sebab yang tidak bersebab | "As a result, the only open classifier is … and no inexpensive classifier has been evaluated" | Hapus "As a result," |
| 3.7 | Generalisasi yang dibantah kalimat berikutnya | "All baselines are trained … with targets from the same teacher" lalu ada baseline berlabel GPT-4o | "All baselines marked + KD …" |
| 3.8 | Istilah yang bertentangan dengan protokol | "students should be selected … with test data" (padahal tidak ada pemilihan memakai test set) | "with a development set outside the training distribution" |
| 3.9 | Kalimat topik yang tidak cocok dengan contohnya | "move … in opposite directions" padahal satu contoh tidak berlawanan arah | "Agreement with the teacher does not always predict accuracy on editorial labels." |
| 3.10 | Kalimat tanpa makna | "Int8 quantization … only gives a constant-factor speed-up" (616× juga faktor konstan) | Hapus |
| 3.11 | Urutan waktu yang tidak logis | "Before deployment, accuracy should be monitored" | "During deployment" |
| 3.12 | Notasi p | "($p$ 0.004)", "$p$ $<$0.001" | "$p=0.004$", "$p<0.001$". Header tabel tidak diubah |
| 3.13 | Panjang abstrak | 311 kata, padahal batasnya 250 ([paper_rules.md](paper_rules.md)) | Padatkan kalimat dulu. Kalau masih lebih, isi mana yang dibuang adalah keputusan penulis |

## 4. Kalimat yang tidak diperlukan

Buang kalimat yang tidak menambah informasi dan tidak memperjelas. Jenis yang ditemukan:

| Jenis | Contoh | Alasan dibuang |
|---|---|---|
| Penanda arah yang isinya diulang di kalimat penutup | "Existing options fall short of this." (penutup: "No available IPTC classifier is both multilingual and this cheap.") | Penutup sudah menyatakannya dengan lebih spesifik |
| Penegasan ulang dalam satu paragraf | "This is a one-time cost." setelah "Labeling ran once" | Informasinya sudah ada |
| Fakta yang sudah tersirat dari nama | "The two periods do not overlap" untuk 2019–2021 dan 2024–2026 | Tahunnya sudah eksplisit |
| Gagasan yang sama di banyak bagian | "absolute scores read as agreement with the publisher categorization" muncul 4 kali (Metode, Hasil, Diskusi, Limitasi) | Pertahankan di tempat yang paling cocok (validitas label dan Limitasi), buang sisanya |
| Kalimat rangkuman di penutup paragraf | "Sending about two fifths of the articles … is enough to match the teacher" | Bisa diturunkan dari angka sebelumnya, dan Diskusi sudah menyatakannya |
| Penunjuk ke bagian lain | "Section V discusses the mechanism behind this pattern." | Bagian itu langsung menyusul |
| Tautologi | "is not public, so it was not available for this study" | Cukup "is not public" |
| Kalimat yang hanya membawa sitasi | "A recent survey covers the development of KD [x]." | Pindahkan sitasinya ke kalimat definisi |

**Jangan dibuang** walaupun tampak berulang:
- Pengulangan yang perannya berbeda di tiap bagian. Contoh: "no model reads the article" sebagai motivasi di Pendahuluan dan sebagai definisi di Metode.
- Daftar atau angka yang menopang argumen di Diskusi. Contoh: label dengan gap terbesar dipakai untuk membuktikan letak gap, jadi daftar itu tidak boleh dihapus.
- Kalimat framing pendek yang membantu pembaca ("Parts of both are still covered."). Tandai sebagai **opsional**, jangan langsung dibuang.

## 5. Klaim saat merapikan gaya

- **Kekuatan klaim harus tetap sama.** Penulisan ulang tidak boleh menguatkan atau melemahkan klaim tanpa data.
- **Urutan atau peringkat harus sesuai metrik utama.**
  - *Kasus:* Diskusi menyebut data sebagai "the largest source" dan inisialisasi "comes next". Pada macro-F1 test (metrik utama), menghapus inisialisasi menurunkan skor 0.120, sedangkan menghapus data menurunkan 0.051. Held-out agreement menunjukkan arah sebaliknya (−0.069 dan −0.077).
  - Laporkan **kedua metrik** dan minta penulis memutuskan. Jangan memilih sendiri.
- **Inkonsistensi klaim antarbagian** dilaporkan sebagai temuan "di luar gaya", bukan diperbaiki diam-diam.

## 6. Alur kerja agent

1. **Baca seluruh teks dulu**, termasuk tabel, sebelum menilai redundansi. Banyak pengulangan baru terlihat lintas bagian.
2. **Susun usulan dalam kelompok:**
   - (1) kesalahan penulisan;
   - (2) kalimat yang bisa dibuang;
   - (3) penggabungan;
   - (4) opsional;
   - (5) di luar gaya, perlu keputusan penulis;
   - (6) sengaja tidak disentuh.

   Setiap butir memuat nomor baris, teks lama, teks usulan, dan alasan satu kalimat.
3. **Terapkan hanya kelompok atau nomor yang disetujui.**
4. **Waspadai jebakan edit.**
   - Menghapus kalimat di **akhir paragraf** dengan alat edit (teks pengganti kosong) bisa ikut menghapus baris kosong sesudahnya. Di LaTeX, dua paragraf jadi menyatu.
   - Setelah menghapus, bandingkan jumlah baris dengan sebelum edit, lalu cek `git diff <file> | grep -cE '^[-+]\s*$'`. Hasilnya harus 0 kecuali memang disengaja.
   - Saat mengganti teks massal lewat skrip, pertahankan akhir baris (CRLF/LF): baca dan tulis dengan `newline=''`.
5. **Kompilasi salinannya** di folder sementara. Pastikan 0 error, tidak ada referensi atau sitasi yang tidak ditemukan, dan jumlah kata abstrak sesuai batas.
6. **Perbarui file turunan.** Contohnya lembar parafrase ([paper_rewrite.md](paper_rewrite.md)) yang dibangun dari `main.tex`.
   - Bangun ulang dengan `python scripts/rewrite_lock.py && python scripts/build_rewrite_md.py`.
   - Terjemahan (Makna) dikunci per ID blok, dan ID **bergeser** kalau ada paragraf baru. Cocokkan blok lama dengan blok baru berdasarkan **teks**, bukan ID. Bawa terjemahan hanya untuk teks yang identik, dan tulis ulang sisanya.
   - Pastikan Paraphrase yang sudah diisi penulis tetap menempel di paragraf yang benar.
7. **Laporkan apa adanya**, termasuk kesalahan agent sendiri dan cara memperbaikinya.

## 7. Cara menyajikan revisi ke penulis

- **Before/after per kalimat yang berubah saja.** Catatannya singkat: pola apa, diganti dengan apa.
- **Paragraf lengkap lama dan baru** diberikan kalau diminta. Sebutkan kalimat mana yang tidak berubah.
- Jangan membuat tabel analisis panjang untuk perubahan kecil. Penulis menolak format itu ("cukup 2 kalimat saja").
- Untuk penjelasan konsep (misalnya "logit itu apa"), beri satu contoh angka kecil yang benar secara matematis. Bedakan ilustrasi dari data asli.

## 8. Daftar cek

**Sebelum mengubah**
- [ ] Sudah ada sorotan detektor dari penulis, atau kesalahan yang jelas. Bukan tebakan.
- [ ] Usulan sudah disetujui.

**Saat mengubah**
- [ ] Hanya kalimat yang ditandai atau salah yang diubah; kalimat lain persis sama.
- [ ] Tidak ada rangkaian "klausa, so/and/which klausa" di setiap kalimat. Tidak ada klausa "When X," + pasif + "shifts by".
- [ ] Tidak ada negatif ganda; notasi p ditulis "p=…"; proporsi dan persen konsisten.
- [ ] Tidak ada tafsiran baru; peringkat sesuai metrik utama; semua angka sama dengan sumber.
- [ ] Bentuk perbaikan bervariasi, tidak membentuk templat baru.

**Sesudah mengubah**
- [ ] Jumlah baris dan baris kosong tidak berubah tanpa sengaja; paragraf tidak menyatu.
- [ ] Kompilasi bersih, dan abstrak ≤ batas kata.
- [ ] File turunan (lembar parafrase) sudah dibangun ulang dan dicocokkan berdasarkan teks.
- [ ] Laporan before/after singkat sudah diberikan, termasuk catatan pengungkapan AI bila teks agent dipakai apa adanya.

## Riwayat

- 18 Oktober 2026: review gaya `paper_final/main.tex` (commit `ef132c2`), pembaruan lembar parafrase, dan uji detektor pada paragraf ablasi HAS-13. Sumber pola ★2.1 dan ★2.2: sorotan detektor dan pengamatan penulis pada sesi yang sama.
