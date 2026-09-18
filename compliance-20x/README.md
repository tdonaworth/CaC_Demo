# Compliance — FedRAMP 20x track

This is the second compliance track, alongside `compliance/` (OSCAL/Trestle,
Rev5). It targets **FedRAMP 20x**, which is replacing Rev5 as FedRAMP's
primary certification model:

- Rev5 stops accepting new certification applications **June 11, 2027**.
- The Consolidated Rules for 2026 (which include 20x) become **mandatory**
  for anyone seeking certification on **January 1, 2027**.

Given that timeline, this track — not `compliance/` — is the one to focus on
if the goal is getting an app FedRAMP-certified after 2027.

## Why this looks different from `compliance/`

FedRAMP 20x is not OSCAL. FedRAMP publishes its own bespoke JSON dataset (not
a NIST/OSCAL document type), vendored here in `data/`. There is no equivalent
of Trestle for it — the tooling in `tools/` here is this project's own, built
directly against the dataset's shape.

The dataset has four sections:

| Section | What it is |
|---|---|
| `FRD` | FedRAMP Definitions — shared glossary terms rules reference |
| `FRR` | FedRAMP Rules — process requirements (vuln disclosure, continuous monitoring, change notification, authorization...) with MUST/SHOULD/MAY force |
| `KSI` | Key Security Indicators — outcome-based capability statements, grouped into themes | 
| `CTL` | Optional per-control guidance/parameters for a curated control subset |

**This track focuses on `KSI`** — the 46 indicators across 10 themes are the
closest thing to a checklist you enforce and produce evidence against. Each
indicator still cites the specific NIST 800-53 controls behind it (e.g.
`KSI-IAM-APM` → `ac-3, ia-2, ia-5, sc-23...`), so it's not disconnected from
the control catalog — it's a leaner, capability-oriented curation of it (46
indicators vs. the 177 controls in the Moderate baseline imported under
`compliance/`).

## Files

- `data/fedramp-consolidated-rules.json` — vendored dataset (version
  `2026.09.13.02`, from [FedRAMP/rules](https://github.com/FedRAMP/rules))
- `data/fedramp-consolidated-rules.schema.json` — its JSON Schema
- `tools/validate_dataset.py` — validates the dataset against the schema
  (FedRAMP's own guidance for agents consuming this data says to do this
  before relying on it — see the upstream repo's `AGENTS.md`)
- `tools/ksi.py` — browse the dataset and check tracker coverage:
  ```sh
  uv run python compliance-20x/tools/ksi.py themes
  uv run python compliance-20x/tools/ksi.py list IAM
  uv run python compliance-20x/tools/ksi.py show KSI-IAM-APM
  uv run python compliance-20x/tools/ksi.py tracker-status
  ```
- `ksi-tracker.yaml` — one entry per KSI indicator (status, linked policy,
  evidence notes). This is the 20x-equivalent of an SSP: a living record of
  what's implemented and how it's evidenced, kept close to the code instead
  of a static document. Currently 10/46 indicators are `in_progress`
  (4 via `policy/fedramp_20x/app_config.rego`, plus request logging,
  Dependabot supply-chain automation, and CI-driven security review — see
  the tracker for specifics); the rest are honestly `not_started` because
  they need real infrastructure, an auth system, or an organizational
  process this placeholder app doesn't have yet. None are marked
  `implemented` — nothing here has been proven to run in a live environment
  (this repo has no remote yet), so don't upgrade a status past
  `in_progress` until it has.

## Refreshing the vendored dataset

The dataset changes as FedRAMP updates the Consolidated Rules. To pull a
newer copy:

```sh
curl -sL -o compliance-20x/data/fedramp-consolidated-rules.json \
  https://raw.githubusercontent.com/FedRAMP/rules/main/fedramp-consolidated-rules.json
curl -sL -o compliance-20x/data/fedramp-consolidated-rules.schema.json \
  https://raw.githubusercontent.com/FedRAMP/rules/main/schemas/fedramp-consolidated-rules.schema.json
uv run python compliance-20x/tools/validate_dataset.py
uv run python compliance-20x/tools/ksi.py tracker-status   # check for new/removed indicator IDs
```

## Theme-by-theme status

All 46 indicators have been triaged (`compliance-20x/ksi-tracker.yaml`).
Most remain `not_started` for one of three honest reasons, not neglect:

- **No real infrastructure yet** (most of CNA, RPL, most of SVC, MLA-ALA/EVC/OSM) —
  network topology, backups, SIEM, config-drift enforcement all need an
  actual deployment target this placeholder app doesn't have.
- **No auth/account system yet** (most of IAM) — the app has no login or
  accounts at all, so account-lifecycle and authorization indicators have
  nothing to check.
- **Organizational, not technical** (CED, most of INR and PIY) — training
  programs, executive review, incident after-action reports. A demo repo
  can't fabricate these; they need a real team and cadence.

What moved to `in_progress` this pass, with real (not simulated) artifacts:

- Request-level audit logging (`app/app.py`, see `docs/logging.md`) — KSI-MLA-LET
- CI running the full check suite on every change (`.github/workflows/ci.yml`) — KSI-CMT-VTD
- Git/PR history + CI run history as the change log — KSI-CMT-LMC
- Dependabot for uv + GitHub Actions (`.github/dependabot.yml`) — KSI-SCR-MIT, KSI-SCR-MON
- Dependabot + CI + this tracker as an ongoing improvement loop — KSI-SVC-EIS

None of these are marked `implemented` — the repo has no git remote yet, so
none of this automation has actually run anywhere. Confirm it runs green
once pushed before upgrading a status.

## Next steps

- [ ] Push this repo to a remote and confirm CI + Dependabot actually run;
      only then consider upgrading any `in_progress` entry.
- [ ] Once there's a real deployment target, revisit the CNA/RPL/most-SVC
      indicators — many are natural fits for a Rego policy over IaC rather
      than app config (a different enforcement point than
      `policy/fedramp_20x/app_config.rego`).
- [ ] Once there's a real auth system, revisit the IAM indicators.
- [ ] Look at `FRR` (the process rules — vuln disclosure, continuous
      monitoring, change notification) once KSI coverage is further along.
- [ ] Revisit whether a Certification Class (A/B/C/D) target has been chosen
      yet — that affects which KSI class variants (`varies_by_class`) apply,
      e.g. KSI-CNA-EIS and KSI-SVC-PRR/RUD/VCM are only required at Class C.
