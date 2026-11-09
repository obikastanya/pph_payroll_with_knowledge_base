"""Knowledge graph round trip, SHACL validation (gate G1), and static consistency checks (gate G3)."""
from dataclasses import replace
from datetime import date
from fractions import Fraction

import pytest

from pph21kbs import config, consistency, graph
from pph21kbs.expr import Expression
from pph21kbs.kb import KnowledgeBase, Parameter, Source


def seed():
    return graph.read_trig(config.SEED_KB, "K")


# --------------------------------------------------------------------------------------------------------------------
# RDF round trip and SHACL
# --------------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def seed_kb():
    return seed()


def _mutate(kb, element_id, **changes):
    """Copy of kb whose latest record of element_id has the given fields changed."""
    target = kb.history(element_id)[-1]
    records = [replace(r, **changes) if r is target else r for r in kb.records]
    return KnowledgeBase(records, kb.updates, kb.documents, kb.name, kb.adoptions)


def _messages(kb):
    return {m for _, m in graph.validate(kb)}


def test_round_trip_keeps_records(seed_kb, tmp_path):
    path = tmp_path / "kb.trig"
    graph.write_trig(seed_kb, path)
    back = graph.read_trig(path)
    assert back.fingerprint() == seed_kb.fingerprint()
    assert [u for u in back.updates] == [u for u in seed_kb.updates]
    for a, b in zip(seed_kb.records, back.records):
        assert type(a) is type(b) and a.id == b.id and a.seq == b.seq
        if hasattr(a, "rows"):
            assert a.rows == b.rows
        if isinstance(a, Parameter):
            assert a.value == b.value and type(a.value) is type(b.value)


def test_seed_conforms(seed_kb):
    assert graph.validate(seed_kb) == []


@pytest.mark.parametrize("element_id,changes,message", [
    ("REG.TER.RUNNING", {"valid_from": date(2024, 1, 2)}, "G1: validFrom must be the first day of a month"),
    ("REG.TER.RUNNING", {"valid_until": date(2024, 2, 28)}, "G1: validUntil must be the last day of a month"),
    ("REG.TER.RUNNING", {"valid_until": date(2023, 12, 31)}, "G1: validUntil must not be before validFrom"),
    ("REG.TER.RUNNING", {"layer": "company", "policy": "SP09", "id": "PRS.X"},
     "G1: a company rule must not be mandatory"),
    ("REG.TER.RUNNING", {"overrides": ("REG.NOT.THERE",)}, "G1: overrides must name an existing element id"),
    ("REG.TER.RUNNING", {"scope": "year"}, "G1: rule scope must equal the scope of the fact it produces"),
    ("REG.TER.RUNNING", {"id": "TER.RUNNING"},
     "G1: regulation rule ids start with REG., company rule ids with PRS."),
    ("REG.TER.RUNNING", {"produces": "no_such_fact"}, "G1: produces must name a fact of the vocabulary"),
    ("REG.TER.RUNNING", {"source": (Source("PP-58-2023", "Pasal 2", ""),)}, "G1: quote text must not be empty"),
    ("REG.TER.RUNNING", {"source": (Source("PP-99-2099", "Pasal 1", "teks apa saja"),)},
     "G1: provision must be part of a known document"),
    ("REG.TER.RUNNING", {"source": ()}, "G1: every record needs at least one source quote"),
    ("PAR.JP_WAGE_CAP.2024", {"value": Fraction(1, 3)},
     "G1: parameter value does not have the type its valueType states"),
    ("PAR.JP_WAGE_CAP.2024", {"id": "JP_WAGE_CAP.2024"}, "G1: parameter ids start with PAR."),
    ("TAB.TER_MONTHLY.2024", {"rows": ()}, "G1: a table needs at least one row"),
])
def test_shape_catches_mutation(seed_kb, element_id, changes, message):
    assert message in _messages(_mutate(seed_kb, element_id, **changes))


def test_company_rule_without_policy(seed_kb):
    kb = _mutate(seed_kb, "REG.TER.RUNNING", layer="company", modality="default", policy=None, id="PRS.X")
    assert "G1: a company rule needs its policy document" in _messages(kb)


def test_bracket_row_order(seed_kb):
    rows = list(seed_kb.history("TAB.TER_MONTHLY.2024")[-1].rows)
    rows[3] = dict(rows[3], upper=rows[3]["lower"])
    assert "G1: bracket or progressive row with upper <= lower" in _messages(
        _mutate(seed_kb, "TAB.TER_MONTHLY.2024", rows=tuple(rows)))


# --------------------------------------------------------------------------------------------------------------------
# Static consistency
# --------------------------------------------------------------------------------------------------------------------
OMEGA = date(2026, 10, 27)


def _with(kb, *records):
    """kb plus extra records appended to the last update."""
    seq = kb.next_seq
    last = kb.updates[-1]
    recs = [replace(r, seq=seq + i, update_id=last.update_id) for i, r in enumerate(records)]
    return KnowledgeBase(kb.records + tuple(recs), kb.updates, kb.documents, kb.name, kb.adoptions)


def _rule(kb, rid, **changes):
    base = kb.history("REG.TER.RUNNING")[-1]
    return replace(base, id=rid, **changes)


def _kinds(kb):
    return {f.kind for f in consistency.check(kb, OMEGA).findings}


def test_seed_has_no_errors(seed_kb):
    for omega in (date(2022, 12, 31), date(2024, 12, 31), OMEGA):
        assert consistency.check(seed_kb, omega).ok


def test_cycle(seed_kb):
    kb = _mutate(seed_kb, "REG.TER.CATEGORY", expression=Expression("lookup('ter_category', ptkp_status_effective)"
                                                                 " if pph21_running >= 0 else 'A'"))
    rep = consistency.check(kb, OMEGA)
    assert any(f.kind == "cycle" for f in rep.errors)


def test_fixed_point_rule_breaks_cycle(seed_kb):
    assert not any(f.kind == "cycle" for f in consistency.check(seed_kb, OMEGA).findings)


def test_override_cycle(seed_kb):
    kb = _mutate(seed_kb, "REG.YEAR.REFUND", overrides=("REG.DTP.REFUND",))
    assert "override_cycle" in _kinds(kb)


def test_dangling_after_early_closure(seed_kb):
    kb = _mutate(seed_kb, "REG.TER.CATEGORY", valid_until=date(2024, 6, 30))
    rep = consistency.check(kb, OMEGA)
    assert any(f.kind == "dangling" and f.fact == "ter_category" for f in rep.errors)


def test_dangling_parameter(seed_kb):
    kb = _mutate(seed_kb, "PAR.DTP_FIXED_INCOME_CAP.2026", valid_from=date(2026, 3, 1))
    assert any(f.kind == "dangling" and f.fact == "dtp_fixed_income_cap" for f in consistency.check(kb, OMEGA).errors)


def test_unknown_names(seed_kb):
    kb = _mutate(seed_kb, "REG.TER.RUNNING", expression=Expression("round(param('no_param') * no_fact, 1, 'down')"))
    found = {(f.kind, f.fact) for f in consistency.check(kb, OMEGA).errors}
    assert ("unknown_name", "no_param") in found and ("unknown_name", "no_fact") in found


def test_redundant(seed_kb):
    assert "redundant" in _kinds(_with(seed_kb, _rule(seed_kb, "REG.TER.RUNNING.COPY")))


def test_subsumed(seed_kb):
    narrow = _rule(seed_kb, "REG.TER.RUNNING.NARROW", valid_from=date(2025, 1, 1), valid_until=date(2025, 12, 31),
                   condition=Expression("not is_final_period and month > 3"))
    assert "subsumed" in _kinds(_with(seed_kb, narrow))


def test_potential_conflict_and_exclusive_conditions(seed_kb):
    other = _rule(seed_kb, "REG.TER.RUNNING.OTHER", expression=Expression("round(ter_rate * gross_income, 1, 'up')"))
    assert "potential_conflict" in _kinds(_with(seed_kb, other))
    exclusive = _rule(seed_kb, "REG.TER.RUNNING.FINAL", expression=Expression("0"),
                      condition=Expression("is_final_period"))
    assert "potential_conflict" not in _kinds(_with(seed_kb, exclusive))


def test_dead_rule_beaten_by_unconditional_rule(seed_kb):
    low = _rule(seed_kb, "REG.TER.RUNNING.LOW", modality="default", condition=None,
                expression=Expression("0"), valid_from=date(2024, 1, 1), valid_until=date(2024, 12, 31))
    high = _rule(seed_kb, "REG.TER.RUNNING.HIGH", condition=None, valid_from=date(2024, 1, 1), overrides=())
    kb = _with(seed_kb, low, high)
    assert any(f.kind == "dead" and f.ids[0] == "REG.TER.RUNNING.LOW" for f in consistency.check(kb, OMEGA).findings)
