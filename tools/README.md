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
