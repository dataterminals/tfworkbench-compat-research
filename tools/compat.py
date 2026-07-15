#!/usr/bin/env python3
"""compat.py - query the TFWWorkbench x UE4SS compatibility matrix.

Stdlib only; runs on any Python 3.8+. Data lives in ../data/compat.json.

Examples
--------
  python tools/compat.py list                 # every entry, newest data first
  python tools/compat.py list --status broken # only broken combos
  python tools/compat.py check --sha a79b894d # match a UE4SS.dll by SHA-256 (prefix ok)
  python tools/compat.py check --build patternsleuth
  python tools/compat.py pin                  # what to install (best 'works' entry)
  python tools/compat.py summary              # counts by status
  python tools/compat.py validate             # sanity-check compat.json against the schema
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "compat.json"
SCHEMA = ROOT / "data" / "schema" / "compat.schema.json"

STATUS_MARK = {"works": "[OK ]", "broken": "[XX ]", "partial": "[~~ ]", "unknown": "[ ? ]"}


def load() -> dict:
    try:
        return json.loads(DATA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"error: {DATA} not found")
    except json.JSONDecodeError as e:
        sys.exit(f"error: {DATA} is not valid JSON: {e}")


def fmt_entry(e: dict) -> str:
    mark = STATUS_MARK.get(e.get("status", "unknown"), "[ ? ]")
    sha = (e.get("ue4ss_dll_sha256") or "")[:12]
    head = f"{mark} {e.get('status','?'):7} | UE4SS: {e.get('ue4ss_build','?')}"
    lines = [head]
    meta = []
    if e.get("ue4ss_channel"):
        meta.append(f"channel={e['ue4ss_channel']}")
    if e.get("ue4ss_date"):
        meta.append(f"date={e['ue4ss_date']}")
    if sha:
        meta.append(f"sha256={sha}...")
    meta.append(f"TFWWorkbench={e.get('tfwworkbench_version','?')}")
    meta.append(f"confidence={e.get('confidence','?')}")
    lines.append("        " + "  ".join(meta))
    if e.get("symptom"):
        lines.append(f"        symptom: {e['symptom']}")
    if e.get("notes"):
        lines.append(f"        notes: {e['notes']}")
    if e.get("sources"):
        lines.append("        sources: " + ", ".join(e["sources"]))
    return "\n".join(lines)


def cmd_list(args) -> int:
    data = load()
    entries = data.get("entries", [])
    if args.status:
        entries = [e for e in entries if e.get("status") == args.status]
    if not entries:
        print("(no matching entries)")
        return 0
    print(f"# {data['meta']['subject']}")
    print(f"# updated {data['meta'].get('updated','?')} - {len(entries)} entr(y/ies)\n")
    for e in entries:
        print(fmt_entry(e))
        print()
    return 0


def cmd_check(args) -> int:
    data = load()
    entries = data.get("entries", [])
    hits = []
    for e in entries:
        if args.sha and (e.get("ue4ss_dll_sha256") or "").lower().startswith(args.sha.lower()):
            hits.append(e)
        elif args.build and args.build.lower() in (e.get("ue4ss_build") or "").lower():
            hits.append(e)
    if not hits:
        needle = args.sha or args.build
        print(f"No entry matches '{needle}'. It is untracked - status UNKNOWN.")
        print("Add it to data/compat.json once you have an observation.")
        return 2
    for e in hits:
        print(fmt_entry(e))
        print()
    return 0


def cmd_pin(args) -> int:
    data = load()
    works = [e for e in data.get("entries", []) if e.get("status") == "works"]
    if not works:
        print("No confirmed-working UE4SS build recorded yet.")
        print("See docs/05-known-good-and-workarounds.md for the current best guess.")
        return 2
    order = {"verified": 0, "reported": 1, "inferred": 2, "untested": 3}
    # An explicit `recommended` flag wins: several combos can 'work' at once (different
    # TFWWorkbench versions, or ABI-only checks with no runtime proof), and confidence
    # alone can't rank those — it would silently fall back to file order.
    works.sort(key=lambda e: (not e.get("recommended", False),
                              order.get(e.get("confidence", "untested"), 9)))
    best = works[0]
    print("Recommended UE4SS build to pin (best 'works' entry):\n")
    print(fmt_entry(best))
    others = [e for e in works[1:] if e.get("status") == "works"]
    if others:
        print(f"Also recorded as working ({len(others)}): "
              + ", ".join(f"{e['ue4ss_build']} x TFWWorkbench {e['tfwworkbench_version']}"
                          for e in others))
        print("Run `compat.py list --status works` for the full evidence on each.")
    return 0


def cmd_summary(args) -> int:
    data = load()
    entries = data.get("entries", [])
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.get("status", "unknown")] = counts.get(e.get("status", "unknown"), 0) + 1
    print(f"{len(entries)} entr(y/ies) tracked:")
    for status in ("works", "partial", "broken", "unknown"):
        if status in counts:
            print(f"  {STATUS_MARK[status]} {status:7} {counts[status]}")
    return 0


def cmd_validate(args) -> int:
    """Light structural validation without external deps."""
    data = load()
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"error: {SCHEMA} not found")
    errors: list[str] = []

    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"top-level: missing required key '{key}'")

    item_schema = schema["properties"]["entries"]["items"]
    req = item_schema.get("required", [])
    enums = {k: v["enum"] for k, v in item_schema["properties"].items() if "enum" in v}
    for i, e in enumerate(data.get("entries", [])):
        for key in req:
            if key not in e:
                errors.append(f"entries[{i}]: missing required key '{key}'")
        for key, allowed in enums.items():
            if key in e and e[key] not in allowed:
                errors.append(f"entries[{i}].{key}: '{e[key]}' not in {allowed}")

    if errors:
        print("INVALID:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"OK: compat.json is well-formed ({len(data.get('entries', []))} entries).")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="list entries")
    pl.add_argument("--status", choices=["works", "broken", "partial", "unknown"])
    pl.set_defaults(func=cmd_list)

    pc = sub.add_parser("check", help="check a specific UE4SS build/hash")
    g = pc.add_mutually_exclusive_group(required=True)
    g.add_argument("--sha", help="UE4SS.dll SHA-256 (prefix match ok)")
    g.add_argument("--build", help="substring of the build label")
    pc.set_defaults(func=cmd_check)

    sub.add_parser("pin", help="show the recommended build to install").set_defaults(func=cmd_pin)
    sub.add_parser("summary", help="counts by status").set_defaults(func=cmd_summary)
    sub.add_parser("validate", help="validate compat.json against the schema").set_defaults(func=cmd_validate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
