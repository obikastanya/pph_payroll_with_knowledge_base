"""Check that everything the full system needs is in place. Costs nothing: it only lists models, no generation.

    env\\Scripts\\python system\\tools\\check_setup.py
"""
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pph21kbs import config  # noqa: E402

OK, FAIL, WARN = "ok  ", "FAIL", "warn"


def report(status, what, detail=""):
    print(f"[{status}] {what}" + (f": {detail}" if detail else ""))
    return status != FAIL


def packages():
    needed = ["rdflib", "pyshacl", "httpx", "jsonschema", "anthropic", "openai", "pdfplumber", "scipy", "allpairspy",
              "streamlit", "plotly", "pandas"]
    missing = [p for p in needed if importlib.util.find_spec(p) is None]
    return report(FAIL if missing else OK, "Python packages in env", ", ".join(missing) or f"{len(needed)} found")


def anthropic_access():
    key = config.anthropic_key()
    if not key:
        return report(FAIL, "Anthropic key", "CLAUDE_API_KEY not found in .env or the environment")
    import anthropic
    try:
        model = anthropic.Anthropic(api_key=key).models.retrieve(config.MAIN_MODEL)
        return report(OK, "Anthropic main model", f"{model.id} available")
    except anthropic.AuthenticationError:
        return report(FAIL, "Anthropic key", "rejected (authentication error)")
    except anthropic.NotFoundError:
        return report(FAIL, "Anthropic main model", f"{config.MAIN_MODEL} not available to this key")
    except anthropic.APIConnectionError as e:
        return report(FAIL, "Anthropic API", f"no connection ({e.__class__.__name__})")


def openai_access():
    key = config.openai_key()
    if not key:
        return report(FAIL, "OpenAI key", "OPENAI_API_KEY not found in .env or the environment")
    import openai
    try:
        ids = sorted(m.id for m in openai.OpenAI(api_key=key).models.list())
    except openai.AuthenticationError:
        return report(FAIL, "OpenAI key", "rejected (authentication error)")
    except openai.APIConnectionError as e:
        return report(FAIL, "OpenAI API", f"no connection ({e.__class__.__name__})")
    gpt6 = [i for i in ids if i.startswith("gpt-6")]
    if config.SECOND_MODEL in ids:
        return report(OK, "OpenAI second model", f"{config.SECOND_MODEL} available (gpt-6 family: {', '.join(gpt6)})")
    return report(FAIL if not gpt6 else WARN, "OpenAI second model",
                  f"{config.SECOND_MODEL} not listed; gpt-6 family: {', '.join(gpt6) or 'none'}")


def graphdb():
    folder = config.REPO / "graphdb"
    license_file = folder / "graphdb.license"
    if not license_file.is_file():
        report(FAIL, "GraphDB license", f"missing {license_file} (request GraphDB Free from Ontotext)")
    import httpx
    try:
        r = httpx.get(f"{config.GRAPHDB_URL}/rest/repositories", timeout=5)
        r.raise_for_status()
        repos = [x.get("id") for x in r.json()]
        detail = f"running at {config.GRAPHDB_URL}; repositories: {', '.join(repos) or 'none yet'}"
        return report(OK, "GraphDB", detail) and license_file.is_file()
    except (httpx.HTTPError, ValueError) as e:
        return report(FAIL, "GraphDB", f"not reachable at {config.GRAPHDB_URL} ({e.__class__.__name__}); "
                                       "start it with: docker compose -f graphdb/docker-compose.yml up -d")


def main():
    results = [packages(), anthropic_access(), openai_access(), graphdb()]
    print(f"\n{sum(results)}/{len(results)} checks passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
