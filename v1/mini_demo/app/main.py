"""Mockup of the planned system: knowledge-base viewer, payroll calculator, knowledge-base management, and the
experiment dashboard that produces the paper's results.

    env\\Scripts\\streamlit run mini_demo\\app\\main.py

Everything runs on the mini engine, the mock LLM, and the demo corpus. Parts that only show what the full system
will do are marked "Mockup" on screen.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="PPh 21 KBS mockup", page_icon=":material/account_tree:", layout="wide")

import state  # noqa: E402,F401  (puts mini_demo/ on the path)
import page_calculator  # noqa: E402
import page_experiments  # noqa: E402
import page_kb_manager  # noqa: E402
import page_kb_viewer  # noqa: E402
import page_overview  # noqa: E402
import widgets as ui  # noqa: E402

ui.setup()
pages = st.navigation({
    "System": [
        st.Page(page_overview.show, title="Overview", icon=":material/home:", default=True),
        st.Page(page_calculator.show, title="Payroll calculator", icon=":material/calculate:", url_path="calculator"),
        st.Page(page_kb_viewer.show, title="Knowledge base viewer", icon=":material/hub:", url_path="kb"),
        st.Page(page_kb_manager.show, title="Knowledge base management", icon=":material/upload_file:", url_path="manage"),
    ],
    "Research": [
        st.Page(page_experiments.show, title="Experiments (E0-E5)", icon=":material/science:", url_path="experiments"),
        st.Page(page_overview.blueprint, title="Blueprint", icon=":material/description:", url_path="blueprint"),
    ],
})
with st.sidebar:
    r = state.repo()
    st.caption(f"Repository head: **{r.head.name}** · {len(r.versions)} versions · inbox {len(st.session_state.inbox)}")
    if st.button("Reset demo state", icon=":material/restart_alt:", width="stretch"):
        state.reset()
        st.rerun()
pages.run()
