"""Mockup v3 of the PPh 21 knowledge-based system: the research system as a demo for a finance admin.

    env\\Scripts\\streamlit run mini_demo\\mockup\\main.py --server.port 8503

Runs on the research system's knowledge base and engine. The demo starts from a fixed state (demo.py) and every change
made during a demo can be undone with "Kembalikan ke keadaan awal demo". See README.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="PPh 21 KBS · demo", page_icon=":material/calculate:", layout="wide")

import assistant  # noqa: E402
import data as d  # noqa: E402
import demo  # noqa: E402
import glossary  # noqa: E402
import page_calculator  # noqa: E402
import page_home  # noqa: E402
import page_manager  # noqa: E402
import page_results  # noqa: E402
import page_viewer  # noqa: E402
import ui  # noqa: E402

ui.setup()
pages = st.navigation({
    "Sistem": [
        st.Page(page_home.show, title="Beranda", icon=":material/home:", default=True),
        st.Page(page_calculator.show, title="Kalkulator PPh 21", icon=":material/calculate:", url_path="kalkulator"),
        st.Page(page_viewer.show, title="Penampil knowledge base", icon=":material/hub:", url_path="kb"),
        st.Page(page_manager.show, title="Manajemen knowledge base", icon=":material/edit_document:", url_path="kelola"),
    ],
    "Penelitian": [
        st.Page(page_results.show, title="Hasil penelitian", icon=":material/science:", url_path="hasil"),
    ],
})
with st.sidebar:
    s = demo.load()
    st.caption(f"Knowledge base diketahui sampai **{d.tgl(demo.known_until())}** · {len(s['approved'])} pembaruan "
               f"disetujui selama demo")
    page_home.reset_button("side_reset")
    with st.expander("Kamus istilah", icon=":material/menu_book:"):
        glossary.dictionary()
pages.run()
assistant.button()
