# `&id001` / `*id001` appear in generated YAML

**Signal.** A script that renders YAML from dicts writes anchors into the output:

```yaml
- name: Create the resource
  headers: &id001
    Content-Type: application/json
  body: &id002
    name: ${list_name}
- name: Repeat the same create
  headers: *id001
  body: *id002
```

Nothing fails: `yaml.safe_load` resolves the aliases, the engine runs the case,
and the file parses. The damage is editorial and latent — a case that a human
edits later loses one `*id001` reference, or a reviewer cannot tell whether the
two steps were meant to share one mapping, and the file breaks with
`found undefined alias 'id001'`.

**Cause.** PyYAML dumps **object identity**, not value equality. A generator that
builds one body dict and passes it to two steps gets aliases:

```python
body = {"name": name}
steps = [step("first", body=body), step("second", body=body)]  # same object
yaml.safe_dump({"testcases": steps})                            # &id001 / *id001
```

`copy.deepcopy(data)` does not help: deepcopy preserves shared references inside
the copied graph. A JSON round-trip does break identity, but it also drops
non-JSON scalars and key order.

**Fix.** Turn aliases off at the dumper, once, and assert the output never
contains them:

```python
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

yaml.dump(data, Dumper=NoAliasDumper, sort_keys=False, allow_unicode=True)
```

Then verify the generated batch in the same command:

```bash
grep -c '&id\|\*id' generated/**/*_Regression_*.yaml   # must be 0
```

**Generalisable.** A serialiser may encode *identity* the format cannot express
usefully. Whenever a generator writes a format with a sharing mechanism — YAML
anchors, JSON `$ref`, object cycles — decide explicitly whether sharing is
intended, and assert the artefact after writing rather than trusting the dump
call to mean "the data, once each".

The sibling trap in the same generator, worth checking together: a template
value written as a raw f-string in two places (`body={"name": f"x_{RAND}"}`)
evaluates the random **twice**, so the two steps silently use different names
even though the file "looks" consistent. Reference the suite variable
(`${list_name}`) instead of re-interpolating; compare the rendered file against
the variables block, not the generator source.

Seen 2026-11-16 while generating the 38 Engagelab Regression cases
(`/tmp/gen_eng_regression.py` → `generated/Engagelab/*_Regression_*.yaml`).
