"""The fixed demo state and everything done on top of it.

Initial state: the gold knowledge base of the research up to the 2025 JP wage cap (recorded 27 Feb 2025), no company
policy installed, and eight documents waiting, each with the real result of the AI from the research runs
(experiments/*/results). Everything done during a demo (approved updates, drafts, rejections, uploads, chat) is kept in
mini_demo/mockup/workspace/. Reset deletes that folder, so the system is back in the initial state.
"""
import json
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

WORKSPACE = Path(__file__).resolve().parent / "workspace"
STATE = WORKSPACE / "state.json"
CHAT = WORKSPACE / "chat.json"
EXP = ROOT / "experiments"
BASE_UPDATE = "GOLD-E08"
BASE_LABEL = "27 Februari 2025"

# documents waiting in the initial state: (id, kind, run file, what the research found)
PENDING = [
    {"id": "E13", "doc": "PER-11-PJ-2025", "kind": "regulasi", "run": "e2-regulasi/results/E13.json",
     "research": "benar", "why": "Aturan pembulatan yang berlaku surut: hitungan lama berubah bila dihitung ulang."},
    {"id": "E09", "doc": "PP-36-2025", "kind": "regulasi", "run": "e2-regulasi/results/E09.json",
     "research": "benar", "why": "Keringanan iuran JKK untuk industri padat karya."},
    {"id": "E10", "doc": "PMK-72-2025", "kind": "regulasi", "run": "e2-regulasi/results/E10.json",
     "research": "benar", "why": "DTP sektor pariwisata; menyentuh kebijakan perusahaan hotel."},
    {"id": "E11", "doc": "PMK-105-2025", "kind": "regulasi", "run": "e2-regulasi/results/E11.json",
     "research": "salah", "why": "Bandingkan kartu 'Penghasilan bruto tetap dan teratur' dan 'Penghasilan tetap bulan "
                                 "pertama' dengan aturan 2025 yang tampil di bawahnya: AI menghilangkan rumah dan mobil "
                                 "dinas dari uji batas Rp10 juta, dan menghilangkan penghasilan menurut kontrak untuk "
                                 "pegawai baru. Minta AI perbaiki dengan catatan itu."},
    {"id": "E12", "doc": "BPJSTK-JP-2026", "kind": "regulasi", "run": "e2-regulasi/results/E12.json",
     "research": "benar", "why": "Perubahan angka tahunan, yang paling sering terjadi."},
    {"id": "SP14", "doc": "SP14", "kind": "kebijakan", "run": "e2-sintetis/results/SP14.json",
     "research": "tidak bisa dinilai", "why": "THR dihitung dari masa kerja: kolom data HR baru muncul di kalkulator."},
    {"id": "PKB-WIKA-2025", "doc": "PKB-WIKA-2025", "kind": "kebijakan", "run": "e2-pkb/results/PKB-WIKA-2025.json",
     "research": "ragu", "why": "Versi usulan AI tidak sepakat; dikerjakan manual atau dengan bantuan AI."},
    {"id": "P05", "doc": "PMK-81-2024", "kind": "regulasi", "run": "e2-pengecoh/results/P05.json",
     "research": "tidak relevan", "why": "Dokumen administrasi Coretax: tidak mengubah perhitungan."},
]
PENDING_BY_ID = {p["id"]: p for p in PENDING}


# ---------------------------------------------------------------- state file
def _empty():
    return {"approved": [], "decided": {}, "drafts": [], "uploads": [], "log": [], "fixed": {}, "catalog": [],
            "employees": {}}


def load():
    if STATE.exists():
        return {**_empty(), **json.loads(STATE.read_text(encoding="utf-8"))}
    return _empty()


def save(s):
    WORKSPACE.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def log(s, text):
    s["log"].insert(0, {"when": datetime.now().strftime("%d/%m %H:%M"), "what": text})


def reset():
    shutil.rmtree(WORKSPACE, ignore_errors=True)
    keep = {"_pages"}
    for k in list(st.session_state.keys()):
        if k not in keep:
            del st.session_state[k]
    _kb_cached.clear()
    _kb_prefix.clear()


# ---------------------------------------------------------------- knowledge base
@st.cache_resource(show_spinner="Memuat knowledge base ...")
def gold():
    return build_gold.load_graph()


@st.cache_resource
def base():
    return gold().until(BASE_UPDATE)


@st.cache_resource(show_spinner="Menerapkan pembaruan demo ...")
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


# ---------------------------------------------------------------- stored AI results
@st.cache_data
def run(pid):
    p = PENDING_BY_ID.get(pid)
    return json.loads((EXP / p["run"]).read_text(encoding="utf-8")) if p else None


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
    return {"applied": "review", "abstain": "ragu", "empty": "tidak relevan"}.get(r["status"], r["status"]) if r else "review"


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
                          "inputs": carried_inputs(pid, s), "when": datetime.now().strftime("%d/%m/%Y %H:%M")})
    s["decided"][pid] = "disetujui"
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    log(s, f"Disetujui: {title} (oleh {reviewer})")
    save(s)


def reject(pid, title, reason):
    s = load()
    s["decided"][pid] = "ditolak"
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    log(s, f"Ditolak: {title}. Alasan: {reason}")
    save(s)


def add_draft(pid, title, delta, origin, inputs=None):
    s = load()
    s["drafts"] = [d for d in s["drafts"] if d["id"] != pid]
    s["drafts"].append({"id": pid, "title": title, "delta": delta, "origin": origin, "inputs": inputs or []})
    s["decided"].pop(pid, None)
    log(s, f"Draf masuk review: {title} ({origin})")
    save(s)


def set_fixed(pid, delta, note, by):
    s = load()
    s["fixed"][pid] = {"delta": delta, "note": note, "by": by}
    log(s, f"Usulan diperbaiki ({by}): {pid}")
    save(s)


def rollback(n):
    """Keep only the first n approved updates of the demo."""
    s = load()
    removed = s["approved"][n:]
    s["approved"] = s["approved"][:n]
    for a in removed:
        s["decided"].pop(a["id"], None)
    log(s, f"Dikembalikan ke versi sebelum: {', '.join(a['title'] for a in removed)}")
    save(s)


# ---------------------------------------------------------------- company data: pay components and saved employees
def add_component(name, key):
    s = load()
    s["catalog"] = [c for c in s["catalog"] if c["name"] != name] + [{"name": name, "key": key}]
    log(s, f"Komponen gaji ditambahkan: {name}")
    save(s)


def save_employee(name, entry):
    s = load()
    s["employees"][name] = entry
    log(s, f"Pegawai disimpan: {name}")
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
