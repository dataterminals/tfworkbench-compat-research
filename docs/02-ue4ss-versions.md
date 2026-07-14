# 02 — UE4SS versions & the changes that endanger a DataTable mod

Machine-readable version of this timeline: [`data/ue4ss-timeline.json`](../data/ue4ss-timeline.json).
Source of record: <https://github.com/UE4SS-RE/RE-UE4SS/releases>.

## The key mental model: TFW rides the *experimental* channel

UE4SS ships two ways:
- **Stable releases** — numbered (…, 3.0.0, 3.0.1, …).
- **Experimental / `experimental-latest`** — rolling CI builds off the dev branch,
  on the modern **patternsleuth** resolver engine.

Because **The Forever Winter is UE 5.4.2**, and stable **3.0.1 (Feb 2024) predates
UE5.4 support**, TFW users run an **experimental build**. That's the channel that
changes without a version bump — and the channel terraru's "latest" refers to.

> **Verified (local binary scan):** the installed TFW UE4SS is a patternsleuth CI
> build (path `D:\a\RE-UE4SS\RE-UE4SS\deps\first\patternsleuth\…` embedded in
> `UE4SS.dll`), with new-era settings keys (`ModsFolderPaths`, `ControllingModsTxt`,
> `Experimental_ShouldPreDuplicateMap`). See
> [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md).

## Timeline (seed — extended by the research workflow)

| Build | Channel | Date | Danger to a DataTable mod |
| --- | --- | --- | --- |
| 3.0.0 | stable | 2024-02-04 | **HIGH** — `FName` ctor default `FNAME_Find` → `FNAME_Add`; new `dwmapi.dll` proxy; `ue4ss/` subfolder layout |
| 3.0.1 | stable | 2024-02-14 | low — patch; predates UE5.4 (not used by TFW) |
| experimental (patternsleuth, rolling) | experimental | 2024–2026 | **the suspect range** — resolver/engine-offset churn; the build that breaks TFWWorkbench lives here |

> ⏳ **Pending research (workflow `wu3yvil3x`):** extend this table through July
> 2026 — any 3.1.x/3.2.x stable, the UE5.4-support introduction point, and the
> specific experimental build/commit that first breaks TFWWorkbench. Rows will be
> promoted from ⏳ to **Verified** with primary-source citations as they land.

## Changes that specifically endanger a runtime DataTable editor

Ranked by how directly they hit TFWWorkbench's surface
([`03-tfworkbench.md`](03-tfworkbench.md)):

1. **`FName` constructor default `FNAME_Find` → `FNAME_Add` (3.0.0).**
   DataTable rows are keyed by `FName`. If code that meant "find this existing
   name" now *adds* a name instead, row lookups can miss or mis-key. **Top suspect.**
2. **`FName` alignment 8 → 4** (a `LessEqual421` build definition). Layout-sensitive
   code reading `FName` fields can mis-read on a mismatched build.
3. **patternsleuth resolver changes** to `StaticConstructObjectInternal`,
   `StaticFindObject`, `GUObjectArray`, `FUObjectHashTables`, `fname` resolvers. If
   a resolver mis-fires on UE5.4.2, object lookup or iteration breaks → tables not
   found. (These resolver names are literally present in the local `UE4SS.dll`.)
4. **UE5.4-specific engine offsets / struct layout** drift between the build
   TFWWorkbench was authored against and "latest."
5. **Lua API/behavior changes** — `FindObject`/`StaticFindObject` semantics,
   `ObjectProperty = nil` support, `IsValid()` now accounting for reachability.

Each of these is evaluated against actual symptoms in
[`04-the-breakage.md`](04-the-breakage.md).

## How to identify an unlabeled build

Experimental `UE4SS.dll` files carry **no version metadata**. Identify them by:
- **SHA-256 of `UE4SS.dll`** (the stable identifier this repo uses — see
  [`data/compat.json`](../data/compat.json)),
- the `UE4SS.log` startup banner (prints version/commit) once the game has run,
- settings.ini key set (new keys appear over time).
