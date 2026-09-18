#!/usr/bin/env python3
"""Validate the vendored FedRAMP consolidated rules dataset against its schema.

FedRAMP's own AGENTS.md guidance for this dataset says: validate it against
the schema before relying on automated analysis. This script does that.
"""
import json
import sys
from pathlib import Path

import jsonschema

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATASET = DATA_DIR / "fedramp-consolidated-rules.json"
SCHEMA = DATA_DIR / "fedramp-consolidated-rules.schema.json"


def main() -> int:
    dataset = json.loads(DATASET.read_text())
    schema = json.loads(SCHEMA.read_text())

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(dataset), key=lambda e: e.path)

    if not errors:
        print(f"OK: {DATASET.name} (version {dataset['info']['version']}) is valid.")
        return 0

    print(f"INVALID: {len(errors)} schema violation(s) in {DATASET.name}:")
    for err in errors:
        path = "/".join(str(p) for p in err.path) or "<root>"
        print(f"  - {path}: {err.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
