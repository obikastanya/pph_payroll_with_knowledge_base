"""Acquisition pipeline for one document, and the impact of an update on company policies.

    select text -> relevance (with quotes) -> m independent drafts -> gates G1-G6, one repair round
    -> behavioural consensus (largest group of drafts that behave the same) or abstention -> reviewer

The pipeline never changes the knowledge base: it returns a proposed update (Delta) that a person approves or rejects.

Terms: a draft is one model output for the document; drafts "agree" (consensus) when they behave the same on the
generated cases; when the largest group is not unique or no draft passes, the pipeline abstains ("the AI is not
sure") and the document goes to a person. F_Delta is the set of facts an update affects, directly or downstream.
"""
import ast
import json
import random
import zlib
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache

from rdflib import Dataset, URIRef

from . import config, digest, documents, draft, gates, graph
from .digest import BUDGET_TOKENS as DIGEST_BUDGET
from .documents import registry
from .draft import BudgetExceeded, ConversionError, to_delta
from .gates import observe
from .kb import Constraint, FactDef, Parameter, Rule, TableVersion, Tombstone, schema


# ====================================================================================================================
# Documents as events
# ====================================================================================================================
@dataclass(frozen=True)
class Event:
    """A document to acquire: its registry id(s), issue date, and layer (regulation or company policy)."""
    id: str
    documents: tuple
    issued: date
    layer: str = "regulation"
    title: str = ""

    @property
    def document(self):
        return self.documents[0]


def documents_of(event):
    reg = registry()
    return [{"id": d, "title": reg[d]["title"], "issued": reg[d]["issued"]} for d in event.documents]


# ====================================================================================================================
# Behavioural consensus
# ====================================================================================================================
def produces_map(kb, omega):
    """Rule id -> produced fact for the rules effective at omega."""
    return {rid: r.produces for rid, r in kb.view(omega).rules.items()}


def align(key, produces):
    """A conflict key with the rule id replaced by the fact the rule produces, so that two drafts that name the same
    company rule differently report the same conflict."""
    if isinstance(key, str):
        key = ast.literal_eval(key)
    if key[0] == "override":
        _, _source, fact, month = key
        return ("override", fact, month)
    _, rules, month, code = key
    rules = rules if isinstance(rules, (list, tuple)) else (rules,)
    return ("constraint", tuple(sorted({produces.get(r, r) for r in rules})), month, code)


def aligned(keys, produces):
    return sorted(map(str, {align(k, produces) for k in keys}))


def signature(kb2, cases, omegas, extra=()):
    """Behaviour of a draft: every observed value, the aligned conflict report, and engine errors on every case at
    both knowledge dates."""
    out, produces = [], {}
    for i, case in enumerate(cases):
        for w in omegas:
            obs, conflicts, errors, _ = observe(kb2, case, w, extra)
            if w not in produces:
                produces[w] = produces_map(kb2, w)
            out.append((i, w.isoformat(), tuple(sorted((k, str(v)) for k, v in obs.items())),
                        tuple(aligned(conflicts, produces[w])), bool(errors)))
    return tuple(out)


def choose(passing, order, extra=()):
    """passing: {draft number: (K', cases, omegas)}; order: draft numbers in random order. Drafts are grouped by their
    behaviour on the union of their generated cases; the largest group wins and its first member in the random order
    is selected. A tie between the largest groups, or no passing draft, gives abstain.
    Returns (selected draft or None, groups as lists of draft numbers, status)."""
    if not passing:
        return None, [], "abstain"
    union, seen, omegas = [], set(), None
    for n in order:
        if n not in passing:
            continue
        _, cases, ws = passing[n]
        omegas = omegas or ws
        for c in cases:
            key = repr(sorted(c.items(), key=lambda t: t[0]))
            if key not in seen:
                seen.add(key)
                union.append(c)
    sigs = {n: signature(passing[n][0], union, omegas, extra) for n in passing}
    groups = []
    for n in [x for x in order if x in passing]:
        for g in groups:
            if sigs[g[0]] == sigs[n]:
                g.append(n)
                break
        else:
            groups.append([n])
    groups.sort(key=lambda g: -len(g))
    if len(groups) > 1 and len(groups[0]) == len(groups[1]):
        return None, groups, "abstain"
    return groups[0][0], groups, "proposed"


# ====================================================================================================================
# Impact on company policies
# ====================================================================================================================
# detect() computes the impact in Python; detect_sparql() evaluates the same definition with the SPARQL queries of
# spec/queries/ on the knowledge graph. Both give the same result (tests/test_pipeline.py); the Python version is fast
# enough for the review screen, rdflib's in-memory evaluation of the property paths is not.
VIEW = graph.KB["graph/view"]
DELTA = graph.KB["graph/delta"]


def _update_records(kb, update_id):
    """The records an update created; a removed element is represented by the record it removed."""
    out = []
    for r in kb.records:
        if r.update_id != update_id:
            continue
        if isinstance(r, Tombstone):
            older = [x for x in kb.history(r.id) if x.seq < r.seq and not isinstance(x, Tombstone)]
            if older:
                out.append(older[-1])
            continue
        out.append(r)
    return out


def _reads(r):
    """Facts read by the expression and condition of a rule, or the assertion and condition of a constraint."""
    exprs = (r.expression, r.condition) if isinstance(r, Rule) else (r.assertion, r.condition)
    return {f for e in exprs if e is not None for f in e.dependencies()}


def _uses(r):
    exprs = (r.expression, r.condition) if isinstance(r, Rule) else (r.assertion, r.condition)
    return {n for e in exprs if e is not None for n in e.params | e.tables}


def affected_facts(kb, update_id, omega):
    """F_Delta: the facts an update touches (rules it adds or changes, rules that use a parameter or table it changes,
    facts it defines) and every fact computed from them."""
    view = [r for r in kb.view(omega).records if isinstance(r, (Rule, Constraint))]
    delta = _update_records(kb, update_id)
    names = {r.name for r in delta if isinstance(r, (Parameter, TableVersion))}
    seeds = {r.produces for r in delta if isinstance(r, Rule)}
    seeds |= {r.produces for r in view if isinstance(r, Rule) and _uses(r) & names}
    seeds |= {r.id for r in delta if isinstance(r, FactDef)}
    readers = {}
    for r in view:
        if isinstance(r, Rule):
            for f in _reads(r):
                readers.setdefault(f, set()).add(r.produces)
    out, todo = set(seeds), list(seeds)
    while todo:
        for g in readers.get(todo.pop(), ()):
            if g not in out:
                out.add(g)
                todo.append(g)
    return sorted(out)


def detect(kb, update_id, policies, omega):
    """Company policies affected by an update already applied to kb.
    Returns {policy: {"kinds": set of a/b/c/d, "hits": [(kind, company rule, update element, fact)]}}:
      a  a policy rule reads a fact the update affects;
      b  a policy rule produces a fact an update rule also produces;
      c  as b with a mandatory regulation rule, or an update constraint reads a fact a policy rule produces;
      d  a policy rule produces a fact the update affects (it competes with a regulation rule changed upstream).
    Only pairs whose validity periods overlap count."""
    affected = set(affected_facts(kb, update_id, omega))
    delta = _update_records(kb, update_id)
    rules = [r for r in kb.view(omega).records if isinstance(r, Rule) and r.policy and r.valid_from is not None]
    out = {}
    for p in policies:
        hits = set()
        for r in (x for x in rules if x.policy == p):
            r_until = r.valid_until or date.max
            for u in delta:
                if not (r.valid_from <= (u.valid_until or date.max) and (u.valid_from or date.min) <= r_until):
                    continue
                hits |= {("a", r.id, u.id, f) for f in _reads(r) & affected}
                if isinstance(u, Rule) and u.produces == r.produces:
                    hits.add(("b", r.id, u.id, r.produces))
                    if u.modality == "mandatory" and u.layer == "regulation":
                        hits.add(("c", r.id, u.id, r.produces))
                if isinstance(u, Constraint) and r.produces in _reads(u):
                    hits.add(("c", r.id, u.id, r.produces))
                if r.produces in affected:
                    hits.add(("d", r.id, u.id, r.produces))
        out[p] = {"kinds": {h[0] for h in hits}, "hits": sorted(hits)}
    return out


@lru_cache(maxsize=None)
def query_text(name):
    return (config.QUERIES / f"{name}.rq").read_text(encoding="utf-8")


def impact_graph(kb, update_id, omega):
    """Two named graphs: the effective records at omega (view) and the records the update created (delta)."""
    ds = Dataset()
    view, delta = ds.graph(VIEW), ds.graph(DELTA)
    for r in kb.view(omega).records:
        graph.record_triples(view, r)
    for r in _update_records(kb, update_id):
        graph.record_triples(delta, r)
    return ds


def detect_sparql(kb, update_id, policies, omega):
    """detect() evaluated with the SPARQL queries of spec/queries on the knowledge graph (slow in memory)."""
    ds = impact_graph(kb, update_id, omega)
    facts = sorted(str(row.fact).rsplit("/", 1)[1] for row in ds.query(query_text("impact_facts")))
    # F_Delta is passed as FILTER ... IN: rdflib ignores an inline VALUES block inside a UNION branch
    members = ", ".join(f"<{graph.fact_iri(f)}>" for f in facts) or "<urn:pph21kbs:none>"
    q = query_text("impact_policy").replace("FILTER_AFFECTED", f"FILTER(?fact IN ({members}))")
    out = {}
    for p in policies:
        hits = {(str(row.kind), str(row.rule), str(row.element), str(row.fact).rsplit("/", 1)[1])
                for row in ds.query(q, initBindings={"policy": URIRef(graph.doc_iri(p))})}
        out[p] = {"kinds": {h[0] for h in hits}, "hits": sorted(hits)}
    return out, facts


# ====================================================================================================================
# Pipeline
# ====================================================================================================================
@dataclass
class Config:
    m: int = 3                         # independent drafts per document
    repair_rounds: int = 1
    seed: int = 20261027               # order in which drafts are taken when groups have the same behaviour
    relevance_effort: str = "medium"
    draft_effort: str = "high"
    budget_tokens: int = documents.TOKEN_BUDGET
    use_stored_map: bool = False       # read a document through its stored map (digest.py)
    digest_budget: int = DIGEST_BUDGET # a mapped selection above this is sent whole and reported as over budget
    fallback: str = "lexical"          # without a usable map: "lexical" selection within budget_tokens, or "full" text
    max_tokens: int = 32000            # per draft or repair call
    policy_omega: date = field(default_factory=date.today)    # knowledge date a company policy is checked against


@dataclass
class Draft:
    n: int
    order: int
    llm: dict | None = None            # the model output
    delta: dict | None = None          # the converted update
    passed: bool = False
    passed_before_repair: bool = False
    repaired: bool = False
    gate_log: dict = field(default_factory=dict)
    first_gate_log: dict = field(default_factory=dict)
    initial_delta: dict | None = None
    case_count: int = 0                # generated cases the draft was checked on
    error: str = ""
    checked: tuple | None = field(default=None, repr=False)   # (K', generated cases, knowledge dates) when passed


def relevance_quotes_ok(rel, event):
    for q in rel.get("quotes") or []:
        if not any(documents.find_quote(d, q["quote"]) for d in event.documents) or len(q["quote"]) < gates.MIN_QUOTE:
            return False
    return bool(rel.get("quotes"))


def check(base, delta, event, issued, relevance, cfg, policies=()):
    """Run the gates in order and stop at the first failure. Returns (passed, log, K', generated cases)."""
    company = event.layer == "company"
    omega = cfg.policy_omega if company else issued
    log = {}
    r1, kb2 = gates.g1(base, delta)
    log["G1"] = r1.summary()
    if not r1.passed:
        return False, log, None, None
    r6 = gates.g6(base.view(omega), delta)
    log["G6"] = r6.summary()
    if not r6.passed:
        return False, log, kb2, None
    r2 = gates.g2(base, delta, list(event.documents), issued)
    log["G2"] = r2.summary()
    if not r2.passed:
        return False, log, kb2, None
    r3 = gates.g3(kb2, omega, policies)
    log["G3"] = r3.summary()
    log["G3_warnings"] = r3.warnings[:20]
    if not r3.passed:
        return False, log, kb2, None
    starts, s_d = gates.effect_start(base, delta)
    sgs = gates.generate(base, kb2, delta, s_d, issued, relevance, cfg.seed, starts=starts,
                         omega=cfg.policy_omega if company else None)
    extra = [e["id"] for e in delta["add"] if e["kind"] == "fact"] if company else []
    ev = gates.Evaluations(sgs.cases, extra)
    r4 = gates.g4(base, kb2, sgs, ev, s_d, company=company)
    log["G4"] = r4.summary()
    if not r4.passed:
        return False, log, kb2, sgs
    r5 = gates.g5(base, kb2, delta, sgs, ev, starts, relevance)
    log["G5"] = r5.summary()
    log["G5_warnings"] = r5.warnings
    if not r5.passed:
        return False, log, kb2, sgs
    return True, log, kb2, sgs


def _messages(log):
    return [f"{g}: {v[6:]}" for g, v in log.items() if isinstance(v, str) and v.startswith("fail")]


def document_text(docs, view, cfg, digester=None, call_prefix=""):
    """(text for the drafting model, selection record). Without a usable map, cfg.fallback decides: the lexical
    selection or the full text."""
    selections, info = [], {}
    for d in docs:
        record = None
        if digester is not None:
            try:
                record = digest.build(d["id"], digester, title=d.get("title", ""), call_prefix=call_prefix)
            except BudgetExceeded:
                pass
        elif cfg.use_stored_map:
            record = digest.load(d["id"])
        usable = record is not None and digest.usable(record)
        if usable:
            sel = digest.select(d["id"], record)
        elif cfg.fallback == "full":
            sel = documents.full(d["id"])
        else:
            sel = documents.select(d["id"], view, cfg.budget_tokens)
        info[d["id"]] = {"tokens": sel.tokens, "dropped": sel.dropped,
                         "reading": "map" if usable else cfg.fallback}
        if usable and sel.tokens > cfg.digest_budget:
            info[d["id"]]["over_budget"] = True
        if record:
            info[d["id"]]["digest"] = {"model": record["model"], "parts": digest.counts(record), "used": usable,
                                       "calls": record["calls"], "failed_calls": record["failed_calls"]}
        selections.append(sel)
    return "\n\n".join(documents.render(s) for s in selections), info


def run_document(event, base, client, ledger, cfg=None, run_id="run", out_dir=None, policies=(), digester=None):
    """Acquire one document against the knowledge base `base`. Returns the result record (also written to
    out_dir/<event id>.json) with status proposed, empty (not relevant), abstain, or budget. digester maps the
    document first (digest.py)."""
    cfg = cfg or Config()
    docs = documents_of(event)
    issued = event.issued
    view = base.view(issued)
    result = {"run": run_id, "event": event.id, "documents": [d["id"] for d in docs], "selection": {},
              "drafts": [], "groups": [], "selected": None, "status": None, "delta": None, "cost_usd": 0.0}
    call_prefix = f"{run_id}-{event.id}-"
    ledgers = [ledger] + ([digester.ledger] if digester is not None and digester.ledger is not ledger else [])
    try:
        doc_text, result["selection"] = document_text(docs, view, cfg, digester, call_prefix)
        ctx = draft.context_text(view, doc_text)
        _, rel, _ = client.complete(system=draft.SYSTEM_RELEVANCE, prefix=[doc_text],
                                    user=draft.relevance_user(event, docs), schema=draft.RELEVANCE_SCHEMA,
                                    schema_name="relevance", effort=cfg.relevance_effort, step="relevance",
                                    document=event.document, event=event.id, call_id=f"{call_prefix}rel")
        rel = rel or {}
        result["relevance"] = {"output": rel, "quotes_ok": relevance_quotes_ok(rel, event) if rel else False}
        if rel and rel.get("relevant") is False:
            if result["relevance"]["quotes_ok"]:
                result["status"] = "empty"
                result["delta"] = {"delta_id": f"{run_id}-{event.id}", "event_id": event.id, "document": docs[0],
                                   "relevant": False, "add": [], "change": [], "remove": [],
                                   "note": rel.get("reason", "")}
            else:
                result["status"] = "abstain"
            return _finish(result, ledgers, call_prefix, out_dir)
        rng = random.Random(cfg.seed + zlib.crc32(event.id.encode()) % 1000)
        order = list(range(1, cfg.m + 1))
        rng.shuffle(order)
        prefix = [doc_text, ctx]
        delta_schema = schema("delta_llm")
        # the m drafts are independent requests; then one repair of each draft that failed a gate, which sees only
        # its own draft and gate messages (same system prompt and prefix, so the cached prefix is read again)
        drafts = [Draft(n, order.index(n)) for n in range(1, cfg.m + 1)]
        outs = client.complete_many([dict(system=draft.SYSTEM_DRAFT, prefix=prefix,
                                          user=draft.draft_user(event, docs, rel), schema=delta_schema,
                                          schema_name="delta", effort=cfg.draft_effort, step="draft",
                                          document=event.document, event=event.id, draft_no=d.n,
                                          call_id=f"{call_prefix}draft{d.n}", max_tokens=cfg.max_tokens)
                                     for d in drafts])
        for d, (_, out, _) in zip(drafts, outs):
            d.llm = out
            _evaluate(d, base, event, issued, rel, cfg, docs, run_id, policies)
            d.passed_before_repair = d.passed
            d.first_gate_log = dict(d.gate_log)
            d.initial_delta = d.delta
        for r in range(cfg.repair_rounds):
            todo = [d for d in drafts if not d.passed and d.llm is not None]
            if not todo:
                break
            outs = client.complete_many([dict(system=draft.SYSTEM_DRAFT, prefix=prefix,
                                              user=draft.repair_user(event, docs, d.llm,
                                                                     _messages(d.gate_log) or [d.error]),
                                              schema=delta_schema, schema_name="delta", effort=cfg.draft_effort,
                                              step="repair", document=event.document, event=event.id,
                                              draft_no=d.n, call_id=f"{call_prefix}draft{d.n}-repair{r + 1}",
                                              max_tokens=cfg.max_tokens)
                                         for d in todo])
            for d, (_, out2, _) in zip(todo, outs):
                if out2 is not None:
                    d.llm, d.repaired = out2, True
                    _evaluate(d, base, event, issued, rel, cfg, docs, run_id, policies)
        passing = {d.n: d.checked for d in drafts if d.passed}
        sel, groups, status = choose(passing, sorted(passing, key=lambda n: order.index(n)))
        result.update(groups=groups, selected=sel, status=status)
        if sel is not None:
            result["delta"] = next(d.delta for d in drafts if d.n == sel)
        result["drafts"] = [{"n": d.n, "order": d.order, "passed": d.passed,
                             "passed_before_repair": d.passed_before_repair, "repaired": d.repaired,
                             "gate_log": d.gate_log, "first_gate_log": d.first_gate_log, "case_count": d.case_count,
                             "error": d.error, "llm": d.llm, "delta": d.delta,
                             "initial_delta": d.initial_delta if d.repaired else None} for d in drafts]
    except BudgetExceeded as e:
        result["status"] = "budget"
        result["error"] = str(e)
    return _finish(result, ledgers, call_prefix, out_dir)


def _evaluate(d, base, event, issued, rel, cfg, docs, run_id, policies):
    d.passed, d.gate_log, d.error, d.delta, d.checked = False, {}, "", None, None
    if d.llm is None:
        d.error = "no parsable output"
        d.gate_log = {"G1": "fail: no parsable output"}
        return
    try:
        d.delta = to_delta(d.llm, f"{run_id}-{event.id}-draft{d.n}", event.id, docs[0])
    except ConversionError as e:
        d.error = str(e)
        d.gate_log = {"G1": f"fail: {e}"}
        return
    ok, log, kb2, sgs = check(base, d.delta, event, issued, rel, cfg, policies)
    d.passed, d.gate_log = ok, log
    d.case_count = len(sgs.cases) if sgs else 0
    if ok:
        d.checked = (kb2, sgs.cases, sgs.omegas)


def _finish(result, ledgers, call_prefix, out_dir):
    result["cost_usd"] = round(sum(led.spent_prefix(call_prefix) for led in ledgers), 6)
    d = out_dir or ledgers[0].dir / "results"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{result['event']}.json").write_text(json.dumps(result, ensure_ascii=False, indent=1, default=str),
                                               encoding="utf-8")
    return result
