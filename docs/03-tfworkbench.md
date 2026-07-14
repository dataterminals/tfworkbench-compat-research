# 03 — TFWWorkbench: what it is and why its ABI is fragile

**Repos:** [github.com/smotti/TFWWorkbench](https://github.com/smotti/TFWWorkbench)
(the release/container) + [github.com/smotti/TFWWorkbench-Cpp](https://github.com/smotti/TFWWorkbench-Cpp)
(the C++ source, wired in as a git submodule) · **Latest:** v0.2.1 (2026-01-20) ·
**First release:** v0.1.0 (2026-01-14) · **Author/maintainer:** **smotti** (GitHub
repo owner).

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

> **Inferred (medium confidence):** `main.dll` was compiled against a **~January
> 2026 experimental UE4SS build, around `v3.0.1-848/-849`**. TFWWorkbench-Cpp was
> last pushed **2026-01-20** (v0.2.1 release day) and has **not been rebuilt
> since**, so no `main.dll` exists for any post-Jan-2026 UE4SS ABI. The exact SDK
> commit smotti built against is **not pinned anywhere in the repo** (CMake just
> links the local UE4SS target) — `-848` is a community-stated floor (a *dependent*
> mod's Nexus page — "Construction Vendor", mod 77 — states *"UE4SS MUST BE VERSION
> v3.0.1-848 OR HIGHER"*), not a build-verified match.

The breakage mechanism and the fix follow in
[`04-the-breakage.md`](04-the-breakage.md) and
[`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md).
