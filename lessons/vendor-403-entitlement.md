# A vendor 403 naming a "resource" is an entitlement, not an auth, failure

**Signal.** A speech/ASR API call fails with `HTTP 403` and a body like
`code=45000030, message=[resource_id=volc.bigasr.auc] requested resource not granted`,
for every model line you try. It reads like "forbidden because the credential is
wrong", so the reflex is to add or change auth headers.

**Check.** Send the identical request twice, once with the real credential and
once with a deliberately invalid one, then compare the codes:

- bogus key: `HTTP 401, code=45000010, message=Invalid X-Api-Key`
- real key:  `HTTP 403, code=45000030, message=[resource_id=...] requested resource not granted`

Two *different* codes prove the credential was read and accepted; the account
simply has no entitlement for that resource. The fix is to enable/activate the
service for the key's project in the console, not to touch the code. This one
extra request also gives the user the single action they must take.

**Related, Volcengine Doubao speech.** The current console issues one API key,
sent as `X-Api-Key` alone ("在任意接口中，填入header即可，不用填写appid" —
`docs/doubao-voice/api-key-usage`). `X-Api-App-Key` + `X-Api-Access-Key` are the
old console's pair; a 403 mentioning the resource is not evidence they are
still needed.


