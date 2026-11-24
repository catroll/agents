# `web_fetch` 200 with only the page title, or an `Access Denied` body, is not page content

## Symptom

- `web_fetch https://www.sendcloud.net/aboutUs/` → `Fetched … (HTTP 200)` and the only text is
  `Aurora SendCloud-关于我们-武汉闪达科技有限公司-提供邮件短信解决方案` (the `<title>`).
- `web_fetch https://www.sendcloud.net/email/` → 200 with an empty body.
- `web_fetch https://www.engagelab.com/zh_CN/` → 200, but only navigation labels, no page copy.
- `web_fetch https://www.baike.baidu.com/item/…` → 200 and the word `百度百科`.
- `web_fetch https://ir.jiguang.cn/` → `HTTP 403` with an Akamai `Access Denied` page.

All of these pages contain the facts in a browser. The fetch is not proof of absence.

## Cause

`sendcloud.net`, `audora`-style marketing sites and EngageLab are client-rendered (Nuxt/Vue):
the HTML shell carries the title and a JSON payload, and the text extractor drops the payload.
The 403s are WAF/CDN blocks, not missing pages.

## Check before concluding “the page has no content”

```bash
curl -sSL -A 'Mozilla/5.0' "$URL" -o /tmp/page.html
wc -c /tmp/page.html
grep -c '__NUXT__\|__NEXT_DATA__\|data-server-rendered\|window.__INITIAL' /tmp/page.html
curl -sSL "$URL/../sitemap.xml" | head        # or the site's /sitemap.xml
```

- A large HTML file with `__NUXT__` / `__NEXT_DATA__` means the body is in JSON; read it with
  `python3`/`jq` instead of a text extractor.
- `sitemap.xml` enumerates the real routes (`/aboutUs`, `/chineseSms`, `/voiceSms`, …) even when
  the rendered text is empty.
- For the same fact prefer a server-rendered source: the company's newsroom, a press release,
  a docs site (`docs.aurorasendcloud.com`), or a search-result snippet that quotes the page.
- A WAF `403 Access Denied` body can be summarised as content if you only skim it; check the HTTP
  status and the literal string `Access Denied`.

## Negative results

- `web_fetch` on `sendcloud.net`, `sendcloud.net/email/`, `engagelab.com/zh_CN/`, `baike.baidu.com`
  and `ir.jiguang.cn` never produced the page body in this session.
- `curl -sSL https://ir.jiguang.cn/…` with a browser UA still returned 451 bytes of `Access Denied`.
- Reading the same facts worked from `jiguang.cn/media/news/*` press releases, the docs site, and
  search snippets quoting the blocked page.

## Rule

A 200 with no text, or a 403 with a WAF page, is a **rendering or access limitation**. Say “could
not read that page this way”, not “the page does not say it”; switch to sitemap, embedded JSON,
docs site, newsroom, or a different source before writing the fact down.
