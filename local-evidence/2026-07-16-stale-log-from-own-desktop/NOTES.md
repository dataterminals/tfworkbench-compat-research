# A stale `-848` log from our own desktop, found masquerading as a local run

Recovered 2026-07-16 from the **laptop's** MO2 `overwrite\` folder, where it had sat for
three days looking like a local run. It is a real UE4SS `-848` runtime session — but it was
written by the **desktop**, not the machine it was found on. Kept for two reasons: it is
first-hand `-848` runtime evidence, and the way it misled a whole session is worth recording.

| | |
|---|---|
| `UE4SS.log` | sha256 `bddf20a2b4f1008b1d386360d9dacf39c56763471068834783f52fcafa6becd2`, 193,469 B, 2,294 lines |
| `bitfix.txt` | 843 B — same run, `bitfix v0.1.0-a2df008` |
| Banner | `UE4SS - v3.0.1 Beta #0 - Git SHA #91b70e5` → **experimental v3.0.1-848-g91b70e5** (2026-01-12) |
| Session | 2026-07-13 06:15:39 → 07:25:29 (70 min, `Timezone: America/New_York`) |
| Game path in log | `H:\SteamLibrary\steamapps\common\The Forever Winter\...` |

Paths left unscrubbed deliberately — the `H:` **is** the evidence.

## Provenance: the desktop, not the laptop

> **Verified:** the log was not written by the machine it was found on.
> That machine (`SYLG5`, Dell G5 5505 — a **laptop**) has **never had an `H:` drive**:
> `HKLM\SYSTEM\MountedDevices` records every letter ever assigned and lists only
> `C: D: E: F: G:`. The laptop runs the game from `D:\SteamLibrary`.

> **Verified:** it did not arrive inside the ConstructionVendor AIO.
> Both `RE-UE4SS` and `TFWWorkbench` carry
> `installationFile=All-in-one file for ConstructionVendor-77-0-9-1-3-1768682266.7z`.
> That trailing field is Nexus's upload timestamp: `1768682266` = **2026-01-17 20:37 UTC**.
> An archive published in **January** cannot contain a log written in **July**.

> **Inferred (high confidence):** it is **our own desktop's** log, copied to the laptop with
> the mod set-up. The user reports running TFW from `H:` on the desktop and `C:`/`D:` on the
> laptop; both this log and the laptop's own say `Timezone: America/New_York`.
> The laptop's backup `_backup_TheForeverWinter_20260714_014349` (taken 07-14 01:43) contains
> **only** the laptop's own `bitfix.txt` (1,686 B, 07-12 14:00) and **no `UE4SS.log`** — and
> `mods\RE-UE4SS` + `mods\TFWWorkbench` were created **07-14 01:47**, four minutes later. The
> 843 B / 07-13-dated `bitfix.txt` **replaced** the laptop's 1,686 B one while carrying an
> *older* mtime: the signature of a timestamp-preserving copy, not a local run.

Timeline (laptop):

```
07-12 09:42  MO2 TFW instance created
07-12 13:53  Root Builder cache built  (cache dir name: D…The_Forever_Winter)
07-12 14:00  bitfix.txt written, 1,686 B   <- the laptop's own run
07-13 06:15  *** this log's session — H:, i.e. the DESKTOP ***
07-14 01:43  backup taken: overwrite has ONLY bitfix.txt (1,686 B / 07-12). No UE4SS.log.
07-14 01:47  RE-UE4SS + TFWWorkbench appear; the 07-13-dated files land with them
```

## What it proves

**The C++ half loaded on `-848`.** L963:

```
[2026-07-13 06:15:50.6353871] [TFWWorkbench] Registered Lua functions for mod
```

No `[Lua]` prefix ⇒ emitted by `main.dll` (CppUserModBase) as it registers
`AddDataTableRow` / `ConfigureDataTables` into TFWWorkbench's `lua_State`. It cannot appear
unless the DLL loaded. No `[0x7f]`, no `Failed to load dll`. The Lua half then ran clean for
70 minutes: `[Lua] [TFWWorkbench:main:LoadDataTableAssets] Successfully loaded data table
asset for ManufacturingGroups`, plus 19 `DumpFile` lines.

> **⚠️ Which TFWWorkbench version is UNKNOWN — do not guess.**
> An earlier draft of this note asserted **0.1.2**, reasoning that the CV stack ships
> `-848` + 0.1.2. That reasoning died with the AIO provenance above: this is the desktop's
> install and we have not inspected it. `main.dll` is byte-identical across 0.1.0–0.2.0
> (`825ba834`) and different in 0.2.1 (`24b05dc2`), and **both** emit the same
> `Registered Lua functions` line — so the log cannot identify its own version. The zero
> `AddTo` lines are equally consistent with 0.1.x *or* with 0.2.1 and no JSON mods.
>
> ⇒ This log upgrades **neither** `-848` compat entry on its own. It proves *`-848` loads
> some TFWWorkbench `main.dll` at runtime*. **To close it:** hash `Scripts/main.lua` on the
> desktop (`2230fa8c…` = 0.2.1, `afe9a5b2…` = 0.1.2). One command finishes the datum.

## ⚠️ `Starting C++ mod 'TFWWorkbench'` is mechanism-dependent, not universal

This cost a session twice — first by grepping for it and wrongly concluding the C++ half
never loaded, then by over-correcting to "it appears in zero logs."

> **Verified:** UE4SS starts mods from **`mods.txt`** first, then from per-mod
> **`enabled.txt`**. In both logs we hold locally, TFWWorkbench is **absent from `mods.txt`**
> and ships its own `enabled.txt`, so it starts on the enabled.txt path:
> ```
> Starting mods (from mods.txt (…\Mods\mods.txt) load order)...
> Starting mods (from enabled.txt (…\Mods), no defined load order)...
> Mod 'TFWWorkbench' has enabled.txt, starting mod.
> ```
> Neither log contains `Starting C++ mod`. Meanwhile Modder A's `-894` log
> (`2026-07-15-aio-bundle-forensics.md`) **does** contain it.

> **Inferred:** the **enable mechanism decides the marker** — `mods.txt` emits
> `Starting C++ mod 'X'`; `enabled.txt` emits `Mod 'X' has enabled.txt, starting mod.`
> Support: a near-natural experiment — Modder A's log and our 2026-07-16 log are the **same
> `-894` build**, differing in enable path, with the marker present/absent accordingly. It
> also explains G's log (via
> [ForeverWinterModSetup](https://github.com/dataterminals/ForeverWinterModSetup), which
> appends `TFWWorkbench : 1` to **mods.txt**) reportedly carrying the marker — that note was
> **right**; an earlier draft here wrongly flagged it as misremembered.
> **Not yet confirmed against UE4SS `-894` source. Do that before relying on it.**

**Practical rule:** use **`[TFWWorkbench] Registered Lua functions for mod`** as the
"main.dll loaded" probe. It is `main.dll`'s own output and is mechanism-independent —
present in both enabled.txt logs here. (Unconfirmed in Modder A's log: we hold only the
excerpt quoted in the forensics note, not the file itself.)

**This blocks the planned `TFWWorkbenchDoctor` rewrite.** The proposal on record — *"parse
`UE4SS.log` for `Starting C++ mod 'TFWWorkbench'` + absence of `[0x7f]`"* — silently returns
**"broken"** for every install enabled via `enabled.txt`, which includes the CV AIO's layout
and every MO2 install. Retarget it at the `Registered Lua functions` line.

Related grep trap: bare `0x7f` matches inside every `0x7ff6…` address the scanner prints.
Always search the bracketed `[0x7f]`. And `[PS] Failed to find FUObjectHashTables::Get()` is
benign — it appears in known-good logs.

## The trap this log set

`overwrite\Root\Windows\ForeverWinter\Binaries\Win64\ue4ss\UE4SS.log` is **exactly** where a
real log lands under MO2 + Root Builder `redirect=true`. Right drawer, wrong log. MO2's
Overwrite never self-clears, so a log copied in from elsewhere sits there looking
authoritative indefinitely.

A **second machine of your own** is the nastiest version of this: same person, same timezone,
same mod versions, plausible date. The only tell was a drive letter.

Corollary to the existing "never date a build from an mtime" rule:
**never trust a `UE4SS.log` without checking its paths resolve on the machine you are standing on.**
The banner SHA is authoritative for *which build wrote it* — never for *which build you are
running*. To verify a local install, hash `UE4SS.dll` (`-894` = `678d8b02…`, and it embeds
the ASCII string `2172883`).

And the meta-lesson: *"not written by this machine"* does **not** imply *"not ours."*
That inference is what produced the fictional AIO-packager story this note originally told.
