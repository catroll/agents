# A capture device that just opened is not silent — and a vendor's 200 can be a failure

**Signal 1 (audio).** A browser microphone recorder ended its turn ~1.3 s after
the microphone opened, with `heardSpeech = true`, and uploaded ~42 KB that the
ASR vendor rejected as "no valid speech". Per 20 ms frame the recording was a
decaying thump and then nothing:

```
0.02s:-13.6  0.10s:-35.3  0.20s:-47.0 ... 1.28s:-64.3   (dBFS)
```

**Cause.** Opening a suspended capture stream resumes the analog input, and it
settles with a transient tens of dB above any sensible speech floor. An RMS gate
sees that as speech; the browser's `noiseSuppression`/`autoGainControl` then gate
the steady room noise to −80 dBFS, so the trailing-silence rule ends the turn
before the person has said anything. The same device reads −20 dBFS of sub-80 Hz
rumble through `parec`, because the browser's speech processing removes exactly
that. Check both sides before blaming the hardware:

```bash
parec --format=float32le --rate=16000 --channels=1 --latency-msec=50 > mic.raw
# and record one turn through the app itself, then print per-20 ms dBFS
```

**Fix.** Ignore the first ~400 ms when deciding whether speech started (keep the
samples in the upload), and never let the speech decision be made in the first
100 ms of a stream — that is a decision about the device, not the user.

**Signal 2 (mapping).** The same endpoint answered HTTP 500 for that recording.
The ASR adapter raised a bare `RuntimeError` for every vendor condition, while
the route caught only its own `AIProviderError`/`httpx`/`ValueError`; a vendor
answer of `X-Api-Status-Code: 20000003` ("Normal silence audio") therefore became
an unhandled exception.

**Check.** Two greps that should agree, because they are in different files and
nothing enforces the contract:

```bash
grep -n "raise " <adapter>.py
grep -n "except " <route>.py
```

Exercise the *successful-but-empty* answer in a test, not just a transport error:
mock `HTTP 200` with the vendor's status header and assert a 4xx.

**Generalisable.** "ASR failed" is three different facts — the audio had no
speech (4xx), the provider failed (5xx), the binding is unconfigured (503) — and
a status code that collapses them tells the next person nothing. Also: a vendor's
HTTP 200 means "the RPC arrived"; the verdict is in the body or a header.

