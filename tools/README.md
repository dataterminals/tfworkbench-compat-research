# tools/

## compat.py — query the compatibility matrix

Stdlib-only Python (3.8+). Reads [`../data/compat.json`](../data/compat.json).
No install, no dependencies.

```bash
python tools/compat.py list                 # every tracked (UE4SS x TFWWorkbench) combo
python tools/compat.py list --status broken # filter by status
python tools/compat.py check --sha a79b894d # identify a UE4SS.dll by SHA-256 (prefix ok)
python tools/compat.py check --build patternsleuth
python tools/compat.py pin                  # the recommended build to install (best 'works')
python tools/compat.py summary              # counts by status
python tools/compat.py validate             # structural check of compat.json vs the schema
```

### Getting your UE4SS.dll hash

```bash
# Git Bash / Linux / macOS
sha256sum ".../Binaries/Win64/ue4ss/UE4SS.dll"
```
```powershell
# PowerShell
Get-FileHash ".../Binaries/Win64/ue4ss/UE4SS.dll" -Algorithm SHA256
```
Then `python tools/compat.py check --sha <hash>`.

### Exit codes
- `0` success / found
- `1` validation failed
- `2` no match (build untracked, or no confirmed pin yet)

### Why SHA-256 as the key
UE4SS experimental CI builds carry **no version metadata**, so the `UE4SS.dll`
SHA-256 is the only stable identifier. Every `compat.json` entry records it when
known — see [`../docs/02-ue4ss-versions.md`](../docs/02-ue4ss-versions.md).

## abi-diff.py — prove/disprove a C++ mod ABI break

Diffs a precompiled UE4SS C++ mod's imports against an installed UE4SS.dll's exports
and names any missing symbol (the cause of a `0x7F ERROR_PROC_NOT_FOUND` load
failure). Needs `pip install pefile`.

```bash
python tools/abi-diff.py <mod_main.dll> <path/to/ue4ss/UE4SS.dll>
```

Exit `0` = every import resolves (ABI-compatible); `1` = missing symbol(s) listed;
`2` = error. Used to prove the TFWWorkbench break — see
[`../local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md).
This is the fastest way to test whether a given UE4SS build will load a given mod
DLL **without launching the game**.
