"""Home: what the system is, how it works, the menus and their main features, the state of the demo, the demo steps,
and the reset to the initial state."""
import streamlit as st

import data as d
import glossary as g
import store
import ui

FLOW = """digraph F { rankdir=LR; bgcolor=transparent; nodesep=.3; ranksep=.4;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11 color="#b4b3ae" fillcolor="#ffffff"];
edge [color="#8a8984" arrowsize=.7 fontname="Helvetica" fontsize=9 fontcolor="#6b6a66"];
doc [label="New documents\\nregulation / company\\npolicy" shape=note fillcolor="#f0efec"];
ai [label="AI reads and\\nwrites several\\nproposed versions" fillcolor="#e8f1fc" color="#2a78d6"];
chk [label="Automatic checks\\n+ agreement check\\n(or system unsure)"];
rev [label="Human review\\napprove / fix / reject" fillcolor="#fdeee7" color="#eb6834"];
kb [label="Knowledge base\\nrules + effective date\\n+ source article" shape=cylinder fillcolor="#fff7e0" color="#b98900"];
eng [label="Calculation engine\\nresult + reasons\\ndown to the article"];
calc [label="PPh 21 calculator\\nfor an employee" penwidth=2];
imp [label="Impact on company\\npolicies" style="rounded,dashed"];
doc -> ai -> chk -> rev -> kb -> eng -> calc; kb -> imp -> rev [style=dashed];
asst [label="AI assistant\\nhelps with review\\nand drafting" shape=oval fillcolor="#e8f1fc" color="#2a78d6"];
asst -> rev [style=dotted arrowhead=none]; }"""

MENUS = [
    ("PPh 21 calculator", ":material/calculate:", ["Built-in employee profile you can edit", "Earlier months can be edited",
                                                   "Results up to the chosen month, full-year recalculation in the final period",
                                                   "Common scenarios fill in all data at once",
                                                   "Data fields are built from the rules in force"]),
    ("Knowledge base viewer", ":material/hub:", ["Topic map and calculation flow", "Numbers over time",
                                                 "History and comparison of two dates",
                                                 "Data the rules need", "Search"]),
    ("Knowledge base management", ":material/edit_document:", ["New documents with the AI's work",
                                                               "Review: approve, edit, ask AI to fix, reject",
                                                               "Before/after examples and policy impact",
                                                               "Add, change, revoke: by hand or ask AI",
                                                               "KB check and version history"]),
    ("AI assistant", ":material/forum:", ["Pop-up window on every page", "Chat is saved and can be deleted",
                                          "Choose the model; cheap default", "Prepares drafts, never approves"]),
]

STEPS = [
    ("Calculate a garment factory employee, January 2026 (scenario 'Labor-intensive DTP 2026'): no DTP yet.",
     lambda s: False),
    ("Review PMK 105/2025: spot the mistake in the AI's proposal, ask the AI to fix it, then approve.",
     lambda s: s["decided"].get("E11") == "disetujui"),
    ("Calculate the same scenario again: DTP now appears, with its article.", lambda s: False),
    ("Approve policy SP14: the HR data field appears by itself in the calculator (scenario 'THR under company policy').",
     lambda s: s["decided"].get("SP14") == "disetujui"),
    ("Approve PER-11/PJ/2025 (retroactive) and compare the 'as of knowledge date' calculation in the calculator.",
     lambda s: s["decided"].get("E13") == "disetujui"),
    ("PKB WIKA: the system is unsure. Ask the AI to redo it or write it by hand.",
     lambda s: s["decided"].get("PKB-WIKA-2025") in ("disetujui", "ditolak")),
    ("Ask the assistant to make a draft (e.g. the JP wage cap for 2027), review it, approve it.",
     lambda s: any(a["id"].startswith("ANGKA") for a in s["approved"])),
    ("Restore the initial demo state.", lambda s: False),
]


def reset_button(key):
    with st.popover("Restore initial demo state", icon=":material/restart_alt:", width="stretch"):
        st.markdown("Everything done during the demo is erased: approved updates, drafts, edits, uploads, and "
                    "assistant chat. The knowledge base returns to its initial state.")
        if st.button("Yes, restore", type="primary", key=key, icon=":material/restart_alt:"):
            store.reset()
            st.rerun()


def show():
    st.session_state.page_ctx = "beranda"
    st.title("Knowledge-based PPh 21 system")
    g.md(f"The system calculates {g.term('PPh 21')} for permanent employees from a {g.term('knowledge base')}: tax rules, "
         f"numbers, and tables that each have an {g.term('berlaku', 'effective date')} and a "
         f"{g.term('sumber', 'source article')}. "
         "When a regulation or company policy changes, the AI reads the document and writes a proposed update; "
         "automatic checks screen it and a person approves it. The program does not need to change.")
    s = store.load()
    c = st.columns(4)
    c[0].metric("Knowledge base known until", d.tgl(store.known_until()), help=g.tip("dicatat"))
    c[1].metric("Rules in force today", sum(r.kind == "rule" and d.in_force(r, store.TODAY) and not d.is_input_convention(r)
                                               for r in d.current()), help=g.tip("aturan"))
    c[2].metric("Approved during the demo" if store.DEMO else "Approved in the app", len(s["approved"]),
                help=g.tip("pembaruan"))
    c[3].metric("Documents waiting", sum(store.status(p["id"], s) in ("review", "ragu", "menunggu AI")
                                        for p in store.pending(s)),
                help="New documents that have not been approved or rejected yet.")
    st.markdown("#### How the system works")
    st.graphviz_chart(FLOW, width="stretch")
    st.markdown("#### Menu")
    cols = st.columns(4)
    for col, (title, icon, feats) in zip(cols, MENUS):
        with col.container(border=True):
            st.markdown(f"**{icon} {title}**")
            st.markdown("\n".join(f"- {f}" for f in feats))
    if not store.DEMO:
        return
    st.markdown("#### Demo")
    left, right = st.columns([2, 1], gap="large")
    with left:
        g.md(f"Initial demo state: the research knowledge base as of **{store.base_label()}**, no company policy, and "
             "eight documents waiting in Knowledge base management: five 2025–2026 regulations, one company policy, one PKB, "
             "and one document that is not relevant. The AI's work is taken from the research, so the demo does not use "
             "API credit.")
        for i, (text, done) in enumerate(STEPS, 1):
            mark = ":material/check_circle:" if done(s) else ":material/radio_button_unchecked:"
            st.markdown(f"{mark} **{i}.** {text}")
    with right:
        with st.container(border=True):
            st.markdown("**Demo state**")
            n_up, n_dr, n_q = len(s["approved"]), len(s["drafts"]), len(store.chat_load()) // 2
            st.caption(f"{n_up} update{'' if n_up == 1 else 's'} approved, {n_dr} draft{'' if n_dr == 1 else 's'}, "
                       f"{n_q} question{'' if n_q == 1 else 's'} to the assistant.")
            reset_button("home_reset")
