# raster-to-arcs — reference

## The traps, with the exact symptom each one shows

### 1. `fill-rule="nonzero"` holes only cancel one black shape

A hole overlapping **two** black subpaths leaves `+2 − 1 = +1`, so it stays
filled and the hole vanishes. Symptom: an eye or a white gap renders solid black
even though the path looks right.

- Fix A: keep every hole inside exactly one black subpath (constrains the design).
- Fix B: give each component its own path and use `evenodd`, or model the whole
  component as outer boundary + hole boundaries. Preferred.

With `evenodd`, a component whose hole is *merged* with another shape (a body
welded to a ring) is still correct: the hole curve is the boundary of the white
region, so a point inside the welded body crosses the outer curve once and the
hole curve zero times.

### 2. `binary_fill_holes` destroys the hole you wanted

Tracing `fill_holes(component)` returns only the outer circle — the ring's hole
is filled in, so the interior silently disappears. Symptom: a ring renders as a
solid disc. Trace the **component mask** and let `find_contours`/`contour` give
you the outer curve and each hole as separate curves.

Classify them by signed area: the largest `|area|` is the outer boundary; curves
of the opposite orientation are holes. If no curve has the opposite sign, the
component is solid.

### 3. An arc that spans more than 180° flips the wrong way

Computing the sweep as `(a1 - a0) % 2π`, then clamping to the short way round,
silently reverses any arc wider than a semicircle. Symptom: a big circle comes
out as a dented blob, or the frame grows a notch.

Fix: keep a point from the middle of the run and choose the turn that passes
through it:

```python
pos = (a1 - a0) % (2*math.pi)
dm  = (am - a0) % (2*math.pi)
turn = pos if dm <= pos else pos - 2*math.pi
```

Do this **after** the junction positions have moved to the primitive
intersections — the traced midpoint is the only witness of which way the arc ran.

### 4. The recursive split never terminates

If the worst-error index lands on an end point, one child is as long as its
parent and the recursion burns to the depth cap, accepting a slice with an
enormous error. Symptom: `worst deviation` in the tens of px while most
primitives look fine. Clamp the split index to `[len//8, len - len//8]`.

### 5. A near-straight slice fitted as a huge circle

Radius `10^4` circles wrap the long way round and spray points thousands of px
away. Cap the radius (`RMAX`, ~700 px): beyond that the slice is a line.

### 6. ImageMagick silently drops strokes

`magick` exits 0 but `<circle stroke=...>` and `<line stroke=...>` simply do not
render — only filled paths survive. `magick -list delegate | grep svg` advertises
`rsvg-convert`, which is not installed here, so it falls back to the bundled
`MSVG` renderer. Nested `<svg>` viewports are ignored too.

```bash
magick -list delegate | grep -i svg   # advertises rsvg-convert
command -v rsvg-convert               # ...which is MISSING
```

Use headless Firefox instead — one call, no WebDriver:

```bash
export MOZ_HEADLESS=1 XDG_RUNTIME_DIR=/run/user/1000
/snap/firefox/current/usr/lib/firefox/firefox --headless --no-remote \
  --profile "$PWD/.cache/ff/prof" --window-size=1200,1200 \
  --screenshot "$PWD/out.png" "file://$PWD/art.svg"
```

The screenshot is the size of `--window-size`; to rasterise at 2x, copy the SVG
with `width`/`height` rewritten rather than upscaling a 1x PNG. The snap needs
`XDG_RUNTIME_DIR` and a writable profile, both outside a workspace-write sandbox.

### 7. A ring fitted piecewise grows dents

The recursion happily cuts a circle into three arcs of radius 226.9 / 228.4 /
227.3 when the traced circle wobbles by ~1.5 px. The joins then show as visible
flat spots. Symptom: a frame that should be a perfect circle looks dented.

Fix: before fitting piecewise, fit the **whole** closed contour to one circle; if
the max deviation is within `--circle-tol` (2 px is a good default), emit one
circle. Costs a few thousandths of IoU and is worth it — the wobble is JPEG, not
design.

## Method notes

- **IoU is the objective.** It is stable and comparable across parameters. On a
  600 px mark, ~0.93 means every differing pixel is on an edge hairline; below
  ~0.90 a shape has visibly moved.
- **Sweep, do not extrapolate.** The count/IoU curve is not monotone: `tol=2.0`
  scored worse than `tol=2.5` because a merge overshot.
- **Vertex-only junctions drift.** Keeping traced endpoints leaks ~0.007 IoU;
  recomputing them as primitive intersections recovers it and removes the small
  kinks at joins.
- **Supersample the self-check** (4x, then box-downsample) or the comparison is
  dominated by rasteriser aliasing rather than by the fit.
- **Ignore the reference's own junk** — watermarks, JPEG speckles — either by
  masking them or with `--min-area`.

## Worked example: the woodpecker reference

4 black components (a ring welded to the body, the beak/head/neck, an isolated
crown, the eye); the white around the eye is a channel open to the background,
not a hole.

| tol | primitives | IoU |
|---|---|---|
| 1.2 | 32 (23 circles, 9 lines) | 0.9507 |
| 1.6 | 27 (22 circles, 5 lines) | 0.9430 |
| 2.2 | 24 (18 circles, 6 lines) | 0.9331 |
| 4.0 | 22 (18 circles, 4 lines) | 0.9306 |
| ladder snapped to `R/phi**k` | 31 groups | 0.8890 |

The first attempt at this mark was drawn from a golden-ratio grid by eye and had
to be thrown away; the measurement-driven version matched at IoU 0.93 with 53
primitives, and the merge pass took that to 27 while *improving* the score.
