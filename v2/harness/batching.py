"""Batch route for model calls (OpenAI Batch, Anthropic Message Batches): half price, answers within 24 hours.

Each document runs in its own thread inside `client.worker()`. A worker holds the CPU lock while it computes (the
gates' RDF and SHACL libraries are not thread-safe, and Python threads give no CPU parallelism anyway) and lets it go
while it waits for a model answer. When every active worker is waiting, all pending requests go out as one batch, so
an isolated run takes one batch per pipeline stage (relevance, drafts, repairs). The m drafts of a document are
submitted together. Calls are logged as usual with cost x 0.5 and batch=True.
Submitted batches are recorded in WORK/batches.jsonl.
"""
import itertools
import json
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from pph21kbs import draft  # noqa: E402

from . import WORK

DISCOUNT = 0.5
RECORD = WORK / "batches.jsonl"


class Batching(draft.Client):
    batched = True

    def __init__(self, inner, backend):
        super().__init__(inner.ledger)
        self.inner, self.backend = inner, backend
        self.provider, self.model = inner.provider, inner.model
        self._cond = threading.Condition()
        self.cpu = threading.Lock()
        self._ids = itertools.count(1)
        self.active = self.waiting = self.rounds = 0
        self.pending, self.results, self.in_flight, self.meta = {}, {}, False, {}

    @contextmanager
    def worker(self):
        with self._cond:
            self.active += 1
        self.cpu.acquire()
        try:
            yield
        finally:
            self.cpu.release()
            with self._cond:
                self.active -= 1
                self._cond.notify_all()

    def complete(self, **request):
        return self.complete_many([request])[0]

    def complete_many(self, requests):
        prepared = []
        for r in requests:
            self.ledger.check(self.provider)
            sha, pfile = self.ledger.save_prompt({"model": self.model, "effort": r["effort"], "system": r["system"],
                                                  "prefix": r["prefix"], "user": r["user"],
                                                  "schema_name": r["schema_name"]})
            body = self.inner.request(r["system"], r["prefix"], r["user"], r["schema"], r["schema_name"],
                                      r["effort"], r.get("max_tokens", 32000), cache=r["step"] != "relevance")
            cid = f"c{next(self._ids):07d}"
            self.meta[cid] = {k: r.get(k) for k in ("call_id", "document", "event", "step", "draft_no")}
            prepared.append((cid, r, sha, pfile, body))
        t0 = time.time()
        with self._cond:
            for cid, _, _, _, body in prepared:
                self.pending[cid] = body
            self.waiting += 1
            self._cond.notify_all()
        self.cpu.release()
        with self._cond:
            while any(cid not in self.results for cid, *_ in prepared):
                self._flush_if_idle()
                self._cond.wait(timeout=1)
            self.waiting -= 1
            raws = [self.results.pop(cid) for cid, *_ in prepared]
        self.cpu.acquire()
        out = []
        for (cid, r, sha, pfile, _), raw in zip(prepared, raws):
            if isinstance(raw, Exception):
                reply, error = draft.Reply("", "error", self.model, {"input": 0, "output": 0, "cache_read": 0,
                                                                       "cache_write": 0}), str(raw)[:500]
            else:
                reply, error = self.inner.reply(raw), None
            reply.seconds = round(time.time() - t0, 2)
            out.append(self.finish(reply, error, sha, pfile, effort=r["effort"], step=r["step"],
                                   document=r.get("document", ""), event=r.get("event", ""),
                                   draft_no=r.get("draft_no"), call_id=r.get("call_id"), discount=DISCOUNT,
                                   extra={"batch": True, "batch_custom_id": cid}))
        return out

    def _flush_if_idle(self):
        """Called with the lock held: submit everything pending once every active worker is waiting."""
        if self.in_flight or not self.pending or self.waiting < self.active:
            return
        batch, self.pending, self.in_flight = dict(self.pending), {}, True
        self.rounds += 1
        threading.Thread(target=self._submit, args=(batch,), daemon=True).start()

    def _submit(self, batch):
        try:
            out = self.backend.run(batch, {cid: self.meta.get(cid) for cid in batch})
        except Exception as e:  # noqa: BLE001 - every request of a failed batch fails, as a failed call would
            out = {cid: e for cid in batch}
        with self._cond:
            self.results.update({cid: out.get(cid, RuntimeError("missing from the batch output")) for cid in batch})
            self.in_flight = False
            self._cond.notify_all()


def _record(provider, batch_id, n):
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    with open(RECORD, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "provider": provider,
                            "batch": batch_id, "requests": n}) + "\n")


class OpenAIBatch:
    def __init__(self, api, poll=30):
        self.api, self.poll = api, poll

    def run(self, batch, meta=None):
        import io

        from openai.types.responses import Response
        lines = "\n".join(json.dumps({"custom_id": cid, "method": "POST", "url": "/v1/responses", "body": body},
                                     ensure_ascii=False) for cid, body in batch.items())
        f = self.api.files.create(file=("batch.jsonl", io.BytesIO(lines.encode("utf-8"))), purpose="batch")
        b = self.api.batches.create(input_file_id=f.id, endpoint="/v1/responses", completion_window="24h")
        _record("openai", b.id, len(batch))
        while b.status not in ("completed", "failed", "expired", "cancelled"):
            time.sleep(self.poll)
            b = self.api.batches.retrieve(b.id)
        out = {}
        for file_id in (b.output_file_id, b.error_file_id):
            if not file_id:
                continue
            for line in self.api.files.content(file_id).text.splitlines():
                row = json.loads(line)
                resp = row.get("response") or {}
                if resp.get("status_code") == 200:
                    out[row["custom_id"]] = Response.model_validate(resp["body"])
                else:
                    out[row["custom_id"]] = RuntimeError(f"batch request failed: {row.get('error') or resp}"[:300])
        return out


class AnthropicBatch:
    def __init__(self, api, poll=30):
        self.api, self.poll = api, poll

    def run(self, batch, meta=None):
        b = self.api.messages.batches.create(requests=[{"custom_id": cid, "params": body}
                                                       for cid, body in batch.items()])
        _record("anthropic", b.id, len(batch))
        while b.processing_status != "ended":
            time.sleep(self.poll)
            b = self.api.messages.batches.retrieve(b.id)
        out = {}
        for r in self.api.messages.batches.results(b.id):
            out[r.custom_id] = (r.result.message if r.result.type == "succeeded"
                                else RuntimeError(f"batch request {r.result.type}"))
        return out


def warm_up(base, update):
    """Initialise the RDF and SHACL machinery once in the calling thread: its lazy parser set-up is not thread-safe,
    and the gate G1 of parallel workers would otherwise race on it."""
    from pph21kbs import gates
    gates.g1(base, update)
