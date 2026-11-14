"""Static consistency (G3) and anomaly checker: each anomaly kind is detected on a mutated gold knowledge base."""
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import build_gold  # noqa: E402
from pph21kbs import static  # noqa: E402
from pph21kbs.expr import Expression  # noqa: E402
from pph21kbs.kb import KnowledgeBase, Rule  # noqa: E402

OMEGA = date(2026, 10, 27)


@pytest.fixture(scope="module")
def gold():
    return build_gold.build(check_only=True)


def _with(kb, *records):
    """kb plus extra records appended to the last update."""
    seq = kb.next_seq
    last = kb.updates[-1]
    recs = [replace(r, seq=seq + i, update_id=last.update_id) for i, r in enumerate(records)]
    return KnowledgeBase(kb.records + tuple(recs), kb.updates, kb.documents, kb.name, kb.adoptions)


def _mutate(kb, element_id, **changes):
    target = kb.history(element_id)[-1]
    return KnowledgeBase([replace(r, **changes) if r is target else r for r in kb.records], kb.updates,
                         kb.documents, kb.name, kb.adoptions)


def _rule(kb, rid, **changes):
    base = kb.history("REG.TER.RUNNING")[-1]
    return replace(base, id=rid, **changes)


def _kinds(kb):
    return {f.kind for f in static.check(kb, OMEGA).findings}


def test_gold_has_no_errors(gold):
    for omega in (date(2022, 12, 31), date(2024, 12, 31), OMEGA):
        assert static.check(gold, omega).ok


def test_cycle(gold):
    kb = _mutate(gold, "REG.TER.CATEGORY", expression=Expression("lookup('ter_category', ptkp_status_effective)"
                                                                 " if pph21_running >= 0 else 'A'"))
    rep = static.check(kb, OMEGA)
    assert any(f.kind == "cycle" for f in rep.errors)


def test_fixed_point_rule_breaks_cycle(gold):
    assert not any(f.kind == "cycle" for f in static.check(gold, OMEGA).findings)


def test_override_cycle(gold):
    kb = _mutate(gold, "REG.YEAR.REFUND", overrides=("REG.DTP.REFUND",))
    assert "override_cycle" in _kinds(kb)


def test_dangling_after_early_closure(gold):
    kb = _mutate(gold, "REG.TER.CATEGORY", valid_until=date(2024, 6, 30))
    rep = static.check(kb, OMEGA)
    assert any(f.kind == "dangling" and f.fact == "ter_category" for f in rep.errors)


def test_dangling_parameter(gold):
    kb = _mutate(gold, "PAR.DTP_FIXED_INCOME_CAP.2026", valid_from=date(2026, 3, 1))
    assert any(f.kind == "dangling" and f.fact == "dtp_fixed_income_cap" for f in static.check(kb, OMEGA).errors)


def test_unknown_names(gold):
    kb = _mutate(gold, "REG.TER.RUNNING", expression=Expression("round(param('no_param') * no_fact, 1, 'down')"))
    found = {(f.kind, f.fact) for f in static.check(kb, OMEGA).errors}
    assert ("unknown_name", "no_param") in found and ("unknown_name", "no_fact") in found


def test_redundant(gold):
    assert "redundant" in _kinds(_with(gold, _rule(gold, "REG.TER.RUNNING.COPY")))


def test_subsumed(gold):
    narrow = _rule(gold, "REG.TER.RUNNING.NARROW", valid_from=date(2025, 1, 1), valid_until=date(2025, 12, 31),
                   condition=Expression("not is_final_period and month > 3"))
    assert "subsumed" in _kinds(_with(gold, narrow))


def test_potential_conflict_and_exclusive_conditions(gold):
    other = _rule(gold, "REG.TER.RUNNING.OTHER", expression=Expression("round(ter_rate * gross_income, 1, 'up')"))
    assert "potential_conflict" in _kinds(_with(gold, other))
    exclusive = _rule(gold, "REG.TER.RUNNING.FINAL", expression=Expression("0"), condition=Expression("is_final_period"))
    assert "potential_conflict" not in _kinds(_with(gold, exclusive))


def test_dead_rule_beaten_by_unconditional_rule(gold):
    low = _rule(gold, "REG.TER.RUNNING.LOW", modality="default", condition=None,
                expression=Expression("0"), valid_from=date(2024, 1, 1), valid_until=date(2024, 12, 31))
    high = _rule(gold, "REG.TER.RUNNING.HIGH", condition=None, valid_from=date(2024, 1, 1), overrides=())
    kb = _with(gold, low, high)
    assert any(f.kind == "dead" and f.ids[0] == "REG.TER.RUNNING.LOW" for f in static.check(kb, OMEGA).findings)
