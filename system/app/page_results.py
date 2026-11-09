"""Research results for people who are not researchers: four questions, a plain answer each, the numbers as
"x out of y", what it means for the user, and the technical detail folded away.

All numbers come from docs/BAHAN_PAPER.md (final results, tag hasil-v2).
"""
import streamlit as st

import glossary as g
import ui

GREEN, RED, YELLOW, GREY = "#2e9e5b", "#d64545", "#e8b730", "#d9d8d4"


def dots(parts, per_row=20):
    """Unit chart: [(count, colour, label)] as small squares, one per item."""
    cells = "".join(f"<span title='{label}' style='display:inline-block;width:14px;height:14px;border-radius:3px;"
                    f"margin:2px;background:{colour}'></span>" for n, colour, label in parts for _ in range(n))
    legend = " &nbsp; ".join(f"<span style='display:inline-block;width:10px;height:10px;border-radius:2px;"
                             f"background:{c};margin-right:4px'></span>{n} {label}" for n, c, label in parts)
    total = sum(n for n, _, _ in parts)
    width = min(total, per_row) * 18
    return f"<div style='max-width:{width}px;line-height:0'>{cells}</div><div class='muted' style='margin-top:.35rem'>{legend}</div>"


def question(n, q, verdict, colour, answer, picture, meaning, detail):
    with st.container(border=True):
        left, right = st.columns([1.25, 1], gap="large")
        with left:
            ui.html(f"<span class='muted'>Question {n}</span><div style='font-size:1.15rem;font-weight:650;"
                    f"margin:.1rem 0 .45rem 0;line-height:1.35'>{q}</div>"
                    f"{ui.badge(verdict, colour)}<div class='answer'>{answer}</div>")
            ui.html(f"<div class='explain'><b>What it means for you:</b> {meaning}</div>")
        with right:
            ui.html(picture)
        with st.expander("Details for researchers"):
            st.markdown(detail)


def show():
    st.session_state.page_ctx = "hasil"
    st.title("Research results")
    g.md("This research tests one idea: a PPh 21 calculator whose knowledge is stored as a "
         f"{g.term('knowledge base')} (rules, numbers, and tables with effective dates and source articles), then updated "
         "from new regulations with the help of AI and automatic checks. Four questions, answered with real "
         "regulations from 2023–2026.")
    c = st.columns(4)
    c[0].metric("Real regulations tested", "13", help="Change events for PPh 21 and BPJS, 2023–2026.")
    c[1].metric("Company documents (PKB)", "5", help=g.tip("kebijakan perusahaan"))
    c[2].metric("Documents that are not relevant", "20", help="Regulations that look similar but do not change PPh 21 for permanent employees.")
    c[3].metric("Test employee cases", "2,398", help="Combinations of salary, status, sector, month, and income component.")

    question(1, "Can a rule change be added without changing the program?", "Yes", "green",
             "16 of 16 previously unseen rule changes were added successfully, and 100 of 100 example "
             "calculations matched.",
             dots([(16, GREEN, "changes added")], per_row=16) +
             "<div class='muted' style='margin-top:.6rem'>2,609 calculated figures were checked.</div>",
             "When a regulation changes, only the content of the knowledge base (rules, numbers, tables) is updated, not "
             "the program code. That is what makes the Knowledge base management page possible.",
             "- Hypothesis H1 (RA ≥ 0.70): 16/16, CP 95% [0.794, 1.000], one-sided lower bound 0.829. **Accepted.**\n"
             "- Depends on the rounding rule: without the PER-11/PJ/2025 rounding convention, 8/16 (all differences ≤ Rp11); "
             "conservative 15/16.\n- The changes were written by an independent agent, not yet by a human payroll expert.")

    question(2, "Can the AI read a new regulation and propose the right update?", "Partly", "yellow",
             "Of 18 real documents: 8 proposed correctly, 3 wrongly, and for 7 the system was unsure, so it proposed nothing.",
             dots([(8, GREEN, "correct"), (3, RED, "wrong"), (7, YELLOW, "system unsure")], per_row=9) +
             "<div class='muted' style='margin-top:.8rem'><b>Without the agreement check</b> (the first proposal that passes "
             "the basic checks):</div>" +
             dots([(8, GREEN, "correct"), (7, RED, "wrong"), (3, YELLOW, "system unsure")], per_row=9),
             "The AI saves work on government regulations, but every proposal still has to be reviewed. The automatic "
             f"checks and the {g.term('kesepakatan', 'agreement check')} cut wrong proposals from 7 to 3; "
             f"in exchange the system is more often {g.term('ragu')}. For company PKBs, write the rules yourself: all five PKBs were held back.",
             "- Regulations (13): 8 correct, 3 wrong (E02, E07, E11), system unsure for 2. PKBs (5): system unsure for 5/5.\n"
             "- H2a (SER upper bound ≤ 0.25): SER 3/18, upper bound 0.377. **Not accepted.**\n"
             "- H2b proposed-method CAR 8/18 = B3 8/18, B4 9/18. **Not accepted**; non-inferiority of SER vs B3 is met.\n"
             "- Look-alike documents: 7/20 judged relevant, 1/20 wrongly applied (PP 49/2023).\n"
             "- Second model (gpt-6.1-sol): SER 3/18, CAR 7/18. Cost per regulation document USD 0.12–1.87.")

    question(3, "When updates keep coming in, do the calculations stay correct?", "Not robust yet", "red",
             "31 of 33 documents that came in one after another added no errors. But the 2 that were wrong carried on: "
             "at the end of the chain, 579 of 600 test cases are wrong.",
             dots([(31, GREEN, "added no errors"), (2, RED, "added errors")], per_row=11) +
             "<div class='muted' style='margin-top:.8rem'>Test cases wrong at the end of the chain without correction</div>" +
             "<div style='background:#f0efec;border-radius:6px;height:16px;width:100%;margin-top:4px'>"
             "<div style='background:#d64545;height:16px;border-radius:6px;width:96.5%'></div></div>"
             "<div class='muted'>579 of 600</div>",
             "One wrong update (here a document that is actually not relevant but was accepted by mistake) breaks later "
             "calculations until it is fixed. That is why the system keeps all versions, can roll back, and refuses to "
             "change past calculations.",
             "- OAR (share of events with no new error), isolated update transplant: 31/33, lower bound 0.821, "
             "H3a **accepted** in the registered analysis. Regeneration: 23/33, 0.540 (**not robust**).\n"
             "- New errors from E02 (15 cases) and P01 (264 cases); P01 persists to the end.\n"
             "- H3b triggered errors 29 cases vs noise floor 0: **not supported**; 26 of the 29 come from cases where "
             "the system was unsure.")

    question(4, "Can the system tell which company policies are affected too?", "Yes", "green",
             "Of 33 policy and regulation pairs that were really affected, 30 were flagged. Of 42 warnings, "
             "30 were right.",
             dots([(30, GREEN, "affected and flagged"), (3, RED, "missed")], per_row=11) +
             "<div class='muted' style='margin-top:.8rem'>Warnings shown</div>" +
             dots([(30, GREEN, "right"), (12, GREY, "false alarm")], per_row=14),
             "When a regulation changes, you get a list of company policies to check. About 3 in 10 warnings turn out "
             "not to need a change, and now and then one is missed.",
             "- H4a recall ≥ 0.70: 0.91 (CI 0.75–1.00). **Accepted.** Precision 0.71; F₂ 0.862.\n"
             "- H4b F₂ > baselines: +0.193 vs text scan; −0.006 vs flag everything that touches a changed value. "
             "**Not accepted.**\n- 134 pairs, 33 positive; 27 of the 33 come from synthetic policies.")

    st.subheader("Compared with other approaches")
    c = st.columns(3)
    with c[0].container(border=True):
        st.markdown("**Hand-coded calculators**")
        ui.html("<div class='answer'>26 and 915 days</div>")
        st.caption("Two open-source calculators took 26 and 915 days to add the TER rates after PP 58/2023 was issued. "
                   "In a knowledge base, that change is one data update.")
    with c[1].container(border=True):
        st.markdown("**AI calculating directly from the regulation**")
        ui.html("<div class='answer'>76 of 100 exact</div>")
        st.caption("97 of 100 are off by at most Rp1. But without an article trail, results can differ from run to run, "
                   "and each calculation costs USD 0.068.")
    with c[2].container(border=True):
        st.markdown("**AI writing rules from scratch**")
        ui.html("<div class='answer'>0 pass the checks</div>")
        st.caption("Without the knowledge base as context, no proposal passes. Updating bit by bit is much easier than "
                   "rewriting everything.")

    st.subheader("Good to know")
    st.markdown("- The comparison experts and checkers are independent AI agents, not yet human payroll experts.\n"
                "- The number of documents is small (18 real), so differences between methods are hard to prove "
                "statistically.\n"
                "- Scope: permanent employees, one employer, one tax year.\n"
                "- All test regulations were published before the AI models' knowledge cutoff, so memorization cannot "
                "be fully ruled out; a test with counterfactual regulations found no memorization.")
    st.caption("Full technical details are in the paper and docs/BAHAN_PAPER.md.")
