r"""The PPh 21 knowledge-based system: calculator, knowledge base viewer, knowledge base management, and the research
results, on the research knowledge base (gold chain dataset/12_emas plus the workspace updates).

    env\Scripts\streamlit run system\app\main.py

No API key is needed except for a live acquisition run in the management page (Claude, uses credit).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="KBS PPh 21", page_icon=":material/account_tree:", layout="wide")

import state  # noqa: E402,F401  (puts system/ and system/tools on the path)
import page_calculator  # noqa: E402
import page_home  # noqa: E402
import page_manager  # noqa: E402
import page_results  # noqa: E402
import page_viewer  # noqa: E402
import widgets as ui  # noqa: E402

ui.setup()
pages = st.navigation({
    "Sistem": [
        st.Page(page_home.show, title="Beranda", icon=":material/home:", default=True),
        st.Page(page_calculator.show, title="Kalkulator PPh 21", icon=":material/calculate:", url_path="kalkulator"),
        st.Page(page_viewer.show, title="Penampil knowledge base", icon=":material/hub:", url_path="kb"),
        st.Page(page_manager.show, title="Manajemen knowledge base", icon=":material/upload_file:", url_path="kelola"),
    ],
    "Penelitian": [
        st.Page(page_results.show, title="Hasil penelitian", icon=":material/science:", url_path="hasil"),
    ],
})
with st.sidebar:
    kb = state.kb()
    ws = len(state.workspace_files())
    st.caption(f"KB: **{len(kb.updates)} pembaruan** · {len(kb.records)} rekaman · ruang kerja {ws} · "
               f"sidik jari `{kb.fingerprint()[:12]}`")
pages.run()
