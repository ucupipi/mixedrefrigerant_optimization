# Kamus Fitur dan Rekonsiliasi Tag Instrumen (Feature Dictionary)

Dokumen ini mendefinisikan seluruh tag sensor Distributed Control System (DCS), hasil kromatografi gas laboratorium (GC), koordinat transformasi komposisi Isometric Log-Ratio (ILR), serta variabel target yang dikarantina pada proyek `MCR_ML_REBUILD` untuk Badak LNG Plant-3 Train H.

## 1. Aturan Tata Kelola Fitur & Satuan Rekayasa
1. **Klasifikasi Sensor (`Category`):** Setiap variabel dikelompokkan ke dalam kategori pengukuran fisik: `flow` (laju alir massa/mol), `temperature` (suhu proses/ambient), `pressure` (tekanan proses), `valve` (bukaan katup kontrol/recycle), `composition` (fraksi mol komponen gas/refrigeran), `ilr_coordinate` (koordinat ruang simpleks tertransformasi), atau `quarantined_target` (variabel target yang dilarang masuk matriks fitur `X`).
2. **Tipe Data (`Data_Type`):** Seluruh fitur numerik kontinu disimpan sebagai `float64`, indeks shift sebagai `int64`, dan penanda status/rezim sebagai `categorical`.
3. **Batas Fisik & Deteksi Nilai Hilang:** Nilai di luar rentang fisik instrumen (`Min` hingga `Max`) atau pembacaan NaN akibat gangguan transmisi ditandai menggunakan flag kualitas data sebelum masuk ke tahap pemodelan.
4. **Karantina Kebocoran Target (Target Leakage Firewall):** Sebanyak 10 variabel yang merekonstruksi target daya poros atau aliran uap penggerak turbin (`4KT-1`, `4KT-2`, `4KT-3`) terdaftar di tabel di bawah dengan status `QUARANTINED` dan dihapus secara ketat dari matriks fitur `features_unleakaged.parquet`.

## 2. Tabel Rekonsiliasi Tag Sensor, Fitur, dan Variabel Karantina

| Tag_ID | Category | Description | Unit | Data_Type | Min | Typical_Nominal | Max | Role_Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| H4TI004B | temperature | 1st Stage MCR Suction Drum 4C-8 Vapor Outlet Temperature (Safety Interlock TAL >= -45.0 degC) | °C | float64 | -50.0 | -41.5 | 40.0 | FEATURE_ACTIVE |
| 4UV-53 | valve | MCR Compressor Secondary Anti-Surge Kickback Recycle Valve Opening | % | float64 | 0.0 | 18.5 | 100.0 | SAFETY_BOUNDARY |
| 4TV-510 | valve | MCR Suction Drum 4C-8 Warm Gas Reheat Valve Opening (Cold Suction Protection) | % | float64 | 0.0 | 5.0 | 100.0 | SAFETY_BOUNDARY |
| H1PIC033 | pressure | Treated Feed Gas Inlet Header Pressure to MCHE 4E-1 | kg/cm2 | float64 | 35.0 | 45.2 | 55.0 | FEATURE_ACTIVE |
| H4PIC002 | pressure | MCR 1st Stage Compressor 4K-2 Suction Drum 4C-8 Pressure | bar | float64 | 2.5 | 4.1 | 6.5 | FEATURE_ACTIVE |
| H4PI013 | pressure | MCR 2nd Stage Compressor 4K-3 Discharge Header Pressure | kg/cm2 | float64 | 30.0 | 46.8 | 55.0 | FEATURE_ACTIVE |
| H4PDIC024 | pressure | Main Cryogenic Heat Exchanger (MCHE 4E-1) Warm/Middle Bundle Differential Pressure | kg/cm2 | float64 | 0.0 | 0.24 | 0.50 | FEATURE_ACTIVE |
| H4TI016 | temperature | MCHE 4E-1 Warm End Mixed Refrigerant Inlet Temperature | °C | float64 | -45.0 | -33.2 | 35.0 | FEATURE_ACTIVE |
| H4TI019 | temperature | MCHE 4E-1 Warm End Feed Gas Inlet Temperature after C3 Chiller | °C | float64 | -45.0 | -33.0 | 35.0 | FEATURE_ACTIVE |
| H4TI042 | temperature | MCHE 4E-1 Middle Bundle Mixed Refrigerant Temperature | °C | float64 | -140.0 | -118.5 | -80.0 | FEATURE_ACTIVE |
| H4TI055 | temperature | MCHE 4E-1 Top Warm End LNG Rundown Outlet Temperature | °C | float64 | -165.0 | -156.4 | -140.0 | FEATURE_ACTIVE |
| H0TI001 | temperature | Plant-3 Ambient Dry-Bulb Air Temperature | °C | float64 | 22.0 | 29.5 | 36.0 | FEATURE_ACTIVE |
| H0TI002 | temperature | Cooling Water Supply Header Temperature to Surface Condensers | °C | float64 | 24.0 | 28.8 | 34.0 | FEATURE_ACTIVE |
| H4FI001 | flow | MCR Circulation Mass Flow Rate to MCHE Shell Side (Anti-Surge Floor >= 480.0 t/h) | t/h | float64 | 300.0 | 520.0 | 750.0 | FEATURE_DECISION |
| H1FI012 | flow | Treated Natural Gas Feed Flow Entering Scrub Column 3C-1 Overhead | t/h | float64 | 250.0 | 750.0 | 950.0 | FEATURE_ACTIVE |
| comp_4C-8_N2 | composition | MCR Suction Drum 4C-8 Lab GC Nitrogen (N2) Mole Fraction | mol% | float64 | 0.50 | 2.17 | 8.50 | FEATURE_DECISION |
| comp_4C-8_C1 | composition | MCR Suction Drum 4C-8 Lab GC Methane (C1) Mole Fraction | mol% | float64 | 35.00 | 44.41 | 55.00 | FEATURE_DECISION |
| comp_4C-8_C2 | composition | MCR Suction Drum 4C-8 Lab GC Ethane (C2) Mole Fraction | mol% | float64 | 30.00 | 46.88 | 55.00 | FEATURE_DECISION |
| comp_4C-8_C2H4 | composition | MCR Suction Drum 4C-8 Lab GC Ethylene (C2H4) Mole Fraction | mol% | float64 | 0.00 | 0.01 | 45.00 | FEATURE_DECISION |
| comp_4C-8_C3 | composition | MCR Suction Drum 4C-8 Lab GC Propane (C3) Mole Fraction | mol% | float64 | 0.00 | 6.53 | 12.00 | FEATURE_DECISION |
| xi_1 | ilr_coordinate | Isometric Log-Ratio Coordinate 1: N2 vs (C1, C2, C2H4, C3) | dimensionless | float64 | -6.00 | -2.18 | 2.00 | FEATURE_ENGINEERED |
| xi_2 | ilr_coordinate | Isometric Log-Ratio Coordinate 2: C1 vs (C2, C2H4, C3) | dimensionless | float64 | -4.00 | 1.85 | 5.00 | FEATURE_ENGINEERED |
| xi_3 | ilr_coordinate | Isometric Log-Ratio Coordinate 3: C2 vs (C2H4, C3) | dimensionless | float64 | -4.00 | 2.41 | 6.00 | FEATURE_ENGINEERED |
| xi_4 | ilr_coordinate | Isometric Log-Ratio Coordinate 4: C2H4 vs C3 | dimensionless | float64 | -8.00 | -4.58 | 4.00 | FEATURE_ENGINEERED |
| shift_id | categorical | Discrete 8-Hour Shift Identifier Synchronized with Lab GC Sampling | dimensionless | int64 | 1 | 1250 | 5000 | GROUP_INDEX |
| H4FI029A | flow | 4KT-2 MCR 1st Stage Steam Turbine High-Pressure Steam Flow Meter | t/h | float64 | 0.0 | 158.0 | 260.0 | QUARANTINED |
| H4FI030A | flow | 4KT-3 MCR 2nd Stage Steam Turbine High-Pressure Steam Flow Meter | t/h | float64 | 0.0 | 162.0 | 260.0 | QUARANTINED |
| H4FI031A | flow | 4KT-1 Propane (C3) Precooling Steam Turbine High-Pressure Steam Flow Meter | t/h | float64 | 0.0 | 210.0 | 320.0 | QUARANTINED |
| H5FI006A | flow | LNG Rundown Product Flow Meter to Storage Tanks (Direct Target Reconstructor) | t/h | float64 | 0.0 | 680.0 | 920.0 | QUARANTINED |
| H1FI0009 | flow | Raw Plant Feed Gas Custody Flow Meter (Collinear Target Proxy) | t/h | float64 | 0.0 | 760.0 | 960.0 | QUARANTINED |
| total_steam_t_h | flow | Aggregate Turbine Driver Steam Flow (H4FI029A + H4FI030A + H4FI031A) | t/h | float64 | 0.0 | 530.0 | 840.0 | QUARANTINED |
| total_shaft_power_mw | flow | Total C3MR Train Shaft Power Target (4KT-1 C3 + 4KT-2/3 MCR) | MW | float64 | 40.0 | 108.0 | 150.0 | QUARANTINED |
| mcr_shaft_power_mw | flow | Direct MCR Compressor Shaft Power Target (4KT-2 LP + 4KT-3 HP) | MW | float64 | 25.0 | 68.2 | 95.0 | QUARANTINED |
| c3_shaft_power_mw | flow | Indirect Propane Precooling Compressor Shaft Power Target (4KT-1) | MW | float64 | 15.0 | 39.8 | 60.0 | QUARANTINED |
| exergy_destruction_mw | flow | Total MCHE 4E-1 and Compression Exergy Destruction Target | MW | float64 | 10.0 | 38.5 | 65.0 | QUARANTINED |

