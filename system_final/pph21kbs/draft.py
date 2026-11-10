"""What the language model sees and writes: knowledge-base context, prompts, the model client, and the conversion of
the model output into a Delta.
"""
import ast
import hashlib
import json
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import jsonschema
from rdflib import Graph

from . import config, graph
from .config import DIGEST_MODEL, MAIN_MODEL, anthropic_key, openai_key
from .documents import normalize
from .expr import CONTEXT_FACTS, FUNCTIONS
from .kb import Constraint, FactDef, Parameter, Rule, TableVersion, fraction_text, record_to_json, validate_delta_json


# ====================================================================================================================
# Knowledge-base context
# ====================================================================================================================
MAIN_OUTPUTS = ("pph21_due", "gross_income", "annual_pph21", "taxable_income", "pph21_dtp")
NEIGHBOURS = """
PREFIX pph: <https://w3id.org/pph21kbs/ontology#>
SELECT DISTINCT ?id WHERE {
  VALUES ?f { %s }
  { ?r pph:produces ?f } UNION { ?r pph:reads ?f }
  ?r pph:elementId ?id .
}"""


def vocabulary_text(view):
    lines = ["FACTS (name | type | scope | output | label | label_id):"]
    for f in sorted(view.facts.values(), key=lambda f: (f.fact_scope, f.id)):
        lines.append(f"{f.id} | {f.fact_type} | {f.fact_scope} | {'output' if f.output else '-'} | {f.label} | "
                     f"{f.label_id}")
    lines.append("")
    lines.append("BUILT-IN CONTEXT FACTS (no rule produces them): " + ", ".join(
        f"{k} ({t}, {s})" for k, (t, s) in sorted(CONTEXT_FACTS.items())))
    lines.append("")
    lines.append("FUNCTIONS (name(arity): meaning):")
    for spec in sorted(FUNCTIONS.values(), key=lambda s: s.name):
        arity = str(spec.min_args) if spec.min_args == spec.max_args else f"{spec.min_args}..{spec.max_args or 'n'}"
        lines.append(f"{spec.name}({arity}) [{spec.scope}]: {spec.doc}")
    names = sorted({p.name for p in view.records if isinstance(p, Parameter)})
    tables = sorted({t.name for t in view.records if isinstance(t, TableVersion)})
    lines.append("")
    lines.append("PARAMETER NAMES: " + ", ".join(names))
    lines.append("TABLE NAMES: " + ", ".join(tables))
    return "\n".join(lines)


def _record_line(r):
    d = record_to_json(r, with_source=False)
    d.pop("recorded_on", None)
    if isinstance(r, TableVersion):
        rows = d.pop("rows", None)
        if rows is not None:
            rows = [{k: (fraction_text(v) if isinstance(v, Fraction) else v) for k, v in row.items()}
                    for row in r.rows]
            d["rows"] = rows[:12] + ([f"... {len(rows) - 12} more rows"] if len(rows) > 12 else [])
    if r.source:
        d["source"] = f"{r.source[0].document} {r.source[0].provision}"
    d["first_recorded"] = None
    return d


GENERIC_ID_TOKENS = {"reg", "prs", "par", "tab", "con", "input", "default", "billed"}


def _id_tokens(record_id):
    """Abbreviations in an element id (REG.BPJS.JKK_RATE -> bpjs, jkk, rate), used to match documents that write
    JKK, JP, JHT instead of the full labels."""
    parts = re.split(r"[._]", record_id.lower())
    return {p for p in parts if p.isalpha() and len(p) >= 2 and p not in GENERIC_ID_TOKENS}


def relevant_records(view, segment_text, limit=220):
    text = normalize(segment_text)
    words = set(re.findall(r"[a-z]{2,}", text))
    oldest = view.omega - timedelta(days=365)
    current = [r for r in view.records if r.valid_until is None or r.valid_until >= oldest]
    seeds = []
    for r in current:
        labels = [normalize(x) for x in (getattr(r, "label_id", ""), getattr(r, "label", "")) if x]
        if any(len(lab) >= 5 and lab in text for lab in labels):
            seeds.append(r)
        elif not isinstance(r, FactDef) and (_id_tokens(r.id) & words) - {"rate", "wage", "cap", "year", "month",
                                                                           "amount", "status", "value", "final",
                                                                           "running", "gross", "net", "tax"}:
            seeds.append(r)
    facts = set()
    for r in seeds:
        if isinstance(r, Rule):
            facts.add(r.produces)
        elif isinstance(r, FactDef):
            facts.add(r.id)
        elif isinstance(r, (Parameter, TableVersion)):
            for rule in view.rules.values():
                e = rule.expression
                if r.name in (e.params | e.tables):
                    facts.add(rule.produces)
    facts |= set(MAIN_OUTPUTS)
    ids = {r.id for r in seeds}
    if facts:
        g = Graph()
        for r in view.records:
            if isinstance(r, Rule):
                graph.record_triples(g, r)
        values = " ".join(f"<{graph.fact_iri(f)}>" for f in sorted(facts))
        ids |= {str(row.id) for row in g.query(NEIGHBOURS % values)}
    chosen = [r for r in current if r.id in ids and not isinstance(r, FactDef)]
    chosen.sort(key=lambda r: (r.kind, r.id))
    return chosen[:limit]


def context_text(view, segment_text):
    """What the model knows about the knowledge base: vocabulary, the records relevant to the document, and the
    case-data attributes that exist."""
    parts = [vocabulary_text(view)]
    recs = relevant_records(view, segment_text)
    parts.append(f"RELEVANT RECORDS OF THE KNOWLEDGE BASE ({len(recs)}; effective records at the knowledge "
                 "date; change an element by repeating its id in change, close it by setting valid_until):")
    for r in recs:
        first = view.first_recorded.get(r.id)
        d = _record_line(r)
        d["first_recorded"] = first.isoformat() if first else None
        parts.append(json.dumps(d, ensure_ascii=False))
    parts += ["", case_data_text(view)]
    return "\n".join(parts)


# ====================================================================================================================
# Case-data attributes
# ====================================================================================================================
ACCESSORS = ("income", "benefit", "hr", "employee", "employer", "case")
EXPR_FIELDS = ("expression", "condition", "assertion", "fixed_point_lower", "fixed_point_upper")


@lru_cache(maxsize=1)
def schema_fields():
    s = json.loads((config.SCHEMAS / "case.schema.json").read_text(encoding="utf-8"))["properties"]
    return {"employee": set(s["employee"]["properties"]), "employer": set(s["employer"]["properties"]) - {"policy"},
            "case": {"tax_year", "method", "start_month", "end_month"}}


def reads(text):
    """(accessor, key) pairs read with a constant key in an expression text."""
    out = set()
    try:
        tree = ast.parse(text.strip(), mode="eval")
    except (SyntaxError, AttributeError):
        return out
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ACCESSORS and n.args
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
            out.add((n.func.id, n.args[0].value))
    return out


def known(view):
    """Attributes that exist at the knowledge date: schema fields plus keys read by the base rules."""
    k = {a: set() for a in ACCESSORS}
    for a, fields in schema_fields().items():
        k[a] |= fields
    for r in view.records:
        if isinstance(r, (Rule, Constraint)):
            for e in (getattr(r, "expression", None), getattr(r, "condition", None), getattr(r, "assertion", None)):
                if e is not None:
                    for a, key in reads(e.text):
                        k[a].add(key)
    return k


def case_data_text(view):
    k = known(view)
    lines = ["CASE DATA (the payroll inputs that exist; rules read them with these accessors and exact names):"]
    for a in ACCESSORS:
        lines.append(f"- {a}(...): " + (", ".join(f"'{x}'" for x in sorted(k[a])) or "(none yet)"))
    lines.append("Use these names exactly. If the document needs an input that is not listed (for example a company "
                 "allowance or an eligibility status), you may introduce it with a plain descriptive name; it will be "
                 "reported to the reviewer as a new payroll input.")
    return "\n".join(lines)


def new_inputs(view, delta):
    """Attributes a Delta reads that are not in known(view)."""
    k = known(view)
    found = set()
    for el in (delta.get("add") or []) + (delta.get("change") or []):
        for f in EXPR_FIELDS:
            v = el.get(f)
            if isinstance(v, str):
                found |= reads(v)
    return sorted(f"{a}('{key}')" for a, key in found if key not in k[a])


# ====================================================================================================================
# Prompts
# ====================================================================================================================
RELEVANCE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["relevant", "layer", "reason", "quotes", "effective_from", "effective_from_quote",
                 "effective_until", "effective_until_quote", "subjects"],
    "properties": {
        "relevant": {"type": "boolean"},
        "layer": {"enum": ["regulation", "company"]},
        "reason": {"type": "string"},
        "quotes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["provision", "quote"],
            "properties": {"provision": {"type": "string"}, "quote": {"type": "string"}}}},
        "effective_from": {"type": ["string", "null"]},
        "effective_from_quote": {"type": ["string", "null"]},
        "effective_until": {"type": ["string", "null"]},
        "effective_until_quote": {"type": ["string", "null"]},
        "subjects": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["kind", "value", "quote"],
            "properties": {"kind": {"enum": ["sector", "klu", "employee_group", "employer_group", "other"]},
                           "value": {"type": "string"}, "quote": {"type": "string"}}}},
    },
}

SYSTEM_RELEVANCE = """You assess whether a legal document changes how Indonesian income tax article 21 (PPh 21) is
computed for permanent employees (pegawai tetap), including the social security contributions and benefits that
enter their gross income or deductions, and the company payroll rules of a company policy.

A document is RELEVANT when it changes a value, rate, threshold, table, rounding, classification, deduction,
facility, validity period, or calculation step for permanent employees. It is NOT relevant when it only concerns
administration or reporting, other taxpayers or subjects (non-permanent employees, pensioners, civil servants, other
taxes), restates existing rules without change, or changes contributions that do not affect PPh 21.

Every claim needs verbatim quotes copied exactly from the document text you are given (at least 20 characters each;
keep the original spelling, do not fix typos or OCR errors). effective_from/effective_until are ISO dates of the first
day of the first tax period or contribution month covered and the last day of the last one (null if not stated), each
with its quote. subjects lists sectors, business classification codes (KLU), employee or employer groups the document
limits itself to, each with a quote. Answer in the JSON schema."""

SYSTEM_DRAFT = """You maintain a versioned knowledge base (KB) of the rules that compute Indonesian income tax article 21
(PPh 21) for permanent employees, and you translate one legal document into an UPDATE (Delta) of that KB.

KNOWLEDGE BASE
- Records have kinds: rule, parameter, table, constraint, fact. Every record has an id, valid_from/valid_until (legal
  validity), recorded_on (knowledge date), and source quotes. Records are immutable; an update adds records.
- Delta = add (new ids), change (new version of an existing id: repeat the id and give the complete new record),
  remove (tombstone an id). To end an old provision, put it in change with valid_until set (do not remove it).
- rule: produces one fact with an expression, optional condition, scope "period" (tax month) or "year" (tax year),
  layer "regulation" (from laws/regulations) or "company" (from a company policy), modality "mandatory" (binding
  regulation), "default" (applies unless something else is set), or "optional" (a choice a company may adopt).
  Rule scope must equal the scope of the fact it produces. Company rules need policy = the policy document id and must
  not be mandatory.
- Conflict resolution when several valid rules produce the same fact: (1) higher rank wins: mandatory regulation 4 >
  company 3 > adopted optional 2 > default 1; (2) a rule that lists another in "overrides" beats it (exceptions, lex
  specialis); (3) otherwise the rule with the later valid_from wins (lex posterior). A newer rule with a later
  valid_from therefore replaces an older one without closing it, but closing old provisions that a document revokes or
  ends is still required. A company rule that loses to a mandatory rule with a different value is reported as a
  conflict with its conflict_code (C1-C10).
- parameter: a named value (value_type money, int, rate, exact, bool, category) read with param('name'); the version
  valid on the evaluated date with the latest valid_from is used. A new value for an existing parameter name is a NEW
  parameter id (e.g. PAR.NAME.2025) with its own valid_from; close the previous id only if the document ends it.
- table: named table (lookup key->value; bracket key+lower<amount<=upper -> value; progressive layers lower/upper/
  rate; set of keys with attributes). Large annex tables are already extracted: refer to them with rows_ref
  (extracted_table id, columns mapping the table's columns to key/lower/upper/value/rate, value_scale "percent" when
  the column holds percentages, filter by column values) instead of copying rows.
- constraint: a mandatory assertion checked on results (conflict codes C8/C10), for minimum entitlements.
- fact: declare a new fact only if no existing fact fits; never mark new facts as output.

EXPRESSION LANGUAGE: a safe Python subset over facts (names), numbers, strings, True/False/None, + - * / comparisons,
and/or/not, x if c else y, and the listed functions. Arithmetic is exact: write rates as 5 / 100 or dec('0.05'), never
0.05 (floats are rejected). Money facts must be whole rupiah: use round(x, unit, mode) with mode down, up, truncate,
half_up or half_even (unit 1 = rupiah, 1000 = thousands). Case data: income('component'), benefit('kind'),
hr('item'), employee('attr'), employer('attr'), case('attr'); context facts: month, tax_year, is_final_period,
first_month, final_month, months_employed.

CONVENTIONS
- ids: regulation rules REG.<AREA>.<NAME>, company rules PRS.<POLICY>.<NAME>, parameters PAR.<NAME>.<YEAR>, tables
  TAB.<NAME>.<YEAR>, constraints CON.<NAME>; fact names lower_case. Reuse existing facts, parameter names and table
  names whenever they mean the same thing.
- valid_from = first day of the first tax period or contribution month the provision covers, even if that is before
  the issue date (retroactive provisions keep their legal start). valid_until = last day of the last month covered,
  or null if open-ended.
- recorded_on = the document's issue date given in the metadata, for every record.
- source: for every element at least one quote copied verbatim from the document text (at least 20 characters), with
  the provision (e.g. "Pasal 4 ayat (2) huruf b") and the PDF page shown in the text. Every number of 100 or more and
  every rate you write must appear in a quote of that element (e.g. 9.559.600, Rp10.000.000,00, 0,24%). Every date
  you set must be supported by a quote of that element (e.g. "Masa Pajak Januari 2025", "1 Juli 2023").
- If the document does not change the computation (see relevance), return relevant=false and empty lists.
- Keep the Delta minimal: only elements the document requires; do not restate unchanged rules.
- note: one or two sentences on the interpretation you made, if any.

OUTPUT FORMAT (JSON following the schema). Every element has kind (rule, parameter, table, constraint, fact), id,
label (English), label_id (Indonesian), valid_from, valid_until (ISO dates or null), recorded_on, source (list of
{document, provision, page, quote}), and "fields": a list of {name, value} strings with the attributes of its kind:
- rule: layer, modality, scope, produces, expression, and when needed condition, overrides (ids separated by commas),
  policy, conflict_code, fixed_point_lower and fixed_point_upper (both expressions);
- parameter: name, value (plain number like 9450000 or 0.0024, true/false, or text), value_type (money, int, rate,
  exact, bool, category);
- table: name, table_kind, and either rows (a JSON array of row objects: lookup {key, value}; bracket {key, lower,
  upper, value}; progressive {lower, upper, rate}; set {key, ...attributes}) or rows_ref (a JSON object
  {"extracted_table": id, "columns": {"key": column, ...}, "value_scale": "percent" if needed, "filter": {column: value}});
- constraint: scope, assertion, conflict_code, and condition when needed;
- fact: fact_type, fact_scope, output (false).
Removed elements go in remove as {id, recorded_on, source}.

GENERIC EXAMPLE (illustrative, not from any real document): a regulation issued 2024-02-10 raises a contribution wage
cap from 9.000.000 to 9.450.000 starting with the March 2024 contribution. Delta: add one element
{"kind": "parameter", "id": "PAR.EXAMPLE_WAGE_CAP.2024", "label": "example wage cap", "label_id": "batas upah contoh",
"valid_from": "2024-03-01", "valid_until": null, "recorded_on": "2024-02-10",
"fields": [{"name": "name", "value": "example_wage_cap"}, {"name": "value", "value": "9450000"},
{"name": "value_type", "value": "money"}], "source": [{"document": "...", "provision": "angka 2", "page": 1,
"quote": "<verbatim text containing Rp9.450.000 and the March 2024 start>"}]}; nothing else, because the existing
rule already reads param('example_wage_cap') (the name of the existing parameter).

MODELLING GUIDANCE
- Change the most specific fact the document sets. If a document sets a premium, rate, deduction, ceiling, rounding
  or eligibility, produce that fact and let the existing rules compute the totals (take_home_pay,
  employee_tax_burden, pph21_due, ...). Rewrite a total only if the document itself defines that total.
- Do not add rules for consequences the document does not state (for example rounding a total that the document does
  not round).
- A company policy: go through the payroll items a policy can set and produce the fact for each item the policy
  states, even when its value equals today's regulation (the policy keeps binding the company if the regulation
  changes): who bears the tax (withholding_method: 'gross' when deducted from pay, 'gross_up' for a tax allowance,
  'employer_borne'), employee and employer premiums (jht_employee, jp_employee, health_employee,
  health_premium_employer, jkk_rate), whether employer premiums count as income (employer_premiums_taxable), job
  expense, rounding, the final period and refunds for leavers (pph21_due, refund_to_employee).
- When the document defines its own intermediate amounts, declare new facts for them instead of overriding existing
  facts that mean something else.
- Read case data only with the attribute names listed under CASE DATA, unless the document introduces a new input.
- Before writing, go through the document provision by provision and make sure every provision that changes the
  computation (values, rates, thresholds, exemptions or ceilings, eligibility conditions, periods, calculation steps,
  who bears or receives the tax) has an element."""

SYSTEM_REPAIR_SUFFIX = """

REPAIR: your previous Delta for this document failed the verification gates. The gate messages are below. Return a
corrected complete Delta (not a diff), keeping what was right."""


def metadata_text(event, documents):
    lines = ["DOCUMENT METADATA"]
    for d in documents:
        lines.append(f"- id: {d['id']}; title: {d.get('title', '')}; issue date (recorded_on): {d.get('issued')}")
    lines.append(f"- layer: {event.layer}")
    return "\n".join(lines)


def relevance_user(event, documents):
    return metadata_text(event, documents) + "\n\nAssess the relevance of the document above."


def draft_user(event, documents, relevance=None):
    text = metadata_text(event, documents)
    if relevance:
        text += ("\n\nRELEVANCE ASSESSMENT (from a previous step): relevant=" + str(relevance.get("relevant"))
                 + f"; effective_from={relevance.get('effective_from')}; effective_until="
                 f"{relevance.get('effective_until')}; reason: {relevance.get('reason', '')}")
    return text + "\n\nWrite the Delta for this document."


def repair_user(event, documents, previous, messages):
    # the repair instruction is in the user message so that the system prompt (and the cached prefix) stay the same
    return (metadata_text(event, documents) + SYSTEM_REPAIR_SUFFIX
            + "\n\nPREVIOUS DELTA:\n" + json.dumps(previous, ensure_ascii=False)
            + "\n\nGATE MESSAGES:\n" + "\n".join(f"- {m}" for m in messages)
            + "\n\nReturn the corrected complete Delta.")


# ====================================================================================================================
# Model client and cost ledger
# ====================================================================================================================
# USD per million tokens (October 2026); OpenAI cached input is counted at the full price, never less than spent
PRICES = {
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_read": 0.20, "cache_write": 5.0},
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0, "cache_read": 0.20, "cache_write": 2.5},
    "gpt-5.4-mini": {"input": 0.75, "output": 4.50, "cache_read": 0.75, "cache_write": 0.75},
    "gpt-6.1-sol": {"input": 2.0, "output": 10.0, "cache_read": 0.20, "cache_write": 2.0},
}


class BudgetExceeded(RuntimeError):
    pass


class LLMError(RuntimeError):
    pass


@dataclass
class Reply:
    text: str
    stop_reason: str
    model: str
    usage: dict                      # input, output, cache_read, cache_write
    seconds: float = 0.0
    error: str = ""


def cost(model, usage):
    p = PRICES.get(model)
    if p is None:
        return 0.0
    c = (usage.get("input", 0) * p["input"] + usage.get("output", 0) * p["output"]
         + usage.get("cache_read", 0) * p["cache_read"] + usage.get("cache_write", 0) * p["cache_write"]) / 1e6
    return round(c, 6)


def priced(model):
    if model not in PRICES:
        raise LLMError(f"no price for model {model} in draft.PRICES")
    return model


def _entries(path):
    """Logged calls of one file; a line still being written by another thread is skipped."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines() if path.exists() else []:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def spent_total(root=None, provider=None):
    """Cost of every logged call under root (default: the workspace), or of one provider's calls."""
    return round(sum(e.get("cost_usd") or 0.0 for path in Path(root or config.CALLS).glob("*/calls.jsonl")
                     for e in _entries(path) if provider is None or e.get("provider") == provider), 6)


class Ledger:
    """Call log and spending limits of one kind of work. Every call is one line of <root>/<name>/calls.jsonl; the full
    prompt is kept once under prompts/<sha256>.json. A call is refused once the provider's total (config.BUDGET_USD)
    or this ledger's own limit is reached."""

    _lock = threading.Lock()

    def __init__(self, name, limit_usd=None, root=None, total_limit_usd=None):
        self.name = name
        self.root = Path(root or config.CALLS)
        self.dir = self.root / name
        (self.dir / "prompts").mkdir(parents=True, exist_ok=True)
        self.calls = self.dir / "calls.jsonl"
        self.limit_usd = limit_usd
        self.total_limit = config.BUDGET_USD if total_limit_usd is None else total_limit_usd

    def spent(self):
        return round(sum(e.get("cost_usd") or 0.0 for e in _entries(self.calls)), 6)

    def check(self, provider):
        limit = self.total_limit.get(provider) if isinstance(self.total_limit, dict) else self.total_limit
        total = spent_total(self.root, provider)
        if limit is not None and total >= limit:
            raise BudgetExceeded(f"{provider} spend {total:.4f} USD reached the limit {limit} USD")
        if self.limit_usd is not None and self.spent() >= self.limit_usd:
            raise BudgetExceeded(f"{self.name} spend reached its limit {self.limit_usd} USD")

    def save_prompt(self, prompt):
        text = json.dumps(prompt, ensure_ascii=False, sort_keys=True)
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        path = self.dir / "prompts" / f"{sha}.json"
        if not path.exists():
            path.write_text(text, encoding="utf-8")
        return sha, f"prompts/{sha}.json"

    def log(self, entry):
        with self._lock, open(self.calls, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def spent_prefix(self, call_prefix):
        """Cost of the calls whose call_id starts with call_prefix (one document)."""
        return round(sum(e.get("cost_usd") or 0.0 for e in _entries(self.calls)
                         if str(e.get("call_id") or "").startswith(call_prefix)), 6)


class Client:
    provider = "none"
    model = ""

    def __init__(self, ledger):
        self.ledger = ledger

    def complete(self, *, system, prefix, user, schema, schema_name, effort, step, document="", event="",
                 draft_no=None, call_id=None, max_tokens=32000):
        """system: text; prefix: text blocks shared by the drafts of one document (cached); user: the final block;
        draft_no: which draft of the document this call writes. Returns (Reply, parsed JSON or None, log entry)."""
        self.ledger.check(self.provider)
        sha, pfile = self.ledger.save_prompt({"model": self.model, "effort": effort, "system": system,
                                              "prefix": prefix, "user": user, "schema_name": schema_name})
        t0 = time.time()
        try:
            reply = self._call(system, prefix, user, schema, schema_name, effort, max_tokens,
                               cache=step != "relevance")
            error = None
        except Exception as e:  # noqa: BLE001 - a refusal or API error is a failed draft, recorded
            reply = Reply("", "error", self.model, {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0})
            error = f"{type(e).__name__}: {e}"[:500]
        reply.seconds = round(time.time() - t0, 2)
        error = error or reply.error or None
        parsed = None
        if reply.text:
            try:
                parsed = json.loads(reply.text)
            except json.JSONDecodeError as e:
                error = error or f"JSONDecodeError: {e}"
        entry = {"call_id": call_id, "ledger": self.ledger.name,
                 "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                 "model_requested": self.model, "model_reported": reply.model, "provider": self.provider,
                 "effort": effort, "step": step, "document": document, "event": event, "draft_no": draft_no,
                 "prompt_sha256": sha, "prompt_file": pfile, "output_raw": reply.text,
                 "stop_reason": reply.stop_reason, "usage": reply.usage, "cost_usd": cost(self.model, reply.usage),
                 "seconds": reply.seconds, "error": error}
        self.ledger.log(entry)
        return reply, parsed, entry

    def complete_many(self, requests):
        """Independent requests (keyword dicts of complete()), one after another; results in the same order."""
        return [self.complete(**r) for r in requests]

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        raise NotImplementedError


class AnthropicClient(Client):
    """Claude with structured output (JSON schema), reasoning effort, and prompt caching of the shared prefix. The
    relevance call has a prefix of its own, so it is not cached (a cache write costs 1.25 x input)."""
    provider = "anthropic"

    def __init__(self, ledger, model=MAIN_MODEL):
        super().__init__(ledger)
        import anthropic
        key = anthropic_key()
        if not key:
            raise LLMError("no Anthropic key in the environment or .env")
        self.model = priced(model)
        self.api = anthropic.Anthropic(api_key=key, max_retries=3)

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        blocks = [{"type": "text", "text": t} for t in prefix]
        if blocks and cache:
            blocks[-1]["cache_control"] = {"type": "ephemeral"}
        blocks.append({"type": "text", "text": user})
        sys_block = {"type": "text", "text": system}
        if cache:
            sys_block["cache_control"] = {"type": "ephemeral"}
        params = {"model": self.model, "max_tokens": max_tokens, "system": [sys_block],
                  "messages": [{"role": "user", "content": blocks}],
                  "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}}}
        with self.api.messages.stream(**params) as stream:
            msg = stream.get_final_message()
        u = msg.usage
        usage = {"input": u.input_tokens or 0, "output": u.output_tokens or 0,
                 "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                 "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0}
        if msg.stop_reason == "refusal":
            category = getattr(getattr(msg, "stop_details", None), "category", None) or "no category"
            return Reply("", "refusal", msg.model, usage, error=f"the model declined the request ({category})")
        text = next((b.text for b in msg.content if b.type == "text"), "")
        return Reply(text, msg.stop_reason or "", msg.model, usage)


class OpenAIClient(Client):
    """An OpenAI model with structured output: maps documents (digest.py) and runs the app's assistant."""
    provider = "openai"

    def __init__(self, ledger, model=DIGEST_MODEL):
        super().__init__(ledger)
        import openai
        key = openai_key()
        if not key:
            raise LLMError("no OpenAI key in the environment or .env")
        self.model = priced(model)
        self.api = openai.OpenAI(api_key=key, max_retries=3)

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        content = [{"type": "input_text", "text": t} for t in prefix] + [{"type": "input_text", "text": user}]
        resp = self.api.responses.create(
            model=self.model, instructions=system, input=[{"role": "user", "content": content}],
            reasoning={"effort": effort}, max_output_tokens=max_tokens,
            text={"format": {"type": "json_schema", "name": schema_name, "schema": strict_schema(schema),
                             "strict": True}})
        u = resp.usage
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        usage = {"input": (u.input_tokens or 0) - cached, "output": u.output_tokens or 0, "cache_read": cached,
                 "cache_write": 0}
        return Reply(resp.output_text or "", resp.status or "", resp.model, usage)


def strict_schema(schema):
    """OpenAI strict mode rejects format keywords and $schema/$id/title at the root."""
    def walk(x):
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items() if k not in ("$schema", "$id", "title", "format")}
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x
    return walk(schema)


class MockClient(Client):
    """Returns prepared outputs in order (dicts are serialised) at zero cost. For tests and dry runs."""
    provider = "mock"

    def __init__(self, ledger, outputs, model="mock"):
        super().__init__(ledger)
        self.outputs = list(outputs)
        self.model = model
        self.seen = []

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        self.seen.append({"system": system, "prefix": prefix, "user": user, "schema_name": schema_name})
        if not self.outputs:
            raise LLMError("mock client has no more outputs")
        out = self.outputs.pop(0)
        if isinstance(out, Exception):
            raise out
        text = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
        return Reply(text, "end_turn", self.model, {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0})


# ====================================================================================================================
# Conversion of the model output into a Delta
# ====================================================================================================================
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
                v = r["value"]
                row = {"key": str(r["key"]), "value": v if isinstance(v, str) else str(v)}
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
        missing = [k for k in ("add", "change", "remove") if k not in llm]
        if missing:
            raise ConversionError(f"malformed output: missing {', '.join(missing)}")
        if not (llm["add"] or llm["change"] or llm["remove"]) and llm.get("relevant", True):
            raise ConversionError("empty update for a document judged relevant (state relevant=false instead)")
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
    """Inverse direction (Delta -> compact model form), for converter tests and mock runs."""
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
