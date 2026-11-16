# An async script can wait for a later parser-blocking script

**Signal.** The resource entry says the script downloaded early, but the DOM
change it should cause happens seconds later, exactly when a *later*
`<script src=...>` without `defer`/`async` finishes. Measured in Firefox 157 on
`www.markjour.com`:

- `highlight.min.js` resource: `start 135 ms`, `responseEnd 340 ms`
- `pre code.hljs` MutationObserver (BiDi preload): `5165 ms`
- the 497 KB synchronous `instantsearch.production.min.js` was delayed 5 s

The async script had been injected **before** the synchronous tag, so "it is
async, therefore it is independent" was false.

**Check.** Measure the effect, not only the resource. Use a WebDriver BiDi
preload script to install a `MutationObserver` on `document` before the page
runs, and print both the effect timestamp and
`performance.getEntriesByType('resource')`. A resource that finished early while
the effect lands with a synchronous script is this failure.

**Fix.** Make every later script `defer`/`async`, or remove it from the path.
For a library needed only on some pages, inject it conditionally and initialise
from its own `script.onload`; do not gate it on `window.onload`, which also waits
for images and async scripts.

**Negative result.** Moving the loader earlier in the body was not enough while
a synchronous search bundle remained after it. Reordering alone looked
plausible and did not change the 5 s result. The same page also loaded a 2.7 MB
optional Mermaid bundle everywhere; the dominant fix was conditional loading,
not mere reordering.
