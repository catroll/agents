# Duplicate content is not the same as disposable

## Trigger

Cleaning a docs tree I moved two folders into `archive/` because their files
largely duplicated a shared training tree — same `book.pdf`, same course
READMEs, near-identical file lists. The owner corrected it: these were the
notes of two people he had mentored, and they belonged with the company
material, not in an archive.

## Why it happens

Hash and `diff -r` answer "is this the same bytes", not "whose work is this and
why is it here". A shared training tree and an individual's copy of it serve
different purposes: one is the curriculum, the other is what a person actually
did with it. Duplication is a reason to reconsider storage, never a reason to
reclassify provenance.

## Check before moving something to archive

1. Who produced it, and when? `git log --diff-filter=A -- <path>` and the
   original parent directory usually answer this. If it once sat inside a
   person's or project's tree, it belongs with that tree.
2. Is the "duplicate" the same artifact or the same source material? Two
   copies of one PDF are duplicates; two people's coursework over the same
   PDF is not.
3. Archive means "no longer an entry point", not "not worth keeping". If the
   only argument is overlap, keep it where its siblings live and say so in the
   README.
4. Ask the owner when provenance is unclear. Deleting or reclassifying someone
   else's work is their call.

## Recovery

`git mv` back to the sibling location, restore the README wording, and leave a
pointer where it was removed ("moved to X"). Check inbound links before and
after — a move that keeps relative links intact still breaks absolute ones.

## The missed signal

Both folders had originally lived inside the onboarding tree, and their git
history showed separate repositories on the old internal Git. Provenance was
visible; the duplicate files were just louder.
