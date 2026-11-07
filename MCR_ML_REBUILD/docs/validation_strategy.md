# Strategi Validasi dan Pencegahan Kebocoran Data (Validation Strategy)

Dokumen ini menjelaskan metode pembagian data (*data splitting*), validasi silang (*cross-validation*), tata urutan prapemrosesan, serta aturan pengamanan kebocoran target pada `MCR_ML_REBUILD`.

## 1. Pembagian Kronologis (Chronological Split 80:20)
Data deret waktu proses industri memiliki autokorelasi temporal yang kuat. Oleh sebab itu, pengacakan baris secara bebas (`random shuffle split`) dilarang untuk evaluasi performa utama.
- **Train Partition (80% awal secara kronologis):** Digunakan untuk fitting parameter prapemrosesan (scaler, imputer, centroid/kovarians ILR) dan pelatihan model.
- **Purge / Embargo Buffer:** Jendela transisi pada perbatasan *train* dan *test* dapat diberikan *purge buffer* agar jendela agregasi bergulir (*rolling window*) dari akhir data *train* tidak bocor ke awal data *test*.
- **Test Partition (20% akhir secara kronologis):** Disimpan terpisah secara ketat (*out-of-sample*) untuk menguji kemampuan generalisasi model pada periode waktu masa depan.

## 2. Validasi Silang Berkelompok per Shift (`GroupKFold` by `shift_id`)
Karena pengambilan sampel laboratorium kromatografi gas (GC) pada drum `4C-8` dilakukan secara diskrit per shift (3 kali sehari), seluruh observasi dalam satu shift berbagi label komposisi GC yang sama.
- Validasi silang wajib menggunakan `GroupKFold(n_splits=5)` dengan `groups = shift_id`.
- Hal ini memastikan tidak ada sampel dari shift yang sama yang terpecah ke dalam *training fold* dan *validation fold* secara bersamaan.

## 3. Tata Urutan Prapemrosesan (Strict Preprocessing Ordering)
1. Lakukan pemisahan indeks *train* dan *test* terlebih dahulu.
2. Terapkan pemeriksaan `quarantined_tags` (`src/data/governance.py`) untuk memastikan 10 tag pembentuk target tidak ada di matriks fitur `X`.
3. Hitung statistik normalisasi (`StandardScaler`), nilai tengah imputasi, serta rata-rata $\boldsymbol{\mu}_{\text{ILR}}$ dan matriks kovarians $\boldsymbol{\Sigma}_{\text{ILR}}$ **hanya pada partisi train**.
4. Terapkan transformasi yang sudah di-fit tersebut ke partisi *validation* dan *test*.

