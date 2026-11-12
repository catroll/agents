---
name: raster-to-arcs
description: >-
  Reconstruct a raster reference (logo, icon, illustration) as an SVG built only
  from circular arcs and straight lines, by measuring the bitmap instead of
  redrawing it by eye, and score the result with IoU. Use when the user supplies
  an image and asks to reproduce / 复刻 / 复现 it geometrically, to redraw it with
  compass and straightedge (尺规作图), to vectorise a logo into few primitives, or
  to turn a raster into a geometric or golden-ratio logo. Also use when an
  earlier "geometric redesign" drifted too far from the source image and the user
  rejected it.
---

# Raster to arcs

Turn a bitmap into a mark made only of circles and straight segments, and prove
how close it is.

**Measure, then fit. Do not redesign.** Inventing a grid (golden ratio, pentagon,
column layout) and drawing "in the spirit of" the reference is what gets rejected.
Fit the actual pixels, then report the IoU. If the user asks for golden ratio,
*treat it as a hypothesis to test*, not a brief to satisfy — see below.

## Quick start

```bash
python3 scripts/raster2arcs.py reference.png -o mark.svg --tol 1.6
```

Prints component count, primitive count, worst deviation and IoU; writes the SVG.

## Workflow

1. **Separate before you fit.** Label the black components. A mark is usually
   several islands, and the parts you assume are joined often are not (and vice
   versa). Note for each: outer boundary, and whether its white regions are
   *holes* (enclosed) or *channels* (open to the background). The distinction
   decides the path's fill rule.
2. **Trace sub-pixel.** Blur the grayscale slightly and take the `128` contour;
   you get ordered, sub-pixel, orientation-consistent curves for the outer
   boundary and every hole.
3. **Fit each boundary** with a greedy recursion: try a line, try a circle, keep
   the closer; if neither is within `tol`, split at the worst point and recurse.
4. **Merge.** After splitting, greedily fuse neighbouring slices while the merged
   primitive still fits within `tol`. This is where the simplification comes from —
   the recursion can only cut, never take a cut back. Then flatten arcs shorter
   than `--min-arc` into chords, and force any whole contour that is within
   `--circle-tol` of a circle to be exactly one circle.
5. **Recompute junctions** as the exact intersection of the two adjacent
   primitives, instead of keeping the traced point. Endpoints then snap together.
6. **Score.** Rasterise the primitives you are about to write and compare with
   the reference: `IoU = |A∩B| / |A∪B|`. Sweep `--tol` and read the knee.
7. **Verify the artefact you ship** in a real renderer, not just the internal
   model, and report the number.

## Simplifying

Raise `--tol` and rely on the merge pass. A typical knee, on a 600 px mark:

| tol | primitives | IoU |
|---|---|---|
| 1.2 | 32 | 0.951 |
| 1.6 | 27 | 0.943 |
| 2.2 | 24 | 0.933 |
| 4.0 | 22 | 0.931 |

Halving the primitive count usually costs 1–2 points of IoU, not more. Watch for
*dips* (`tol=2.0` measured 0.888 because the merge overshot) — always sweep, never
extrapolate.

## Golden ratio: test it, do not assume it

Fit first, then ask whether the fitted radii land on the `R/phi**k` ladder. On the
reference this was written for, exactly **1 of 37 circles** fell within 2% of a rung
and the median gap was 13% — the mark has no phi structure at all, and snapping to
the ladder cost IoU 0.930 -> 0.889. Report that. Only claim a ratio the measurement
supports.

## Report back

Quote the primitive count, the worst deviation in px, and the IoU. Say which
deviations remain and where. A number the user can re-run beats an adjective.

See [REFERENCE.md](REFERENCE.md) for the traps that cost hours.
