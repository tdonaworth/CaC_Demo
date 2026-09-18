# CoC Demo

## Purpose

This repository exists to learn and build out a **Compliance as Code (CaC)**
setup, targeting the **FedRAMP Moderate** baseline. The web application in
`app/` is a placeholder — its purpose is irrelevant. It exists only to give
the compliance tooling something concrete to point at (a real codebase to
scan, a real config surface to enforce policy against, etc.). Do not invest
effort in the app's features; do invest effort in the compliance layers
around it.

## Compliance approach

Two complementary layers, both keyed to the same FedRAMP Moderate /
NIST 800-53 control IDs so findings are cross-referenceable:

1. **Enforcement — OPA / Rego** (`policy/`)
   Machine-checkable policies that gate configuration/deployments at CI
   time (and, eventually, integrate with the target application's existing
   OPA deployment). Each `deny` rule maps to a specific control ID.

2. **Audit & reporting — OSCAL / Trestle** (`compliance/`)
   `compliance-trestle` workspace producing OSCAL documents (System
   Security Plan, Component Definitions, Assessment Results) against the
   imported FedRAMP Moderate profile. This is the artifact layer an
   assessor would actually review. Not yet initialized — see
   `compliance/README.md` for the `trestle init` steps.

When adding a control mapping, add it in both places where applicable: a
Rego rule enforcing it in `policy/`, and a corresponding
control-implementation entry in the Trestle component definition once that
workspace exists.

## Repo layout

```
app/                    Placeholder Flask web app
  app.py                Entry point (routes: / and /healthz)
  templates/            Jinja templates
  static/               CSS
tests/
  test_app.py           Basic Flask tests
policy/                 OPA/Rego enforcement policies (see policy/README.md)
compliance/             OSCAL/Trestle audit workspace (see compliance/README.md)
requirements.txt        Runtime deps (Flask)
requirements-dev.txt    Dev/test deps + compliance-trestle
```

## Stack

- **App:** Python 3 + Flask
- **Enforcement:** OPA + Rego
- **Audit/reporting:** OSCAL via compliance-trestle

## Running the app

```sh
pip install -r requirements.txt
python app/app.py
# http://localhost:5000
```

> On macOS, port 5000 is often taken by AirPlay Receiver. If the app fails to
> bind, either disable AirPlay Receiver (System Settings → General → AirDrop
> & Handoff) or change the port in `app/app.py`.

## Running tests

```sh
pip install -r requirements-dev.txt
pytest
```

## Running policy tests

Requires the `opa` CLI ([install docs](https://www.openpolicyagent.org/docs/latest/#running-opa)):

```sh
opa test policy/ -v
```

## Status / next steps

- [x] Placeholder Flask app
- [x] Example Rego policy + tests (`policy/fedramp/app_config.rego`)
- [ ] Initialize the Trestle workspace under `compliance/` and import the
      FedRAMP Moderate profile
- [ ] Build out a full control-to-policy mapping (start with the FedRAMP
      Moderate control families most relevant to a web app: AC, AU, IA, SC, SI)
- [ ] Wire `opa test` and (once it exists) `trestle validate`/`trestle author`
      checks into CI
- [ ] Connect the Rego policies here with the target application's existing
      OPA deployment mentioned by the repo owner
