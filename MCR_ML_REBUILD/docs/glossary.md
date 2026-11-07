# Glosarium Istilah Proses LNG dan Machine Learning (Glossary)

| Istilah / Singkatan | Kepanjangan | Penjelasan Sederhana |
| :--- | :--- | :--- |
| **C3MR** | Propane-Precooled Mixed Refrigerant | Siklus pencairan gas alam yang menggunakan propana murni untuk pendinginan awal dan campuran refrigeran untuk pencairan akhir di MCHE. |
| **MCR / MR** | Mixed Component Refrigerant | Campuran fluida pendingin yang terdiri dari Nitrogen ($N_2$), Metana ($C_1$), Etana ($C_2$), Etilena ($C_2H_4$), dan Propana ($C_3$). |
| **MCHE (`4E-1`)** | Main Cryogenic Heat Exchanger | Penukar panas kriogenik utama tipe *spiral-wound* tempat gas alam didinginkan hingga menjadi LNG (sekitar $-156^\circ\text{C}$). |
| **MITA** | Minimum Internal Temperature Approach | Selisih suhu terkecil antara aliran fluida panas dan aliran fluida dingin di dalam MCHE (batas aman $\ge 1.50^\circ\text{C}$). |
| **TAL** | Temperature Alarm Low | Batas alarm suhu rendah pada suction drum kompresor `4C-8` ($\ge -45.0^\circ\text{C}$) untuk mencegah cairan masuk ke kompresor. |
| **Anti-Surge Floor** | Minimum Safe Compressor Flow | Laju alir massa minimum ($\ge 480.0\text{ t/h}$) yang harus melewati kompresor sentrifugal agar tidak terjadi aliran balik (*surge*). |
| **DCS** | Distributed Control System | Sistem komputer pengendali dan perekam data sensor otomatis di ruang kontrol kilang (Yokogawa Centum VP). |
| **GC** | Gas Chromatography | Analisis laboratorium untuk mengukur persentase mol masing-masing komponen gas di dalam sampel refrigeran atau umpan. |
| **ILR** | Isometric Log-Ratio | Transformasi matematika yang memetakan data komposisi persentase (jumlah 100%) ke koordinat bebas sehingga aman diproses oleh model regresi. |
| **Mahalanobis Distance ($D_M$)** | Jarak Statistik Multivariat | Ukuran seberapa jauh suatu resep komposisi dari rata-rata operasi historis kilang dengan memperhitungkan korelasi antar komponen (batas aman $D_M \le 3.0802$). |
| **Target Leakage** | Kebocoran Variabel Target | Kesalahan pemodelan ketika variabel yang secara langsung menghitung target (seperti aliran uap turbin penggerak kompresor) ikut dimasukkan sebagai fitur input. |
| **NMAE** | Normalized Mean Absolute Error | Rata-rata kesalahan absolut prediksi dibagi nilai rata-rata aktual, dinyatakan dalam persen ($< 1.0\%$). |

