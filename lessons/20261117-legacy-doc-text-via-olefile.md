# Legacy .doc text extraction: no libreoffice/antiword, use olefile

## Signal

`libreoffice --headless --convert-to txt file.doc` exits 1 with no output,
`command -v libreoffice soffice antiword catdoc wvText` prints nothing, and
`strings -el file.doc` shows only metadata (author, fonts, phone) — no body text.

`file` still says `Composite Document File V2 Document` (or, for some files,
`HTML document`, in which case just strip tags).

## Meaning

No office converter is installed on this machine. The body text is inside the
OLE `WordDocument` stream as UTF-16LE, not in printable strings.

## Check

```bash
command -v libreoffice soffice antiword catdoc wvText   # empty = no converter
file <doc>                                              # confirm OLE2 vs HTML
```

## Do instead

```python
import olefile, struct, re
ole = olefile.OleFileIO(path)
d = ole.openstream('WordDocument').read()
fc_min, fc_mac = struct.unpack_from('<II', d, 0x18)
for enc in ('utf-16le', 'gb18030'):
    t = d[fc_min:fc_mac].decode(enc, errors='ignore')
    for c in re.findall(r'[^\x00-\x1f]{2,}', t):
        if re.search(r'[\u4e00-\u9fff]', c):
            print(c)
```

- UTF-16LE is the usual Chinese Word encoding; retry `gb18030` when the UTF-16
  pass yields CJK-looking mojibake.
- `茶`-style mojibake from `strings -el` is not the text; ignore it.
- `.wps` files from WPS Office are OLE2 too and follow the same path.

## Negative result

`pip install textract` / `python-docx` do not read legacy `.doc`; `python-docx`
opens only OOXML `.docx` and raises `PackageNotFoundError` on OLE2.
