# Headless Firefox keeps AudioContext suspended, so a level meter reads 0

**Signal.** A Web Audio level meter shows `0%` and `getByteTimeDomainData`
returns all `128`, while `MediaRecorder` on the same stream records audio with
real energy (an uploaded clip measures `max_volume: -19.8 dB`). No exception is
thrown.

**Cause.** The browser has no audio output device in headless mode, so
`AudioContext.state` stays `"suspended"` and `currentTime` stays `0`; the graph
never renders and the analyser sees silence. `resume()` does not fix it, and
calling `close()` while `resume()` is pending rejects with
`InvalidStateError: Closed before resume completed`.

**Check (in the page).**

```js
const ctx = new AudioContext();
// after starting: ctx.state, ctx.currentTime, and the analyser's byte data
```

`state === "suspended"` plus `currentTime === 0` means the meter cannot work
here — not that its arithmetic is wrong.

**Fix.** Do not debug the meter logic from a headless run. Gate the meter on
`state === "running"` (hide it otherwise, so a suspended context never shows a
misleading flat bar), and verify capture by measuring the recorded blob's level
(e.g. transcode to WAV and read `volumedetect`). Keep `.catch()` on `resume()`
and `close()`.

**Evidence (2026-11-22).** Headless Firefox 157 with
`media.navigator.streams.fake=true`: `ctx.state=suspended`, `currentTime=0`,
analyser RMS `0.0000`, while the uploaded Ogg/Opus blob measured
`peak_db=-19.8`. After gating on `running`, the meter stays hidden in headless
and shows no console error.
