# Driving a real browser

A browser is available on this machine. Do not conclude otherwise without trying
these steps, and do not report a visual or layout finding from static analysis
alone when a browser could settle it.

- **Both are snaps, and a snap needs paths outside the workspace.** Firefox wants
  `/run/user/1000/snap.firefox` and `$HOME/snap/firefox`. The file sandbox refuses
  those, and the failure reads as a broken browser rather than a policy denial:
  `cannot create XDG_RUNTIME_DIR folder ... read-only file system`. Launch with
  `sandbox_permissions: danger-full-access`, and say why in the justification.
- **The profile must be inside the workspace and must already exist.** `/tmp` is
  refused with `Could not find profile folder`, and the same error appears for a
  workspace path that was `rm -rf`'d without a following `mkdir -p`; create
  `$PWD/.cache/ff/prof` before launching.
- **Use the real binary, not the wrapper.** `/snap/bin/firefox` is a symlink to
  `/usr/bin/snap` and geckodriver rejects it with
  `binary is not a Firefox executable`. The binary is
  `/snap/firefox/current/usr/lib/firefox/firefox`.
- **`geckodriver` is installed** at `/snap/bin/geckodriver`, but the snap
  wrapper can fail before it listens:
  `cannot create transient scope: DBus error "org.freedesktop.DBus.Error.InvalidArgs":
  [Process 4 is a kernel thread, refusing.]`. That is an environment failure (the
  wrapper is `/usr/bin/snap`), not a Firefox or WebDriver problem. Fall back to
  Firefox's own WebDriver BiDi remote agent, which needs no geckodriver —
  `/snap/firefox/current/usr/lib/firefox/firefox --headless --no-remote
  --profile "$PWD/.tmp/ff/prof" --remote-debugging-port 9222 about:blank` logs
  `WebDriver BiDi listening on ws://127.0.0.1:9222`. Connect to
  `ws://127.0.0.1:9222/session` (a plain `GET /json/version` is 404). Node 22's
  global `WebSocket` is enough; the minimal sequence is `session.new` →
  `browsingContext.getTree` → `browsingContext.navigate` → `script.evaluate`
  (return `JSON.stringify(...)`, then parse the string from `result.value`) →
  `browsingContext.captureScreenshot` (base64 in `data`) → `session.end`. Use
  `browsingContext.setViewport` for desktop/mobile widths and click
  `[data-bs-theme-value="dark"]` to exercise AdminLTE's colour control.
- **`browsingContext.setViewport` takes `context`, not `contexts`.** Firefox 157
  rejects `contexts: [id]` with `At least one of "context" or "userContexts"
  arguments should be provided`; pass
  `{ context, viewport: { width, height }, devicePixelRatio: 1 }`. `navigate`
  and `captureScreenshot` also use the singular `context`.
- **WebDriver is a plain HTTP protocol**, so `curl` is enough when geckodriver
  does work — Selenium, Playwright and jsdom are not needed and installing them
  usually fails offline.
- **Do the whole run in one bash call.** Background processes do not survive
  across calls, so start the app, start geckodriver, create the session, drive the
  page, read the result and clean up in a single command.
- **Read `getComputedStyle`, do not squint at a screenshot.** For any factual
  question — which colour, which font, is it hidden, what is the size — a
  `execute/sync` returning the computed value is decisive where an image is an
  opinion. Keep the screenshot for layout and for anything you would only notice
  by looking.
- **Form fields may have no `id`.** Select with `querySelector('input[name=...]')`.
  A missing element throws, the script returns nothing, and if the result was
  discarded the whole step fails silently. Always print what the script returned.
- **Screenshot what a user sees, in their language, in each theme.** Static
  analysis cannot see a value the server supplies at render time. A page can pass
  every template test and still show `pending_payment` where a label belongs.
- **A page behind a login you do not have: mirror its DOM, do not skip the
  measurement.** When the component is only reachable with a session and no
  credential exists in the checkout, copy its markup class for class into a
  temporary page that loads the app's own CSS bundles (plus whatever layout
  classes the framework puts on `<body>`), serve it from the app's dev server,
  and measure before and after the change with `getBoundingClientRect()`. Keep
  the class list identical to the source — a harness that drifts proves nothing —
  delete the page afterwards, and say plainly that it verifies the CSS and the
  classes, not the page.
- **One BiDi session at a time, and `session.end` in a `finally`.** A probe that
  throws between `session.new` and `session.end` leaves the session open, and the
  next run dies with `session not created: Maximum number of active sessions`
  before it navigates anywhere. `GET /` on the port still answers `200`, and a
  bare `session.end` on a stale connection returns `invalid session id`, so the
  recoverable move is to kill that Firefox (by the pid you started) and relaunch;
  the durable one is to end the session in `finally`.

- **BiDi commands take the browsing context id, not the session id.**
  `session.new` returns `{sessionId}`; `browsingContext.getTree` returns
  `contexts[].context`. Use that second id in `script.evaluate`
  (`target: {context}`), `browsingContext.captureScreenshot` and
  `input.performActions` (`context`). Passing the session id fails with
  `no such frame: Browsing Context with id <session-id> not found`, and
  `getTree`/`navigate` succeeding makes it look like the page is the problem.
- **Headless Firefox cannot verify `:focus` / `:focus-within` styles.**
  It reports `document.hasFocus() === false` and `document.activeElement` set at
  the same time; `el.matches(':focus')` and `.closest('.x').matches(':focus-within')`
  stay `false`, so the focused computed colour equals the idle one and reads as a
  CSS bug. Use headless Chromium (`/usr/bin/microsoft-edge --headless=new
  --remote-debugging-port=9223`) over CDP (`GET /json/list` → page
  `webSocketDebuggerUrl`, then `Page.navigate`, `Input.dispatchMouseEvent`,
  `Runtime.evaluate`) where `document.hasFocus()` is `true` and the state is real.
- **A CSS harness must load every stylesheet the page loads, in page order.**
  Loading only the sheet being edited can miss a more specific rule from another
  sheet: `.article-tag a { text-decoration: none }` lost to
  `.markdown-body a:hover { text-decoration: underline }` in
  `github-markdown.css`, so idle looked correct and hover underlined. Assert the
  computed state (`getComputedStyle(el).textDecorationLine`), not only the colour.
- **`prefers-color-scheme` cannot be emulated over BiDi.** Firefox 157 answers
  `emulation.setEmulatedMedia` with `unknown command`, so a dark-theme check
  cannot be forced with the protocol. Put
  `user_pref("layout.css.prefers-color-scheme.content-override", N);` in the
  profile's `user.js` and restart Firefox: `1` is light and `0` is dark, the
  opposite of the intuitive reading. Assert the outcome with
  `window.matchMedia('(prefers-color-scheme: dark)').matches` and the computed
  colours (`body`/card background), never the pref number alone.
- **`window.prompt()` is auto-dismissed in headless Firefox before BiDi can
  answer it.** `browsingContext.userPromptOpened` does arrive, but a following
  `browsingContext.handleUserPrompt` fails with `no such alert` and the page
  already received `null`. For a token-gated flow, seed `sessionStorage` /
  `localStorage` where the script reads the value and stub
  `window.confirm = () => true`; verify the prompt itself separately.
