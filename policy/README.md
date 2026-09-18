# Policy (OPA / Rego)

This directory holds Rego policies used to **enforce** FedRAMP Moderate control
requirements as machine-checkable rules, meant to run in CI (and eventually
against the target application's real OPA deployment).

## Layout

- `fedramp/app_config.rego` — example policy evaluating a simplified app
  config against a few controls (SI-11, SC-8, AC-12), to demonstrate the
  pattern of mapping a `deny[msg]` rule back to a specific control ID via
  the rule's metadata annotation.
- `fedramp/app_config_test.rego` — matching `opa test` unit tests.

## Running the tests

```sh
opa test policy/ -v
```

## Conventions

- One package per logical policy domain (e.g. `fedramp.app_config`,
  `fedramp.network`, `fedramp.iam`).
- Every `deny` rule should reference the FedRAMP/NIST 800-53 control ID it
  enforces, both in a `METADATA` block and in the returned message, so
  failures are traceable to a control during an audit.
- Policies here are enforcement-time checks. Point-in-time audit evidence and
  narrative documentation live in `compliance/` (OSCAL/Trestle) instead —
  the two are meant to reference the same control IDs.
