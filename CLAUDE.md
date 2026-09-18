# CoC Demo

## Purpose

This repository exists to learn and build out a **Compliance as Code (CaC)**
setup, working toward getting an app **FedRAMP certified**. The web
application in `app/` is a placeholder — its purpose is irrelevant. It
exists only to give the compliance tooling something concrete to point at
(a real codebase to scan, a real config surface to enforce policy against,
etc.). Do not invest effort in the app's features; do invest effort in the
compliance layers around it.

## Why there are two compliance tracks

FedRAMP is mid-transition. Per FedRAMP's own published timeline:

- **January 1, 2027** — the Consolidated Rules for 2026 (FedRAMP 20x)
  become **mandatory** for anyone seeking certification.
- **June 11, 2027** — FedRAMP stops accepting **new Rev5** (the traditional
  NIST 800-53 + OSCAL-based) certification applications entirely.

So this repo has a legacy track and the track that actually matters for a
2027+ certification target:

| | Legacy (Rev5) | **Current target (20x)** |
|---|---|---|
| Enforcement | `policy/fedramp_rev5/` | `policy/fedramp_20x/` |
| Audit/reporting | `compliance/` (OSCAL/Trestle) | `compliance-20x/` |
| Keyed to | NIST 800-53 control IDs | FedRAMP Key Security Indicators (KSI) |
| Format | OSCAL (catalog/profile/SSP) | FedRAMP's own `consolidated-rules.json` |

**Prioritize `compliance-20x/` and `policy/fedramp_20x/`.** The Rev5/OSCAL
track stays in the repo because OSCAL is a widely-used standard worth
knowing independent of FedRAMP, and it's still what the temporary Rev5
pipeline uses through mid-2027 — but it's not where a 2027 certification
effort should be spending its time.

## Compliance approach

Each track is two complementary layers, keyed to the same IDs so findings
are cross-referenceable between enforcement and audit evidence:

1. **Enforcement — OPA / Rego** (`policy/`)
   Machine-checkable policies that gate configuration/deployments at CI
   time (and, eventually, integrate with the target application's existing
   OPA deployment). Each `deny` rule maps to a specific control ID (Rev5
   track) or KSI ID (20x track). See `policy/README.md`.

2. **Audit & reporting**
   - `compliance/` — `compliance-trestle` workspace producing OSCAL
     documents (SSP, Component Definitions, Assessment Results) against the
     NIST Rev 5 Moderate baseline. See `compliance/README.md`.
   - `compliance-20x/` — vendored FedRAMP 20x Consolidated Rules dataset,
     a KSI browser CLI, and `ksi-tracker.yaml` (a lightweight per-indicator
     status record — the 20x-equivalent of an SSP, since 20x moves away
     from static point-in-time documents). See `compliance-20x/README.md`.

When adding a mapping, add it on both sides of a track: a Rego rule
enforcing it, and a corresponding entry in that track's audit side (a
Trestle component-definition entry for Rev5, a `ksi-tracker.yaml` status
update for 20x).

## Repo layout

```
app/                    Placeholder Flask web app
  app.py                Entry point (routes: / and /healthz), request audit logging
  templates/            Jinja templates
  static/               CSS
tests/
  test_app.py           Basic Flask tests, incl. audit-log test
policy/                 OPA/Rego enforcement policies (see policy/README.md)
  fedramp_rev5/         Rev5/NIST 800-53 control-tagged rules (legacy)
  fedramp_20x/          FedRAMP 20x KSI-tagged rules (current target)
compliance/             OSCAL/Trestle audit workspace, Rev5 (see compliance/README.md)
compliance-20x/         FedRAMP 20x dataset + KSI tracker (see compliance-20x/README.md)
docs/
  change-management.md  Draft change process (KSI-CMT-RVP prerequisite)
  logging.md            What's logged today vs. gaps (KSI-MLA-LET)
SECURITY.md             Draft vulnerability disclosure policy (KSI-PIY-RVD prerequisite)
.github/
  workflows/ci.yml      Runs pytest, opa test, dataset validation on every push/PR
  dependabot.yml        Automated dependency updates (KSI-SCR-MIT/MON)
pyproject.toml          Project + runtime deps (Flask) + dev dep group (pytest, compliance-trestle, pyyaml, jsonschema)
uv.lock                 Locked, resolved dependency tree (committed — like package-lock.json)
.python-version         Pins 3.12 for uv to select/install automatically
```

## Stack

- **App:** Python + Flask, managed with **uv** (not pip/venv directly)
- **Enforcement:** OPA + Rego (v1 syntax — this repo's OPA is 1.20+, which
  requires `if`/`contains` keywords)
- **Audit/reporting:** OSCAL via compliance-trestle (Rev5) +
  FedRAMP's own consolidated-rules JSON (20x)

> `compliance-trestle` requires **Python 3.10+** (a dependency uses
> `typing.TypeGuard`). `uv sync` handles this automatically — it reads
> `.python-version` (3.12) and downloads that interpreter itself if needed,
> so there's no more manual Homebrew-Python workaround.

## Running the app

```sh
uv sync
uv run python app/app.py
# http://localhost:5000
```

> On macOS, port 5000 is often taken by AirPlay Receiver. If the app fails to
> bind, either disable AirPlay Receiver (System Settings → General → AirDrop
> & Handoff) or change the port in `app/app.py`.

## Running tests

```sh
uv run pytest
```

## Running policy tests

Requires the `opa` CLI ([install docs](https://www.openpolicyagent.org/docs/latest/#running-opa)):

```sh
opa test policy/ -v
```

## Browsing the FedRAMP 20x KSI dataset

```sh
uv run python compliance-20x/tools/ksi.py themes
uv run python compliance-20x/tools/ksi.py show KSI-IAM-APM
uv run python compliance-20x/tools/ksi.py tracker-status
```

## Status / next steps

- [x] Placeholder Flask app
- [x] Rev5 track: example Rego policy + tests (`policy/fedramp_rev5/`),
      Trestle workspace importing NIST Rev 5 catalog + Moderate baseline
      (177 controls / 18 families, confirmed resolving)
- [x] 20x track: vendored FedRAMP Consolidated Rules dataset + schema
      validator, KSI browser CLI, `ksi-tracker.yaml` seeded with all 46 KSI
      indicators
- [x] All 46 KSI indicators triaged theme by theme; 10 `in_progress` with
      real evidence (Rego policies, request audit logging, CI, Dependabot),
      36 honestly `not_started` pending real infra/auth/org process (see
      `compliance-20x/README.md` for the breakdown and why)
- [x] CI (`.github/workflows/ci.yml`) runs pytest, opa test, and the 20x
      dataset validator on every push/PR
- [ ] Push this repo to a remote and confirm CI + Dependabot actually run;
      only then consider upgrading any `in_progress` tracker entry
- [ ] Look at the 20x `FRR` process rules (vuln disclosure, continuous
      monitoring, change notification) once KSI coverage is further along
- [ ] Decide on a target Certification Class (A/B/C/D) — affects which KSI
      class variants apply
- [ ] Connect the Rego policies here with the target application's existing
      OPA deployment mentioned by the repo owner
- [ ] Rev5 track (lower priority): author a Trestle component definition and
      generate an SSP, if still useful once 20x coverage is solid
