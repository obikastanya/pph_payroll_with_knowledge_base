"""Dump the base knowledge view at a date: rules, params, tables, facts."""
import sys
from datetime import date
from common import base_at

d = sys.argv[1] if len(sys.argv) > 1 else "2026-10-28"
kb = base_at(d)
v = kb.view(date.fromisoformat(d))
print("UPDATES", [u.update_id for u in kb.updates][-5:])
for f in sorted(v.facts.values(), key=lambda f: f.id):
    print(f"FACT {f.id} {f.fact_type} {f.fact_scope} out={f.output}")
for r in sorted(v.rules.values(), key=lambda r: (r.produces, r.id)):
    print(f"RULE {r.id} [{r.layer}/{r.modality}/{r.scope}] {r.valid_from}..{r.valid_until} -> {r.produces}"
          f"{' IF ' + r.condition.text if r.condition else ''} := {r.expression.text}"
          f"{' FP' + str((r.fixed_point[0].text, r.fixed_point[1].text)) if r.fixed_point else ''}"
          f"{' OV' + str(r.overrides) if r.overrides else ''}")
for name, recs in sorted(v.params.items()):
    for p in recs:
        print(f"PARAM {name} {p.id} {p.valid_from}..{p.valid_until} = {p.value!r}")
for name, recs in sorted(v.tables.items()):
    for t in recs:
        print(f"TABLE {name} {t.id} {t.table_kind} {t.valid_from}..{t.valid_until} rows={len(t.rows)}")
for c in v.constraints:
    print(f"CON {c.id} {c.valid_from}..{c.valid_until} {c.condition.text if c.condition else ''} => {c.assertion.text}")
