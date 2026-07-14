# 05 — Known-good build, downgrade, and the fix

> **Two ways out:** (A) **recompile** TFWWorkbench's `main.dll` against current
> UE4SS — keeps "latest," the clean long-term fix, the *"fixable (probably)"* path;
> or (B) **pin** UE4SS to the ~Jan-2026 build the shipped `main.dll` already
> matches. Because the break is a **C++ ABI mismatch**, a Lua shim cannot fix it.

## The recommended pin

`python tools/compat.py pin` →

> **experimental `v3.0.1-848 / -849`** (~2026-01-11 to 01-16; commits
> `91b70e5b8b1f` / `486806ab2bed`). Confidence: **medium**.

Why this build:
- It's the **Nexus-documented floor** — [mod 77](https://www.nexusmods.com/theforeverwinter/mods/77)
  (authors incl. Terraru): *"UE4SS MUST BE VERSION v3.0.1-848 OR HIGHER."*
- It's the **inferred ABI baseline** the shipped `main.dll` was built against
  (TFWWorkbench-Cpp last pushed 2026-01-20; -848 ≈ 2026-01-12).

> ⚠️ **The "OR HIGHER" part of that Nexus note is now stale.** It was only valid
> inside the ABI-compatible window near -848. Newer experimental builds are exactly
> what break the mod. The safe target is **~-848/-849 specifically**, not "anything
> newer."

## Getting a ~Jan-2026 build (downgrade is fragile)

There is **no tidy download** for an old experimental build:
- `experimental-latest` keeps **only the current asset** (no historical Jan-2026 zip).
- CI artifacts have **~14-day retention** — all long expired.
- No confirmed community mirror of a `-848` zip was located.

So, in order of reliability:
1. **Restore a personal pre-2026-07-12 UE4SS backup** if you have one (fastest).
2. **Build UE4SS from source** at commit `91b70e5b8b1f` (-848) or `486806ab2bed`
   (-849) and use that `UE4SS.dll`.
3. **Ask the TFW community** (Nexus old-files / Discord) for an archived `-848`
   zip — existence unconfirmed; **verify its git-describe version before use**.

Whatever you install, record its `UE4SS.dll` SHA-256 in
[`data/compat.json`](../data/compat.json) so it's identifiable later.

## The real fix (A): recompile `main.dll`

The break is a **pure ABI/import mismatch, not a logic bug**, so **no source change
is needed** — `TFWWorkbench-Cpp/CMakeLists.txt` already links the `UE4SS` target.
Rebuild against the **current** UE4SS SDK and ship the new `dlls/main.dll`:

1. Clone `smotti/TFWWorkbench-Cpp` (with submodules).
2. Point its `UE4SS` dependency at the SDK matching the **installed** UE4SS build.
3. `cmake` configure + build the `TFWWorkbench` SHARED target → new `main.dll`.
4. Drop the rebuilt `main.dll` into the mod's `dlls/`; test in-game.
5. Ideally upstream it to smotti/terraru so everyone benefits.

Requires the maintainer or a user with the C++ toolchain. Skeleton + a fuller
recipe: [`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md). This is the option that
keeps you on the latest UE4SS.

## First, confirm it's actually the ABI break (not H3)

Before downgrading or rebuilding, read `…\ue4ss\UE4SS.log` and confirm the failure
mode (see [`04-the-breakage.md`](04-the-breakage.md) "Deciding H1 vs H2 vs H3"):
- `Failed to load dll …main.dll… error: [0x7f]` → ABI break — pin or rebuild.
- Mod mis-placed / not attempted → **install error** (issue #1's cause) — fix the
  install first; don't downgrade UE4SS for nothing.

Also verify the mod is at `Binaries\Win64\ue4ss\Mods\TFWWorkbench` and enabled in
`mods.txt`.

## Bisecting the exact first-breaking build (open)

The precise commit between `-849` (works) and `-1011` (broken) where an imported
symbol first disappears is **not yet bisected** — it needs building `main.dll`
against successive UE4SS builds, or diffing `UE4SS.dll` exports (`dumpbin /exports`
/ `llvm-nm`) against `main.dll`'s decorated import list. Tracked in
[`meta/next-session.md`](../meta/next-session.md). Log each result to
[`data/compat.json`](../data/compat.json) with its `UE4SS.dll` SHA-256.
