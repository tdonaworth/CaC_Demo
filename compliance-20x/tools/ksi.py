#!/usr/bin/env python3
"""Browse the vendored FedRAMP 20x Key Security Indicators (KSIs) and
cross-check them against ksi-tracker.yaml.

Usage:
    ksi.py themes                 List KSI themes with indicator counts.
    ksi.py list [THEME]           List indicator IDs and names, optionally
                                   filtered to one theme (e.g. IAM).
    ksi.py show KSI-IAM-APM       Show one indicator's full detail.
    ksi.py tracker-status         Cross-check ksi-tracker.yaml coverage
                                   against every indicator in the dataset.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "fedramp-consolidated-rules.json"
TRACKER = ROOT / "ksi-tracker.yaml"


def load_dataset():
    return json.loads(DATASET.read_text())


def load_tracker():
    return yaml.safe_load(TRACKER.read_text()) or {}


def cmd_themes():
    ksi = load_dataset()["KSI"]
    for key, theme in ksi.items():
        count = len(theme.get("indicators", {}))
        print(f"{key:5} {theme['name']:35} {theme['status']:10} {count} indicator(s)")


def cmd_list(theme_filter=None):
    ksi = load_dataset()["KSI"]
    for key, theme in ksi.items():
        if theme_filter and key.upper() != theme_filter.upper():
            continue
        for iid, ind in theme.get("indicators", {}).items():
            print(f"{iid:16} {ind['name']}")


def cmd_show(indicator_id):
    ksi = load_dataset()["KSI"]
    for theme in ksi.values():
        ind = theme.get("indicators", {}).get(indicator_id)
        if ind:
            print(json.dumps(ind, indent=2))
            return
    print(f"Indicator {indicator_id} not found.", file=sys.stderr)
    sys.exit(1)


def cmd_tracker_status():
    ksi = load_dataset()["KSI"]
    all_ids = {
        iid for theme in ksi.values() for iid in theme.get("indicators", {})
    }
    tracker = load_tracker()
    tracked_ids = set(tracker.keys())

    by_status = {}
    for iid, entry in tracker.items():
        by_status.setdefault(entry.get("status", "unknown"), []).append(iid)

    print(f"Dataset indicators: {len(all_ids)}")
    print(f"Tracked indicators: {len(tracked_ids)}")
    missing = sorted(all_ids - tracked_ids)
    if missing:
        print(f"\nUntracked ({len(missing)}):")
        for iid in missing:
            print(f"  - {iid}")

    stale = sorted(tracked_ids - all_ids)
    if stale:
        print(f"\nTracked but no longer in dataset ({len(stale)}):")
        for iid in stale:
            print(f"  - {iid}")

    print("\nBy status:")
    for status, ids in sorted(by_status.items()):
        print(f"  {status}: {len(ids)}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    cmd, rest = args[0], args[1:]
    if cmd == "themes":
        cmd_themes()
    elif cmd == "list":
        cmd_list(rest[0] if rest else None)
    elif cmd == "show":
        if not rest:
            print("usage: ksi.py show KSI-IAM-APM", file=sys.stderr)
            sys.exit(1)
        cmd_show(rest[0])
    elif cmd == "tracker-status":
        cmd_tracker_status()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
