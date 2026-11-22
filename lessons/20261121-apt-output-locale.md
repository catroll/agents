# Parse package-manager output with `LC_ALL=C`

Date: 2026-11-21

## Symptom

A script that classified "script package missing on this host" by running

```sh
apt-cache policy "$pkg" | grep -E 'Candidate:|Installed:'
```

reported **every** missing package as `NO-PACKAGE`, including `haproxy`, `php-cli`
and `pipx`, which were plainly in the archive. Installed packages still parsed
correctly because their name was on the command line, so the failure looked like
"the archive is empty" rather than "the parser matched nothing".

The second half of the bug was silent: `apt-cache policy` exited 0 and printed a
candidate version, so only the labels were lost.

## Cause

`apt`/`dpkg` localize their field labels. On this host (`LANG=zh_CN.UTF-8`) the
output is:

```
haproxy:
  已安装：(无)
  候选： 3.2.25-0ubuntu0.26.04.2
```

There is no `Candidate:` string, so `grep 'Candidate:'` returns empty and the
downstream logic treats "no label" as "no package".

## Rule

Any script that parses `apt`, `apt-cache`, `apt-get`, `dpkg-query` or
`dpkg -l` output runs the query with `LC_ALL=C`:

```sh
LC_ALL=C apt-cache policy "$pkg"
LC_ALL=C dpkg-query -W -f='${Package}\t${Version}\n'
```

Alternatively use a machine interface that has no translatable labels
(`apt-cache madison`, `apt-get -s install`, `dpkg-query -f` with explicit
fields). Never grep human-readable English labels from a localized CLI.

## Check

```sh
# before: empty
apt-cache policy haproxy | grep 'Candidate:'
# after: one line
LC_ALL=C apt-cache policy haproxy | grep 'Candidate:'
```

## Negative result

`apt-cache policy` itself exited 0 in both cases, so `set -e` and exit-code
checks do not catch this. The only reliable signal is a unit check that a known
package (`bash`, `git`) yields a non-empty candidate under the same locale.

## Scope

Global: affects any package audit or install-plan script, not only the
`stdenv` audit that hit it. The audit's first comparison (`missing-candidates.tsv`)
was wrong until the queries were rerun with `LC_ALL=C`; the corrected tables are
`missing-available.tsv` / `missing-gone.tsv`.
