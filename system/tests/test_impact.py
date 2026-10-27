"""Static impact detector (RQ4): labels (a), (b), (c) from the SPARQL queries on a toy knowledge base."""
from datetime import date

from pph21kbs import impact
from pph21kbs.kb import apply_delta

from test_engine_core import SRC, delta, fact, rule, toy_kb

OMEGA = date(2022, 12, 31)


def kb_with_policies():
    kb = toy_kb()
    kb = apply_delta(kb, {**delta("PX", issued="2020-06-01", add=[
        fact("bonus_px", output=True),
        rule("PRS.X.BONUS", "bonus_px", "round(gross / 10, 1, 'down')", layer="company", modality="default", policy="PX",
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


def test_reads_produces_and_mandatory_overlap():
    kb = kb_with_policies()
    ev = delta("EV", issued="2022-01-10", add=[
        {"kind": "parameter", "id": "PAR.ROUND.2", "name": "round_mode", "value": "half_up",
         "value_type": "category", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC},
        rule("REG.ALLOW.MIN", "allowance", "100000", vf="2022-01-01", rec="2022-01-10")])
    kb = apply_delta(kb, ev)
    facts = impact.affected_facts(impact.impact_graph(kb, "EV", OMEGA))
    assert {"tax", "allowance", "gross", "annual_gross", "annual_tax"} <= set(facts)
    res = impact.detect(kb, "EV", ["PX", "PY", "PZ"], OMEGA)
    assert res["PX"]["kinds"] == {"a", "b", "c"}
    assert res["PY"]["kinds"] == set(), "PY's rule expired before the Delta's elements are valid"
    assert res["PZ"]["kinds"] == set()
    assert impact.flag_all(kb, "EV", ["PX", "PY", "PZ"], OMEGA) == {"PX": True, "PY": True, "PZ": False}


def test_constraint_reading_policy_fact():
    kb = kb_with_policies()
    ev = delta("EVC", issued="2022-01-10", add=[
        {"kind": "constraint", "id": "CON.CANTEEN", "scope": "period", "assertion": "canteen_pz <= 10000",
         "conflict_code": "C8", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC}])
    kb = apply_delta(kb, ev)
    res = impact.detect(kb, "EVC", ["PX", "PZ"], OMEGA)
    assert res["PZ"]["kinds"] == {"c"}
    assert res["PX"]["kinds"] == set()


def test_removed_rule_counts_through_its_old_record():
    kb = kb_with_policies()
    ev = delta("EVR", issued="2022-01-10", remove=[{"id": "REG.ALLOW0", "recorded_on": "2022-01-10", "source": SRC}])
    kb = apply_delta(kb, ev)
    res = impact.detect(kb, "EVR", ["PX"], OMEGA)
    assert "b" in res["PX"]["kinds"]



def test_graphdb_backend_gives_the_same_labels():
    """The RQ4 evaluation runs the same queries in GraphDB; both engines must agree (skipped without GraphDB)."""
    import pytest
    from pph21kbs.kb import graphdb
    if not graphdb.available():
        pytest.skip("GraphDB not running")
    events = [
        delta("EV", issued="2022-01-10", add=[
            {"kind": "parameter", "id": "PAR.ROUND.2", "name": "round_mode", "value": "half_up",
             "value_type": "category", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC},
            rule("REG.ALLOW.MIN", "allowance", "100000", vf="2022-01-01", rec="2022-01-10")]),
        delta("EVC", issued="2022-01-10", add=[
            {"kind": "constraint", "id": "CON.CANTEEN", "scope": "period", "assertion": "canteen_pz <= 10000",
             "conflict_code": "C8", "valid_from": "2022-01-01", "recorded_on": "2022-01-10", "source": SRC}]),
        delta("EVR", issued="2022-01-10", remove=[{"id": "REG.ALLOW0", "recorded_on": "2022-01-10", "source": SRC}])]
    pols = ["PX", "PY", "PZ"]
    for ev in events:
        kb = apply_delta(kb_with_policies(), ev)
        uid = ev["delta_id"]
        assert impact.detect(kb, uid, pols, OMEGA, remote=True) == impact.detect(kb, uid, pols, OMEGA)
        assert impact.flag_all(kb, uid, pols, OMEGA, remote=True) == impact.flag_all(kb, uid, pols, OMEGA)
