# Rebuild recipe — recompile TFWWorkbench's `main.dll` for current UE4SS

This is the **real fix**. Because the break is a **single re-signatured symbol**
([`docs/04-the-breakage.md`](../docs/04-the-breakage.md)) and **not** a logic bug,
you recompile `main.dll` against the UE4SS SDK that matches the build you run — the
loader can then resolve the import again.

> **Verified (2026-07-14): this is a clean recompile, zero source changes.** The
> only call to the broken symbol is `dllmain.cpp:543`:
> ```cpp
> FMemory::Malloc(structSize, rowStruct->GetMinAlignment())
> ```
> `UStruct::GetMinAlignment()` return type went `int32&` → `int16&`; the value is
> just read and passed as `Malloc`'s alignment arg, so `short&`→`int` converts
> implicitly and the result is identical (alignments are 1–16). The other
> `GetMinAlignment` calls are `FProperty::GetMinAlignment` (unchanged). Nothing in
> the source needs to change — just rebuild.

## What the mod actually is (verified)

`smotti/TFWWorkbench-Cpp` is tiny: one `dllmain.cpp` + this `CMakeLists.txt`:
```cmake
set(TARGET TFWWorkbench)
add_library(${TARGET} SHARED dllmain.cpp)
target_include_directories(${TARGET} PRIVATE .)
target_link_libraries(${TARGET} PUBLIC UE4SS)
```
No submodules. It expects a **`UE4SS` CMake target to already exist** — i.e. it's
built **inside the RE-UE4SS source tree** (the standard "drop your mod in `UE4SS/Mods/`"
flow), which is where its headers (`<Mod/CppUserModBase.hpp>`, `<Unreal/...>`,
`<LuaMadeSimple/...>`) and the `UE4SS` link target come from.

> ⚠️ **The `zDEV-UE4SS_*.zip` release asset is NOT a build SDK.** It's a runtime
> dev install (just `dwmapi.dll` + `ue4ss/`), no headers/libs/CMake. You need the
> UE4SS **source**, not zDEV.

## Toolchain required

- **MSVC** (Visual Studio 2022 Build Tools, C++ workload) — the mod is MSVC-mangled.
- **CMake** ≥ 3.22 and **Ninja**.
- **Rust** (the `patternsleuth` resolver in modern UE4SS is Rust) — needed to build
  UE4SS itself.
- Git (with submodules).

## Steps

1. **Clone RE-UE4SS at the matching commit**, recursively:
   ```
   git clone --recursive https://github.com/UE4SS-RE/RE-UE4SS
   cd RE-UE4SS && git checkout <your build's commit>   # e.g. b50986bd for v3.0.1-1011
   git submodule update --init --recursive
   ```
   Match the commit to *your* installed build (read it from `UE4SS.log`'s banner, or
   use the latest if you also update your install).
2. **Add the mod to the tree:** clone `smotti/TFWWorkbench-Cpp` into `UE4SS/Mods/TFWWorkbench`
   and register it in the Mods CMake list (per UE4SS's C++ mod guide).
3. **Configure + build** with UE4SS's documented CMake/Ninja preset (e.g. a
   `Game__Shipping__Win64` config). This builds UE4SS **and** the mod target →
   `TFWWorkbench.dll`. Rename to `main.dll`.
4. **Swap it in:** replace `dlls/main.dll` in the installed TFWWorkbench mod folder.

## Verify the rebuilt DLL (before even launching the game)

```
python tools/abi-diff.py <new main.dll> <your ue4ss/UE4SS.dll>
```
Expect **`MISSING: 0`** (every import resolves). Then launch once and confirm no
`0x7F` in `UE4SS.log` and that `AddDataTableRow`/`ConfigureDataTables` register
(the [`TFWWorkbenchDoctor`](TFWWorkbenchDoctor) mod reports this). Finally, add a
`works` row to [`../data/compat.json`](../data/compat.json) with the new
`main.dll`/`UE4SS.dll` identifiers, and offer the DLL upstream (smotti; issue #2 is open).

## Why this is usually a 2-minute job for the right person

Anyone who already has a UE4SS C++ mod dev environment (the maintainer, or any TFW
C++ modder) just drops the mod in, rebuilds, and ships `main.dll`. The heavy part is
only *first-time* toolchain setup + a from-source UE4SS build on a clean machine.

## Not recommended: the no-recompile binary patch

In principle you could patch `main.dll`'s import table to point at the surviving
`?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAFXZ` (`int16&`) export. It *might* work
because the underlying engine field is small and little-endian, but the compiled
code dereferences the reference as a 4-byte `int`, so it depends on the adjacent
bytes being zero — **unverified and fragile**. Recompilation is the correct fix.
