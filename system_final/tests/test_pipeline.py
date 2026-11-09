"""Acquisition pipeline with a mock model client, gate G6, and the impact detector.

The pipeline tests read a sample company policy (examples/documents/SP09.txt) into a temporary workspace and replay
its reference update (data/policies/SP09.json) as the model output.
"""
import copy
import json
from datetime import date

import pytest
from test_engine import SRC, delta, fact, rule, toy_kb

from pph21kbs import config, documents, draft, gates, graph, pipeline
from pph21kbs.kb import apply_delta

POLICY = "SP09"
OMEGA = date(2026, 11, 8)


@pytest.fixture(scope="module")
def seed_kb():
    return graph.read_trig(config.SEED_KB, "K")


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DOCUMENTS", tmp_path / "documents")
    monkeypatch.setattr(config, "CALLS", tmp_path / "calls")
    text = (config.ROOT / "examples" / "documents" / f"{POLICY}.txt").read_text(encoding="utf-8")
    documents.add_document(POLICY, "Sample company regulation", "2023-08-01", text=text, company=True)
    yield tmp_path
    documents.clear_caches()


def reference():
    return json.loads((config.POLICIES / f"{POLICY}.json").read_text(encoding="utf-8"))


def event():
    return pipeline.Event(POLICY, (POLICY,), date(2023, 8, 1), layer="company", title="Sample company regulation")


def relevance(quote, relevant=True):
    return {"relevant": relevant, "layer": "company", "reason": "test",
            "quotes": [{"provision": "Pasal 1", "quote": quote}],
            "effective_from": None, "effective_from_quote": None, "effective_until": None,
            "effective_until_quote": None, "subjects": []}


def run(seed_kb, workspace, outputs, **cfg):
    ledger = draft.Ledger("test", root=workspace / "calls")
    client = draft.MockClient(ledger, outputs)
    res = pipeline.run_document(event(), seed_kb, client, ledger, pipeline.Config(policy_omega=OMEGA, **cfg),
                                run_id="t", out_dir=workspace / "results", policies=(POLICY,))
    return res, client, ledger


def test_converter_round_trip_keeps_every_sample_policy():
    for path in sorted(config.POLICIES.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        back = draft.to_delta(draft.to_llm(d), d["delta_id"], d.get("event_id"), d["document"])
        assert [e["id"] for e in back["add"]] == [e["id"] for e in d["add"]]
        assert [e["id"] for e in back["change"]] == [e["id"] for e in d["change"]]


def test_matching_drafts_are_applied(seed_kb, workspace):
    ref = reference()
    quote = ref["add"][0]["source"][0]["quote"]
    res, _, ledger = run(seed_kb, workspace, [relevance(quote)] + [draft.to_llm(ref)] * 2, m=2)
    assert res["status"] == "proposed", [d["gate_log"] for d in res["drafts"]]
    assert all(d["passed"] and d["passed_before_repair"] for d in res["drafts"])
    assert [e["id"] for e in res["delta"]["add"]] == [e["id"] for e in ref["add"]]
    assert len(res["groups"]) == 1
    steps = [json.loads(line)["step"] for line in ledger.calls.read_text(encoding="utf-8").splitlines()]
    assert steps == ["relevance", "draft", "draft"]


def test_irrelevant_document_gives_an_empty_update(seed_kb, workspace):
    text = " ".join(t for _, t in documents.pages(POLICY))
    quote = " ".join(text.split()[10:22])
    res, _, _ = run(seed_kb, workspace, [relevance(quote, relevant=False)], m=2)
    assert res["status"] == "empty" and res["delta"]["add"] == []
    res, _, _ = run(seed_kb, workspace, [relevance("this sentence is not in the document at all", False)], m=2)
    assert res["status"] == "abstain"


def test_bad_quote_fails_g2_and_the_repair_fixes_it(seed_kb, workspace):
    ref = reference()
    bad = copy.deepcopy(draft.to_llm(ref))
    bad["add"][0]["source"][0]["quote"] = "Iuran jaminan kecelakaan kerja ditetapkan sebesar 9,99% dari upah"
    res, client, _ = run(seed_kb, workspace, [relevance(ref["add"][0]["source"][0]["quote"]), bad,
                                              draft.to_llm(ref)], m=1)
    d = res["drafts"][0]
    assert not d["passed_before_repair"] and d["first_gate_log"]["G2"].startswith("fail")
    assert d["repaired"] and d["passed"] and res["status"] == "proposed"
    assert "repair" in client.seen[-1]["user"].lower()
    assert client.seen[-1]["system"] == client.seen[-2]["system"], "a repair reuses the cached system prompt"


def test_drafts_that_behave_differently_abstain(seed_kb, workspace):
    ref = reference()
    other = copy.deepcopy(draft.to_llm(ref))
    other["add"] = [e for e in other["add"] if e["id"] != "PRS.SP09.JKK_RATE"]
    res, _, _ = run(seed_kb, workspace, [relevance(ref["add"][0]["source"][0]["quote"]), draft.to_llm(ref), other],
                    m=2, repair_rounds=0)
    assert [d["passed"] for d in res["drafts"]] == [True, True], [d["gate_log"] for d in res["drafts"]]
    assert res["status"] == "abstain" and len(res["groups"]) == 2


def test_g6_rejects_an_input_the_payroll_data_does_not_have(seed_kb):
    ref = reference()
    bad = copy.deepcopy(ref)
    bad["add"][0]["expression"] = "0 if hr('attendance_days') >= 0 else 0"
    result = gates.g6(seed_kb.view(OMEGA), bad)
    assert not result.passed and "hr('attendance_days')" in result.messages[0]
    assert gates.g6(seed_kb.view(OMEGA), ref).passed


def test_budget_limit_stops_calls(tmp_path):
    ledger = draft.Ledger("test-budget", root=tmp_path, total_limit_usd=0.5)
    ledger.log({"cost_usd": 0.6, "provider": "mock"})
    client = draft.MockClient(ledger, [{"x": 1}])
    with pytest.raises(draft.BudgetExceeded):
        client.complete(system="s", prefix=[], user="u", schema={}, schema_name="x", effort="low", step="relevance")


# --------------------------------------------------------------------------------------------------------------------
# Impact on company policies (toy knowledge base)
# --------------------------------------------------------------------------------------------------------------------
TOY_OMEGA = date(2022, 12, 31)


def kb_with_policies():
    kb = toy_kb()
    kb = apply_delta(kb, {**delta("PX", issued="2020-06-01", add=[
        fact("bonus_px", output=True),
        rule("PRS.X.BONUS", "bonus_px", "round(gross / 10, 1, 'down')", layer="company", modality="default",
             policy="PX",
             rec="2020-06-01"),
        rule("PRS.X.ALLOW", "allowance", "50000", layer="company", modality="default", policy="PX",
             rec="2020-06-01")]), "document": {"id": "PX", "issued": "2020-06-01"}})
    kb = apply_delta(kb, {**delta("PY", issued="2020-06-01", add=[
        fact("bonus_py", output=True),
        rule("PRS.Y.BONUS", "bonus_py", "tax", layer="company", modality="default", policy="PY",
             rec="2020-06-01", vf="2019-01-01", vu="2019-12-31")]), "document": {"id": "PY", "issued": "2020-06-01"}})
    kb = apply_delta(kb, {**delta("PZ", issued="2020-06-01", add=[
        fact("canteen_pz", output=True),
        rule("PRS.Z.CANTEEN", "canteen_pz", "15000", layer="company", modality="default", policy="PZ",
             rec="2020-06-01")]), "document": {"id": "PZ", "issued": "2020-06-01"}})
    return kb


def test_impact_reads_produces_and_mandatory_overlap():
    kb = kb_with_policies()
    ev = delta("EV", issued="2022-01-10", add=[
        {"kind": "parameter", "id": "PAR.ROUND.2", "name": "round_mode", "value": "half_up",
         "value_type": "category", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC},
        rule("REG.ALLOW.MIN", "allowance", "100000", vf="2022-01-01", rec="2022-01-10")])
    kb = apply_delta(kb, ev)
    facts = pipeline.affected_facts(kb, "EV", TOY_OMEGA)
    assert {"tax", "allowance", "gross", "annual_gross", "annual_tax"} <= set(facts)
    res = pipeline.detect(kb, "EV", ["PX", "PY", "PZ"], TOY_OMEGA)
    assert {"a", "b", "c"} <= res["PX"]["kinds"]
    assert res["PY"]["kinds"] == set(), "PY's rule expired before the update's elements are valid"
    assert res["PZ"]["kinds"] == set()


def test_impact_of_a_constraint_reading_a_policy_fact():
    kb = kb_with_policies()
    ev = delta("EVC", issued="2022-01-10", add=[
        {"kind": "constraint", "id": "CON.CANTEEN", "scope": "period", "assertion": "canteen_pz <= 10000",
         "conflict_code": "C8", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC}])
    kb = apply_delta(kb, ev)
    res = pipeline.detect(kb, "EVC", ["PX", "PZ"], TOY_OMEGA)
    assert res["PZ"]["kinds"] == {"c"}
    assert res["PX"]["kinds"] == set()


def test_impact_of_a_removed_rule_counts_through_its_old_record():
    kb = kb_with_policies()
    ev = delta("EVR", issued="2022-01-10", remove=[{"id": "REG.ALLOW0", "recorded_on": "2022-01-10", "source": SRC}])
    kb = apply_delta(kb, ev)
    res = pipeline.detect(kb, "EVR", ["PX"], TOY_OMEGA)
    assert "b" in res["PX"]["kinds"]


def test_python_detector_equals_the_sparql_queries():
    """detect() and the SPARQL specification in spec/queries give the same facts and the same hits."""
    for ev in (delta("EV", issued="2022-01-10", add=[
                   {"kind": "parameter", "id": "PAR.ROUND.2", "name": "round_mode", "value": "half_up",
                    "value_type": "category", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC},
                   rule("REG.ALLOW.MIN", "allowance", "100000", vf="2022-01-01", rec="2022-01-10")]),
               delta("EVC", issued="2022-01-10", add=[
                   {"kind": "constraint", "id": "CON.CANTEEN", "scope": "period", "assertion": "canteen_pz <= 10000",
                    "conflict_code": "C8", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC}]),
               delta("EVR", issued="2022-01-10", remove=[{"id": "REG.ALLOW0", "recorded_on": "2022-01-10",
                                                           "source": SRC}])):
        kb = apply_delta(kb_with_policies(), ev)
        uid = ev["delta_id"]
        sparql, facts = pipeline.detect_sparql(kb, uid, ["PX", "PY", "PZ"], TOY_OMEGA)
        assert pipeline.affected_facts(kb, uid, TOY_OMEGA) == facts
        assert pipeline.detect(kb, uid, ["PX", "PY", "PZ"], TOY_OMEGA) == sparql
