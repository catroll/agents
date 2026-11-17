# `Glyph 20854 (CJK) missing from font(s) DejaVu Sans` — matplotlib renders Chinese as boxes

## Signal

A matplotlib script that draws Chinese labels exits 0 and writes a normal
looking PNG, but stderr carries one warning per character:

```
UserWarning: Glyph 20854 (\N{CJK UNIFIED IDEOGRAPH-5176}) missing from font(s) DejaVu Sans.
```

`fc-list :lang=zh` shows Source Han Sans / WenQuanYi, so the system font is
installed. The image is the only place the failure shows up, and only if you
look at it.

## Why

matplotlib's `font_manager` does not index `~/.local/share/fonts` in this
environment. Here the Chinese face is
`~/.local/share/fonts/SourceHanSansCN-Regular.otf`; `fc-match` finds it but
`{f.name for f in font_manager.fontManager.ttflist}` does not contain
`Source Han Sans CN`. A helper that picks a family by name therefore falls
through to `sans-serif` → DejaVu Sans, which has no CJK glyphs. matplotlib does
not treat this as an error.

## Check

```sh
fc-match -f '%{file}\n' 'Source Han Sans CN'      # the file fc sees
python3 - <<'EOF'
from matplotlib import font_manager as fm
print([f.name for f in fm.fontManager.ttflist if 'Han' in f.name or 'CJK' in f.name])
EOF
```

If the name is absent, register the file before looking it up:

```python
from matplotlib import font_manager
font_manager.fontManager.addfont(
    os.path.expanduser("~/.local/share/fonts/SourceHanSansCN-Regular.otf"))
# then pick from the updated ttflist, or set:
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Source Han Sans CN", "Noto Sans CJK JP", "DejaVu Sans"]
```

Run the generator with warnings promoted to errors so tofu can never ship:

```sh
python3 -W error::UserWarning make.py
```

That turns every `Glyph … missing` warning into a non-zero exit.

## Negative results

- Installing a font package is not the fix; the font was already installed and
  `fc-list` saw it. The missing step is `addfont`.
- `Noto Sans CJK JP` *is* indexed by matplotlib here (the TTC's first face) and
  has the Han glyphs, so it is a usable fallback — but it picks Japanese glyph
  variants, so only use it when the CN face is genuinely unavailable.

## Related check: don't flag clipped tick labels

When adding a "label ran outside the canvas" check, iterate only over
`fig.texts`, `ax.texts`, titles and legends. `AutoLocator` emits a tick label
past the axis limit (e.g. `35000` for an xlim that ends at 30,800) that
matplotlib clips at draw time; including all `Text` objects reports it as
clipped and aborts a correct chart.
