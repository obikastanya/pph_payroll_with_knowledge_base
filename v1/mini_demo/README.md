# mini_demo: end-to-end prototype and mockup of the planned system

A deliberately tiny version of the system described in [paper/draft/skeleton.tex](../paper/draft/skeleton.tex). It runs the whole pipeline once, from the initial knowledge base to the four research questions, and shows every screen the full system will have. Parts that only show what the full system will do are marked **Mockup** on screen.

**UI mockup v2 for finance admins** (calculator, knowledge base viewer, knowledge base management with an assistant, research results in plain language) is in [mockup/](mockup/README.md): `env\Scripts\streamlit run mini_demo\mockup\main.py --server.port 8503`.

**Start with [BLUEPRINT.md](BLUEPRINT.md)**: what is being built, what each screen looks like, the data contracts, the datasets the study needs, how each experiment fills the paper, the build order, and what building this mockup taught us.

What "tiny" means here:
- one employee per case, one regular month (no December recalculation, no gross-up);
- nine rules in the initial knowledge base, three real change events, one distractor, one counterfactual, one unseen change;
- a mock LLM with prepared answers, so nothing needs an API key or costs money;
- 75 evaluation tuples instead of the full combinatorial test space.

## Install

Requirements: Python 3.12 and the virtual environment `env` in the repository root. No API key, database, Java, or Graphviz installation is needed; diagrams are drawn in the browser.

The demo's dependencies are part of the root [requirements.txt](../requirements.txt):

| Package | Used for |
|---|---|
| `rdflib` 7.6.0 | Knowledge graph (RDF, SPARQL) |
| `pyshacl` 0.40.1 | Gate G1, SHACL validation (also installs `owlrl`) |
| `jsonschema` 4.26.0 | Delta schema check on the management screens |
| `streamlit` 1.64.0, `plotly` 7.1.0, `pandas` 3.0.6 | The app |

The demo also imports `engine/ekspresi.py`, `engine/angka.py`, and `engine/pembulatan.py` from the repository, so run it from a full checkout.

From the repository root, once:

```
python -m venv env                                    # skip if env already exists
env\Scripts\python -m pip install -r requirements.txt
```

`requirements-lock.txt` pins every package, including transitive ones, for an identical environment:
`env\Scripts\python -m pip install -r requirements-lock.txt`.

## Run

From the repository root:

```
env\Scripts\streamlit run mini_demo\app\main.py      # the app
env\Scripts\python mini_demo\run_demo.py             # the same experiments as a printed walkthrough
```

The app opens at http://localhost:8501 (pick another port with `--server.port 8765`). The pages are also reachable directly: `/calculator`, `/kb` (knowledge base viewer), `/manage`, `/experiments`, `/blueprint`.

The first visit to the Experiments page computes E0 to E4 for six conditions (about 20 seconds); later visits are cached. The first visit to the calculator takes a few seconds because it builds the system's replay chain.

Optional, outside `env`: to browse the exported Turtle files in another tool, use Protégé (ontology) or GraphDB Free / Apache Jena Fuseki (graph browser and SPARQL endpoint). The app's own viewer does not need them.

## The app

| Page | What you can do |
|---|---|
| Overview | Architecture with the status of every component, a demo walkthrough, screens mapped to the paper |
| Payroll calculator | Payslip with a derivation graph and a trace to the article; compare knowledge-base versions and knowledge dates; one employee across 2023 to 2026; batch payroll with CSV upload |
| Knowledge base viewer | Graph (data flow, provenance), rules with status in a period, table versions, bitemporal timeline, anomalies, SPARQL console, Turtle export |
| Knowledge base management | Inbox with upload; the acquisition pipeline step by step (relevance, candidates, gates G1-G5, S^G, consensus, impact report); review with correction effort; manual Delta with worked-example check (RQ1); company policy editor; version history and diff |
| Experiments | E0 to E4 in the shape of the paper's tables and figures, baselines B3 and B4 and ablations AB3 and AB4, what is not computed yet, the LLM call log |
| Blueprint | This folder's BLUEPRINT.md |

The app starts with versions v0 (K0) to v3 (E1, K1, P1 applied) and PMK 10/2025 waiting in the inbox. "Reset demo state" in the sidebar restores that.

## The script

| Step | What happens | PANDUAN stage | Skeleton section |
|---|---|---|---|
| 1 | Builds K0 as an RDF graph, validates it with SHACL, computes one case with a trace to the source article | 3, 5 | IV |
| 2 | Loads events, distractor, counterfactual; builds the gold chain K*_0 ... K*_N | 6, 7 | VI (corpus) |
| 3 | Builds the evaluation tuples S^E | 8 | VI (test space) |
| 4 | E0: references (GT3, GT5) and the Δ-focused mutation score | 13 | VI (chain of trust) |
| 5 | E1 (RQ1): gold Deltas as data only; the unseen change U1 against the collaborator's worked examples | 14 | VI (RQ1) |
| 6 | The acquisition pipeline on E2, step by step | 9 | V |
| 7 | E2 (RQ2): SER, CAR, ABS with exact bounds for every condition; memorisation on the counterfactual | 15 | VI (RQ2) |
| 8 | E3 (RQ3): chained replay; inherited, new, induced errors; OAR; drift; invariants A1 and A3_ω | 16 | VI (RQ3) |
| 9 | E4 (RQ4): impact labels from execution against the SPARQL detector; recall, F2, flag-all baseline | 17 | VI (RQ4) |

It writes `outputs/` (knowledge graphs as Turtle, the LLM call log).

## Files

| File | Role |
|---|---|
| `kg.py` | Knowledge graph: applies a Delta to RDF, table-extraction tool, SHACL check (G1), SPARQL for impact and conflicts, rule and table records |
| `reasoner.py` | Inference engine reading rules from the graph: rule selection by period and knowledge date, conflict resolution, trace, anomaly check. Reuses `engine/ekspresi.py`, `engine/angka.py`, `engine/pembulatan.py` through an English adapter |
| `repository.py` | Version repository: append-only log of Deltas |
| `acquisition.py` | Acquisition pipeline: segmentation, relevance, candidates, gates G1-G5, repair round, S^G, consensus or abstain, impact; conditions for B3, B4, AB3, AB4 |
| `prompts.py` | Prompt templates for a real model |
| `mock_llm.py` | Mock LLM reading prepared answers from `data/mock_llm/`, with a call log |
| `evaluation.py` | Corpus and counterfactual derivation, gold chain, S^E, scoring, mutation score, Clopper-Pearson bounds, correction effort, replay, impact labels |
| `experiments.py` | E0 to E4 as data, shared by the script and the app |
| `run_demo.py` | The printed walkthrough |
| `app/` | The Streamlit app (`main.py`, one module per page, `state.py`, `widgets.py`) |
| `data/ontology.ttl`, `data/shapes.ttl` | Ontology and SHACL shapes |
| `data/schema/delta.schema.json` | The Delta contract shared by pipeline, gold, baselines, and scoring |
| `data/initial_kb.json` | K0 in the same format as a Delta |
| `data/corpus/` | Event table and document texts (demo summaries, not official quotations) |
| `data/gold/` | Gold Deltas |
| `data/mock_llm/` | Prepared LLM answers, chosen so that every gate has something to catch |
| `data/hidden/` | Unseen change U1, its worked examples, the researcher's Delta (private repository in the study) |
| `data/reference/` | References for E0 (GT3, GT5) |
| `data/roster.json` | Fictional employees for the batch payroll |

Rate tables (TER, Article 17, PTKP) are not retyped; the table-extraction tool reads them from `dataset/01_regulasi/tables/`.

## Simplifications

| In the demo | In the full system |
|---|---|
| One regular month | Full year with December recalculation, irregular income, gross-up, employer-borne method |
| DTP eligibility checked on monthly gross income | Fixed regular income in January or the first month of work, per PMK 10/2025 |
| Retroactive DTP recomputes January directly | Semantics follow the legal mechanism (refund or December recalculation), defined in stage 4 |
| Rounding always down | Rounding registry per article |
| Mock LLM | Real models, structured output against the Delta schema, full logging |
| Reviewer screen without a reviewer study | Reviewer effort measured by edit operations |
| One run per document | m candidates before repair for pass@k, R repetitions of the replay, a second isolated run for the noise floor |
| 75 evaluation tuples | Constrained 2-way and 3-way combinations, every layer boundary, about 3,000 operational cases |
| Repository in memory | Triple store with a named graph per version and PROV-O provenance |
