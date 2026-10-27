"""Acquisition pipeline with a mock LLM client (Tahap 9 completion criterion: every test with the mock client passes)."""
import copy
import json
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import build_gold  # noqa: E402
from pph21kbs import corpus  # noqa: E402
from pph21kbs.pipeline import llm  # noqa: E402
from pph21kbs.pipeline.convert import to_delta, to_llm  # noqa: E402
from pph21kbs.pipeline.run import Config, run_document  # noqa: E402

PIPELINE = Path(__file__).resolve().parents[1] / "pph21kbs" / "pipeline"


@pytest.fixture(scope="module")
def chain():
    return build_gold.build(check_only=True, side=False)


def _gold(chain, event_id):
    for u in build_gold.collect():
        if u.event_id == event_id:
            d = u.to_json()
            i = [x.update_id for x in chain.updates].index(u.delta_id)
            return d, chain.until(chain.updates[i - 1].update_id)
    raise KeyError(event_id)


def _relevance(event, quote, relevant=True):
    return {"relevant": relevant, "layer": "regulation", "reason": "test",
            "quotes": [{"provision": "Pasal 1", "quote": quote}], "effective_from": None,
            "effective_from_quote": None, "effective_until": None, "effective_until_quote": None, "subjects": []}


def test_converter_round_trip_keeps_gold(chain):
    for u in build_gold.collect():
        d = u.to_json()
        back = to_delta(to_llm(d), d["delta_id"], d.get("event_id"), d["document"])
        assert [e["id"] for e in back["add"]] == [e["id"] for e in d["add"]]
        assert [e["id"] for e in back["change"]] == [e["id"] for e in d["change"]]


def test_gold_candidates_are_applied(chain, tmp_path):
    gold, base = _gold(chain, "D01")
    event = corpus.event("D01")
    quote = gold["add"][0]["source"][0]["quote"]
    ledger = llm.Ledger("test-gold", root=tmp_path)
    client = llm.MockClient(ledger, [_relevance(event, quote)] + [to_llm(gold)] * 2)
    res = run_document(event, base, client, ledger, Config(m=2), run_id="t", out_dir=tmp_path)
    assert res["status"] == "applied"
    assert all(c["passed"] and c["passed_before_repair"] for c in res["candidates"])
    assert [e["id"] for e in res["delta"]["add"]] == [e["id"] for e in gold["add"]]
    assert len(res["groups"]) == 1
    calls = [json.loads(l) for l in (tmp_path / "test-gold" / "calls.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [c["step"] for c in calls] == ["relevance", "draft", "draft"]


def test_irrelevant_document_gives_empty_delta(chain, tmp_path):
    gold, base = _gold(chain, "D08")
    event = corpus.event("D08")
    from pph21kbs.text import pages
    text = " ".join(t for _, t in pages(event.document))
    quote = " ".join(text.split()[40:52])
    ledger = llm.Ledger("test-empty", root=tmp_path)
    client = llm.MockClient(ledger, [_relevance(event, quote, relevant=False)])
    res = run_document(event, base, client, ledger, Config(m=2), run_id="t", out_dir=tmp_path)
    assert res["status"] == "empty" and res["delta"]["add"] == []
    client = llm.MockClient(ledger, [_relevance(event, "this sentence is not in the document at all", False)])
    assert run_document(event, base, client, ledger, Config(m=2), run_id="t", out_dir=tmp_path)["status"] == "abstain"


def test_bad_quote_fails_g2_and_repair_fixes_it(chain, tmp_path):
    gold, base = _gold(chain, "D03")
    event = corpus.event("D03")
    bad = copy.deepcopy(to_llm(gold))
    bad["add"][0]["source"][0]["quote"] = "Penghasilan Tidak Kena Pajak sebesar Rp99.000.000 per tahun"
    ledger = llm.Ledger("test-repair", root=tmp_path)
    client = llm.MockClient(ledger, [_relevance(event, gold["add"][0]["source"][0]["quote"]), bad, to_llm(gold)])
    res = run_document(event, base, client, ledger, Config(m=1), run_id="t", out_dir=tmp_path)
    c = res["candidates"][0]
    assert not c["passed_before_repair"] and c["first_gate_log"]["G2"].startswith("fail")
    assert c["repaired"] and c["passed"] and res["status"] == "applied"
    assert "repair" in client.seen[-1]["user"].lower()
    assert client.seen[-1]["system"] == client.seen[-2]["system"], "repairs reuse the cached system prompt"


def test_tie_abstains(chain, tmp_path):
    gold, base = _gold(chain, "D01")
    event = corpus.event("D01")
    other = copy.deepcopy(to_llm(gold))
    for f in other["add"][0]["fields"]:        # same element, a different (still grounded) PTKP for TK/0
        if f["name"] == "rows":
            rows = json.loads(f["value"])
            for r in rows:
                if r["key"] == "TK/0":
                    r["value"] = 26325000
            f["value"] = json.dumps(rows)
    ledger = llm.Ledger("test-tie", root=tmp_path)
    client = llm.MockClient(ledger, [_relevance(event, gold["add"][0]["source"][0]["quote"]), to_llm(gold), other])
    res = run_document(event, base, client, ledger, Config(m=2, repair_rounds=0), run_id="t", out_dir=tmp_path)
    passed = [c for c in res["candidates"] if c["passed"]]
    assert len(passed) == 2, [c["gate_log"] for c in res["candidates"]]
    assert res["status"] == "abstain" and len(res["groups"]) == 2


def test_budget_guard_stops_calls(tmp_path):
    ledger = llm.Ledger("test-budget", root=tmp_path, total_limit_usd=0.5)
    ledger.log({"cost_usd": 0.6})
    client = llm.MockClient(ledger, [{"x": 1}])
    with pytest.raises(llm.BudgetExceeded):
        client.complete(system="s", prefix=[], user="u", schema={}, schema_name="x", effort="low", step="relevance")


def test_pipeline_does_not_read_gold_or_references():
    forbidden = ("gold_src", "build_gold", "refs", "12_emas", "11_acuan", "07_kasus_uji_resmi", "expected")
    for path in PIPELINE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.strip().startswith(("import", "from")):
                assert not any(f in line for f in forbidden), f"{path.name}: {line}"
