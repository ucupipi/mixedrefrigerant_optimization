# Kamus Data Sumber dan Skema Tabel (Data Dictionary)

Dokumen ini mendefinisikan struktur file data sumber, tabel antara (`data/interim/`), dan tabel siap-pakai (`data/processed/`) dalam `MCR_ML_REBUILD`.

## 1. Struktur File Sumber Kanonik (`data/unprocessed/`)

| Nama File | Format | Resolusi Waktu | Jumlah Kolom Utama | Peran dalam Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| `OverallComposition_2023_2024.xlsx` | Excel (`.xlsx`) | Shift 8-jam (3x/hari) | Komponen $N_2, C_1, C_2, C_2H_4, C_3, iC_4, nC_4$ | Sumber historis komposisi GC drum `4C-8` (2.531 sampel). |
| `OverallComposition_July_2025.tsv` | Tab-Separated (`.tsv`) | Shift 8-jam (3x/hari) | Komponen GC `4C-8` & Feed Gas | Rekaman GC operasional Juli 2025. |
| `OverallComposition_August_2026.tsv` | Tab-Separated (`.tsv`) | Shift 8-jam (3x/hari) | Komponen GC `4C-8` & Feed Gas | Rekaman GC operasional Agustus 2026. |
| `ProcessParameter_2023_2024.xlsx` | Excel (`.xlsx`) | Ringkasan / Shift | Tag proses utama Train H | Konteks beban operasi historis 2023–2024. |
| `ProcessParameter_July_2025.xlsx` | Excel (`.xlsx`) | 1-menit (DCS) | 170+ tag instrumen DCS | Telemetry suhu, tekanan, laju alir Juli 2025. |
| `ProcessParameter_August_2026.xlsx` | Excel (`.xlsx`) | 1-menit (DCS) | 170+ tag instrumen DCS | Telemetry suhu, tekanan, laju alir Agustus 2026. |

## 2. Skema Tabel Siap-Pakai (`data/processed/`)

### 2.1 `features_unleakaged.parquet`
Berisi matriks fitur bersih `X` pada resolusi shift operasi tunak yang telah bebas dari 10 tag pembentuk target (`quarantined_tags`):
- `shift_id` (`int64`): Identitas unik shift operasi 8 jam.
- `timestamp_utc` (`string` / `datetime64`): Waktu acuan pengambilan sampel shift.
- `H1FI012` (`float64`, $\text{t/h}$): Laju alir gas umpan terolah masuk unit pencairan.
- `H0TI001` (`float64`, $^\circ\text{C}$): Suhu udara lingkungan Plant-3.
- `H0TI002` (`float64`, $^\circ\text{C}$): Suhu air pendingin (*cooling water supply*).
- `H1PIC033` (`float64`, $\text{kg/cm}^2$): Tekanan masuk gas umpan ke MCHE `4E-1`.
- `H4PIC002` (`float64`, $\text{bar}$): Tekanan suction drum `4C-8`.
- `H4PI013` (`float64`, $\text{kg/cm}^2$): Tekanan discharge kompresor MCR tingkat 2 (`4K-3`).
- `H4TI004B` (`float64`, $^\circ\text{C}$): Suhu uap keluar suction drum `4C-8` (batas keselamatan TAL $\ge -45.0^\circ\text{C}$).
- `H4TI016`, `H4TI019`, `H4TI042`, `H4TI055` (`float64`, $^\circ\text{C}$): Profil suhu bundel hangat, tengah, dan dingin MCHE `4E-1`.
- `H4PDIC024` (`float64`, $\text{kg/cm}^2$): Kehilangan tekan diferensial MCHE ($\le 0.35\text{ kg/cm}^2$).
- `H4FI001` (`float64`, $\text{t/h}$): Laju alir sirkulasi MCR (batas anti-surge $\ge 480.0\text{ t/h}$).
- `4UV-53`, `4TV-510` (`float64`, $\%$): Bukaan katup pengaman recycle anti-surge dan reheat suction.
- `comp_4C-8_N2`, `comp_4C-8_C1`, `comp_4C-8_C2`, `comp_4C-8_C2H4`, `comp_4C-8_C3` (`float64`, fraksi mol ter-closure $\sum x_i = 1.0$).
- `xi_1`, `xi_2`, `xi_3`, `xi_4` (`float64`, dimensionless): Koordinat Euclidean Isometric Log-Ratio (ILR).

### 2.2 `target_energy.parquet`
Berisi matriks variabel target `y` yang dipisahkan secara fisik dari matriks fitur:
- `shift_id` (`int64`): Kunci penghubung shift operasi.
- `mcr_shaft_power_mw` (`float64`, **MW**): Daya poros langsung kompresor MCR (`4KT-2` + `4KT-3`).
- `c3_shaft_power_mw` (`float64`, **MW**): Daya poros kompresor propana precooling (`4KT-1`).
- `total_shaft_power_mw` (`float64`, **MW**): Total daya poros Train C3MR (`mcr_shaft_power_mw + c3_shaft_power_mw`).
- `exergy_destruction_mw` (`float64`, **MW**): Destruksi eksergi total MCHE dan kompresi.

