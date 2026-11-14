"""GraphDB as the store of the knowledge graph (repository pph21, one named graph per update).

Uses the RDF4J REST protocol that GraphDB serves: POST/DELETE /repositories/<repo>/statements for loading and
clearing, GET .../statements with Accept application/x-trig for export, and the SPARQL endpoint for queries.
"""
import json
import urllib.parse
import urllib.request

from rdflib import Dataset

from ..config import GRAPHDB_REPOSITORY, GRAPHDB_URL
from . import rdf


def _endpoint(path=""):
    return f"{GRAPHDB_URL}/repositories/{GRAPHDB_REPOSITORY}{path}"


def _request(method, url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def available():
    try:
        _request("GET", _endpoint("/size"), timeout=5)
        return True
    except OSError:
        return False


def size():
    return int(_request("GET", _endpoint("/size")))


def clear():
    _request("DELETE", _endpoint("/statements"))


def upload(kb, replace=True):
    """Store the knowledge base; with replace=True the repository is cleared first."""
    if replace:
        clear()
    data = rdf.to_dataset(kb).serialize(format="trig").encode("utf-8")
    _request("POST", _endpoint("/statements"), data, {"Content-Type": "application/x-trig"})
    return size()


def download(name="K"):
    """Read the whole repository back into a KnowledgeBase."""
    data = _request("GET", _endpoint("/statements"), headers={"Accept": "application/x-trig"})
    ds = Dataset()
    ds.parse(data=data.decode("utf-8"), format="trig")
    return rdf.from_dataset(ds, name)


def select(query):
    """SPARQL SELECT; returns a list of dicts from variable name to plain string value."""
    body = urllib.parse.urlencode({"query": query}).encode("utf-8")
    raw = _request("POST", _endpoint(), body, {"Accept": "application/sparql-results+json",
                                                "Content-Type": "application/x-www-form-urlencoded"})
    res = json.loads(raw)
    return [{k: v["value"] for k, v in b.items()} for b in res["results"]["bindings"]]
