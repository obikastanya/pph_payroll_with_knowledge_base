"""The researcher's local Claude account as a model client, for development only.

It runs `claude -p` with structured output and no tools. It is refused unless PPH21_DEV=1 is set, and refused for any
ledger under the measured-run folder, so no reported number can come from it: the Claude Code harness adds its own
system prompt and its model version and settings cannot be pinned. Calls are logged with provider "local" and cost 0.
"""
import json
import os
import subprocess

from . import WORK

from pph21kbs import draft  # noqa: E402

MEASURED = WORK / "measured"


class LocalClaude(draft.Client):
    provider = "local"

    def __init__(self, ledger, model="sonnet", timeout=900):
        if os.environ.get("PPH21_DEV") != "1":
            raise RuntimeError("the local Claude client is for development only: set PPH21_DEV=1")
        if MEASURED in ledger.dir.resolve().parents or ledger.dir.resolve() == MEASURED:
            raise RuntimeError("the local Claude client may not write to the measured-run folder")
        super().__init__(ledger)
        self.model, self.timeout = f"local-{model}", timeout
        self._alias = model

    def _call(self, system, prefix, user, schema, schema_name, effort, max_tokens, cache=True):
        cmd = ["claude", "-p", "--output-format", "json", "--json-schema", json.dumps(schema), "--system-prompt",
               system, "--tools", "", "--no-session-persistence", "--model", self._alias]
        proc = subprocess.run(cmd, input="\n\n".join(list(prefix) + [user]), capture_output=True, text=True,
                              encoding="utf-8", timeout=self.timeout)
        if proc.returncode != 0:
            raise draft.LLMError(f"claude -p failed: {proc.stderr[-300:]}")
        out = json.loads(proc.stdout)
        if out.get("is_error") or out.get("structured_output") is None:
            raise draft.LLMError(f"claude -p returned no structured output: {str(out.get('result'))[:300]}")
        usage = out.get("usage") or {}
        return draft.Reply(json.dumps(out["structured_output"], ensure_ascii=False), "end_turn", self.model,
                           {"input": usage.get("input_tokens", 0), "output": usage.get("output_tokens", 0),
                            "cache_read": usage.get("cache_read_input_tokens", 0),
                            "cache_write": usage.get("cache_creation_input_tokens", 0)})
