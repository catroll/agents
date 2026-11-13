# A webhook/IMAP timeout blames the platform only after you resolve the id there

**Signal.** A whole cohort of webhook-waiting cases times out with
`seen events=[]`, and the event store holds no record for the exact emailId the
case is waiting on.

**Check the platform's own API with that exact id before talking about delay or
load.** For ASC: `GET /api/data/emailStatus?emailIds=<id>$rcpt&days=3`
(the `$rcpt` suffix and the day window are both mandatory).
If the platform still answers `No corresponding record found` for an id it
handed back 19 hours earlier, while the same second/recipient has a record under
a *different* id ~29 ms away, that is a **platform-side id mismatch** — not push
delay, not load, not "the mail was never delivered".

**Trust the population, not the sample.** Diff the number of DSL cases that wait
on webhooks (`grep -rl webhook_check_request`) against the failure list: here
**all 204 executed sg cases failed** while the two hk/us region cases in the
same batch **passed**. "One scoped subset failed 100% while its sibling cases
were fine" beats any single log — it kills the flake/concurrency explanations in
one step and points at that one path.

**Trap.** A failed-only export **does not contain the passing sibling cases**, so
the control group is not in it. Sites usually expose
`GET /runs/<run_id>/logs/<case_name>/download` for any case, in any run —
that is how the healthy batch's send ids were obtained here. Do not stop at
"the export does not have it".

**Also.** "The id does not exist" and "the event arrived late" can both print
`seen events=[]`. And `delay > timeout` is not proof of push delay: the window
ends at *step start + timeout*, not at `event_time + timeout`. Separating these
requires going back to the platform for data.

