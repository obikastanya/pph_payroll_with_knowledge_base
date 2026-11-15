"""Record and replay of model calls.

A call is replayed only when the same model receives the same prompt under the same call id, so the drafts of one
document stay independent and a measured run (its own run id, hence its own call ids) never reuses an answer from
development. Replays are logged with cost 0 and replayed=True, so cost and call counts stay truthful.
"""
import hashlib
import json
import threading
from contextlib import contextmanager
from datetime import datetime, timezone

from . import WORK

from pph21kbs import draft  # noqa: E402

STORE = WORK / "replay"


def key(model, effort, system, prefix, user, schema_name, call_id):
    payload = json.dumps({"model": model, "effort": effort, "system": system, "prefix": prefix, "user": user,
                          "schema_name": schema_name, "call_id": call_id}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Recorded(draft.Client):
    """A client that answers from the store when it can and asks `inner` (logging to the same ledger) otherwise."""

    def __init__(self, inner, store=STORE):
        super().__init__(inner.ledger)
        self.inner, self.provider, self.model = inner, inner.provider, inner.model
        self.path = store / f"{inner.model}.jsonl"
        self._lock = threading.Lock()
        self.answers = {}
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    self.answers[row["key"]] = row
        self.hits = self.misses = 0
        self.cpu = threading.Lock()        # rdflib is not thread-safe: one worker computes at a time
        self._held = threading.local()

    @contextmanager
    def worker(self):
        """A thread's share of the work: it holds the CPU lock except while it waits for the API."""
        self.cpu.acquire()
        self._held.on = True
        try:
            yield
        finally:
            self._held.on = False
            self.cpu.release()

    def complete(self, *, system, prefix, user, schema, schema_name, effort, step, document="", event="",
                 draft_no=None, call_id=None, max_tokens=32000):
        k = key(self.model, effort, system, prefix, user, schema_name, call_id)
        row = self.answers.get(k)
        if row is None:
            self.misses += 1
            held = getattr(self._held, "on", False)
            if held:
                self.cpu.release()
            try:
                reply, parsed, entry = self.inner.complete(
                    system=system, prefix=prefix, user=user, schema=schema, schema_name=schema_name, effort=effort,
                    step=step, document=document, event=event, draft_no=draft_no, call_id=call_id,
                    max_tokens=max_tokens)
            finally:
                if held:
                    self.cpu.acquire()
            if not entry.get("error"):
                self._store({"key": k, "call_id": call_id, "output_raw": entry["output_raw"],
                             "stop_reason": entry["stop_reason"], "model_reported": entry["model_reported"],
                             "usage": entry["usage"]})
            return reply, parsed, entry
        self.hits += 1
        sha, pfile = self.ledger.save_prompt({"model": self.model, "effort": effort, "system": system,
                                              "prefix": prefix, "user": user, "schema_name": schema_name})
        reply = draft.Reply(row["output_raw"], row["stop_reason"], row["model_reported"], row["usage"])
        entry = {"call_id": call_id, "ledger": self.ledger.name,
                 "time": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                 "model_requested": self.model, "model_reported": row["model_reported"], "provider": self.provider,
                 "effort": effort, "step": step, "document": document, "event": event, "draft_no": draft_no,
                 "prompt_sha256": sha, "prompt_file": pfile, "output_raw": row["output_raw"],
                 "stop_reason": row["stop_reason"], "usage": row["usage"], "cost_usd": 0.0, "seconds": 0.0,
                 "error": None, "replayed": True}
        self.ledger.log(entry)
        return reply, json.loads(row["output_raw"]) if row["output_raw"] else None, entry

    def _store(self, row):
        with self._lock:
            self.answers[row["key"]] = row
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
