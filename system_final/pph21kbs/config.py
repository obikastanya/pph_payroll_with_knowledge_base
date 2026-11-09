"""Settings: file locations, model choice, spending limits, API keys, and the optional GraphDB endpoint.

Every setting is read from the environment first, then from the .env file in this folder (see .env.example). Key
values are never printed or logged.
"""
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"

# Specification: ontology, SHACL shapes, SPARQL queries, JSON schemas
SPEC = ROOT / "spec"
SCHEMAS = SPEC / "schemas"
QUERIES = SPEC / "queries"

# Shipped data: the starting knowledge base, its document registry, sample company policies, app presets
DATA = ROOT / "data"
SEED_KB = DATA / "kb" / "seed.trig"
REGISTRY = DATA / "kb" / "documents.csv"
POLICIES = DATA / "policies"
PRESETS = DATA / "presets"



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


def _usd(name):
    value = secret(name)
    return float(value) if value else None


# Working state written at run time (approved updates, uploaded documents, model calls); not committed
WORKSPACE = Path(secret("PPH21_WORKSPACE") or ROOT / "workspace")
DOCUMENTS = WORKSPACE / "documents"
CALLS = WORKSPACE / "calls"

# Language model used to draft updates
MAIN_MODEL = "claude-opus-5-5"

# Last tax year the checks generate cases for and examine (the year after the current one, at least 2027)
LAST_TAX_YEAR = max(2027, date.today().year + 1)

# Optional total spending limit per provider (USD) over all logged calls; None means no limit
BUDGET_USD = {"anthropic": _usd("PPH21_BUDGET_ANTHROPIC_USD"), "openai": _usd("PPH21_BUDGET_OPENAI_USD")}

GRAPHDB_URL = secret("PPH21_GRAPHDB_URL") or "http://localhost:7200"
GRAPHDB_REPOSITORY = secret("PPH21_GRAPHDB_REPOSITORY") or "pph21"


def anthropic_key():
    return secret("ANTHROPIC_API_KEY", "CLAUDE_API_KEY")


def openai_key():
    return secret("OPENAI_API_KEY")
