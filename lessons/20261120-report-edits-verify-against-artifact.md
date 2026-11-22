# A failure report proposed DSL edits that were already in place

A pasted "failure fix report" said three Engagelab cases (`15910`, `15911`,
`15912`) asserted `status: 200` and should be changed to `400`, and that `8306`
needed its status re-checked. Reading the artifacts instead of the report:

    grep -n "status:" generated/Engagelab/update-webhook_Exception_NotFound_AfterDelete.yaml
    #   status: 400  (and the 30715 assertion is already there)
    git log --diff-filter=D --name-only -- '*update-webhook_Exception_Url_*Matrix*'
    # dslcheck cases 15911/15912 were deleted in 61de25daa; the report described files that no longer exist
    grep -n "Maximum 256" apis/Engagelab/docs/deliverlies.md
    # docs say 256, so the report's 256 limit was right even though its status claims were not

Two of the report's claims were false, one was right. Acting on it unread would
have "fixed" a correct `400` assertion, and the code citations
(`WebhookEntityController…` line numbers, `MAX_TITLE_LENGTH`) cannot be checked
from this repo at all.

## The check

For every proposed edit in a report or vendor reply, open the artifact and
confirm the claim before changing it:

- `grep -n "status:" <case>.yaml` for status claims.
- `git log --diff-filter=D --name-only -- '<path>'` when the report references a
  file that `ls` does not show.
- Treat file/line citations to code outside the repo as **hypotheses**; record
  them as "reported, not verified" rather than facts.
- Keep the product team's explicit statement separate from a generated report
  that quotes it — only the former is confirmation.

## Scope

Any generated failure report, triage plan, or vendor "please adjust your test"
message. The report is a claim set; the YAML/spec/code is the evidence.
