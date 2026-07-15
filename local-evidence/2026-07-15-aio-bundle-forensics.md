# 2026-07-15 — Forensics on three redistributed TFW mod bundles

**Question asked (modding chat):** *"What versions of UE4SS/TFWWorkbench are we
supposed to be using? Is the Construction-Vendor-derived AIO packet functional?"*

**Answer:** the AIO packets are **stock upstream artifacts, byte-for-byte**. The
dispute between them is **not** an ABI break, a crash, or the game version — it is a
**TFWWorkbench version gap that fails silently**.

## Artifacts examined

| Bundle | Source file |
| --- | --- |
| **A** — the Codex AIO bundle | `<Codex AIO bundle zip (community-distributed)>` |
| **C** — the standalone Codex Vendor mod | `<standalone Codex Vendor mod zip>` |
| **B** — Construction Vendor easy-install | `ConstructionVendor_easyinstall_0.9.1.3.rar` |

Community context: Modder B's "AIO packet" is **B with the CV mod stripped out**. Modder A
reported it *"incompatible with my mod / version of TFWWorkbench."* This session
establishes why.

## Verified: both bundles ship unmodified upstream builds

> **Verified (byte-identical, downloaded and hashed 2026-07-15).**

| | TFWWorkbench | `main.lua` SHA-256 | UE4SS | `UE4SS.dll` SHA-256 |
| --- | --- | --- | --- | --- |
| **Bundle A** | **0.2.1** | `2230fa8c…` | **v3.0.1-894-g2172883** (2026-01-28) | `678d8b02…` (15,801,856 B) |
| **Bundle B** | **0.1.2** | `afe9a5b2…` | **v3.0.1-848-g91b70e5** (2026-01-12) | `c81d29ed…` (15,467,520 B) |

- Bundle A's `UE4SS.dll` == the DLL inside official
  `UE4SS_v3.0.1-894-g2172883.zip` (6,878,895 B), **hash-for-hash**.
- Bundle B's `UE4SS.dll` == the DLL inside official
  `UE4SS_v3.0.1-848-g91b70e5.zip`, **hash-for-hash**.
- Bundle A's `Scripts/main.lua` == TFWWorkbench release **0.2.1**; `main.dll`
  `24b05dc2…` (219,136 B) == 0.2.1's.
- Bundle B's `Scripts/main.lua` == TFWWorkbench release **0.1.2**; `main.dll`
  `825ba834…` (223,744 B) == 0.1.0–0.2.0's (identical across those four).
- Bundle C's `001_CodexPatch.json` is **byte-identical** to Bundle A's
  (`1654f5b7f3cb…`) — A genuinely bundles C's payload, plus two more patches
  (`002_CraftingMaterialsPatch.json`, `003_HKSandDiverPach.json`).

Nobody hand-patched anything. This is stock upstream software, repackaged.

## Verified: the full TFWWorkbench release map

`smotti/TFWWorkbench` has **exactly 5 releases, all January 2026**. **0.2.1
(2026-01-20) is the latest — nothing has shipped since.** Fingerprints from the
release zips:

| Release | Date | JSON `Action`s handled | `SourceRow` | `DataTableRowData.lua` | `main.dll` |
| --- | --- | --- | --- | --- | --- |
| 0.1.0 | 2026-01-14 | Add / **Modify** / Remove | 5 | ✗ | `825ba834` (223,744) |
| 0.1.1 | 2026-01-15 | Add / **Modify** / Remove | 5 | ✗ | `825ba834` |
| 0.1.2 | 2026-01-16 | Add / **Replace** / Remove | 5 | ✗ | `825ba834` |
| 0.2.0 | 2026-01-20 | + **AddTo / ModifyIn / RemoveFrom** | 5 | ✓ | `825ba834` |
| **0.2.1** | 2026-01-20 | Add/AddTo/ModifyIn/Remove/RemoveFrom/Replace | **0** | ✓ | **`24b05dc2`** (219,136) |

Notes: `Modify` was renamed → `Replace` in **0.1.2**. **`AddTo` arrived in 0.2.0.**
Only **0.2.1** rebuilt `main.dll` and dropped the `SourceRow` template requirement.

## The actual finding: `AddTo` fails **silently** on 0.1.x

Every Modder A Codex JSON uses **`"Action": "AddTo"` exclusively** (all three
files, verified by scan). Bundle B / Modder B's packet ships **0.1.2**, whose
`CollectData` dispatch is:

```lua
if     element["Action"] == "Add"     then …
elseif element["Action"] == "Replace" then …
elseif element["Action"] == "Remove"  then …
end          -- <-- no else branch
```

> **Verified:** there is **no `else`**. An `AddTo` element matches nothing and is
> dropped — **no error, no crash, not even a log line**. Additionally, 0.1.2's
> VendorData apply loop only ever consumes `.Replace`; there is no `AddTo` path at
> all. Result: a **total silent no-op**.

That is exactly why users "complain it doesn't work" rather than reporting an error.
0.2.1 handles it at `main.lua:593` via `DataTableHandlers.VendorData.RowData:AddTo(…)`.

## The halves are a matched pair — don't mix them

Dropping 0.2.1's Lua onto 0.1.2's `main.dll` will **not** work:
- `AddTo` needs `DataTableRowData.lua`, absent in 0.1.x.
- The Lua↔DLL contract changed: 0.1.x calls
  `ConfigureDataTables(name, path, sourceRow)`; 0.2.1 calls
  `ConfigureDataTables(name, path)`.

## Verified: this is NOT the ABI break

`tools/abi-diff.py` across all four DLL combinations — **every one resolves 100%**:

| `main.dll` | `UE4SS.dll` | imports | missing |
| --- | --- | --- | --- |
| 0.2.1 (`24b05dc2`) | `-894` | 81 | **0** |
| 0.1.2 (`825ba834`) | `-848` | 83 | **0** |
| 0.2.1 (`24b05dc2`) | `-848` | 81 | **0** |
| 0.1.2 (`825ba834`) | `-894` | 83 | **0** |

Both shipped UE4SS builds **predate the narrowing** and still export
`?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ` (`int32&`). The local install
(`a79b894d`, `-1009`/`-1011`) exports only the `int16&` variant plus
`GetMinAlignment506` / `GetMinAlignmentBase` → `0x7F`.

**Consequence: 0.2.1 is not pinned to `-894`.** The entire pre-narrowing window is
ABI-good; `-894` is merely the newest build with first-hand runtime proof.

## Runtime proof that Bundle A works

Bundle A ships the packager's own `UE4SS.log` (2026-07-14, 7,096 lines):

```
UE4SS - v3.0.1 Beta #0 - Git SHA #2172883
Starting C++ mod 'TFWWorkbench'                       <- no 0x7F
[TFWWorkbench:main:CollectData] AddTo (Property) VendorData - Name: ScavSurplusVendor  File: 001_CodexPatch.json
[TFWWorkbench] Configuring DataTable: VendorData | /Game/Blueprints/Data/VendorDataTable.VendorDataTable
[TFWWorkbench] Map key: Codex.Grabber
[TFWWorkbecnh] Set FName property 'RowName' to value: Codex.Grabber
```

The whole chain lands. (`TFWWorkbecnh` is an upstream typo in `main.dll`.) Modder A's
claim that his AIO works is **first-hand confirmed**.

## Corrections this session forced

> ❌ **"The narrowing landed 2026-07-10..07-12."** **Wrong** — inferred from DLL
> mtimes, which in a redistributed bundle are **repack** times. Bundle A's
> `UE4SS.dll` is stamped 2026-07-10 but its log banner says `Git SHA #2172883` =
> commit `21728830cb49`, **2026-01-28** — and the byte hash proves the banner honest.
> **Real window:** UEPseudo `2d115713` (2026-01-28) → `b2e876da` (2026-06-25); one of
> **13** submodule bumps. **Never date a build from an mtime.**

> ❌ **"There is no tidy download for an old experimental build."** **Wrong** — the
> `experimental` tag is a permanent archive of **851** builds; both bundles' UE4SS
> versions downloaded cleanly today. See
> [`05-known-good-and-workarounds.md`](../docs/05-known-good-and-workarounds.md).

> ❌ **"TFWWorkbench has 2 releases (0.1.0, 0.2.1)."** **Wrong** — there are **5**.
> The missing 0.1.1 / 0.1.2 / 0.2.0 are exactly what pins Bundle B to **0.1.2** and
> dates `AddTo` to **0.2.0**.

> ❌ **"`-848/-849` is the recommended pin, confidence medium."** Superseded —
> `-894` is verified with runtime proof, and `-848` is verified ABI-only. The pin is
> a **window**, not a point.

## Verdict for the chat

- **Use TFWWorkbench 0.2.1 + UE4SS `v3.0.1-894-g2172883`** — i.e. exactly what
  Modder A's AIO already ships. It is stock upstream and provably works.
- **Modder B's packet is not "broken"** — it is a **Construction-Vendor-era stack**
  (0.1.2 + `-848`). It works for CV-era mods and **silently no-ops** for any mod
  built on `AddTo` (all Codex Vendor content).
- Both are internally consistent. Neither is infallible; they solve different eras.

## Reproduce

```powershell
python tools/abi-diff.py <bundle>/Mods/TFWWorkbench/dlls/main.dll <bundle>/ue4ss/UE4SS.dll
python tools/compat.py pin
# identify any bundle's TFWWorkbench release:
Get-FileHash <bundle>/Mods/TFWWorkbench/Scripts/main.lua -Algorithm SHA256   # 2230fa8c=0.2.1, afe9a5b2=0.1.2
# identify any UE4SS build (never trust mtime):
Select-String -Path <bundle>/ue4ss/UE4SS.log -Pattern 'Git SHA #'
```
