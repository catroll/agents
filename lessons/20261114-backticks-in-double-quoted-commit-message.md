# Backticks inside a double-quoted `git commit -m` message are command substitution

**Signal.** After

```sh
git commit -m "… an explicit summary (`summary_explicit`), and archive rows …"
```

the commit landed but the message printed

```
bash: 行 1: summary_explicit: 未找到命令
```

and `git log -1 --format=%B` showed `explicit summary\n(), and archive rows`
— the backticked word was executed as a command substitution and replaced by
empty output. The commit "succeeded", so nothing looks broken until someone
reads the message.

**Fix.** Pass the message on stdin with a *quoted* heredoc, which disables all
expansion:

```sh
cat > /tmp/commit-msg.txt <<'EOF'
… message mentioning `summary_explicit` … (backticks stay literal)
EOF
git commit --amend -F /tmp/commit-msg.txt   # unpublished commit: amend is safe
```

Or escape the backticks (`\``) / use single quotes around the whole message.
After any commit message containing backticks, `$`, or `!`, verify it with
`git log -1 --format=%B | cat -A` or `git log -1 --format=%B`.

Never `git push` first and discover this later: amending is only safe while the
commit is unpushed.
