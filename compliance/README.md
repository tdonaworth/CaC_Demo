# Compliance (OSCAL / Trestle)

Trestle workspace producing OSCAL artifacts (System Security Plan, Component
Definitions, Assessment Plans/Results) for this project's compliance target.

## Baseline note: FedRAMP-specific profile is not currently available as OSCAL

The original plan was to import FedRAMP's own tailored Moderate baseline
profile (NIST Moderate + FedRAMP's added controls/parameter overrides) from
`GSA/fedramp-automation`. As of this writing that repository no longer
exists, and FedRAMP's current GitHub org (`FedRAMP/rules`) publishes a
different artifact — a `fedramp-consolidated-rules.json` format that looks
tied to the newer "FedRAMP 20x" initiative rather than the classic
OSCAL SSP/profile model. FedRAMP's legacy baseline docs now live in
`FedRAMP/docs-legacy` only as `.xlsx`/`.docx`, not machine-readable OSCAL.

Until a current machine-readable FedRAMP-tailored baseline is available,
this workspace imports **NIST SP 800-53 Rev 5's own generic Moderate
baseline** as a stand-in — same control family structure, same 177 controls
FedRAMP Moderate is built on top of, just without FedRAMP's specific
additions/tailoring. Re-visit this if/when FedRAMP publishes a current OSCAL
baseline, or if the FedRAMP 20x rules format becomes the better target
instead.

## Current state

- `catalogs/nist800-53r5/catalog.json` — imported NIST SP 800-53 Rev 5.2.0
  catalog (from `usnistgov/oscal-content`)
- `profiles/fedramp-moderate/profile.json` — imported NIST Rev 5 Moderate
  baseline profile, re-pointed (via `trestle href`) to import the catalog
  above from the local workspace instead of its original relative path
- `catalogs/fedramp-moderate-resolved/` — resolved profile+catalog output
  (git-ignored; regenerate with the command below)

Not yet started: `component-definitions/`, `system-security-plans/`,
`assessment-plans/`, `assessment-results/`.

## Commands used to set this up

```sh
trestle init

# Catalog + baseline profile, from NIST's own OSCAL content repo
curl -sL -o /tmp/catalog.json \
  https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
curl -sL -o /tmp/profile.json \
  https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json

trestle import -f /tmp/catalog.json -o nist800-53r5
trestle import -f /tmp/profile.json -o fedramp-moderate

# The imported profile references its catalog by a relative path meant for
# the oscal-content repo's own layout; repoint it at the local catalog:
trestle href -n fedramp-moderate -hr trestle://catalogs/nist800-53r5/catalog.json

trestle validate -a
```

## Regenerating the resolved catalog

```sh
trestle author profile-resolve -n fedramp-moderate -o fedramp-moderate-resolved
```

## Next steps

- [ ] Author a component definition describing how the placeholder app (and
      its Rego policies) implement a subset of controls
- [ ] Generate an SSP from the profile + component definition
- [ ] Decide whether to keep chasing a FedRAMP-tailored baseline or treat
      FedRAMP 20x's `consolidated-rules.json` as the real target

## How this relates to `policy/`

- `compliance/` (this directory) is the **audit and reporting** layer:
  human- and machine-readable OSCAL documents describing which controls
  apply and how they're satisfied — the artifacts an assessor reviews.
- `policy/` is the **enforcement** layer: Rego policies that actively gate
  configuration/deployments in CI against a subset of those same controls.

Control IDs should stay consistent between the two so a Rego `deny` rule and
an OSCAL component-definition control-implementation can be cross-referenced.
