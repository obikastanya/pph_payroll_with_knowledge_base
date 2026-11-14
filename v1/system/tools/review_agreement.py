r"""Agreement between the gold author and the second reader (PANDUAN Tahap 7: Krippendorff's alpha).

    env\Scripts\python system\tools\review_agreement.py

Reads review/gold/regulasi.banding.csv and review/gold/kebijakan.banding.csv (stage 2 of the second reader, built on
the blind stage-1 coding) and writes docs/hasil/kesepakatan_emas.json. Variables:
  presence     the element exists in the coding (gold always 1 for its rows; reviewer-only units are 0 for gold)
  valid_from, valid_until (regulation)   the dates both coded (nominal)
  conflict code (policies)               "-", "none" and empty mean no conflict
  value        only "same / different" was recorded, so percent agreement is reported, not alpha
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "system"))

from pph21kbs.analysis.agreement import cohen_kappa, krippendorff_alpha_nominal, percent_agreement  # noqa: E402

YES = {"1", "ya", "yes", "true"}


def _flag(v):
    return 1 if str(v).strip().lower() in YES else 0


def _code(v):
    v = (v or "").strip()
    return "none" if v in ("", "-", "none", "tidak") else v


def regulation():
    rows = list(csv.DictReader(open(ROOT / "review/gold/regulasi.banding.csv", encoding="utf-8")))
    pres = [[_flag(r["present_gold"]), _flag(r["present_reviewer"])] for r in rows]
    both = [r for r in rows if _flag(r["present_gold"]) and _flag(r["present_reviewer"])]
    vf = [[r["valid_from_gold"] or None, r["valid_from_reviewer"] or None] for r in both
          if r["valid_from_gold"] or r["valid_from_reviewer"]]
    # a changed element keeps its original valid_from in the gold while the reader wrote the start of the change
    # (notation, not disagreement): valid_from is compared on added elements only
    changed = _changed_ids()
    vf_add = [[r["valid_from_gold"] or None, r["valid_from_reviewer"] or None] for r in both
              if (r["valid_from_gold"] or r["valid_from_reviewer"]) and r["gold_id"].split(" ")[0] not in changed]
    vu = [[r["valid_until_gold"] or "open", r["valid_until_reviewer"] or "open"] for r in both
          if r["valid_from_gold"] or r["valid_from_reviewer"]]
    val = [(1, 1 if r["value_same"] == "ya" else 0) for r in both if r["value_same"] in ("ya", "tidak")]
    # sensitivity: without the event the reviewer could not code blind (E13)
    blind = [r for r in rows if r["event"] != "E13"]
    return {"units": len(rows), "both_present": len(both),
            "alpha_presence": krippendorff_alpha_nominal(pres),
            "agreement_presence": percent_agreement([tuple(x) for x in pres]),
            "alpha_valid_from": krippendorff_alpha_nominal(vf),
            "alpha_valid_from_added_elements": krippendorff_alpha_nominal(vf_add),
            "units_valid_from_added_elements": len(vf_add),
            "alpha_valid_until": krippendorff_alpha_nominal(vu),
            "agreement_value": percent_agreement(val),
            "alpha_presence_without_E13": krippendorff_alpha_nominal(
                [[_flag(r["present_gold"]), _flag(r["present_reviewer"])] for r in blind]),
            "verdicts": _count(rows)}


def policy():
    rows = list(csv.DictReader(open(ROOT / "review/gold/kebijakan.banding.csv", encoding="utf-8")))
    pres = [[_flag(r["present_gold"]), _flag(r["present_reviewer"])] for r in rows]
    both = [r for r in rows if _flag(r["present_gold"]) and _flag(r["present_reviewer"])]
    codes = [[_code(r["conflict_gold"]), _code(r["conflict_reviewer"])] for r in both]
    val = [(1, 1 if r["value_same"] == "ya" else 0) for r in both if r["value_same"] in ("ya", "tidak")]
    return {"units": len(rows), "both_present": len(both),
            "alpha_presence": krippendorff_alpha_nominal(pres),
            "agreement_presence": percent_agreement([tuple(x) for x in pres]),
            "alpha_conflict_code": krippendorff_alpha_nominal(codes),
            "kappa_conflict_code": cohen_kappa([tuple(x) for x in codes]),
            "agreement_conflict_code": percent_agreement([tuple(x) for x in codes]),
            "agreement_value": percent_agreement(val), "verdicts": _count(rows)}


def _changed_ids():
    out = set()
    for path in (ROOT / "dataset" / "12_emas" / "delta").glob("GOLD-E*.json"):
        d = json.loads(path.read_text(encoding="utf-8"))
        out |= {e["id"] for e in d["change"]}
    return out


def _count(rows):
    out = {}
    for r in rows:
        out[r["verdict"]] = out.get(r["verdict"], 0) + 1
    return out


def main():
    res = {"regulation_E01_E13": regulation(), "policy_SP01_SP14": policy()}
    out = ROOT / "docs" / "hasil" / "kesepakatan_emas.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
