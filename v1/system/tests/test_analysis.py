"""Statistics and scoring on data with known answers (Tahap 10 completion criterion)."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from pph21kbs.analysis import stats  # noqa: E402
from pph21kbs.analysis.agreement import cohen_kappa, krippendorff_alpha_nominal  # noqa: E402


def test_clopper_pearson_and_bounds():
    lo, hi = stats.clopper_pearson(0, 10)
    assert lo == 0 and abs(hi - 0.3084971) < 1e-6
    lo, hi = stats.clopper_pearson(5, 10)
    assert abs(lo - 0.187086) < 1e-5 and abs(hi - 0.812914) < 1e-5
    assert abs(stats.upper_bound(0, 10) - (1 - 0.05 ** 0.1)) < 1e-9          # 0.2589 (skeleton)
    assert abs(stats.upper_bound(0, 59) - 0.0495) < 1e-3                      # 59 documents for SER <= 5%
    assert abs(stats.lower_bound_all_detected(30) - 0.905) < 1e-3             # skeleton example
    assert math.ceil(math.log(0.05) / math.log(1 - 0.001)) == 2995            # operational sample size


def test_newcombe_intervals():
    # Newcombe (1998), independent proportions 56/70 vs 48/80: difference 0.2, CI 0.0524 to 0.3339
    diff, lo, hi = stats.newcombe_unpaired(56, 70, 48, 80)
    assert abs(diff - 0.2) < 1e-12 and abs(lo - 0.0524) < 1e-3 and abs(hi - 0.3339) < 1e-3
    # paired (method 10): same Wilson limits, correlation narrows the interval; it contains the difference
    diff, lo, hi = stats.newcombe_paired(12, 9, 2, 21)
    assert abs(diff - 7 / 44) < 1e-12 and lo < diff < hi
    _, ulo, uhi = stats.newcombe_unpaired(21, 44, 14, 44)
    assert hi - lo < uhi - ulo
    assert stats.newcombe_paired(5, 0, 0, 5)[0] == 0


def test_mcnemar_and_holm():
    assert abs(stats.mcnemar_exact(9, 2) - 0.0654) < 1e-3
    assert stats.mcnemar_exact(0, 0) == 1.0
    adj = stats.holm([0.01, 0.04, 0.03])
    assert [round(x, 3) for x in adj] == [0.03, 0.06, 0.06]


def test_pass_at_and_efficiency():
    assert stats.pass_at(5, 0, 1) == 0 and stats.pass_at(5, 5, 1) == 1
    assert abs(stats.pass_at(5, 2, 1) - 0.4) < 1e-12
    assert abs(stats.pass_at(5, 2, 5) - 1.0) < 1e-12
    assert stats.selection_efficiency(0.7, 0.4, 1.0) == pytest.approx(0.5)
    assert stats.selection_efficiency(0.5, 0.5, 0.5) is None


def test_f2_and_flag_all():
    assert stats.f_beta(1.0, 1.0) == pytest.approx(1.0)
    assert stats.f_beta(0.5, 1.0) == pytest.approx(5 * 0.5 / (4 * 0.5 + 1))
    assert stats.f2_flag_all(0.25) == pytest.approx(5 * 0.25 / 2.0)


def test_wilcoxon_and_bootstrap():
    stat, p, r = stats.wilcoxon([3, 4, 5, 6, 7, 8], [1, 1, 1, 1, 1, 1])
    assert p < 0.05 and r == 1.0
    clusters = {i: [1] * 5 for i in range(20)}
    assert stats.cluster_bootstrap(clusters, lambda xs: sum(xs) / len(xs), b=200) == (1, 1)


def test_agreement_known_values():
    data = [[1, 1, None, 1], [2, 2, 3, 2], [3, 3, 3, 3], [3, 3, 3, 3], [2, 2, 2, 2], [1, 2, 3, 4], [4, 4, 4, 4],
            [1, 1, 2, 1], [2, 2, 2, 2], [None, 5, 5, 5], [None, None, 1, 1], [None, None, 3, None]]
    assert round(krippendorff_alpha_nominal(data), 3) == 0.743                # Krippendorff (2011)
    assert round(cohen_kappa([(1, 1), (1, 0), (0, 0), (0, 0), (1, 1), (0, 1)]), 3) == 0.333
