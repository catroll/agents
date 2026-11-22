# "The repo is private" was never checked logged-out

## Signal

Reviewing a repository whose remote was SSH (`git@gitee.com:stdenv/stdenv`),
`curl -o /dev/null -w '%{http_code}'` returned `200`. Fetching the same URL
without authentication returned the full file tree, both branches, commit list,
and a "下载ZIP" link — the repository was public. The working tree contained an
Aliyun access key and several passwords.

## Why it matters

Repo visibility changes the response: a leak in a private repo is a cleanup; a
leak in a public repo is an active incident (rotate first, rewrite second).
HTTP 200 alone proves nothing — Gitee and GitHub both serve login/redirect pages
with 200 in some states — and an SSH remote says nothing about visibility.

## Procedure

- Fetch the web URL logged-out (`web_fetch` or `curl -sL`) and look for the file
  listing, branch selector, and archive download. For GitHub, also query
  `https://api.github.com/repos/<owner>/<repo>`; private returns 404.
- Only after that, run the credential scan across all history
  (`git log --all -S '<literal>'`, `gitleaks detect --log-opts=--all`).
- If public: rotate every exposed credential immediately, set the repo private
  for the cleanup window, then rewrite history and force-push. Rewriting without
  rotating does not undo the exposure window.

## Negative results

`grep -ril 'public.*repo\|repo.*visib' ~/.agents/lessons` matched nothing; no
existing lesson covered verifying repository visibility before rating a leak.

Date learned: 2026-11-21.
