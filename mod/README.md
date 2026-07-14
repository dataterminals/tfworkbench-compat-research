# mod/ — the fix pillar

The break is a **C++ ABI mismatch** ([`docs/04-the-breakage.md`](../docs/04-the-breakage.md)):
TFWWorkbench's precompiled `main.dll` fails to load on newer UE4SS. That shapes what
a "fix" can be.

| Path | What | For whom |
| --- | --- | --- |
| [`rebuild-recipe.md`](rebuild-recipe.md) | **The real fix** — recompile `main.dll` against current UE4SS (no source change). | maintainer, or a user with the C++ toolchain |
| [`TFWWorkbenchDoctor/`](TFWWorkbenchDoctor) | A read-only **diagnostic** Lua mod: reports the UE4SS build and whether TFWWorkbench's C++ side loaded. | any user, to confirm the failure mode |

> **Why there's no Lua "shim."** A Lua mod can't fix an ABI break — `main.dll` fails
> to *load* before any Lua executes. The original `TFWWorkbenchCompatShim` idea was
> dropped once research established the C++-ABI root cause. The Doctor mod is what
> remains useful in Lua: **telling you which failure you're in** so you choose
> rebuild (keep latest UE4SS) or pin (downgrade UE4SS —
> [`docs/05`](../docs/05-known-good-and-workarounds.md)).
