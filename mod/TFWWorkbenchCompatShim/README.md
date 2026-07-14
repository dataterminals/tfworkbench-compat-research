# TFWWorkbenchCompatShim (skeleton)

A UE4SS mod that will host the **fix** for the TFWWorkbench × newer-UE4SS
incompatibility, once [`docs/04-the-breakage.md`](../../docs/04-the-breakage.md)
confirms the root cause.

## Current state: INERT

`Scripts/main.lua` ships with `ENABLE_FIX = false`. It only:
- logs that it loaded, and
- prints a best-effort environment fingerprint (UE4SS / UE version) to `UE4SS.log`,
  wrapped in `pcall` so it can never crash the game on any build.

It applies **no patch**. This is deliberate — see the decision gate in
[`docs/05-known-good-and-workarounds.md`](../../docs/05-known-good-and-workarounds.md):
a shim against an unconfirmed cause is worse than none.

## Why a shim (vs. patching TFWWorkbench directly)

Two viable fix shapes, decided once the cause is known:
1. **Shim mod (this):** loads *before* TFWWorkbench and restores the UE4SS behavior
   TFWWorkbench assumes (e.g. name-lookup semantics). Keeps TFWWorkbench untouched;
   works even if TFWWorkbench isn't updated.
2. **Patched TFWWorkbench fork:** change TFWWorkbench to be explicit about the
   behavior it needs (e.g. pass an explicit `EFindName`). Cleaner long-term; needs
   upstreaming to smotti.

The shim is the faster, non-invasive path and the reason this skeleton exists.

## Install (for testers, once a fix lands)

1. Copy this `TFWWorkbenchCompatShim` folder into
   `…\Binaries\Win64\ue4ss\Mods\`.
2. In `ue4ss\Mods\mods.txt`, enable it **above** TFWWorkbench:
   ```
   TFWWorkbenchCompatShim : 1
   TFWWorkbench : 1
   ```
3. Launch once; check `UE4SS.log` for the `[TFWWorkbenchCompatShim]` lines.

## Load order matters

UE4SS initializes mods in `mods.txt` order (top first). The shim must run before
TFWWorkbench so any compensation is in place before TFWWorkbench reads the
DataTables.
