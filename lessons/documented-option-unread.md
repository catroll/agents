# A documented library option can be dead code — grep for its read site

**Signal.** Setting a documented option has no effect, and the library has no
error to show for it. Example: EasyMDE 2.21.0's `iconClassMap` is accepted and
stored (`options.iconClassMap = extend({}, iconClassMap, options.iconClassMap || {})`,
`src/js/easymde.js:1873`) but never read again — built-in toolbar buttons got
their classes from the module-level `iconClassMap` at load time, so the option
cannot change them. The README lists it; the typings do not; the behaviour is
absent.

**Check.** Search the source for *reads*, not the assignment:

```sh
grep -n "iconClassMap" node_modules/<pkg>/src/js/*.js   # one assignment, zero reads
```

If the only hit is where it is set, the option is a no-op for that code path.
Then choose the narrow workaround (`post-init DOM class swap`, custom toolbar with
the documented `icon` markup, etc.) and write the evidence next to it, so the
next reader does not re-trust the option.

