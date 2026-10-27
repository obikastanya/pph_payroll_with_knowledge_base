"""Prompts of the acquisition pipeline (akuisisi.md 3.2-3.5). Frozen with the pipeline at tag alur-beku (Tahap 11).

The example in SYSTEM_DRAFT is generic (not taken from any test event). Prompts are written in English; documents
are Indonesian.
"""

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
rule already reads param('example_wage_cap') (the name of the existing parameter)."""

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
    import json
    # the repair instruction is in the user message so that the system prompt (and the cached prefix) stay the same
    return (metadata_text(event, documents) + SYSTEM_REPAIR_SUFFIX
            + "\n\nPREVIOUS DELTA:\n" + json.dumps(previous, ensure_ascii=False)
            + "\n\nGATE MESSAGES:\n" + "\n".join(f"- {m}" for m in messages)
            + "\n\nReturn the corrected complete Delta.")
