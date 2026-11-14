"""Assemble the restructured IEEE Access manuscript from the pre-restructure main.tex.

Every paragraph is copied verbatim by line range from commit b4bf5e6 (paper_final/main.tex).
Text changes are limited to the replacements in EDITS, each of which must match exactly once.
Outputs: paper_final/main.tex, paper_final/supplementary.tex, paper_final/figures/fig_pipeline.tex.

Run from the repository root:  python paper_writing/restructure/assemble_restructure.py --force

WARNING: after the restructure commit, paper_final/main.tex is edited by hand and is the source of truth.
Running this script overwrites main.tex and supplementary.tex, so it refuses to run without --force.
"""
import subprocess
import sys
from pathlib import Path

if "--force" not in sys.argv:
    sys.exit("Refusing to overwrite paper_final/main.tex. It is edited by hand now; pass --force only to "
             "reproduce the restructure from commit b4bf5e6.")

ROOT = Path(__file__).resolve().parents[2]
OLD = subprocess.run(["git", "show", "b4bf5e6:paper_final/main.tex"], cwd=ROOT,
                     capture_output=True, text=True, encoding="utf8", check=True).stdout.split("\n")
assert len(OLD) >= 760, len(OLD)


def L(a, b=None):
    """Old lines a..b (1-indexed, inclusive)."""
    b = a if b is None else b
    return "\n".join(OLD[a - 1:b])


def edit(text, old, new):
    assert text.count(old) == 1, (text.count(old), old[:80])
    return text.replace(old, new)


def split_at(text, marker):
    """Split a paragraph before the sentence that starts with marker."""
    assert text.count(marker) == 1, marker
    i = text.index(marker)
    return text[:i].rstrip(), text[i:]


# ---------------------------------------------------------------- preamble
PREAMBLE = r"""% =====================================================================
% StaticKD -- IEEE Access manuscript (ieeeaccess class)
% Restructured on 2026-11-01 from commit b4bf5e6 by paper_writing/restructure/assemble_restructure.py.
% Numbers are literal; results/final/paper_number_map.json lists every number.
% Fig. 1 is compiled separately: cd figures && pdflatex fig_pipeline (TikZ clashes with ieeeaccess.cls).
% Compile: pdflatex main && bibtex main && pdflatex main && pdflatex main
% =====================================================================
\documentclass{ieeeaccess}
\usepackage[nocompress]{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{array}
\usepackage[hyphens]{url}
\usepackage{algorithm}
\usepackage{algpseudocode}

\DeclareRobustCommand{\todo}[1]{{\color{red}[TODO: #1]}}

\emergencystretch=1.5em

\begin{document}
\history{Date of publication xxxx 00, 0000, date of current version xxxx 00, 0000.}
\doi{10.1109/ACCESS.2024.0429000}

""" + L(30) + r"""

\author{\uppercase{Obi Kastanya}\authorrefmark{1} AND \uppercase{Ananta Dwi Prayoga Alwy}\authorrefmark{1}}
\address[1]{Department of Informatics Engineering, Sepuluh Nopember Institute of Technology, Surabaya, Indonesia (e-mail: 6025252015@student.its.ac.id; 6025252007@student.its.ac.id)}
\tfootnote{This work received no specific funding.}

\markboth
{Kastanya and Alwy: StaticKD, Multilingual IPTC News Topic Classification on CPU}
{Kastanya and Alwy: StaticKD, Multilingual IPTC News Topic Classification on CPU}

\corresp{Corresponding author: Obi Kastanya (e-mail: 6025252015@student.its.ac.id).}

"""

# ---------------------------------------------------------------- front matter
abstract = L(40, 42)
keywords = L(44, 46).replace("\\begin{IEEEkeywords}", "\\begin{keywords}").replace("\\end{IEEEkeywords}", "\\end{keywords}")
front = abstract + "\n\n" + keywords + "\n\n\\titlepgskip=-21pt\n\n\\maketitle\n"

# ---------------------------------------------------------------- I. Introduction
rq = L(60)
rq = edit(rq, " RQ2 examines which parts of the training recipe matter for this very small student. The tested parts are soft labels, multilingual data, embedding initialization, embedding fine-tuning, token dropout, temperature, and ensembling. For RQ3, the study measures the inference cost of the teacher on CPU and how far StaticKD reduces that cost.",
          " For RQ2, the study measures the inference cost of the teacher on CPU and how far StaticKD reduces that cost. RQ3 examines which parts of the training recipe matter for this very small student. The tested parts are soft labels, multilingual data, embedding initialization, embedding fine-tuning, token dropout, temperature, and ensembling.")
roadmap = ("Section~\\ref{sec:related} reviews related work. Section~\\ref{sec:method} describes StaticKD, and Section~\\ref{sec:data} "
           "describes the data and the test set. The baselines and the evaluation protocol are given in Section~\\ref{sec:setup}. "
           "The results are presented in Section~\\ref{sec:results} and discussed together with the limitations of the study in "
           "Section~\\ref{sec:discussion}. Section~\\ref{sec:conclusion} concludes the paper.")
intro = "\n\n".join([
    L(48, 50).replace("\\IEEEPARstart", "\\PARstart"), L(52), L(54), L(56), L(58), rq,
    L(64, 70), roadmap])  # L62 (summary of RQ answers) removed: see restructure_log.md

# ---------------------------------------------------------------- II. Related Work
related = "\n".join([L(74, 80), "", L(82), "", L(84, 109)])  # L81 heading dropped, L82 joins II-B

# ---------------------------------------------------------------- III. The StaticKD Method
fig_pipeline = "\n".join([L(144, 145), "\\includegraphics[width=\\textwidth]{figures/fig_pipeline.pdf}", L(170, 172)])
hparams_ref = edit(L(282), "The hyperparameters of all models are listed in Table~\\ref{tab:hparams}.",
                   "The hyperparameters of all models are listed in Table~S1 of the supplementary material.")
method = "\n".join([
    "\\section{The StaticKD Method}", "\\label{sec:method}",
    "\\subsection{Study Overview}", "\\label{sec:overview}", L(114), "", L(116), "", L(118), "",
    fig_pipeline, "",
    L(174, 175), "",
    L(243, 245), "",
    L(247, 262), "",
    "\\subsection{Folding, Table Ensemble, and Compact Variant}", "\\label{sec:fold}",
    edit(L(264, 269), "Algorithm~\\ref{alg:infer} lists the whole inference procedure.",
         "Algorithm~S1 in the supplementary material lists the whole inference procedure."),
    "", hparams_ref])  # Algorithm 1 (L271-280) moved to the supplement

# ---------------------------------------------------------------- IV. Data and Test Set
testset_last = edit(L(211), "Table~\\ref{tab:testset} summarizes the composition of the article sources and Fig.~\\ref{fig:testset} shows the number of articles of each language per label.",
                    "Table~\\ref{tab:testset} summarizes the composition of the article sources and Fig.~S1 in the supplementary material shows the number of articles of each language per label.")
data = "\n".join([
    "\\section{Data and Test Set}", "\\label{sec:data}",
    "\\subsection{Data Sets and Their Roles}", "\\label{sec:roles}", L(120), "", L(122, 142), "",
    L(177, 189), "",
    L(191, 209), "", testset_last, "", L(213, 234), "",
    L(474, 482)])

# ---------------------------------------------------------------- V. Experimental Setup
design_old = L(341)
design_part, impl_part = split_at(design_old, "On average, one StaticKD run takes")
baselines = edit(L(321, 325), "Their values are listed in Table~\\ref{tab:hparams}.",
                 "Their values are listed in Table~S1 of the supplementary material.")
setup = "\n".join([
    "\\section{Experimental Setup}", "\\label{sec:setup}",
    baselines, "",
    L(327, 331), "",
    L(333, 337), "",
    "\\subsection{Ablation Design}", "\\label{sec:design}", design_part, "",
    "\\subsection{Implementation Details}", "\\label{sec:impl}", impl_part])

# ---------------------------------------------------------------- VI. Results
groups_old = L(409)
groups_part, sens_part = split_at(groups_old, "A test set limited to at most five articles")
groups_part = edit(groups_part, "Table~\\ref{tab:groups} and Fig.~\\ref{fig:groups} show",
                   "Table~\\ref{tab:groups} and Fig.~S5 in the supplementary material show")
eff_first = edit(L(581), "(Table~\\ref{tab:eff}, Figs.~\\ref{fig:tradeoff} and~\\ref{fig:latency})",
                 "(Table~\\ref{tab:eff}, Fig.~\\ref{fig:tradeoff}, and Fig.~S2 in the supplementary material)")
temp_par = edit(L(539), "(Fig.~\\ref{fig:temperature})", "(Fig.~S3 in the supplementary material)")
ens_par = edit(L(541), "(Fig.~\\ref{fig:ensemble})", "(Fig.~S4 in the supplementary material)")
calib_par = edit(L(668), "(Fig.~\\ref{fig:calib})", "(Fig.~S7 in the supplementary material)")
sources_par = edit(L(445), "Table~\\ref{tab:sources} splits the test set by source.",
                   "Table~S2 in the supplementary material splits the test set by source.")
factors_par = edit(L(624), "Table~\\ref{tab:factors} relates this gap",
                   "Table~S3 in the supplementary material relates this gap")
label_par = edit(L(635), "Fig.~\\ref{fig:label} shows the results per label.",
                 "Fig.~S6 in the supplementary material shows the results per label.")
lang_head = edit(L(601), "Analysis by Language and Label (RQ4)", "Analysis by Language, Label, and Source (RQ4)")
abl_head = edit(L(484), "(RQ2)", "(RQ3)")
eff_head = edit(L(557), "(RQ3)", "(RQ2)")
results = "\n".join([
    L(343, 380), "", L(382, 405), "", L(407), "", sens_part, "",
    eff_head, L(558, 580), eff_first, "", L(583), "", L(585), "", L(587, 592), "",
    abl_head, L(485, 532), L(533), "", L(535), "", L(537), "", temp_par, "", ens_par, "",
    lang_head, L(602), groups_part, "", L(411, 443), "", sources_par, "",
    factors_par, "", L(626), "", L(628, 633), "", label_par, "", L(637), "",
    L(646, 667), calib_par])  # Tables sources/factors and Fig. label moved to the supplement

# ---------------------------------------------------------------- VII. Discussion
rq_disc = edit(L(683), "For RQ2, the ablations", "For RQ3, the ablations")
# D2, D3 (restructure_log.md): sentences that only repeat numbers reported in Sections VI-B and VI-E
pract1 = edit(L(695), " For one million articles per day, the ONNX int8 teacher needs 15.1 cores, whereas StaticKD needs only 0.02 cores (Section~\\ref{sec:res-eff}).", "")
pract2 = edit(L(697), " At $\\theta=0.8$, the cascade accuracy of 0.703 is on par with that of the teacher alone (0.699). The cascade throughput is 1.92 articles per second per core compared with 0.77 for the teacher alone.", "")
disc_first = edit(L(679), "(Fig.~\\ref{fig:label})", "(Fig.~S6 in the supplementary material)")
limitations = L(701, 715)
discussion = "\n".join([
    L(677, 678),
    "\\subsection{What a Token Table Retains}", disc_first, "", L(681), "",
    "\\subsection{Where the Accuracy Comes From}", rq_disc, "", L(685), "", L(687), "",
    "\\subsection{Weak Languages and Model Selection}", L(689), "", L(691), "", L(693), "",
    "\\subsection{Practical Implications}", pract1, "", pract2, "",
    "\\subsection{Limitations}", "\\label{sec:limitations}", limitations])

# ---------------------------------------------------------------- VIII. Conclusion and back matter
avail = edit(L(726), "Table~\\ref{tab:license} lists the licenses of the assets used and released in this study.",
             "Table~S4 in the supplementary material lists the licenses of the assets used and released in this study.")
bios = r"""
\begin{IEEEbiographynophoto}{Obi Kastanya}
\todo{author biography}
\end{IEEEbiographynophoto}

\begin{IEEEbiographynophoto}{Ananta Dwi Prayoga Alwy}
\todo{author biography}
\end{IEEEbiographynophoto}

\EOD
"""
back = "\n".join([L(717, 723), "", L(725), avail, "", L(754, 758), bios, "\\end{document}", ""])

body = "\n\n".join([intro, related, method, data, setup, results, discussion, back])
# Formatting only: wide result tables in \scriptsize, Fig. per language at 0.8 text width
for lab in ["tab:main", "tab:sig", "tab:eff", "tab:ablation", "tab:groups"]:
    i = body.index("\\label{" + lab + "}")
    j = body.index("\\footnotesize", i)
    assert j - i < 200, lab
    body = body[:j] + "\\scriptsize" + body[j + len("\\footnotesize"):]
body = edit(body, "\\includegraphics[width=0.9\\textwidth]{figures/fig_per_language.pdf}",
            "\\includegraphics[width=0.8\\textwidth]{figures/fig_per_language.pdf}")
main = PREAMBLE + front + "\n" + body
(ROOT / "paper_final" / "main.tex").write_text(main, encoding="utf8", newline="\n")

# ---------------------------------------------------------------- Fig. 1 standalone source
tikz = L(146, 169)
assert tikz.lstrip().startswith("\\begin{tikzpicture}") and tikz.rstrip().endswith("\\end{tikzpicture}")
(ROOT / "paper_final" / "figures" / "fig_pipeline.tex").write_text(
    "% Fig. 1 of main.tex. Compile: pdflatex fig_pipeline\n"
    "\\documentclass[border=1pt]{standalone}\n\\usepackage{amsmath,amssymb}\n\\usepackage{tikz}\n"
    + L(22) + "\n\\begin{document}\n" + tikz + "\n\\end{document}\n", encoding="utf8", newline="\n")

# ---------------------------------------------------------------- supplementary material
supp = r"""% =====================================================================
% StaticKD -- supplementary material for the IEEE Access manuscript (main.tex)
% Floats moved out of the main text on 2026-11-01; content unchanged.
% Compile: pdflatex supplementary && bibtex supplementary && pdflatex supplementary && pdflatex supplementary
% =====================================================================
\documentclass[journal,onecolumn]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[nocompress]{cite}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage[hyphens]{url}
\usepackage{algorithm}
\usepackage{algpseudocode}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\thealgorithm}{S\arabic{algorithm}}
\begin{document}
\title{Supplementary Material for ``StaticKD: Distilling a Multilingual IPTC News Topic Classifier into a Static Token-Logit Table for Lightweight CPU Inference''}
\author{Obi~Kastanya and Ananta~Dwi~Prayoga~Alwy}
\maketitle

This document contains the algorithm, tables, and figures that the main text refers to as Algorithm~S1, Table~S1--S4, and Fig.~S1--S7.

"""


def fl(a, b, env_from=None, env_to=None):
    t = L(a, b)
    if env_from:
        t = t.replace(env_from, env_to)
    return t


supp_body = [
    # numbered in the order of first reference in main.tex
    fl(271, 280),                                        # Algorithm S1 inference
    fl(284, 319),                                      # Table S1 hyperparameters
    fl(447, 465, "table*", "table"),                     # Table S2 macro-F1 by source
    fl(603, 623),                                        # Table S3 factors behind per-language performance
    fl(728, 752),                                        # Table S4 licenses
    fl(236, 241),                                        # Fig. S1 test set heatmap
    fl(594, 599, "figure*", "figure"),                   # Fig. S2 latency, RAM, file size
    fl(543, 548, "figure*", "figure"),                   # Fig. S3 temperature
    fl(550, 555),                                        # Fig. S4 ensemble size
    fl(467, 472, "figure*", "figure"),                   # Fig. S5 groups
    fl(639, 644, "figure*", "figure"),                   # Fig. S6 per label and confusion matrix
    fl(670, 675),                                        # Fig. S7 calibration
]
supp_body = [t.replace("[!t]", "[!htbp]").replace("\\resizebox{\\columnwidth}", "\\resizebox{0.7\\textwidth}")
             for t in supp_body]
supp += "\n\n".join(supp_body) + "\n\n\\clearpage\n\\bibliographystyle{IEEEtran}\n\\bibliography{references}\n\n\\end{document}\n"
(ROOT / "paper_final" / "supplementary.tex").write_text(supp, encoding="utf8", newline="\n")
print("ok")
