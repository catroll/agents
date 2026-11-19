# A `#` inside an unquoted YAML plain scalar starts a comment

**Signal.** A hand-edited `openapi.yaml` fails with:

```
yaml.parser.ParserError: while parsing a block mapping
  in "openapi.yaml", line N, column 19
expected <block end>, but found '<scalar>'
  in "openapi.yaml", line N+3, column 21
```

The reported line often looks valid. Look at the preceding description line for
` # ` (space-hash-space). In a plain scalar YAML treats it as a comment, drops
the rest of that line, and the next indented line is then a stray scalar.

Bad:

```yaml
description: Rejected names contain %, $, # or *. Suffixes are ...
```

Good — remove the character, quote the whole scalar, or use a block scalar:

```yaml
description: Rejected names contain percent, dollar, hash or star. Suffixes are ...
```

or

```yaml
description: "Rejected names contain %, $, # or *. Suffixes are ..."
```

**Check.** After editing, always run `python -c 'import yaml; yaml.safe_load(...)'`
before using the file; the parser error points at the line after the real
comment, not at the `#` itself.
