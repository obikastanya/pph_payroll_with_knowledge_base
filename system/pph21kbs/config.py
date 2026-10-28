"""Settings of the full system: API keys from .env, model choices, and the GraphDB endpoint.

Keys are read from the repository's .env file (CLAUDE_API_KEY, OPENAI_API_KEY) unless the operating system already
defines them, so nothing has to be exported before running. Key values are never printed or logged.
"""
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENV_FILE = REPO / ".env"

# Decision log 2026-10-27: main model Claude Opus 5.5 at high effort; second model GPT-6.1 Sol at high effort.
MAIN_MODEL = "claude-opus-5-5"
MAIN_EFFORT = "high"
SECOND_MODEL = os.environ.get("PPH21_SECOND_MODEL", "gpt-6.1-sol")
SECOND_EFFORT = "high"
# LLM budget per provider, cumulative over all runs under experiments/. 2026-10-27: USD 15; 2026-10-28: at most USD 100
# more per provider; 2026-10-29: the researcher reports about USD 23 Claude credit left (no top-up), cap set at the
# spend logged then (78.54) + 21, so a call in flight cannot cross the credit
BUDGET_USD = {"anthropic": 99.54, "openai": 98.0}

GRAPHDB_URL = os.environ.get("PPH21_GRAPHDB_URL", "http://localhost:7200")
GRAPHDB_REPOSITORY = os.environ.get("PPH21_GRAPHDB_REPOSITORY", "pph21")


def _read_env_file(path=ENV_FILE):
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().removeprefix("export ").strip()] = value.strip().strip("'\"")
    return values


def secret(*names):
    """First non-empty value among names, from the environment, then from .env. None if absent."""
    file_values = _read_env_file()
    for name in names:
        value = os.environ.get(name) or file_values.get(name)
        if value:
            return value
    return None


def anthropic_key():
    return secret("ANTHROPIC_API_KEY", "CLAUDE_API_KEY")


def openai_key():
    return secret("OPENAI_API_KEY")
