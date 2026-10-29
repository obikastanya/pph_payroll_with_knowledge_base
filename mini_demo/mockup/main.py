"""UI mockup v2 of the PPh 21 knowledge-based system: designed for a finance admin.

    env\\Scripts\\streamlit run mini_demo\\mockup\\main.py --server.port 8502

Calculator and knowledge base viewer run on the research system's gold knowledge base and engine (read only).
Knowledge base management and the assistant are simulated in the session. See README.md for the design notes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="PPh 21 KBS · mockup v2", page_icon=":material/calculate:", layout="wide")

import glossary  # noqa: E402
import page_calculator  # noqa: E402
import page_manager  # noqa: E402
import page_results  # noqa: E402
import page_viewer  # noqa: E402
import ui  # noqa: E402

ui.setup()
pages = st.navigation({
    "Sistem": [
        st.Page(page_calculator.show, title="Kalkulator PPh 21", icon=":material/calculate:", url_path="kalkulator",
                default=True),
        st.Page(page_viewer.show, title="Penampil knowledge base", icon=":material/hub:", url_path="kb"),
        st.Page(page_manager.show, title="Manajemen knowledge base", icon=":material/edit_document:", url_path="kelola"),
    ],
    "Penelitian": [
        st.Page(page_results.show, title="Hasil penelitian", icon=":material/science:", url_path="hasil"),
    ],
})
with st.sidebar:
    st.caption(":orange-badge[Mockup v2] Rancangan tampilan untuk admin finance. Beranda tetap seperti aplikasi "
               "sistem (`system/app`).")
    with st.expander("Kamus istilah", icon=":material/menu_book:"):
        glossary.dictionary()
pages.run()
