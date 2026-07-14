# TFWWorkbenchDoctor — a UE4SS diagnostic mod

A tiny, **read-only** UE4SS Lua mod that helps a user pinpoint why TFWWorkbench
isn't working. It **modifies nothing**.

## What it reports (to `UE4SS.log` / the UE4SS console)

1. A fingerprint of the running **UE4SS build** (and a reminder that the
   authoritative version is the git-describe banner at the top of `UE4SS.log`,
   e.g. `v3.0.1-1011-gb50986bd`).
2. Whether TFWWorkbench's **C++ side loaded** — it checks for the Lua functions the
   C++ `main.dll` registers (`AddDataTableRow`, `ConfigureDataTables`). If they're
   missing, `main.dll` almost certainly failed to load, and it points you at the
   `0x7F` line in `UE4SS.log` and the fix.

## Why a diagnostic and not a "shim"

> The break is a **C++ ABI mismatch** (see
> [`docs/04-the-breakage.md`](../../docs/04-the-breakage.md)): TFWWorkbench's
> precompiled `main.dll` fails to **load** on newer UE4SS, *before any Lua runs*. A
> Lua mod therefore **cannot** patch around it. This mod's job is to **tell you
> which failure you're in** so you pick the right fix:
> - `0x7F` load failure → **recompile** `main.dll` ([`../rebuild-recipe.md`](../rebuild-recipe.md))
>   or **pin** UE4SS ([`docs/05`](../../docs/05-known-good-and-workarounds.md)).
> - functions missing but no `0x7F`, and the mod isn't under `ue4ss/Mods/TFWWorkbench`
>   → **install error** (the cause of issue #1).

(The earlier `TFWWorkbenchCompatShim` idea was dropped once research showed the
break is C++-ABI, not a Lua-fixable behavior change.)

## Install

1. Copy `TFWWorkbenchDoctor` into `…\Binaries\Win64\ue4ss\Mods\`.
2. Enable it in `ue4ss\Mods\mods.txt`:
   ```
   TFWWorkbenchDoctor : 1
   ```
3. Launch once; read the `[TFWWorkbenchDoctor]` lines in `UE4SS.log`.

Safe on any UE4SS build — every probe is wrapped in `pcall`.
