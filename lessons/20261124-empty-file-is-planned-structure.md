# A zero-byte file can be a planned page, not litter

## Trigger

Cleaning a docs tree I deleted 59 empty `.md` files as "placeholders", plus
the root `SUMMARY.md` I judged vestigial. The owner answered: the SUMMARY was
the designed structure and those empty files were the planned chapter
skeleton — both were meaningful, neither should have gone.

## Why it happens

`find -empty` answers "does this file have bytes", not "is this file
intended". A page planned for later and an abandoned stub look identical to
the shell. The discriminator is the table of contents, and the TOC sat in the
same tree: deleting it first destroys the evidence you would have judged the
stubs by.

## Check before deleting an empty file

1. Does the directory or an ancestor have a `SUMMARY.md` / `index.md` /
   `README.md` that names the file? Listed-but-empty means planned structure.
2. Are the empty files systematic — one shared prefix or one per topic
   (`api-mail-*.md`, `email-*.md`, `sms-*.md`)? Systematic names indicate a
   skeleton, not noise.
3. Check history: `git log --diff-filter=A -- <path>`; added in a batch with
   the TOC and never touched since → planned.
4. Still unsure? Keep the file, mark it "planned" in the directory README,
   and let the owner decide. Deletion is the owner's call, not the cleaner's.

## Recovering a wrong deletion

`git checkout <commit> -- <path>` restores individual files. The TOC goes
back first so you can judge the stubs by it; then map moved paths and
recreate. Expect the restored TOC to show broken links to pages not written
yet — that is the plan, not a defect.

## The missed signal

32 empty `api-*.md` pages sat next to their `07.kb/README.md` outline, and the
root `SUMMARY.md` was the design of the whole tree. Both signals were on
screen in the same listing and were dismissed as clutter because the files
were zero bytes.
