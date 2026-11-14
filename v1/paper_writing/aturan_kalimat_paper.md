# Aturan Penulisan Kalimat untuk Paper

Dua belas aturan kalimat untuk naskah StaticKD ([paper_final/main.tex](../paper_final/main.tex)). File ini melengkapi [ai_text_revision_guide.md](ai_text_revision_guide.md), yang tetap menjadi acuan utama untuk pola gaya AI. Aturan yang ditandai **(proyek)** adalah keputusan khusus naskah ini, bukan aturan umum.

- **Dibuat:** 2 November 2026

## Aturan

1. **Subjek dan predikat berdekatan dan muncul di awal kalimat.** Jangan menyisipkan klausa panjang di antara keduanya (Gopen & Swan).
2. **Informasi penting diletakkan di akhir kalimat.** Pembaca secara alami memberi penekanan pada bagian akhir (Gopen & Swan).
3. **Satu gagasan utama per kalimat.** Panjangnya sekitar 12 sampai 25 kata, dengan panjang yang bervariasi. Kalimat yang memaksa pembaca membaca ulang sebaiknya dipecah.
4. **Tindakan ditaruh di kata kerja, bukan kata benda.** Contoh: "perform an evaluation of X" menjadi "evaluate X" (Williams, *Style*).
5. **Kalimat pasif (proyek).** Panduan umum menyarankan kalimat aktif, karena IEEE merujuk ke *Chicago Manual of Style* untuk tata bahasa. Naskah ini memakai pasif atau kalimat impersonal tanpa *we, I, you, they, their, them,* atau *author*. Subjek kalimat pasif sebaiknya hal yang sedang dibahas di paragraf itu. Hindari rentetan lebih dari tiga kalimat pasif berturut-turut.
6. **Awal kalimat (proyek).** Kalimat dibuka dengan subjek. Jangan membuka dengan kata sambung yang diikuti koma, seperti *However*, *In addition*, atau *Thus*. Frasa keterangan di depan seperti "On this set," atau "At such latencies," dipindahkan ke akhir kalimat.
7. **Koma.** Jangan memotong klausa yang seharusnya bersambung dengan koma. Jangan pula menggabungkan dua kalimat utuh hanya dengan koma. Koma dipakai untuk klausa nonrestriktif dan daftar. Perbaikan kalimat tidak boleh menambah koma **(proyek)**.
8. **Kata yang tepat.** Kata *significant* hanya dipakai untuk hasil uji statistik. Hindari penguat yang kabur seperti *very*, *greatly*, atau *substantially*, dan tulis angkanya.
9. **Hedging sesuai bukti.** Satu kata pelunak sudah cukup, misalnya *suggests* atau *may*. Jangan menumpuknya ("could potentially suggest").
10. **Tense.** Present tense dipakai untuk isi paper, tabel, dan fakta umum ("Table 3 shows"). Past tense dipakai untuk prosedur yang sudah dijalankan ("was trained", "was reviewed").
11. **Angka dan singkatan.**
    - Kalimat tidak boleh dibuka dengan angka. Tulis "Twelve runs", bukan "12 runs".
    - Angka dan satuan dipisah spasi tak-putus (`34~MB`).
    - Kata sifat majemuk diberi tanda hubung (`34-MB model`).
    - Singkatan didefinisikan saat pertama muncul, terpisah untuk abstrak dan isi utama.
12. **Pola gaya AI yang dihindari (proyek).** Aturan lengkapnya ada di [ai_text_revision_guide.md](ai_text_revision_guide.md). Ringkasnya:
    - em dash;
    - daftar yang dipaksa menjadi tiga butir;
    - pola "not just X but Y";
    - pembuka "This/These" yang berulang;
    - kerangka "The difference is…";
    - lebih dari satu penjelasan dalam kurung (glos) per paragraf;
    - kalimat pendek sejajar yang berulang;
    - kata seperti *crucial, leverage, showcase,* dan *underscore*.

## Sumber

- Gopen, G. D., & Swan, J. A. (1990). The Science of Scientific Writing. *American Scientist*, 78(6). Ringkasan: [AcaWiki](https://acawiki.org/The_Science_of_Scientific_Writing), [kutipan Verhoeff](https://www.win.tue.nl/~wstomv/quotes/science-of-scientific-writing.html), [TTUHSC Better Writing Tips](https://www.ttuhsc.edu/medicine/medical-education/success-types/documents/BetterWritingTips.pdf).
- Williams, J. M. *Style: Lessons in Clarity and Grace.*
- IEEE Editorial Style Manual, yang merujuk ke *Chicago Manual of Style* untuk tata bahasa: [salinan manual](https://www.cis.uoguelph.ca/~matsakis/CIS6320/manualStyleIEEE.pdf), [Allen Downey tentang kalimat pasif](https://allendowney.com/essays/passive.html).
- Klaim bahwa IEEE mewajibkan abstrak berbentuk pasif hanya berasal dari [forum Accellera](https://forums.accellera.org/topic/7655-comments-on-style/) dan belum terverifikasi di teks manual.
