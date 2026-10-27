"""Show what an acquirer of one event sees: the base knowledge base (gold chain before the event, or the full
regulation chain for a policy) as vocabulary and relevant records, and the document text with page markers.

    env\\Scripts\\python system\\tools\\kb_context.py E06            # context + selected segments
    env\\Scripts\\python system\\tools\\kb_context.py E06 --full     # context + whole locked text
    env\\Scripts\\python system\\tools\\kb_context.py SP03

Used by the second reader of the gold (Tahap 7): the same view the pipeline gives the LLM, without the gold Delta.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_gold  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.pipeline import context, select  # noqa: E402
from pph21kbs.text import pages  # noqa: E402


def base_for(event, chain):
    if event.layer == "company":
        return chain, date(2026, 10, 27)
    ids = [u.update_id for u in chain.updates]
    gold = next((u for u in build_gold.collect() if u.event_id == event.id), None)
    if gold is not None:
        i = ids.index(gold.delta_id)
        return (chain.until(ids[i - 1]) if i else chain), event.issued
    return build_gold.prefix_at(chain, event.issued.isoformat()), event.issued


def main():
    eid = sys.argv[1]
    full = "--full" in sys.argv
    ev = corpus.event(eid)
    chain = build_gold.build(check_only=True, side=False)
    base, omega = base_for(ev, chain)
    view = base.view(omega)
    if full:
        text = "\n\n".join(f"=== DOCUMENT {d} ===\n" + "\n".join(f"=== PDF hlm. {n} ===\n{t}" for n, t in pages(d))
                           for d in ev.documents)
    else:
        text = "\n\n".join(select.render(select.select(d, view)) for d in ev.documents)
    print(f"EVENT {ev.id} | documents {', '.join(ev.documents)} | issued {ev.issued} | layer {ev.layer} | "
          f"knowledge date of the base {omega}\n")
    print(context.context_text(view, text))
    print("\n" + text)


if __name__ == "__main__":
    main()
