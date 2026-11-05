# REGISTER KENDALA & BATAS OPERASI REKAYASA (CONSTRAINT REGISTER)
## Plant-3 Train H — C3MR Optimization & Make-Up Advisory Website
**Tanggal:** 5 November 2026  
**Status:** Disetujui untuk Evaluasi Rekayasa  
**Tingkat Klasifikasi:** Hard Constraint, Warning/Operating Guidance, Model-Domain Boundary, Data-Quality Check.

---

| Constraint ID | Parameter Proses | Aturan / Evaluasi Numerik | Satuan | Tipe Kendala | Sumber Dokumen / Dasar Rekayasa | Versi | Status Persetujuan |
|---|---|---|---|---|---|---|---|
| **CONST-01** | Suction Drum Temperature 4C-8 (`H4TI004B`) | $T_{\text{suct}} \ge -45.0^\circ\text{C}$ | °C | **Hard Constraint** (Mechanical Safety Interlock) | AGENTS.md Modul 4, Badak LNG DCS Interlock Schedule: mencegah *liquid carryover* ke impeller kompresor 4K-2 | Rev 4.0 | **Approved (Verified)** |
| **CONST-02** | Suction Temperature Near-TAL Warning | $-45.0^\circ\text{C} \le T_{\text{suct}} < -42.0^\circ\text{C} \implies \text{WARNING}$ | °C | **Warning / Operating Guidance** | Prosedur Operasi Train H: pembukaan proporsional katup reheat 4TV-510 | Rev 2.1 | **Approved (Verified)** |
| **CONST-03** | MCR Circulation Safe Operating Flow Floor | $\dot{m}_{\text{MCR}} \ge 480.0\text{ t/h}$ | t/h | **Hard Constraint** (Flow Floor Envelope) | AGENTS.md Modul 3: safe operating envelope flow floor kompresor sentrifugal 4K-2/3 via kickback 4UV-53 | Rev 3.0 | **Approved (Verified)** |
| **CONST-04** | Peta Anti-Surge Dinamis Kompresor Sentrifugal | $\Delta p$ vs $Q_{\text{actual}}$ pada kurva surge map | % margin | **Protection Map** (Dynamic Anti-Surge) | Elliott / Cooper Centrifugal Compressor Operating Map | Pending | **NOT EVALUATED** (Kurva map dinamis belum diintegrasikan) |
| **CONST-05** | Mahalanobis Distance ILR Composition | $D_M(\boldsymbol{\xi}) \le 3.080216$ | — | **Model-Domain Boundary** | AGENTS.md Modul 5: batas elipsoid $\chi^2_{0.95, 4}$ dari 1.475 shift operasional kilang Badak | v1.0 | **Approved (Verified)** |
| **CONST-06** | Mahalanobis Distance Warning Margin | $2.50 < D_M(\boldsymbol{\xi}) \le 3.0802 \implies \text{WARNING}$ | — | **Warning / Operating Guidance** | Model Governance Protocol: komposisi mendekati tepi elipsoid historis | v1.0 | **Approved (Verified)** |
| **CONST-07** | Thermodynamic Suction Superheat (PR-EOS) | $T_{\text{suct}} - T_{\text{dew}}(\text{PR}) \ge 3.0^\circ\text{C}$ | °C | **Hard Constraint** (Thermodynamic Phase Protection) | First-principles Peng-Robinson EOS flash calculation: menjamin 100% fasa gas tanpa kondensasi di suction drum | v1.0 | **Approved (Verified)** |
| **CONST-08** | MCHE Warm-End Approach Temperature | $\Delta T_{\text{approach}} = T_{\text{hp, in}} - T_{\text{suct}} \ge 2.0^\circ\text{C}$ | °C | **Hard Constraint** (2nd Law Thermodynamics) | AGENTS.md Modul 2: pinch protection, melarang terjadinya *temperature crossover* ($\Delta T \le 0$) | v1.0 | **Approved (Verified)** |
| **CONST-09** | Simplex Composition Closure & Non-Negativity | $\sum_{i=1}^5 x_i \equiv 100.00\text{ mol\%}$ dan $x_i \ge 0.0$ | mol% | **Data-Quality Check** (Conservation Law) | Hukum Kekekalan Massa pada ruang Simpleks $\mathcal{S}^5$ Aitchison | v1.0 | **Approved (Verified)** |
| **CONST-10** | Rentang Laju Umpan Uji Model (Feed Gas Flow) | $100.0 \le \dot{m}_{\text{feed}} \le 350.0\text{ t/h}$ | t/h | **Data-Quality Check** (Model Applicability) | Rentang operasional kilang Train H ($H1FI012$) | Master 20261014 | **Approved (Verified)** |
| **CONST-11** | Freshness Limit Data DCS Snapshot | $\Delta t_{\text{data}} \le 15\text{ menit}$ | menit | **Data-Quality Check** (Freshness Guard) | Kebijakan Integritas Data Operator: snapshot kadaluarsa ditandai `STALE` | v1.0 | **Approved (Verified)** |

---

### Catatan Penting Tata Kelola Keselamatan:
1. **Tidak Ada Klaim "SEMUA AMAN"**: Setiap status di UI hanya menyatakan kepatuhan terhadap kendala di atas yang berhasil dievaluasi secara tervalidasi.
2. **Status Anti-Surge Jujur**: Status anti-surge pada website **hanya membuktikan kepatuhan terhadap batas bawah aliran sirkulasi 480.0 t/h (CONST-03)**. Status peta kompresor dinamis (CONST-04) secara jujur diberi keterangan **`Belum dievaluasi (memerlukan kurva head/dp lengkap)`**.
