# CLAUDE.md — orientation for AI agents

You are working in **tfworkbench-compat-research**. Read this before acting.

> **🎯 The mission, in one line:** find out **which RE-UE4SS build breaks
> TFWWorkbench on The Forever Winter, and why, then ship a fix.** Everything here
> serves that. Start with [`docs/00-overview.md`](docs/00-overview.md), then the
> latest entry in [`meta/research-log.md`](meta/research-log.md) and
> [`meta/next-session.md`](meta/next-session.md).

## What this repo is

A focused investigation + toolkit around one compatibility break. It has four
parts: a **docs** knowledge base, a **compat tracker** (`data/compat.json` +
`tools/compat.py`), a **fix skeleton** (`mod/TFWWorkbenchCompatShim`), and
**evidence** (`local-evidence/`, `seed/`). There is a small Python CLI; otherwise
it's documentation-first.

## The mental model (load this first)

- **The Forever Winter (TFW)** = Unreal Engine **5.4.2** game. Ships signed paks →
  needs a **Signature Bypass** (`dsound.dll` + `bitfix\`) for any mod to load.
- **RE-UE4SS** = the Lua/C++ scripting system injected via a proxy `dwmapi.dll`.
  For UE5.4 it's a **rolling experimental (patternsleuth) build**, not a numbered
  stable — so "latest" is a moving target with no clean version string.
- **TFWWorkbench** (smotti/TFWWorkbench, note double-W) = a UE4SS mod that edits
  Unreal **DataTables at runtime** from JSON. It's a **framework dependency** other
  mods rely on. It didn't change; UE4SS did — that's the whole problem.
- **The break** = a newer UE4SS build changes some behavior TFWWorkbench assumes
  (leading suspect: the `FName` ctor default `FNAME_Find`→`FNAME_Add` from 3.0.0,
  and/or patternsleuth resolver drift). See [`docs/04-the-breakage.md`](docs/04-the-breakage.md).

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
- **The fix skeleton stays inert until a cause is confirmed.**
  `mod/TFWWorkbenchCompatShim/Scripts/main.lua` has `ENABLE_FIX = false`. Do not
  ship shim logic against an unconfirmed hypothesis — see the decision gate in
  [`docs/05-known-good-and-workarounds.md`](docs/05-known-good-and-workarounds.md).
- **Identify builds by `UE4SS.dll` SHA-256**, since CI builds lack version metadata.

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
