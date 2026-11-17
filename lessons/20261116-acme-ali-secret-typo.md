# `You don't specify aliyun api key and secret yet.` is usually a misspelled key in account.conf

**Signal.** `~/.acme.sh/acme.sh --issue --dns dns_ali -d <domain> ...` reaches
DNS-01, prints `Adding TXT value: ...`, then immediately fails:

```
You don't specify aliyun api key and secret yet.
Error adding TXT record to domain: _acme-challenge.<domain>
```

It is not a missing Aliyun account, a wrong key, or DNS delegation. On this
machine the account file had the public key under the correct name but the
secret under a misspelled one:

```
# broken
SAVED_Ali_Key='LTA...'
SACED_Ali_Secret='uNt...'     # SACED, not SAVED

# what dns_ali.sh actually loads
SAVED_Ali_Key='LTA...'
SAVED_Ali_Secret='uNt...'
```

`dns_ali.sh` reads `SAVED_Ali_Key` / `SAVED_Ali_Secret` through acme.sh's account
loader. One letter missing makes both look absent.

**Check before touching the Aliyun console:**

```bash
grep -E '^(SACED|SAVED)_Ali_(Key|Secret)=' ~/.acme.sh/account.conf \
  | sed -E 's/=(.{4}).*/=\1.../'
```

If the secret is under `SACED_`, back up the file and rename the key:

```bash
cp -p ~/.acme.sh/account.conf ~/.acme.sh/account.conf.bak.$(date +%Y%m%d-%H%M)
sed -i 's/^SACED_Ali_Secret=/SAVED_Ali_Secret=/' ~/.acme.sh/account.conf
```

Then rerun the same `--issue` command. On 2026-11-16 this went from exit 1 to
exit 0 and issued `track.us.ectrump.com` under
`~/.acme.sh/track.us.ectrump.com/` (fullchain + key, SAN matches, notAfter
2027-02-14).

**Do not blame the CNAME.** The host `track.us.ectrump.com` CNAMEs to
`track-us.engagelab.email`, but DNS-01 asks for
`_acme-challenge.track.us.ectrump.com`, a separate name with no CNAME; the TXT
record belongs in the Aliyun-hosted `ectrump.com` zone. The CNAME of the host
is irrelevant to this challenge.

**Transient curl errors are not the failure.** The successful run still logged
`curl` 35 (TLS connect) and 28 (timeout) during the DNS wait, then
`Success for domain ...`. Fix the credential first; only investigate network
errors if the TXT add itself fails.
