#!/usr/bin/env python3
"""patch-main-dll.py - EXPERIMENTAL single-symbol import patch for TFWWorkbench's main.dll.

The break is one re-signatured UE4SS export: UStruct::GetMinAlignment() went from
returning int32& to int16&, so main.dll's import
    ?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ   (int&,  'H')
no longer exists; current UE4SS exports
    ?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAFXZ   (short&, 'F')
The two decorated names differ by exactly ONE byte (H=0x48 -> F=0x46) at the same
length, so we can repoint the import in place without touching the PE layout.

>>> THIS IS EXPERIMENTAL AND MUST BE LOAD-TESTED IN-GAME. <<<
main.dll's compiled code dereferences the returned reference as a 4-byte int; the
underlying engine field is small and little-endian, so this *should* read the right
alignment, but that depends on UStruct::MinAlignment's real width/layout in the
target engine build. If the game crashes or rows misbehave, revert to the original
DLL. The correct long-term fix is a recompile (see mod/rebuild-recipe.md).

Usage:
  python tools/patch-main-dll.py <in main.dll> <out main.patched.dll>
"""
from __future__ import annotations
import shutil, sys

OLD = b"?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ"   # int&  (what main.dll imports)
NEW = b"?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAFXZ"   # short& (what UE4SS now exports)


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    src, dst = argv
    data = bytearray(open(src, "rb").read())

    assert len(OLD) == len(NEW), "same-length replacement required"
    n = data.count(OLD)
    if n == 0:
        print(f"error: import symbol not found in {src}. Already patched, or wrong DLL?")
        return 1
    if n != 1:
        print(f"error: expected exactly 1 occurrence of the symbol, found {n}. Aborting for safety.")
        return 1
    # Confirm the diff is a single byte (sanity).
    diffs = [i for i, (a, b) in enumerate(zip(OLD, NEW)) if a != b]
    assert diffs == [len(OLD) - 3], f"unexpected diff position {diffs}"  # the 'H'/'F' before 'XZ'

    idx = data.find(OLD)
    data[idx:idx + len(OLD)] = NEW
    shutil.copystat  # noqa: B018  (no-op ref; we write fresh bytes below)
    open(dst, "wb").write(data)
    print(f"patched 1 import at offset 0x{idx:X} ('H'->'F')")
    print(f"  {OLD.decode()}")
    print(f"  {NEW.decode()}")
    print(f"wrote {dst}")
    print("NEXT: verify with `python tools/abi-diff.py <dst> <UE4SS.dll>` (expect MISSING: 0),")
    print("      then BACK UP the original and load-test the patched DLL in-game.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
