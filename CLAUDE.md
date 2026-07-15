# CLAUDE.md — orientation for AI agents

You are working in **tfworkbench-compat-research**. Read this before acting.

> **🎯 The mission, in one line:** find out **which RE-UE4SS build breaks
> TFWWorkbench on The Forever Winter, and why, then ship a fix.** Everything here
> serves that. Start with [`docs/00-overview.md`](docs/00-overview.md), then the
> latest entry in [`meta/research-log.md`](meta/research-log.md) and
> [`meta/next-session.md`](meta/next-session.md).
>
> ## ✅ ANSWERED (2026-07-15)
>
> **First breaking build: UE4SS `v3.0.1-929-gcd556d70`** (commit
> `cd556d706a680af35379913006153e9807aabf4a`, 2026-01-30, *"chore: update UE submodule
> for FUObjectArray changes"*). **Last good: `-894-g2172883`** (2026-01-28). Safe range
> **`-823`…`-928`**. The narrowing rode in on a **UVTD regeneration** — collateral
> damage, named in no commit message. **Use TFWWorkbench 0.2.1 + UE4SS `-894`**
> (`compat.py pin`). The *why* and *fix* pillars are still open (see below).

## What this repo is

A focused investigation + toolkit around one compatibility break. It has four
parts: a **docs** knowledge base, a **compat tracker** (`data/compat.json` +
`tools/compat.py`), a **fix pillar** (`mod/` — `rebuild-recipe.md` + the
`TFWWorkbenchDoctor` diagnostic mod), and **evidence** (`local-evidence/`, `seed/`).
There is a small Python CLI; otherwise it's documentation-first.

## The mental model (load this first)

- **The Forever Winter (TFW)** = Unreal Engine **5.4.2** game. Ships signed paks →
  needs a **Signature Bypass** (`dsound.dll` + `bitfix\`) for any mod to load.
- **RE-UE4SS** = the Lua/C++ scripting system injected via a proxy `dwmapi.dll`.
  For UE5.4 it's a **rolling experimental (patternsleuth) build**, not a numbered
  stable — so "latest" is a moving target with no clean version string.
- **TFWWorkbench** (smotti/TFWWorkbench, note double-W) = a **C++/Lua hybrid** UE4SS
  mod that edits Unreal **DataTables at runtime** from JSON. Its C++ half ships as a
  **precompiled `main.dll`** (219 KB). It's a **framework dependency** other mods
  rely on. It didn't change; UE4SS did — that's the whole problem. **5 releases, all
  Jan 2026; 0.2.1 is latest.** `main.dll` is byte-identical across 0.1.0–0.2.0 →
  identify a copy by hashing `Scripts/main.lua` (`2230fa8c…`=0.2.1, `afe9a5b2…`=0.1.2).
- **The break** = a **C++ mod ABI mismatch**: `main.dll` imports UE4SS symbols by
  decorated name; a newer UE4SS (no stable since v3.0.1; rolling experimental
  ~`v3.0.1-1011`) no longer exports one → Windows aborts the load with
  **`0x7F ERROR_PROC_NOT_FOUND`**. The `FName` flip is a **ruled-out red herring**.
  See [`docs/04-the-breakage.md`](docs/04-the-breakage.md).
- **Two failure modes, don't conflate them.** The ABI break is *loud* (`0x7F`, mod
  never loads). There is also a **silent** one: TFWWorkbench **0.1.x ignores unknown
  JSON `Action`s with no error at all** — a mod using `AddTo` (added in 0.2.0) simply
  does nothing. Mod loads + no `AddTo` lines in the log = **version gap, not ABI**.
  See [`docs/03-tfworkbench.md`](docs/03-tfworkbench.md).

## House style — non-negotiable

1. **Keep Verified vs. Inferred explicit.** Use `> **Verified:**` / `> **Inferred:**`
   callouts. Never silently promote a guess to a fact.
2. **Cite how you know** — GitHub release/commit/issue URL, binary scan, file
   listing, `UE4SS.log`, or community report. Mark community claims `reported`, not
   `verified`, until first-hand confirmed.
3. **Append provenance to [`meta/research-log.md`](meta/research-log.md)** whenever
   you learn something. Newest entry last.
4. **Do not invent version numbers, dates, commits, or hashes.** Unknown = say
   unknown. This whole repo exists because a specific version was *unknown*.
5. **The compat matrix has honest confidence levels.** When adding rows to
   `data/compat.json`, set `confidence` to `verified` only for first-hand tests;
   run `python tools/compat.py validate` after editing.

## Safety rules

- **Never modify the user's game install.** `D:\SteamLibrary\steamapps\common\The
  Forever Winter` is real game data. Read/inspect only; don't swap DLLs, edit
  `mods.txt`, or launch the game without explicit instruction.
- **No Lua "shim" can fix this.** The C++ `main.dll` fails to *load* before any Lua
  runs, so the fix is a **recompile** ([`mod/rebuild-recipe.md`](mod/rebuild-recipe.md))
  or a **UE4SS pin**, not Lua. [`mod/TFWWorkbenchDoctor`](mod/TFWWorkbenchDoctor) is a
  read-only **diagnostic** only — keep it read-only.
- **Identify builds by `UE4SS.dll` SHA-256**, since CI builds lack version metadata.
- **NEVER date a build from a file mtime.** In any redistributed bundle the DLL mtime
  is the **repacker's** timestamp, not the build date. A previous session dated the
  break to "2026-07-10..07-12" from mtimes and was wrong by ~5 months. Instead use:
  1. **PE `TimeDateStamp`** — the linker stamps it *inside* the DLL, so it survives
     repacking and is the **real build time**. This is the antidote to the mtime trap:
     ```python
     import pefile, datetime
     pe = pefile.PE(path, fast_load=True)
     print(datetime.datetime.utcfromtimestamp(pe.FILE_HEADER.TimeDateStamp))
     ```
     It proved TFWWorkbench 0.2.1's `main.dll` was compiled **2026-01-20 15:26:44 UTC**
     (1h before release) — which **excludes** any later UE4SS as its compile baseline.
  2. The `UE4SS.log` **`Git SHA #`** banner, or the **DLL SHA-256**.
- **Import/export diffing has a blind spot.** `abi-diff.py` proves *mangled symbols
  resolve*; it CANNOT see **struct/vtable layout drift** — offsets baked into a
  precompiled mod when a UEPseudo bump moves a type. So "81/81 resolve" means *will
  load*, not *is the baseline*. Prefer a pin whose UEPseudo pointer matches the one the
  mod was compiled against.
- **Pinned old UE4SS builds are easy to get:** the **`experimental`** release tag is a
  permanent archive of 851 builds. (`experimental-latest` is rolling — it wipes assets
  every build and can never serve a historical one.)

## Where to find authoritative facts

| Question | Look here |
| --- | --- |
| The whole problem, quick | [`docs/00-overview.md`](docs/00-overview.md) |
| How the stack fits together | [`docs/01-the-stack.md`](docs/01-the-stack.md) |
| UE4SS versions & risky changes | [`docs/02-ue4ss-versions.md`](docs/02-ue4ss-versions.md), [`data/ue4ss-timeline.json`](data/ue4ss-timeline.json) |
| What TFWWorkbench depends on | [`docs/03-tfworkbench.md`](docs/03-tfworkbench.md) |
| Root-cause hypotheses | [`docs/04-the-breakage.md`](docs/04-the-breakage.md) |
| The pin / downgrade / fix plan | [`docs/05-known-good-and-workarounds.md`](docs/05-known-good-and-workarounds.md) |
| Ground-truth local facts | [`local-evidence/2026-07-13-local-install.md`](local-evidence/2026-07-13-local-install.md) |
| Source URLs | [`meta/sources.md`](meta/sources.md) |
| What to do next | [`meta/next-session.md`](meta/next-session.md) |

## The compat tracker

`python tools/compat.py {list,check,pin,summary,validate}` — see
[`tools/README.md`](tools/README.md). Data is `data/compat.json` (schema in
`data/schema/`). Adding a tested combo = a new entry with its `UE4SS.dll` SHA-256.
