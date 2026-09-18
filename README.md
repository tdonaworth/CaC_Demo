# CoC Demo

![CI](https://github.com/tdonaworth/CaC_Demo/actions/workflows/ci.yml/badge.svg)

A learning project for **Compliance as Code (CaC)**, working toward getting
an application **FedRAMP certified**. The web app in [`app/`](app/) is a
deliberately minimal Flask placeholder — its only job is to give the
compliance tooling something real to point at. All the actual substance of
this repo is in how compliance requirements get turned into code: enforced
policy, tracked evidence, and automation, instead of static documents.

## Why two compliance tracks

FedRAMP is mid-transition. Per FedRAMP's own published timeline:

- **January 1, 2027** — FedRAMP 20x becomes **mandatory** for anyone seeking
  certification.
- **June 11, 2027** — FedRAMP stops accepting **new Rev5** (the traditional
  NIST 800-53 + OSCAL) certification applications entirely.

So this repo tracks both, with 20x as the priority:

| | Legacy — Rev5 | **Current target — 20x** |
|---|---|---|
| Enforcement | [`policy/fedramp_rev5/`](policy/fedramp_rev5/) | [`policy/fedramp_20x/`](policy/fedramp_20x/) |
| Audit / evidence | [`compliance/`](compliance/) (OSCAL via Trestle) | [`compliance-20x/`](compliance-20x/) |
| Keyed to | NIST 800-53 control IDs | FedRAMP Key Security Indicators (KSI) |

## Current status

All 46 FedRAMP 20x Key Security Indicators have been triaged in
[`compliance-20x/ksi-tracker.yaml`](compliance-20x/ksi-tracker.yaml) — the
lightweight, continuously-updated stand-in 20x calls for instead of a static
point-in-time SSP:

| implemented | in progress | not started |
|---|---|---|
| 2 | 8 | 36 |

Most `not_started` entries are that way for an honest reason, not neglect —
this placeholder app has no real infrastructure, no auth system, and no
organizational processes yet. See
[`compliance-20x/README.md`](compliance-20x/README.md) for the full
breakdown of what's blocking what.

## Repo layout

```
app/                 Placeholder Flask web app
tests/                Its test suite
policy/               OPA/Rego enforcement (Rev5-tagged and 20x-tagged tracks)
compliance/           OSCAL/Trestle audit workspace (Rev5)
compliance-20x/       Vendored FedRAMP 20x dataset, KSI browser CLI, KSI tracker
docs/                 Supporting process docs (change management, logging)
.github/              CI (pytest, opa test, dataset validation) + Dependabot
```

See [`CLAUDE.md`](CLAUDE.md) for the full write-up of how the pieces fit
together, and each directory's own README for specifics.

## Getting started

Dependencies are managed with [uv](https://docs.astral.sh/uv/) — it also
handles installing the right Python version itself, no separate setup step
needed.

```sh
uv sync
uv run python app/app.py
# http://localhost:5000
```

Run the tests:

```sh
uv run pytest                                          # app tests
opa test policy/ -v                                    # policy tests (requires the opa CLI)
uv run python compliance-20x/tools/validate_dataset.py # validate the vendored FedRAMP dataset
```

Browse the FedRAMP 20x KSI dataset:

```sh
uv run python compliance-20x/tools/ksi.py themes
uv run python compliance-20x/tools/ksi.py show KSI-IAM-APM
uv run python compliance-20x/tools/ksi.py tracker-status
```

## More detail

- [`CLAUDE.md`](CLAUDE.md) — full project context and status
- [`policy/README.md`](policy/README.md) — the Rego enforcement layer
- [`compliance/README.md`](compliance/README.md) — the Rev5/OSCAL track
- [`compliance-20x/README.md`](compliance-20x/README.md) — the FedRAMP 20x track
- [`SECURITY.md`](SECURITY.md) — vulnerability disclosure (draft)
