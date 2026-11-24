# A project rename needs three passes; one global replacement creates garbage

**Signal.** After renaming a project, source and docs contain doubled words or
mangled paths:

```text
// Command the the channel system runs ...
| 位置变更 | 从 ~/Projects/Mine/NewAPI渠道系统 移到 tools/newapi-NewAPI渠道系统 |
```

and the old name still shows in the UI because the brand was split across tags
(`key<span>ops</span>`), which a plain `grep keyops` never matches.

**Cause.** A single case-insensitive replacement was run over identifiers
(module, imports, binary, config, DB, cookie, env prefix, directories) and
prose together. Identifiers need a slug (`newapi-channel`), prose needs the
display name (`NewAPI渠道系统` / `NewAPI Channel System`), and possessives or
split markup need a human.

**Check.** After the mechanical pass, run all of:

```sh
grep -Rin 'oldname' . --exclude-dir=.git
grep -RinE '\b(the|a|an) \1\b|NewAPI渠道系统[ ]+[一-龥]' .
go build ./... && go test ./...
curl -s http://127.0.0.1:<port>/ | grep -ci oldname
```

Also list the router and assert no URL path contains the old name. A build
passes fine with broken comments and dead doc links.

**Fix.** Three ordered passes: (1) technical identifiers, longest first, plus
file/dir renames; (2) prose per language; (3) manual review of every remaining
hit (possessives, split brand markup, table names, docs links). Keep historical
docs only if the header says they are archived under the old codename, and never
let the old name stay in a live route, cookie, config key or generated link.
