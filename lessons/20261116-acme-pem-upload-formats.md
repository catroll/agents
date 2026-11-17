# acme.sh `.cer` is already PEM; upload platforms that only accept `.pem`/`.crt` need a copy, not a conversion

**Signal.** A platform's certificate upload accepts only `.pem` or `.crt`, while
acme.sh produced `fullchain.cer` / `<domain>.cer`. The extension differs; the
bytes are already PEM.

Check before running any converter:

```bash
cd ~/.acme.sh/<domain>
file fullchain.cer <domain>.cer
head -1 <domain>.cer
```

`PEM certificate` / `-----BEGIN CERTIFICATE-----` means copy or rename. A real
DER file shows `data` and no BEGIN line; only then run:

```bash
openssl x509 -inform DER -in cert.cer -out cert.pem
```

**Upload set for a normal HTTPS certificate.** Use a leaf + intermediate chain
unless the platform explicitly wants the full chain:

```bash
cd ~/.acme.sh/<domain>

# leaf only, for platforms that accept exactly one certificate
cp <domain>.cer <domain>.crt

# leaf + intermediate, no root — recommended upload
awk 'BEGIN{n=0} /BEGIN CERTIFICATE/{n++} n<=2{print} /END CERTIFICATE/{if(n==2) exit}' \
  fullchain.cer > <domain>.chain.pem

# full chain (leaf + intermediate + root); some platforms reject the root
cp fullchain.cer fullchain.pem

# private key: content is already PEM; add a .pem copy if the key field also filters extensions
cp <domain>.key <domain>.key.pem
chmod 600 <domain>.key.pem
```

On 2026-11-16 this produced for `track.us.ectrump.com`:

- `<domain>.crt` — 1 certificate (leaf)
- `<domain>.chain.pem` — 2 certificates (leaf + Let's Encrypt YR1)
- `fullchain.pem` — 3 certificates (adds Root YR)
- `<domain>.key` / `<domain>.key.pem` — same RSA private key

**Verify before upload.**

```bash
# key and certificate match: the two MD5 lines must be equal
openssl x509 -in <domain>.crt -noout -modulus | openssl md5
openssl rsa  -in <domain>.key -noout -modulus | openssl md5

# leaf verifies against the intermediate
openssl verify -untrusted ca.cer <domain>.crt

# count certificates in a chain file
grep -c 'BEGIN CERTIFICATE' <domain>.chain.pem
```

**Negative result.** `openssl x509 -inform DER` on an acme.sh `.cer` fails or
produces an empty/garbled file because the input is already PEM. The extension
never decides the encoding; inspect the first line. Also do not upload `.csr`
or `.conf` from the acme.sh directory.
