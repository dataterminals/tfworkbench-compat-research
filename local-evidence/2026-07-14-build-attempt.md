# Build attempt — 2026-07-14

Attempted to actually recompile TFWWorkbench's `main.dll` against current UE4SS to
close the loop on the fix. Got a full toolchain and the UE4SS source, but hit a hard
external blocker: **the UE4SS Unreal SDK is not publicly obtainable**, so the public
source can't be compiled from a clean clone.

## What worked

| Step | Result |
| --- | --- |
| Install CMake | ✅ Kitware.CMake 4.4.0 (winget) |
| Install Ninja | ✅ (winget) |
| Install Rust | ✅ rustup + stable-x86_64-pc-windows-msvc (rustc 1.97.0) |
| Install MSVC Build Tools | ✅ VCTools workload (winget; C++ + Win11 SDK) |
| Clone RE-UE4SS @ `b50986bd` | ✅ 41 MB; matches the current experimental asset |
| Main-repo headers present | ✅ `UE4SS/include/Mod/CppUserModBase.hpp`, `LuaMadeSimple`, etc. |
| Confirm mod build model | ✅ mods go in `cppmods/` via `add_subdirectory(...)`; build mode `Game__Shipping__Win64`; `cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Game__Shipping__Win64` |

## What blocked it

`git submodule update --init --recursive` fails on `deps/first/Unreal`:

```
Cloning into '.../deps/first/Unreal'...
fatal: clone of 'git@github.com:Re-UE4SS/UEPseudo.git' ... failed
```

Rewriting SSH→HTTPS just changes the error to the truth:

```
remote: Repository not found.
fatal: repository 'https://github.com/Re-UE4SS/UEPseudo.git/' not found
```

Investigation:
- `deps/first/Unreal` ends up **empty (0 headers)**; the `<Unreal/*>` SDK is entirely
  absent, so the mod (and UE4SS itself) cannot compile.
- **`Re-UE4SS` org → HTTP 404** (does not exist publicly). It is *not* the public
  `UE4SS-RE` org, which has all the other deps (LuaMadeSimple, PolyHook, patternsleuth,
  …) but **no Unreal/UEPseudo repo**.
- `UEPseudo` → **404** via web, API, SSH, HTTPS, and codeload tarball. GitHub repo
  search finds **no forks or mirrors**.
- Current `main`'s `.gitmodules` still points at the same dead URL.
- `UE4SS-RE/UE4SSCPPTemplate` (the official C++ mod template) submodules the whole
  `RE-UE4SS`, so it inherits the same blocker.

## Conclusion

The public RE-UE4SS repository is **not self-contained**: building it (or any C++ mod
against it) requires the private/removed `Re-UE4SS/UEPseudo` Unreal SDK. Therefore a
clean recompile of `main.dll` is only doable by someone with an existing `UEPseudo`
checkout or access — realistically the **maintainer (smotti)** or a core contributor.

This does not weaken the fix analysis: the recompile is still trivial and correct
(one re-signatured symbol, zero source changes — see
[`2026-07-14-abi-symbol-proof.md`](2026-07-14-abi-symbol-proof.md)). It only means the
*build environment* is gated. Toolchain installed on this machine: CMake, Ninja, Rust,
MSVC Build Tools.

> **Alternative if a rebuild stays out of reach:** the no-recompile import-table patch
> (repoint `main.dll`'s `…GetMinAlignment…AEAHXZ` import to the surviving `…AEAFXZ`
> export). Plausible because the engine field is small/little-endian, but it depends on
> `UStruct::MinAlignment`'s real width/layout in UE5.4.2 and **must be load-tested
> in-game** — see the caution in [`../mod/rebuild-recipe.md`](../mod/rebuild-recipe.md).
