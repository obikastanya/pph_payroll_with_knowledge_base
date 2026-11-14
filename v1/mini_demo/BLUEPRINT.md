# Blueprint of the system and the study

This document describes what the full system is, what each screen looks like, which data contracts connect the parts, which datasets the study needs, and how every part produces something the paper reports. It is written from the mini demo: everything described here can be seen running, either for real on the mini corpus or as a marked mockup.

- Paper skeleton: [paper/draft/skeleton.tex](../paper/draft/skeleton.tex)
- Research guide (stages 0 to 24): [PANDUAN_PENELITIAN.md](../PANDUAN_PENELITIAN.md)
- App: `env\Scripts\streamlit run mini_demo\app\main.py`
- Script version of the same experiments: `env\Scripts\python mini_demo\run_demo.py`

---

## 1. The system in one picture

```
 Sources                 Knowledge acquisition (K2)                                  Knowledge base (K1)          Use
 ─────────               ─────────────────────────────────────────────────────────   ───────────────────────      ─────────────────────
 Regulation PDF ─┐       1 segment   2 relevance   3 context    4 LLM drafts   5 gates     6 consensus   7 impact     8 version repository         inference engine
 Company policy ─┴──►    by article ─► + quote  ──► from graph ─► m Deltas ───► G1..G5 ──► or abstain ─► report ──►  (append-only Deltas) ──►     │
                                                        ▲            ▲            ▲  repair            reviewer      knowledge graph            ├─► payroll calculator
                                                        │       table-extraction  │                                 RDF + SHACL                └─► KB viewer
                                                        └──── graph ──────────────┴── S^G generator                 two layers, bitemporal

 Evaluation (K3, K4):  references GT1-GT5 ─► gold chain K*_n ─► expected values on S^E ─► scores of the pipeline's Deltas (E0-E5)
```

| Component | What it does | Mini demo | Full system | Skeleton | PANDUAN |
|---|---|---|---|---|---|
| Ontology and SHACL shapes | Classes Regulation, Article, Rule, Fact, Table, CompanyPolicy, Layer; G1 constraints | 8 classes, 3 shapes ([data/ontology.ttl](data/ontology.ttl), [data/shapes.ttl](data/shapes.ttl)) | Reuse ELI, OWL-Time, PROV-O; full G1 constraint list | IV | 3, 5 |
| Knowledge graph | Rules with layer, modality, valid time, knowledge time, condition, expression, source, quote | [kg.py](kg.py) | Migration of all of `kb/` (YAML) to the graph, with an equivalence check against the existing engine | IV | 5 |
| Version repository | Version n = K0 ⊕ Δ1 ⊕ ... ⊕ Δn; never edited in place | [repository.py](repository.py), in memory | Triple store with one named graph per version and PROV-O provenance; git tag per experiment | V | 5, 9 |
| Inference engine | Rule selection by (t, ω), repeal, lex superior / specialis / posterior, conflict report, trace | [reasoner.py](reasoner.py), monthly only | Whole tax year, December recalculation, gross-up, irregular income, rounding registry | IV | 5 |
| Expression language | The only functions a rule may call | 8 functions | Full set with types; also limits LLM output | IV | 3 |
| Anomaly checker | dangling, unused, overridden, conflict, superseded | `reasoner.anomalies` | Plus redundant and subsumed rules; counts per version for RQ3 | VI (diagnostic) | 5 |
| Acquisition pipeline | Steps 1 to 8 | [acquisition.py](acquisition.py) with the mock LLM | Real models, structured output against the Delta schema, PDF segmentation, date grounding | V | 9 |
| Prompts | Relevance, drafting, repair | [prompts.py](prompts.py), shown in the app, not used by the mock | Frozen after calibration on development data | V | 9, 11 |
| Gates G1 to G5 | Shapes, quote, known facts and conflicts, regression, non-vacuity | All five | Plus date grounding; G5 for change and repeal | V | 9 |
| S^G generator | Gate cases from the numbers and dates in the candidates | Built; no overlap with S^E | Also targets every condition φ of a changed element | V | 4, 9 |
| Impact analysis | Company policies affected by a Delta | Two SPARQL queries | Same queries over a real policy corpus; baselines B5 | V | 5, 17 |
| Gold chain | K*_n and Δ*_n | 4 events, written for the demo | Every event 2023 to 2026, second reader, locked by hash | VI | 7 |
| S^E generator | Evaluation tuples (case, ω) | 75 hand-picked boundaries | Constrained 2-way and 3-way, every layer boundary (inverse from taxable income), operational sample | VI | 8 |
| References | Independent checks of the gold KB | 5 hand calculations (GT3, GT5) | GT1 with holdout, GT2, GT3, GT4, GT5 | VI | 8 |
| Experiments | E0 to E5, baselines, ablations, statistics | [experiments.py](experiments.py), [evaluation.py](evaluation.py): E0 to E4, B3, B4, AB3, AB4 | Plus E5, B1, B2, B5, AB1, AB2, AB5, second model, R repetitions, Newcombe, McNemar, bootstrap | VI, VII | 10, 13 to 20 |
| Experiment logger | Every LLM call | Mock call log (tokens estimated, cost 0) | Prompt hash, model version, cutoff, parameters, tokens, cost, time, gate results | VI | 9 |
| App | Calculator, KB viewer, KB management, experiments | [app/](app/) | Same screens; the paper needs only screenshots of the viewer and the pipeline | - | - |

---

## 2. Screens

### 2.1 Payroll calculator

The calculator is the inference engine with a face. It never contains tax knowledge; it only chooses which knowledge base to use, for which period, and as known on which date.

```
┌ Employee ──────────┐  ┌ Payslip ─┬ Compare versions ─┬ Across periods ─┬ Batch payroll ─────────────────────┐
│ Name               │  │ Year [2024] Month [Aug]   Knowledge date ω ( ) today (•) as known on [2025-01-31] │
│ PTKP status [TK/0] │  │ Knowledge base [v4 · E2, PMK 10/2025 ...]                                         │
│ Basic salary       │  │ ┌ Payslip · Aug 2024 ──────────┐   ┌ Why these numbers ───────────────────────┐   │
│ Fixed allowance    │  │ │ Basic salary     9,500,000   │   │ salary ─R-GROSS─► gross_income 10,000,000 │   │
│ Overtime           │  │ │ Overtime           500,000   │   │ ptkp_status ─R24-CAT─► ter_category TER-A │   │
│ [x] DTP sector     │  │ │ Gross income    10,000,000   │   │ ter_category, gross ─R24-PPH─► pph21      │   │
└────────────────────┘  │ │ PPh 21 due         200,000   │   └───────────────────────────────────────────┘   │
                        │ │ PPh 21 withheld    200,000   │   ⚠ Company policy PX-OVERTIME overridden by a     │
                        │ │ Take-home pay    9,800,000   │     mandatory regulation (reported, A4)           │
                        │ └──────────────────────────────┘   ✓ Reference A-2024 (GT3) matches               │
                        │ Calculation trace: fact │ value │ rule │ layer │ source article │ quote │ expression │
                        └────────────────────────────────────────────────────────────────────────────────────┘
```

| Tab | Shows | Why it matters for the paper |
|---|---|---|
| Payslip | Payslip, derivation graph, trace table to the article and quote, reported conflicts, matching references | Definition of the result hasil(K, x, t, ω); trace completeness (RQ1 diagnostic) |
| Compare versions | One case under several KBs (repository versions, pending candidate, gold, system chain) and knowledge dates; differing rows highlighted | Conditions A2 and A3 checked by eye; the experiments do the same over S^E |
| Across periods | One employee from 2023 to 2026 per version, "today" and "as known then"; a table of periods where later knowledge changes the result | Regime switches; retroactive regulation (A3_ω); the open definition of retroactive semantics |
| Batch payroll | All employees of Company X for one month, totals, comparison with another version, CSV upload and download | What an HR user actually runs; operational sample later used for drift D_N |

Mockup parts: the full payroll year (December recalculation, THR and bonus, gross-up, BPJS, proration, bukti potong). The legacy calculator in `engine/` and `ui/` already does these and is the reference for the migration (PANDUAN stage 5).

### 2.2 Knowledge base viewer

```
Knowledge base [v4 ▾]   Year [2024] Month [Aug]   Knowledge date ω ( ) today (•) as known on [...]
┌ Graph ┬ Rules ┬ Tables ┬ Timeline ┬ Quality checks ┬ SPARQL ┬ Export ┐
│ View (•) Data flow ( ) Provenance ( ) Full    [ ] only rules in force   Layers [regulation][company]   │
│                                                                                                        │
│  (gross_income) ──► [R24-PPH  mandatory 2024-01] ──► ((pph21)) ──► [R-WITHHELD default] ──► ...       │
│  [R16-PPH  (superseded)] ◄─supersedes── [R24-PPH]        [PX-OVERTIME] ┄┄conflict┄┄ [R-OVERTIME]      │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

| Tab | Shows |
|---|---|
| Graph | Rules (blue regulation, orange company), facts, tables, documents and articles; status at (t, ω): in force, not in force, not yet known, superseded; supersedes and conflict edges |
| Rules | Table of rules with status; detail card with expression, validity, recording date, source, quote, readers, rivals, and the version that introduced it |
| Tables | Every table version (PTKP, Article 17, TER categories and rates) with a step chart of rates |
| Timeline | Bitemporal chart: bar = valid time [t_s, t_e], diamond = knowledge time t_c, lines at t and ω. A diamond right of a bar's start is a retroactive rule |
| Quality checks | SHACL result (G1), anomalies in the chosen period, conflicts reported |
| SPARQL | Preset queries (rules, impact path, conflicts, repeal chain, documents) and free queries |
| Export | Turtle of the selected version, ontology, shapes. External viewers: Protégé for the ontology; GraphDB or Apache Jena Fuseki for graph browsing and a SPARQL endpoint |

The viewer is where feedback no. 1 ("what is the final representation?") is answered visually, and the source of the ontology figure in Section IV.

### 2.3 Knowledge base management

```
┌ Inbox and acquisition ┬ Review (1) ┬ Manual Delta ┬ Company policy editor ┬ Version history ┐
│ + Add a document: (•) upload .txt/.pdf ( ) demo corpus   title  layer  issue date            │
│ Inbox: E2 · PMK 10/2025 · regulation · 2025-02-04                [▶ Run acquisition pipeline] │
│ 1 Segment by article        Preamble │ Pasal 2 │ Pasal 4 ayat (2) │ Pasal 5 ayat (1)            │
│ 2 Relevance + quote         relevant: true · quote found: true  > "ditanggung pemerintah"      │
│ 3 Context from graph        R-GROSS gross_income, R24-PPH pph21, ...      [prompt preview]     │
│ 4 Candidates                Candidate 1 │ Candidate 2 │ Candidate 3   (table + JSON)           │
│ 5 Gates                            C1     C2     C3                                            │
│     G1 shapes                     pass   pass   pass                                           │
│     G2 quote in document          pass   pass   pass                                           │
│     G3 known facts, conflicts     pass   pass   pass                                           │
│     G4 no change before t_eff/ω   pass   pass   pass                                           │
│     G5 every element has effect   pass   pass   pass                                           │
│ 6 S^G                       60 tuples · overlap with S^E: 0                                    │
│ 7 Consensus                 groups [[1], [2, 3]] → candidate 2                                 │
│ 8 Impact report             policies affected: PX-THP · 24/60 gate cases change   [Send to review] │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

| Tab | Shows | Paper |
|---|---|---|
| Inbox and acquisition | Upload or pick a document; the eight pipeline steps with prompts, candidates, gate matrix, S^G, behaviour groups, impact report, call log. Abstain is shown when no candidate passes | Section V pipeline figure and gate table; RQ2 |
| Review | Selected Delta in an editor, reviewer name, recording date, schema check, edit operations and saving vs writing from scratch; approve or reject | Correction effort (RQ2 diagnostic); reviewer role |
| Manual Delta | Upload or paste a Delta; schema, G1, G3, new conflicts, and the collaborator's worked examples; apply | RQ1: unseen changes, RA |
| Company policy editor | A company rule in the same representation; conflicts with mandatory rules reported; before and after for an example employee | Two-layer representation, A4, RQ4 inputs |
| Version history | Every version with author, recording date, size, fingerprint; diff between two versions; Delta download | Append-only history that makes A3_ω reproducible |

Mockup parts: PDF text and table extraction (upload .txt for now); a real LLM (the mock has answers only for the demo corpus; for any other document the screen shows the prompts that would be sent); reviewer study.

### 2.4 Experiments

| Tab | Computed in the demo | Paper artefact |
|---|---|---|
| Summary | Hypothesis table with mini results and invariants | Table "Keterlacakan RQ, hipotesis, dan metrik utama" |
| E0 instruments | References vs gold, Δ-focused mutation score with surviving mutants, coverage table | Section VII instrument validation; table "Ruang uji dan cakupannya" |
| E1 · RQ1 | Real changes as data only, unseen change U1 with worked examples, RA with exact lower bound, conflict-resolution accuracy | RQ1 results |
| E2 · RQ2 | SER, CAR, ABS with exact bounds for Proposed, B3, B4, AB3 (without G5, without G4), AB4; selective-risk figure; per-document outcomes; pass@k; gate confusion matrix; memorisation | Figure "Keamanan dan kegunaan akuisisi"; RQ2 tables |
| E3 · RQ3 | Replay in both abstain variants; inherited, new, induced (mechanical) errors per event; OAR; drift; A1 hash; A3_ω | Figure "Hasil regulation replay"; RQ3 |
| E4 · RQ4 | Policy-event pairs with execution labels and the SPARQL detector; recall, precision, F2, flag-all baseline | RQ4 table |
| Not computed yet | E5/B2, B1, AB1, AB2, AB5, second model, repetitions, prospective events, statistics, cost calculator | Lists what fills each remaining cell |
| LLM log | Every mock call | Reproducibility and cost subsections |

Mini results (they are not findings about LLMs, only about the mock answers; they show that each instrument works):

| | Proposed | B3 | B4 | AB3 no G5 | AB3 no G4 | AB4 first passing |
|---|---|---|---|---|---|---|
| SER (3 real documents) | 1/3 | 3/3 | 1/3 | 1/3 | 1/3 | 2/3 |
| CAR | 2/3 | 0/3 | 2/3 | 2/3 | 2/3 | 1/3 |
| Counterfactual E2CF | abstain | abstain | wrong | abstain | wrong | abstain |

---

## 3. Data contracts

All parts exchange the same few records. They are fixed in PANDUAN stage 4 before anything else is built.

| Record | Fields | Where |
|---|---|---|
| Rule | id, layer (regulation, company), modality (mandatory, default, optional), valid_from, valid_until, recorded_on, produces, condition, expression, supersedes, source {document, article, quote} | [data/schema/delta.schema.json](data/schema/delta.schema.json) |
| Table version | name, valid_from, recorded_on, source, rows [{key or lower/upper, value}] or extract {file, filter, key or lower/upper, value} | same schema |
| Delta | add [rules], tables [table versions]; change and remove reserved | same schema; gold in [data/gold/](data/gold/), candidates in [data/mock_llm/](data/mock_llm/) |
| Change event | id, document, title, layer, issued, effective, change_type, split (development, test, prospective, counterfactual), relevant | [data/corpus/events.json](data/corpus/events.json) |
| Case | ptkp_status, salary, allowance, overtime, dtp_sector, year, month (full system: the whole tax year) | [evaluation.py](evaluation.py) |
| Evaluation tuple | (case, knowledge date ω) with expected output facts gross_income, pph21, pph21_dtp, pph21_withheld, take_home_pay, and the reported conflicts | `evaluation_cases`, `score_results` |
| Reference | id, source (GT1 to GT5), case, knowledge_date, expected, working | [data/reference/references.json](data/reference/references.json) |
| Unseen change | change text, worked examples {case, expected, working}, researcher's Delta | [data/hidden/](data/hidden/) (private repository in the study) |
| Version | number, label, document, delta, recorded_on, author, note, fingerprint | [repository.py](repository.py) |
| Pipeline result | status (applied, empty, abstain), relevance, candidates, gate verdicts per candidate, behaviour groups, selected, impacted policies, S^G | [acquisition.py](acquisition.py) |
| LLM call | document, step, model, parameters, tokens in/out, cost, seconds, output | [mock_llm.py](mock_llm.py) |
| Impact pair | policy, event, label (from execution), flagged (from SPARQL) | [experiments.py](experiments.py) |

---

## 4. Data the study needs

| Dataset | Content | Target size | Source | Who | In the demo |
|---|---|---|---|---|---|
| Real change events | Every 2023 to 2026 event affecting PPh 21 of permanent employees, official PDFs, issue and effective dates | All (expected 8 to 15) | JDIH Kemenkeu, DJP | researcher | 3 summaries (E1, K1, E2) |
| Development events | Fictional regulations and pre-2023 changes (PTKP 2016, Article 17 layers 2022) | 5 to 10 | official archive, authored | researcher | none |
| Distractors | PPh 21 documents that do not change permanent-employee withholding, including hard ones | 5 or more | PMK and PER on administration, non-permanent employees | researcher | 1 (P1) |
| Counterfactuals | Values, dates, thresholds changed consistently; gold derived by program | 1 or more per test document | generated | script | 1 (E2CF) |
| Unseen changes | Structural changes from the change taxonomy, with 5 to 10 worked examples each | at least 15 | collaborator | collaborator | 1 (U1) |
| Gold Deltas and K*_n | One per event, checked by a second reader, locked by hash | one per event | researcher + second reader | both | 4 |
| Company policies | Public collective agreements or company regulations, plus authored conflicts | 5 to 10 documents | public PKB/PP, collaborator | both | 1 fictional amendment |
| GT1 official examples | Worked examples in PMK 168/2023 and PER-16, including a holdout | all available | regulations | researcher | none |
| GT2 DJP calculator | Results for sampled cells | per regime | DJP site, if available | researcher | none |
| GT3 manual calculations | Independent hand calculations | about 50 graded cases | collaborator or tax practitioner | collaborator | 3 |
| GT4 third-party calculators | Open-source and public calculators, versions and dates recorded | 3 or more tools | GitHub, public sites | researcher | none |
| GT5 policy examples | Worked examples from policy texts, written before the gold Delta | per policy | collaborator | collaborator | 1 |
| Operational distribution | Wage distribution and PTKP shares | 1 table | BPS (Sakernas), Kemnaker UMP (already in `dataset/04_data_publik/`) | researcher | none |
| Rate tables | PTKP, Article 17, TER A/B/C | complete | `dataset/01_regulasi/tables/` | done | used |
| B1 commit histories | Commits of open-source PPh 21 calculators around January 2024 | 3 or more repositories | GitHub | researcher | none |

Public vs private: the repository is public, so unseen changes, authored conflicts, GT5 examples, the holdout, and the expected values of S^E live in a private repository; only their hashes are committed (pre-registration).

---

## 5. From experiment to paper

| Experiment | Screen | Fills | Demo status |
|---|---|---|---|
| E0 instrument validation | Experiments → E0 | Section VII.A; coverage table; adjudication log | References and mutation score computed; E0 fails on purpose (S^E too small) |
| E1 RQ1 | Experiments → E1; Manual Delta | RA table; conflict-resolution accuracy; engine history | 1 unseen change; 4 conflict pairs |
| E2 RQ2 | Experiments → E2; Inbox | SER/CAR/ABS per condition, layer, change type; RQ2 figure; diagnostics | 6 conditions on mock answers |
| E3 RQ3 | Experiments → E3 | Replay figure; OAR; induced errors; drift | Both abstain variants, mechanical induced errors |
| E4 RQ4 | Experiments → E4 | Recall, F2 vs B5 | SPARQL detector and flag-all only |
| E5 motivation | Experiments → Not computed yet | One paragraph in the introduction or results | mockup |
| Prospective | Inbox | Strongest evidence against contamination | the inbox is the operational path for it |

---

## 6. Build order (from the mini demo to the full system)

1. **Fix definitions** (PANDUAN stages 2 to 4): scope, change taxonomy, Definitions 1 to 8, retroactive semantics, the data contracts above, the decisions in section 8. Show them to the supervisor.
2. **Representation and engine** (stage 5): ontology with ELI/OWL-Time/PROV-O, migration of `kb/` to the graph, engine over the whole tax year, equivalence check against the legacy engine, engine unit tests, anomaly checker, conflict test suite.
3. **Corpus and gold** (stages 6 and 7): real events with PDFs, distractors, counterfactual generator, policies; gold Deltas with a second reader.
4. **Test space and references** (stage 8): S^E generator with effective-month cases and every layer boundary, GT1 to GT5, mutation operators.
5. **Pipeline** (stage 9): real LLM client with structured output, PDF segmentation, table tool, date grounding, repair prompts, logger.
6. **Baselines and analysis scripts** (stage 10), **calibration on development data and freezing** (stage 11), **pre-registration** (stage 12).
7. **Experiments** E0 to E5 (stages 13 to 18), prospective events (stage 19), analysis (stage 20), writing (stage 21).

The app grows with the system, but the paper does not depend on it: everything it shows comes from `experiments.py` and the outputs folder.

---

## 7. What building the mockup taught us

Each item is a requirement or a decision for the full system.

1. **Wrong effective dates pass every gate.** All K1 candidates use 1 January instead of 1 July and pass G1 to G5, so the error is silent (SER 1/3). The full system needs a date-grounding check: every date in a Delta must appear in the quoted text.
2. **A retroactive regulation tempts the LLM to backdate knowledge.** The faithful E2CF candidate records the rule on the effective date (1 January) instead of the issue date (4 February). January results computed before the regulation existed would change. Only G4 catches it, and only because S^G contains cases with ω the day before issue. Without G4 (AB3) the counterfactual becomes a silent error.
3. **A company policy overridden by a mandatory rule has no numeric effect.** A plain non-vacuity gate would reject it, yet A4 requires it to be stored and reported. G5 therefore accepts an element whose only effect is a reported conflict.
4. **The test space must reach every changed element.** The Δ-focused mutation score is 0/5 for E1 and 0/1 for K1 because S^E has no case in the effective month and covers few table layers. E0 catches this, as it should.
5. **The quote gate stops memorised values.** On the counterfactual, two of three candidates use the remembered Rp10,000,000 and G2 rejects them because their quote is not in the document.
6. **Consensus needs equivalent candidates to agree, and a tie rule.** For E2, candidates 2 and 3 are written differently and behave the same, so they outvote candidate 1. With one passing candidate per behaviour, the current code takes the first group; the study must pre-register a tie rule (proposal: abstain on a tie).
7. **Candidate order matters for first-passing selection.** AB4 and B3 depend on which candidate comes first. The study must randomise and record the order.
8. **Repeal leaves helper rules behind.** After TER, `R16-TAXABLE` still computes an annual taxable income that nothing reads. Results are correct, so S^E cannot see it; the anomaly checker reports it as unused. Decide whether a gold Delta must repeal helper rules, and count such rules in the RQ3 anomaly diagnostic.
9. **Knowledge time has two meanings.** The skeleton sets t_c to the issue date (legal knowledge), which makes A3_ω hold by construction. In operation, the update is approved days later. The review screen lets the reviewer choose; the paper must state that ω means legal knowledge.
10. **Changing the validity of an existing rule needs versioned rule records.** The demo expresses repeal only through `supersedes`. Editing `valid_until` of an existing rule would lose what was known earlier. `change` and `remove` are reserved in the schema for this.
11. **Small numbers give weak bounds.** With 3 relevant documents, SER 1/3 has an exact upper bound of 0.86; one unseen change gives a lower bound of 0.05 for RA. This is the sample-size issue the skeleton plans for.

---

## 8. Open decisions this mockup makes concrete

| Decision | Options | Where it shows |
|---|---|---|
| Tie rule in consensus | first group, abstain, smallest Delta | Inbox step 7 |
| Date grounding as a gate (G2 extension or G6) | yes, no | K1 silent error |
| Meaning of ω | legal knowledge (issue date), system knowledge (approval date) | Review: recorded on |
| Retroactive semantics | refund, December recalculation, recompute the month | Calculator → Across periods |
| Repeal of helper rules in gold Deltas | required, optional | Viewer → Quality checks |
| m and the repair budget | m = 3 in the demo, 5 proposed | Inbox step 4; cost calculator |
| Table extraction tool for the LLM | allowed (proposal), not allowed | Δ uses `extract` |
| Triple store | rdflib in memory, GraphDB, Fuseki | Viewer → Export |
| PDF handling | text layer + manual check, OCR, layout model | Inbox upload |

---

## 9. People, tools, budget

| Need | Status |
|---|---|
| `rdflib`, `pyshacl`, `streamlit`, `plotly`, `pandas`, `jsonschema` | In the root [requirements.txt](../requirements.txt), installed in `env` |
| Statistics (`scipy` or `statsmodels`) | Installable in `env` |
| Combinatorial test generation | `allpairspy` installable in `env`; PICT or ACTS would need installing outside `env` |
| Triple store (optional) | GraphDB Free or Apache Jena Fuseki, outside `env` |
| LLM API keys and budget | Needed for the real runs; estimate in Experiments → Not computed yet |
| Pre-registration account (OSF or AsPredicted) | Needed before the experiments |
| Collaborators (at most two) | Unseen changes and worked examples, authored conflicts, GT5, second reader, blind second adjudicator, second labeller for RQ4 |
| Tax practitioner | Optional; checks the TER gold Delta and about 50 graded cases |
