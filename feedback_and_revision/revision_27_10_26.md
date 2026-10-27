# Revisi 27 Oktober 2026

Tanggapan atas [feedback_27_10_26.txt](feedback_27_10_26.txt).

## 1. Pergantian judul

**Judul lama**

> *Knowledge Base* Dua Lapis Berversi Waktu untuk Perhitungan PPh Pasal 21: Rancangan Sistem, Aplikasi Web, dan Metodologi Validasi tanpa *Domain Expert*

**Judul baru**

> ***Knowledge-Based System* Adaptif untuk Perhitungan PPh 21 dengan Akuisisi Pengetahuan Berbantuan LLM dari Regulasi dan Kebijakan Perusahaan**

*An Adaptive Knowledge-Based System for PPh 21 Calculation with LLM-Assisted Knowledge Acquisition from Regulations and Company Policies*

### Alasan

Judul lama menonjolkan bentuk *knowledge base*-nya ("dua lapis berversi waktu") dan perangkat pendukung (aplikasi web, metodologi validasi). Menurut feedback no. 2, *knowledge base* saja tidak cukup sebagai kontribusi. Judul baru memindahkan fokus ke kemampuan sistem mengikuti perubahan regulasi.

| Unsur judul baru | Yang diwakili | Kaitan dengan feedback |
|---|---|---|
| *Knowledge-Based System* | Wujudnya perangkat lunak KBS (*knowledge base* + *inference engine*), bukan rumus *spreadsheet* | No. 1 |
| Adaptif | Perubahan regulasi diterapkan lewat pembaruan *knowledge base*, tanpa mengubah kode *engine* | No. 2, no. 5 |
| Akuisisi Pengetahuan Berbantuan LLM | LLM mengubah teks peraturan menjadi rancangan aturan; *engine* deterministik yang menghitung | No. 2 |
| Regulasi dan Kebijakan Perusahaan | Dua lapis pengetahuan beserta deteksi konflik antarlapis | — |

### Unsur judul lama yang dipindahkan

| Unsur | Tempat baru |
|---|---|
| Dua lapis, berversi waktu | Bagian representasi *knowledge base* di metodologi |
| Aplikasi web | Bagian implementasi; tidak lagi disebut sebagai kontribusi |
| Metodologi validasi tanpa *domain expert* | Bagian evaluasi |
| Rentang tahun pajak 2023–2026 | Abstrak dan metodologi, sebagai data evaluasi |

Kebaruan (*novelty*) yang diwakili judul ini diuraikan di bagian 3.

## 2. Representasi final *knowledge base* (feedback no. 1)

> Feedback: "Perlu diperjelas representasi final knowledgebase nya apa, yaml itu terlalu sederhana."

### Keputusan

Representasi final *knowledge base* adalah ***legal knowledge graph*** berbasis RDF/OWL. YAML tidak lagi dipakai sebagai representasi.

> *Knowledge base* direpresentasikan sebagai *legal knowledge graph* (RDF/OWL) yang menghubungkan regulasi, pasal, aturan, konsep, dan kebijakan perusahaan secara temporal. Graf ini divalidasi dengan SHACL, di-*query* dengan SPARQL untuk analisis dampak, dan aturan *executable*-nya dijalankan oleh *inference engine* deterministik.

### Pembagian peran graf dan *engine*

Pengetahuan PPh 21 terdiri atas dua jenis yang sifatnya berbeda, sehingga ditangani oleh komponen yang berbeda.

| Jenis pengetahuan | Contoh | Ditangani oleh |
|---|---|---|
| Struktural | Regulasi memuat pasal; aturan bersumber dari pasal; PMK baru mengubah atau mencabut PMK lama; komponen lembur diklasifikasikan sebagai penghasilan teratur; kebijakan perusahaan berkonflik dengan aturan wajib; aturan membaca dan menghasilkan fakta | *Knowledge graph* |
| Komputasional | Tarif TER × bruto, pembulatan per pasal, *gross-up* sebagai *fixed point*, perhitungan ulang di masa pajak terakhir | *Inference engine* yang sudah ada. Ekspresi perhitungan disimpan sebagai atribut *node* aturan di graf |

Perhitungan tidak dipindahkan ke graf. OWL/SWRL tidak mendukung aritmetika eksak, iterasi *fixed point*, maupun registri pembulatan. Padahal sistem saat ini sudah tepat sampai rupiah pada 1.213 nilai contoh resmi, dan ketepatan itu dipertahankan.

### Komponen representasi

1. **Ontologi.** Kosakatanya memakai ulang standar yang sudah ada, bukan istilah buatan sendiri:
   - ELI (*European Legislation Identifier*) untuk regulasi, pasal, dan relasi amandemen;
   - OWL-Time untuk masa berlaku (*valid time*);
   - PROV-O untuk asal-usul dan waktu pencatatan (*knowledge time*).
2. **SHACL sebagai gerbang validasi**, termasuk untuk rancangan aturan dari LLM. Contoh *constraint*:
   - setiap aturan wajib harus bersumber dari pasal;
   - aturan perusahaan tidak boleh menghasilkan fakta yang dikunci aturan wajib;
   - aturan pengganti harus mulai berlaku sesudah aturan yang digantikan.
3. **SPARQL untuk analisis dampak perubahan.** Contohnya: ketika sebuah PMK baru terbit, aturan, fakta, dan kebijakan perusahaan mana yang terdampak.
4. ***Inference engine* deterministik.** *Engine* yang sudah ada membaca aturan dari graf, lalu menghitung dengan aritmetika eksak dan menghasilkan jejak sampai pasal.

### Kebijakan perusahaan di dalam graf

Kebijakan perusahaan dimodelkan setara dengan regulasi pemerintah. Yang membedakan hanya lapisan dan otoritasnya.

| Unsur | Regulasi pemerintah | Kebijakan perusahaan |
|---|---|---|
| Otoritas | Kemenkeu, DJP | Perusahaan |
| Dokumen sumber | PMK, PP, PER | Peraturan Perusahaan, PKB, SK Direksi |
| Unit sumber | Pasal | Pasal atau butir dokumen internal |
| Sifat aturan | Wajib, *default*, tafsir | Opsional (menimpa *default* yang sah) |
| Versi waktu | Masa berlaku dan waktu pencatatan | Masa berlaku dan waktu pencatatan |

Isi lapisan Perusahaan X yang sekarang masuk ke graf seluruhnya:
- aturan kebijakan (prorata hari kerja, kenaikan gaji di tengah bulan, THR, BPJS, *take home pay*);
- pemetaan komponen gaji ke kategori pajak;
- isian tambahan yang diminta kebijakan baru;
- aturan pembulatan perusahaan.

Hubungan antara kebijakan dan regulasi menjadi relasi eksplisit, misalnya:

```
Perusahaan X ──menerbitkan──> Peraturan Perusahaan ──memuat──> Pasal 12
                                                                  ^
PX-LEMBUR (lembur → tidak teratur) ──bersumber────────────────────┘
      │
      └──berkonflik_dengan──> Klasifikasi wajib: lembur → teratur
                                  └──bersumber──> PER-16 Ps. 1 angka 15; PMK 168/2023 Ps. 5(3)a
```

Dengan relasi eksplisit seperti ini, tiga hal menjadi mungkin:
- kebijakan yang melanggar aturan wajib ditolak SHACL sebelum dipakai;
- pertanyaan lintas lapis seperti "kebijakan perusahaan mana yang berkonflik setelah regulasi ini terbit?" dapat dijawab dengan satu *query*;
- beberapa perusahaan dapat memakai lapisan regulasi yang sama, masing-masing dengan *named graph* sendiri.

Aturan wajib tetap tidak dapat ditimpa perusahaan. Bila kebijakan perusahaan bertentangan dengan aturan wajib, konfliknya dicatat dan *engine* memakai aturan regulasi (*lex superior*).

### Ukuran keberhasilan

*Knowledge graph* harus menambah kemampuan yang dapat diukur, bukan sekadar mengganti format berkas:

| Kemampuan | Metrik |
|---|---|
| Validasi rancangan LLM (SHACL) | Jumlah dan jenis kesalahan rancangan yang tertangkap sebelum diterapkan |
| Analisis dampak perubahan (SPARQL) | *Precision* dan *recall* aturan, fakta, dan kebijakan terdampak pada perubahan regulasi yang nyata |
| Ketepatan perhitungan | Keluaran seluruh eksperimen yang ada harus identik sebelum dan sesudah migrasi ke graf |

### Status

Tahap rancangan, belum diimplementasikan. Langkah berikutnya adalah merancang ontologi (kelas, relasi, contoh SHACL dan SPARQL), lalu memigrasikan *knowledge base* yang ada ke graf.

## 3. *Novelty* (feedback no. 2)

> Feedback: "Perlu diperkuat lagi kontribusi nya. Knowledge base saja tidak cukup. Apakah mengubahnya menjadi adaptive tax calculation using knowledge base bisa jadi kontribusi? LLM digunakan untuk konversi aturan menjadi knowledge. sebuah engine dibuat untuk membaca knowledge base agar bisa digunakan sistem."
>
> Catatan: kata "kontribusi" pada feedback adalah salah tulis; yang dimaksud adalah *novelty*.

### Tanggapan

Usulan *adaptive tax calculation* diadopsi dan menjadi dasar judul baru. Namun, penelusuran pustaka 2024–2026 menunjukkan bahwa pola "LLM mengonversi aturan menjadi *knowledge*, lalu *engine* membaca *knowledge base*" sudah dikerjakan untuk pajak di negara lain. Contohnya NTOL untuk pajak India (*Frontiers in Artificial Intelligence*, 2026), formalisasi IRC dengan LLM (*Artificial Intelligence and Law*, 2026), dan penerjemahan hukum pajak ke Catala (NLLP 2025). Karena itu *novelty* tidak diletakkan pada pola tersebut, melainkan pada hal yang belum dikerjakan karya-karya itu.

### Pernyataan *novelty*

> Pembaruan inkremental berbantuan LLM pada *knowledge base* perhitungan pajak yang sudah berjalan, mengikuti perubahan regulasi yang nyata, dengan dua lapis norma (regulasi dan kebijakan perusahaan). Hasil periode lama terjaga, dan dampak perubahan terhadap kebijakan perusahaan terdeteksi otomatis.

| | *Novelty* | Penelitian terdahulu | Kata di judul |
|---|---|---|---|
| **Inti** | LLM **memperbarui** *knowledge base* yang sudah berjalan mengikuti rangkaian amandemen, bukan memformalkan dari nol | NTOL (2026), formalisasi IRC (2026), dan LLM → Catala (2025) memformalkan satu potret hukum dari nol untuk satu tahun pajak, tanpa mekanisme amandemen | Adaptif; Akuisisi Pengetahuan Berbantuan LLM |
| Penguat 1 | **Dampak lintas lapis**: ketika regulasi berubah, kebijakan perusahaan yang menjadi melanggar terdeteksi otomatis | Tidak ditemukan karya akademik yang memisahkan lapisan regulasi dari kebijakan pemberi kerja dalam perhitungan payroll | Regulasi dan Kebijakan Perusahaan |
| Penguat 2 | **Diuji pada perubahan struktural yang nyata**: pergantian metode PER-16 ke TER, bukan sekadar perubahan parameter, dengan verifikasi pada kasus uji bahwa hasil periode lama tidak berubah | Benchmark temporal 2026 hanya menguji LLM dalam tanya-jawab hukum, dan menunjukkan LLM lemah pada amandemen. Belum ada evaluasi pada basis aturan yang dapat dieksekusi | Adaptif |

### Yang bukan *novelty*

Bagian berikut adalah landasan penelitian ini, bukan klaim kebaruan:

| Unsur | Sudah dikerjakan oleh |
|---|---|
| LLM menyusun aturan, *engine* deterministik menghitung | NTOL (2026), formalisasi IRC (2026), LLM → Catala (2025) |
| *Knowledge graph* untuk hukum pajak | NTOL (2026), De Martim (2025) |
| Versi waktu peraturan | De Martim (2025), Moguillansky dkk. (2024) |
| *Knowledge base* untuk PPh 21 | Kebaruan domain saja (pertama untuk Indonesia); disebut, tetapi bukan *novelty* utama |

Kebaruannya terletak pada pertanyaan yang belum dijawab: **apakah *knowledge base* pajak dapat terus dimutakhirkan dengan bantuan LLM mengikuti perubahan hukum yang nyata, tanpa merusak hasil periode lama, dan tanpa melanggar batas antara aturan negara dan kebijakan perusahaan?**

### Status

Klaim *novelty* ini baru dapat dipertahankan setelah eksperimen pemutaran ulang perubahan regulasi (*regulation replay*) dijalankan. Saat ini asisten LLM baru diuji satu kali dengan PDF peraturan fiktif. Karya pembanding di atas dibaca dari abstrak dan ringkasannya; naskah lengkapnya masih harus dibaca sebelum masuk ke tinjauan pustaka.
