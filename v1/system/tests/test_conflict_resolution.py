"""Conflict resolution suite (Tahap 5): pairs of rules whose legal winner is known, one group per principle of
representasi.md section 8. Independent of the gold knowledge base."""
from datetime import date

from pph21kbs.engine import evaluate_case
from pph21kbs.kb import apply_delta, empty_kb

from test_engine_core import SRC, case, delta, fact, rule

OMEGA = date(2021, 12, 31)


def base(*rules, adopts=None):
    """Toy KB where fact `x` (output) is produced only by the given rules, read from a case with salary income."""
    d = delta("BASE", add=[fact("x", output=True), fact("y", output=True), *rules])
    if adopts:
        d["adopts"] = adopts
    return apply_delta(empty_kb(), d)


def x_of(kb, policy=None, months=(1,), omega=OMEGA, year=2021):
    r = evaluate_case(kb, case(1000, months=months, policy=policy, year=year), omega)
    return r, r.periods[months[0]]["x"]


# ---------------------------------------------------------------------- lex superior
def test_mandatory_regulation_beats_company_beats_optional_beats_default():
    rules = [rule("REG.D", "x", "1", modality="default"),
             rule("REG.O", "x", "2", modality="optional"),
             rule("PRS.C", "x", "3", layer="company", modality="default", policy="PX"),
             rule("REG.M", "x", "4")]
    r, v = x_of(base(*rules), policy="PX")
    assert v == 4 and r.winners[("x", 1)] == "REG.M"
    r, v = x_of(base(*rules[:3]), policy="PX")
    assert v == 3
    r, v = x_of(base(*rules[:2]))
    assert v == 1, "an optional rule counts only when a policy adopts it"
    kb = base(*rules[:2])
    kb = apply_delta(kb, {**delta("ADOPT"), "document": {"id": "PX", "issued": "2020-01-01"}, "adopts": ["REG.O"]})
    _, v = x_of(kb, policy="PX")
    assert v == 2


def test_company_rule_needs_its_policy_in_the_case():
    kb = base(rule("REG.D", "x", "1", modality="default"),
              rule("PRS.C", "x", "3", layer="company", modality="default", policy="PX"))
    assert x_of(kb)[1] == 1
    assert x_of(kb, policy="PY")[1] == 1
    assert x_of(kb, policy=["PY", "PX"])[1] == 3


def test_company_rule_losing_to_mandatory_rule_is_a_conflict_only_when_values_differ():
    kb = base(rule("REG.M", "x", "4"),
              rule("PRS.SAME", "x", "4", layer="company", modality="default", policy="PX"),
              rule("PRS.DIFF", "y", "5", layer="company", modality="default", policy="PX", conflict_code="C3"),
              rule("REG.MY", "y", "6"))
    r, v = x_of(kb, policy="PX")
    assert v == 4 and r.periods[1]["y"] == 6
    assert [(c["source"], c["code"]) for c in r.conflicts] == [("PRS.DIFF", "C3")]
    assert r.conflict_keys() == {("override", "PRS.DIFF", "y", 1)}


# ---------------------------------------------------------------------- lex specialis
def test_explicit_override_beats_same_rank_rule_even_if_older():
    kb = base(rule("REG.GENERAL", "x", "1", vf="2021-01-01"),
              rule("REG.SPECIAL", "x", "2", vf="2020-01-01", overrides=["REG.GENERAL"]))
    r, v = x_of(kb)
    assert v == 2 and r.winners[("x", 1)] == "REG.SPECIAL"


def test_override_is_transitive_and_inactive_special_rule_leaves_general_rule():
    kb = base(rule("REG.A", "x", "1"),
              rule("REG.B", "x", "2", overrides=["REG.A"], cond="income('salary') > 5000"),
              rule("REG.C", "x", "3", overrides=["REG.B"]))
    assert x_of(kb)[1] == 3
    kb = base(rule("REG.A", "x", "1"), rule("REG.B", "x", "2", overrides=["REG.A"], cond="income('salary') > 5000"))
    assert x_of(kb)[1] == 1


def test_override_does_not_lift_a_lower_rank():
    kb = base(rule("REG.M", "x", "4"), rule("REG.D", "x", "1", modality="default", overrides=["REG.M"]))
    assert x_of(kb)[1] == 4


# ---------------------------------------------------------------------- lex posterior
def test_later_valid_from_wins():
    kb = base(rule("REG.OLD", "x", "1", vf="2020-01-01"), rule("REG.NEW", "x", "2", vf="2021-01-01"))
    assert x_of(kb)[1] == 2
    assert x_of(kb, year=2020)[1] == 1


def test_same_valid_from_later_first_recording_wins():
    kb = base(rule("REG.OLD", "x", "1", vf="2021-01-01"))
    kb = apply_delta(kb, delta("NEW", issued="2021-03-01",
                               add=[rule("REG.NEW", "x", "2", vf="2021-01-01", rec="2021-03-01")]))
    assert x_of(kb)[1] == 2
    assert x_of(kb, omega=date(2021, 2, 28))[1] == 1, "not known before 2021-03-01"


def test_revising_an_old_rule_does_not_make_it_newer():
    kb = base(rule("REG.OLD", "x", "1", vf="2021-01-01"))
    kb = apply_delta(kb, delta("NEW", issued="2021-03-01",
                               add=[rule("REG.NEW", "x", "2", vf="2021-01-01", rec="2021-03-01")]))
    kb = apply_delta(kb, delta("FIX", issued="2021-06-01",
                               change=[rule("REG.OLD", "x", "7", vf="2021-01-01", rec="2021-06-01")]))
    r, v = x_of(kb)
    assert v == 2, "lex posterior uses the first recording date t_c^0, not the revision date"


# ---------------------------------------------------------------------- no unique winner
def test_unresolved_conflict_and_redundant_rules():
    kb = base(rule("REG.A", "x", "1"), rule("REG.B", "x", "2"))
    r, v = x_of(kb)
    assert any("UnresolvedConflict" in e for e in r.errors)
    kb = base(rule("REG.A", "x", "1 + 1"), rule("REG.B", "x", "2"))
    r, v = x_of(kb)
    assert v == 2 and r.errors == [] and any("RedundantRules" in w for w in r.warnings)


# ---------------------------------------------------------------------- validity
def test_period_rules_valid_on_first_day_and_year_rules_on_employment_span():
    kb = base(rule("REG.D", "x", "0", modality="default"),
              rule("REG.MAR", "x", "1", vf="2021-03-01", vu="2021-03-31"),
              fact("z", scope="year", output=True),
              rule("REG.ZD", "z", "0", scope="year", modality="default"),
              rule("REG.Z", "z", "9", scope="year", vf="2021-10-01", vu="2021-12-31"))
    r = evaluate_case(kb, case(1000, months=(2, 3, 4)), OMEGA)
    assert [r.periods[m]["x"] for m in (2, 3, 4)] == [0, 1, 0]
    assert r.year["z"] == 0, "employment Feb-Apr does not meet Oct-Dec"
    r = evaluate_case(kb, case(1000, months=(9, 10)), OMEGA)
    assert r.year["z"] == 9


def test_constraint_violation_names_company_rules():
    kb = base(rule("REG.D", "x", "0", modality="default"),
              rule("PRS.LOW", "x", "-5", layer="company", modality="default", policy="PX"),
              {"kind": "constraint", "id": "CON.NONNEG", "scope": "period", "assertion": "x >= 0",
               "conflict_code": "C8", "valid_from": "2020-01-01", "recorded_on": "2020-01-01", "source": SRC})
    r, v = x_of(kb, policy="PX")
    assert v == -5
    assert r.conflict_keys() == {("constraint", ("PRS.LOW",), 1, "C8")}
