#!/usr/bin/env python3
"""abi-diff.py - prove (or disprove) a UE4SS C++ mod ABI break by diffing imports vs exports.

A precompiled UE4SS C++ mod (e.g. TFWWorkbench's dlls/main.dll) imports UE4SS
functions by their decorated (name-mangled) symbol. If the installed UE4SS.dll no
longer EXPORTS a symbol the mod IMPORTS, the Windows loader fails the mod load with
0x7F ERROR_PROC_NOT_FOUND. This tool finds exactly which symbol(s), if any.

Requires pefile:  pip install pefile

Usage:
  python tools/abi-diff.py <mod_main.dll> <UE4SS.dll>
  python tools/abi-diff.py <mod_main.dll> <UE4SS.dll> --json

Exit codes: 0 = all imports resolve (no ABI break)  |  1 = missing symbol(s)  |  2 = error
"""
from __future__ import annotations
import argparse, json, sys

try:
    import pefile
except ImportError:
    sys.exit("error: pefile not installed. Run: pip install pefile")


def imports_from(dll_path: str, target_dll: str = "ue4ss.dll") -> list[str]:
    pe = pefile.PE(dll_path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
    out = []
    for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
        if e.dll.decode(errors="replace").lower() == target_dll.lower():
            for imp in e.imports:
                out.append(imp.name.decode(errors="replace") if imp.name else f"<ordinal {imp.ordinal}>")
    return out


def exports_of(dll_path: str) -> set[str]:
    pe = pefile.PE(dll_path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    return {s.name.decode(errors="replace") for s in getattr(pe, "DIRECTORY_ENTRY_EXPORT", []).symbols
            if getattr(pe, "DIRECTORY_ENTRY_EXPORT", None) and s.name}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mod_dll", help="the mod's precompiled DLL (e.g. TFWWorkbench/dlls/main.dll)")
    ap.add_argument("ue4ss_dll", help="the installed UE4SS.dll to test against")
    ap.add_argument("--target", default="ue4ss.dll", help="import source DLL name (default: ue4ss.dll)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    try:
        imps = imports_from(args.mod_dll, args.target)
        exps = exports_of(args.ue4ss_dll)
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    missing = [i for i in imps if i not in exps]
    present = [i for i in imps if i in exps]

    if args.json:
        print(json.dumps({"imports": len(imps), "exports": len(exps),
                          "resolved": present, "missing": missing}, indent=2))
    else:
        print(f"{args.mod_dll}")
        print(f"  imports from {args.target}: {len(imps)}")
        print(f"  {args.ue4ss_dll} exports: {len(exps)}")
        print(f"  resolved: {len(present)}   MISSING: {len(missing)}")
        if missing:
            print("\n  MISSING (cause of 0x7F ERROR_PROC_NOT_FOUND):")
            for m in missing:
                print("    " + m)
        else:
            print("\n  OK - every import resolves; this UE4SS build is ABI-compatible with the mod.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
