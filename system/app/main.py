"""The PPh 21 knowledge-based system: calculator, knowledge base viewer (content and the knowledge base system itself),
knowledge base management with the AI, the assistant, and the research results.

    env\\Scripts\\streamlit run system\\app\\main.py

Runs on the research's knowledge base and engine; the AI (acquisition and repair with Claude, assistant with an
OpenAI model) uses API credit within the limits of ai.py and config.BUDGET_USD. The demo with its fixed initial state
and reset runs the same program from mini_demo/mockup/main.py. See README.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

import store  # noqa: E402

st.set_page_config(page_title="PPh 21 KBS" + (" · demo" if store.DEMO else ""), page_icon=":material/calculate:",
                   layout="wide")

import ai  # noqa: E402
import assistant  # noqa: E402
import data as d  # noqa: E402
import glossary  # noqa: E402
import page_calculator  # noqa: E402
import page_home  # noqa: E402
import page_manager  # noqa: E402
import page_results  # noqa: E402
import page_viewer  # noqa: E402
import reset_control  # noqa: E402
import ui  # noqa: E402

ui.setup()
ai.register(store.load()["inbox"])          # uploaded documents back in the document registry after a restart
pages = st.navigation({
    "System": [
        st.Page(page_home.show, title="Home", icon=":material/home:", default=True),
        st.Page(page_calculator.show, title="PPh 21 calculator", icon=":material/calculate:", url_path="kalkulator"),
        st.Page(page_viewer.show, title="Knowledge base viewer", icon=":material/hub:", url_path="kb"),
        st.Page(page_manager.show, title="Knowledge base management", icon=":material/edit_document:", url_path="kelola"),
    ],
    "Research": [
        st.Page(page_results.show, title="Research results", icon=":material/science:", url_path="hasil"),
    ],
})
st.session_state.g_date = None     # each page sets the date its explanations speak about
with st.sidebar:
    reset_control.show()
    s = store.load()
    n_up = len(s["approved"])
    st.caption(f"Knowledge base known until **{d.tgl(store.known_until())}** · {n_up} update{'' if n_up == 1 else 's'} "
               f"approved {'during the demo' if store.DEMO else 'in the app'}")
    with st.expander("Glossary", icon=":material/menu_book:"):
        glossary.dictionary()
pages.run()
assistant.button()
