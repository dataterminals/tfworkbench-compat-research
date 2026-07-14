# dist/ — the experimental patched `main.dll`

`main.patched.dll` is **not committed** (binaries are gitignored). Regenerate it any
time from the official TFWWorkbench v0.2.1 release:

```bash
python tools/patch-main-dll.py <TFWWorkbench v0.2.1>/dlls/main.dll dist/main.patched.dll
python tools/abi-diff.py dist/main.patched.dll "<game>/Binaries/Win64/ue4ss/UE4SS.dll"
# expect: MISSING: 0
```

## What it is

TFWWorkbench v0.2.1's `main.dll` with **one byte changed** (offset `0x301D3`,
`H`→`F`) so its `UStruct::GetMinAlignment` import points at the surviving `int16&`
export instead of the removed `int32&` one. See
[`../local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md).

- Original SHA-256: `24b05dc267dc6e9faa6cbcb4e85a8491733e0a86b86fbac92f5aa1a0950aa6ca`
- Patched  SHA-256: `a7a5b5f38b1cbf4a239e9df05d14e4b408f69b4d528855dc00e0902b2917bbd8`
- **ABI check:** 81 imports, **81 resolved, 0 missing** → it will load (no `0x7F`).

## ⚠️ This is experimental — load-test it, don't trust it blindly

The ABI check only proves the DLL will **load**. It does not prove the alignment
value is read correctly at runtime (the old code reads the reference as a 4-byte
`int`; the export is now `int16&`). Alignments are tiny and the engine field is
little-endian, so it *should* be fine — but that must be confirmed in-game.

## How to test

1. **Install TFWWorkbench v0.2.1 normally** and confirm it currently fails
   (`UE4SS.log` shows `Failed to load dll …main.dll… error: [0x7f]`).
2. **Back up** the original `…\ue4ss\Mods\TFWWorkbench\dlls\main.dll`.
3. Replace it with `main.patched.dll` (rename to `main.dll`).
4. Launch the game once. In `UE4SS.log`, confirm:
   - **no `0x7f`** / "Failed to load dll" for `main.dll`;
   - TFWWorkbench initializes and `AddDataTableRow` / `ConfigureDataTables` register
     (the [`TFWWorkbenchDoctor`](../mod/TFWWorkbenchDoctor) mod reports this).
5. **The real test:** load a TFWWorkbench-dependent content mod and verify its
   DataTable edits actually apply in-game (items/recipes/vendor entries appear and
   are correct). This is what would expose a bad alignment read.
6. If anything crashes or looks wrong, **restore the backup**. The correct
   permanent fix is a recompile (see [`../mod/rebuild-recipe.md`](../mod/rebuild-recipe.md)).

If it works, please report back on
[TFWWorkbench issue #2](https://github.com/smotti/TFWWorkbench/issues/2) so others benefit.
