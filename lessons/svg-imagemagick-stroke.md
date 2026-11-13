# Rendering SVG on this machine: use headless Firefox, not ImageMagick

**Signal.** ImageMagick accepts an SVG and exits 0, but the output is silently
wrong. Circles and lines that use `stroke` simply vanish; only filled paths
survive. `magick -list delegate | grep svg` advertises
`svg => 'rsvg-convert' ...`, but `rsvg-convert` is **not installed**, so IM
falls back to its own `MSVG` renderer, which does not implement stroke on
`<circle>`/`<line>`. Nested `<svg>` elements are ignored too — a contact sheet
built from nested viewports renders only the first panel.

**Consequence.** Any visual verification done through ImageMagick is worthless
for stroked artwork: a correct logo looks like it is missing its frame, and you
will "fix" a bug that does not exist. Check the renderer before trusting it:

```bash
magick -list delegate | grep -i svg     # advertises rsvg-convert
command -v rsvg-convert                 # ...which is MISSING
```

**What works.** Headless Firefox screenshots a real SVG (or a local HTML page)
exactly, including strokes, arcs, `fill-rule` and text. One call, no WebDriver,
no Selenium:

```bash
export MOZ_HEADLESS=1 XDG_RUNTIME_DIR=/run/user/1000
/snap/firefox/current/usr/lib/firefox/firefox --headless --no-remote \
  --profile "$PWD/.cache/ff/prof" \
  --window-size=1200,1200 --screenshot "$PWD/out.png" "file://$PWD/art.svg"
```

- `--screenshot` needs a *writable* profile directory and `XDG_RUNTIME_DIR`;
  both are outside a workspace-write sandbox, so this needs full access.
- The screenshot is the size of `--window-size`. To rasterise at 2x, copy the
  SVG with `width`/`height` rewritten to the target size (the `viewBox` keeps
  the geometry exact) rather than upscaling a 1x PNG.
- The snap needs `MOZ_HEADLESS=1` **and** `--headless`; without
  `XDG_RUNTIME_DIR` it reports a misleading read-only-filesystem error.

**Corollary for hand-written SVG.** Prefer a real renderer for verification, but
keep the deliverable idiomatic: emit the frame as a stroked `<circle>` and
verify it in the browser, rather than contorting the artwork into filled annuli
just to satisfy a broken rasteriser. Ship a fill-only build only as a separate
convenience asset.

