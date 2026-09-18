# Change Management Procedure (Draft)

Status: **draft, not yet reviewed or in effect**. This exists as the starting
artifact for KSI-CMT-RVP (Reviewing Change Procedures) — a procedure has to
exist before its effectiveness can be reviewed. See
`compliance-20x/ksi-tracker.yaml` for current status.

## How changes are made

1. All changes land through a pull request against `master` — no direct
   pushes to `master` and no manual changes to a running deployment.
2. Required automated checks (`.github/workflows/ci.yml`) must pass before
   merge: `pytest` (app tests), `opa test` (policy tests), and
   `compliance-20x/tools/validate_dataset.py` (compliance dataset schema
   check).
3. The commit history and PR record on the git host serve as the log of
   what changed, when, and why (KSI-CMT-LMC).

## Known gaps (TBD)

- **Branch protection is not yet configured** — this repo has no remote yet,
  so "PRs required" above is a stated intent, not an enforced GitHub
  setting. Enforce this (required PR reviews + required status checks)
  once the repo has a remote.
- **No review cadence exists yet.** KSI-CMT-RVP requires this procedure's
  *effectiveness* to be persistently reviewed — that requires an actual
  recurring review (e.g. a quarterly look at change failure rate, rollback
  frequency, time-to-deploy) which hasn't been established. Don't mark
  KSI-CMT-RVP as implemented until a real cadence exists and has run at
  least once.
- **No deployment target exists yet.** This app isn't deployed anywhere, so
  KSI-CMT-RMV (redeploy vs. modify) has nothing to evidence yet — that needs
  an actual deployment mechanism (e.g. containerized, deployed only via the
  CI pipeline, no direct server access) before it can be claimed.
