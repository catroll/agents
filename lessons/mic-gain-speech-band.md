# A microphone that reads loud may be an open input at +60 dB

**Signal.** A voice turn failed with "no valid speech in audio". The capture
device reported a healthy-looking `rms -23 dBFS`, yet the 300–3000 Hz band sat at
**-58.7 dBFS** and did not move at all while a full-scale speech clip was played
to the sink. All of the power (100%) was under 80 Hz.

**Cause.** Gain, not signal. `amixer -c 1 sget 'Rear Mic Boost'` showed boost 3
(+30 dB) and `Capture` 63 (+30 dB): **+60 dB into the ADC**. At that gain an open
or unpowered input's own DC drift and sub-sonic rumble read like a usable level,
while the audible band stays at the converter's noise floor. Jack-detect
`Rear Mic Jack: on` only says a plug is inserted — a cable to a device that is
off or unpowered closes the switch too.

**Check.** Measure the speech band, not broadband RMS, and make it rise:

```bash
make audio-check                                  # speak when prompted
make audio-check ARGS="--play clip.wav"           # speaker -> room -> mic
```

A broadband number with an empty 300–3000 Hz band means "nothing audible is
connected", not "the microphone is sensitive". `amixer -c <card> sget 'Capture'`
plus the same for `<Front|Rear> Mic Boost` gives the real gain; `alsamixer -c
<card>` shows it interactively. A correct capture at this gain would clip speech,
so the gain is wrong even once a microphone works.

**Do not conclude "the mic is deaf" from a playback test alone.** The monitor
source proves what the sink *received*, not what the speaker emitted: an amp that
is off and a microphone that hears nothing produce the same recording. Only the
person in the room can separate them — ask, or have them speak during the quiet
phase and read the band level.

**A control measurement on another pin separates "dead codec" from "dead
microphone".** Retask the same converter's other input and measure it with nothing
plugged in:

```bash
amixer -c 1 sset 'Input Source' 'Line'    # open jack: expect a quiet, flat floor
timeout 6 parec --format=s16le --rate=16000 --channels=1 --raw > line.raw
amixer -c 1 sset 'Input Source' 'Rear Mic' # restore, and read it back to be sure
```

Here the open line input read `rms -70.4 dBFS` with a flat spectrum (speech band
-75.0), while the rear-mic pin read `-20.5 dBFS` with 100% of its power under
80 Hz and a flat -58.7 dBFS speech band. That rules out the ADC, the mixer and the
port selection in one step: the mic pin has a device attached that shifts the DC
operating point and emits nothing audible. It is still not proof the *capsule* is
dead — a 4-pole (TRRS) headset in a 3-pole (TRS) mic jack lands its mic contact on
ground and looks identical — so the remaining tests are physical: unplug the
microphone and repeat (do the numbers collapse to the open-jack floor?), then
touch the plug tip with a finger (a working mic input roars with 50 Hz hum at this
gain; silence means the jack or cable does not reach the converter).

**Generalisable.** An RMS level is an absolute number with no reference; only a
*ratio between bands* or a *difference between two phases* tells you whether the
signal is a voice or the amplifier's own noise. When a speech pipeline fails,
measure the band the consumer uses (300–3000 Hz here) before touching thresholds.

