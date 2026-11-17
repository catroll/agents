# A template copy reverts production when the template is older than the live file

**Signal.** A deploy step

```bash
cp conf/nginx/x.conf.prod conf/nginx/x.conf && nginx -t && nginx -s reload
```

runs successfully and the headers you verified a minute earlier disappear. The
live file's sha256 is now the *pre-fix* value, and the commit that added the fix is
weeks old.

**Cause.** The fix had been installed by hand into the live file (`scp
repo/x.conf.prod host:/opt/.../conf/x.conf`), so the live file was newer than the
shipped template `x.conf.prod` that sat next to it. Automating "materialize the
template" therefore copied the **old** template over the live fix — a working deploy
step that is, without its preceding rsync, a rollback command. Here the drift was a
month old (auth.d3v.cn), so the deploy had been silently reverting the cache fix all
along.

**Check.**

- Run the materialize **inside** the deploy, immediately after the rsync, and put
  that order in a comment next to the `cp`. Do not expose it as a standalone target:
  it will be used on its own and roll the config back.
- Assert the observable header after reload, not the file contents. This caught the
  incident within one run:

  ```bash
  asset=$(curl -fsS https://host/ | grep -oE '/static/js/main\.[A-Za-z0-9]+\.js' | head -1)
  curl -fsS -r 0-0 -D - -o /dev/null "https://host$asset" | grep -iE 'cache-control|vary|set-cookie'
  ```

  Without that verifier the regression looks like a successful deploy.
- Before automating, compare live vs template and expect the live one to be newer
  (`sha256sum host:conf/x.conf repo/x.conf.prod`). If they differ, sync the template
  from the repo first, then materialize — otherwise the copy direction is backwards.
- `*.conf.prod` is also inert to nginx (`include *.conf`), so the same automation
  must materialize *and* reload; copying alone changes nothing.
