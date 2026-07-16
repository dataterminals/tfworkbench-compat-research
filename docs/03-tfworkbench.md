# 03 — TFWWorkbench: what it is and why its ABI is fragile

**Repos:** [github.com/smotti/TFWWorkbench](https://github.com/smotti/TFWWorkbench)
(the release/container) + [github.com/smotti/TFWWorkbench-Cpp](https://github.com/smotti/TFWWorkbench-Cpp)
(the C++ source, wired in as a git submodule) · **Latest:** v0.2.1 (2026-01-20) ·
**First release:** v0.1.0 (2026-01-14) · **Author/maintainer:** **smotti** (GitHub
repo owner).

## The release map (all 5)

> **Verified (2026-07-15):** the repo has **exactly 5 releases, all January 2026**.
> **0.2.1 is the latest — nothing has shipped since 2026-01-20.** Fingerprints below
> are from the release zips themselves; use them to identify any redistributed copy.

| Release | Date | JSON `Action`s handled | `SourceRow` | `DataTableRowData.lua` | `main.dll` | `main.lua` sha256 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.1.0 | 2026-01-14 | Add / **Modify** / Remove | 5 | ✗ | `825ba834` (223,744) | `33627f2f…` |
| 0.1.1 | 2026-01-15 | Add / **Modify** / Remove | 5 | ✗ | `825ba834` | `c1091659…` |
| 0.1.2 | 2026-01-16 | Add / **Replace** / Remove | 5 | ✗ | `825ba834` | `afe9a5b2…` |
| 0.2.0 | 2026-01-20 | + **AddTo / ModifyIn / RemoveFrom** | 5 | ✓ | `825ba834` | `7132c365…` |
| **0.2.1** | 2026-01-20 | Add/AddTo/ModifyIn/Remove/RemoveFrom/Replace | **0** | ✓ | **`24b05dc2`** (219,136) | `2230fa8c…` |

Key transitions: `Modify` → renamed `Replace` in **0.1.2**; **`AddTo` arrived in
0.2.0**; only **0.2.1** rebuilt `main.dll` and dropped the `SourceRow` requirement.
`main.dll` is **byte-identical across 0.1.0–0.2.0**, so the DLL alone cannot
distinguish them — hash `Scripts/main.lua` instead.

## The silent failure: JSON `Action`s are version-gated

> **Verified (2026-07-15) — this bites real users and produces NO error.**

A content mod's JSON declares an `Action`. 0.1.x's `CollectData` dispatch is a bare
`if/elseif` chain over `Add` / `Replace` / `Remove` with **no `else` branch**. An
unrecognized action — e.g. **`AddTo`**, which every Codex Vendor patch uses — matches
nothing and is **dropped without an error, a crash, or even a log line**. In 0.1.2 the
VendorData apply loop also only consumes `.Replace`, so there is no `AddTo` path at
all. The mod loads perfectly and does **nothing**.

**Diagnosing it:** if `UE4SS.log` shows the C++ half **loaded** (no `0x7F`) but no
`AddTo (Property) …` lines, your TFWWorkbench is **too old for the JSON you
installed** — that is a version gap, *not* the ABI break. Upgrade to **0.2.1**.

> **⚠️ Probe the load with `[TFWWorkbench] Registered Lua functions for mod`** — no `[Lua]`
> prefix ⇒ it is `main.dll`'s own output, so it cannot appear unless the DLL loaded.
> **Do not use `Starting C++ mod 'TFWWorkbench'`** (as this step did until 2026-07-16).
> That line is emitted only when the mod is started from **`mods.txt`**; an install that
> relies on the per-mod **`enabled.txt`** — the CV AIO's layout, and every MO2 install —
> logs `Mod 'TFWWorkbench' has enabled.txt, starting mod.` instead and never emits it, so
> the probe reads a **working** install as broken. See
> [`local-evidence/2026-07-16-stale-log-from-own-desktop/`](../local-evidence/2026-07-16-stale-log-from-own-desktop/NOTES.md).

**You cannot mix halves to fix it.** The Lua and `main.dll` are a **matched pair**:
`AddTo` calls `DataTableHandlers.<T>.RowData:AddTo(…)` from `DataTableRowData.lua`
(absent before 0.2.0), and the Lua↔DLL contract changed — 0.1.x calls
`ConfigureDataTables(name, path, sourceRow)`, 0.2.1 calls
`ConfigureDataTables(name, path)`. Install a release **whole**.

## It is a C++/Lua **hybrid**, not a Lua mod

> **Verified** (source + release inspection): TFWWorkbench is a hybrid UE4SS mod.
> This single fact reorganizes the whole diagnosis.

- A **C++ side** — `TFWWorkbench-Cpp/dllmain.cpp` subclasses `RC::CppUserModBase`
  and is compiled to a **precompiled `dlls/main.dll` (219,136 bytes)** shipped in
  the release zip. It imports concrete UE4SS C++ symbols and registers Lua
  functions (`AddDataTableRow`, `ConfigureDataTables`).
- A **Lua side** — the larger scripting layer that reads the per-mod JSON and calls
  into the C++ functions to apply DataTable edits.
- `TFWWorkbench-Cpp/CMakeLists.txt` does `add_library(... SHARED)` +
  `target_link_libraries(TFWWorkbench PUBLIC UE4SS)` — i.e. it **links against the
  UE4SS SDK** present at build time.

## Why that makes it fragile: C++ ABI locking

A precompiled C++ mod DLL imports UE4SS functions by their **name-mangled
(decorated) symbol** — e.g. `StaticFindObject`, the `FName` constructor,
`UDataTable::AddRow` / `FindRowUnchecked` / `GetRowStruct`, and the
`FProperty`/`CastField` reflection family. At load time the Windows loader must
resolve every imported symbol against the UE4SS DLL actually present.

> **If a newer UE4SS build renames, removes, re-signatures, or inlines even one of
> those exported symbols, the import can't be resolved and the loader aborts** —
> the mod's `main.dll` never loads. This is a pure **ABI mismatch**, independent of
> the mod's logic.

UE4SS is explicit that C++ mod ABI is **pinned per build**: see
[docs.ue4ss.com — installing a C++ mod](https://docs.ue4ss.com/dev/guides/installing-a-c++-mod.html).
And UE4SS's own changelog, on the xmake→CMake migration, states it *"cannot
guarantee ABI compatability"* — see [`02-ue4ss-versions.md`](02-ue4ss-versions.md).

## What it does (functionally)

A **runtime DataTable editor**: instead of each content mod shipping a conflicting
replaced asset, a mod ships a small **JSON patch** and TFWWorkbench applies it to
the live DataTable at runtime, so mods coexist. DataTables it targets:

| Game DataTable | Concept |
| --- | --- |
| `DT_ManufactoringGroups` | CraftingGroups |
| `DT_ManufactoringRecipies` | CraftingRecipes |
| `InventoryItemDetailsData` | Item |
| Value DataTables | ItemValue |
| `VendorDataTable` | VendorData |
| `WeaponPartsStatsData` / `WeaponsDetailsData` | weapon stats/details |

## Install shape

Per the README: extract to `Binaries\Win64\ue4ss\Mods`, add `TFWWorkbench : 1` to
`mods.txt`, create `Content\Paks\Mods\TFWWorkbench`, drop per-mod JSON in. The
`dlls/main.dll` inside the mod folder is the ABI-locked binary that must match your
UE4SS build.

## The ABI baseline (what it was built against)

> **Verified (2026-07-15):** 0.2.1's `main.dll` resolves **81/81** imports against
> **both** `v3.0.1-848-g91b70e5` (2026-01-12) and `v3.0.1-894-g2172883` (2026-01-28).
> So the ABI baseline is a **window**, not a single build: any pre-narrowing UE4SS
> works. TFWWorkbench-Cpp was last pushed **2026-01-20** (v0.2.1 release day) and has
> **not been rebuilt since**, so no `main.dll` exists for any post-narrowing UE4SS
> ABI. The exact SDK commit smotti built against is still **not pinned anywhere in
> the repo** (CMake just links the local UE4SS target).

> **Recommended pin: `-894`** — the newest build with first-hand runtime proof. The
> Nexus floor *"UE4SS MUST BE VERSION v3.0.1-848 OR HIGHER"* ([mod 77](https://www.nexusmods.com/theforeverwinter/mods/77))
> is now explained: Construction Vendor's easy-install ships **exactly `-848`**. Its
> **"OR HIGHER" half is stale and actively harmful** — builds from `-998` on are
> broken. See [`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md).

The breakage mechanism and the fix follow in
[`04-the-breakage.md`](04-the-breakage.md) and
[`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md).
