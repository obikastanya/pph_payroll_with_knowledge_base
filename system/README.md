# system: the full implementation

The full version of the system prototyped in [mini_demo/](../mini_demo/README.md) and specified in [paper/draft/skeleton.tex](../paper/draft/skeleton.tex). The legacy calculator (`engine/`, `kb/`, `ui/`, `web/`) stays untouched: it is the reference for the equivalence check when the knowledge base is migrated to the graph (PANDUAN stage 5).

Decisions this implementation follows are in the decision log at the end of [PANDUAN_PENELITIAN.md](../PANDUAN_PENELITIAN.md). Materials that people must check before they are used (gold Deltas, graded cases, adjudication, labels, unseen changes) go to [review/](../review/README.md).

## Setup

1. Python packages: `env\Scripts\python -m pip install -r requirements.txt` from the repository root.
2. API keys in the root `.env` (never committed): `CLAUDE_API_KEY` and `OPENAI_API_KEY`. They do not need to be exported; [pph21kbs/config.py](pph21kbs/config.py) reads `.env` directly.
3. GraphDB Free 11.5.1 in Docker (Docker Desktop must be running):
   - request the free license on the GraphDB page of graphwise.ai; the email contains a base64 code;
   - put the code in `.env` as `GRAPHDB_LICENSE` (one line);
   - `env\Scripts\python system\tools\graphdb_setup.py` decodes it to `graphdb/graphdb.license`, starts the container, and creates the `pph21` repository;
   - Workbench and SPARQL endpoint at http://localhost:7200.
4. Check everything: `env\Scripts\python system\tools\check_setup.py`. It only lists models and repositories, so it costs nothing.

## GraphDB repository

| Setting | Value | Why |
|---|---|---|
| SHACL validation | on | Gate G1 and the store refuse data that violates the shapes. Can only be set when the repository is created |
| Ruleset | `empty` (no inference) | Queries see exactly the stored triples; results do not depend on a reasoner |
| Context index | on | One named graph per knowledge-base version |

SHACL `sh:class` follows `rdfs:subClassOf` only for triples inside the repository, so the ontology graph must be loaded together with the data. Tested on 2026-10-27: with the ontology loaded, a valid rule is accepted and a rule without id, layer, dates, fact, expression, and source is rejected; without it, a valid rule whose article belongs to a `tax:Regulation` is rejected.

The free license allows one CPU core and limited query concurrency, which is enough for this study.

## Tools

| Tool | Purpose |
|---|---|
| [tools/check_setup.py](tools/check_setup.py) | Packages, API keys, model availability, GraphDB |
| [tools/graphdb_setup.py](tools/graphdb_setup.py) | License from `.env`, container, `pph21` repository with SHACL |
| [tools/seal.py](tools/seal.py) | SHA-256 manifest to seal materials (unseen changes, locked gold) and verify them later |

## Planned layout

Built stage by stage, following PANDUAN. Each module takes over a mini-demo module and grows to the full scope.

| Module | From the mini demo | Full scope | PANDUAN |
|---|---|---|---|
| `pph21kbs/config.py` | - | Keys, models, budget, GraphDB endpoint | 0 |
| `pph21kbs/store.py` | `repository.py` | GraphDB repository, one named graph per version, append-only Delta log in git | 5 |
| `pph21kbs/kg.py` | `kg.py` | Ontology with ELI, OWL-Time, PROV-O; SHACL; versioned rule records (add, change, remove) | 3, 5 |
| `pph21kbs/engine.py` | `reasoner.py` | Whole tax year, December recalculation, irregular income, gross-up, explicit lex specialis, rounding registry | 5 |
| `pph21kbs/migrate.py` | - | Legacy YAML KB to the graph, equivalence check against `engine/` | 5 |
| `pph21kbs/llm.py` | `mock_llm.py` | Claude and OpenAI clients, structured output, Batch API, caching, call log with cost | 9 |
| `pph21kbs/acquisition.py` | `acquisition.py` | PDF segmentation (pdfplumber), relevance, m = 5 candidates, G1-G5 with date grounding, consensus with abstain on ties | 9 |
| `pph21kbs/testspace.py` | `evaluation.evaluation_cases` | Constrained 2-way and 3-way combinations, inverse boundaries, operational sample | 8 |
| `pph21kbs/evaluation.py` | `evaluation.py`, `experiments.py` | E0-E5, baselines, ablations, statistics | 10, 13-18 |
| `app/` | `mini_demo/app/` | The same screens on the full system | - |
