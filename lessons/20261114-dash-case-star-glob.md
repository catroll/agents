# dash rejects a `*)` case default in a Makefile recipe

**Signal.** `/bin/sh: Syntax error: word unexpected (expecting ")")` and `dash -n`
points at the `*)` line. GNU make on this machine runs recipes with `/bin/sh`,
which is dash. The working directory was not empty.

**Why it matters.** dash pathname-expands an unquoted `*` in a `case` pattern.
`*)` then stops being a single pattern and the `)` is no longer the terminator.
An empty directory hides it, so `make -n` from a clean tree is not proof.
Quoting the pattern as `"*")` still failed `dash -n` on this dash.

**Check.** Do not write a star default. Match the known arms, then test the
variable:

```sh
sc=
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) sc=x86_64 ;;
esac
if [ -z "$sc" ]; then
  echo "unsupported"
fi
```

Feed the expanded recipe (`make -n`) to `dash -n` from a directory that
contains files.
