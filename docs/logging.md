# Logging (event types)

Status: starting point for KSI-MLA-LET (maintaining a list of information
resources and event types that are logged, monitored, and audited).

## Currently logged

- **HTTP requests** — method, path, status code, remote address. Emitted by
  the `after_request` hook in `app/app.py`, logger name `audit`.

## Not yet logged (known gaps)

- **Authentication events** — the app has no auth system yet, so there's
  nothing to log here. Add this when accounts/auth are implemented (see the
  IAM entries in `compliance-20x/ksi-tracker.yaml`).
- **Configuration/infrastructure changes** — no real infra exists yet (see
  `docs/change-management.md`). Once it does, infra-level changes need their
  own audit trail (KSI-CMT-LMC).
- **OPA policy decisions** — OPA supports decision logging natively, but
  this repo runs `opa test` at CI time only, not a live OPA server making
  runtime decisions. Wire this up if/when the app actually queries OPA at
  runtime (per the target application's existing OPA deployment).

## Storage and access (known gaps)

Logs currently go to stdout only:

- No centralized, tamper-resistant storage — that's KSI-MLA-OSM (a SIEM or
  equivalent), not yet in place.
- No access control on who can read log data — that's KSI-MLA-ALA, not
  applicable until there's a real log storage system to control access to.
