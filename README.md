# sport-search
## Deskripsi

SportSearch merupakan sistem Information Retrieval (IR) berbasis web yang digunakan untuk mencari berita olahraga berdasarkan query pengguna.

Sistem menerapkan Query Expansion menggunakan thesaurus untuk memperluas kata kunci pencarian, kemudian menggunakan TF-IDF sebagai metode pembobotan dan Cosine Similarity untuk menghitung tingkat kemiripan antara query dan dokumen.

## Fitur

* Pencarian berita olahraga
* Query Expansion berbasis thesaurus
* Preprocessing teks Bahasa Indonesia
* Pembobotan TF-IDF
* Perhitungan Cosine Similarity
* Pagination hasil pencarian (5 berita per halaman)
* Deployment menggunakan Railway

## Dataset

Dataset terdiri dari 50 berita olahraga yang mencakup berbagai cabang olahraga seperti:

* Sepak Bola
* MotoGP
* Formula 1
* Basket
* Badminton

## Teknologi yang Digunakan

* Python
* Flask
* Pandas
* Scikit-Learn
* Sastrawi
* GitHub
* Railway

## Alur Sistem

1. User memasukkan query.
2. Query dipreprocessing (case folding, stopword removal, tokenizing, stemming).
3. Query Expansion dilakukan menggunakan thesaurus.
4. TF-IDF menghitung bobot kata.
5. Cosine Similarity menghitung kemiripan query dan dokumen.
6. Dokumen diurutkan berdasarkan nilai similarity.
7. Hasil ditampilkan pada website.

## Menjalankan Program

Install dependency:

```bash
pip install -r requirements.txt
```

Jalankan aplikasi:

```bash
python app.py
```

Buka browser:

```text
http://127.0.0.1:5000
```

## Deployment

Aplikasi dideploy menggunakan Railway dan source code dikelola menggunakan GitHub.
