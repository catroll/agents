# Project todo system

One file per project, one item per unit of work. This is the cross-session owner
of planned work; the chat transcript and the per-turn session todo list are not.

    ~/.agents/todo/
      _README.md      this specification
      _TEMPLATE.md    skeleton to copy for a new project
      _INDEX.md       project index with open/P0 counts
      <project>.md    the project's todo items

## Project files

- Project name = the owning repository or tool directory in lowercase:
  `woody` (tools/woody coder service), `homepage`, `auth`, `newapi`, `wlb`.
  One file owns the work; an item that spans two projects lives in the one that
  has to change, and the other file links to it.
- Create a file from `_TEMPLATE.md` only when the work is more than a one-off;
  a one-off still goes into the matching project file as a P2/P3 if it will
  outlive the session.
- The header carries `Updated`, `Next ID` and `Prefix`. IDs are monotonic and
  never reused; a done item keeps its ID.

## Item schema

    - [ ] **W-012** [P1][B20261125-w2c2][due:2026-11-25] Short imperative title
      - Done when: the observable result that closes it
      - Ev: command, file or endpoint that proves it (optional for trivial items)

- **ID**: `<prefix>-<NNN>`, prefix defined once in the file header.
- **Importance**:
  - `P0` blocked, release-critical, or an external deadline that breaks work.
  - `P1` high: the main line of the project, or unlocks a P0.
  - `P2` normal: worthwhile, no deadline pressure.
  - `P3` optional: nice-to-have, do it when adjacent work is open.
- **Batch**: `B<YYYYMMDD>-<slug>` = the planned delivery iteration; items with
  no plan go to `B-backlog`. Every item has one. A batch header states its
  target date and status (`open`, `wip`, `done`).
- **Owner**: `[user]` only for things the agent cannot do (push, external
  approval). Anything without an owner is the agent's.
- **Dependency**: `[dep W-004]` when the item cannot start before another closes.

## Statuses

| Marker | Meaning | Rule |
|--------|---------|------|
| `[ ]` | open | default |
| `[x]` | done | append `-> done YYYY-MM-DD (evidence)` on the same line |
| `[!]` | blocked | append `why: ...`; re-check when the blocker closes |
| `[-]` | dropped/deferred | append `reason: ...`; keep the ID |

## Loading and updating protocol

1. **Read before planning.** When a request names a project, read its file
   first (or `grep -n '^- \[ \]' <file>` for the open list). Order of work:
   open P0s (earliest due), then P1s, then the earliest open batch. State which
   item ID is being executed.
2. **Update in the same turn** a task starts, finishes, blocks or changes scope:
   flip the marker, append evidence, allocate the next ID from `Next ID`, bump
   `Updated`, and fix `_INDEX.md` counts in the same edit.
3. **Do not duplicate homes.** A turn's mechanical steps still use the session
   todo list; durable items and decisions go to this file. If the chat has a
   plan that is not here yet, add it here before the reply.
4. **Archive, do not delete.** When every item of a batch is done and the batch
   is older than 30 days, move the section under `## Archive` at the bottom of
   the file. `_INDEX.md` counts only open items.

## Index

`_INDEX.md` has one row per project: path, open count, P0 count, next due,
last updated. It is the only cross-project view; keep counts exact (count
`- [ ]` lines in the file).
