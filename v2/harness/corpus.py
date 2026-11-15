"""Events of the study: real regulations 2023-2026, distractors, development events, and company documents."""
import csv
from dataclasses import dataclass, field
from datetime import date

from . import DATA

EVENTS_CSV = DATA / "09_korpus_peristiwa" / "peristiwa.csv"
DOCUMENTS_CSV = DATA / "13_teks" / "dokumen.csv"
CHAIN_CSV = DATA / "12_emas" / "rantai.csv"
SIDE_CSV = DATA / "12_emas" / "sisi.csv"
PARTS = {"uji": "test", "pengecoh": "distractor", "pengembangan": "dev"}


@dataclass(frozen=True)
class Event:
    id: str
    part: str                       # test | distractor | dev | fictive | company
    relevant: bool
    documents: tuple
    issued: date
    effective_from: date | None
    effective_until: date | None
    layer: str = "regulation"
    title: str = ""
    gold: str | None = None         # gold update id (12_emas), None for a distractor
    extra: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def document(self):
        return self.documents[0]


def _date(text):
    return date.fromisoformat(text) if text else None


def _rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def documents_by_event():
    out = {}
    for r in _rows(DOCUMENTS_CSV):
        if r["event"]:
            out.setdefault(r["event"], []).append(r["id"])
    return out


def gold_updates():
    """Event id -> gold update id, for the chain and the side updates."""
    out = {r["event_id"]: r["update_id"] for r in _rows(CHAIN_CSV) if r["event_id"]}
    out.update({r["event_id"]: r["update_id"] for r in _rows(SIDE_CSV) if r["event_id"]})
    return out


def regulation_events():
    docs, gold = documents_by_event(), gold_updates()
    out = []
    for r in _rows(EVENTS_CSV):
        relevant = r["relevan"] == "ya"
        out.append(Event(r["id"], PARTS[r["bagian"]], relevant, tuple(docs.get(r["id"], ())),
                         _date(r["tanggal_terbit"]), _date(r["berlaku_mulai"]), _date(r["berlaku_sampai"]),
                         title=r["judul"], gold=gold.get(r["id"]) if relevant else None))
    return out


def test_stream():
    """The 13 real regulations and 20 distractors in the order of their issue dates (the gold chain's order for
    events issued on the same day)."""
    order = {r["event_id"]: int(r["seq"]) for r in _rows(CHAIN_CSV) if r["event_id"]}
    evs = [e for e in regulation_events() if e.part in ("test", "distractor")]
    return sorted(evs, key=lambda e: (e.issued, order.get(e.id, 10_000), e.id))
