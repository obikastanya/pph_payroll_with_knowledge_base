"""Shared state of the app: the study (corpus, gold chain, S^E), cached experiment results, and the KB repository.

Experiment results and the study are cached for every session. The repository, the inbox, and the review queue
live in the session, so each visitor can apply updates without affecting anyone else.
"""
import sys
from datetime import date
from pathlib import Path

import streamlit as st

APP = Path(__file__).resolve().parent
MINI = APP.parent
for p in (str(MINI), str(APP)):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments as ex  # noqa: E402
import repository  # noqa: E402
from mock_llm import MockLLM  # noqa: E402

TODAY = date.today()
GOLD = "Gold K* after every event"
SYSTEM = "System chain, no reviewer (E3)"


@st.cache_resource(show_spinner="Building the gold chain and the test space S^E ...")
def study():
    return ex.prepare()


@st.cache_resource(show_spinner=False)
def experiment_llm():
    """One mock LLM for all cached experiments, so its call log is the experiment log."""
    return MockLLM()


@st.cache_resource(show_spinner="E0: references and mutation score ...")
def e0():
    return ex.e0(study())


@st.cache_resource(show_spinner="E1: unseen change ...")
def e1():
    return ex.e1(study())


@st.cache_resource(show_spinner="E2: isolated acquisition ...")
def e2(condition="Proposed"):
    return ex.e2(study(), experiment_llm(), condition)


@st.cache_resource(show_spinner="E3: regulation replay ...")
def e3(perfect_reviewer=False):
    return ex.e3(study(), experiment_llm(), e2()["isolated"], perfect_reviewer)


@st.cache_resource(show_spinner="E4: impact analysis ...")
def e4():
    return ex.e4(study())


def repo():
    if "repo" not in st.session_state:
        s = study()
        st.session_state.repo = repository.demo_repository(s.events, s.gold)
        st.session_state.inbox = [dict(e, text=s.texts[e["id"]], origin="corpus") for e in s.events if e["id"] == "E2"]
        st.session_state.runs = {}
        st.session_state.pending = None
    return st.session_state.repo


def reset():
    for k in ("repo", "inbox", "runs", "pending"):
        st.session_state.pop(k, None)


def catalog():
    """Every knowledge base the user can pick: repository versions, the pending candidate, and research views."""
    r = repo()
    out = {f"{v.name} · {v.label}": v.graph for v in reversed(r.versions)}
    pending = st.session_state.get("pending")
    if pending and pending["result"].kb is not None and pending["result"].status == "applied":
        out[f"Pending review · {pending['document']} (not applied)"] = pending["result"].kb
    out[GOLD] = study().kb_gold
    out[SYSTEM] = e3()["kb_sys"]
    return out


def version_picker(label, key, default_head=True, help=None):
    options = list(catalog())
    choice = st.selectbox(label, options, index=0 if default_head else min(1, len(options) - 1), key=key, help=help)
    return choice, catalog()[choice]
