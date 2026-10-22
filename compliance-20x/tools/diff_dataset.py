#!/usr/bin/env python3
"""Summarize how the vendored FedRAMP dataset changed vs. the committed copy.

Compares the dataset currently on disk against the version at git HEAD and
prints a Markdown summary: version bump, added/removed KSI indicators and FRR
rules, control-mapping changes, and statement/force changes. Used by the
scheduled dataset-refresh workflow to populate the PR body, and handy to run
by hand after a manual refresh.

    uv run python compliance-20x/tools/diff_dataset.py

Exit code 0 if there is a difference worth reporting, 1 if the dataset is
unchanged vs. HEAD (nothing to open a PR for).
"""
import json
import subprocess
import sys
from pathlib import Path

DATASET = Path(__file__).resolve().parent.parent / "data" / "fedramp-consolidated-rules.json"
REPO_PATH = "compliance-20x/data/fedramp-consolidated-rules.json"


def load_head() -> dict | None:
    """Return the dataset as committed at HEAD, or None if it isn't tracked yet."""
    try:
        blob = subprocess.run(
            ["git", "show", f"HEAD:{REPO_PATH}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None
    return json.loads(blob)


def ksi_indicators(d: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for theme in d.get("KSI", {}).values():
        out.update(theme.get("indicators", {}))
    return out


def frr_rules(d: dict) -> dict[str, dict]:
    """Flatten every FRR leaf rule (a dict carrying a 'statement') to {id: node}."""
    out: dict[str, dict] = {}

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, val in node.items():
                if isinstance(val, dict) and "statement" in val:
                    out[key] = val
                elif isinstance(val, dict):
                    walk(val)

    for cat in d.get("FRR", {}).values():
        walk(cat.get("data", {}))
    return out


def fmt_set(ids: set[str]) -> str:
    return ", ".join(f"`{i}`" for i in sorted(ids)) if ids else "_none_"


def main() -> int:
    new = json.loads(DATASET.read_text())
    old = load_head()

    new_ver = new["info"]["version"]
    if old is None:
        print(f"Dataset not yet tracked at HEAD; on-disk version is `{new_ver}`.")
        return 0

    old_ver = old["info"]["version"]

    new_ksi, old_ksi = ksi_indicators(new), ksi_indicators(old)
    new_frr, old_frr = frr_rules(new), frr_rules(old)

    ksi_added = set(new_ksi) - set(old_ksi)
    ksi_removed = set(old_ksi) - set(new_ksi)
    frr_added = set(new_frr) - set(old_frr)
    frr_removed = set(old_frr) - set(new_frr)

    control_changes = []
    for i in sorted(set(new_ksi) & set(old_ksi)):
        o, n = old_ksi[i].get("controls", []), new_ksi[i].get("controls", [])
        if set(o) != set(n):
            added = sorted(set(n) - set(o))
            removed = sorted(set(o) - set(n))
            control_changes.append((i, added, removed))

    ksi_stmt_changes = sorted(
        i for i in set(new_ksi) & set(old_ksi)
        if new_ksi[i].get("statement") != old_ksi[i].get("statement")
    )

    frr_changes = sorted(
        i for i in set(new_frr) & set(old_frr)
        if new_frr[i].get("statement") != old_frr[i].get("statement")
        or new_frr[i].get("force") != old_frr[i].get("force")
    )

    unchanged = (
        old_ver == new_ver
        and not ksi_added and not ksi_removed
        and not frr_added and not frr_removed
        and not control_changes and not ksi_stmt_changes and not frr_changes
    )
    if unchanged:
        print(f"No change: dataset still at version `{new_ver}`.")
        return 1

    lines = [
        f"## FedRAMP dataset update: `{old_ver}` → `{new_ver}`",
        "",
        f"- KSI indicators: {len(old_ksi)} → {len(new_ksi)} "
        f"(added: {fmt_set(ksi_added)}; removed: {fmt_set(ksi_removed)})",
        f"- FRR rules: {len(old_frr)} → {len(new_frr)} "
        f"(added: {fmt_set(frr_added)}; removed: {fmt_set(frr_removed)})",
        "",
    ]

    if ksi_stmt_changes:
        lines += [f"### KSI statement changes ({len(ksi_stmt_changes)})", ""]
        lines += [f"- `{i}`" for i in ksi_stmt_changes] + [""]

    if control_changes:
        lines += [f"### KSI control-mapping changes ({len(control_changes)})", ""]
        for i, added, removed in control_changes:
            parts = []
            if added:
                parts.append("added " + ", ".join(f"`{c}`" for c in added))
            if removed:
                parts.append("removed " + ", ".join(f"`{c}`" for c in removed))
            lines.append(f"- `{i}`: " + "; ".join(parts))
        lines.append("")

    if frr_changes:
        lines += [f"### FRR statement/force changes ({len(frr_changes)})", ""]
        lines += [f"- `{i}`" for i in frr_changes] + [""]

    lines += [
        "> Trackers (`ksi-tracker.yaml` / `frr-tracker.yaml`) key off indicator "
        "and rule IDs, not duplicated control lists. Review whether any tracker "
        "**notes** reference details that changed above before merging.",
    ]

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
