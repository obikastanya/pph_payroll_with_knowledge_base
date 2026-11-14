"""Data figures of the IEEE Access manuscript, generated from the repository's result files.

    env\\Scripts\\python paper\\final\\make_figures.py

Writes paper/final/figs/fig_*.pdf. Every number drawn here is read from a file under dataset/, experiments/, or
docs/hasil/; nothing is typed in by hand except the two open-source calculator delays (B1, docs/hasil/b1_pemeliharaan.csv
is read for them).
"""
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "figs"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "DejaVu Serif"], "font.size": 8,
    "axes.titlesize": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})
BLUE, ORANGE, GREEN, RED, PURPLE, GRAY = "#2864AA", "#E2871E", "#288C50", "#C83232", "#823CA0", "#8C8C8C"
COL1, COL2 = 3.45, 7.1          # inches: one column, full width


def d(s):
    return date.fromisoformat(s)


# ------------------------------------------------------------------------------------------- timeline
def timeline():
    rows = [r for r in csv.DictReader(open(ROOT / "dataset/09_korpus_peristiwa/peristiwa.csv", encoding="utf-8"))
            if r["id"].startswith("E")]
    group = {"T1": ("parameter value (T1, T6)", BLUE), "T6": ("parameter value (T1, T6)", BLUE),
             "T2": ("calculation method (T2, T7)", RED), "T7": ("calculation method (T2, T7)", RED),
             "T3": ("income classification (T3)", ORANGE), "T4": ("tax facility (T4, T5)", GREEN),
             "T5": ("tax facility (T4, T5)", GREEN), "T9": ("rounding (T9)", PURPLE)}
    fig, ax = plt.subplots(figsize=(COL2, 1.55))
    heights = {}
    seen = set()
    for r in sorted(rows, key=lambda r: r["tanggal_terbit"]):
        code = r["jenis_perubahan"].split(",")[0].split(";")[0].strip()
        label, color = group[code]
        x = d(r["tanggal_terbit"])
        h = 1.0 + 0.8 * (sum(1 for k in heights if abs((k - x).days) < 75))
        heights[x] = h
        ax.vlines(x, 0, h, color=color, lw=1)
        ax.plot([x], [h], "o", color=color, ms=4, label=None if label in seen else label)
        seen.add(label)
        ax.text(x, h + 0.12, r["id"], ha="center", va="bottom", fontsize=7)
        if r["berlaku_surut"] == "ya":
            ax.annotate("", xy=(d(r["berlaku_mulai"]), -0.45), xytext=(x, -0.45),
                        arrowprops=dict(arrowstyle="->", color=GRAY, lw=0.8, connectionstyle="arc3,rad=0.35"))
    ax.set_ylim(-1.0, 3.9)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_position(("data", 0))
    ax.set_xlim(date(2023, 1, 1), date(2026, 4, 30))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", which="major", length=4, pad=2)
    ax.tick_params(axis="x", which="minor", length=2)
    ax.legend(loc="upper left", ncol=5, frameon=False, handletextpad=0.3, columnspacing=1.2,
              bbox_to_anchor=(0, 1.12))
    ax.text(date(2023, 1, 5), -0.85, "grey arrows: from issue date back to the start of validity (retroactive rules)",
            fontsize=6.5, color=GRAY, ha="left")
    fig.savefig(OUT / "fig_timeline.pdf")
    plt.close(fig)


# ------------------------------------------------------------------------------------------- coverage
def coverage():
    rows = list(csv.DictReader(open(ROOT / "docs/hasil/sebaran_ruang_uji.csv", encoding="utf-8")))
    ter = defaultdict(list)
    pkp = []
    for r in rows:
        v = int(r["value"])
        if r["kind"] == "ter_month":
            ter[r["category"]].append(v)
        elif v > 0:
            pkp.append(v)
    bounds = defaultdict(list)
    for r in csv.DictReader(open(ROOT / "dataset/13_teks/PP-58-2023/tabel/LAMPIRAN-ABC.csv", encoding="utf-8")):
        lo = int(float(r["batas_bawah"]))
        if lo > 0:
            bounds[r["kategori"]].append(lo)
    rng = np.random.default_rng(7)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(COL1, 2.55), gridspec_kw={"height_ratios": [1.6, 1]})
    for i, cat in enumerate(["A", "B", "C"]):
        y = i + 1
        for b in bounds[cat]:
            a1.vlines(b / 1e6, y - 0.38, y + 0.38, color=BLUE, lw=0.35, alpha=0.6)
        xs = np.array(ter[cat]) / 1e6
        a1.scatter(xs, y + rng.uniform(-0.3, 0.3, len(xs)), s=0.6, color=ORANGE, alpha=0.35, lw=0,
                   rasterized=True)
    top = max(max(v) for v in ter.values()) / 1e6
    a1.axvspan(top, 2000, color=GRAY, alpha=0.18, lw=0)
    a1.text(900, 3.55, "not reached", ha="center", fontsize=6.5)
    a1.set_xscale("log")
    a1.set_xlim(1, 2000)
    a1.set_yticks([1, 2, 3], ["A", "B", "C"])
    a1.set_ylim(0.4, 3.8)
    a1.set_ylabel("TER category")
    a1.set_xlabel("monthly gross income, January to November 2024–2026 (Rp million)")
    p17 = [60e6, 250e6, 500e6, 5e9]
    xs = np.array(pkp) / 1e6
    a2.scatter(xs, rng.uniform(-0.3, 0.3, len(xs)), s=0.8, color=ORANGE, alpha=0.4, lw=0, rasterized=True)
    for b in p17:
        a2.axvline(b / 1e6, color=BLUE, lw=0.8)
    edges = [0] + p17 + [float("inf")]
    for (lo, hi), rate in zip(zip(edges, edges[1:]), ["5%", "15%", "25%", "30%", "35%"]):
        n = sum(1 for v in pkp if lo < v <= hi)
        xm = np.sqrt(max(lo, 3e6) * min(hi, 4e10)) / 1e6
        a2.text(xm, 0.55, f"{rate}\nn={n}", ha="center", va="bottom", fontsize=6.5)
    a2.set_xscale("log")
    a2.set_xlim(3, 40000)
    a2.set_ylim(-0.5, 1.4)
    a2.set_yticks([])
    a2.spines["left"].set_visible(False)
    a2.set_xlabel("annual taxable income, 2023–2026 (Rp million); lines: Article 17 brackets")
    fig.tight_layout(h_pad=0.6)
    fig.savefig(OUT / "fig_coverage.pdf", dpi=300)
    plt.close(fig)


# ------------------------------------------------------------------------------------------- acquisition
def acquisition():
    e2 = json.load(open(ROOT / "docs/hasil/e2_ringkasan.json", encoding="utf-8"))["conditions"]
    abl = json.load(open(ROOT / "docs/hasil/ablasi_gerbang.json", encoding="utf-8"))

    def frac(s):
        a, b = s.split("/")
        return int(a) / int(b)

    pts = {
        "proposed (also m = 5)": (e2["proposed"]["CAR"], e2["proposed"]["SER"]),
        "first draft passing G1–G2 (B3)": (e2["B3"]["CAR"], e2["B3"]["SER"]),
        "majority without gates (B4);\nwithout G5; G1 only": (e2["B4"]["CAR"], e2["B4"]["SER"]),
        "first draft passing all gates\n(no consensus)": (e2["AB4_first"]["CAR"], e2["AB4_first"]["SER"]),
        "perfect selection": (e2["AB4_perfect"]["CAR"], e2["AB4_perfect"]["SER"]),
        "without repair": (e2["AB3_norepair"]["CAR"], e2["AB3_norepair"]["SER"]),
    }
    ab2 = [r for run in ("e2-ab2-regulasi", "e2-ab2-pkb")
           for r in csv.DictReader(open(ROOT / "experiments" / run / "scores.csv", encoding="utf-8"))
           if r["condition"] == "proposed"]
    pts["without KB context"] = (f"{sum(r['outcome'] == 'benar' for r in ab2)}/{len(ab2)}",
                                 f"{sum(r['outcome'] == 'salah' for r in ab2)}/{len(ab2)}")
    assert abl["AB3_onlyG1"]["SER"] == e2["B4"]["SER"] and abl["AB3_onlyG1"]["CAR"] == e2["B4"]["CAR"]
    offs = {"proposed (also m = 5)": (-6, -11), "first draft passing G1–G2 (B3)": (6, -5),
            "majority without gates (B4);\nwithout G5; G1 only": (6, 2), "first draft passing all gates\n(no consensus)": (-6, 6),
            "perfect selection": (6, 2), "without repair": (-6, 6), "without KB context": (6, 4)}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL2, 2.25), gridspec_kw={"width_ratios": [1.35, 1]})
    for risk in (0.25, 0.5):
        x = np.linspace(0, 0.75, 10)
        a1.plot(x, risk / (1 - risk) * x, ls=":", color=GRAY, lw=0.7)
        xt = 0.72 if risk < 0.5 else 0.47
        a1.text(xt, risk / (1 - risk) * xt, f"selective risk {risk:g}", fontsize=6, color=GRAY,
                ha="right" if risk < 0.5 else "left", va="bottom")
    for name, (car, ser) in pts.items():
        x, y = frac(car), frac(ser)
        color = ORANGE if name.startswith("proposed") else BLUE
        a1.plot([x], [y], "o", color=color, ms=4)
        dx, dy = offs[name]
        a1.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=6.3,
                    ha="right" if dx < 0 else "left", va="center")
    a1.set_xlim(0.25, 0.75)
    a1.set_ylim(-0.03, 0.5)
    a1.set_xlabel("correct application rate (of 18 documents)")
    a1.set_ylabel("silent error rate")
    a1.set_title("(a) safety versus usefulness by condition")
    size = {}
    for r in csv.DictReader(open(ROOT / "dataset/12_emas/rantai.csv", encoding="utf-8")):
        if r["event_id"].startswith("E"):
            size[r["event_id"]] = int(r["add"]) + int(r["change"]) + int(r["remove"])
    out = {r["event"]: r["outcome"] for r in csv.DictReader(
        open(ROOT / "experiments/e2-regulasi/scores.csv", encoding="utf-8")) if r["condition"] == "proposed"}
    groups = [("1", lambda n: n == 1), ("2–7", lambda n: 2 <= n <= 7), ("11–15", lambda n: 11 <= n <= 15)]
    labels, ok, bad, ab = [], [], [], []
    for lab, f in groups:
        evs = [e for e in size if f(size[e])]
        labels.append(f"{lab}\n(n={len(evs)})")
        ok.append(sum(out.get(e) == "benar" for e in evs))
        bad.append(sum(out.get(e) == "salah" for e in evs))
        ab.append(sum(out.get(e, "abstain") == "abstain" for e in evs))
    pkb = [r for r in csv.DictReader(open(ROOT / "experiments/e2-pkb/scores.csv", encoding="utf-8"))
           if r["condition"] == "proposed"]
    labels.append(f"agreements\n14–35 (n={len(pkb)})")
    ok.append(sum(r["outcome"] == "benar" for r in pkb))
    bad.append(sum(r["outcome"] == "salah" for r in pkb))
    ab.append(sum(r["outcome"] == "abstain" for r in pkb))
    x = np.arange(len(labels))
    a2.bar(x, ok, color=GREEN, width=0.6, label="correct")
    a2.bar(x, bad, bottom=ok, color=RED, width=0.6, label="silent error")
    a2.bar(x, ab, bottom=np.array(ok) + np.array(bad), color="#C8C8C8", width=0.6, label="abstain")
    a2.set_xticks(x, labels)
    a2.set_ylabel("documents")
    a2.set_xlabel("size of the gold update (elements)")
    a2.set_title("(b) outcome by size of the required update")
    a2.legend(frameon=False, loc="upper center", ncol=3)
    a2.set_ylim(0, 6.6)
    fig.tight_layout(w_pad=1.5)
    fig.savefig(OUT / "fig_acquisition.pdf")
    plt.close(fig)


# ------------------------------------------------------------------------------------------- replay
def replay():
    fig, axes = plt.subplots(2, 1, figsize=(COL2, 2.9), sharex=True)
    for ax, run, title in zip(axes, ["e3-tetap", "e3-bangkit-ulang"],
                              ["(a) transplanted chain (drafts of the isolated run reused)",
                               "(b) regenerated chain (drafts written against the system's own KB)"]):
        rows = list(csv.DictReader(open(ROOT / "experiments" / run / "chain.csv", encoding="utf-8")))
        x = np.arange(len(rows))
        wrong = [int(r["wrong"]) for r in rows]
        cases = [int(r["cases"]) for r in rows]
        color = [RED if r["event"].startswith("E") else GRAY for r in rows]
        ax.bar(x, wrong, color=color, width=0.7)
        ax.step(x, cases, where="mid", color=BLUE, lw=0.9, label="cases scored")
        for i, r in enumerate(rows):
            if r["abstain"] == "True":
                ax.text(i, wrong[i] + 12, "A", ha="center", fontsize=6)
        ax.set_ylim(0, 680)
        ax.set_ylabel("incorrect cases")
        ax.set_title(title, loc="left")
        ax.bar([0], [0], color=RED, label="test event")
        ax.bar([0], [0], color=GRAY, label="distractor")
        ax.legend(frameon=False, loc="upper left", fontsize=6.5, ncol=3)
        ax.set_xticks(x, [r["event"] for r in rows], rotation=90, fontsize=6)
    fig.tight_layout(h_pad=0.4)
    fig.savefig(OUT / "fig_replay.pdf")
    plt.close(fig)


# ------------------------------------------------------------------------------------------- time to adapt
def adapt():
    calls = defaultdict(lambda: defaultdict(list))
    for line in open(ROOT / "experiments/e2-regulasi/calls.jsonl", encoding="utf-8"):
        c = json.loads(line)
        calls[c["event"]][c["step"]].append(c.get("seconds") or 0)

    def total(ev):
        return sum(sum(v) for v in calls[ev].values())

    b1 = {r["repo"]: int(r["days_after_issue"]) for r in csv.DictReader(
        open(ROOT / "docs/hasil/b1_pemeliharaan.csv", encoding="utf-8")) if r.get("days_after_issue")}
    s03, s04 = total("E03"), total("E04")
    items = [("KB: model calls drafting PP 58/2023\nand PMK 168/2023 (review excluded)", (s03 + s04) / 86400,
              "8 new and 13 changed elements", ORANGE)]
    for i, (repo, days) in enumerate(sorted(b1.items(), key=lambda kv: kv[1])):
        items.append((f"open-source calculator {i + 1}", days, None, BLUE))
    fig, ax = plt.subplots(figsize=(COL1, 1.35))
    y = np.arange(len(items))[::-1]
    for yy, (lab, days, note, color) in zip(y, items):
        ax.barh(yy, days, color=color, height=0.55, left=1e-4)
        txt = f"{days * 1440:.1f} min" if days < 1 else f"{days} days"
        ax.text(days * 1.4 + 1e-4, yy, txt + (f"; {note}" if note else ""), va="center", fontsize=6.5)
    ax.set_yticks(y, [it[0] for it in items])
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 2e4)
    ax.set_xlabel("days after PP 58/2023 was issued (log scale)")
    fig.savefig(OUT / "fig_adapt.pdf")
    plt.close(fig)
    return s03, s04, b1


if __name__ == "__main__":
    timeline()
    coverage()
    acquisition()
    replay()
    print("adapt", adapt())
    print("written:", sorted(p.name for p in OUT.glob("fig_*.pdf")))
