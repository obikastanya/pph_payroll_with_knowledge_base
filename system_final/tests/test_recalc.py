"""Recalculation report for a retroactive regulation."""
from datetime import date

import cli
from pph21kbs import config, graph, recalc


def test_retroactive_dtp_is_reported_for_the_month_already_paid():
    kb = graph.read_trig(config.SEED_KB, "K")
    garment, other = cli.simple_case(2025, 8_000_000, klu="14111"), cli.simple_case(2025, 8_000_000, klu="62019")
    before, after = date(2025, 2, 3), date(2025, 2, 5)      # PMK 10/2025 was issued on 4 February, for January on
    out = recalc.report(kb, [garment, other], before, after, paid_through=1)
    assert [r["case_id"] for r in out] == [garment["case_id"]]
    january = {r["fact"]: r for r in out[0]["differences"] if r["month"] == 1}
    assert january["pph21_dtp"]["before"] == 0 and january["pph21_dtp"]["after"] > 0
    assert recalc.differences(kb, garment, before, before) == []
