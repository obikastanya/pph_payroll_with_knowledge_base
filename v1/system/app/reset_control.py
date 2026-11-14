"""Reset to the initial state: one icon button at the top of the sidebar, level with the sidebar toggle. It asks for a
confirmation, and after the page reloads a message says the state was restored. The initial state is always the same:
the knowledge base without anything approved, drafted, or uploaded in the app (store.reset)."""
import streamlit as st

import store

CSS = """
<style>
.st-key-resetbar { position: absolute; top: .85rem; left: 1rem; z-index: 5; width: auto !important; }
.st-key-resetbar [data-testid="stPopoverButton"] {
    min-height: 2rem; width: 2rem; padding: 0; border-radius: 8px; color: #6b6a66; }
.st-key-resetbar [data-testid="stPopoverButton"]:hover { background: rgba(128,128,128,.16); color: inherit; }
.st-key-resetbar [data-testid="stPopoverButton"] > div { justify-content: center; }
.st-key-resetbar [data-testid="stPopoverButton"] > div > div:last-child { display: none; }
.st-key-resetbar_body { width: 17rem; }
body:has(.st-key-resetbar button[aria-expanded="true"]) [data-testid="stTooltipContent"] { display: none; }
</style>
"""


def show():
    st.markdown(CSS, unsafe_allow_html=True)
    if st.session_state.pop("_reset_notice", False):
        st.toast(f"Restored to the initial state: knowledge base as of {store.base_label()}, with no updates, drafts, "
                 "uploads, or chat.", icon=":material/check_circle:")
    with st.container(key="resetbar"):
        with st.popover("", icon=":material/restart_alt:", type="tertiary", help="Restore the initial state"):
            with st.container(key="resetbar_body"):
                st.markdown("**Restore the initial state**")
                st.caption("Everything done is erased: approved updates, drafts, edits, uploads, and "
                           f"assistant chat. The knowledge base returns to its initial state (as of {store.base_label()}). "
                           "AI cost already spent is not refunded.")
                if st.button("Yes, restore", type="primary", key="reset_confirm", icon=":material/restart_alt:",
                             width="stretch"):
                    store.reset()
                    st.rerun()
