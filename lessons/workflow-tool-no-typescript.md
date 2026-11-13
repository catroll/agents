# The `workflow` tool does not run on this machine

**Signal.** Every call fails immediately, before the script does anything:

```
workflow run failed: workflow execution failed (exception):
Node.js is not compiled with TypeScript support
```

A one-line body (`return { ok: true };`) fails the same way, so it is the runtime,
not the script. Do not debug the script — there is nothing in it to fix.

**Cause.** The harness evaluates the workflow script as TypeScript, which needs
Node's type stripping. This machine runs Node `v22.22.1`, where stripping is
opt-in and off:

```bash
node --version                              # v22.22.1
node -e "console.log(process.features.typescript)"   # false
```

Type stripping is enabled by default only from Node 23.6, or by passing
`--experimental-strip-types` (22.6+). Nothing a caller passes to the tool changes
this.

**Workaround.** Use the `subagent` tool instead of `workflow`, and run the fan-out
yourself. The concurrency cap is **8 active children**; a ninth call returns
`Error: subagent limit reached (active child limit: 8)`. Launch in waves of eight,
and launch the next as each child finishes — the completion notice is the signal.
A long fan-out (20 modules, say) is three or four waves.

**What is lost.** `workflow` gives per-item pipelines with a barrier and a
schema-validated result; `subagent` gives only a text result. When the phases
depend on each other, either write the intermediate state to files the children
read, or accept a second wave.

**Lesson for the next tool that fails on its first call.** A failure on a
one-line input is an environment failure. Report it, find the check
(`process.features.typescript` here), and record the exact string — do not spend
turns re-authoring the payload.

