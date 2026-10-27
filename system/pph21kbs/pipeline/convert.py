"""Deterministic converter from the LLM output (system/schemas/delta_llm.schema.json, compact form) to a Delta
(system/schemas/delta.schema.json), format_data.md 2.3.

The LLM writes common attributes as properties and kind-specific attributes as name/value pairs ("fields"; rows and
rows_ref as JSON text, overrides as ids separated by commas). The converter restores types from value_type, fills
policy = document id for a company rule without policy, drops empty values, and validates the result against the full
Delta schema. A ConversionError carries the reason (a G1 failure that the repair round sees).
"""
import json

import jsonschema

from ..kb.delta import validate_delta_json

FIELDS = {
    "rule": ("layer", "modality", "scope", "produces", "condition", "expression", "overrides", "policy",
             "conflict_code", "fixed_point_lower", "fixed_point_upper"),
    "parameter": ("name", "value", "value_type"),
    "table": ("name", "table_kind", "rows", "rows_ref"),
    "constraint": ("scope", "condition", "assertion", "conflict_code"),
    "fact": ("fact_type", "fact_scope", "output", "unit"),
}


class ConversionError(ValueError):
    pass


def _source(items):
    out = []
    for s in items or []:
        d = {"document": s["document"], "provision": s["provision"], "quote": s["quote"]}
        if s.get("page") is not None:
            d["page"] = s["page"]
        out.append(d)
    return out


def _number_text(text):
    t = str(text).strip().replace("Rp", "").replace(" ", "")
    if t.count(".") > 1 or ("," in t and "." in t):        # Indonesian thousands separators
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    return t


def _param_value(v, vtype, element_id):
    if v in (None, ""):
        raise ConversionError(f"{element_id}: parameter without value")
    if vtype in ("money", "int"):
        try:
            return int(_number_text(v))
        except ValueError:
            raise ConversionError(f"{element_id}: {vtype} value {v!r} is not a whole number") from None
    if vtype in ("rate", "exact"):
        return _number_text(v)
    if vtype == "bool":
        t = str(v).strip().lower()
        if t not in ("true", "false"):
            raise ConversionError(f"{element_id}: bool value {v!r}")
        return t == "true"
    return v


def _bound(v):
    if v is None or str(v).strip() in ("", "null", "None"):
        return None
    return int(_number_text(v))


def _rows(kind, rows, element_id):
    if not isinstance(rows, list):
        raise ConversionError(f"{element_id}: rows must be a JSON array")
    out = []
    for r in rows:
        if not isinstance(r, dict):
            raise ConversionError(f"{element_id}: table row {r!r} is not an object")
        try:
            if kind == "lookup":
                row = {"key": str(r["key"]), "value": str(r["value"]) if not isinstance(r["value"], str) else r["value"]}
            elif kind == "bracket":
                row = {"key": None if r.get("key") in (None, "") else str(r["key"]),
                       "lower": _bound(r.get("lower")) or 0, "upper": _bound(r.get("upper")),
                       "value": _number_text(r["value"])}
            elif kind == "progressive":
                row = {"lower": _bound(r.get("lower")) or 0, "upper": _bound(r.get("upper")),
                       "rate": _number_text(r.get("rate", r.get("value")))}
            else:
                row = {"key": str(r["key"])}
                row.update({k: v for k, v in r.items() if k != "key"})
        except (ValueError, TypeError, KeyError) as e:
            raise ConversionError(f"{element_id}: table row {r}: {e}") from None
        out.append(row)
    return out


def _json_field(text, element_id, name):
    try:
        return json.loads(text) if isinstance(text, str) else text
    except json.JSONDecodeError as e:
        raise ConversionError(f"{element_id}: field {name} is not valid JSON: {e.msg}") from None


def _element(e, doc_id):
    kind, eid = e.get("kind"), e.get("id")
    if kind not in FIELDS:
        raise ConversionError(f"{eid}: unknown kind {kind!r}")
    f = {}
    for p in e.get("fields") or []:
        name = p["name"].strip()
        if name not in FIELDS[kind]:
            raise ConversionError(f"{eid}: field {name!r} does not belong to a {kind}")
        if p["value"] not in (None, ""):
            f[name] = p["value"]
    out = {"kind": kind, "id": eid, "recorded_on": e.get("recorded_on")}
    for k in ("label", "label_id", "valid_from", "valid_until"):
        if e.get(k):
            out[k] = e[k]
    if kind == "rule":
        for k in ("layer", "modality", "scope", "produces", "condition", "expression", "policy", "conflict_code"):
            if k in f:
                out[k] = f[k]
        if "overrides" in f:
            out["overrides"] = [x.strip() for x in f["overrides"].replace(";", ",").split(",") if x.strip()]
        if "fixed_point_lower" in f or "fixed_point_upper" in f:
            out["fixed_point"] = {"lower": f.get("fixed_point_lower"), "upper": f.get("fixed_point_upper")}
        if out.get("layer") == "company" and not out.get("policy"):
            out["policy"] = doc_id
    elif kind == "parameter":
        out.update(name=f.get("name"), value_type=f.get("value_type"))
        out["value"] = _param_value(f.get("value"), f.get("value_type"), eid)
    elif kind == "table":
        out.update(name=f.get("name"), table_kind=f.get("table_kind"))
        if "rows_ref" in f:
            ref = _json_field(f["rows_ref"], eid, "rows_ref")
            if not isinstance(ref, dict) or "extracted_table" not in ref or "columns" not in ref:
                raise ConversionError(f"{eid}: rows_ref needs extracted_table and columns")
            out["rows_ref"] = {k: v for k, v in ref.items() if k in ("extracted_table", "columns", "value_scale",
                                                                        "filter") and v not in (None, {}, "unit")}
        else:
            out["rows"] = _rows(f.get("table_kind"), _json_field(f.get("rows", "[]"), eid, "rows"), eid)
    elif kind == "constraint":
        for k in ("scope", "condition", "assertion", "conflict_code"):
            if k in f:
                out[k] = f[k]
    elif kind == "fact":
        out.update(fact_type=f.get("fact_type"), fact_scope=f.get("fact_scope"),
                   output=str(f.get("output", "false")).strip().lower() == "true")
        if f.get("unit"):
            out["unit"] = f["unit"]
    out["source"] = _source(e.get("source"))
    return {k: v for k, v in out.items() if v is not None}


def to_delta(llm, delta_id, event_id, document):
    """document: {"id", "title", "issued"}. Returns a Delta that follows delta.schema.json."""
    try:
        doc_id = document["id"]
        delta = {"delta_id": delta_id, "event_id": event_id, "document": dict(document),
                 "relevant": bool(llm.get("relevant", True)),
                 "add": [_element(e, doc_id) for e in llm.get("add") or []],
                 "change": [_element(e, doc_id) for e in llm.get("change") or []],
                 "remove": [{"id": r["id"], "recorded_on": r["recorded_on"], "source": _source(r.get("source"))}
                            for r in llm.get("remove") or []],
                 "note": llm.get("note") or ""}
        if llm.get("adopts"):
            delta["adopts"] = list(llm["adopts"])
        validate_delta_json(delta)
    except ConversionError:
        raise
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path)
        raise ConversionError(f"Delta schema: {path}: {e.message[:200]}") from None
    except (KeyError, TypeError, ValueError) as e:
        raise ConversionError(f"malformed output: {e}") from None
    return delta


def to_llm(delta):
    """Inverse direction (gold Delta -> compact LLM form): tests of the converter and mock runs."""
    def element(e):
        fields = []
        for k, v in e.items():
            if k in ("kind", "id", "label", "label_id", "valid_from", "valid_until", "recorded_on", "source"):
                continue
            if k == "fixed_point":
                fields += [{"name": "fixed_point_lower", "value": str(v["lower"])},
                           {"name": "fixed_point_upper", "value": str(v["upper"])}]
            elif k == "overrides":
                fields.append({"name": "overrides", "value": ", ".join(v)})
            elif k in ("rows", "rows_ref"):
                fields.append({"name": k, "value": json.dumps(v, ensure_ascii=False, default=str)})
            elif isinstance(v, bool):
                fields.append({"name": k, "value": str(v).lower()})
            else:
                fields.append({"name": k, "value": str(v)})
        return {"kind": e["kind"], "id": e["id"], "label": e.get("label", ""), "label_id": e.get("label_id", ""),
                "valid_from": e.get("valid_from"), "valid_until": e.get("valid_until"),
                "recorded_on": e["recorded_on"], "fields": fields,
                "source": [{"document": s["document"], "provision": s["provision"], "page": s.get("page"),
                            "quote": s["quote"]} for s in e.get("source", [])]}
    return {"relevant": delta.get("relevant", True), "add": [element(e) for e in delta["add"]],
            "change": [element(e) for e in delta["change"]],
            "remove": [{"id": r["id"], "recorded_on": r["recorded_on"],
                        "source": [{"document": s["document"], "provision": s["provision"], "page": s.get("page"),
                                    "quote": s["quote"]} for s in r.get("source", [])]} for r in delta["remove"]],
            "adopts": list(delta.get("adopts") or []), "note": delta.get("note") or ""}
