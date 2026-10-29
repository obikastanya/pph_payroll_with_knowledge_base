"""Shared state of the app: the knowledge base (gold chain, company policies, the user's workspace updates), versions,
documents, and stored acquisition runs.

The gold chain (dataset/12_emas/kb.trig) is never modified. Updates applied in the management screens are stored as
Delta files in system/app/workspace/updates/ and applied on top of the gold chain, in order.
"""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "system", ROOT / "system" / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import streamlit as st  # noqa: E402

import build_gold  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402
from pph21kbs.text import registry  # noqa: E402

WORKSPACE = ROOT / "system" / "app" / "workspace"
UPDATES = WORKSPACE / "updates"
UPLOADS = WORKSPACE / "docs"
EXPERIMENTS = ROOT / "experiments"
TODAY = date.today()


@st.cache_resource(show_spinner="Memuat knowledge base emas ...")
def gold_chain():
    return build_gold.load_graph()


@st.cache_resource
def policy_deltas():
    """Company policies of the corpus (side updates of the gold): document id -> Delta JSON."""
    return {u.doc.id: u.to_json() for u in build_gold.collect_side() if u.kind == "policy"}


def workspace_files():
    UPDATES.mkdir(parents=True, exist_ok=True)
    return sorted(UPDATES.glob("*.json"))


def _signature():
    return tuple((f.name, f.stat().st_mtime) for f in workspace_files())


@st.cache_resource(show_spinner="Menerapkan pembaruan ruang kerja ...")
def _kb(signature):
    kb = gold_chain()
    for f in workspace_files():
        kb = apply_delta(kb, json.loads(f.read_text(encoding="utf-8")))
    return kb


def kb():
    """The current knowledge base: gold chain plus workspace updates."""
    return _kb(_signature())


def versions():
    """(label, update id) for every update of the current knowledge base, oldest first."""
    out = []
    for i, u in enumerate(kb().updates, start=1):
        what = u.event_id or u.document
        mark = "ruang kerja" if u.update_id.startswith("WS-") else "emas"
        out.append((f"v{i:02d} · {u.update_id} · {what} · {u.recorded_on or ''} ({mark})", u.update_id))
    return out


@st.cache_resource
def _until(signature, update_id):
    return kb().until(update_id)


def kb_at(update_id=None):
    return kb() if update_id is None else _until(_signature(), update_id)


@st.cache_resource
def _with_policy(signature, update_id, policy):
    return apply_delta(kb_at(update_id), policy_deltas()[policy])


def kb_for(update_id=None, policy=None):
    """A version of the knowledge base, with a company policy installed when one is chosen."""
    if not policy:
        return kb_at(update_id)
    return _with_policy(_signature(), update_id, policy)


def save_update(delta, note=""):
    """Store a reviewed Delta in the workspace. Its id gets the prefix WS- so it is told apart from the gold."""
    files = workspace_files()
    n = len(files) + 1
    d = dict(delta)
    if not str(d.get("delta_id", "")).startswith("WS-"):
        d["delta_id"] = f"WS-{n:03d}-{d.get('delta_id', 'update')}"
    if note:
        d["note"] = (d.get("note", "") + " | " + note).strip(" |")
    path = UPDATES / f"{n:03d}_{d['delta_id']}.json"
    path.write_text(json.dumps(d, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return path


def reset_workspace():
    for f in workspace_files():
        f.unlink()


def documents():
    return registry()


def events():
    """Every event of the corpus with its part, for the inbox."""
    out = []
    for e in corpus.regulation_events():
        out.append(e)
    out += list(corpus.fictive_events()) + list(corpus.policy_events()) + list(corpus.counterfactual_events())
    return out


def stored_runs(event_id):
    """Experiment runs that hold a result for an event: run name -> path."""
    main = ("e2-regulasi", "e2-pkb", "e2-pengecoh", "e2-sintetis", "e2-kontrafaktual", "kalibrasi-1", "kalibrasi-2")
    found = {p.parent.parent.name: p for p in EXPERIMENTS.glob(f"*/results/{event_id}.json")}
    order = [r for r in main if r in found] + sorted(r for r in found if r not in main)
    return {r: found[r] for r in order}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def gold_delta(event_id):
    for u in build_gold.collect():
        if u.event_id == event_id:
            return u.to_json()
    for u in build_gold.collect_side():
        if u.event_id == event_id or u.doc.id == event_id:
            return u.to_json()
    return None
