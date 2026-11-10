# E2E Test Infra: Badak LNG Train H C3MR Compressor Performance Curve Digitization & ML Optimization

## Test Philosophy
- Opaque-box, requirement-driven. Derived from user requirements (R1–R5), project acceptance criteria, and `AGENTS.md` rules.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## Feature Inventory
| # | Feature | Source (Requirement) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|---------------------|:------:|:------:|:------:|:------:|
| 1 | ML Lineage & Dataset Catalog | R1 | 5 | 5 | ✓ | ✓ |
| 2 | Metric Reproduction & Dual-Domain Validation | R1 | 5 | 5 | ✓ | ✓ |
| 3 | Target Decoupling (Deterministic Balances) | R1 | 5 | 5 | ✓ | ✓ |
| 4 | Audit of R² ≈ 0.99 Claims | R1 | 5 | 5 | ✓ | ✓ |
| 5 | Steam Meter Metadata Verification | R1 | 5 | 5 | ✓ | ✓ |
| 6 | 4K-1 Curve Extraction & Digitization | R2 | 5 | 5 | ✓ | ✓ |
| 7 | 4K-2 Curve Extraction & Digitization | R2 | 5 | 5 | ✓ | ✓ |
| 8 | 4K-3 Curve Extraction & Digitization | R2 | 5 | 5 | ✓ | ✓ |
| 9 | Curve Calibration & Data Dictionary | R2 | 5 | 5 | ✓ | ✓ |
| 10 | Historical DCS Telemetry Linking | R3 | 5 | 5 | ✓ | ✓ |
| 11 | Suction Thermodynamic Conversions | R3 | 5 | 5 | ✓ | ✓ |
| 12 | Operating Envelope & Surge Verification | R4 | 5 | 5 | ✓ | ✓ |
| 13 | 480 t/h Floor & 4UV-53 / 4TV-510 Enforcement | R4 | 5 | 5 | ✓ | ✓ |
| 14 | Thermodynamic Feasibility & Power Decomposition | R4 | 5 | 5 | ✓ | ✓ |
| 15 | Publication Visualizations (Figures 1–5) | R5 | 5 | 5 | ✓ | ✓ |
| 16 | Standalone Technical Reports | R5 | 5 | 5 | ✓ | ✓ |
| 17 | IKMS 2026 Paper Revision Draft | R5 | 5 | 5 | ✓ | ✓ |
| 18 | Standalone Reproducible Validation Scripts | R5 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test Runner: Python test suite executed via `pytest` or standalone Python runner scripts.
- Location: `tests/e2e/` and standalone validation test runner in `D:\User\Documents\KULIAH\LOMBA\IKMS 2026\scripts\`.
- Pass/Fail Semantics: Exit code 0, all assertions pass, zero tolerance for magic numbers, NaN, or physical violations.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | P10 Deep Turndown Operation (141.22 t/h LNG) with 4UV-53 Kickback Modulation | F10, F11, F12, F13, F14 | High |
| 2 | P50 Nominal Mid-Load Operation (225.77 t/h LNG) Envelope Compliance | F10, F11, F12, F13, F14 | Medium |
| 3 | P90 Baseload Liquefaction (308.27 t/h LNG) & Maximum Heat Exchanger Duty | F10, F11, F12, F14, F15 | High |
| 4 | Decoupled ML Pipeline Inference & Deterministic Stoichiometric Balances | F1, F2, F3, F4, F5 | High |
| 5 | Full Operating Map Verification Across Speeds (70% to 105% MCS) for 4K-1/2/3 | F6, F7, F8, F9, F12 | High |
| 6 | End-to-End Paper Revision & Visualization Artifact Audit | F15, F16, F17, F18 | Medium |

## Coverage Thresholds
- Tier 1: 18 features × 5 = 90 test cases
- Tier 2: 18 features × 5 = 90 test cases
- Tier 3: Pairwise coverage of major feature interactions = 20 test cases
- Tier 4: Real-world operational scenarios = 6 test cases
- Total Minimum Test Cases: 206 test cases

