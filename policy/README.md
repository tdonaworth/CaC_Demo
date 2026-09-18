# Policy (OPA / Rego)

This directory holds Rego policies used to **enforce** compliance requirements
as machine-checkable rules, meant to run in CI (and eventually against the
target application's real OPA deployment). It's split into two tracks that
mirror the two tracks under the compliance-reporting side of the repo:

- `fedramp_rev5/` — rules tagged to NIST 800-53 / FedRAMP Rev5 control IDs,
  paired with `compliance/` (OSCAL/Trestle). This is the **legacy** path —
  FedRAMP stops accepting new Rev5 certifications June 11, 2027.
- `fedramp_20x/` — rules tagged to FedRAMP 20x Key Security Indicator (KSI)
  IDs, paired with `compliance-20x/`. This is the **current** path — 20x
  becomes mandatory January 1, 2027.

Both tracks check the same kind of input (a simplified app-config JSON
object) but tag their `deny` rules differently, since the two frameworks use
different IDs for (mostly overlapping) requirements.

## Layout

- `fedramp_rev5/app_config.rego` — checks debug/TLS/session-timeout against
  control IDs SI-11, SC-8, AC-12.
- `fedramp_20x/app_config.rego` — checks TLS/MFA/session-timeout/audit-logging
  against KSI IDs KSI-SVC-SIN, KSI-IAM-APM, KSI-IAM-ELP, KSI-MLA-RVL.
- Each has a matching `*_test.rego` with `opa test` unit tests.

## Running the tests

```sh
opa test policy/ -v
```

## Conventions

- One package per logical policy domain, named after its track and domain
  (e.g. `fedramp_rev5.app_config`, `fedramp_20x.app_config`). Rego package
  names can't contain hyphens, hence the underscore.
- Written in Rego v1 syntax (`if`/`contains` required) — this repo's OPA
  (1.20+) defaults to v1 and rejects the older syntax.
- Every `deny` rule should reference the specific control ID or KSI ID it
  enforces, both in a `METADATA` block and in the returned message, so
  failures are traceable to a specific requirement during an audit.
- Policies here are enforcement-time checks. Point-in-time audit evidence and
  narrative documentation live in `compliance/` and `compliance-20x/` instead
  — each policy track is meant to reference the same IDs as its paired
  compliance-reporting track.
