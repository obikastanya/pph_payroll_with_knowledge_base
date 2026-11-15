"""The gold knowledge base (12_emas): the regulation chain, and the knowledge base before and after an event."""
import json
from datetime import timedelta
from functools import lru_cache

from . import DATA

from pph21kbs import graph  # noqa: E402
from pph21kbs.kb import apply_delta  # noqa: E402

GOLD = DATA / "12_emas"


@lru_cache(maxsize=1)
def chain():
    """The gold regulation chain as one bitemporal knowledge base (background and events through E12)."""
    return graph.read_trig(GOLD / "kb.trig", "K*")


PROSPECTIVE = DATA / "15_set_prospektif" / "units"


@lru_cache(maxsize=None)
def delta(update_id):
    """A gold update of 12_emas, or the gold of a prospective unit (its spec.json)."""
    path = GOLD / "delta" / f"{update_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads((PROSPECTIVE / update_id / "spec.json").read_text(encoding="utf-8"))["gold"]


def exists(update_id):
    return (GOLD / "delta" / f"{update_id}.json").exists() or (PROSPECTIVE / update_id / "spec.json").exists()


def _chain_ids():
    return [u.update_id for u in chain().updates]


def base_before(event):
    """The gold knowledge base the event's document is applied to: the chain before the event's own gold update, or,
    for a document without one (a distractor), the chain as known on its issue date."""
    ids = _chain_ids()
    if event.gold in ids:
        i = ids.index(event.gold)
        return chain().until(ids[i - 1])
    return chain().known_on(event.issued)


def empty(event_id, document, issued):
    """An update that changes nothing, as the gold of a distractor or the result of a 'not relevant' decision."""
    return {"delta_id": f"EMPTY-{event_id}", "event_id": event_id, "document": {"id": document, "issued": str(issued)},
            "relevant": False, "add": [], "change": [], "remove": [], "note": ""}


def expected_delta(event):
    """The gold update of an event; an empty update for a document that changes nothing."""
    return delta(event.gold) if event.gold else empty(event.id, event.document, event.issued)


def omegas(event):
    """The two knowledge dates an update is scored at: the day before the document was issued, and its issue day."""
    return (event.issued - timedelta(days=1), event.issued)


def recorded(update, day):
    """The update with every record recorded on `day`: a company document is known from the day it is uploaded
    (company records apply whatever the knowledge date, so this changes no result, only what gate G2 expects)."""
    d = json.loads(json.dumps(update))
    for op in ("add", "change", "remove"):
        for rec in d.get(op, []):
            rec["recorded_on"] = str(day)
    return d


def apply(base, update, update_id=None):
    return apply_delta(base, update, update_id=update_id or update.get("delta_id"))
