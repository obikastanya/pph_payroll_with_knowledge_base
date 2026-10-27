"""LLM clients, call log, and budget guard (akuisisi.md 8, format_data.md 6).

Every call is logged as one JSONL line in experiments/<run>/calls.jsonl; the full prompt goes to
experiments/<run>/prompts/<sha256>.json. The budget guard sums the cost of every call ever logged under experiments/
(all runs) and refuses a call that would start once the total reached the limit (USD 15, config.BUDGET_USD) or the
run's own limit. Keys come from .env through config; they are never logged.

Clients: AnthropicClient (main model, structured output through output_config.format, effort through
output_config.effort, prompt caching on the shared prefix), AnthropicBatchClient (the same requests through the
Message Batches API at half price: complete_many() calls of documents run in parallel threads are pooled by a
BatchDispatcher into one batch), OpenAIClient (second model, Responses API with a strict JSON schema), MockClient
(tests and dry runs; returns prepared outputs and logs zero cost).
"""
import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..config import BUDGET_USD, MAIN_MODEL, REPO, SECOND_MODEL, anthropic_key, openai_key

EXPERIMENTS = REPO / "experiments"

# USD per million tokens (akuisisi.md 8, prices of October 2026). Batch halves every price.
PRICES = {
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_read": 0.20, "cache_write": 5.0},
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
    raw: dict = field(default_factory=dict)


def cost(model, usage, batch=False):
    p = PRICES.get(model)
    if p is None:
        return 0.0
    c = (usage.get("input", 0) * p["input"] + usage.get("output", 0) * p["output"]
         + usage.get("cache_read", 0) * p["cache_read"] + usage.get("cache_write", 0) * p["cache_write"]) / 1e6
    return round(c * (0.5 if batch else 1.0), 6)


def spent_total(root=EXPERIMENTS):
    total = 0.0
    for path in Path(root).glob("*/calls.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                total += json.loads(line).get("cost_usd") or 0.0
    return round(total, 6)


class Ledger:
    """Call log and budget of one run."""

    def __init__(self, run, run_limit_usd=None, root=EXPERIMENTS, total_limit_usd=BUDGET_USD):
        self.run = run
        self.dir = Path(root) / run
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / "prompts").mkdir(exist_ok=True)
        self.calls = self.dir / "calls.jsonl"
        self.root = Path(root)
        self.run_limit = run_limit_usd
        self.total_limit = total_limit_usd

    def spent_run(self):
        if not self.calls.exists():
            return 0.0
        return round(sum(json.loads(l).get("cost_usd") or 0.0
                         for l in self.calls.read_text(encoding="utf-8").splitlines() if l.strip()), 6)

    def check(self):
        total = spent_total(self.root)
        if total >= self.total_limit:
            raise BudgetExceeded(f"total LLM spend {total:.4f} USD reached the limit {self.total_limit} USD")
        if self.run_limit is not None and self.spent_run() >= self.run_limit:
            raise BudgetExceeded(f"run {self.run} spend reached its limit {self.run_limit} USD")

    def save_prompt(self, prompt, private=False):
        """Prompts that contain licensed text (copies of collective agreements, PKB-*) go to prompts_private/,
        which is not committed; their SHA-256 is still logged."""
        text = json.dumps(prompt, ensure_ascii=False, sort_keys=True)
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        folder = "prompts_private" if private else "prompts"
        (self.dir / folder).mkdir(exist_ok=True)
        path = self.dir / folder / f"{sha}.json"
        if not path.exists():
            path.write_text(text, encoding="utf-8")
        return sha, f"{folder}/{sha}.json"

    _lock = threading.Lock()

    def log(self, entry):
        with self._lock, open(self.calls, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def spent_prefix(self, call_prefix):
        """Cost of this run's calls whose call_id starts with call_prefix (one document when runs share a ledger)."""
        if not self.calls.exists():
            return 0.0
        total = 0.0
        for line in self.calls.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                if str(e.get("call_id") or "").startswith(call_prefix):
                    total += e.get("cost_usd") or 0.0
        return round(total, 6)


class Client:
    provider = "none"
    model = ""

    def __init__(self, ledger, batch=False):
        self.ledger = ledger
        self.batch = batch

    def complete(self, *, system, prefix, user, schema, schema_name, effort, step, document="", event="",
                 candidate=None, order_seed=None, call_id=None, max_tokens=32000):
        """system: text; prefix: list of text blocks shared by the candidates of one document (cached);
        user: final text block. Returns (Reply, parsed JSON or None, log entry)."""
        req = dict(system=system, prefix=prefix, user=user, schema=schema, schema_name=schema_name, effort=effort,
                   step=step, document=document, event=event, candidate=candidate, order_seed=order_seed,
                   call_id=call_id, max_tokens=max_tokens)
        meta = self._begin(req)
        t0 = time.time()
        try:
            reply = self._call(system, prefix, user, schema, schema_name, effort, max_tokens,
                               cache=_cached(step))
            error = None
        except Exception as e:  # noqa: BLE001 - a refusal or API error is a failed candidate, recorded
            reply, error = _failed(self.model), f"{type(e).__name__}: {e}"[:500]
        reply.seconds = round(time.time() - t0, 2)
        return self._end(req, meta, reply, error)

    def complete_many(self, requests):
        """Independent requests (keyword dicts of complete()); results in the same order."""
        return [self.complete(**r) for r in requests]

    def _begin(self, req):
        self.ledger.check()
        prompt = {"model": self.model, "effort": req["effort"], "system": req["system"], "prefix": req["prefix"],
                  "user": req["user"], "schema_name": req["schema_name"]}
        return self.ledger.save_prompt(prompt, private=str(req["document"]).startswith("PKB-"))

    def _end(self, req, meta, reply, error):
        sha, pfile = meta
        parsed = None
        if reply.text:
            try:
                parsed = json.loads(reply.text)
            except json.JSONDecodeError as e:
                error = error or f"JSONDecodeError: {e}"
        entry = {"call_id": req["call_id"], "run": self.ledger.run,
                 "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                 "model_requested": self.model, "model_reported": reply.model, "provider": self.provider,
                 "effort": req["effort"], "step": req["step"], "document": req["document"], "event": req["event"],
                 "candidate": req["candidate"], "order_seed": req["order_seed"], "prompt_sha256": sha,
                 "prompt_file": pfile, "output_raw": reply.text, "stop_reason": reply.stop_reason,
                 "usage": reply.usage, "cost_usd": cost(self.model, reply.usage, self.batch), "batch": self.batch,
                 "seconds": reply.seconds, "error": error, "gates": {}}
        if reply.raw.get("batch_id"):
            entry["batch_id"] = reply.raw["batch_id"]
        self.ledger.log(entry)
        return reply, parsed, entry

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        raise NotImplementedError


class AnthropicClient(Client):
    provider = "anthropic"

    def __init__(self, ledger, model=MAIN_MODEL, batch=False):
        super().__init__(ledger, batch)
        import anthropic
        key = anthropic_key()
        if not key:
            raise LLMError("no Anthropic key in the environment or .env")
        self.model = model
        self.api = anthropic.Anthropic(api_key=key, max_retries=3)

    def request_params(self, system, prefix, user, schema, effort, max_tokens, cache=True):
        blocks = [{"type": "text", "text": t} for t in prefix]
        if blocks and cache:
            blocks[-1]["cache_control"] = {"type": "ephemeral"}
        blocks.append({"type": "text", "text": user})
        sys_block = {"type": "text", "text": system}
        if cache:
            sys_block["cache_control"] = {"type": "ephemeral"}
        return {"model": self.model, "max_tokens": max_tokens,
                "system": [sys_block],
                "messages": [{"role": "user", "content": blocks}],
                "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}}}

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        params = self.request_params(system, prefix, user, schema, effort, max_tokens, cache)
        with self.api.messages.stream(**params) as stream:
            msg = stream.get_final_message()
        return self.reply_of(msg)

    def reply_of(self, msg):  # also called unbound (self None) by BatchDispatcher
        text = next((b.text for b in msg.content if b.type == "text"), "")
        u = msg.usage
        usage = {"input": u.input_tokens or 0, "output": u.output_tokens or 0,
                 "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                 "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0}
        return Reply(text, msg.stop_reason or "", msg.model, usage)


class AnthropicBatchClient(AnthropicClient):
    """AnthropicClient through the Message Batches API (half price). complete_many() hands its requests to the shared
    dispatcher; complete() is a batch of one."""

    def __init__(self, ledger, dispatcher=None, model=MAIN_MODEL, poll_seconds=30, log=print):
        super().__init__(ledger, model=model, batch=True)
        self.dispatcher = dispatcher or BatchDispatcher(self.api, ledger, poll_seconds, log)

    def complete(self, **req):
        return self.complete_many([req])[0]

    def complete_many(self, requests):
        reqs = [dict({"candidate": None, "order_seed": None, "call_id": None, "max_tokens": 32000, "document": "",
                      "event": ""}, **r) for r in requests]
        metas = [self._begin(r) for r in reqs]
        items = []
        for i, r in enumerate(reqs):
            cid = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in str(r["call_id"] or f"req{i}"))[:64]
            params = self.request_params(r["system"], r["prefix"], r["user"], r["schema"], r["effort"],
                                         r["max_tokens"], _cached(r["step"]))
            items.append((cid, params, self.model))
        if len({cid for cid, _, _ in items}) != len(items):
            raise LLMError("duplicate call ids in one batch")
        results = self.dispatcher.submit(items)
        return [self._end(r, m, reply, err) for r, m, (reply, err) in zip(reqs, metas, results)]


def _cached(step):
    """The relevance call is the only one with its system prompt and prefix, so nothing would read its cache; a
    cache write costs 1.25 x input. Drafts and repairs of one document share the cached prefix."""
    return step != "relevance"


def _failed(model):
    return Reply("", "error", model, {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0})


class BatchDispatcher:
    """Pools the requests of documents processed in parallel threads into one Message Batch.

    The runner calls enter() once per document before starting any thread, and each thread calls leave() when its
    document is done. The document threads do their own work (gates, S^G, consensus) under the dispatcher's cpu lock
    (with dispatcher.cpu(): ...), released only while waiting for a batch: the SPARQL parser of rdflib is not
    thread-safe, and under the GIL parallel threads would gain nothing. A thread that needs LLM output submits its
    requests and waits; when every active thread is waiting, the pooled requests are sent as one batch, polled until
    it ends, and the results handed back. Before sending, the cost of the batch is bounded from above (all prompt
    text as uncached input at 4 characters per token, max_tokens/4 output per request) and the batch is refused when
    that bound would cross the total budget."""

    def __init__(self, api, ledger, poll_seconds=30, log=print):
        self.api = api
        self.ledger = ledger
        self.poll = poll_seconds
        self.cv = threading.Condition()
        self.active = 0
        self.waiting = []
        self.log = log
        self.batches = []
        self._cpu = threading.Lock()
        self._held = threading.local()

    def cpu(self):
        dispatcher = self

        class _Hold:
            def __enter__(self):
                dispatcher._cpu.acquire()
                dispatcher._held.on = True

            def __exit__(self, *exc):
                dispatcher._held.on = False
                dispatcher._cpu.release()
        return _Hold()

    def enter(self):
        with self.cv:
            self.active += 1

    def leave(self):
        with self.cv:
            self.active -= 1
            self.cv.notify_all()

    def submit(self, items):
        """items: [(custom_id, params, model)]. Returns [(Reply, error)] in the same order."""
        slot = {"done": False, "results": None, "error": None, "items": items}
        held = getattr(self._held, "on", False)
        if held:                                # let the other documents work while this one waits
            self._held.on = False
            self._cpu.release()
        try:
            return self._wait(slot)
        finally:
            if held:
                self._cpu.acquire()
                self._held.on = True

    def _wait(self, slot):
        with self.cv:
            self.waiting.append(slot)
            self.cv.notify_all()
            while not slot["done"]:
                if self.waiting and slot is self.waiting[0] and len(self.waiting) >= max(self.active, 1):
                    pool, self.waiting = self.waiting, []
                    self.cv.release()
                    try:
                        self._send(pool)
                    finally:
                        self.cv.acquire()
                        self.cv.notify_all()
                else:
                    self.cv.wait(timeout=5)
        if slot["error"] is not None:
            raise slot["error"]
        return slot["results"]

    def _bound(self, items):
        usd = 0.0
        for _, params, model in items:
            chars = len(json.dumps(params.get("system"))) + len(json.dumps(params.get("messages")))
            usd += cost(model, {"input": chars / 4, "output": params["max_tokens"] / 4}, batch=True)
        return usd

    def _send(self, pool):
        items = [it for slot in pool for it in slot["items"]]
        try:
            bound = self._bound(items)
            total = spent_total(self.ledger.root)
            if total + bound > self.ledger.total_limit:
                raise BudgetExceeded(f"batch of {len(items)} requests may cost up to {bound:.2f} USD; spent "
                                     f"{total:.4f} of {self.ledger.total_limit} USD")
            if self.ledger.run_limit is not None and self.ledger.spent_run() + bound > self.ledger.run_limit:
                raise BudgetExceeded(f"batch of {len(items)} requests may cost up to {bound:.2f} USD; run "
                                     f"{self.ledger.run} spent {self.ledger.spent_run():.4f} of its limit "
                                     f"{self.ledger.run_limit} USD")
            batch = self.api.messages.batches.create(
                requests=[{"custom_id": cid, "params": params} for cid, params, _ in items])
            self.batches.append(batch.id)
            self.log(f"batch {batch.id}: {len(items)} requests (cost bound {bound:.2f} USD)")
            t0 = time.time()
            while True:
                b = self.api.messages.batches.retrieve(batch.id)
                if b.processing_status == "ended":
                    break
                time.sleep(self.poll)
            seconds = round(time.time() - t0, 1)
            self.log(f"batch {batch.id} ended after {seconds}s: {b.request_counts}")
            got = {}
            for r in self.api.messages.batches.results(batch.id):
                if r.result.type == "succeeded":
                    reply = AnthropicClient.reply_of(None, r.result.message)
                    reply.raw = {"batch_id": batch.id}
                    reply.seconds = seconds
                    got[r.custom_id] = (reply, None)
                else:
                    err = getattr(r.result, "error", None)
                    got[r.custom_id] = (_failed(""), f"batch {r.result.type}: {err}"[:500])
            for slot in pool:
                slot["results"] = [got.get(cid, (_failed(""), "batch: no result")) for cid, _, _ in slot["items"]]
        except Exception as e:  # noqa: BLE001 - handed to every waiting thread
            for slot in pool:
                slot["error"] = e
        for slot in pool:
            slot["done"] = True


class OpenAIClient(Client):
    provider = "openai"

    def __init__(self, ledger, model=SECOND_MODEL, batch=False):
        super().__init__(ledger, batch)
        import openai
        key = openai_key()
        if not key:
            raise LLMError("no OpenAI key in the environment or .env")
        self.model = model
        self.api = openai.OpenAI(api_key=key, max_retries=3)

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        content = [{"type": "input_text", "text": t} for t in prefix] + [{"type": "input_text", "text": user}]
        resp = self.api.responses.create(
            model=self.model, instructions=system, input=[{"role": "user", "content": content}],
            reasoning={"effort": effort}, max_output_tokens=max_tokens,
            text={"format": {"type": "json_schema", "name": schema_name, "schema": _strict(schema), "strict": True}})
        u = resp.usage
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        usage = {"input": (u.input_tokens or 0) - cached, "output": u.output_tokens or 0, "cache_read": cached,
                 "cache_write": 0}
        return Reply(resp.output_text or "", resp.status or "", resp.model, usage)


def _strict(schema):
    """OpenAI strict mode rejects format keywords and $schema/$id/title at the root."""
    def walk(x):
        if isinstance(x, dict):
            return {k: walk(v) for k, v in x.items() if k not in ("$schema", "$id", "title", "format")}
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x
    return walk(schema)


class MockClient(Client):
    """Returns prepared outputs in order (dicts are serialised); logs zero cost. For tests and dry runs."""
    provider = "mock"

    def __init__(self, ledger, outputs, model="mock"):
        super().__init__(ledger, False)
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
