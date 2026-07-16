# Ghost log: `-848-g91b70e5` runtime session, shipped inside the ConstructionVendor AIO

Recovered 2026-07-16 from the dev box's MO2 **overwrite** folder, where it had been
masquerading as a local run for three days. Archived because it is **first-hand runtime
proof for the `-848` + 0.1.2 pair**, and because the way it misled us is worth recording.

| | |
|---|---|
| `UE4SS.log` | sha256 `bddf20a2b4f1008b1d386360d9dacf39c56763471068834783f52fcafa6becd2`, 193,469 B, 2,294 lines |
| `bitfix.txt` | 843 B — same run, `bitfix v0.1.0-a2df008` |
| Banner | `UE4SS - v3.0.1 Beta #0 - Git SHA #91b70e5` → **experimental v3.0.1-848-g91b70e5** (2026-01-12) |
| Session | 2026-07-13 06:15:39 → 07:25:29 (70 min, `Timezone: America/New_York`) |
| Game path in log | `H:\SteamLibrary\steamapps\common\The Forever Winter\...` |

## It is NOT ours — three independent proofs

1. **No `H:` drive exists on the dev box** (C, D, F, G only).
2. **RootBuilder bakes the drive letter into its per-game cache folder name**
   (`C:\Modding\MO2\plugins\data\RootBuilder\<mangled path>\`). The Cyberpunk pair
   `SSteamLibrary…Cyberpunk_2077` + `DSteamLibrary…Cyberpunk_2077` proves old letters
   persist as separate folders. There is **no `H…The_Forever_Winter` folder** → TFW has
   never run from `H:` under this MO2 install.
3. **MO2's own usvfs logs show sessions on 07-12, 07-14, 07-15, 07-16 — but not 07-13.**
   MO2 was not open when this log was written.

Origin: both `RE-UE4SS` and `TFWWorkbench` mods carry
`installationFile=All-in-one file for ConstructionVendor-77-0-9-1-3-1768682266.7z`.
compat.json already identifies that bundle as **"THE CONSTRUCTION VENDOR STACK … ships
exactly -848"**. The packager's own logs rode along inside the archive and were swept into
`overwrite\Root\` (RootBuilder `redirect=true`), 7-Zip preserving the mtimes.

## What it proves

**The C++ half loaded on `-848`.** L963:

```
[2026-07-13 06:15:50.6353871] [TFWWorkbench] Registered Lua functions for mod
```

That line has **no `[Lua]` prefix** — it is emitted by `main.dll` (CppUserModBase) as it
registers `AddDataTableRow` / `ConfigureDataTables` into TFWWorkbench's `lua_State`. It is
C++-side output and cannot appear unless the DLL loaded. No `[0x7f]`, no `Failed to load`.

The Lua half then ran clean for 70 minutes:
`[Lua] [TFWWorkbench:main:LoadDataTableAssets] Successfully loaded data table asset for
ManufacturingGroups`, plus 19 DumpFile lines.

⇒ This **upgrades the `-848` entries in compat.json from ABI-only to runtime-verified.**
The `-848 (cross-tested)` entry's caveat *"NOT runtime-tested"* is now satisfied for the
**0.1.2** pairing (the CV stack). It says nothing about `-848` + **0.2.1**, which remains
ABI-only.

Zero `AddTo` and zero `Add`/`Replace`/`Remove` actions — consistent with 0.1.2 (`AddTo` is
0.2.0+) and with no JSON mods being installed in that packager's setup.

## ⚠️ Marker correction — `Starting C++ mod` is NOT a reliable probe

An earlier pass of this note wrongly concluded "the C++ half never loaded", because it
grepped for `Starting C++ mod`, `C++`, `.dll` and `main.dll` — **all of which return zero
hits across all 2,294 lines even though the DLL demonstrably loaded.** The same is true of
the dev box's own `-894` log from 2026-07-16.

**Use `[TFWWorkbench] Registered Lua functions for mod` as the "main.dll loaded" marker.**
Do not grep for `Starting C++ mod`; it is absent from every log we hold (`-848` and `-894`
alike), and searching for it produces a **false negative**.

This directly affects the planned `TFWWorkbenchDoctor` rewrite. The proposal on record —
*"parse UE4SS.log for `Starting C++ mod 'TFWWorkbench'` + absence of `[0x7f]`"* — **would
reproduce the very false negative it is meant to fix.** Retarget it at the `Registered Lua
functions` line.

> Unresolved: the notes on G's `-894` log record a `Starting C++ mod 'TFWWorkbench'`
> line. Neither log here has one. Either that recollection is imprecise or the line is
> verbosity/settings-gated. Worth re-checking `Desktop.7z` before relying on either marker.
>
> Note that G's log is a **separate artifact** from the `-894` `UE4SS.log` shipped inside
> the community AIO bundle (Modder A's), which is what `data/compat.json`'s `-894` entry
> currently cites. Do not conflate the two when resolving this.

Also note: grepping for bare `0x7f` is itself a trap — it matches inside every `0x7ff6…`
address the scanner prints. Always search the bracketed `[0x7f]`.

## The trap

`overwrite\Root\Windows\ForeverWinter\Binaries\Win64\ue4ss\UE4SS.log` is **exactly** where a
real log lands. Right drawer, wrong log. MO2's Overwrite never self-clears and outranks every
mod, so a log that arrived inside a mod archive sits there looking authoritative forever.

Adds a corollary to the existing "never date a build from an mtime" rule:
**never trust a `UE4SS.log` without checking its paths resolve on the machine you're standing on.**
The banner SHA is authoritative for *which build wrote it* — not for *which build you are running*.
To verify a local install, hash `UE4SS.dll` or grep it for the embedded SHA string
(`-894` = `678d8b02…`, embeds ASCII `2172883`).
