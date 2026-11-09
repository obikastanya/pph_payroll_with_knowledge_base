"""State of the application: the knowledge base in use, everything done on top of it, and the documents waiting.

Two modes, one program:
- sistem (default): the full gold knowledge base of the research plus the updates approved in the app. Documents come
  in through the inbox (upload) and are read by the research's acquisition pipeline with the real LLM. Kept in
  system/app/workspace/.
- demo (PPH21_APP_MODE=demo, started by mini_demo/mockup/main.py): a fixed initial state, the gold knowledge base up to
  the 2025 JP wage cap (recorded 27 Feb 2025), no company policy, and eight documents waiting with the real AI results of
  the research runs (experiments/*/results). Kept in mini_demo/mockup/workspace/; Reset deletes it.
"""
import json
import os
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT / "system", ROOT / "system" / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import build_gold  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

MODE = "demo" if os.environ.get("PPH21_APP_MODE") == "demo" else "sistem"
DEMO = MODE == "demo"
WORKSPACE = (ROOT / "mini_demo" / "mockup" / "workspace") if DEMO else (ROOT / "system" / "app" / "workspace")
STATE = WORKSPACE / "state.json"
CHAT = WORKSPACE / "chat.json"
RUNS = WORKSPACE / "runs"                    # acquisition runs of the documents read in the app
EXP = ROOT / "experiments"
BASE_UPDATE = "GOLD-E08" if DEMO else None   # None: the whole gold chain

# demo: documents waiting in the initial state (id, kind, run file, what the research found)
DEMO_PENDING = [
    {"id": "E13", "doc": "PER-11-PJ-2025", "kind": "regulasi", "run": "e2-regulasi/results/E13.json",
     "research": "benar", "why": "Retroactive rounding rule: old calculations change when recalculated."},
    {"id": "E09", "doc": "PP-36-2025", "kind": "regulasi", "run": "e2-regulasi/results/E09.json",
     "research": "benar", "why": "JKK contribution relief for labor-intensive industries."},
    {"id": "E10", "doc": "PMK-72-2025", "kind": "regulasi", "run": "e2-regulasi/results/E10.json",
     "research": "benar", "why": "Government-borne tax (DTP) for the tourism sector; affects the hotel's company policy."},
    {"id": "E11", "doc": "PMK-105-2025", "kind": "regulasi", "run": "e2-regulasi/results/E11.json",
     "research": "salah", "why": "Compare the cards 'Fixed and regular gross income' and 'Fixed income in the first month' with the 2025 "
                                 "rules shown below them: the AI dropped the company house and car from the Rp10 million cap test, "
                                 "and dropped contract-based income for new employees. Use Ask AI to fix with that note."},
    {"id": "E12", "doc": "BPJSTK-JP-2026", "kind": "regulasi", "run": "e2-regulasi/results/E12.json",
     "research": "benar", "why": "Yearly change of a number, the most common kind of update."},
    {"id": "SP14", "doc": "SP14", "kind": "kebijakan", "run": "e2-sintetis/results/SP14.json",
     "research": "tidak bisa dinilai", "why": "Religious holiday allowance (THR) is based on length of service: a new HR data column appears in the calculator."},
    {"id": "PKB-WIKA-2025", "doc": "PKB-WIKA-2025", "kind": "kebijakan", "run": "e2-pkb/results/PKB-WIKA-2025.json",
     "research": "ragu", "why": "The AI's proposed versions do not agree; do it by hand or with AI help."},
    {"id": "P05", "doc": "PMK-81-2024", "kind": "regulasi", "run": "e2-pengecoh/results/P05.json",
     "research": "tidak relevan", "why": "Coretax administration document: does not change any calculation."},
]


def pending(s=None):
    """Documents in the inbox: the fixed list of the demo, or the documents uploaded in the app."""
    return (DEMO_PENDING if DEMO else []) + (s or load())["inbox"]


def pending_by_id(s=None):
    return {p["id"]: p for p in pending(s)}


# ---------------------------------------------------------------- state file
def _empty():
    return {"approved": [], "decided": {}, "drafts": [], "uploads": [], "log": [], "fixed": {}, "catalog": [],
            "employees": {}, "inbox": []}


def load():
    if STATE.exists():
        return {**_empty(), **json.loads(STATE.read_text(encoding="utf-8"))}
    return _empty()


def save(s):
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def log(s, text):
    s["log"].insert(0, {"when": datetime.now().strftime("%d %b %H:%M"), "what": text})


def reset():
    """Back to the initial state: the workspace is deleted, so the knowledge base is the base one again."""
    shutil.rmtree(WORKSPACE, ignore_errors=True)
    keep = {"_pages"}
    for k in list(st.session_state.keys()):
        if k not in keep:
            del st.session_state[k]
    _kb_cached.clear()
    _kb_prefix.clear()
    st.session_state["_reset_notice"] = True      # shown once by reset_control after the page reloads


# ---------------------------------------------------------------- knowledge base
@st.cache_resource(show_spinner="Loading knowledge base ...")
def gold():
    return build_gold.load_graph()


@st.cache_resource
def base():
    """The knowledge base before anything approved in the app: the gold chain (demo: up to its initial state)."""
    return gold().until(BASE_UPDATE) if BASE_UPDATE else gold()


def base_label():
    from data import tgl
    return tgl(max(u.recorded_on for u in base().updates if u.recorded_on))


@st.cache_resource(show_spinner="Applying updates ...")
def _kb_cached(signature):
    k = base()
    for a in load()["approved"]:
        k = apply_delta(k, a["delta"])
    return k


def signature():
    return STATE.stat().st_mtime if STATE.exists() else 0


def kb():
    return _kb_cached(signature())


@st.cache_resource
def _kb_prefix(signature, n):
    k = base()
    for a in load()["approved"][:n]:
        k = apply_delta(k, a["delta"])
    return k


def kb_before(n):
    """The knowledge base before the n-th approved update of the demo (0 = initial state)."""
    return _kb_prefix(signature(), n)


def known_until():
    ups = kb().updates
    return max(u.recorded_on for u in ups if u.recorded_on)


def installed_policies():
    """Company policies in the current knowledge base: id -> title."""
    out = {}
    for a in load()["approved"]:
        for el in a["delta"].get("add", []):
            if el.get("kind") == "rule" and el.get("policy"):
                out[el["policy"]] = a["title"]
    return out


# ---------------------------------------------------------------- AI results
@st.cache_data
def _read(path, mtime):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run(pid):
    """The acquisition run of a waiting document: stored from the research (demo) or made in the app (sistem)."""
    p = pending_by_id().get(pid)
    if not p or not p.get("run"):
        return None
    path = (WORKSPACE if p.get("upload") else EXP) / p["run"]
    return _read(str(path), path.stat().st_mtime) if path.exists() else None


@st.cache_data
def gold_delta(pid):
    """The research's reference answer for a document (used only for the simulated 'AI fixes it' step)."""
    for u in build_gold.collect():
        if u.event_id == pid:
            return u.to_json()
    for u in build_gold.collect_side():
        if u.doc.id == pid:
            return u.to_json()
    return None


def status(pid, s=None):
    s = s or load()
    if pid in s["decided"]:
        return s["decided"][pid]
    if any(x["id"] == pid for x in s["drafts"]) or pid in s["fixed"]:
        return "review"
    r = run(pid)
    if r is None:
        return "menunggu AI"
    return {"applied": "review", "abstain": "ragu", "empty": "tidak relevan", "budget": "anggaran habis"}.get(
        r["status"], r["status"])


def proposal(pid, s=None):
    """The delta under review: a fixed or edited version if there is one, else the AI's."""
    s = s or load()
    if pid in s["fixed"]:
        return s["fixed"][pid]["delta"]
    for d in s["drafts"]:
        if d["id"] == pid:
            return d["delta"]
    r = run(pid)
    return r.get("delta") if r else None


def carried_inputs(pid, s=None):
    """Input definitions carried by an update: the draft's own, or the file written for a stored document."""
    s = s or load()
    for x in s["drafts"]:
        if x["id"] == pid and x.get("inputs"):
            return x["inputs"]
    p = Path(__file__).resolve().parent / "kb_ext" / "pending" / f"{pid}.json"
    return json.loads(p.read_text(encoding="utf-8"))["defs"] if p.exists() else []


def approve(pid, title, delta, reviewer, note=""):
    s = load()
    s["approved"].append({"id": pid, "title": title, "delta": delta, "reviewer": reviewer, "note": note,
                          "inputs": carried_inputs(pid, s), "when": datetime.now().strftime("%d %b %Y %H:%M")})
    s["decided"][pid] = "disetujui"
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    log(s, f"Approved: {title} (by {reviewer})")
    save(s)


def reject(pid, title, reason):
    s = load()
    s["decided"][pid] = "ditolak"
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    log(s, f"Rejected: {title}. Reason: {reason}")
    save(s)


def add_draft(pid, title, delta, origin, inputs=None):
    s = load()
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    s["drafts"].append({"id": pid, "title": title, "delta": delta, "origin": origin, "inputs": inputs or []})
    s["decided"].pop(pid, None)
    log(s, f"Draft sent to review: {title} ({origin})")
    save(s)


def set_fixed(pid, delta, note, by, llm=None):
    """A new version of the proposal: edited by hand, or repaired by the AI (llm = the model's own output, kept for a
    further repair round)."""
    s = load()
    s["fixed"][pid] = {"delta": delta, "note": note, "by": by, "llm": llm}
    log(s, f"Proposal fixed ({by}): {pid}")
    save(s)


def rollback(n):
    """Keep only the first n updates approved in the app."""
    s = load()
    removed = s["approved"][n:]
    s["approved"] = s["approved"][:n]
    for a in removed:
        s["decided"].pop(a["id"], None)
    log(s, f"Rolled back to the version before: {', '.join(a['title'] for a in removed)}")
    save(s)


# ---------------------------------------------------------------- company data: pay components and saved employees
def add_component(name, key):
    s = load()
    s["catalog"] = [c for c in s["catalog"] if c["name"] != name] + [{"name": name, "key": key}]
    log(s, f"Pay component added: {name}")
    save(s)


def save_employee(name, entry):
    s = load()
    s["employees"][name] = entry
    log(s, f"Employee saved: {name}")
    save(s)


# ---------------------------------------------------------------- chat
def chat_load():
    return json.loads(CHAT.read_text(encoding="utf-8")) if CHAT.exists() else []


def chat_save(msgs):
    WORKSPACE.mkdir(exist_ok=True)
    CHAT.write_text(json.dumps(msgs, ensure_ascii=False, indent=1), encoding="utf-8")


def chat_clear():
    CHAT.unlink(missing_ok=True)


TODAY = date.today()


# ---------------------------------------------------------------- inbox (sistem): uploaded documents and their AI runs
def add_inbox(item):
    s = load()
    s["inbox"] = [x for x in s["inbox"] if x["id"] != item["id"]] + [item]
    s["decided"].pop(item["id"], None)
    s["fixed"].pop(item["id"], None)
    log(s, f"Document received: {item['title']}")
    save(s)


def set_run(pid, relpath, cost):
    s = load()
    for x in s["inbox"]:
        if x["id"] == pid:
            x["run"] = relpath
            x["cost_usd"] = round((x.get("cost_usd") or 0) + cost, 4)
    s["fixed"].pop(pid, None)
    s["decided"].pop(pid, None)
    log(s, f"AI finished reading: {pid} (USD {cost:.3f})")
    save(s)
