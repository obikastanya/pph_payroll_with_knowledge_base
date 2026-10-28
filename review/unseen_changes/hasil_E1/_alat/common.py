"""Shared helpers for E1 (RQ1). Reads the frozen system; never modifies it."""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(REPO / "system"), str(REPO / "system" / "tools")]
OUT = Path(__file__).resolve().parents[1]
SEALED = REPO / "review" / "unseen_changes" / "sealed"

_chain = None


def chain():
    global _chain
    if _chain is None:
        import build_gold
        _chain = build_gold.load_graph()
    return _chain


def base_at(date_text):
    import build_gold
    return build_gold.prefix_at(chain(), date_text)
