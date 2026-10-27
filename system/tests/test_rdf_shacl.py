"""Knowledge graph round trip and SHACL gate G1: the gold chain conforms, and each G1 condition catches a mutation."""
import sys
from dataclasses import replace
from datetime import date
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import build_gold  # noqa: E402
from pph21kbs.expr import Expression  # noqa: E402
from pph21kbs.kb import KnowledgeBase, Parameter, Rule, Source, rdf, shacl  # noqa: E402


@pytest.fixture(scope="module")
def gold():
    return build_gold.build(check_only=True)


def _mutate(kb, element_id, **changes):
    """Copy of kb whose latest record of element_id has the given fields changed."""
    target = kb.history(element_id)[-1]
    records = [replace(r, **changes) if r is target else r for r in kb.records]
    return KnowledgeBase(records, kb.updates, kb.documents, kb.name, kb.adoptions)


def _messages(kb):
    return {m for _, m in shacl.validate(kb)}


def test_round_trip_keeps_records(gold, tmp_path):
    path = tmp_path / "kb.trig"
    rdf.write_trig(gold, path)
    back = rdf.read_trig(path)
    assert back.fingerprint() == gold.fingerprint()
    assert [u for u in back.updates] == [u for u in gold.updates]
    for a, b in zip(gold.records, back.records):
        assert type(a) is type(b) and a.id == b.id and a.seq == b.seq
        if hasattr(a, "rows"):
            assert a.rows == b.rows
        if isinstance(a, Parameter):
            assert a.value == b.value and type(a.value) is type(b.value)


def test_gold_conforms(gold):
    assert shacl.validate(gold) == []


@pytest.mark.parametrize("element_id,changes,message", [
    ("REG.TER.RUNNING", {"valid_from": date(2024, 1, 2)}, "G1: validFrom must be the first day of a month"),
    ("REG.TER.RUNNING", {"valid_until": date(2024, 2, 28)}, "G1: validUntil must be the last day of a month"),
    ("REG.TER.RUNNING", {"valid_until": date(2023, 12, 31)}, "G1: validUntil must not be before validFrom"),
    ("REG.TER.RUNNING", {"layer": "company", "policy": "PKB-WIKA-2025", "id": "PRS.X"},
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
def test_shape_catches_mutation(gold, element_id, changes, message):
    assert message in _messages(_mutate(gold, element_id, **changes))


def test_company_rule_without_policy(gold):
    kb = _mutate(gold, "REG.TER.RUNNING", layer="company", modality="default", policy=None, id="PRS.X")
    assert "G1: a company rule needs its policy document" in _messages(kb)


def test_bracket_row_order(gold):
    rows = list(gold.history("TAB.TER_MONTHLY.2024")[-1].rows)
    rows[3] = dict(rows[3], upper=rows[3]["lower"])
    assert "G1: bracket or progressive row with upper <= lower" in _messages(
        _mutate(gold, "TAB.TER_MONTHLY.2024", rows=tuple(rows)))
