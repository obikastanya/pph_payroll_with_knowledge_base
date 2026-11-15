"""Experiment harness for the v2 study, built on the proposed system in system_final.

Importing the package points system_final at the v2 workspace (v2/work), so documents, calls, and results of the
experiments never mix with the demo's workspace.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "v2"
DATA = V2 / "dataset"
WORK = V2 / "work"
os.environ.setdefault("PPH21_WORKSPACE", str(WORK))
# one payroll data dictionary per process, so that harness processes can run side by side
os.environ.setdefault("PPH21_PAYROLL_INPUTS", str(WORK / "dictionaries" / f"{os.getpid()}.json"))
if str(ROOT / "system_final") not in sys.path:
    sys.path.insert(0, str(ROOT / "system_final"))
