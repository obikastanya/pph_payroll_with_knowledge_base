"""Experiment dashboard: E0-E4 computed on the mini corpus with the mock LLM, in the shape of the paper's tables and
figures, plus mockups of what is not computed yet (E5, B1, B2, AB1, AB2, AB5, second model, repetitions, cost)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import evaluation as ev
import experiments as ex
import state
import widgets as ui
from reasoner import compute


def _pct(k, n):
    return f"{k}/{n}" if n else "-"


def tab_summary():
    st.markdown("Traceability table of the skeleton (RQ → hypothesis → primary metric), filled with the mini results. "
                "Thresholds θ are fixed at pre-registration; here they are open.")
    r1, r2, r3, r4 = state.e1(), state.e2(), state.e3(), state.e4()
    k, n, lower = r1["ra"]
    rows = [
        {"RQ": "-", "hypothesis": "Invariants A1 and A3_ω hold", "primary metric": "violations",
         "mini result": f"A1 engine hash {ex.engine_hash()}; A3_ω violations "
                        f"{sum(not row['knowledge_isolation'][0] for row in r3['rows'])}", "experiment": "all"},
        {"RQ": "RQ1", "hypothesis": "H1: RA on unseen changes ≥ θ1", "primary metric": "RA, exact CI",
         "mini result": f"RA {k}/{n}, 95% lower bound {lower:.2f}", "experiment": "E1"},
        {"RQ": "RQ2", "hypothesis": "H2a: upper bound of SER ≤ θ2; H2b: CAR > B3, B4 and SER non-inferior",
         "primary metric": "SER, CAR per layer", "mini result": f"SER {_pct(r2['ser'], r2['n'])} (upper {r2['ser_upper']:.2f}), "
                                                                 f"CAR {_pct(r2['car'], r2['n'])}", "experiment": "E2"},
        {"RQ": "RQ3", "hypothesis": "H3a: OAR ≥ θ3; H3b: induced errors within the noise floor", "primary metric": "OAR, induced I",
         "mini result": f"OAR {_pct(r3['oar'], r3['n'])}, induced {sum(len(x['induced']) for x in r3['rows'])}, "
                        f"drift {r3['drift']}/{r3['n_cases']}", "experiment": "E3"},
        {"RQ": "RQ4", "hypothesis": "H4a: recall ≥ θ4; H4b: F2 > every B5 baseline", "primary metric": "recall, F2",
         "mini result": f"recall {r4['recall']:.2f} (lower {r4['recall_lower']:.2f}), F2 {r4['f2']:.2f} vs flag-all "
                        f"{r4['flag_all_f2']:.2f}", "experiment": "E4"},
    ]
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    if not state.e0()["passed"]:
        st.warning("E0 did not pass (see the E0 tab). In the study, E2-E4 run only after E0 passes; the mockup shows them "
                   "anyway.", icon=":material/warning:")
    ui.where("Table 'Keterlacakan RQ, hipotesis, dan metrik utama' (skeleton Section VI).")


def tab_e0():
    r = state.e0()
    st.markdown("**References against the gold knowledge base** (GT3 manual calculation, GT5 company-policy example)")
    st.dataframe(pd.DataFrame([{"id": x["id"], "source": x["source"], "expected": str(x["expected"]), "gold KB": str(x["got"]),
                                "match": x["match"], "working": x["working"]} for x in r["references"]]),
                 hide_index=True, width="stretch")
    st.markdown("**Δ-focused mutation score of S^E** (mutants of each gold Delta that S^E detects)")
    st.dataframe(pd.DataFrame([{"event": doc, "killed": k, "mutants": n, "score": f"{k}/{n}", "survivors": "; ".join(sv)}
                               for doc, (k, n, sv) in r["mutation"].items()]), hide_index=True, width="stretch")
    st.markdown(f"E0 pass criteria met: **{r['passed']}**")
    st.caption("Surviving mutants mean S^E has no case that reaches the changed element, for example no case in the effective "
               "month. The full S^E generator adds cases at every effective month and at every layer boundary.")
    st.markdown("**Coverage of the test space** (skeleton table 'Ruang uji dan cakupannya')")
    s = state.study()
    st.dataframe(pd.DataFrame([
        {"criterion": "Article 17 layer boundaries per regime", "cells": "4 boundaries × 3 points", "tested": "1 boundary (60,000,000)", "reference": "GT3"},
        {"criterion": "TER layer boundaries per category", "cells": "A, B, C: all boundaries × 3", "tested": "category A, 3 boundaries", "reference": "-"},
        {"criterion": "Constrained 2-way combinations", "cells": "to compute", "tested": "-", "reference": "-"},
        {"criterion": "Constrained 3-way combinations", "cells": "to compute", "tested": "-", "reference": "-"},
        {"criterion": "Operational random sample", "cells": "≈ 3,000 for < 0.1% at α = 0.05", "tested": "-", "reference": "-"},
        {"criterion": "Total S^E in the mini demo", "cells": "", "tested": f"{len(s.cases)} tuples", "reference": ""},
    ]), hide_index=True, width="stretch")
    ui.mockup("GT1 (official examples with a holdout), GT2 (DJP calculator), GT4 (third-party calculators), adjudication of "
              "every discrepancy, Krippendorff's α of the second reader of the gold Deltas.")


def tab_e1():
    r = state.e1()
    st.markdown("**Real changes and policies:** every gold Delta applied as data only, engine unchanged")
    st.dataframe(pd.DataFrame(r["real"], columns=["event", "layer", "SHACL conforms"]), hide_index=True)
    st.markdown("**Unseen change U1** (written by a collaborator, revealed after the representation was frozen)")
    st.dataframe(pd.DataFrame([{"case": f"{e['case']['ptkp_status']} {e['case']['salary']:,} {e['case']['year']}-{e['case']['month']:02d}",
                                "expected": str(e["expected"]), "engine": str(got), "match": got == e["expected"],
                                "working": e["working"]} for e, got in r["unseen"]]), hide_index=True, width="stretch")
    k, n, lower = r["ra"]
    c1, c2 = st.columns(2)
    c1.metric("RA on unseen changes", f"{k}/{n}")
    c2.metric("Exact 95% lower bound", f"{lower:.2f}", help="With 15 unseen changes all expressed, the bound would be 0.82.")
    st.markdown("**Conflict resolution accuracy** (pairs with a known legal winner)")
    g = state.study().kb_gold
    base = {"ptkp_status": "TK/0", "salary": 9_500_000, "allowance": 0, "overtime": 500_000, "dtp_sector": True}
    tests = [("lex superior", "R-OVERTIME vs PX-OVERTIME", dict(base, year=2024, month=8), "overtime_is_regular", "R-OVERTIME"),
             ("lex superior", "R25-WITHHELD vs R-WITHHELD (default)", dict(base, year=2025, month=3), "pph21_withheld", "R25-WITHHELD"),
             ("repeal (supersedes)", "R24-PPH vs R16-PPH", dict(base, year=2024, month=3), "pph21", "R24-PPH"),
             ("valid time", "R16-PPH before TER", dict(base, year=2023, month=12), "pph21", "R16-PPH")]
    rows = []
    for principle, pair, case, fact, expected in tests:
        got = compute(g, case).trace.get(fact, ("-",))[0]
        rows.append({"principle": principle, "pair": pair, "period": f"{case['year']}-{case['month']:02d}", "fact": fact,
                     "expected winner": expected, "engine": got, "correct": got == expected})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    ui.mockup("Engine development history mapped to the regulation that triggered each change (hindsight-bias mitigation), "
              "and RA on the company-policy corpus.")


def tab_e2():
    st.markdown("Isolated mode: each document is applied to the gold knowledge base before it. One outcome per real document.")
    results = {name: state.e2(name) for name in ex.CONDITIONS}
    table = pd.DataFrame([{"condition": name, "SER": _pct(r["ser"], r["n"]), "SER upper 95%": round(r["ser_upper"], 2),
                           "CAR": _pct(r["car"], r["n"]), "CAR lower 95%": round(r["car_lower"], 2), "ABS": _pct(r["abs"], r["n"]),
                           "counterfactual": next(x["outcome"] for x in r["rows"] if x["split"] == "counterfactual"),
                           "distractor FP": _pct(r["distractor_fp"], r["n_distractors"])} for name, r in results.items()])
    st.dataframe(table, hide_index=True, width="stretch")
    fig = go.Figure()
    for name, r in results.items():
        coverage = (r["car"] + r["ser"]) / r["n"]
        risk = r["ser"] / (r["car"] + r["ser"]) if r["car"] + r["ser"] else 0
        fig.add_scatter(x=[coverage], y=[risk], mode="markers+text", text=[name], textposition="top center", name=name,
                        marker=dict(size=13))
    fig.update_layout(height=360, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                      xaxis=dict(title="coverage = CAR + SER", range=[-0.05, 1.1]),
                      yaxis=dict(title="selective risk = SER / (CAR + SER)", range=[-0.05, 1.1]))
    st.plotly_chart(fig, width="stretch")
    ui.where("Figure 'Keamanan dan kegunaan akuisisi per kondisi' (RQ2). The study adds exact CIs per point and "
             "Newcombe intervals for the paired differences.")

    name = st.selectbox("Per-document outcomes for condition", list(ex.CONDITIONS), key="e2_cond")
    r = results[name]
    st.dataframe(pd.DataFrame([{"document": x["document"], "split": x["split"], "layer": x["layer"], "type": x["change_type"],
                                "status": x["status"], "outcome": x["outcome"], "wrong S^E tuples": x["wrong_tuples"],
                                "candidates correct before gates": f"{x['c']}/{x['m']}", "groups": str(x["groups"]),
                                "selected": x["selected"], "reason": x["reason"]} for x in r["rows"]]),
                 hide_index=True, width="stretch")

    proposed = results["Proposed"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**pass@k on candidates before repair** (real relevant documents)")
        rows = [x for x in proposed["rows"] if x["relevant"] and x["m"]]
        st.dataframe(pd.DataFrame([{"document": x["document"], "m": x["m"], "c": x["c"],
                                    "pass@1": round(ex.pass_at(1, x["m"], x["c"]), 2),
                                    f"pass@{x['m']}": round(ex.pass_at(x["m"], x["m"], x["c"]), 2),
                                    f"1@{x['m']} (selected correct)": x["outcome"] == "correct-applied"} for x in rows]),
                     hide_index=True)
    with c2:
        st.markdown("**Gate confusion matrix** (positive = wrong candidate)")
        conf = ex.gate_confusion(proposed)
        st.dataframe(pd.DataFrame([{"gate": g, **{k: v for k, v in m.items() if k in ("TP", "FN", "FP", "TN")},
                                    "leakage": None if m["leakage"] is None else round(m["leakage"], 2),
                                    "false rejection": None if m["false_rejection"] is None else round(m["false_rejection"], 2)}
                                   for g, m in conf.items()]), hide_index=True)
    cf = next(x for x in proposed["rows"] if "memorised" in x)
    k, m, orig = cf["memorised"]
    st.markdown(f"**Memorisation on the counterfactual {cf['document']}:** {k}/{m} candidates use the original value {orig} "
                f"instead of the value in the document. Outcome: {cf['outcome']}.")
    ui.mockup("Correction effort per document (edit operations, Hungarian alignment), contamination split by training "
              "cutoff, quote accuracy, cost-accuracy curve, second open-weight model, AB2 (no KB context), AB5 (schema vs "
              "SHACL). Each needs a real model or an extra run.")


def tab_e3():
    variant = st.radio("Abstain variant", ("Keep the old knowledge base", "Perfect reviewer inserts the gold Delta"),
                       horizontal=True, key="e3_var")
    r = state.e3(variant.startswith("Perfect"))
    rows = r["rows"]
    s = state.study()
    types = {e["id"]: e["change_type"] for e in s.events}
    fig = go.Figure()
    for key, label, color in (("inherited", "inherited", "#b4b3ae"), ("new", "new", "#eb6834"), ("induced", "induced", "#c62828")):
        fig.add_bar(x=[f"{x['event']}<br>{types[x['event']]}" for x in rows], y=[len(x[key]) for x in rows], name=label,
                    marker_color=color)
    fig.update_layout(barmode="stack", height=340, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="wrong S^E tuples",
                      legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, width="stretch")
    ui.where("Figure 'Hasil regulation replay' (RQ3). The study adds markers for A2, A3_t, A4 and ranges over R repetitions.")
    st.dataframe(pd.DataFrame([{"event": x["event"], "status": x["status"], "inherited": len(x["inherited"]), "new": len(x["new"]),
                                "induced": len(x["induced"]), "induced (mechanical)": len(x["induced_mechanical"]),
                                "step correct": x["ok"], "A3_ω holds": x["knowledge_isolation"][0]} for x in rows]),
                 hide_index=True, width="stretch")
    c1, c2, c3 = st.columns(3)
    c1.metric("OAR", _pct(r["oar"], r["n"]), help=f"exact 95% lower bound {ev.cp_lower(r['oar'], r['n']):.2f}")
    c2.metric("Final drift D_N", f"{r['drift']}/{r['n_cases']}", help="S^E tuples wrong after the whole chain")
    c3.metric("A1 engine hash", ex.engine_hash())
    ui.mockup("Propagation ratio, persistence and recovery, error locking by G4, KB anomalies per version, contextual "
              "induced errors (re-generation with the system's own KB as context), noise floor from a second isolated run, "
              "drift weighted by the operational sample in rupiah, and B1 (commit history of open-source calculators).")


def tab_e4():
    r = state.e4()
    st.dataframe(pd.DataFrame(r["pairs"]), hide_index=True, width="stretch")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recall", f"{r['recall']:.2f}", help=f"exact 95% lower bound {r['recall_lower']:.2f}")
    c2.metric("Precision", f"{r['precision']:.2f}")
    c3.metric("F2", f"{r['f2']:.2f}")
    c4.metric("Flag-all baseline F2", f"{r['flag_all_f2']:.2f}", help=f"5π/(4π+1) with prevalence π = {r['prevalence']:.2f}")
    st.markdown("**Baselines B5**")
    st.dataframe(pd.DataFrame([
        {"detector": "Proposed: SPARQL over the graph", "input": "gold Delta", "recall": round(r["recall"], 2), "F2": round(r["f2"], 2)},
        {"detector": "Flag all policies touching a changed fact", "input": "gold Delta", "recall": 1.0, "F2": round(r["flag_all_f2"], 2)},
        {"detector": "Dependency scan without execution (flat)", "input": "gold Delta", "recall": None, "F2": None},
        {"detector": "LLM judgement", "input": "gold Delta", "recall": None, "F2": None},
        {"detector": "Proposed, full pipeline", "input": "selected Delta", "recall": None, "F2": None},
    ]), hide_index=True, width="stretch")
    ui.mockup("Rows without numbers need the flat scanner, an LLM judge, and the pipeline's own Deltas; labels of type (c) "
              "need two labellers and Cohen's κ.")


def tab_mockups():
    st.markdown("Everything the paper reports that the mini demo does not compute yet, and what fills it.")
    st.dataframe(pd.DataFrame([
        {"item": "E5 / B2: LLM computes PPh 21 directly", "fills": "motivation paragraph, Section VII", "needs": "≈100 operational cases, one model, references"},
        {"item": "B1: current practice", "fills": "motivation, RQ3 comparison", "needs": "commit history of open-source PPh 21 calculators around the TER switch"},
        {"item": "AB1: formalisation from scratch", "fills": "RQ2/RQ3 case study", "needs": "2-3 legal states, all documents in force, same gates"},
        {"item": "AB2: no KB context", "fills": "ablation table", "needs": "re-run E2 without step 3"},
        {"item": "AB5: schema vs SHACL, flat scan vs graph query", "fills": "answer to feedback no. 1", "needs": "JSON-schema-only G1, flat dependency scanner"},
        {"item": "Second (open-weight) model", "fills": "RQ2 robustness", "needs": "API or local model, same prompts"},
        {"item": "R repetitions and noise floor", "fills": "H3b", "needs": "R = 3 replays, one extra isolated run"},
        {"item": "Prospective events", "fills": "contamination-free evidence", "needs": "regulations issued after pre-registration"},
        {"item": "Statistics", "fills": "Section VII", "needs": "Newcombe paired difference, McNemar, non-inferiority margin δ_S, cluster bootstrap, Holm"},
        {"item": "Cost and feasibility", "fills": "Section VI cost subsection", "needs": "token counts and prices per call (logger below)"},
    ]), hide_index=True, width="stretch")
    st.markdown("**Cost estimate** (formula from the skeleton, editable)")
    c1, c2, c3, c4 = st.columns(4)
    d = c1.number_input("|D'| documents incl. counterfactuals and distractors", 1, 500, 40)
    m = c2.number_input("m candidates", 1, 10, 5)
    rbar = c3.number_input("mean repair rounds r̄", 0.0, 3.0, 0.5)
    price = c4.number_input("cost per call (USD)", 0.0, 5.0, 0.05)
    calls_e2 = d * m * (1 + rbar) * 2 + d
    calls_e3 = 2 * 3 * 4 * m * (1 + rbar)
    st.markdown(f"E2 (proposed, B3, B4): **{calls_e2:,.0f} calls** · E3 (2 variants, R=3, N=4): **{calls_e3:,.0f} calls** · "
                f"estimate **USD {(calls_e2 + calls_e3) * price:,.0f}** before ablations and AB1.")
    ui.mockup("Numbers here are inputs for the pre-registration, not measurements.")


def tab_log():
    calls = state.experiment_llm().calls
    st.markdown(f"{len(calls)} LLM calls made by the cached experiments (mock: tokens estimated, cost 0).")
    if calls:
        st.dataframe(pd.DataFrame(calls), hide_index=True, width="stretch")
    ui.mockup("The full logger also records the prompt hash, model version, access date, training cutoff, sampling "
              "parameters, latency, and the result of every gate, so all analyses can be re-run without calling the LLM.")


def show():
    st.title("Experiments")
    st.markdown("E0-E4 computed on the mini corpus with the mock LLM. The numbers are not results; the shapes are the "
                "tables and figures the paper will report.")
    tabs = st.tabs(["Summary", "E0 instruments", "E1 · RQ1", "E2 · RQ2", "E3 · RQ3", "E4 · RQ4", "Not computed yet", "LLM log"])
    with tabs[0]:
        tab_summary()
    with tabs[1]:
        tab_e0()
    with tabs[2]:
        tab_e1()
    with tabs[3]:
        tab_e2()
    with tabs[4]:
        tab_e3()
    with tabs[5]:
        tab_e4()
    with tabs[6]:
        tab_mockups()
    with tabs[7]:
        tab_log()

