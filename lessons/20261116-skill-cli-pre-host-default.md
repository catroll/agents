# One skill script times out while a sibling script on the same domain works

Signal: `{"success": false, "error": "<urlopen error [Errno 110] Connection timed out>"}`
from one ClawX/skill CLI, while another script of the same family calls
`https://youqian.jd.com` successfully at the same moment. Retrying the failed
script reproduces it; `curl` against the host the working script used returns
`http=200`.

Root cause class: the failing script has its **own** default base URL, and that
default points at an internal/pre host that is not routable from here. In
`news-search/scripts/cli.py` (v0.0.1) line 45:

```python
base_url = os.environ.get("CLAWX_BASE_URL", "https://clawx-pre.jd.com")
```

`https://clawx-pre.jd.com` times out (`curl -w '%{http_code}'` = `000`, connect
never completes), while `https://youqian.jd.com/api/gateway/youqian/search`
answers `http=200`. The same package family's other scripts default to
`https://youqian.jd.com`, which is why only one skill looked broken.

Check before touching the network:

```sh
grep -rn 'CLAWX_BASE_URL' ~/.dsh/skills/*/scripts/*.py ~/.dsh/skills/*/skills/*/scripts/*.py
```

Fix with the documented override instead of editing vendor code, in the same
marker block as the API key (idempotent):

```sh
export CLAWX_BASE_URL='https://youqian.jd.com'
export CLAWX_JR_API_KEY='...'
```

Then re-run the failing script through the profile alone
(`zsh -c 'source ~/.zshrc; python3 <script> ...'`) and assert it returns real
rows.

Related: every one of these ClawX scripts also carries a hardcoded fallback
`apikey` (`os.environ.get("CLAWX_JR_API_KEY", "clawx_abc1...")`). If the env var
is missing the script silently uses that shared key instead of failing, so a
"working" call does not prove the user's key is configured. Check the key was
actually read (`blogger_api.py` logs `apikey 来源: env:CLAWX_JR_API_KEY`).
