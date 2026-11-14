# A `#` inside a continued Makefile recipe drops the rest of the recipe

**Signal.** `/bin/sh: 10: Syntax error: end of file unexpected (expecting "fi")`
right after a comment is added in the middle of a `deps` recipe. `make -n`
still prints the later lines, so a dry run does not show the cut.

**Why it matters.** GNU make treats `#` as a comment through the end of the
logical line. The recipe is one continued line (`\`). Everything after the `#`
never reaches the shell, including the matching `fi`.

**Check.** Put explanations in a make comment above the target. Inside a
recipe, do not use `#`. Confirm with `dash -n` on `make -n` output, then run
the target; the syntax error appears only when the recipe runs.
