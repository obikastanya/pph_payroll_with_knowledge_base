"""Overview: architecture with the status of every component, the demo walkthrough, and the blueprint document."""
import pandas as pd
import streamlit as st

import kg
import state
import widgets as ui

BUILT, MOCK, TODO = "#d9f2e3", "#fff3cd", "#f4f4f2"

ARCHITECTURE = f"""digraph A {{
rankdir=TB; bgcolor=transparent; nodesep=0.25; ranksep=0.35; newrank=true;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=12 color="#8a8984"];
edge [fontname="Helvetica" fontsize=8 color="#6b6a66"];
subgraph cluster_in {{ label="Sources"; fontname="Helvetica"; fontsize=10; color="#d6d5d0";
  reg [label="Regulations\\n(PDF: PP, PMK, PER)" fillcolor="{TODO}"];
  pol [label="Company policies\\n(PP / PKB)" fillcolor="{TODO}"];
}}
subgraph cluster_acq {{ label="Knowledge acquisition (K2, Section V)"; fontname="Helvetica"; fontsize=10; color="#d6d5d0";
  seg [label="1 Segment by article" fillcolor="{BUILT}"];
  rel [label="2 Relevance + quote" fillcolor="{BUILT}"];
  ctx [label="3 Context from graph" fillcolor="{BUILT}"];
  llm [label="4 LLM: m candidate Deltas" fillcolor="{MOCK}"];
  tab [label="Table extraction tool" fillcolor="{BUILT}"];
  gates [label="5 Gates G1-G5\\n+ repair round" fillcolor="{BUILT}"];
  sg [label="S^G generator" fillcolor="{BUILT}"];
  sel [label="6 Consensus / abstain" fillcolor="{BUILT}"];
  imp [label="7 Impact report (SPARQL)" fillcolor="{BUILT}"];
  rev [label="Reviewer" fillcolor="{MOCK}"];
  {{ rank=same; seg; rel; ctx; llm; gates; sel; imp; rev; }}
}}
subgraph cluster_kb {{ label="Knowledge base (K1, Section IV)"; fontname="Helvetica"; fontsize=10; color="#d6d5d0";
  repo [label="8 Version repository\\n(append-only Deltas)" fillcolor="{BUILT}"];
  kg [label="Knowledge graph\\nRDF + SHACL, 2 layers,\\nbitemporal" fillcolor="{BUILT}"];
}}
subgraph cluster_use {{ label="Use"; fontname="Helvetica"; fontsize=10; color="#d6d5d0";
  eng [label="Inference engine\\n(time selection, lex superior /\\nspecialis / posterior, trace)" fillcolor="{BUILT}"];
  calc [label="Payroll calculator\\npayslip, versions, batch" fillcolor="{BUILT}"];
  view [label="KB viewer\\ngraph, timeline, SPARQL" fillcolor="{BUILT}"];
}}
subgraph cluster_eval {{ label="Evaluation (K3, K4, Section VI)"; fontname="Helvetica"; fontsize=10; color="#d6d5d0";
  gold [label="Gold chain K*_n, Delta*_n" fillcolor="{BUILT}"];
  se [label="S^E generator" fillcolor="{MOCK}"];
  gt [label="References GT1-GT5" fillcolor="{MOCK}"];
  exps [label="E0-E5, baselines, ablations,\\nstatistics, logger" fillcolor="{MOCK}"];
}}
reg -> seg; pol -> seg; seg -> rel -> ctx -> llm -> gates -> sel -> imp -> rev; rev -> repo;
tab -> llm [style=dashed]; sg -> gates [style=dashed]; repo -> kg; kg -> ctx [style=dashed constraint=false]; kg -> eng -> calc; eng -> view;
gt -> gold [label=" validates"]; gold -> se [label=" expected values"]; se -> exps; exps -> rel [style=dotted constraint=false label=" runs"];
{{ rank=same; tab; sg; reg; pol; }}
{{ rank=same; gt; repo; }}
}}"""


def show():
    st.title("Adaptive KBS for PPh 21: system mockup")
    st.markdown("This app is the mini version of the system in the paper skeleton. It runs end to end on a small corpus "
                "(three real changes, one distractor, one counterfactual, one unseen change) with a mock LLM. "
                "Use it to see what will be built, what it looks like, and what each part needs.")
    st.graphviz_chart(ARCHITECTURE, width="stretch")
    st.caption(f"Green: works in the mini demo. Yellow: simulated (mock LLM, no reviewer study, partial generator). "
               f"Grey: not built yet (real documents and PDF handling).")

    r = state.repo()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Repository versions", len(r.versions))
    c2.metric("Rules in head version", len(kg.rule_records(r.head.graph)))
    c3.metric("Documents in inbox", len(st.session_state.inbox))
    c4.metric("Evaluation tuples S^E", len(state.study().cases))

    st.subheader("Demo walkthrough")
    st.markdown("""
1. **Payroll calculator → Payslip.** Employee B (TK/0, 9.5 M + 0.5 M overtime), August 2024 on the head version. TER is
   used, the trace goes to PMK 168/2023, and Company X's overtime policy is reported as a conflict.
2. **Payroll calculator → Across periods.** The same employee from 2023 to 2026: the switch from the annualised method
   to TER in January 2024 appears as a step.
3. **Knowledge base viewer.** Look at the graph in 2023-06 and in 2024-08: R16-PPH becomes *superseded*. The timeline
   shows valid time and knowledge time for every rule.
4. **Knowledge base management → Inbox.** PMK 10/2025 (DTP, retroactive) waits in the inbox. Run the pipeline: three
   candidates, the gates, consensus outvotes the candidate with the wrong date, and the impact report names PX-THP.
5. **Review.** Approve (optionally edit and see the correction effort). The update becomes version v4.
6. **Payroll calculator → Compare versions.** January 2025 with v3 and v4, and v4 as known on 31 January: the
   retroactive DTP appears only with today's knowledge.
7. **Manual Delta.** Apply the unseen change U1 (TER category D) and check the collaborator's worked examples (RQ1).
8. **Company policy editor.** Add a policy; one that contradicts a mandatory rule is stored and reported.
9. **Experiments.** E0-E4 in the shape of the paper's tables and figures, including baselines B3, B4 and ablations.
""")

    st.subheader("Screens and the paper")
    st.dataframe(pd.DataFrame([
        {"screen": "Payroll calculator", "shows": "results, trace to article, conflicts, versions, knowledge dates",
         "paper": "Section IV (definition of the result, engine), RQ1 diagnostics", "PANDUAN": "5"},
        {"screen": "Knowledge base viewer", "shows": "graph, rules, tables, bitemporal timeline, anomalies, SPARQL",
         "paper": "Section IV (ontology figure), RQ3 anomaly diagnostic, AB5", "PANDUAN": "3, 5"},
        {"screen": "KB management: inbox and pipeline", "shows": "relevance, candidates, gates, S^G, consensus, impact",
         "paper": "Section V (pipeline figure, gate table), RQ2", "PANDUAN": "4, 9"},
        {"screen": "KB management: review, manual Delta, policies", "shows": "correction effort, RA check, A4 report",
         "paper": "RQ1 (unseen changes), RQ2 (correction effort), RQ4", "PANDUAN": "7, 14"},
        {"screen": "Experiments", "shows": "E0-E4 tables and figures, mockups of E5 and the rest",
         "paper": "Sections VI and VII", "PANDUAN": "13-20"},
    ]), hide_index=True, width="stretch")


def blueprint():
    st.markdown((state.MINI / "BLUEPRINT.md").read_text(encoding="utf-8"))
