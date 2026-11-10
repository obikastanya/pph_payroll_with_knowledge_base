"""Entry point of the PPh 21 knowledge-based system: page setup, navigation, sidebar, the assistant pop-up, and the
home page (what the system does, how it works, the state of the knowledge base, and the menu).

    streamlit run app/main.py        (from system_final/)
"""
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent
for p in (APP, APP.parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="PPh 21 KBS", page_icon=":material/calculate:", layout="wide")

import calculator  # noqa: E402
import common  # noqa: E402
import knowledge_base  # noqa: E402
import manage  # noqa: E402
import state  # noqa: E402
import workflow  # noqa: E402

# ====================================================================================================================
# Home page
# ====================================================================================================================
FLOW = """digraph F { rankdir=LR; bgcolor=transparent; nodesep=.3; ranksep=.4;
node [shape=box style="rounded,filled" fontname="Helvetica" fontsize=11 color="#b4b3ae" fillcolor="#ffffff"];
edge [color="#8a8984" arrowsize=.7 fontname="Helvetica" fontsize=9 fontcolor="#6b6a66"];
doc [label="New document\\nregulation / company\\npolicy" shape=note fillcolor="#f0efec"];
ai [label="The AI reads it and\\nwrites several\\ndraft versions" fillcolor="#e8f1fc" color="#2a78d6"];
chk [label="Automatic checks\\n+ do the drafts agree?\\n(or the AI is not sure)"];
rev [label="Human review\\napprove / fix / reject" fillcolor="#fdeee7" color="#eb6834"];
kb [label="Knowledge base\\nrules + valid dates\\n+ source articles" shape=cylinder
    fillcolor="#fff7e0" color="#b98900"];
eng [label="Calculation engine\\nresult + reasons\\nback to the article"];
calc [label="PPh 21 calculator\\nfor an employee" penwidth=2];
imp [label="Impact on company\\npolicies" style="rounded,dashed"];
doc -> ai -> chk -> rev -> kb -> eng -> calc; kb -> imp -> rev [style=dashed];
asst [label="AI assistant\\nhelps with review\\nand does the work" shape=oval fillcolor="#e8f1fc" color="#2a78d6"];
asst -> rev [style=dotted arrowhead=none]; }"""

MENUS = [
    ("PPh 21 calculator", ":material/calculate:", ["Default employee profile you can edit",
                                                  "Earlier months of the year can be edited",
                                                  "Results up to the chosen month, annual recalculation in the final "
                                                  "period",
                                                  "Common scenarios fill in all the data at once",
                                                  "Input fields follow the rules in force"]),
    ("Knowledge base viewer", ":material/hub:", ["Topic map and calculation flow", "Numbers over time",
                                                 "History and comparison of two dates",
                                                 "Data the rules need", "Search"]),
    ("Knowledge base management", ":material/edit_document:", ["New documents with the AI's work",
                                                               "Review: approve, edit, ask the AI to fix, reject",
                                                               "Before/after example and impact on company policies",
                                                               "Add, change, revoke: by hand or with the AI",
                                                               "Knowledge base check and version history"]),
    ("AI assistant", ":material/forum:", ["Pop-up window on every page", "Chat is saved and can be cleared",
                                          "Choose a model; the default is the low-cost one",
                                          "Prepares drafts, never approves them"]),
]


def show_home():
    st.session_state.page_ctx = "home"
    st.title("PPh 21 system based on a knowledge base")
    common.md(f"The system computes {common.term('PPh 21')} for permanent employees from a "
              f"{common.term('knowledge base')}: the tax rules, numbers, and tables, each with its "
              f"{common.term('valid', 'valid dates')} and its {common.term('source', 'source article')}. When a "
              "regulation or a company policy changes, the knowledge base is updated, not the program.")
    left, right = st.columns(2, gap="large")
    with left.container(border=True):
        st.markdown("**:material/description: A new document becomes an approved update**")
        common.md("Upload a new regulation or company policy in Knowledge base management. The AI reads it and "
                  f"writes a {common.term('proposal', 'proposed update')}; automatic {common.term('checks')} screen "
                  f"it, and a person {common.term('review', 'reviews')} it: approve, fix, or reject. Only an approved "
                  "update changes the calculation.")
    with right.container(border=True):
        st.markdown("**:material/calculate: The calculator computes PPh 21 with a trace**")
        common.md("Enter an employee's pay for a tax month. The calculator applies the rules in force on that date "
                  f"and shows a {common.term('trace')}: every step of the calculation with the rule and the source "
                  "article it comes from.")
    s = state.load()
    st.markdown("#### State of the knowledge base")
    c = st.columns(4)
    c[0].metric("Knowledge base known until", state.fmt_date(state.known_until()), help=common.tip("recorded"))
    c[1].metric("Rules in force today", sum(r.kind == "rule" and state.in_force(r, state.TODAY)
                                            and not state.is_input_convention(r) for r in state.current()),
                help=common.tip("rule"))
    c[2].metric("Updates approved in the app", len(s["approved"]), help=common.tip("update"))
    c[3].metric("Documents waiting", sum(state.status(p["id"], s) in ("review", "uncertain", "awaiting_ai")
                                         for p in state.pending(s)),
                help="New documents that have not been approved or rejected yet.")
    common.md(f"The {common.term('starting knowledge base')} holds the regulations recorded up to "
              f"**{state.base_label()}**."
              + (" Approved since then: " + "; ".join(f"{a['title']} ({a['when']})" for a in s["approved"]) + "."
                 if s["approved"] else " No update has been approved in the app yet."))
    st.markdown("#### How it works")
    st.graphviz_chart(FLOW, width="stretch")
    st.markdown("#### Menu")
    cols = st.columns(4)
    for col, (title, icon, feats) in zip(cols, MENUS):
        with col.container(border=True):
            st.markdown(f"**{icon} {title}**")
            st.markdown("\n".join(f"- {f}" for f in feats))


# ====================================================================================================================
# Navigation and sidebar
# ====================================================================================================================
common.setup()
pages = st.navigation([
    st.Page(show_home, title="Home", icon=":material/home:", default=True),
    st.Page(calculator.show, title="PPh 21 calculator", icon=":material/calculate:", url_path="calculator"),
    st.Page(knowledge_base.show, title="Knowledge base viewer", icon=":material/hub:", url_path="kb"),
    st.Page(manage.show, title="Knowledge base management", icon=":material/edit_document:", url_path="manage"),
])
st.session_state.g_date = None     # each page sets the date its explanations speak about
with st.sidebar:
    common.reset_control()
    s = state.load()
    st.caption(f"Knowledge base known until **{state.fmt_date(state.known_until())}** · {len(s['approved'])} "
               "updates approved in the app")
    with st.expander("Glossary", icon=":material/menu_book:"):
        common.dictionary()
pages.run()
workflow.button()
