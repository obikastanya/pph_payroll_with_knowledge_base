"""Mock LLM: answers are prepared in data/mock_llm/, so the demo runs without an API and without cost.

The real study calls an actual model (the client in asisten_kb/llm.py) with a prompt holding the document text and
context from the graph, and logs the prompt, output, tokens, cost, and time of every call. The mock keeps the same
call log so the logger format is visible; token counts are estimated as characters / 4 and cost is zero.
"""
import json

from kg import DATA


def _expand(value, shared):
    """Replace "$name" references with entries from the file's "shared" section (a convenience of the mock files)."""
    if isinstance(value, str) and value.startswith("$"):
        return _expand(shared[value[1:]], shared)
    if isinstance(value, list):
        return [_expand(v, shared) for v in value]
    if isinstance(value, dict):
        return {k: _expand(v, shared) for k, v in value.items()}
    return value


class MockLLM:
    name = "mock-llm"

    def __init__(self, folder=DATA / "mock_llm"):
        self.folder = folder
        self.calls = []

    def has_answer(self, doc_id):
        return (self.folder / f"{doc_id}.json").exists()

    def _answer(self, doc_id):
        data = json.loads((self.folder / f"{doc_id}.json").read_text(encoding="utf-8"))
        return _expand(data, data.get("shared", {}))

    def _log(self, doc_id, step, prompt, output):
        out = json.dumps(output, ensure_ascii=False)
        self.calls.append({"document": doc_id, "step": step, "model": self.name, "temperature": None,
                           "tokens_in": len(prompt) // 4, "tokens_out": len(out) // 4, "cost_usd": 0.0, "seconds": 0.0,
                           "output": out})
        return output

    def judge_relevance(self, doc_id, text):
        """Does the document change how PPh 21 for permanent employees is calculated? Answer with a supporting quote."""
        return self._log(doc_id, "relevance", text, self._answer(doc_id)["relevance"])

    def draft_candidates(self, doc_id, text, context, m):
        """m independently drafted Delta candidates."""
        prompt = text + json.dumps(context)
        return [self._log(doc_id, f"candidate {i}", prompt, c) for i, c in enumerate(self._answer(doc_id)["candidates"][:m], 1)]

    def repair(self, doc_id, candidate, gate_feedback):
        """Repair round driven by gate feedback. The mock never repairs anything."""
        self._log(doc_id, "repair", json.dumps(candidate) + json.dumps(gate_feedback), None)
        return None
