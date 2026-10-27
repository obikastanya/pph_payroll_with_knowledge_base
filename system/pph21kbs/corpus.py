"""Event table (format_data.md 5): regulation events from dataset/09_korpus_peristiwa/peristiwa.csv, fictive
development regulations from fiktif/INDEX.csv, and policy events from dataset/10_kebijakan_perusahaan/
peristiwa_kebijakan.csv, each mapped to its locked document(s) in dataset/13_teks."""
import csv
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache

from .config import REPO
from .text import registry

EVENTS = REPO / "dataset" / "09_korpus_peristiwa" / "peristiwa.csv"
FICTIVE = REPO / "dataset" / "09_korpus_peristiwa" / "fiktif" / "INDEX.csv"
POLICY_EVENTS = REPO / "dataset" / "10_kebijakan_perusahaan" / "peristiwa_kebijakan.csv"


@dataclass(frozen=True)
class Event:
    id: str
    part: str                 # uji, pengecoh, pengembangan, fiktif, kebijakan_uji, kebijakan_sintetis, ...
    relevant: bool
    documents: tuple          # registry ids of the locked texts (usually one)
    issued: date              # t_terbit
    effective_from: date | None
    effective_until: date | None
    change_types: str = ""
    layer: str = "regulation"
    title: str = ""
    order: int = 0            # row order in the table (ties on issue date)
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def document(self):
        return self.documents[0]


def _d(text):
    text = (text or "").strip()
    return date.fromisoformat(text) if text and text != "-" else None


def _docs_of(event_id):
    return tuple(sorted(r["id"] for r in registry().values() if r.get("event") == event_id))


@lru_cache(maxsize=1)
def regulation_events():
    out = []
    with open(EVENTS, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            docs = _docs_of(r["id"])
            if not docs:
                raise ValueError(f"event {r['id']} has no locked document in dataset/13_teks/dokumen.csv")
            out.append(Event(r["id"], r["bagian"], r["relevan"] == "ya", docs, _d(r["tanggal_terbit"]),
                             _d(r["berlaku_mulai"]), _d(r["berlaku_sampai"]), r["jenis_perubahan"],
                             "regulation", r["judul"], i))
    return tuple(out)


@lru_cache(maxsize=1)
def fictive_events():
    out = []
    with open(FICTIVE, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            docs = _docs_of(r["id"])
            issued = _d(r["diundangkan"]) or _d(r["ditetapkan"])
            out.append(Event(r["id"], "fiktif", True, docs, issued, _d(r["berlaku_mulai"]), _d(r["berlaku_sampai"]),
                             f"{r['jenis_utama']}", "regulation", r["judul"], i))
    return tuple(out)


@lru_cache(maxsize=1)
def policy_events():
    if not POLICY_EVENTS.exists():
        return ()
    out = []
    with open(POLICY_EVENTS, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            out.append(Event(r["id"], r["bagian"], True, (r["dokumen"],), _d(r["tanggal_dokumen"]),
                             _d(r["berlaku_mulai"]), _d(r["berlaku_sampai"]), r.get("kode_konflik", ""),
                             "company", r.get("judul", ""), i, extra=dict(r)))
    return tuple(out)


def chain_order(events):
    """Regulation sequence order: issue date, then table row order (akuisisi.md Definition 4)."""
    return sorted(events, key=lambda e: (e.issued, e.order))


def event(event_id):
    for e in regulation_events() + fictive_events() + policy_events():
        if e.id == event_id:
            return e
    raise KeyError(event_id)
