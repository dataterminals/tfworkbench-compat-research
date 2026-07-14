# 04 — The breakage: root-cause analysis

> **Status: PROVEN (2026-07-14) at the symbol level.** A static import/export diff
> of the two DLLs shows `main.dll` imports **81** UE4SS symbols, **80 resolve**
> against the current UE4SS.dll, and **exactly one does not**:
> `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ` (`UStruct::GetMinAlignment() ->
> int&`). UE4SS narrowed that method's return from `int32&` to `int16&`, so the
> import can't bind → guaranteed `0x7F ERROR_PROC_NOT_FOUND`. This is a deterministic
> loader outcome. Full analysis + reproduction:
> [`local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md)
> (`python tools/abi-diff.py <main.dll> <UE4SS.dll>`).

## TL;DR

TFWWorkbench ships a **precompiled C++ `main.dll`** ([`03-tfworkbench.md`](03-tfworkbench.md))
ABI-locked to the UE4SS SDK it was built against (~Jan 2026, `v3.0.1-848/-849`).
UE4SS has no stable release since 3.0.1 and force-rolls an experimental build whose
own changelog says it *"cannot guarantee ABI compatability."* A current build
(~`v3.0.1-1011`, ~160 commits later) no longer exports a symbol the DLL imports, so
the Windows loader aborts the load with **`[0x7f] The specified procedure could not
be found` (ERROR_PROC_NOT_FOUND)**.

## Candidate root causes (ranked)

### H1 — C++ mod ABI mismatch  ·  **CONFIRMED (proven)**  ·  PRIMARY
UE4SS re-signatured an exported C++ symbol that `main.dll` imports by decorated name
→ the loader can't resolve the import → the DLL never loads.
- **The exact break:** `UStruct::GetMinAlignment()` had its return type narrowed
  `int32&` → `int16&`. `main.dll` (v0.2.1) imports the `int32&` mangling
  `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ`, which the current UE4SS.dll no
  longer exports (it exports the `int16&` variant `…AEAFXZ` and a renamed private
  `GetMinAlignmentBase` `…AEAHXZ`).
- **Symptom:** clean **non-load** with `0x7F ERROR_PROC_NOT_FOUND`; UE4SS.log shows
  `Failed to load dll …main.dll… error: [0x7f]`.
- **Proof:** static import/export diff — 81 UE4SS imports, 80 resolve, 1 missing (the
  symbol above). A single unresolved import deterministically fails the load. Fully
  reproducible from the two DLLs:
  [`local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md).
- **Corroboration:** TFWWorkbench issues [#2](https://github.com/smotti/TFWWorkbench/issues/2)
  (OPEN) / [#1](https://github.com/smotti/TFWWorkbench/issues/1) show the exact 0x7F;
  upstream RE-UE4SS [#696](https://github.com/UE4SS-RE/RE-UE4SS/issues/696): 0x7F ==
  C++ mod ABI incompatibility; xmake→CMake (PR #1067) *"cannot guarantee ABI compatability."*
- **Residual caveat:** the analysis proves *this build cannot load this mod*. That the
  broader community complaint is the same symbol (vs a different newer build) is
  extremely likely but not separately version-stamped in any issue.

### H2 — Struct/layout drift (loads, then crashes)  ·  likelihood: MEDIUM  ·  SECONDARY
If the imports still resolve but a consumed UE object layout changed, `main.dll`
loads and then reads wrong offsets → access violation at apply time.
- **Prime candidate:** `TObjectPtr<>` reworked into a real smart pointer (PR #850);
  the mod consumes `UDataTable::GetRowStruct()` returning `TObjectPtr<UScriptStruct>&`
  and implicitly converts to `UScriptStruct*`. If names stay stable but size/repr
  or `UScriptStruct`/`UDataTable` layout changes, it mis-reads.
- **Symptom:** crash **during `AddDataTableRow`**, not a clean 0x7F non-load —
  that's how to tell H2 from H1.

### H3 — User installation error (confound)  ·  likelihood: MEDIUM
0x7F is not *by itself* diagnostic of an ABI break.
- **Evidence:** issue #1 (2026-03-15) had a byte-identical 0x7F and was **closed by
  the reporter as "user error — incorrect install."** Issue #2 references #1 as "the
  same problem." So the issue threads alone can't fully separate an ABI break from a
  bad install. This is the main reason the synthesis is *well-supported*, not *proven*.

### H4 — patternsleuth/AOB resolver failure  ·  likelihood: LOW
A resolver miss on TFW's exact UE5.4.2 could null out `StaticFindObject` and break
DataTable lookups — but that would break **every** UE4SS mod on TFW, whereas the
complaint singles out TFWWorkbench and other mods run fine. Keep only as an alternate.

### Ruled out
- **FName default flip `FNAME_Find`→`FNAME_Add` (PR #994).** ❌ Mod passes
  `FNAME_Add` explicitly; a C++ default arg is not part of the mangled symbol, so it
  can't break linkage. (This was the original leading hypothesis — **refuted by
  verification.**) The Lua-default sub-claim was also refuted (Lua was already `FNAME_Add`).
- **FName alignment 8→4** (UE ≤ 4.21 only) and **engine-support gap** (UE5.4
  supported since May 2024). ❌

## Evidence board

| Signal | Source | Supports | Status |
| --- | --- | --- | --- |
| Mod ships precompiled `main.dll` (219,136 B), links UE4SS | TFWWorkbench-Cpp | H1/H2 | Verified |
| No stable UE4SS since 3.0.1; force-rolled experimental | GitHub releases/tags | H1 | Verified |
| xmake→CMake "cannot guarantee ABI compatability" | Changelog (PR #1067) | H1 | Verified |
| Issue #2 OPEN: 0x7F main.dll load failure on v0.2.1 | TFWWorkbench #2 | H1 | Verified (reported) |
| Issue #1 closed as user install error | TFWWorkbench #1 | H3 | Verified (reported) |
| Upstream #696: 0x7F == C++ mod ABI incompatibility | RE-UE4SS #696 | H1 | Verified |
| `TObjectPtr<>` smart-pointer rework | Changelog (PR #850) | H2 | Verified (change exists) |
| FName flip cannot affect linkage | mangling analysis + PR #994 | ruled out | Verified |
| Reporter's UE4SS build in any issue | — | direction | **missing** (open) |

## Deciding H1 vs H2 vs H3 first-hand

Read `…\ue4ss\UE4SS.log` after one launch (see [`meta/next-session.md`](../meta/next-session.md)):
- **`Failed to load dll …main.dll… error: [0x7f]`** → H1 (ABI non-load). ✅ expected
- **Lua `attempt to call a nil value (AddDataTableRow/ConfigureDataTables)`** → the
  C++ functions never registered (a softer form of H1).
- **Crash / access violation during apply** → H2 (layout drift).
- **`DataTable not found` for *all* tables** → H4 (resolver).
- **Mod not even attempted / mis-placed** → H3 (install).

The confirmed cause drives the fix in
[`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md). Note H1's fix
(recompile `main.dll`) is **not** something a Lua shim can do — see the mod pillar.
