"""LLM clients, call log, and budget guard (akuisisi.md 8, format_data.md 6).

Every call is logged as one JSONL line in experiments/<run>/calls.jsonl; the full prompt goes to
experiments/<run>/prompts/<sha256>.json. The budget guard sums the cost of every call ever logged under experiments/
(all runs) and refuses a call that would start once the total reached the limit (USD 15, config.BUDGET_USD) or the
run's own limit. Keys come from .env through config; they are never logged.

Clients: AnthropicClient (main model, structured output through output_config.format, effort through
output_config.effort, prompt caching on the shared prefix), OpenAIClient (second model, Responses API with a strict
JSON schema), MockClient (tests and dry runs; returns prepared outputs and logs zero cost).
"""
import hashlib
import json
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

    def log(self, entry):
        with open(self.calls, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


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
        self.ledger.check()
        prompt = {"model": self.model, "effort": effort, "system": system, "prefix": prefix, "user": user,
                  "schema_name": schema_name}
        sha, pfile = self.ledger.save_prompt(prompt, private=str(document).startswith("PKB-"))
        t0 = time.time()
        try:
            reply = self._call(system, prefix, user, schema, schema_name, effort, max_tokens)
            error = None
        except Exception as e:  # noqa: BLE001 - a refusal or API error is a failed candidate, recorded
            reply = Reply("", "error", self.model, {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0})
            error = f"{type(e).__name__}: {e}"[:500]
        reply.seconds = round(time.time() - t0, 2)
        parsed = None
        if reply.text:
            try:
                parsed = json.loads(reply.text)
            except json.JSONDecodeError as e:
                error = error or f"JSONDecodeError: {e}"
        entry = {"call_id": call_id, "run": self.ledger.run,
                 "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                 "model_requested": self.model, "model_reported": reply.model, "provider": self.provider,
                 "effort": effort, "step": step, "document": document, "event": event, "candidate": candidate,
                 "order_seed": order_seed, "prompt_sha256": sha, "prompt_file": pfile, "output_raw": reply.text,
                 "stop_reason": reply.stop_reason, "usage": reply.usage,
                 "cost_usd": cost(self.model, reply.usage, self.batch), "batch": self.batch,
                 "seconds": reply.seconds, "error": error, "gates": {}}
        self.ledger.log(entry)
        return reply, parsed, entry

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens):
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

    def request_params(self, system, prefix, user, schema, effort, max_tokens):
        blocks = [{"type": "text", "text": t} for t in prefix]
        if blocks:
            blocks[-1]["cache_control"] = {"type": "ephemeral"}
        blocks.append({"type": "text", "text": user})
        return {"model": self.model, "max_tokens": max_tokens,
                "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": blocks}],
                "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}}}

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens):
        params = self.request_params(system, prefix, user, schema, effort, max_tokens)
        with self.api.messages.stream(**params) as stream:
            msg = stream.get_final_message()
        return self.reply_of(msg)

    def reply_of(self, msg):
        text = next((b.text for b in msg.content if b.type == "text"), "")
        u = msg.usage
        usage = {"input": u.input_tokens or 0, "output": u.output_tokens or 0,
                 "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                 "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0}
        return Reply(text, msg.stop_reason or "", msg.model, usage)


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

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens):
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

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens):
        self.seen.append({"system": system, "prefix": prefix, "user": user, "schema_name": schema_name})
        if not self.outputs:
            raise LLMError("mock client has no more outputs")
        out = self.outputs.pop(0)
        if isinstance(out, Exception):
            raise out
        text = out if isinstance(out, str) else json.dumps(out, ensure_ascii=False)
        return Reply(text, "end_turn", self.model, {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0})
