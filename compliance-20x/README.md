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
  python compliance-20x/tools/ksi.py themes
  python compliance-20x/tools/ksi.py list IAM
  python compliance-20x/tools/ksi.py show KSI-IAM-APM
  python compliance-20x/tools/ksi.py tracker-status
  ```
- `ksi-tracker.yaml` — one entry per KSI indicator (status, linked policy,
  evidence notes). This is the 20x-equivalent of an SSP: a living record of
  what's implemented and how it's evidenced, kept close to the code instead
  of a static document. Currently 4/46 indicators are `in_progress`, tied to
  `policy/fedramp_20x/app_config.rego`; the rest are `not_started`.

## Refreshing the vendored dataset

The dataset changes as FedRAMP updates the Consolidated Rules. To pull a
newer copy:

```sh
curl -sL -o compliance-20x/data/fedramp-consolidated-rules.json \
  https://raw.githubusercontent.com/FedRAMP/rules/main/fedramp-consolidated-rules.json
curl -sL -o compliance-20x/data/fedramp-consolidated-rules.schema.json \
  https://raw.githubusercontent.com/FedRAMP/rules/main/schemas/fedramp-consolidated-rules.schema.json
python compliance-20x/tools/validate_dataset.py
python compliance-20x/tools/ksi.py tracker-status   # check for new/removed indicator IDs
```

## Next steps

- [ ] Work through the remaining 42 `not_started` indicators theme by theme;
      for each, decide: enforceable via Rego (`policy/fedramp_20x/`),
      evidenced some other way (a runbook, a CI check, a config), or not
      applicable to this app, and update the tracker accordingly.
- [ ] Look at `FRR` (the process rules — vuln disclosure, continuous
      monitoring, change notification) once the KSI side has more coverage;
      those are less about the app's config and more about the operational
      process around it.
- [ ] Revisit whether a Certification Class (A/B/C/D) target has been chosen
      yet — that affects which KSI class variants (`varies_by_class`) apply.
