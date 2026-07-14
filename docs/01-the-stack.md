# 01 — The stack: how TFW modding fits together

To reason about the breakage you need the whole load-bearing chain, because
TFWWorkbench sits near the top of it and any layer below can take it down.

```
The Forever Winter  (UE 5.4.2, Steam AppID 2828860, Fun Dog Studios)
  └─ Binaries\Win64\
       ├─ ForeverWinter-Win64-Shipping.exe      the game
       ├─ dsound.dll  + bitfix\                  Signature Bypass (unsigned paks load)
       ├─ dwmapi.dll                             UE4SS proxy DLL (loads UE4SS.dll)
       └─ ue4ss\
            ├─ UE4SS.dll                          the scripting system / mod loader
            ├─ UE4SS-settings.ini
            └─ Mods\                              UE4SS Lua/C++/BP mods (incl. TFWWorkbench's script side)
                 ├─ BPModLoaderMod, ...           built-ins
                 └─ mods.txt                      "ModName : 1" enables a mod
  └─ Content\Paks\
       ├─ Mods\                                   content-pak mods (.pak/.utoc/.ucas) — created manually
       │    └─ TFWWorkbench\                       TFWWorkbench's pak/JSON data side
       └─ LogicMods\                              Blueprint "logic" mods (BPModLoaderMod scans here)
```

> **Verified** layout from a real install:
> [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md).
> Signed-pak + bypass details cross-checked against
> [`ForeverWinterMO2Support/docs/RESEARCH.md`](../../ForeverWinterMO2Support/docs/RESEARCH.md).

## The four layers, bottom to top

### 1. The game — Unreal Engine 5.4.2
TFW ships **signed, encrypted IoStore paks** (every `.pak` has a matching `.sig`).
The stock engine rejects unsigned paks, so *no mod loads* without a bypass. This
is why the whole stack exists.

### 2. Signature Bypass — `dsound.dll` + `bitfix\`
A proxy `dsound.dll` (or `version.dll` if you need in-game voice) plus a `bitfix\`
folder, dropped into `Binaries\Win64`, hook out the signature check so unsigned
community paks mount. The game "generally must be launched directly via the
shipping exe" for this to hold. Independent of UE4SS, but required for any pak mod.

### 3. RE-UE4SS — the scripting system / mod loader
UE4SS injects into the game via a **proxy DLL** (`dwmapi.dll` on the modern 3.x
layout) which loads `UE4SS.dll`. UE4SS then:
- scans engine memory to locate Unreal internals (the **patternsleuth** resolver
  engine on modern builds — see [`02-ue4ss-versions.md`](02-ue4ss-versions.md)),
- exposes a **Lua API** (and a C++ modding API) over Unreal objects, and
- loads mods listed in `Mods\mods.txt`.

Because TFW is UE**5.4.2**, it needs a UE5.4-capable UE4SS — which in practice
means an **experimental CI build**, since stable 3.0.1 predates UE5.4 support.
**This is the layer that changes under you.**

### 4. TFWWorkbench — the framework mod (the thing that breaks)
A UE4SS **C++/Lua hybrid** mod that, at runtime, finds the game's **DataTables** and
rewrites rows from JSON so multiple content mods can coexist. Its C++ half ships as a
**precompiled `main.dll`** that is **ABI-locked** to the UE4SS build it was compiled
against — so it depends not just on layer 3's *behavior* but on layer 3's exact
**binary interface**. That's the fragile joint: change UE4SS's ABI and `main.dll`
won't even load. See [`03-tfworkbench.md`](03-tfworkbench.md).

## The dependency arrows that matter

- **content mods → TFWWorkbench → UE4SS API → UE engine internals.**
- A change **anywhere** in "UE4SS API / how it resolves engine internals" can
  break TFWWorkbench without TFWWorkbench itself changing a line. That is exactly
  the failure described in the origin log: *TFWWorkbench didn't change; UE4SS did.*

## Two ways people install this stack

- **Manual:** drop the bypass, drop `ue4ss\` + `dwmapi.dll`, create
  `Content\Paks\Mods`, install TFWWorkbench, edit `mods.txt`.
- **Vortex extension** (TFW Nexus mod 121): auto-installs UE4SS + Signature Bypass
  + TFWWorkbench together. Convenient, but it can pull a **newer UE4SS than
  TFWWorkbench tolerates** — a plausible vector for how users end up on a broken
  "latest." (Whether the Vortex extension pins a UE4SS build is an open question —
  see [`meta/next-session.md`](../meta/next-session.md).)
