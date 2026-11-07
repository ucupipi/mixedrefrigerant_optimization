# Laporan Kualitas Data dan Audit Sumber (Data Quality Report)

Dokumen ini merangkum hasil audit integritas file sumber, frekuensi pencuplikan, pola nilai hilang, dan perlakuan anomali pada `MCR_ML_REBUILD`.

## 1. Inventarisasi File Sumber Kanonik (Read-Only Raw Assets)
Seluruh 6 file mentah di `data/unprocessed/` telah diverifikasi menggunakan hash SHA-256 (`data/manifests/sha256_manifest.json`) tanpa modifikasi sedikit pun:
1. `OverallComposition_2023_2024.xlsx` — Data laboratorium GC historis (sheet `gas_routine`, 2.531 sampel shift).
2. `OverallComposition_July_2025.tsv` — Data komposisi GC periode Juli 2025.
3. `OverallComposition_August_2026.tsv` — Data komposisi GC periode Agustus 2026.
4. `ProcessParameter_2023_2024.xlsx` — Parameter proses DCS 2023–2024.
5. `ProcessParameter_July_2025.xlsx` — Rekaman DCS 1-menit periode Juli 2025.
6. `ProcessParameter_August_2026.xlsx` — Rekaman DCS 1-menit periode Agustus 2026.

## 2. Perbedaan Frekuensi Pengukuran (DCS 1-Menit vs Lab GC 8-Jam)
- **Telemetry DCS:** Diambil setiap 1 menit.
- **Kromatografi Gas (GC `4C-8`):** Diambil secara diskrit 3 kali sehari (per shift 8 jam).
- **Kebijakan Penyelarasan:** Dilarang melakukan *forward-fill* 480 menit dan menganggapnya sebagai 480 sampel independen. Data diselaraskan pada tingkat **shift-grain** menggunakan agregasi jendela tunak (*steady-state window median/mean*) di sekitar waktu sampel GC.

## 3. Penanganan Shutdown, Gap Waktu, dan Anomali Komposisi
- **Filter Shutdown/Idle:** Baris dengan laju alir umpan gas $< 100.0\text{ t/h}$ ditandai sebagai kondisi *shutdown/turnaround* dan dipisahkan dari pelatihan model operasi tunak.
- **Validasi Penjumlahan GC Mentah:** Sampel GC mentah yang jumlah komponennya berada di luar rentang fisik $[95.0\%, 105.0\%]$ ditandai sebagai anomali instrumen analisis sebelum dilakukan penutupan simpleks (*simplex closure* $\sum x_i = 100.0\%$).
- **Penanganan Komponen Nol ($C_2H_4$):** Saat pabrik beroperasi tanpa injeksi etilena ($C_2H_4 = 0.00\%$), dilakukan *multiplicative zero replacement* ($\delta = 10^{-5}$) sesuai formulasi Martin-Fernandez et al. (2003) agar transformasi logaritmik ILR tidak menghasilkan $\ln(0)$ atau `NaN`.

