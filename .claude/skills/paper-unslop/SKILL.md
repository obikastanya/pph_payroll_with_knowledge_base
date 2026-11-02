---
name: paper-unslop
description: Membersihkan naskah paper ilmiah (LaTeX atau teks, bahasa Indonesia atau Inggris) dari pola tulisan AI tanpa mengubah makna, angka, dan sitasi. Gabungan skill unslop, 12 aturan kalimat paper, dan panduan teks AI yang harus dihindari, ditambah pemindai otomatis dan pemeriksa fakta. Pakai saat diminta merapikan, unslop, menghilangkan AI slop, membuat paper terbaca natural, atau memeriksa naskah terhadap aturan kalimat paper.
---

# Paper unslop

Skill ini menyunting naskah ilmiah supaya terbaca seperti tulisan peneliti: spesifik, jujur, punya alasan, dan dapat diverifikasi. Detektor AI menandai teks yang mudah ditebak, yaitu pilihan kata paling umum, ritme kalimat seragam, kerangka wacana bertemplat, dan isi generik. Revisi yang berhasil menambah isi dan mengubah struktur. Revisi yang hanya mengganti kata dengan sinonim gagal, dan teks yang dipoles ulang oleh model bahasa justru makin mirip teks model bahasa.

Sumber yang digabung ada di bagian "Asal aturan" di akhir file. Setiap aturan punya ID tetap (misalnya `K3`, `P7`) supaya laporan revisi dapat merujuknya.

## 0. Larangan

Larangan ini berlaku di atas semua aturan lain.

- Angka, satuan, sitasi (`\cite`), rujukan silang (`\ref`), simbol matematika, nama dataset, dan istilah teknis tidak boleh berubah, hilang, atau bertambah. Pemeriksanya `scripts/check_facts.py`.
- Kekuatan klaim tetap sama. Jangan menguatkan, melemahkan, atau menambah tafsiran supaya kalimat terdengar alami. Tafsiran baru harus benar untuk semua metrik yang dilaporkan.
- Jangan sengaja menyisipkan salah ketik, tata bahasa salah, karakter tersembunyi, homoglyph, atau spasi aneh. Jangan memakai pengganti kata acak atau kata langka yang menggeser makna.
- Jangan menghapus pernyataan penggunaan AI. Bila teks hasil agen dipakai apa adanya, pernyataan itu harus mencakupnya. Sampaikan hal ini sekali kepada penulis.
- Tidak ada versi yang dijamin lolos detektor. Jangan menjanjikannya.
- Inkonsistensi klaim antarbagian dilaporkan sebagai temuan "di luar gaya" dan tidak diperbaiki diam-diam.

## 1. Parameter naskah

Tetapkan sebelum menyunting. Bila penulis tidak menyebutnya, pakai nilai bawaan dan sebutkan nilai itu di laporan.

| Parameter | Bawaan | Catatan |
|---|---|---|
| Bahasa | ikuti naskah | Istilah teknis Inggris di naskah Indonesia tidak diterjemahkan dan ditulis miring (misalnya lewat makro `\en{}`). |
| Sudut pandang | impersonal, tanpa *kami, kita, saya, penulis, we, our, I* | Bila naskah memakai "kami" secara konsisten, ikuti naskah dan jangan dicampur. |
| Pasif | boleh, paling banyak tiga kalimat pasif berturut-turut | Lihat `K5`. |
| Cakupan revisi | hanya kalimat yang ditandai pemindai, detektor, atau yang jelas salah | Lihat bagian 3. |
| Batas abstrak | 150 sampai 250 kata | Ikuti aturan jurnal bila berbeda. Pemindai melaporkannya dengan kode `ABS`. |

## 2. Katalog aturan

Satu kemunculan pola belum tentu salah. Yang ditandai detektor adalah penumpukan pola. Tanda ★ berarti pola itu sudah terbukti ditandai detektor pada naskah nyata.

### K. Aturan kalimat (12 aturan)

- **K1. Subjek dan predikat berdekatan dan muncul di awal kalimat.** Klausa panjang tidak disisipkan di antara keduanya.
  - Kurang: "Gerbang G4, yang menjalankan seluruh kasus uji pada basis lama dan basis baru sebelum pembaruan diterima, menolak 12 kandidat."
  - Lebih baik: "Gerbang G4 menolak 12 kandidat. Gerbang ini menjalankan seluruh kasus uji pada basis lama dan basis baru sebelum pembaruan diterima."
  - Rantai anak kalimat "yang" (empat atau lebih dalam satu kalimat: "aturan yang disimpan di graf yang dibaca engine yang menghitung pajak yang terutang") juga menjauhkan pembaca dari inti kalimat. Pecah menjadi dua kalimat atau ganti sebagian dengan kata kerja.
- **K2. Informasi penting diletakkan di akhir kalimat.** Pembaca memberi tekanan pada bagian akhir. Taruh angka atau temuan baru di sana, bukan di awal.
- **K3. Satu gagasan utama per kalimat.** Panjang sekitar 12 sampai 25 kata dan bervariasi. Kalimat yang memaksa pembaca membaca ulang dipecah. Kalimat di atas 35 kata hampir selalu perlu dipecah.
- **K4. Tindakan ditaruh di kata kerja, bukan kata benda.** "melakukan evaluasi terhadap X" menjadi "mengevaluasi X". "dilakukan perhitungan ulang" menjadi "X dihitung ulang". "proses pengujian dilakukan" menjadi "X diuji". "memberikan dampak" menjadi "berdampak", "mengalami peningkatan" menjadi "naik", *perform an evaluation of* menjadi *evaluate*.
- **K5. Kalimat pasif dan impersonal.** Subjek kalimat pasif sebaiknya hal yang sedang dibahas di paragraf itu. Bila pelakunya diketahui dan penting, sebutkan pelakunya sebagai subjek ("Gerbang G5 menolak pembaruan kosong", bukan "Pembaruan kosong ditolak"). Hindari lebih dari tiga kalimat pasif berturut-turut, dan lebih dari 60% kalimat pasif dalam satu paragraf. Pasif yang menyebut pelakunya ("dihitung oleh *engine*", *was computed by the engine*) hampir selalu lebih baik ditulis aktif ("*Engine* menghitung...", *The engine computes...*). Pasif di dalam anak kalimat ("kandidat yang dibuat LLM", *the rules that were extracted*) tidak dihitung sebagai pasif kalimat. Pasif tanpa pelaku ketika pelakunya penting ("Pembaruan diterapkan", padahal tidak jelas sistem atau peninjau yang menerapkan) hanya dapat ditemukan dengan membaca.
- **K6. Awal kalimat.** Kalimat dibuka dengan subjek. Jangan membuka dengan kata sambung yang diikuti koma, seperti *Namun,*, *Selain itu,*, *Oleh karena itu,*, *Dengan demikian,*, *However,*, atau *Thus,*. Frasa keterangan di depan seperti "Pada data uji," atau "Dengan anggaran ini," dipindahkan ke akhir kalimat.
  - Kurang: "Pada 13 regulasi, usulan benar 8 kali."
  - Lebih baik: "Usulan benar pada 8 dari 13 regulasi."
- **K7. Koma.** Jangan memotong klausa yang seharusnya bersambung dengan koma. Jangan menggabungkan dua kalimat utuh hanya dengan koma. Koma dipakai untuk klausa nonrestriktif dan daftar. Perbaikan kalimat tidak boleh menambah koma. Pola koma lain ada di `P6` (rangkaian klausa berkoma, pola ★), `P11` (sisipan berkoma di tengah kalimat), dan `K6` (frasa pembuka berkoma). `check_facts.py` melaporkan jumlah koma sebelum dan sesudah revisi.
- **K8. Kata yang tepat.** *Signifikan* dan *significant* hanya untuk hasil uji statistik, dengan p atau CI di kalimat yang sama. Penguat kabur (*sangat, jauh lebih, benar-benar, secara substansial, cukup, very, greatly, substantially*) diganti angkanya. Hasil juga tidak diberi kata sifat penilai ("luar biasa", "menjanjikan", "memuaskan", "akurasi yang tinggi", "performa yang baik", *remarkable, promising, impressive, valuable insights*). Hasil disebut dengan angka dan pembandingnya ("akurasi 0,91, naik 0,06 dari B3").
- **K9. Hedging sesuai bukti.** Satu kata pelunak cukup (*dapat, mungkin, menunjukkan, suggests, may*). Jangan menumpuknya ("berpotensi dapat meningkatkan", "could potentially suggest"). Kebalikannya juga dihindari, yaitu penguat kepastian yang tidak didukung bukti ("tidak diragukan lagi", "tak pelak", "sudah pasti", "jelas bahwa", "tentunya", *undoubtedly, clearly, obviously, of course, it is clear that*). Tingkat keyakinan ditunjukkan dengan angka, CI, atau uji, bukan dengan kata.
- **K10. Kala.** Isi paper, tabel, dan fakta umum memakai bentuk kini ("Tabel 3 menunjukkan", "Table 3 shows"). Prosedur yang sudah dijalankan memakai bentuk lampau ("dijalankan pada 28 Oktober", "was trained"). Di bahasa Indonesia, jangan menambah "telah" atau "sudah" di setiap kalimat; tiga kali atau lebih dalam satu paragraf hampir selalu berlebihan.
- **K11. Angka dan singkatan.** Kalimat tidak dibuka dengan angka; tulis "Tiga belas peristiwa", bukan "13 peristiwa", atau susun ulang kalimatnya. Angka dan satuan dipisah spasi tak-putus (`34~MB`). Kata sifat majemuk berangka diberi tanda hubung (`34-MB model`). Singkatan didefinisikan saat pertama muncul, terpisah untuk abstrak dan isi utama. Proporsi dan persen tidak dicampur dalam satu bagian. Naskah Indonesia memakai koma desimal dan titik ribuan secara konsisten.
- **K12. Pola gaya AI.** Rinciannya ada di kelompok P, B, W, dan F di bawah. Ringkasnya: em dash, daftar yang dipaksa tiga butir, pola "tidak hanya X tetapi juga Y", pembuka "Hal ini/This/These" berulang, kerangka "Perbedaannya adalah...", lebih dari satu glos per paragraf, kalimat pendek sejajar berulang, serta kata seperti *krusial, memanfaatkan, menyoroti, leverage, showcase, underscore*.

### B. Kosakata

- **B1. Kata yang melonjak sejak LLM.** Pakai hanya bila maknanya tepat dan tidak ada padanan yang lebih sederhana.
  - Inggris: *delve, intricate, pivotal, underscore, showcase, leverage, seamless, robust* (tanpa uji robustness), *comprehensive, meticulous, commendable, notably, multifaceted, paramount, landscape, realm, tapestry, testament, harness, unlock, elevate, crucial, enhance, foster, garner, interplay, vibrant, enduring, shed light on, pave the way, cutting-edge, groundbreaking, game-changer, it is worth noting, insights into, exhibit, emphasize, invaluable, unprecedented, noteworthy, unveil, embark, intricacies*, dan *novel* di judul.
  - Indonesia: lihat tabel.

  | Hindari | Ganti dengan |
  |---|---|
  | memainkan peran krusial/penting/kunci | sebut perannya secara langsung |
  | menyoroti, menggarisbawahi, menegaskan pentingnya | "menunjukkan", atau langsung sebut temuannya |
  | lanskap, ranah, ekosistem (kiasan) | "penelitian tentang X" |
  | komprehensif, holistik, menyeluruh | sebut cakupannya ("13 peristiwa, 2.398 kasus") |
  | wawasan berharga, kontribusi berarti | sebut wawasan atau kontribusinya |
  | membuka jalan bagi, menjadi landasan bagi | "memungkinkan X", atau hapus |
  | inovatif, mutakhir, revolusioner, canggih | hapus; biarkan hasil yang berbicara |
  | sangat efektif, sangat efisien | angkanya |
  | mulus, tangguh, andal (tanpa uji) | kondisi ujinya |
  | di era digital saat ini, seiring perkembangan teknologi, dalam beberapa tahun terakhir, semakin meningkat, mendapat perhatian luas | hapus; mulai dari masalah beserta angkanya |
  | menjawab tantangan, solusi yang efektif, tantangan utama | sebut masalah dan cara kerjanya |
  | dewasa ini, tidak terlepas dari, tak terpisahkan dari | hapus; mulai dari faktanya |
  | pemangku kepentingan, implikasi penting/luas | sebut siapa dan implikasi apa |
  | perlu dicatat bahwa, penting untuk dicatat, perlu diketahui | hapus; tulis faktanya |
  | memanfaatkan, mengoptimalkan (sebagai "memakai") | "memakai", "menggunakan" |
  | secara signifikan (tanpa uji) | angka beserta p atau CI |
- **B2. Cara megah untuk menyebut "adalah".** *serves as, stands as, boasts, features, offers*; "berperan sebagai", "bertindak sebagai", "berfungsi sebagai", "hadir sebagai", "menjadi kunci", "menawarkan", dan "merupakan" yang berulang. Tulis "adalah", "ialah", "punya", atau langsung kata kerjanya.
- **B3. Kata benda kiasan abstrak.** *substrate, vector, locus, nexus, paradigm, modality, scaffolding, north star, flywheel, bedrock*; "fondasi", "pilar", "tulang punggung", "jantung dari", "payung". Ganti dengan kata konkret.
- **B4. Kata polos lebih baik.** *utilize, facilitate, numerous, in the event that*; "mengutilisasi", "memfasilitasi", "guna", "dalam rangka", "terkait dengan", "adapun", "yang mana", "di mana" (sebagai terjemahan *where* untuk benda, bukan tempat). Pakai "memakai", "membantu", "banyak", "bila", "untuk", "tentang", "yang".
- **B5. Satu istilah untuk satu konsep.** Jangan memutar sinonim (*knowledge base*, basis pengetahuan, KB, repositori aturan) dalam satu paragraf. Pilih satu dan ulangi. Istilah yang sudah didefinisikan tidak diganti di bagian lain.
- **B6. Kuantor kabur.** "berbagai", "beragam", "sejumlah", "banyak", "beberapa", *various, several, a variety of* tanpa angka diganti jumlahnya bila jumlah itu diketahui.
- **B7. Kata tidak lazim: arkais, sastrawi, atau serapan bergaya.** Model bahasa memilih kata formal yang terdengar berbobot, padahal ada padanan biasa. Kata-kata ini tidak selalu langka. "tatkala" dan "niscaya" lebih sering muncul di korpus umum daripada istilah teknis seperti "inferensi", sehingga daftar frekuensi kata tidak dapat menyaringnya dan yang dipakai adalah daftar kurasi. Pakai kata di daftar ini hanya bila maknanya tepat dan tidak ada padanan yang lebih biasa. Istilah teknis bidang yang memang baku (misalnya "inferensi", "regresi") bukan sasaran aturan ini.

  | Hindari | Ganti dengan |
  |---|---|
  | tatkala, manakala, bilamana | ketika, bila |
  | niscaya, mutlak, sudah barang tentu | pasti, atau hapus |
  | senantiasa | selalu |
  | acap kali, kerap, kerap kali | sering |
  | termaktub, terejawantah, mengejawantahkan | tercantum, terwujud, mewujudkan |
  | ihwal | tentang |
  | kiranya, hendaknya, notabene | hapus, atau "sebaiknya" |
  | mumpuni, paripurna, adiluhung | memadai, lengkap; atau sebut ukurannya |
  | gamblang | jelas |
  | esensial, esensi | penting, inti |
  | signifikansi (bukan statistik) | arti, makna |
  | optimalisasi, akselerasi, eskalasi | perbaikan, percepatan, kenaikan |
  | sinergi, sinergis | kerja sama, gabungan |
  | elaborasi, diskursus | uraian, pembahasan |
  | implementatif, aplikatif, transformatif | dapat diterapkan; atau sebut perubahannya |
  | urgensi | alasan, pentingnya |
  | determinan | penentu |
  | masif | besar, luas; atau angkanya |
  | eksistensi | keberadaan |
  | dinamika, konstelasi (kiasan) | perubahan, susunan; atau sebut perubahannya |
  | akomodatif | dapat menampung |
  | *myriad, plethora* | *many*, atau angkanya |
  | *endeavor, commence, ascertain* | *try, start, find out* |
  | *aforementioned, henceforth, thereby, wherein, whereby* | *this, from now on, so, where, by which* |
  | *albeit, notwithstanding* | *although, despite* |
  | *elucidate, exemplify, encompass, culminate* | *explain, show, include, end* |
  | *salient, profound, unwavering, burgeoning, quintessential* | kata biasa atau angkanya |
  | *bolster, spearhead, underpin, streamline, juxtapose* | *support, lead, rest on, simplify, compare* |

### P. Pola kalimat

- **P1. ★ Kalimat pendek sejajar yang berderet.** Tiga kalimat atau lebih dengan panjang dan bentuk yang sama, atau yang dibuka kata yang sama. Gabungkan atau variasikan.
- **P2. Ritme seragam.** Campur kalimat pendek untuk temuan utama dengan kalimat panjang untuk prosedur dan syaratnya. Memotong semua kalimat menjadi sama pendek juga merupakan pola.
- **P3. Pola tiga.** Jangan memaksa gagasan menjadi tiga ("cepat, akurat, dan andal"). Sebut jumlah yang memang ada.
- **P4. "Tidak hanya X, tetapi juga Y".** Termasuk "bukan sekadar X, melainkan Y", "bukan hanya", dan *not only... but also*. Paling banyak sekali di seluruh naskah, lebih baik tidak sama sekali. Kerangka kontras "bukan X, melainkan Y" yang berulang, *not merely X; it is Y*, dan keseimbangan semu "Di satu sisi... Di sisi lain..." juga termasuk.
- **P5. Rentang palsu.** "dari X hingga Y" ketika X dan Y tidak berada pada satu skala. Sebut butirnya langsung.
- **P6. ★ Rangkaian klausa yang disambung koma.** Kalimat berisi 2 sampai 4 klausa yang disambung koma ("X, sehingga Y", "Jika X, Y", "X, yang Y", "X, dan Y", ", dan pada..." di ekor kalimat), lalu diulang di beberapa kalimat berturut-turut. Pecah menjadi satu klausa per kalimat, jadikan kesimpulan kalimat sendiri, dan pakai objek ganda tanpa koma. Tetap variasikan panjangnya.
- **P7. ★ Kerangka pelaporan hasil.** Ciri-cirinya: klausa syarat di depan ("Ketika data dikurangi menjadi X, skor..."), pasif di klausa syarat, kata kerja netral diikuti angka bertanda ("berubah sebesar -0,002"), subjek tiruan ("Perbedaannya adalah", *The difference is*) untuk beberapa hasil sekaligus, keterangan yang tidak sejajar, dan frasa metrik yang diulang di setiap kalimat. Perbaikannya menjadikan aksi sebagai subjek, memakai kata kerja berarah (menurunkan, menaikkan, menyamai, membagi dua), dan menghilangkan kata kerja kedua yang sama ("Mengurangi data menjadi X menurunkan skor 0,002, dan menghapus *dropout* menaikkannya 0,001"). Variasikan bentuknya, karena satu bentuk yang diulang menjadi templat baru.
- **P8. ★ Kerangka enumerasi.** "X harus memenuhi dua syarat. Syarat pertama... Syarat kedua...", atau "Pertama, ... Kedua, ... Ketiga, ..." di dalam prosa. Lipat menjadi satu atau dua kalimat. Pakai urutan bernomor hanya bila sumbernya memang daftar.
- **P9. ★ Glos lebih dari satu per paragraf.** Glos adalah penjelasan sisipan: "yaitu...", "yakni...", "artinya...", "dengan kata lain...", *i.e.*, *that is*, atau keterangan dalam kurung. Paling banyak satu per paragraf. Kurung untuk definisi singkatan, angka, CI, dan rujukan bukan glos.
- **P10. ★ Pembuka "Hal ini", "Hal tersebut", "Ini", "This", "These" yang beruntun.** Ganti dengan subjek yang dirujuk ("Penurunan ini...", "Gerbang G4...").
- **P11. ★ Aposisi di dalam subjek.** "Model utama, yaitu Claude dengan *effort* tinggi, menyusun..." memisahkan subjek dan predikat (lihat `K1`).
- **P12. ★ Rantai konsesi, kontras, kesimpulan.** Tiga kalimat yang masing-masing satu langkah logika ("meskipun...", "tetapi...", "karena itu...") dengan kalimat ketiga yang hanya menafsirkan kalimat kedua. Padatkan menjadi dua kalimat.
- **P13. Em dash dan pengganti dash.** Tidak dipakai sama sekali, termasuk `---` dan ` -- ` di antara kata. Pakai titik dan kalimat baru, atau koma. En dash untuk rentang angka (2023--2026) tetap boleh.
- **P14. Titik dua sebagai penyambung.** Titik dua boleh sebelum daftar, definisi, atau contoh. Titik dua di tengah kalimat untuk efek ("Hasilnya jelas: gerbang bekerja") dihapus dan kalimatnya ditulis lurus.
- **P15. Pertanyaan retoris.** "Lalu, bagaimana jika...?" Ganti dengan pernyataan.
- **P16. Kata transisi di awal kalimat.** Paling banyak satu per paragraf dan, sesuai `K6`, tanpa koma sesudahnya. Kata seperti "Selain itu", "Lebih lanjut", "Tidak hanya itu", "Lebih dari itu", "Di sisi lain", dan "Sementara itu" adalah yang paling sering muncul.
- **P17. Frasa *-ing* atau anak kalimat dangkal di ekor kalimat.** *highlighting..., ensuring..., reflecting..., showcasing...*; "..., yang menunjukkan pentingnya...", "..., sehingga memastikan...", "..., mencerminkan...". Hapus atau ganti dengan fakta yang bisa dicek.
- **P18. Atribusi kabur.** "Para ahli berpendapat", "Studi menunjukkan", "Banyak penelitian" tanpa sitasi. Sebut sumbernya atau hapus.
- **P19. Pengisi.** "Perlu dicatat bahwa", "Penting untuk diketahui", "Dapat dikatakan bahwa", "Pada dasarnya", "Dalam hal ini", "Sebagaimana diketahui", "merupakan hal yang penting", "dapat dilihat bahwa", *in order to*, *due to the fact that*. Hapus atau pendekkan.
- **P20. Adverbia penopang dan kepadatan adverbia.** "secara otomatis", "secara signifikan", "secara efektif", "secara eksplisit", "dengan baik", "dengan cepat" yang tidak menambah informasi. Hapus atau ganti dengan angka atau kata kerja yang lebih tepat. Di naskah Inggris, adverbia berakhiran *-ly* (*significantly, consistently, seamlessly, effectively, carefully, ultimately*) adalah salah satu penanda AI yang paling mudah terlihat bila menumpuk. Batas praktis: paling banyak satu per kalimat, kurang dari tiga per paragraf, dan sekitar 12 per 1.000 kata di seluruh naskah. Batas yang sama berlaku untuk keterangan cara "secara X" dan "dengan X" di naskah Indonesia (kurang dari tiga per paragraf). Kata sifat berakhiran *-ly* (*monthly, daily, early, only, likely*) tidak dihitung.
- **P21. Gaya berbunga.** Metafora, aforisme, personifikasi ("sistem ini memahami"), kata kerja kiasan ("menavigasi kompleksitas", "menjembatani kesenjangan"). Tulis maksud literalnya.
- **P22. Kalimat terlalu padat.** Kata sandang atau kata kerja yang hilang, panah, simbol, dan singkatan yang memaksa pembaca menerjemahkan ("G4 gagal → *abstain*"). Tulis kalimat utuh.
- **P23. Negatif ganda.** Kata kerja turun ditambah angka bertanda minus ("menurunkan skor sebesar -0,05"). Buang tandanya, atau pakai bentuk netral "selisihnya -0,05 [CI]".
- **P24. Penghubung sebab tanpa sebab.** "Akibatnya", "Oleh karena itu", "sehingga", *as a result* ketika kalimat berikutnya bukan akibat kalimat sebelumnya. Hapus penghubungnya.
- **P25. Translationese (Indonesia ke Inggris dan sebaliknya).** "yang merupakan" menjadi *which is* di setiap kalimat, "serta" menjadi *as well as*, "Hal ini" menjadi *This*, "dilakukan" menjadi *is carried out*. Arah sebaliknya: "di mana" untuk *where*, "yang mana" untuk *which*, "dalam hal" untuk *in terms of*, "Adalah penting untuk" untuk *It is important to*, "sebuah" dan "suatu" untuk *a/an* di depan setiap kata benda, dan "tersebut" untuk *the/this* di setiap kalimat.
- **P26. Kalimat pengungkap dan penegas.** Kalimat yang menunda isi demi efek: "Inilah yang disebut...", "Itulah sebabnya...", "Di sinilah letak...", "Yang menarik adalah...", "Yang didukung data hanya...", "Kuncinya terletak pada...", "Jawabannya sederhana:", *Here is the key*, *This is where*. Juga keterangan penilai di awal kalimat seperti "Menariknya,", "Ironisnya,", "Sayangnya,", "Tentu saja,", dan penegas "-lah yang" di tengah kalimat ("Faktor inilah yang...", "Gerbang G4-lah yang..."). Tulis isinya langsung ("Hambatan ini dikenal sebagai...", "Data hanya mendukung non-inferioritas").
- **P27. Pasangan kata bersinonim.** "efektif dan efisien", "jelas dan terorganisir", "cepat dan tepat", "akurat dan andal", "baik secara teoretis maupun praktis", *efficient and effective*. Pangkas menjadi satu kata yang memang diukur, atau ganti dengan angkanya.

### W. Pola paragraf dan wacana

- **W1. Paragraf bertemplat.** Semua paragraf berpola kalimat topik, tiga poin, kalimat kesimpulan, atau banyak paragraf dibuka dengan frasa yang sama ("Penelitian ini...", "Sistem ini...", "Hasil ini..."). Bila pembuka yang sama dipakai di empat paragraf atau lebih, variasikan subjeknya sesuai topik paragraf.
- **W2. Penutup paragraf generik.** "Secara keseluruhan...", "Dengan demikian...", "Singkatnya...", "Hal ini menunjukkan pentingnya...", *Overall*, *The future looks bright*. Akhiri dengan fakta, angka, atau implikasi yang spesifik.
- **W3. Penanda arah tanpa isi.** "Pada bagian ini akan dibahas...", "Bagian berikut menjelaskan...", "Section V discusses...". Cukup satu kalimat peta di akhir Pendahuluan.
- **W4. Pengulangan dalam satu paragraf.** Gagasan yang sama diulang dengan kata lain. Hapus versi yang kurang spesifik.
- **W5. Nada selalu positif dan seimbang.** Kelemahan disebut tegas dan spesifik, beserta angkanya.
- **W6. Klaim umum tanpa rujukan atau angka.** "LLM sangat populer", "Regulasi pajak sering berubah", "salah satu tantangan terbesar", "salah satu teknologi yang paling banyak digunakan". Tambahkan angka atau sitasi, atau hapus.
- **W7. Satu paragraf dua topik.** Pecah.
- **W8. Istilah dipakai sebelum didefinisikan.** Pindahkan definisinya ke depan.
- **W9. Angka tanpa kesimpulan.** Setiap kelompok angka diikuti satu kalimat yang menyatakan artinya bagi klaim.
- **W10. Alasan pilihan tidak disebut.** Setiap pilihan metode punya alasan satu kalimat.
- **W11. Panjang paragraf.** Paragraf prosa sebaiknya 3 sampai 8 kalimat dan sekitar 60 sampai 200 kata. Paragraf satu atau dua kalimat digabung dengan paragraf yang topiknya sama. Paragraf di atas 10 kalimat dipecah pada pergantian topik.
- **W12. Kalimat yang tidak diperlukan.** Buang penanda arah yang isinya diulang di kalimat penutup, penegasan ulang ("Ini adalah biaya satu kali" sesudah "Pelabelan dijalankan sekali"), fakta yang tersirat dari nama atau tahun, gagasan yang sama di banyak bagian (pertahankan di tempat yang paling cocok), penunjuk ke bagian yang langsung menyusul atau ke penjelasan yang sudah lewat ("seperti dijelaskan sebelumnya"), tautologi ("tidak publik, sehingga tidak tersedia"), kalimat yang hanya membawa sitasi (pindahkan sitasinya ke kalimat definisi), dan kalimat yang tidak membedakan apa pun.
  - Jangan dibuang: pengulangan yang perannya berbeda di tiap bagian (motivasi di Pendahuluan, definisi di Metode), daftar atau angka yang menopang argumen di Pembahasan, dan kalimat pembingkai pendek yang membantu pembaca. Kalimat terakhir ini ditandai **opsional**.
- **W14. Rumus harapan manfaat.** "Penelitian ini diharapkan dapat memberikan kontribusi...", "Dengan adanya sistem ini, diharapkan...", "Hasil penelitian diharapkan bermanfaat bagi...". Penelitian tidak menyatakan harapan tentang dirinya sendiri. Sebut apa yang diukur dan hasilnya, atau siapa yang dapat memakai hasilnya dan untuk apa.
- **W15. Klise celah penelitian.** "masih sangat terbatas", "belum banyak penelitian yang...", "celah penelitian yang ingin diisi", *remains largely unexplored*. Celah ditulis sebagai apa yang sudah dikerjakan karya tertentu (dengan sitasi) dan apa yang belum.
- **W16. Definisi buku teks.** "Sistem pakar merupakan salah satu cabang dari kecerdasan buatan yang...", lalu "Menurut X [c], ... adalah...". Istilah baku bidang tidak didefinisikan ulang. Definisikan hanya konsep atau ukuran yang diperkenalkan atau dipersempit oleh paper ini.
- **W13. Sebut mekanismenya, bukan kesannya.** "Sistem ini mudah dipelihara" menjadi "Perubahan PP 58/2023 dinyatakan dengan 7 rekaman tanpa mengubah kode". Kalimat yang dapat muncul tanpa perubahan di paper lain tidak mengatakan apa pun tentang paper ini.

### F. Format dan ciri khusus paper

- **F1. Daftar butir di bagian prosa.** Pendahuluan, Penelitian Terkait, Hasil, dan Pembahasan ditulis sebagai prosa. Daftar hanya untuk kontribusi, langkah prosedur, atau butir yang memang terpisah.
- **F2. Label tebal di tengah paragraf.** `\textbf{Efisiensi:} ...` atau "**Kinerja:** Kinerja meningkat...". Ubah menjadi prosa atau subjudul. Pembuka tebal yang diakhiri titik, menamai butir, dan diikuti informasi baru masih boleh di daftar.
- **F3. Penekanan berlebihan.** Jangan menebalkan setiap nama atau singkatan. Huruf miring untuk penekanan (`\emph{sangat}`, `\emph{tidak}`) dipakai paling banyak sekali per paragraf. Istilah asing ditulis lewat makro istilah (misalnya `\en{}`), bukan `\emph{}`, supaya keduanya dapat dibedakan.
- **F4. Judul.** Huruf kapital hanya di awal (*sentence case*) kecuali template jurnal meminta lain. Tanpa emoji.
- **F5. Karakter.** Tanpa kutip melengkung, elipsis Unicode, atau em dash Unicode di `.tex`. Pakai ``` `` ''```, `\ldots`, dan konstruksi kalimat biasa. Tanpa sisa markdown (`**`, `##`, backtick).
- **F6. Artefak LLM dan nada percakapan.** "Tentu!", "Berikut adalah", "Semoga membantu", *Certainly*, *As an AI*, *[insert citation]*, *[citation needed]*, "TODO", "XX", *as of my knowledge cutoff*. Juga ajakan kepada pembaca ("Mari kita lihat", "Bayangkan", *Let us*) dan tanda seru. Hapus seluruhnya.
- **F7. Sitasi.** Setiap entri `.bib` harus nyata dan dapat diverifikasi. Sitasi harus mendukung klaim di kalimatnya, bukan hanya cocok judulnya.
- **F8. Kontribusi generik.** "Kerangka baru yang meningkatkan kinerja secara signifikan". Tulis metodenya, pembandingnya, besar perubahannya, dan datanya.
- **F9. Tinjauan pustaka berupa daftar ringkasan.** "A dkk. melakukan X. B dkk. melakukan Y." Kelompokkan per pendekatan, bandingkan, lalu tunjukkan celahnya.
- **F10. Keterbatasan klise.** "Penelitian selanjutnya dapat memakai data yang lebih besar", *several limitations should be acknowledged*, *beyond the scope of this study*, *while our results are encouraging*, *future work could explore*. Tulis keterbatasan spesifik beserta akibatnya.
- **F11. Klaim kebaruan.** "Sejauh pengetahuan kami/penelusuran ini" paling banyak sekali, hanya untuk klaim yang sudah dicek ke pustaka.
- **F13. Penilaian keberhasilan diri.** "telah berhasil mengembangkan", "terbukti mampu", "membuktikan bahwa metode ini efektif", "tujuan penelitian telah tercapai", *successfully demonstrated*, *proves that*. Hasil empiris tidak "membuktikan". Tulis apa yang diukur dan angkanya, dengan hedging satu tingkat bila buktinya terbatas.
- **F12. Notasi.** `$p=0{,}004$` atau `$p<0{,}001$`, bukan "p 0,004". Detail teknis yang dibutuhkan replikasi (*seed*, versi model, ukuran tiap bagian data) tidak boleh hilang saat merapikan.

### E. Khusus naskah berbahasa Inggris

Semua aturan K, B, P, W, dan F di atas juga berlaku untuk naskah Inggris. Kelompok ini menambah pola yang khas bahasa Inggris, beserta contoh Inggris untuk aturan yang paling sering dilanggar. Paper akademik Inggris rujukan (pra-2023, tulisan manusia) tetap memakai *we*, pembuka partisip, dan kalimat panjang; yang membedakan teks AI adalah penumpukan pola di bawah, bukan satu kemunculan.

- **E1. Inflasi makna dan penghindaran kopula.** *a testament to, reflects a broader, sets the stage for, marks a shift, pivotal moment, focal point, deeply rooted, evolving landscape, underscores the importance of, highlights the need for, is of paramount importance, cannot be overstated, lies at the heart of, at the forefront of, in today's rapidly evolving, serves a dual purpose, reflects a deliberate trade-off, paints a compelling picture, poses significant challenges, we envision a future, will play an increasingly vital role*. Juga *functions as, operates as, offers a [powerful/unique/robust] ...* sebagai pengganti *is* atau *has* (lihat `B2`). Tulis faktanya: *The engine computes 2,398 cases in 41 s*.
- **E2. Kosakata AI lunak.** Kata yang wajar satu per satu tetapi melonjak pada model 2024 sampai 2026: *additionally, align with, resonate with, highlight* (kata kerja), *valuable, key insight/challenge/contribution, deep dive, clearer, dependable, echo, matters, practical, prioritize, quietly, steady, universally, ultimately, meaningful, tailored, actionable, empower, lever, pays off, where it matters*. Dua atau lebih dalam satu paragraf patut diganti dengan kata yang lebih spesifik.
- **E3. Kontras "rather than" dan framing korektif.** Pola terbalik *Y rather than X* dan *a complement to, rather than a replacement for* dipakai berulang. Naskah manusia pembanding memakai *rather than* sekitar 0,5 kali per 1.000 kata, sedangkan teks AI uji sekitar 6. Juga framing korektif: *should be understood as X rather than Y, does not by itself establish, should not be confused with, is best understood as, is less about X than Y, the question is not whether, The difficulty is not X; it lies in Y, Tax rules are not static; they evolve, not without limitations*. Nyatakan klaimnya langsung tanpa menyangkal posisi yang tidak diajukan siapa pun.
- **E4. Pembuka partisip.** Pembuka khas AI selalu ditandai: *Leveraging X, ...; Building on this, ...; Drawing on ..., ...; By integrating/combining/harnessing X, ...; Grounded in ..., ...; Recognizing ..., ...*. Pembuka partisip lain (*Given ..., Using ..., Following ...*) wajar bila subjek sesudah koma memang pelakunya, tetapi menjadi *dangling modifier* bila subjeknya bukan pelaku.
  - Kurang: *Using the gold rules, the results show 8 correct updates.* (hasil tidak "memakai" apa pun)
  - Lebih baik: *With the gold rules as reference, 8 of 18 updates were correct.*
- **E5. Konstruksi ekspletif dan cleft.** *There are many/several ..., It is important/essential/worth noting that ..., It is also important to note that ..., It is this property that ...*. Jadikan pelaku sebagai subjek (*Two reasons support ...*; *The gate rejects ...*).
- **E6. Gerakan retoris bertemplat.** *To address this gap, we propose; To this end; In this regard; Building on prior work; Our contributions are threefold; The remainder of this paper is organized as follows; Extensive experiments demonstrate the effectiveness of; state-of-the-art performance; opens new avenues; a promising direction; To evaluate the effectiveness of*. Satu kalimat peta di akhir Pendahuluan masih boleh (`W3`). Sisanya diganti dengan isi: apa yang diusulkan, dibandingkan dengan apa, dan hasilnya berapa.
- **E7. Register informal dan kontraksi.** *it's, don't, can't, a lot of, lots of, huge, really, pretty much, kind of, sort of, basically, literally*. Paper IEEE tidak memakai kontraksi.
- **E8. Ejaan Amerika dan Inggris tercampur.** *-ize* dan *-ise*, *modeling* dan *modelling*, *behavior* dan *behaviour* dalam satu naskah. IEEE memakai ejaan Amerika; pilih satu dan seragamkan.
- **E9. Terjemahan kaku Indonesia ke Inggris.** Pola yang muncul ketika draf Indonesia dipoles LLM: *has experienced several changes* (mengalami), *in the last years*, *Government Regulation Number 58 Year 2023* (Nomor ... Tahun), *which is valid since*, *is done by* (dilakukan oleh), *from 6.5 hours become 2.1 hours* (menjadi), *Based on the results of this research, it can be concluded that*, *is able to answer the problem formulation* (rumusan masalah), *this research* untuk *this study*, *In this case*, *the calculation result*. Tulis ulang dengan kata kerja langsung: *The regulation changed four times between 2023 and 2026*; *Expert time fell from 6.5 to 2.1 hours*.

Contoh Inggris untuk aturan yang paling sering dilanggar:

| Aturan | Kurang | Lebih baik |
|---|---|---|
| K1 | *The gate, which runs every test case on both the old and the new base before an update is accepted, rejected 12 candidates.* | *The gate rejected 12 candidates. It runs every test case on both bases before an update is accepted.* |
| K4 | *We perform an evaluation of the pipeline.* | *We evaluate the pipeline.* / *The pipeline was evaluated on 18 documents.* |
| K6 | *However, the consensus abstained on E04.* / *On the test set, accuracy fell.* | *The consensus abstained on E04.* / *Accuracy fell on the test set.* |
| K8 | *The system achieves remarkable accuracy.* | *The system matches the reference on 232 of 235 observations.* |
| K9 | *This could potentially suggest that ...* | *This suggests that ...* |
| P6 | *When the data are reduced, accuracy drops, which shows that size matters, and the effect is larger for E07.* | *Halving the data lowers accuracy by 0.04. The drop is largest for E07 (0.09).* |
| P7 | *When dropout is removed, the score shifts by -0.002. The difference is +0.009 with an MLP head.* | *Removing dropout lowers the score by 0.002; an MLP head raises it by 0.009.* |
| P17 | *The gate rejects empty updates, ensuring robustness.* | *The gate rejects empty updates; 7 of 319 drafts failed it.* |
| P20 | *The gates rigorously and carefully check every candidate, effectively preventing silent errors.* | *The gates check every candidate; silent errors fell from 7 to 3 of 18 documents.* |

## 3. Alur kerja

1. **Baca seluruh naskah**, termasuk tabel dan keterangan gambar, sebelum menilai pengulangan. Banyak pengulangan baru terlihat lintas bagian.
2. **Simpan salinan asli** (misalnya `naskah.orig.tex` di folder sementara) untuk verifikasi ulang di langkah 6 dan review makna di langkah 7.
3. **Jalankan pemindai.**
   ```
   python <skill>/scripts/scan_style.py naskah.tex            # semua paragraf
   python <skill>/scripts/scan_style.py naskah.tex --summary  # hitungan per aturan saja
   python <skill>/scripts/scan_style.py naskah.tex --rules K6,P6
   python <skill>/scripts/scan_style.py naskah.tex --synonyms "knowledge base|KB|basis pengetahuan;LLM|model bahasa"
   ```
   Bahasa naskah dideteksi otomatis (paksa dengan `--lang id` atau `--lang en`). `--synonyms` mengisi `B5` dengan kelompok istilah naskah itu. Pemindai hanya saringan pertama. Setiap temuan dinilai manual, karena sebagian adalah peringatan (misalnya `K6` frasa keterangan, `K5` deret pasif, `B6` kuantor). Pola yang tidak dapat dideteksi mesin atau hanya terdeteksi sebagian (P3, P12, P21, W1, W4 sampai W10, W12, W13, W16, F7 sampai F10) diperiksa dengan membaca.

   Ringkasan pemindai memisahkan **penanda AI** (kosakata, kerangka, dan pola yang khas teks model) dari aturan gaya lain, dan melaporkan penanda AI per 1.000 kata. Kalibrasi pada November 2026: enam paper Inggris tulisan manusia dari 2021 sampai 2022 berada di 5,7 sampai 12,2; teks AI halus buatan agen 33; teks AI terang-terangan 123 sampai 128; teks bersih buatan agen 0. Angka di atas sekitar 15 berarti naskah masih jelas terbaca sebagai teks AI. Angka ini hanya pembanding kasar, bukan detektor.
4. **Ubah sesedikit mungkin.** Hanya kalimat yang ditandai pemindai, detektor penulis, atau yang memang salah yang diubah. Kalimat lain dibiarkan persis. Bila penulis punya sorotan detektor, kerjakan sorotan itu lebih dulu daripada tebakan sendiri.
5. **Revisi per paragraf** dengan teknik di bagian 4. Setiap perbaikan diperiksa lagi terhadap katalog, karena perbaikan sering memunculkan pola baru (misalnya memindahkan frasa keterangan ke akhir kalimat sambil menambah koma, yang melanggar `K7`).
6. **Verifikasi ulang berulang (wajib, minimal dua putaran).** Satu kali revisi hampir selalu meninggalkan temuan, dan perbaikan sering membuat pola baru. Sesudah setiap putaran revisi, bandingkan dengan versi asli:
   ```
   python <skill>/scripts/scan_style.py naskah.tex --baseline naskah.orig.tex
   ```
   Keluarannya memisahkan temuan yang **hilang**, yang **TERTINGGAL** (temuan yang sama masih ada), dan yang **BARU MUNCUL** (kemungkinan dibuat oleh perbaikan). Kerjakan dua kelompok terakhir, lalu ulangi pemindaian. Berhenti hanya bila kedua kelompok itu berisi temuan yang sengaja dipertahankan, masing-masing dengan alasan satu kalimat (misalnya "K6: frasa 'Pada 2024' dipertahankan karena memindahkannya membuat kalimat ambigu"). Selain pemindai, baca ulang seluruh paragraf yang berubah terhadap katalog, karena pola yang hanya dapat ditemukan dengan membaca juga sering tertinggal. Laporkan jumlah putaran.
7. **Review makna (wajib, sesudah putaran terakhir).** Revisi gaya tidak boleh mengubah makna. Pemeriksaannya dua lapis.
   - Mesin:
     ```
     python <skill>/scripts/check_facts.py naskah.orig.tex naskah.tex
     ```
     Skrip ini membandingkan angka, sitasi, rujukan silang, matematika, istilah miring, kata penentu kekuatan klaim ("hanya", "semua", "tidak", *only*, *all*, *not*), dan jumlah koma. Semua selisih harus nol, kecuali perubahan yang disengaja dan dilaporkan.
   - Pembaca: bandingkan setiap pasangan kalimat lama dan baru untuk memeriksa klaim, kekuatan klaim, penekanan, sebab-akibat, pelaku, urutan, cakupan (semua atau sebagian, selalu atau kadang), dan istilah teknis. Sebaiknya dikerjakan pemeriksa independen, misalnya agen lain yang hanya menerima pasangan kalimat lama dan baru tanpa alasan revisi, dengan tugas mencari perubahan makna. Setiap kalimat yang maknanya bergeser dikembalikan ke versi asli atau ditulis ulang, lalu langkah 6 dan 7 diulang untuk kalimat itu.
8. **Pass gaya oleh pemeriksa independen** bila tersedia, misalnya agen lain yang hanya menerima naskah dan file ini. Penulis revisi cenderung tidak melihat pola buatannya sendiri. Temuan pemeriksa dicek dulu kebenarannya sebelum diterapkan, karena pemeriksa juga dapat keliru.
9. **Periksa kerusakan edit.** Menghapus kalimat terakhir sebuah paragraf dapat ikut menghapus baris kosong sehingga dua paragraf LaTeX menyatu. Bandingkan jumlah baris kosong (`git diff naskah.tex | grep -cE '^[-+]\s*$'` harus 0 kecuali disengaja). Pertahankan akhir baris (CRLF atau LF). Kompilasi naskah dan pastikan tidak ada galat, sitasi, atau rujukan yang hilang.
10. **Laporkan** sesuai bagian 5.

Bila diminta "review" atau "usulan", tampilkan usulan per kalimat dengan nomor baris dan tunggu persetujuan sebelum menerapkan. Bila diminta "perbaiki" atau "bersihkan", langsung terapkan lalu laporkan.

## 4. Teknik revisi

Urutan dari yang paling berdampak:

1. **Tambahkan hal yang hanya diketahui penulis.** Alasan memilih metode, eksperimen yang gagal, batasan nyata (anggaran, perangkat keras, waktu), dan hasil yang mengejutkan. Detail ini tidak dapat ditebak model bahasa. Bila detailnya tidak ada di naskah atau data, tanyakan kepada penulis dan jangan mengarang.
2. **Mulai dari temuan atau angka, bukan dari kerangka.** "Usulan salah pada 3 dari 18 dokumen" lebih baik daripada "Bagian ini menyajikan hasil evaluasi".
3. **Lipat enumerasi** menjadi satu atau dua kalimat panjang dengan anak kalimat.
4. **Hapus kalimat yang tidak menambah informasi**, yaitu penegasan ulang, glos kedua, dan penutup rangkuman.
5. **Ganti kata umum dengan istilah domain yang tepat.** "*bootstrap* klaster per peristiwa", bukan "metode statistik yang andal".
6. **Variasikan ritme sesuai isi.** Kalimat pendek untuk temuan utama, kalimat panjang untuk prosedur dan syaratnya.
7. **Untuk laporan hasil**, jadikan aksi sebagai subjek, pakai kata kerja berarah, dan hilangkan kata kerja yang diulang. Ganti bentuknya dari kalimat ke kalimat.
8. **Variasikan setiap perbaikan.** Pengganti yang sama, bila dipakai berulang, menjadi templat baru yang juga terdeteksi.

## 5. Laporan

- Sebutkan parameter naskah yang dipakai (bagian 1).
- Berikan sebelum dan sesudah untuk kalimat yang berubah saja, dengan ID aturan dan catatan satu baris ("K6: frasa keterangan dipindah ke akhir").
- Kelompokkan usulan menjadi: kesalahan penulisan, kalimat yang dapat dibuang, penggabungan, opsional, di luar gaya (perlu keputusan penulis), dan sengaja tidak disentuh beserta alasannya.
- Laporkan hasil `check_facts.py`, ringkasan `scan_style.py --summary` sebelum dan sesudah (termasuk penanda AI per 1.000 kata), jumlah putaran verifikasi ulang, daftar temuan yang sengaja dipertahankan beserta alasannya, dan hasil review makna.
- Laporkan kesalahan agen sendiri dan cara memperbaikinya.
- Jangan membuat tabel analisis panjang untuk perubahan kecil.

## 6. Daftar cek akhir

**Verifikasi dan makna**
- [ ] Minimal dua putaran `scan_style.py --baseline`; TERTINGGAL dan BARU MUNCUL hanya berisi temuan yang sengaja dipertahankan beserta alasannya.
- [ ] Review makna per pasangan kalimat sudah dikerjakan sesudah putaran terakhir, sebaiknya oleh pemeriksa independen.
- [ ] `check_facts.py` tidak menunjukkan selisih yang tidak disengaja.
- [ ] Makna, penekanan, sebab-akibat, dan pelaku sama dengan aslinya; tidak ada "hanya", "semua", atau "selalu" yang muncul atau hilang.
- [ ] Setiap klaim punya angka, rujukan, atau lokasi bukti.

**Kalimat**
- [ ] Tidak ada kata dari `B1` sampai `B4` tanpa alasan kuat.
- [ ] Tidak ada kata ganti orang pertama (kecuali parameter berkata lain) dan paling banyak tiga pasif berturut-turut.
- [ ] Tidak ada kalimat yang dibuka kata sambung berkoma atau frasa keterangan berkoma (`K6`).
- [ ] Tidak ada "tidak hanya... tetapi juga", kerangka enumerasi, glos ganda, rangkaian klausa berkoma, atau kerangka "perbedaannya adalah".
- [ ] Tidak ada em dash, pertanyaan retoris, atau titik dua penyambung.
- [ ] Panjang kalimat bervariasi (SD di ringkasan pemindai tidak kecil), dan tidak ada kalimat di atas 35 kata tanpa alasan.

**Paragraf dan format**
- [ ] Paragraf tidak ditutup kalimat rangkuman generik, membahas satu topik, dan panjangnya wajar (`W11`).
- [ ] Keterbatasan dan saran spesifik untuk penelitian ini.
- [ ] Tidak ada artefak LLM, placeholder, sisa markdown, karakter Unicode yang belum dikonversi, atau label tebal di prosa.
- [ ] Naskah terkompilasi tanpa galat, abstrak dalam batas kata, dan pernyataan penggunaan AI tetap ada.

## Asal aturan

- Skill `unslop` proyek ini (`.claude/skills/unslop/SKILL.md`), aturan 3 sampai 33: menjadi `P17`, `P18`, `B1` sampai `B4`, `P3` sampai `P5`, `B5`, `P13`, `P14`, `F2` sampai `F6`, `P19`, `K9`, `W2`, `B3`, `W13`, `K3`, `K5`, `P20`, `B4`, `P21`, dan `P22`. Dua aturan unslop disesuaikan untuk paper. Aturan 13 melarang tanda kurung, padahal paper membutuhkannya untuk sitasi, singkatan, dan angka, sehingga yang dibatasi hanya glos dalam kurung (`P9`). Aturan 29 meminta kalimat aktif, sedangkan aturan kalimat paper memakai pasif atau impersonal, sehingga `K5` meminta pelaku disebut bila diketahui dan membatasi deret pasif.
- Dua belas aturan kalimat paper (Gopen dan Swan 1990, *The Science of Scientific Writing*; Williams, *Style: Lessons in Clarity and Grace*; IEEE Editorial Style Manual yang merujuk ke *Chicago Manual of Style*): menjadi `K1` sampai `K12`.
- Panduan teks AI yang harus dihindari (versi 18 Oktober dan 1 November 2026), termasuk pola ★ hasil uji detektor dan katalog kalimat yang tidak diperlukan: menjadi kelompok `B`, `P`, `W`, dan `F`. Rujukan kosakata: Kobak dkk., *Science Advances* 2025; Liang dkk., ICML 2024. Bias detektor terhadap penulis non-penutur asli: Liang dkk., *Patterns* 2023.
- Tambahan dari pemeriksaan pola yang masih lolos (3 November 2026), yaitu uji pada draf paper proyek ini dan uji serang oleh agen independen dengan 36 paragraf teks AI buatan: pola khas bahasa Indonesia di `B2`, `B4`, `B6`, `P10`, `P16`, `P17`, `P24`, `P25`, `W11`; aturan baru `P26`, `P27`, `W14`, `W15`, `W16`, `F13`; dan perluasan `K4`, `K8`, `W6`. Evaluasi kedua pada hari yang sama menambah `B7` (kata tidak lazim), kepadatan adverbia *-ly* dan "secara/dengan X" di `P20`, penguat kepastian di `K9`, rantai "yang" di `K1`, pembuka paragraf berulang di `W1`, penekanan miring di `F3`, dan sebagian kosakata dari daftar kata berlebih Kobak dkk. Pendekatan daftar frekuensi kata (`wordfreq`) diuji untuk `B7` dan ditolak, karena kata arkais seperti "tatkala" lebih sering muncul daripada istilah teknis yang sah.
- Penguatan versi Inggris (3 November 2026): kelompok `E1` sampai `E9`, contoh Inggris untuk aturan K dan P, deteksi pasif klausa utama, pasif berpelaku dan proporsi pasif di `K5`, mode `--baseline`, dan skor penanda AI. Sumber pola: halaman Wikipedia "Signs of AI writing" (kosakata per periode model 2023 sampai 2026, *rather than* terbalik, framing korektif, penghindaran kopula) dan Kobak dkk. (*delves* 28 kali, *underscores* 10,9 kali, dan *showcasing* 10,2 kali di atas tren pra-LLM). Kalibrasi memakai enam paper Inggris tulisan manusia 2021 sampai 2022 (sekitar 29.000 kata), 41 paragraf teks AI halus dan 8 paragraf bersih yang ditulis agen yang tidak membaca skill ini, serta 8 paragraf teks AI terang-terangan dari uji sebelumnya. Pola yang terlalu sering muncul di teks manusia dipersempit atau dikeluarkan (misalnya *outstanding*, *actually*, *offers* umum, dan pembuka partisip biasa).
