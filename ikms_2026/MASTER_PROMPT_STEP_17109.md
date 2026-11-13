<USER_REQUEST>
# MASTER PROMPT — COMPLETE STORYLINE RECONSTRUCTION & FULL PAPER REWRITING
## IKMS 2026 | Mixed Refrigerant Optimization | Badak LNG Train H C3MR

---

# 1. ROLE AND MISSION

Act as a senior scientific editor, LNG process engineer, thermodynamics reviewer, machine learning researcher, and technical manuscript reviewer.

You are responsible for reconstructing the complete scientific storyline and rewriting the full paper for the Indonesia Knowledge Management Summit (IKMS) 2026.

This is not a proofreading assignment.

Your task is to critically redesign the manuscript from its central research argument, section structure, technical explanations, evidence presentation, and academic writing.

The final paper must be:

1. Technically defensible.
2. Scientifically coherent.
3. Concise without omitting essential engineering information.
4. Understandable to a multidisciplinary energy-sector audience.
5. Specific to the actual operating problem at Badak LNG Train H.
6. Written in natural, professional academic Bahasa Indonesia.
7. Free from generic AI-generated language, exaggerated claims, unnecessary repetition, and unsupported conclusions.

The intended result is a focused engineering paper, not a long project report or a collection of disconnected technical calculations.

**Primary instruction: Reconstruct the scientific argument first. Rewrite the manuscript only after the argument and evidence have been audited.**

---

# 2. RESEARCH CONTEXT

The study concerns the propane-precooled mixed-refrigerant (C3MR) liquefaction process at PT Badak NGL, Train H.

The research focuses on the relationship between:

- LNG production rate.
- Mixed Refrigerant (MR) circulation rate.
- Five-component MR composition.
- Main Cryogenic Heat Exchanger (MCHE) thermal performance.
- Centrifugal compressor operating limits.
- Compressor power and associated utility consumption.

The five MR components are:

1. Nitrogen (N₂)
2. Methane (CH₄)
3. Ethane (C₂H₆)
4. Ethylene (C₂H₄)
5. Propane (C₃H₈)

The composition is constrained by:

\[
\sum_{i=1}^{5}x_i=1
\]

The research intends to develop a plant-specific framework that integrates historical operating data, compositional analysis, thermodynamic modeling, machine learning, and constrained optimization.

The central engineering problem is not simply that MR circulation is high.

It is that the refrigerant operating condition must adapt to changing feed-gas composition and LNG production rate while satisfying the physical requirements of the heat exchanger and rotating equipment.

Do not reduce this research to a generic statement such as "AI is used to optimize LNG production."

---

# 3. MANDATORY SOURCE AUDIT

Before rewriting, discover and inspect the actual project directory.

Do not rely exclusively on the current manuscript or previous executive summaries.

At minimum, inspect the following sources if present:

## A. Manuscript and guideline sources

- `IKMS2026_FullPaper_PNJ_Final.docx`
- `IKMS2026_FullPaper_PNJ.docx`
- `IKMS 2026 Guide Book.pdf`
- The official IKMS full-paper template.
- Existing abstract and previous manuscript versions.
- Existing reference list and citation register.

## B. Current research and reconstruction sources

- `MR_OPTIMIZATION_REBUILD/`
- `ikms_2026/rebuild_v3_3/`
- `ikms_2026/clean_rebuild_v2/`
- `MASTER_HANDOVER_REBUILD_v3_3.md`
- `BASELINE_RECONSTRUCTION_REPORT.md`
- Latest P4 thermodynamic investigation and residual reconciliation outputs.
- Latest source-code modifications and test reports.

## C. Primary operational evidence

Locate the actual source files for:

- DCS historian data.
- Gas chromatography (GC) records.
- Instrument and tag dictionaries.
- Operating-point and quantile definitions.
- P&IDs and process flow diagrams.
- Compressor OEM performance curves.
- Thermodynamic property-package calculations.
- Energy, steam, fuel-gas, and emissions calculations.

## D. Modeling and verification sources

Inspect:

- Data preprocessing scripts.
- MR composition reconstruction and soft-sensor scripts.
- ILR transformation scripts.
- Thermodynamic engine.
- Surrogate training and validation scripts.
- Optimization scripts.
- Independent numerical verification scripts.
- Claim-evidence registers.
- Uncertainty and discrepancy registers.

### Source hierarchy

Apply the following priority:

| Priority | Source | Use |
|---|---|---|
| 1 | Original DCS, GC, instrument records, and authenticated engineering documents | Primary evidence |
| 2 | Reproducible calculations, verified simulator outputs, and source code | Computational evidence |
| 3 | Independent validation and audit reports | Verification evidence |
| 4 | Peer-reviewed literature and authoritative engineering references | Scientific context |
| 5 | Current and historical manuscript drafts | Writing references only |

An old manuscript does not become authoritative merely because it contains a detailed table or a confident statement.

When sources disagree, preserve the conflict in a discrepancy register. Do not choose the most favorable number.

---

# 4. CRITICAL SCIENTIFIC GUARDRAILS

These instructions override any previous manuscript statement that conflicts with the current evidence.

## 4.1 The 2017–2026 comparison must be reassessed

The current research data availability is primarily 2024–2026.

The authors have previously identified that the original 2017 operating dataset cannot be obtained.

Therefore:

- Do not claim to have analyzed 2017 and 2026 minute-level DCS datasets unless the original 2017 data are actually recovered.
- Remove the statement that 1,051,200 one-minute records originate from 2017 and 2026 if this cannot be demonstrated.
- Do not present 88.1 mol% methane in 2017 as a directly measured comparative dataset without an authenticated primary source.
- A historical composition may only be retained as a documented historical reference if its provenance is confirmed and it is clearly distinguished from current measurements.
- Do not use a historical reference value as if it were part of the model training dataset.

The main operational analysis must use the actual available and traceable 2024–2026 records.

## 4.2 Reassess the 59.3% energy-consumption claim

The current manuscript states that C3MR accounts for 59.3% of Badak LNG's energy consumption.

Retain this value only when the following are established:

- Original reference.
- Measurement or calculation basis.
- Plant boundary.
- Time period.
- Included equipment and utilities.

If the original source cannot substantiate the exact scope, remove or qualify the statement.

Do not use this statistic as decorative opening material.

## 4.3 P4 thermodynamic validation remains an active blocker

The previous `neqsim_engine.py` implementation contained a dimensional inconsistency in which an energy shortfall in MW entered a temperature-approach calculation in °C.

The resulting MITA values were contaminated.

The corrected engine `mche_engine_v33.py` has subsequently been developed, but the reported energy closure remains approximately:

| Quantile | Reported energy residual |
|---|---:|
| P10 | -4.3% |
| P50 | +10.6% |
| P90 | +15.3% |

The full-MCR topology is currently a leading hypothesis, not an accepted final process topology.

Consequently:

- MITA is not yet qualified.
- Thermal crossover is not established.
- The energy closure remains unresolved.
- The physical baseline has not received final qualification.
- P6–P10 optimization results remain blocked pending P4 validation.

You must inspect the latest actual project status before writing the results section.

Do not restore old conclusions simply because they already exist in the manuscript.

## 4.4 Historical optimization outputs are quarantined

The following categories must be treated as unverified until reproduced using a qualified physical baseline:

- Previous optimized MR recipes.
- Previous optimal circulation schedules.
- Old MITA results.
- Old compressor power savings.
- Old SEC improvements.
- Old steam savings.
- Old annual energy savings.
- Old fuel-gas savings.
- Old economic estimates.
- Old CO₂ reduction estimates.
- Claims of zero-CAPEX implementation.

This includes previously reported figures such as:

- 28.98 MW compressor power reduction.
- 227.52 GWh/year energy savings.
- USD 8.48 million/year fuel value.
- 239,889.7 tonnes/year steam savings.
- 49,961.8 tonnes/year CO₂ reduction.
- The historical 14.805 MW and 116.215 GWh/year alternatives.

These figures are historical audit checkpoints, not acceptable expected outcomes.

Do not retain them unless the complete calculation chain is independently validated again.

## 4.5 NeqSim and HYSYS must not be confused

NeqSim PR-EOS runtime has been successfully restored after correcting the Java environment.

However, this does not establish numerical equivalence with Aspen HYSYS.

Distinguish explicitly:

- NeqSim property-package calculations.
- Aspen HYSYS simulations.
- Direct HYSYS automation.
- Imported HYSYS results.
- Analytical engineering calculations.

Do not claim HYSYS was executed directly if the current environment did not run HYSYS.

Do not describe two simulators as equivalent merely because both use Peng–Robinson EOS.

## 4.6 Compressor power is not directly measured by a torquemeter

Train H does not have a direct shaft torque measurement available in the current evidence.

Therefore distinguish:

- Measured DCS variables.
- OEM-map-derived compressor performance.
- Thermodynamic-model-derived shaft power.
- Surrogate-predicted power.

Do not describe calculated shaft power as directly measured plant power.

## 4.7 Composition statistics and Mahalanobis geometry

For five MR components, the composition simplex has four independent degrees of freedom.

Therefore, the ILR representation has four coordinates.

If the 95% Mahalanobis threshold is calculated from a chi-square distribution, the appropriate degree of freedom is four:

\[
D_{\mathrm{critical}}=
\sqrt{\chi^2_{0.95,4}}
\approx 3.0802
\]

Check every manuscript equation and implementation for consistency.

Do not retain an obsolete degree-of-freedom value of six.

---

# 5. RECONSTRUCT THE CENTRAL STORYLINE

Build the paper around one central argument:

**Changing feed-gas conditions and production rates create an operating challenge for the C3MR refrigeration system. Adjusting MR composition and circulation requires a framework that combines plant data, compositional constraints, thermodynamic feasibility, and compressor operating limits.**

The paper must answer four questions:

1. What operational problem is observed at Train H?
2. Why can MR composition and circulation not be optimized using production rate or machine learning alone?
3. How does the proposed framework integrate operational data and physical constraints?
4. What results have actually been validated, and what engineering implications follow?

## 5.1 General-to-specific narrative

Use this progression.

### Level 1 — General industrial context

Explain the energy requirement of LNG liquefaction briefly.

Limit general energy-transition statements to what is necessary to establish the engineering problem.

### Level 2 — Process-specific context

Explain why C3MR is relevant.

Describe the role of propane precooling, mixed refrigerant, MCHE, and compressors only to the extent required to understand the research.

### Level 3 — Plant-specific problem

Present the actual Train H operating evidence.

Focus on the relationship between:

- Feed-gas throughput.
- LNG production.
- MR circulation.
- MR-to-LNG ratio.
- Relevant energy indicators.

Clearly distinguish raw feed, treated feed, and LNG rundown.

Use consistent tags, units, and quantile definitions.

### Level 4 — Engineering challenge

Explain why simply reducing circulation can create unacceptable conditions.

Discuss only relevant constraints, such as:

- MCHE thermal feasibility.
- MR phase behavior.
- Compressor surge and operating envelope.
- Compressor suction temperature.
- Hydraulic or pressure-drop limits.
- Actual plant equipment and control limitations.

### Level 5 — Research gap

Explain precisely what existing approaches fail to address in this application.

Avoid statements such as "no research has ever studied this" unless supported by a systematic literature review.

Use a defensible gap:

The research addresses the difficulty of integrating compositional constraints, plant operating data, thermodynamic feasibility, and compressor operating limits into one plant-specific decision framework.

### Level 6 — Research objective and contribution

End the introduction with a direct objective statement.

The objective must identify:

- What is being optimized.
- Which operating system is studied.
- Which variables are decision variables.
- Which constraints determine feasibility.
- What constitutes the contribution.

Do not introduce final numerical savings in the introduction.

---

# 6. PROPOSED PAPER STRUCTURE

Use this as the default architecture, then adapt it to the official IKMS template.

Do not retain existing headings simply because the previous draft uses them.

## TITLE

Use a concise title that reflects the actual validated research scope.

A provisional title is:

**OPTIMASI KOMPOSISI DAN LAJU SIRKULASI MIXED REFRIGERANT BERBASIS DATA OPERASI DAN PEMBATAS TERMODINAMIKA PADA SISTEM C3MR TRAIN H PT BADAK NGL**

If the machine-learning component is demonstrably central and validated, it may be included in the title.

Do not overemphasize machine learning merely to make the work appear more advanced.

Avoid titles that imply demonstrated energy savings when the optimization has not been independently validated.

## ABSTRACT

Write the abstract after the full results have been finalized.

Maximum 500 words, subject to the official IKMS guidance.

It must include:

1. Industrial urgency.
2. Specific research problem.
3. Research objective.
4. Dataset and methods.
5. Main validated results.
6. Engineering implications and limitations.

Do not use a list of every algorithm or every numerical result.

The abstract must accurately represent the final paper.

## 1. PENDAHULUAN

Recommended flow:

**Paragraph 1 — LNG and energy context**

Introduce LNG liquefaction energy requirements and the relevance of refrigeration efficiency.

**Paragraph 2 — C3MR system**

Explain the role of MR composition and circulation in MCHE cooling and compressor power.

**Paragraph 3 — Train H operating problem**

Present the verified operational mismatch between production load and refrigerant circulation.

Use only a small number of carefully selected quantitative indicators.

**Paragraph 4 — Engineering limitations and research gap**

Explain why data-driven optimization alone or unconstrained simulation optimization is insufficient for actual plant application.

**Paragraph 5 — Objective and contribution**

State the study objective and the specific methodological contribution.

Keep the introduction focused. Do not turn it into a general LNG textbook chapter.

## 2. METODOLOGI PENELITIAN

### 2.1 Objek Penelitian dan Batas Sistem

Describe Train H C3MR and identify the equipment directly relevant to the study.

Explain the MCHE and the relevant compressor system.

Use a PFD or simplified process diagram.

Do not describe unrelated plant units in detail.

Clearly distinguish:

- MCR compression system.
- Propane precooling system.
- Process heat-exchange boundaries.
- Steam utility boundary, if included in the research.

### 2.2 Data Operasi dan Pra-pemrosesan

Explain:

- DCS historian period.
- Number of original records.
- Data sampling interval.
- GC sample count.
- Instrument tags.
- Data synchronization.
- Steady-state selection.
- Missing-data treatment.
- Outlier and transient handling.
- Operating quantile construction.

State the actual dataset population and the retained sample count separately.

Do not report raw record count as the number of independent training samples.

Avoid unnecessary descriptions of basic data cleaning operations.

### 2.3 Rekonstruksi Komposisi Mixed Refrigerant

Explain the GC composition dataset and its relationship with operating records.

If a minute-level soft sensor is used, document:

- GC sampling interval.
- Training samples.
- Independent sample definition.
- Features.
- Target variables.
- Temporal validation.
- Prediction uncertainty.

Do not treat repeated minute-level predictions generated from a single GC sample as independent chemical measurements.

Explain the need for compositional-data analysis.

Introduce ILR as the method used to represent five-component MR composition in four independent coordinates.

### 2.4 Model Termodinamika dan Evaluasi Kelayakan Fisik

Explain the thermodynamic calculation approach.

Include only verified details:

- Property-package runtime.
- EOS configuration.
- Component list.
- Phase-equilibrium calculation.
- Stream boundaries.
- Pressure and temperature inputs.
- Mass and energy balance.
- MCHE profile construction.

The MCHE pinch methodology must be explained rigorously.

Distinguish temperature approach from energy-balance residual.

Do not report a qualified MITA until the current P4 model passes validation.

### 2.5 Model Surrogate Machine Learning

Explain why the surrogate model is needed.

Describe:

- Model architecture.
- Input variables.
- Target variables.
- Training dataset.
- Feature engineering.
- Chronological or group-based partitioning.
- Hyperparameter selection.
- Independent test set.
- Performance metrics.

Explain how the surrogate supports computational efficiency without replacing physical verification.

Do not list multiple algorithms unless they serve a specific methodological purpose.

Do not claim high accuracy proves physical validity.

### 2.6 Formulasi Optimasi

Clearly distinguish:

**Decision variables:**
- MR composition.
- MR circulation rate or load-dependent circulation schedule.

**Constraints:**
- Composition simplex.
- Historical compositional envelope.
- MCHE thermal feasibility.
- Compressor operating envelope.
- Surge margin.
- Suction temperature.
- Actual process and equipment restrictions.

Define the objective function and explain why it is appropriate.

Identify which constraints are hard physical limits and which are statistical or operational guardrails.

Do not describe safety control valves as optimization decision variables unless they are genuinely manipulated and validated as such.

### 2.7 Perhitungan Energi dan Dampak Turunan

Include this subsection only if the underlying calculations pass independent validation.

Explain how compressor power, steam demand, boiler fuel gas, cost, and CO₂ emissions are calculated.

Distinguish direct results from secondary estimates.

Do not combine compressor shaft power, steam consumption, and fuel gas into a single energy quantity without a consistent accounting boundary.

---

## 3. HASIL DAN PEMBAHASAN

This section should carry the scientific argument.

Avoid reporting a result and repeating the same result in several subsequent paragraphs.

Each subsection must answer a specific research question.

### 3.1 Karakteristik Operasi Baseline

Present the measured relationship between:

- Feed-gas throughput.
- LNG production.
- MR circulation.
- MR-to-LNG ratio.
- Energy indicators.

Explain what the measured data establish and what they do not establish.

Do not automatically interpret correlation as causation.

### 3.2 Karakteristik Komposisi dan Ruang Operasi MR

Discuss the observed MR composition distribution and its implications.

Present the ILR and Mahalanobis approach only where necessary to explain why composition optimization must respect the historical operating domain.

Show the real operating envelope and candidate composition only if validated.

### 3.3 Validasi Model Termodinamika

Present evidence of thermodynamic model validity.

Include:

- Phase behavior.
- Stream mass balances.
- Component balances.
- Energy closure.
- Temperature profiles.
- MCHE minimum approach.
- Pressure and temperature boundary conditions.

This section is not allowed to present a validated MITA while P4 remains blocked.

If the current closure problem remains unresolved, report the remaining residuals and identify the limits of the physical reconstruction.

Do not conceal failed cases.

### 3.4 Kinerja Model Machine Learning

Present the model performance using independent test data.

Use only metrics that have a clearly stated target and validation basis.

Explain:

- What the model predicts.
- How accurately it predicts.
- Where its predictions are reliable.
- Where its predictions should not be used.

Avoid presenting R² as the only measure of performance.

### 3.5 Hasil Optimasi Komposisi dan Sirkulasi MR

Include only if the P4 and downstream validation gates have passed.

Present:

- Optimal MR composition.
- Circulation schedule by load.
- Baseline-versus-optimized comparison.
- Compressor power.
- SEC.
- Constraint margins.
- Prediction uncertainty.
- Direct thermodynamic verification.

Baseline and optimized cases must use the same production throughput and comparable operating boundaries.

A surrogate-only optimum must be labelled as a candidate, not a physically validated solution.

If P4 remains unresolved, replace this subsection with a transparent discussion of preliminary optimization limitations. Do not manufacture an optimized result.

### 3.6 Implikasi Energi, Ekonomi, dan Lingkungan

Include only validated downstream calculations.

Keep the following separate:

1. Compressor shaft power reduction.
2. Steam demand reduction.
3. Boiler fuel-gas reduction.
4. Economic value.
5. Scope 1 emissions.

Clearly state all assumptions and annualization methods.

Do not claim zero CAPEX, instant payback, or direct implementation unless the actual valves, dosing procedure, operational feasibility, and management-of-change requirements have been verified.

### 3.7 Implikasi terhadap Operasi dan Knowledge Management

IKMS is a knowledge-management forum.

Explain the contribution in a practical and evidence-based way.

For example:

- Transforming dispersed DCS and GC information into traceable operating knowledge.
- Linking operational data to thermodynamic models.
- Making engineering assumptions explicit.
- Creating a reproducible evaluation framework.
- Supporting engineering decision-making with traceable constraints and evidence.

Do not force a generic discussion of digital transformation or artificial intelligence.

The knowledge-management contribution must emerge naturally from the actual research workflow.

---

## 4. KESIMPULAN

Write three to five concise conclusions.

The conclusions must answer the research objective directly.

Use this sequence:

1. What operational problem was established?
2. What methodological framework was developed?
3. What results were independently validated?
4. What engineering implications follow?
5. What limitations remain?

Do not introduce new numbers, literature, calculations, or assumptions in the conclusion.

If the optimization is not yet physically validated, explicitly state that the work has not established a deployable optimal recipe or verified annual savings.

Avoid generic endings such as "this research is expected to be useful for the future development of the energy industry."

---

## REFERENCES

Retain only references that are actually cited.

For every reference:

- Verify author names.
- Verify publication year.
- Verify article or book title.
- Verify journal or publisher.
- Verify volume, issue, and page range where applicable.
- Verify DOI or official publication URL.

Use the citation system required by the official IKMS template.

Do not fabricate references or preserve citations that do not support the corresponding statements.

Do not copy references from unrelated drafts simply to increase the reference count.

---

# 7. NUMERICAL AND CLAIM RECONCILIATION

Before writing the final manuscript, create a master claim-evidence register.

Every important number must have:

| Field | Description |
|---|---|
| Claim ID | Unique identifier |
| Claim | Exact scientific statement |
| Value | Numerical value |
| Unit | Engineering unit |
| Source file | Original evidence |
| Source location | Sheet, column, tag, or code line |
| Calculation | Formula and inputs |
| Evidence type | Measured, calculated, simulator, model, or assumed |
| Validation status | PASS, CONDITIONAL, BLOCKED, INVALIDATED |
| Uncertainty | Available uncertainty or limitation |
| Manuscript location | Section, table, or figure |
| Release decision | Include, qualify, or exclude |

Audit every number in the current manuscript, including:

- 59.3% energy-consumption share.
- 88.1 mol% historical methane.
- 94.5 mol% lean-gas methane.
- 91.6 mol% design reference.
- 720,734 DCS records.
- 67,916 steady-state records.
- 2,531 GC samples.
- Feed-gas flow quantiles.
- Treated-feed flow quantiles.
- LNG production quantiles.
- MR circulation quantiles.
- MR/LNG ratio.
- SEC.
- Compressor shaft power.
- Steam consumption.
- Surrogate performance.
- MITA.
- Pressure drop.
- Surge margin.
- Optimal MR composition.
- Mahalanobis distance.
- Annual operating hours.
- Annual energy savings.
- Fuel-gas savings.
- Financial value.
- CO₂ reduction.

### Critical consistency checks

Investigate and resolve the following conflicts:

1. Different P10/P90 flow values appearing across drafts.
2. Raw-feed, treated-feed, and LNG rundown values being mixed.
3. Different MR circulation baselines across versions.
4. DCS proxy SEC being presented as measured shaft SEC.
5. Historical design-reference SEC being compared with actual operating SEC without equivalent boundary conditions.
6. Different reported surrogate R² values.
7. Differences between steam measured at individual turbine condensate extraction points and total steam-header measurements.
8. NeqSim output being labelled as direct HYSYS output.
9. Differences between steam, power, fuel-gas, and annualized savings.
10. Different optimized MR formulations in historical versions.

Never resolve discrepancies by selecting the number that produces the strongest manuscript.

---

# 8. STORYLINE AND WRITING QUALITY RULES

The paper must sound like it was written by engineers who understand the plant and have examined the data.

## 8.1 General-to-specific, not generic-to-generic

Start with the industrial context, but reach the actual Train H problem quickly.

Do not spend several paragraphs explaining:

- Global energy transition.
- General LNG history.
- Basic AI definitions.
- Generic advantages of optimization.
- Broad sustainability narratives.

Use the introduction to establish the research problem, not to demonstrate general knowledge.

## 8.2 One paragraph, one main idea

Every paragraph must have:

1. A clear topic sentence.
2. Supporting technical evidence.
3. An explanation of its relevance.
4. A logical transition where necessary.

Avoid paragraphs that introduce five unrelated technical issues at once.

## 8.3 Prefer direct sentences

Use active and precise academic Bahasa Indonesia.

Prefer:

"Data DCS menunjukkan bahwa laju sirkulasi MR turun lebih lambat daripada produksi LNG."

Avoid:

"Fenomena tersebut mengindikasikan adanya suatu kondisi ketidaksesuaian operasional yang secara komprehensif dapat memberikan implikasi terhadap efektivitas proses."

## 8.4 Remove AI-style expressions

Avoid unnecessary use of phrases such as:

- Dalam era transisi energi yang semakin dinamis.
- Solusi inovatif dan revolusioner.
- Pendekatan holistik dan komprehensif.
- Transformasi signifikan.
- Menjadi game changer.
- Menghadirkan peluang strategis.
- Secara komprehensif.
- Secara fundamental.
- Terobosan yang luar biasa.
- Optimalisasi yang sangat efektif.
- Membuktikan efektivitas secara mutlak.

Do not replace these phrases with different generic buzzwords.

Use a specific engineering observation instead.

## 8.5 Avoid excessive technical jargon

Explain every uncommon term once, briefly, when it first appears.

Do not repeatedly explain common abbreviations.

Use consistent terms throughout:

- Mixed Refrigerant (MR).
- Main Cryogenic Heat Exchanger (MCHE).
- Specific Energy Consumption (SEC).
- Isometric Log-Ratio (ILR).
- Minimum Internal Temperature Approach (MITA).

Use either English technical terms or their Indonesian equivalents consistently.

Do not change technical nomenclature from section to section.

## 8.6 No repetitive explanations

Avoid repeating:

- C3MR process descriptions.
- DCS dataset descriptions.
- ILR equations.
- MR component definitions.
- Compressor constraints.
- Energy-saving figures.

Explain each methodology once, then refer to its results where needed.

## 8.7 No exaggerated causal claims

Distinguish:

- Observation.
- Correlation.
- Engineering interpretation.
- Model prediction.
- Thermodynamic verification.
- Demonstrated plant performance.

Do not use words such as "menyebabkan", "membuktikan", or "menghasilkan" where the available evidence only supports "berkorelasi", "mengindikasikan", or "diprediksi".

## 8.8 Efficient academic presentation

Avoid long tables containing dozens of variables that do not help answer the research question.

Prefer a small number of essential figures and tables.

Every figure and table must answer a specific question.

Remove duplicate tables, decorative flowcharts, and charts that repeat the same message.

---

# 9. FIGURE AND TABLE STRATEGY

Develop a figure/table plan before rewriting.

Recommended essential figures:

1. Simplified C3MR Train H process diagram showing the research boundary.
2. Research methodology flowchart.
3. Baseline relationship between LNG production and MR circulation.
4. MR composition operating-domain visualization.
5. Validated MCHE temperature profile, only after P4 qualification.
6. Surrogate-model evaluation plots, only if they add information beyond the table.
7. Baseline-versus-optimized operating comparison, only after optimization qualification.

Recommended essential tables:

1. Dataset and source summary.
2. Operating quantile baseline.
3. MR composition statistics and operating domain.
4. Thermodynamic and compressor constraint register.
5. Model validation performance.
6. Baseline-versus-optimized results.
7. Energy, economic, and emissions summary.

Do not force all these figures and tables into the final paper.

Select only those that make the scientific argument clearer.

All figures must be generated directly from verified source data or calculation outputs.

All table values must trace to the master claim-evidence register.

Do not manually type numerical results into figure-generation scripts.

---

# 10. TWO-PATH MANUSCRIPT STRATEGY

The final storyline must follow the actual state of scientific validation.

## PATH A — P4 PASSES AND OPTIMIZATION IS FULLY VALIDATED

Use this route only when:

- Thermodynamic engine passes.
- Correct stream topology is established.
- Energy and mass balances pass.
- MITA is valid.
- Surrogate models pass independent validation.
- Optimization candidates pass direct physical verification.
- Energy and economic calculations are independently reconciled.

The storyline may then present:

Operational diagnosis → plant-specific constrained methodology → model validation → validated MR optimization → energy and utility implications.

## PATH B — P4 REMAINS BLOCKED OR OPTIMIZATION IS NOT VERIFIED

Do not manufacture a successful optimization story.

Reframe the manuscript around what has genuinely been achieved.

The storyline should become:

Operational diagnosis → development of a plant-specific data and compositional framework → thermodynamic reconstruction methodology → identification of physical validation challenges → limitations and requirements for safe optimization.

The paper may present:

- Verified DCS baseline observations.
- Validated GC and composition data.
- Correct compositional representation.
- Reproducible model-development workflow.
- Confirmed limitations of previous models.
- Current thermodynamic reconstruction status.
- The exact remaining evidence needed before optimization can be qualified.

Clearly label preliminary outputs as preliminary.

Do not use a future research objective as if it were a completed result.

**The final paper must reflect the strongest scientifically defensible level of completion, not the most impressive narrative.**

---

# 11. REVIEW THE PAPER AS A MULTIDISCIPLINARY IKMS REVIEWER

After rewriting, conduct three separate reviews.

## Review A — Engineering reviewer

Check:

- Process logic.
- System boundaries.
- Stream identity.
- Units.
- Thermodynamic equations.
- Compressor constraints.
- Data provenance.
- Energy balance.
- Reproducibility.

## Review B — Machine learning reviewer

Check:

- Target definition.
- Feature relevance.
- Data leakage.
- Temporal and group validation.
- Independent test set.
- Prediction uncertainty.
- Out-of-domain predictions.
- Difference between prediction accuracy and physical validity.

## Review C — General energy-sector reviewer

Check:

- Can the problem be understood quickly?
- Is the research objective obvious?
- Is the methodology easy to follow?
- Are the results presented in the right order?
- Are technical terms explained sufficiently?
- Can the reader understand the actual contribution without reading the code?
- Does the paper explain why the study matters to plant operation?

For every criticism, either fix the manuscript or record a justified reason for retaining the original wording.

---

# 12. REQUIRED EXECUTION WORKFLOW

Do not jump directly to rewriting.

Follow these stages.

### Stage 1 — Manuscript diagnosis

Inspect the complete latest manuscript.

Prepare:

`IKMS_MANUSCRIPT_DIAGNOSTIC.md`

Identify:

- Current storyline.
- Repeated arguments.
- Unnecessary background.
- Unsupported claims.
- Contradictory numbers.
- Weak transitions.
- Missing engineering explanation.
- Unclear research objectives.
- Sections requiring complete restructuring.

### Stage 2 — Claim and evidence audit

Prepare:

`IKMS_CLAIM_EVIDENCE_REGISTER.csv`

Classify every material statement as:

- VERIFIED.
- CONDITIONALLY SUPPORTED.
- PRELIMINARY.
- UNSUPPORTED.
- INVALIDATED.

### Stage 3 — Storyline reconstruction

Prepare:

`IKMS_STORYLINE_RECONSTRUCTION.md`

Include:

- Central research argument.
- Research problem.
- Research gap.
- Research objective.
- Scientific contributions.
- Proposed section structure.
- Narrative logic between sections.
- Which existing materials should be retained, rewritten, moved, or removed.

### Stage 4 — Manuscript architecture

Prepare:

`IKMS_FULLPAPER_OUTLINE.md`

For every subsection, specify:

- Its purpose.
- The question it answers.
- Required evidence.
- Relevant figure or table.
- Main conclusion.

Avoid drafting prose before this structure is coherent.

### Stage 5 — Complete rewriting

Prepare:

- `IKMS_FULLPAPER_REWRITTEN.md`
- `IKMS_FULLPAPER_REWRITTEN.docx`

Write the complete manuscript in Bahasa Indonesia.

The Markdown and Word versions must contain identical substantive content.

Apply the actual IKMS template.

Do not import OilWeek formatting rules unless the IKMS template explicitly requires them.

### Stage 6 — Final scientific and editorial audit

Prepare:

`IKMS_FULLPAPER_FINAL_REVIEW.md`

Verify:

- Abstract and conclusion reflect the actual results.
- Every number is traceable.
- Every reference is valid.
- Figures and tables use the correct values.
- No invalidated result remains.
- No unsupported causal statement remains.
- No historical dataset is misrepresented.
- No optimization result is described as physically verified when it is not.
- The manuscript follows IKMS formatting requirements.

### Stage 7 — Final handover

Provide:

1. Final Word document.
2. Final Markdown document.
3. Storyline reconstruction.
4. Claim-evidence register.
5. Discrepancy register.
6. Final reviewer report.
7. Complete list of removed, corrected, or qualified claims.
8. Remaining scientific limitations.

---

# 13. FINAL ACCEPTANCE CRITERIA

The manuscript is accepted only when the following are satisfied.

| Criterion | Acceptance requirement |
|---|---|
| Storyline | Clear progression from industrial problem to specific engineering contribution |
| Research gap | Specific, defensible, and supported by literature |
| Objective | Explicit and consistent with the actual research |
| Methodology | Reproducible and technically accurate |
| Dataset | Actual source period, sample count, and sampling basis are correct |
| Thermodynamics | No invalidated MITA or energy-balance claims |
| Machine learning | Independent validation and correct interpretation |
| Optimization | Candidate results only presented as validated when physical gates pass |
| Results | Directly answer the research objective |
| Discussion | Explains engineering meaning rather than repeating tables |
| References | All citations verified and relevant |
| Writing | Concise, natural, and free from generic AI-style statements |
| Formatting | Matches the official IKMS template |
| Traceability | Every important quantitative claim has a supporting source |

Do not force all criteria to pass.

An unresolved scientific limitation must remain visible.

---

# 14. FINAL EDITORIAL PRINCIPLE

Write as an engineer explaining a real industrial problem to other engineers, researchers, and energy-sector decision-makers.

The paper should not try to impress the reviewer by mentioning every algorithm, every equation, every equipment tag, or every numerical output.

It should make the reader understand five things:

1. What is happening at Train H?
2. Why is it an engineering problem?
3. Why are existing approaches insufficient?
4. What did this research do differently?
5. What has actually been demonstrated?

Use the smallest amount of text necessary to explain the complete scientific argument.

Preserve technical depth, but remove unnecessary complexity.

**Clarity is not achieved by deleting engineering detail. It is achieved by retaining only the detail that supports the research argument.**

Begin with the manuscript diagnosis and claim-evidence audit. Reconstruct the storyline before writing the full paper. Do not ask the user to repeat information already available in the repository or conversation.
</USER_REQUEST>
<ADDITIONAL_METADATA>
The current local time is: 2026-11-13T14:24:08+07:00.

The user's current state is as follows:
Other open documents:
- d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK\ikms_2026\rebuild_v3_3\scripts\p5_compressor_turbine.py (LANGUAGE_UNSPECIFIED)
- d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK\chat_gateway.py (LANGUAGE_UNSPECIFIED)
- d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK\MASTER_HANDOVER_REBUILD_v3_3.md (LANGUAGE_UNSPECIFIED)
- d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK\.env (LANGUAGE_UNSPECIFIED)
- d:\User\Documents\KULIAH\LOMBA\FINAL_FIX_OILWEEK\MR_OPTIMIZATION_REBUILD\src\thermodynamics\neqsim_engine.py (LANGUAGE_UNSPECIFIED)
</ADDITIONAL_METADATA>