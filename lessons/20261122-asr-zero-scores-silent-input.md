# A speech API can answer 200 with all-zero scores when it heard nothing

**Signal.** An ASR / pronunciation-assessment call succeeds (HTTP 200,
`RecognitionStatus: "Success"`) but the result is useless: `PronScore`,
`AccuracyScore`, `FluencyScore`, `CompletenessScore` are all `0`, `ProsodyScore`
is absent, `Display` is `"."`, and every reference word comes back with
`ErrorType: "Omission"`. The UI shows a 0/100 assessment, not an error.

**Cause.** The audio contains no speech (muted mic, wrong input device, or a
silent stream). The service treats that as a successful recognition of nothing
and scores it. Nothing is wrong with the request shape, the key, or the parser.

**Check.**

```bash
ffmpeg -v info -i rec.wav -af volumedetect -f null - 2>&1 | grep max_volume
# max_volume: -91.0 dB   (digital silence; speech is roughly -30..-5 dBFS)
```

Prove the pipeline separately with a known-good clip — a TTS lesson segment
worked end to end (`PronScore 89.7`, accuracy 96, prosody 90.6, phonemes
present), which rules out the API path.

**Fix.** Reject near-silence before calling the vendor: parse `max_volume` from
the transcode, return 422 below about -50 dBFS with the measured value, and
treat an empty `Words` list as an input error. In the UI, show the input device
and a live level bar, and let the user pick the microphone — the system default
is not always the device that carries sound.

**Evidence (2026-11-22).** Two recordings of "hello, world" (2.76 s, 3.48 s)
returned `display: "."`, both words `Omission`, all scores 0.0. `volumedetect`
on silence: `max_volume: -91.0 dB`; on speech: `-4.4 dB`. After the guard, the
same silence answers `422 录音里没有声音（峰值 -91 dB）` and the speech clip
still scores normally.
