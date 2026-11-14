#!/usr/bin/env bash
# Compile paper_final/main.tex and supplementary.tex (IEEE Access class); print page counts and LaTeX problems.
# Usage: bash paper_writing/restructure/build.sh             (compile only; main.tex is edited by hand)
#        bash paper_writing/restructure/build.sh --assemble  (regenerate main.tex from commit b4bf5e6 first; overwrites edits)
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if [ "${1:-}" = "--assemble" ]; then
  env/Scripts/python.exe paper_writing/restructure/assemble_restructure.py --force || exit 1
fi
# ieeeaccess.cls and its fonts are licensed and not in git; copy them from the local template folder
TPL=paper_writing/template_ieeeaccess/ACCESS_latex_template_20260513
cp "$TPL"/{ieeeaccess.cls,spotcolor.sty,logo.png,notaglinelogo.png,bullet.png} "$TPL"/t1* paper_final/
cd paper_final/figures && pdflatex -interaction=nonstopmode fig_pipeline.tex >/dev/null 2>&1; cd ..
for f in main supplementary; do
  rm -f $f.aux $f.bbl
  (pdflatex -interaction=nonstopmode $f.tex; bibtex $f; pdflatex -interaction=nonstopmode $f.tex; pdflatex -interaction=nonstopmode $f.tex) >/dev/null 2>&1
  echo "== $f"; grep -n "Output written\|^! \|Reference .* undefined\|Citation .* undefined" $f.log | head -20
done
