# 03 — TFWWorkbench: what it does and the UE4SS surface it depends on

**Repo:** [github.com/smotti/TFWWorkbench](https://github.com/smotti/TFWWorkbench)
(note the double-W in the repo name) · **Latest release:** v0.2.1 (2026-01-20) ·
**TFW Nexus:** mod 77.

## What it is

TFWWorkbench is a **runtime DataTable editor** for The Forever Winter, delivered as
a UE4SS mod. Instead of a content mod shipping a whole replaced asset (which
conflicts with every other mod that touches the same asset), a mod ships a small
**JSON patch**, and TFWWorkbench applies it to the live DataTable at runtime.

> **Its stated purpose (from the README):** *"Mods that modify the same static
> assets are most often incompatible with each other."* TFWWorkbench mitigates
> that by applying dynamic, additive modifications from JSON.

## The DataTables it operates on

| Game DataTable | Workbench concept |
| --- | --- |
| `DT_ManufactoringGroups` | CraftingGroups |
| `DT_ManufactoringRecipies` | CraftingRecipes |
| `InventoryItemDetailsData` | Item |
| Value DataTables | ItemValue |
| `VendorDataTable` | VendorData |
| `WeaponPartsStatsData` | (weapon part stats) |
| `WeaponsDetailsData` | (weapon details) |

## Install shape

Per the README:
1. Extract to `Binaries\Win64\ue4ss\Mods` (the UE4SS script side).
2. Add `TFWWorkbench : 1` to `mods.txt`.
3. Create `Content\Paks\Mods\TFWWorkbench` (the data side).
4. Drop per-mod JSON into the example folders.

So it has **both** a UE4SS-mod half (the code that does the patching) and a
content-pak half (where JSON patches live).

## The UE4SS surface it depends on — i.e. what a UE4SS change can break

> **This is the crux of the whole investigation.** A runtime DataTable editor is
> unusually exposed to UE4SS internals. Everything below is the API surface whose
> behavior TFWWorkbench assumes; [`04-the-breakage.md`](04-the-breakage.md) maps
> UE4SS changes onto these.

A DataTable editor of this kind must, at minimum:

1. **Locate the DataTable objects** — typically via UE4SS Lua
   `StaticFindObject` / `FindObject` / `FindFirstOf`, keyed by object name/path.
   → Breaks if UE4SS changes how object lookup resolves, or how it scans
   `GUObjectArray` / the UObject hash tables.
2. **Resolve row keys, which are `FName`s** — DataTable rows are keyed by `FName`.
   Constructing or comparing an `FName` for a row name is central.
   → Breaks if the `FName` constructor's default behavior changes (e.g. the 3.0.0
   `FNAME_Find` → `FNAME_Add` flip) or if `FName` memory layout/alignment changes.
3. **Read/write row struct fields** — reflect over the row `UScriptStruct` and set
   properties (ints/floats/names/object refs).
   → Breaks if property iteration, `ObjectProperty` handling, or struct offsets
   shift (engine-version- or resolver-dependent).
4. **Hook a safe apply point** — run *after* the tables exist but before/around
   first use (often a load or post-init hook, or `RegisterHook`/`NotifyOnNewObject`).
   → Breaks if hook/callback timing or registration semantics change.

> **Verified:** the *categories* above are how UE4SS DataTable mods generally work
> and match TFWWorkbench's described behavior.
> **Inferred (pending source read):** the *exact* UE4SS calls TFWWorkbench uses
> (Lua vs C++, which functions) — to be confirmed by reading the TFWWorkbench
> source and pinned in [`04-the-breakage.md`](04-the-breakage.md). The research
> workflow is auditing the repo (source, releases, and issues) for this.

## Version facts to nail down

- Which UE4SS build was v0.2.1 authored/tested against? (README states no min/max
  version — a gap this repo aims to fill.)
- Do TFWWorkbench issues/PRs mention "stopped working after updating UE4SS"?
- Is there a smotti (or community) build that already works with newer UE4SS?

These feed [`data/compat.json`](../data/compat.json).
