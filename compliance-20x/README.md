# Compliance — FedRAMP 20x track

This is the second compliance track, alongside `compliance/` (OSCAL/Trestle,
Rev5). It targets **FedRAMP 20x**, which is replacing Rev5 as FedRAMP's
primary certification model:

- Rev5 stops accepting new certification applications **June 11, 2027**.
- The Consolidated Rules for 2026 (which include 20x) become **mandatory**
  for anyone seeking certification on **January 1, 2027**.

Given that timeline, this track — not `compliance/` — is the one to focus on
if the goal is getting an app FedRAMP-certified after 2027.

**Target Certification Class: C.** FedRAMP 20x defines four Certification
Classes (A/B/C/D), and both the `KSI` and `FRR` sides of the dataset have
rules that only apply (or apply at a stricter force) for specific classes.
Picking C resolves that ambiguity everywhere it showed up:

- `ksi-tracker.yaml`: KSI-CNA-EIS, KSI-MLA-ALA, and KSI-SVC-PRR/RUD/VCM are
  confirmed *required* (Class C is a required, not optional, class for
  those indicators).
- `frr-tracker.yaml`: 13 rules exist only as per-class variants (e.g.
  VDR-TFR-MVX, IEC-CSO-IIR/OIR/FIR, CCM-QTR-MTG) and are now tracked using
  their Class C force/statement.
- `FRC-CSF-BSL` (not yet in a tracker) maps Class C's Rev5 baseline to the
  same 18 NIST 800-53 control families already imported as the Moderate
  baseline under `compliance/` — consistent with Class C being roughly the
  20x equivalent of a Moderate-impact Rev5 authorization.

None of this makes anything `implemented` by itself — picking a class
doesn't create the infrastructure, incident process, or agency
relationship most `not_started` entries are still waiting on. It just
removes "which class applies" as an open question.

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
  of a static document. Currently 2/46 indicators are `implemented`
  (proven by a real green CI run and a real Dependabot PR after the repo
  was pushed to `github.com/tdonaworth/CaC_Demo`), 8/46 are `in_progress`
  (via `policy/fedramp_20x/app_config.rego`, request logging, and
  Dependabot supply-chain automation — see the tracker for specifics); the
  rest are honestly `not_started` because they need real infrastructure, an
  auth system, or an organizational process this placeholder app doesn't
  have yet.
- `frr-tracker.yaml` / `tools/frr.py` — the same tracker pattern, but for
  the `FRR` (process rule) side of the dataset instead of `KSI`. Scoped so
  far to the five categories CLAUDE.md calls out (VDR, VER, IEC, CCM, SCN —
  vulnerability disclosure, incident communication, continuous monitoring,
  change notification); see "FRR (process rules)" below.

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

With the repo now pushed to `github.com/tdonaworth/CaC_Demo`, two of those
`in_progress` indicators became provable and moved to `implemented`:

- CI running the full check suite on every change, confirmed green on
  `main` (`.github/workflows/ci.yml`) — KSI-CMT-VTD
- Git/PR history + CI run history as the change log, confirmed via a real
  run URL — KSI-CMT-LMC

The other `in_progress` indicators still have real (not simulated)
artifacts, but haven't yet cleared the same "proven to run live" bar:

- Request-level audit logging (`app/app.py`, see `docs/logging.md`) — KSI-MLA-LET
- Dependabot for uv + GitHub Actions (`.github/dependabot.yml`) — KSI-SCR-MIT, KSI-SCR-MON
- Dependabot + CI + this tracker as an ongoing improvement loop — KSI-SVC-EIS

## FRR (process rules)

`frr-tracker.yaml` (browse with `tools/frr.py`) triages the FRR side the
same way `ksi-tracker.yaml` triages KSI. So far it covers the five
categories CLAUDE.md flagged as the FRR follow-up — VDR and VER
(vulnerability detection/response/reporting), IEC (incident communication),
CCM (continuous monitoring), and SCN (change notification) — restricted to
the rules where `affects: [Providers]` (the other rules in those same
categories bind FedRAMP or Agencies, not the CSO).

76 rules are tracked (63 with a class-agnostic top-level statement, plus 13
that exist only as per-class variants — e.g. VDR-TFR-MVX, IEC-CSO-IIR/OIR/FIR,
CCM-QTR-MTG — now tracked using their Class C force/statement since that's
this project's target class).

The finding: 73 of the 76 tracked rules are `not_started` for one structural
reason — almost every rule in these categories presumes an active FedRAMP
Certification and real agency customers already exist (an Ongoing
Certification Report to publish, a Quarterly Review to host, "necessary
parties" to notify of a change). None of that exists for a demo repo with
no ATO, so all of CCM and most of VER/IEC/SCN are honestly `not_started`.
The exception is 3 of VDR's detection/response rules
(VDR-CSO-DET/RES/ADT), which don't require a Certification to be true
today — Dependabot is real, running vulnerability detection and response
regardless of certification status, so those move to `in_progress` on the
same evidence as KSI-SCR-MON/KSI-SCR-MIT.

The other 12 FRR categories (AFC, AGU, CDS, CMU, CPO, FRC, IVV, MAS, MKT,
REC, SCG, SDR) aren't covered by the tracker yet.

## Next steps

- [x] Push this repo to a remote and confirm CI + Dependabot actually run —
      done; KSI-CMT-VTD and KSI-CMT-LMC upgraded to `implemented` above.
- [ ] Once there's a real deployment target, revisit the CNA/RPL/most-SVC
      indicators — many are natural fits for a Rego policy over IaC rather
      than app config (a different enforcement point than
      `policy/fedramp_20x/app_config.rego`).
- [ ] Once there's a real auth system, revisit the IAM indicators.
- [x] Decide on a target Certification Class — **C**, see "Target
      Certification Class: C" at the top of this README. Resolved which
      `varies_by_class` KSI indicators apply and which FRR rules' Class C
      variant to track; did not itself unblock any `not_started` entry
      (those still need a real Certification/agency relationship or real
      infrastructure).
- [ ] Pursuing an actual FedRAMP Certification is the real unblock for
      nearly all of `frr-tracker.yaml` (an Ongoing Certification Report,
      Quarterly Reviews, agency customers to notify) — out of scope for a
      demo repo, but worth knowing that's the wall, not missing engineering.
- [ ] Extend the FRR tracker to the remaining 12 categories once there's a
      reason to (e.g. AFC/CDS/FRC become relevant once actually pursuing a
      Certification Package).
