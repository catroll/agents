# A count or date range written into a document came from eyeballing a list

A plan described `OE/` as "2017–2018 旧公司" and `WPS/` as "2014 年 Windows
文档" because two sampled filenames looked that old, and wrote "7 个外部脚本"
after reading a `grep` output by eye. Measured afterwards:

    find OE -type f -printf '%TY-%Tm\n' | sort -u | sed -n '1p;$p'
    # 2012-09 .. 2023-10
    find WPS -type f -printf '%TY-%Tm\n' | sort -u | sed -n '1p;$p'
    # 2016-03 .. 2022-07
    grep -rn 'Documents/Mine' --include='*.py' . | wc -l
    # 10 lines, not 7

Two errors in one document that a reader would have taken as fact.

## The check

Before a number, count, date range, or era label enters a document, run the
command that produces it and paste its output. Do not derive it from the list
you were skimming.

- Count references: `grep -rn '<needle>' --include='*.py' <root> | wc -l`.
- Date range of a directory: `find <dir> -type f -printf '%TY-%Tm\n' | sort -u`.
- File/line count: `wc -l`, `find … | wc -l`.

## Negative result

`find -printf '%TY'` is **mtime = copy/move time**, not the date the content was
written. A directory named `2014` can hold 2022 edits (that is exactly what
`WPS/` did). So either say "mtime 跨度 2016–2022" in the document, or omit the
era entirely — never present mtime as the content's era.

## Scope

Applies to any prose that states facts about a tree: plans, audits, READMEs,
migration notes. The document is what the next session trusts; an unmeasured
number in it costs more than the command would have.