# Rebuild recipe — recompile TFWWorkbench's `main.dll` for current UE4SS

This is the **real fix** (the *"fixable (probably)"* path): because the break is a
**C++ ABI mismatch, not a logic bug**, you don't change any TFWWorkbench source —
you just **recompile its `main.dll` against the UE4SS SDK that matches the build you
actually run**, so the loader can resolve the imports again.

> Requires a C++ toolchain (MSVC + CMake). Ideally done by the maintainer
> (smotti) and published, so every user benefits. Until then, a user with
> the toolchain can self-build. See [`docs/04-the-breakage.md`](../docs/04-the-breakage.md)
> for why this works and [`docs/05`](../docs/05-known-good-and-workarounds.md) for
> the alternative (pinning UE4SS).

## Preconditions

- Confirm the failure is the ABI break (H1), not an install error (H3): run
  [`TFWWorkbenchDoctor`](TFWWorkbenchDoctor) or read `UE4SS.log` for
  `Failed to load dll …main.dll… error: [0x7f]`.
- Know the **exact UE4SS build** you run (git-describe from `UE4SS.log`), so you can
  build against a matching SDK/commit.

## Steps (outline — verify against upstream build docs before relying on it)

1. **Clone with submodules:**
   ```
   git clone --recursive https://github.com/smotti/TFWWorkbench-Cpp
   ```
   (`CMakeLists.txt` does `add_library(TFWWorkbench SHARED …)` +
   `target_link_libraries(TFWWorkbench PUBLIC UE4SS)`.)
2. **Provide a matching UE4SS SDK.** Point the `UE4SS` CMake target at the RE-UE4SS
   source/SDK **at the commit matching your installed build** (build UE4SS from that
   commit, or use its published SDK). This is the crux — the SDK version is what
   fixes the ABI.
3. **Configure + build** the `TFWWorkbench` SHARED target with the same
   MSVC/CMake toolchain UE4SS uses (post-2025-11-11 UE4SS is CMake; older was xmake —
   match whatever your target build expects). Output: a fresh `main.dll`.
4. **Swap it in:** replace `dlls/main.dll` in the installed TFWWorkbench mod folder
   with the freshly built one.
5. **Verify in-game:** launch, check `UE4SS.log` — no `0x7F`, and
   `AddDataTableRow`/`ConfigureDataTables` register (the Doctor mod confirms this).
6. **Record + share:** add a `works` row to [`../data/compat.json`](../data/compat.json)
   (UE4SS build + `main.dll` provenance), and open a PR / issue note upstream so
   smotti can publish an official rebuild.

## Open unknowns for this recipe

- The **exact UE4SS commit** smotti built v0.2.1 against isn't pinned in the repo
  (CMake just links whatever UE4SS is present); `~-848/-849` is inferred. For a
  rebuild you match **your** target build, so this matters less — but it means there
  is no "official" reference SDK version to reproduce the original.
- UE4SS's own build steps / SDK-consumption path should be confirmed against current
  [docs.ue4ss.com](https://docs.ue4ss.com/) before a first build — the xmake→CMake
  migration changed the process.

See also [`meta/next-session.md`](../meta/next-session.md) for the export-diff
approach (`dumpbin /exports` on `UE4SS.dll` vs `main.dll`'s decorated imports) to
identify *which* symbol changed — useful for a minimal, well-understood rebuild.
