"""Prompt templates of the acquisition pipeline (skeleton Section V, LLM configuration).

The mock LLM does not read them. They are here so the full system starts from a written contract, and so the app can
show what would be sent to a real model. Every placeholder is filled from the document or from the graph, never
from S^E or a gold Delta.
"""
import json

RELEVANCE = """You maintain a knowledge base for Indonesian PPh 21 withholding of permanent employees.
Read the document below. Does it change how PPh 21 of permanent employees is calculated, or how a company policy
in the knowledge base applies? Answer as JSON: {{"relevant": true|false, "quote": "<verbatim sentence from the document>"}}.
The quote must be copied exactly; it is checked against the document.

Document {doc_id}:
{text}
"""

DRAFT = """You maintain a knowledge base for Indonesian PPh 21 withholding of permanent employees.
Write one update (Delta) for the document below, as JSON that conforms to the Delta schema.

Rules of the representation:
- A rule produces exactly one fact with an expression. Allowed functions: {functions}.
- valid_from and valid_until are the legal validity of the rule. recorded_on is left empty; the system sets it to the
  issue date of the document.
- To repeal a rule, add a new rule with "supersedes": [old id]. Never edit an existing rule.
- Copy tables with the extract tool ({{"extract": ...}}) instead of typing rows.
- Every rule and table has a source with a verbatim quote from the document.

Facts and rules already in the knowledge base (id, fact produced):
{context}

Document {doc_id}, issued {issued}:
{text}
"""

REPAIR = """Your update was rejected by the verification gates. Gate feedback:
{feedback}
Return a corrected Delta for the same document, as JSON, or {{"give_up": true}}.
"""


def render_relevance(doc_id, text):
    return RELEVANCE.format(doc_id=doc_id, text=text)


def render_draft(doc_id, issued, text, context, functions):
    return DRAFT.format(doc_id=doc_id, issued=issued, text=text, functions=", ".join(sorted(functions)),
                        context="\n".join(f"- {rid}: {fact}" for rid, fact in context))


def render_repair(gates):
    return REPAIR.format(feedback=json.dumps(gates, indent=2))
