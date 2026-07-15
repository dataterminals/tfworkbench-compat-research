# 05 — Known-good build, downgrade, and the fix

> **Two ways out:** (A) **recompile** TFWWorkbench's `main.dll` against current
> UE4SS — keeps "latest," the clean long-term fix, the *"fixable (probably)"* path;
> or (B) **pin** UE4SS to a pre-narrowing build the shipped `main.dll` already
> matches. Because the break is a **C++ ABI mismatch**, a Lua shim cannot fix it.

## The recommended pin

`python tools/compat.py pin` →

> **experimental `v3.0.1-894-g2172883`** (commit `21728830cb49`, **2026-01-28**)
> paired with **TFWWorkbench 0.2.1**. Confidence: **verified**.

Download (stable, permanent, no auth):

```
https://github.com/UE4SS-RE/RE-UE4SS/releases/download/experimental/UE4SS_v3.0.1-894-g2172883.zip
```
6,878,895 bytes · the contained `ue4ss\UE4SS.dll` is SHA-256 `678d8b02b919…` (15,801,856 B).

> **Verified (2026-07-15, first-hand):** this is the exact pair inside the community Codex AIO bundle, and both halves are
> **byte-identical to their official upstream artifacts** — the AIO's `UE4SS.dll`
> hashes to `678d8b02…`, matching the archive zip above; its
> `Scripts/main.lua` matches TFWWorkbench release **0.2.1** exactly. It is the only
> combo with **end-to-end runtime proof**: the AIO's own shipped `UE4SS.log`
> (2026-07-14) shows `Starting C++ mod 'TFWWorkbench'` with no `0x7F`, then
> `AddTo (Property) VendorData … 001_CodexPatch.json` and
> `Set FName property 'RowName' to value: Codex.Grabber` — the DataTable edit landed.
> Build 894 pins UEPseudo submodule `2d115713`, which still exports the `int32&`
> `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ`. See
> [`local-evidence/2026-07-15-aio-bundle-forensics.md`](../local-evidence/2026-07-15-aio-bundle-forensics.md).

### The pin is a window, not a point — and `-894` is *not* the baseline

> **Verified (ABI-only):** TFWWorkbench 0.2.1's `main.dll` resolves **81/81** against
> `-823-g3e2d111` (2025-12-28) and `-848-g91b70e5` (2026-01-12) as well. The whole
> pre-narrowing range is ABI-good.

> ⚠️ **`-894` cannot be the compile baseline.** 0.2.1's `main.dll` has PE
> `TimeDateStamp` **2026-01-20 15:26:44 UTC** — one hour before the 0.2.1 release, and
> **8 days before `-894` existed**. Its SDK is therefore a build on/before 2026-01-20.
> **Reported (Modder C, TFW modding chat, 2026-07-15):** the dev build was
> **`v3.0.1-823-g3e2d111`** — consistent with that timestamp, and verified ABI-good
> here. Import analysis cannot separate `-823` from `-848` (all 81 resolve on both).

> ⚠️ **Blind spot:** `-823`, `-848` and `-894` each pin a **different UEPseudo commit**
> (`4d476af9` / `53f54bb0` / `2d115713`), so the Unreal type layer moved between them.
> `abi-diff.py` proves symbols *resolve*; it cannot see **struct/vtable layout drift**.
> `-894` is empirically fine (Modder A's runtime log shows correct `FName` writes), but
> **`-823` is the closest-to-baseline choice**.

**Which to use?** Both work. `-894` = proven in the wild, already shipping in Modder A's
AIO — no reason to churn if you're on it. `-823` = the reported compile baseline,
lowest theoretical drift:
`https://github.com/UE4SS-RE/RE-UE4SS/releases/download/experimental/UE4SS_v3.0.1-823-g3e2d111.zip`
(6,697,505 B · `UE4SS.dll` sha256 `288a4fcb…`, 3,777 exports)

This also explains the community folklore: Construction Vendor's Nexus page says
*"UE4SS MUST BE VERSION v3.0.1-848 OR HIGHER"* — and its easy-install ships **exactly
`-848`** ([mod 77](https://www.nexusmods.com/theforeverwinter/mods/77)).

> ⚠️ **The "OR HIGHER" half of that note is stale and now actively harmful.** It was
> only true inside the pre-narrowing window. Anything from `-998` onward is broken.

## Getting a pinned build — this is easy, not fragile

> **Corrected 2026-07-15.** This page previously claimed *"there is no tidy download
> for an old experimental build"* and recommended building from source. **That was
> wrong.** Every experimental build is permanently archived.

- **`experimental`** ([release tag](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental))
  = *"UE4SS Experimental Release Archive"* — an **accumulating** prerelease holding
  **851 assets** spanning 2023-06 → 2026-07-13. The CI workflow appends to it and
  **never deletes**. Builds from 2024-03 still download today. **This is where you get
  a pinned build.**
- **`experimental-latest`** = a **rolling** tag. CI *wipes all assets* then re-uploads
  on every build, so it only ever holds the newest one — no per-commit permalink.
  Don't cite it as a source of record.
- **GitHub Actions artifacts** are `retention-days: 1` (not 14) — gone within a day.
  Irrelevant, because the archive release makes them unnecessary.

Asset naming is git-describe: `UE4SS_v3.0.1-<commits-since-tag>-g<short-sha>.zip`.

> 🚫 **Do NOT "downgrade" to `-1009`.** Builds `-998`, `-1000`, `-1005`, `-1008`,
> `-1009` and `-1011` **all pin the identical UEPseudo submodule `b2e876da`**, so they
> share the same broken ABI. Going back a few builds does nothing; you must go back
> **past the narrowing** (see [`04-the-breakage.md`](04-the-breakage.md)).

> ⚠️ **Never date a build from a file mtime.** In any redistributed bundle the DLL
> mtime is the **repacker's** timestamp. The AIO's `UE4SS.dll` is stamped 2026-07-10
> but is a **2026-01-28** build. Identify builds by the `UE4SS.log` `Git SHA #` banner
> or the `UE4SS.dll` SHA-256 — nothing else. (An earlier revision of this repo dated
> the break to "2026-07-10..07-12" purely from mtimes; that inference was invalid.)

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
5. Ideally upstream it to smotti (the maintainer) so everyone benefits.

> ⚠️ **Externally blocked:** UE4SS's Unreal SDK submodule (`Re-UE4SS/UEPseudo`) is
> private/removed — 404 to the API, the web UI, and `git ls-remote`, with no public
> mirror — so the public source can't be configured as-is. Needs smotti or someone
> with a UEPseudo checkout. Skeleton + fuller recipe:
> [`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md).

## First, confirm it's actually the ABI break (not H3)

Before downgrading or rebuilding, read `…\ue4ss\UE4SS.log` and confirm the failure
mode (see [`04-the-breakage.md`](04-the-breakage.md) "Deciding H1 vs H2 vs H3"):
- `Failed to load dll …main.dll… error: [0x7f]` → ABI break — pin or rebuild.
- Mod mis-placed / not attempted → **install error** (issue #1's cause) — fix the
  install first; don't downgrade UE4SS for nothing.
- **Mod loads fine but nothing changes in-game, and the log shows no `AddTo` lines**
  → **not an ABI problem at all.** You're running a TFWWorkbench too old for the
  JSON your content mod ships. See
  [`03-tfworkbench.md`](03-tfworkbench.md#the-silent-failure-json-actions-are-version-gated).

Also verify the mod is at `Binaries\Win64\ue4ss\Mods\TFWWorkbench` and enabled in
`mods.txt`.

## The exact first-breaking build — **SOLVED (2026-07-15)**

> **Verified by binary search over the archive** (`tools/ue4ss-bisect.py`, 5 downloads):
>
> | | build | date | UEPseudo | `GetMinAlignment` |
> | --- | --- | --- | --- | --- |
> | **last good** | **`v3.0.1-894-g2172883`** | 2026-01-28 | `2d115713` | `int32&` ✅ |
> | **first broken** | **`v3.0.1-929-gcd556d70`** | 2026-01-30 | `3a756005` | `int16&` ❌ |

**The commit:** `cd556d706a680af35379913006153e9807aabf4a` — narknon,
2026-01-30T23:02:24Z, *"chore: update UE submodule for FUObjectArray changes"*. It
touches **only** `deps/first/Unreal`.

**Why it's provably this commit and not an earlier one:**
`compare 21728830…cd556d70` = 35 commits, and `cd556d70` is the **only one touching
the submodule**. So builds `895`–`928` still pin `2d115713` and are **good** — they
were simply never archived. The good range is therefore **`-823` … `-928`**, with
**`-894` the newest one you can actually download**.

**The mechanism.** Those 35 commits are a **UVTD (vtable-dumper) overhaul** of
2026-01-28..30 — notably `2313a76620` *"update macrosetter, membervar and vtable
templates for UVTD changes"*. Regenerating the Unreal layer emitted **versioned
getters** (`GetMinAlignment506`, `GetMinAlignmentBase`) and narrowed
`UStruct::GetMinAlignment` to `int16&`, so the old mangled export vanished.

> 💡 **`GetMinAlignment` is named in no commit message.** The break is pure collateral
> damage of an FUObjectArray refactor — invisible in the changelog, which is exactly
> why the community never pinned it. It also means **UE 5.6 support (PR #977) is not
> the cause**: that merged 2025-08-22 and is an ancestor of good build `-894`.

Reproduce: `python tools/ue4ss-bisect.py`. Source-level confirmation remains
impossible (UEPseudo is private/404), but the **symbol-level** answer is complete.
