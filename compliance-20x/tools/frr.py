#!/usr/bin/env python3
"""Browse the vendored FedRAMP 20x Rules (FRR) and cross-check the
provider-facing rules against frr-tracker.yaml.

Target Certification Class is C (see CLAUDE.md) — rules that vary by class
(no top-level statement/force, only a `varies_by_class` map) are shown and
tracked using their Class C variant.

Usage:
    frr.py categories             List FRR categories with rule counts.
    frr.py list CAT                List provider-facing rule IDs and names
                                    in one category (e.g. VDR).
    frr.py show VDR-CSO-DET        Show one rule's full detail.
    frr.py tracker-status          Cross-check frr-tracker.yaml coverage
                                    against every affects:[Providers] rule
                                    in the tracked categories.
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "fedramp-consolidated-rules.json"
TRACKER = ROOT / "frr-tracker.yaml"

# Categories frr-tracker.yaml actually covers today.
TRACKED_CATEGORIES = {"VDR", "VER", "IEC", "CCM", "SCN"}

# This project's target FedRAMP 20x Certification Class (see CLAUDE.md).
CERT_CLASS = "c"

# Version scopes to include. FRR rules are split by "all" (both Rev5 and
# 20x), "20x", and "rev5". This repo targets 20x, so rev5-only rules (e.g.
# a rule's Rev5-specific sibling) are excluded.
INCLUDED_SCOPES = {"all", "20x"}


def load_dataset():
    return json.loads(DATASET.read_text())["FRR"]


def load_tracker():
    return yaml.safe_load(TRACKER.read_text()) or {}


def walk_rules(node, path=""):
    """Yield (rule_id, rule_dict, scope) for every leaf rule under node.

    A leaf rule is any dict carrying 'affects' — this catches both ordinary
    rules (top-level 'statement'/'force') and rules that only exist as
    class variants (no top-level statement, only 'varies_by_class').
    """
    if isinstance(node, dict):
        if "affects" in node and ("statement" in node or "varies_by_class" in node):
            parts = path.split("/")
            scope = parts[0]
            rid = parts[-1]
            if scope in INCLUDED_SCOPES:
                yield rid, node, scope
        else:
            for key, value in node.items():
                yield from walk_rules(value, f"{path}/{key}" if path else key)


def effective_force(rule):
    """This project's applicable force: top-level if present, else the
    Class C variant's force."""
    if "force" in rule:
        return rule["force"]
    variant = rule.get("varies_by_class", {}).get(CERT_CLASS)
    return variant["force"] if variant else None


def effective_statement(rule):
    if "statement" in rule:
        return rule["statement"]
    variant = rule.get("varies_by_class", {}).get(CERT_CLASS)
    return variant["statement"] if variant else None


def cmd_categories():
    frr = load_dataset()
    for key, cat in frr.items():
        rules = list(walk_rules(cat["data"]))
        provider_rules = [r for r in rules if r[1].get("affects") == ["Providers"]]
        tracked = " (tracked)" if key in TRACKED_CATEGORIES else ""
        print(
            f"{key:5} {cat['info']['name']:45} "
            f"{len(provider_rules)}/{len(rules)} provider-facing rule(s){tracked}"
        )


def cmd_list(category):
    frr = load_dataset()
    cat = frr.get(category.upper())
    if not cat:
        print(f"Category {category} not found.", file=sys.stderr)
        sys.exit(1)
    for rid, rule, scope in sorted(walk_rules(cat["data"])):
        affects = ",".join(rule.get("affects", []))
        force = effective_force(rule) or "?"
        variant_flag = "*" if "varies_by_class" in rule else " "
        print(f"{rid:16}{variant_flag}[{force:9}] {affects:12} {rule.get('name')}")
    print("\n* = force/statement shown is the Class C variant (varies_by_class)")


def cmd_show(rule_id):
    frr = load_dataset()
    category = rule_id.split("-")[0]
    cat = frr.get(category)
    if cat:
        for rid, rule, scope in walk_rules(cat["data"]):
            if rid == rule_id:
                print(json.dumps(rule, indent=2))
                if "varies_by_class" in rule:
                    print(f"\nEffective for Class {CERT_CLASS.upper()}:")
                    print(f"  force: {effective_force(rule)}")
                    print(f"  statement: {effective_statement(rule)}")
                return
    print(f"Rule {rule_id} not found.", file=sys.stderr)
    sys.exit(1)


def cmd_tracker_status():
    frr = load_dataset()
    all_ids = set()
    for key in TRACKED_CATEGORIES:
        cat = frr.get(key)
        if not cat:
            continue
        for rid, rule, scope in walk_rules(cat["data"]):
            if rule.get("affects") == ["Providers"]:
                all_ids.add(rid)

    tracker = load_tracker()
    tracked_ids = set(tracker.keys())

    by_status = {}
    for rid, entry in tracker.items():
        by_status.setdefault(entry.get("status", "unknown"), []).append(rid)

    print(f"Provider-facing rules in tracked categories ({sorted(TRACKED_CATEGORIES)}): {len(all_ids)}")
    print(f"Tracked rules: {len(tracked_ids)}")

    missing = sorted(all_ids - tracked_ids)
    if missing:
        print(f"\nUntracked ({len(missing)}):")
        for rid in missing:
            print(f"  - {rid}")

    stale = sorted(tracked_ids - all_ids)
    if stale:
        print(f"\nTracked but no longer applicable ({len(stale)}):")
        for rid in stale:
            print(f"  - {rid}")

    print("\nBy status:")
    for status, ids in sorted(by_status.items()):
        print(f"  {status}: {len(ids)}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    cmd, rest = args[0], args[1:]
    if cmd == "categories":
        cmd_categories()
    elif cmd == "list":
        if not rest:
            print("usage: frr.py list VDR", file=sys.stderr)
            sys.exit(1)
        cmd_list(rest[0])
    elif cmd == "show":
        if not rest:
            print("usage: frr.py show VDR-CSO-DET", file=sys.stderr)
            sys.exit(1)
        cmd_show(rest[0])
    elif cmd == "tracker-status":
        cmd_tracker_status()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
