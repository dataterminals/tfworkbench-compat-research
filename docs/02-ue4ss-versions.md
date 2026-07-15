# 02 — UE4SS versions & the changes that matter here

Machine-readable: [`data/ue4ss-timeline.json`](../data/ue4ss-timeline.json).
Source of record: the single rolling
[`experimental-latest`](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental-latest)
prerelease.

## The core fact: there is no stable UE4SS after 3.0.1

> **Verified:** RE-UE4SS has shipped **no stable release since v3.0.1
> (2024-02-14)**. The only "latest" is a **single rolling `experimental-latest`
> prerelease** — the unreleased **v4.0.0-rc1** line — whose assets are
> **force-updated continuously**. That is *why* "the latest ue4ss version" is a
> moving target with no version-number change: users grab a fresh CI zip and the
> ABI has silently moved.

### git-describe versioning explains the "3.0.1" confusion

Experimental builds are versioned by **git-describe**: `v3.0.1-<commits-since-tag>-g<hash>`.
So a build can *report* "v3.0.1-1011-gb50986bd" and look like 3.0.1 while actually
being **1011 commits into the v4.0.0-rc line**. The v3.0.1 **tag** (commit `d935b5b`)
is just the anchor the count is measured from.

- **Current rolling asset (2026-07-13):** `UE4SS_v3.0.1-1011-gb50986bd.zip`
  (`main` is 1011 commits ahead of the v3.0.1 tag).
- **The local install (2026-07-12):** same `experimental-latest` channel, ~1–2
  commits earlier — see
  [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md).

## Timeline (verified)

| Build / change | Date | Relevance |
| --- | --- | --- |
| **v3.0.1** (last stable, `d935b5b`) | 2024-02-14 | anchor tag for all git-describe strings |
| UE 5.4 support (PR #503, `03f3fb6`) | 2024-05-17 | covers TFW 5.4.2 → **rules out an engine-support gap** |
| `ue4ss/` dir restructure (PR #506) | 2024-05-29 | adds the `ModsFolderPaths`/`ControllingModsTxt` keys seen locally; back-compat; not the breaker |
| `experimental-latest` channel created | 2024-12-29 | the rolling prerelease; force-updated ever since |
| **FName default flip** `FNAME_Find`→`FNAME_Add` (PR #994, `d876a82`) | 2025-09-03 | breaking C++ change — **RED HERRING here** (see below) |
| **xmake→CMake migration** (PR #1067) | 2025-11-11 | changelog: *"cannot guarantee ABI compatability"* — **the ABI-instability enabler** |
| `TObjectPtr<>` reworked as real smart pointer (PR #850) | v4.0.0-rc | breaking; on the mod's surface via `GetRowStruct()` — secondary suspect |
| **experimental v3.0.1-848-g91b70e5** | 2026-01-12 | **verified good (ABI)**; ships in ConstructionVendor easy-install → explains the Nexus floor *"-848 or higher"* (whose "or higher" half is now **stale**) |
| **experimental v3.0.1-894-g2172883** (`21728830…`) | 2026-01-28 | ⭐ **RECOMMENDED PIN** — verified good with **in-game proof**; pins UEPseudo `2d115713`, the last pointer still exporting the `int32&` symbol |
| **UVTD overhaul** (35 commits, incl. `2313a76620` vtable/macrosetter template regen) | 2026-01-28 → 30 | the **mechanism**: regenerating the Unreal layer emits versioned `GetMinAlignment506`/`GetMinAlignmentBase` and narrows `GetMinAlignment` to `int16&` |
| **v3.0.1-929-gcd556d70** — 🔥 **THE FIRST BREAKING BUILD** | **2026-01-30** | **BISECTED.** *"chore: update UE submodule for FUObjectArray changes"* — touches **only** `deps/first/Unreal`, bumping UEPseudo `2d115713`→`3a756005`. The **only** submodule-touching commit in `21728830…cd556d70` (35 commits), so builds `895`–`928` are still good. `GetMinAlignment` is in **no** commit message → collateral damage |
| current rolling v3.0.1-**998 … -1011** | 2026-06-29 → 07-13 | **all broken and all identical** for this purpose — every one pins UEPseudo `b2e876da`, so downgrading *within* this range is useless |

## The change that actually matters: **C++ ABI**, not FName

The breaker for TFWWorkbench is **C++ mod ABI drift**, not any single documented
behavior change. The chain:

1. TFWWorkbench ships a **precompiled `main.dll`** ([`03-tfworkbench.md`](03-tfworkbench.md)).
2. The xmake→CMake migration + ongoing refactors (`v4.0.0-rc`) change the exported
   C++ symbol set / signatures — UE4SS says ABI is not guaranteed.
3. A build ~160 commits past the mod's baseline no longer exports a symbol the mod
   imports → the loader aborts with `0x7F ERROR_PROC_NOT_FOUND`
   ([`04-the-breakage.md`](04-the-breakage.md)).

### Ruled out (with reasons)

- **FName default flip (`FNAME_Find`→`FNAME_Add`, PR #994).** ❌ The mod passes
  `FNAME_Add` **explicitly**, and a C++ default argument is resolved at the call
  site — it is **not part of the mangled symbol name** — so it cannot break
  linkage. Verification also **refuted** the claim that PR #994 changed the Lua
  `FName()` global default (Lua was already `FNAME_Add`).
- **FName alignment 8→4.** ❌ Scoped to the `LessEqual421` build definition
  (UE ≤ 4.21); TFW is UE5.4.2.
- **Engine-version support gap.** ❌ UE5.4 supported since May 2024; 5.5/5.6
  (PR #977)/5.7 too.

## Identifying an unlabeled build

Experimental `UE4SS.dll` files carry no version metadata. Identify by:
- **`UE4SS.dll` SHA-256** (the stable key used in [`data/compat.json`](../data/compat.json));
- the **`UE4SS.log` banner** after one launch — prints the git-describe version;
- the settings.ini key set (the `[Overrides]` keys are v4.0.0-rc-era).
