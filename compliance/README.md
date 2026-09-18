# Compliance (OSCAL / Trestle)

This directory is the future home of the [compliance-trestle](https://github.com/oscal-compliance/compliance-trestle)
workspace used to produce and maintain OSCAL artifacts (System Security Plan,
Component Definitions, Assessment Plans/Results) against the **FedRAMP
Moderate** baseline.

This is currently a placeholder — `compliance-trestle` is listed in
`requirements-dev.txt` but the workspace has not been initialized yet.

## Planned setup

```sh
pip install -r requirements-dev.txt
cd compliance
trestle init
trestle import -f <fedramp-moderate-baseline.json> -o fedramp-moderate
```

That will create the standard Trestle workspace layout under this directory:

```
compliance/
├── .trestle/                # trestle config
├── dist/                    # rendered/assembled OSCAL output (JSON/YAML/XML)
├── catalogs/                 # imported NIST 800-53 catalog
├── profiles/
│   └── fedramp-moderate/     # imported FedRAMP Moderate baseline profile
├── component-definitions/    # how this app's components satisfy controls
└── system-security-plans/    # the SSP tying it all together
```

## How this relates to `policy/`

- `compliance/` (this directory) is the **audit and reporting** layer:
  human- and machine-readable OSCAL documents describing which controls
  apply and how they're satisfied — the artifacts an assessor reviews.
- `policy/` is the **enforcement** layer: Rego policies that actively gate
  configuration/deployments in CI against a subset of those same controls.

Control IDs should stay consistent between the two so a Rego `deny` rule and
an OSCAL component-definition control-implementation can be cross-referenced.
