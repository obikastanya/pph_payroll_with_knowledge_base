"""Data figures of the manuscript, drawn from the analysis files (no numbers are typed here).

    env\\Scripts\\python v2\\paper\\make_figures.py

Reads v2/work/analysis/{chains,isolated}.json and v2/work/posthoc_g7/chains_report.json; writes v2/paper/figs/.
Colors: the categorical order and status steps of the reference palette (light surface).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "v2" / "work"
FIGS = Path(__file__).resolve().parent / "figs"
REAL = ("SANSAN", "CENTEX", "TAEKWANG", "AVCO", "WIKA")
NAMES = {"SANSAN": "Sansan", "CENTEX": "Century\nTextile", "TAEKWANG": "Taekwang", "AVCO": "AVCO", "WIKA": "WIKA"}
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
GOOD, WARN, CRIT = "#0ca30c", "#fab219", "#d03b3b"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False, "pdf.fonttype": 42})


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def payslip_figure():
    base = load(WORK / "analysis" / "chains.json")["chains"]
    g7 = load(WORK / "posthoc_g7" / "chains_report.json")["chains"]
    series = [("Without reviewer", lambda c: base[c]["accuracy"]["none"]["at_payroll"]),
              ("With reviewer", lambda c: base[c]["accuracy"]["base"]["at_payroll"]),
              ("With reviewer and completeness gate", lambda c: g7[c]["accuracy"]["base"]["at_payroll"]),
              ("Code update after 26 days", lambda c: base[c]["accuracy"]["code"]["at_payroll"])]
    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    w, gap = 0.19, 0.012
    for i, (label, get) in enumerate(series):
        xs = [k + (i - 1.5) * (w + gap) for k in range(len(REAL))]
        ax.bar(xs, [get(c) for c in REAL], width=w, color=SERIES[i], label=label, zorder=3)
    ax.set_xticks(range(len(REAL)), [NAMES[c] for c in REAL])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Payslips correct on payroll date")
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.2), fontsize=7.5)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_payslip.pdf", bbox_inches="tight")
    plt.close(fig)


def outcome_figure():
    iso = load(WORK / "analysis" / "isolated.json")
    by_layer = iso["prospective_by"]["layer"]
    rows = [("Real regulations (13)", iso["real"]["regulations"]["pipeline"]),
            ("Real labor agreements (6)", iso["real"]["pkb"]["pipeline"]),
            ("Real distractors (20)", iso["real"]["distractors"]),
            ("Prospective regulation units (50)", by_layer["regulation"]["pipeline"]),
            ("Prospective company-policy units (30)", by_layer["company"]["pipeline"])]
    parts = (("correct", "Correct", GOOD), ("abstain", "Abstained", WARN), ("silent_error", "Silent error", CRIT))
    fig, ax = plt.subplots(figsize=(3.5, 2.0))
    for y, (label, r) in enumerate(reversed(rows)):
        n = sum(r.get(k, 0) for k, _, _ in parts)
        left = 0.0
        for k, name, color in parts:
            share = r.get(k, 0) / n
            if share:
                ax.barh(y, share - 0.004, left=left, color=color, height=0.62, zorder=3,
                        label=name if y == 0 else None)
                if share >= 0.05:
                    ax.text(left + share / 2, y, str(r.get(k, 0)), ha="center", va="center", fontsize=7,
                            color="white" if k != "abstain" else INK)
            left += share
    ax.set_yticks(range(len(rows)), [r[0] for r in reversed(rows)], fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Share of documents")
    handles, labels = ax.get_legend_handles_labels()
    order = [labels.index(n) for _, n, _ in parts if n in labels]
    ax.legend([handles[i] for i in order], [labels[i] for i in order], ncol=3, frameon=False, loc="upper center",
              bbox_to_anchor=(0.35, 1.2), fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_outcomes.pdf", bbox_inches="tight")
    plt.close(fig)


def timeline_figure():
    """Issue dates of the 13 test events; grey arcs run from the issue date back to the start of validity."""
    import csv
    from datetime import date

    import matplotlib.dates as mdates
    rows = [r for r in csv.DictReader(open(ROOT / "v2" / "dataset" / "09_korpus_peristiwa" / "peristiwa.csv",
                                           encoding="utf-8")) if r["bagian"] == "uji"]
    group = {"T1": ("parameter value (T1, T6)", SERIES[0]), "T6": ("parameter value (T1, T6)", SERIES[0]),
             "T2": ("calculation method (T2, T7)", CRIT), "T7": ("calculation method (T2, T7)", CRIT),
             "T3": ("income classification (T3)", SERIES[1]), "T4": ("tax facility (T4, T5)", GOOD),
             "T5": ("tax facility (T4, T5)", GOOD), "T9": ("rounding (T9)", "#6250d6")}
    fig, ax = plt.subplots(figsize=(7.1, 1.9))
    heights, seen = {}, set()
    for r in sorted(rows, key=lambda r: r["tanggal_terbit"]):
        code = r["jenis_perubahan"].split(",")[0].split(";")[0].strip()
        label, color = group[code]
        x = date.fromisoformat(r["tanggal_terbit"])
        h = 1.0 + 1.1 * sum(1 for k in heights if abs((k - x).days) < 75)
        heights[x] = h
        ax.vlines(x, 0, h, color=color, lw=1)
        ax.plot([x], [h], "o", color=color, ms=4, label=None if label in seen else label)
        seen.add(label)
        ax.text(x, h + 0.12, r["id"], ha="center", va="bottom", fontsize=7, color=INK)
        if r["berlaku_surut"] == "ya":
            ax.annotate("", xy=(date.fromisoformat(r["berlaku_mulai"]), 0.08), xytext=(x, 0.08),
                        arrowprops=dict(arrowstyle="->", color="#8c8c8c", lw=0.9,
                                        connectionstyle="arc3,rad=-0.6"))
    ax.set_ylim(-0.2, 4.9)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.set_xlim(date(2023, 1, 1), date(2026, 4, 30))
    ax.xaxis.set_major_locator(mdates.YearLocator(base=1, month=7))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper left", ncol=5, frameon=False, handletextpad=0.3, columnspacing=1.2,
              bbox_to_anchor=(0, 1.15), fontsize=7)
    fig.savefig(FIGS / "fig_timeline.pdf", bbox_inches="tight")
    plt.close(fig)


def workload_figure():
    """Decision on every document of the five real chains, per company."""
    data = load(WORK / "analysis" / "workload_split.json")
    parts = (("correct proposal", GOOD, "white"), ("silently wrong proposal", CRIT, "white"),
             ("written by the engineer", SERIES[0], "white"), ("judged not relevant", "#d6d5d0", INK),
             ("abstained, no change needed", "#b4b3ae", INK), ("proposal without effect", "#8a8984", "white"))
    fig, ax = plt.subplots(figsize=(7.0, 2.1))
    comps = list(reversed(REAL))
    for y, c in enumerate(comps):
        left = 0
        for k, color, txt in parts:
            v = data[c].get(k, 0)
            if v:
                ax.barh(y, v - 0.15, left=left, color=color, height=0.62, zorder=3,
                        label=k if y == len(comps) - 1 else None)
                ax.text(left + v / 2, y, str(v), ha="center", va="center", fontsize=7, color=txt)
            left += v
    ax.set_yticks(range(len(comps)), [NAMES[c].replace("\n", " ") for c in comps])
    ax.set_xlabel("Documents received")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.45, 1.32), fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_workload.pdf", bbox_inches="tight")
    plt.close(fig)


def monthly_figure():
    """Monthly payslip accuracy on the payroll date per real company."""
    path = WORK / "analysis" / "monthly.json"
    if not path.exists():
        return
    import datetime as dt
    data = load(path)
    series = (("code", "Code update after 26 days", SERIES[3]), ("reviewer", "With reviewer", SERIES[1]),
              ("reviewer_g7", "With reviewer and completeness gate", SERIES[2]))
    fig, axes = plt.subplots(1, 5, figsize=(7.1, 1.9), sharey=True)
    for ax, c in zip(axes, REAL):
        for key, label, color in series:
            months = sorted(data[c][key])
            xs = [dt.date(int(m[:4]), int(m[5:]), 15) for m in months]
            ys = [data[c][key][m][0] / data[c][key][m][1] for m in months]
            ax.plot(xs, ys, color=color, lw=1.4 if key != "reviewer_g7" else 1.1,
                    ls="-" if key != "reviewer_g7" else (0, (3, 1.5)), label=label, zorder=3)
        ax.set_title(NAMES[c].replace("\n", " "), fontsize=7.5, color=INK)
        ax.set_ylim(-0.03, 1.03)
        ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
        ax.tick_params(axis="x", labelsize=5.5, rotation=0, length=2)
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.YearLocator(base=1, month=7))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_xlim(dt.date(2023, 1, 1), dt.date(2026, 12, 31))
    axes[0].set_ylabel("Correct payslips", fontsize=7)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.12), fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "fig_monthly.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIGS.mkdir(exist_ok=True)
    workload_figure()
    monthly_figure()
    timeline_figure()
    payslip_figure()
    outcome_figure()
    print("written", sorted(p.name for p in FIGS.glob("fig_*.pdf")))
