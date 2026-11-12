#!/usr/bin/env python3
"""
Rebuild a raster reference as an SVG made only of circular arcs and straight
lines, then score how close it is.

    python3 raster2arcs.py ref.png -o mark.svg [--tol 1.6] [--size 600]

Pipeline: binarise -> label the black components -> trace every boundary
(outer and holes) at sub-pixel accuracy -> fit each boundary with a greedy
line-vs-circle split -> collapse runs that share a primitive -> place every
junction at the exact intersection of its two primitives -> emit one evenodd
path per component -> report IoU against the reference bitmap.

Output is measured, not asserted: the IoU printed at the end is the number to
report, and it is computed from the same primitives that were written out.
"""

import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.optimize import least_squares

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RMAX = 700.0        # a "circle" flatter than this is just a line
SS = 4              # supersampling for the self-check raster


# ------------------------------------------------------------------ tracing
def binarise(img, level=128, smooth=1.2):
    g = np.asarray(img.convert('L')).astype(float)
    return g, (ndimage.gaussian_filter(g, smooth) if smooth else g)


def contours_of(mask, sigma=1.0, level=0.5):
    """Ordered sub-pixel boundaries of a boolean mask (outer and holes)."""
    f = ndimage.gaussian_filter(mask.astype(float), sigma)
    cs = plt.contour(f, levels=[level])
    segs = [np.asarray(s, float) for s in cs.allsegs[0]]
    plt.close('all')
    return [s for s in segs if len(s) > 8]


# --------------------------------------------------------------- fitting
def fit_line(p):
    c = p.mean(axis=0)
    _, _, vt = np.linalg.svd(p - c, full_matrices=False)
    n = np.array([-vt[0][1], vt[0][0]])
    e = (p - c) @ n
    return dict(kind='L', err=float(np.abs(e).max()), iworst=int(np.argmax(np.abs(e))))


def fit_circle(p):
    x, y = p[:, 0], p[:, 1]
    cx, cy = float(x.mean()), float(y.mean())
    r = float(np.hypot(x - cx, y - cy).mean())

    def res(v):
        return np.hypot(x - v[0], y - v[1]) - v[2]

    try:
        v = least_squares(res, [cx, cy, r], method='lm').x
    except Exception:
        v = np.array([cx, cy, r])
    if not np.all(np.isfinite(v)):
        return dict(kind='L', err=float('inf'), iworst=0)
    e = np.abs(res(v))
    return dict(kind='A', c=(float(v[0]), float(v[1])), r=float(abs(v[2])),
                err=float(e.max()), iworst=int(np.argmax(e)))


def best_fit(p, line_bias=1.0):
    """line_bias > 1 prefers lines: a circle must beat the line by that factor."""
    if len(p) < 5:
        return fit_line(p)
    ln, ci = fit_line(p), fit_circle(p)
    if ci['r'] > RMAX or not np.isfinite(ci['err']):
        return ln
    return ci if ci['err'] * line_bias < ln['err'] else ln


def smooth(p, k=5):
    if k < 3 or len(p) <= k:
        return p
    ext = np.vstack([p[-k:], p, p[:k]])
    ker = np.ones(k) / k
    return np.c_[np.convolve(ext[:, 0], ker, 'same')[k:-k],
                 np.convolve(ext[:, 1], ker, 'same')[k:-k]]


def split(p, tol, minlen=8, depth=0, line_bias=1.0):
    if len(p) < 2:
        return []
    f = best_fit(p, line_bias)
    if f['err'] <= tol or len(p) <= minlen or depth > 30:
        f['pts'] = p
        return [f]
    # children must be strictly shorter, or the recursion never terminates and
    # ends up accepting a slice with an enormous error
    lo, hi = max(2, len(p) // 8), len(p) - max(2, len(p) // 8)
    w = min(max(f['iworst'], lo), hi)
    return (split(p[:w + 1], tol, minlen, depth + 1, line_bias)
            + split(p[w:], tol, minlen, depth + 1, line_bias))


def merge_runs(segs, tol, line_bias=1.0, max_rounds=200):
    """Greedily fuse neighbouring slices while one merged primitive still fits
    within tol.  This is what actually removes primitives: the recursive split
    alone has no way to take a join back."""
    segs = list(segs)
    for _ in range(max_rounds):
        if len(segs) <= 4:
            break
        done = False
        for rot in (1, 0):                    # 1 first, to expose the wrap pair
            s = (segs[rot:] + segs[:rot]) if rot else segs
            for i in range(len(s) - 1):
                pts = np.vstack([s[i]['pts'], s[i + 1]['pts'][1:]])
                f = best_fit(pts, line_bias)
                if f['err'] <= tol:
                    f['pts'] = pts
                    merged = s[:i] + [f] + s[i + 2:]
                    segs = (merged[-rot:] + merged[:-rot]) if rot else merged
                    done = True
                    break
            if done:
                break
        if not done:
            break
    return segs


def snap_circles(segs, pos_tol=3.0, r_tol=3.0):
    """Fuse arcs that are the same circle fitted twice.  A ring interrupted by
    a shape welded to it comes back as two arcs of radius 221.6 and 223.7; the
    sliver between them is thinner than a pixel in places, and the browser and
    your own rasteriser then legitimately disagree about what it covers."""
    groups = []
    for i, s in enumerate(segs):
        if s['kind'] != 'A':
            continue
        _, turn = arc_turn(s)
        for g in groups:
            if (math.hypot(s['c'][0] - g['c'][0], s['c'][1] - g['c'][1]) <= pos_tol
                    and abs(s['r'] - g['r']) <= r_tol):
                g['mem'].append(i)
                break
        else:
            groups.append(dict(c=s['c'], r=s['r'], mem=[i]))
    out = list(segs)
    for g in groups:
        if len(g['mem']) < 2:
            continue
        pts = np.vstack([segs[i]['pts'] for i in g['mem']])
        f = fit_circle(pts)
        if f['kind'] != 'A' or f['r'] > RMAX:
            continue
        for i in g['mem']:
            out[i] = dict(out[i], c=f['c'], r=f['r'])
    return out


def flatten_tiny_arcs(segs, tol, min_arc=14.0):
    """An arc shorter than min_arc is a rounded corner, not a construction
    circle: replace it with a chord whenever the chord still fits."""
    out = []
    for s in segs:
        if s['kind'] == 'A':
            _, turn = arc_turn(s)
            if abs(turn) * s['r'] < min_arc:
                f = fit_line(s['pts'])
                if f['err'] <= tol:
                    f['pts'] = s['pts']
                    out.append(f)
                    continue
        out.append(s)
    return out


def fit_contour(pts, tol, line_bias=1.0, sm=5, merge=True, min_arc=14.0,
                circle_tol=2.0, snap=3.0):
    # A closed contour that really is a circle - a logo's enclosing ring, an
    # eye - must come out as ONE circle.  Fitting it piecewise leaves visible
    # dents where the arcs meet, so check the whole contour first.
    if circle_tol:
        f = fit_circle(pts)
        if f['kind'] == 'A' and f['r'] < RMAX and f['err'] <= circle_tol:
            f['pts'] = pts
            return [f]
    p = smooth(pts, sm)
    c = p.mean(axis=0)
    i0 = int(np.argmax(np.hypot(*(p - c).T)))
    p = np.roll(p, -i0, axis=0)
    segs = split(np.vstack([p, p[0]]), tol, line_bias=line_bias)
    if not merge:
        return segs
    for _ in range(3):
        segs = flatten_tiny_arcs(segs, tol, min_arc)
        segs = merge_runs(segs, tol, line_bias)
    segs = flatten_tiny_arcs(segs, tol, min_arc)
    return snap_circles(segs, snap, snap) if snap else segs


def arc_turn(seg):
    """Start angle and signed turn measured from the slice's own points, so the
    sweep can never wrap the long way round a huge, nearly straight circle."""
    cx, cy = seg['c']
    p = seg['pts']
    ang = np.arctan2(p[:, 1] - cy, p[:, 0] - cx)
    d = np.diff(ang)
    d = (d + np.pi) % (2 * np.pi) - np.pi
    return float(ang[0]), float(d.sum())


# --------------------------------------------------------------- geometry
def primitive(seg):
    if seg['kind'] == 'L':
        p = seg['pts']
        d = p[-1] - p[0]
        if np.hypot(*d) < 1e-9:
            d = np.array([1.0, 0.0])
        return dict(t='L', p=tuple(p[0]), d=tuple(d))
    return dict(t='C', c=tuple(seg['c']), r=float(seg['r']))


def inter(a, b, near):
    def cc(c1, r1, c2, r2):
        d = math.hypot(c2[0] - c1[0], c2[1] - c1[1])
        if d > r1 + r2 or d < abs(r1 - r2) or d < 1e-9:
            return None
        x = (d * d + r1 * r1 - r2 * r2) / (2 * d)
        h2 = r1 * r1 - x * x
        if h2 < 0:
            return None
        h = math.sqrt(h2)
        ux, uy = (c2[0] - c1[0]) / d, (c2[1] - c1[1]) / d
        bx, by = c1[0] + x * ux, c1[1] + x * uy
        return [(bx - h * uy, by + h * ux), (bx + h * uy, by - h * ux)]

    def cl(c, r, ln):
        (x1, y1), d = ln
        L = math.hypot(*d)
        if L < 1e-12:
            return None
        dx, dy = d[0] / L, d[1] / L
        fx, fy = x1 - c[0], y1 - c[1]
        b = fx * dx + fy * dy
        disc = b * b - (fx * fx + fy * fy - r * r)
        if disc < 0:
            return None
        s = math.sqrt(disc)
        return [(x1 + dx * (-b + s), y1 + dy * (-b + s)),
                (x1 + dx * (-b - s), y1 + dy * (-b - s))]

    if a['t'] == 'C' and b['t'] == 'C':
        pts = cc(a['c'], a['r'], b['c'], b['r'])
    elif a['t'] == 'C':
        pts = cl(a['c'], a['r'], (b['p'], b['d']))
    elif b['t'] == 'C':
        pts = cl(b['c'], b['r'], (a['p'], a['d']))
    else:
        (x1, y1), (dx1, dy1) = a['p'], a['d']
        (x2, y2), (dx2, dy2) = b['p'], b['d']
        den = dx1 * dy2 - dy1 * dx2
        if abs(den) < 1e-12:
            pts = None
        else:
            t = ((x2 - x1) * dy2 - (y2 - y1) * dx2) / den
            pts = [(x1 + t * dx1, y1 + t * dy1)]
    if not pts:
        return None
    j = min(pts, key=lambda q: math.hypot(q[0] - near[0], q[1] - near[1]))
    return j if math.hypot(j[0] - near[0], j[1] - near[1]) <= 8.0 else None


def same_prim(a, b, tol=1e-6):
    if a['t'] != b['t']:
        return False
    if a['t'] == 'L':
        return (math.hypot(a['p'][0] - b['p'][0], a['p'][1] - b['p'][1]) < 1e-6
                and abs(a['d'][0] * b['d'][1] - a['d'][1] * b['d'][0]) < 1e-9)
    return (abs(a['r'] - b['r']) < tol
            and math.hypot(a['c'][0] - b['c'][0], a['c'][1] - b['c'][1]) < tol)


def rebuild(segs, prims):
    """Collapse runs sharing a primitive, then place every junction exactly
    where its two primitives cross instead of at the traced point."""
    runs = []
    for i, pr in enumerate(prims):
        if runs and same_prim(pr, runs[-1]['prim']):
            runs[-1]['idx'].append(i)
        else:
            runs.append(dict(prim=pr, idx=[i]))
    if len(runs) > 1 and same_prim(runs[0]['prim'], runs[-1]['prim']):
        runs[0]['idx'] = runs[-1]['idx'] + runs[0]['idx']
        runs.pop()
    m = len(runs)
    if m == 1:
        return [dict(prim=runs[0]['prim'], a=None, b=None, n=len(runs[0]['idx']))]
    joins = []
    for k in range(m):
        near = segs[runs[k]['idx'][0]]['pts'][0]
        j = inter(runs[k - 1]['prim'], runs[k]['prim'], near)
        joins.append(j if j else (float(near[0]), float(near[1])))
    out = []
    for k in range(m):
        # remember a point from the middle of the run: the emitted arc must go
        # the same way round as the traced points, and an arc can legitimately
        # span more than 180 degrees, so "always take the short way" is wrong
        mid = segs[runs[k]['idx'][len(runs[k]['idx']) // 2]]['pts']
        out.append(dict(prim=runs[k]['prim'], a=joins[k], b=joins[(k + 1) % m],
                        mid=tuple(mid[len(mid) // 2]), n=len(runs[k]['idx'])))
    return out


def fmt(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def turn_through(o):
    """Signed turn from a to b that passes the run's own midpoint."""
    c = o['prim']['c']
    a0 = math.atan2(o['a'][1] - c[1], o['a'][0] - c[0])
    a1 = math.atan2(o['b'][1] - c[1], o['b'][0] - c[0])
    am = math.atan2(o['mid'][1] - c[1], o['mid'][0] - c[0])
    pos = (a1 - a0) % (2 * math.pi)
    dm = (am - a0) % (2 * math.pi)
    return pos if dm <= pos else pos - 2 * math.pi


def path_of(seq):
    if seq[0]['a'] is None:
        c, r = seq[0]['prim']['c'], seq[0]['prim']['r']
        return ('M%s,%s A%s,%s 0 1 1 %s,%s A%s,%s 0 1 1 %s,%s Z'
                % (fmt(c[0] - r), fmt(c[1]), fmt(r), fmt(r), fmt(c[0] + r), fmt(c[1]),
                   fmt(r), fmt(r), fmt(c[0] - r), fmt(c[1])))
    out = ['M%s,%s' % (fmt(seq[0]['a'][0]), fmt(seq[0]['a'][1]))]
    for o in seq:
        p, a, b = o['prim'], o['a'], o['b']
        if p['t'] == 'C':
            r = p['r']
            turn = turn_through(o)
            out.append('A%s,%s 0 %d %d %s,%s'
                       % (fmt(r), fmt(r), 1 if abs(turn) > math.pi else 0,
                          1 if turn > 0 else 0, fmt(b[0]), fmt(b[1])))
        else:
            out.append('L%s,%s' % (fmt(b[0]), fmt(b[1])))
    out.append('Z')
    return ''.join(out)


def sample(seq, step=0.5):
    if seq[0]['a'] is None:
        c, r = seq[0]['prim']['c'], seq[0]['prim']['r']
        k = max(8, int(2 * math.pi * r / step))
        return np.array([[c[0] + r * math.cos(2 * math.pi * i / k),
                          c[1] + r * math.sin(2 * math.pi * i / k)] for i in range(k)])
    pts = []
    for o in seq:
        p, a, b = o['prim'], o['a'], o['b']
        if p['t'] == 'C':
            c, r = p['c'], p['r']
            a0 = math.atan2(a[1] - c[1], a[0] - c[0])
            turn = turn_through(o)
            k = max(2, int(abs(turn) * r / step))
            for i in range(k):
                t = a0 + turn * i / k
                pts.append([c[0] + r * math.cos(t), c[1] + r * math.sin(t)])
        else:
            k = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
            for i in range(k):
                pts.append([a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k])
    return np.array(pts)


# -------------------------------------------------------------------- main
def evenodd(seqs, size, ss):
    """Even-odd scanline fill of a list of run-sequences, supersampled."""
    polys = [sample(s, 0.4) * ss for s in seqs]
    x0, y0, x1, y1 = [], [], [], []
    for p in polys:
        q = np.vstack([p, p[:1]])
        x0.append(q[:-1, 0]); y0.append(q[:-1, 1])
        x1.append(q[1:, 0]); y1.append(q[1:, 1])
    x0 = np.concatenate(x0); y0 = np.concatenate(y0)
    x1 = np.concatenate(x1); y1 = np.concatenate(y1)
    n = int(size * ss)
    img = np.zeros((n, n), bool)
    for row in range(n):
        yc = row + 0.5
        m = (y0 <= yc) != (y1 <= yc)
        if not m.any():
            continue
        t = (yc - y0[m]) / (y1[m] - y0[m])
        xc = np.sort(x0[m] + t * (x1[m] - x0[m]))
        for i in range(0, len(xc) - 1, 2):
            a = int(np.ceil(xc[i] - 0.5))
            b = int(np.floor(xc[i + 1] - 0.5))
            if b >= a:
                img[row, max(a, 0):min(b + 1, n)] = True
    return img


def signed_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def run(src, out, tol=1.6, size=600, min_area=50, line_bias=1.0, sigma=1.0,
        merge=True, min_arc=14.0, circle_tol=2.0, snap=3.0, quiet=False):
    img = Image.open(src)
    if max(img.size) != size:
        img = img.convert('L').resize((size, size), Image.LANCZOS)
    _, gs = binarise(img)
    black = gs < 128
    lab, n = ndimage.label(black, structure=np.ones((3, 3)))

    comps = [lab == k for k in range(1, n + 1) if (lab == k).sum() >= min_area]
    comps.sort(key=lambda m: -m.sum())          # big first, so nested survive

    paths, rings = [], []
    n_c = n_l = 0
    worst = 0.0
    for m in comps:
        # trace the mask itself - not fill_holes(m), which would swallow the
        # ring's hole and leave only the outer circle.  matplotlib gives the
        # outer boundary and every hole as separate curves with opposite
        # orientation, which is exactly what fill-rule=evenodd wants.
        cs = contours_of(m, sigma)
        if not cs:
            continue
        areas = [signed_area(c) for c in cs]
        big = int(np.argmax([abs(a) for a in areas]))
        sgn = 1.0 if areas[big] > 0 else -1.0
        outer = cs[big]
        holes = [c for i, c in enumerate(cs) if i != big and areas[i] * sgn < 0]
        if not holes:                       # no hole: keep every curve as solid
            outer, holes = None, cs
        comp = []
        for c in (holes if outer is None else [outer] + holes):
            segs = fit_contour(c, tol, line_bias, merge=merge,
                               min_arc=min_arc, circle_tol=circle_tol, snap=snap)
            seq = rebuild(segs, [primitive(s) for s in segs])
            paths.append(path_of(seq))
            comp.append((seq, outer is None or c is outer))
            n_c += sum(1 for o in seq if o['prim']['t'] == 'C')
            n_l += sum(1 for o in seq if o['prim']['t'] == 'L')
            worst = max(worst, max(s['err'] for s in segs))
        rings.append(comp)

    d = ' '.join(paths)
    open(out, 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
        'height="%d"><path fill="#000" fill-rule="evenodd" d="%s"/></svg>\n'
        % (size, size, size, size, d))

    # Self-check: rasterise exactly the primitives that were written out, with
    # the even-odd rule the path declares.  Painting the contours in order
    # instead disagrees with the browser wherever two fitted primitives nearly
    # coincide, and that disagreement is invisible until it bites.
    mine = evenodd([seq for comp in rings for seq, _ in comp], size, SS) \
        .reshape(size, SS, size, SS).mean(axis=(1, 3)) > 0.5
    iou = (mine & black).sum() / (mine | black).sum()
    if not quiet:
        print('%d components -> %d circles + %d lines = %d primitives'
              % (len(comps), n_c, n_l, n_c + n_l))
        print('worst primitive deviation from the trace: %.2f px' % worst)
        print('IoU vs reference: %.4f  (%d differing px of %d)'
              % (iou, int((mine ^ black).sum()), int(black.sum())))
    return dict(iou=iou, circles=n_c, lines=n_l, worst=worst)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('-o', '--out', default='mark.svg')
    ap.add_argument('--tol', type=float, default=1.6,
                    help='max px a primitive may deviate from the trace')
    ap.add_argument('--size', type=int, default=600)
    ap.add_argument('--min-area', type=int, default=50,
                    help='ignore black specks smaller than this')
    ap.add_argument('--line-bias', type=float, default=1.0,
                    help='>1 prefers straight lines over arcs')
    ap.add_argument('--sigma', type=float, default=1.0,
                    help='blur before contouring; higher = smoother trace')
    ap.add_argument('--circle-tol', type=float, default=2.0,
                    help='max px a whole closed contour may miss a circle by '
                         'and still be drawn as one circle')
    ap.add_argument('--snap', type=float, default=3.0,
                    help='fuse arcs whose circles agree to within this many px')
    ap.add_argument('--min-arc', type=float, default=14.0,
                    help='arcs shorter than this become straight chords')
    ap.add_argument('--no-merge', action='store_true',
                    help='keep every split; merge removes primitives, not accuracy')
    a = ap.parse_args()
    run(a.src, a.out, a.tol, a.size, a.min_area, a.line_bias, a.sigma,
        not a.no_merge, a.min_arc, a.circle_tol, a.snap)
