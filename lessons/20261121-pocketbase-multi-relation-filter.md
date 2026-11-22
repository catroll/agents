# PocketBase multi-relation filter `field ?= "id"` matches nothing

**Signal.** A guard that asks "does any row name this record" returns zero for a
multi-relation even though the stored array visibly contains the id. Swapping in
`field.id ?= "id"` matches.

**Cause.** On a multi-relation, `?=` compares the field itself, not the related
record's id, so the id never matches. The working form joins through the relation:
`field.id ?= {:id}`. A single relation still uses `field = {:id}`. The same form
appears in the announcement audience query:
`departments.id ?= {:dept}`.

**Fix/check.** Choose the filter by `RelationField.MaxSelect`: `= {:id}` for a
single relation, `<field>.id ?= {:id}` for a multi-relation. A guard test must
insert a row whose multi-relation contains the target id; a query that matches
nothing fails silently and looks like "no references".
