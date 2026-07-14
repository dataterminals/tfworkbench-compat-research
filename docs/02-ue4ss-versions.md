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
| **experimental v3.0.1-848 / -849** (`91b70e5…` / `486806a…`) | 2026-01-11 / 16 | **recommended pin**; Nexus floor; inferred ABI baseline for the mod |
| current `experimental-latest` ~v3.0.1-1011-gb50986bd | 2026-07-13 | ~160 commits of C++ ABI drift past the mod's build → **breaks it** |

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
