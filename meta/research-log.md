# Research log

Newest entry last. Every entry records **what was done, what was learned, and how
we know** — preserve provenance; never silently promote a guess to a fact.
(House style borrowed from `grb-modding-knowledgebase`.)

---

## 2026-07-13 — Repo founded; local ground truth captured

**Done**
- Seeded the repo from a TFW modding chat snippet ([`seed/running-log.txt`](../seed/running-log.txt)):
  "you can't use the latest ue4ss version when having TFWorkbench as a dependency."
- Initial web recon: identified TFWWorkbench = [smotti/TFWWorkbench](https://github.com/smotti/TFWWorkbench)
  (runtime DataTable editor for The Forever Winter, latest v0.2.1 2026-01-20);
  UE4SS = [UE4SS-RE/RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS).
- Forensically inspected the local TFW install (see
  [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md)).
- Scaffolded all four pillars: docs KB, `data/compat.json` + `tools/compat.py`
  tracker, `mod/TFWWorkbenchCompatShim` skeleton, evidence.
- Launched a verified research workflow (id `wu3yvil3x`): 5 finders → adversarial
  verification → synthesis, targeting the exact breaking build, mechanism, and pin.

**Learned (Verified)**
- TFW is UE **5.4.2** (Steam AppID 2828860). Stable UE4SS 3.0.1 (Feb 2024) predates
  UE5.4 support → TFW runs an **experimental** UE4SS build.
- The local `UE4SS.dll` is an **official RE-UE4SS patternsleuth CI build** (embedded
  path `D:\a\RE-UE4SS\RE-UE4SS\deps\first\patternsleuth\…`; new-era settings keys).
  SHA-256 `a79b894d…`. No version metadata; no `UE4SS.log` yet.
- UE4SS **3.0.0** flipped `FName` ctor default `FNAME_Find` → `FNAME_Add` — leading
  suspect for name-keyed DataTable lookups (H1 in [`docs/04-the-breakage.md`](../docs/04-the-breakage.md)).

**Learned (Inferred / open)**
- Exact experimental build that first breaks TFWWorkbench: **unknown** (researching).
- Exact UE4SS calls TFWWorkbench uses: **unread** (source audit pending).
- Known-good pin: **none on record** yet.

**Next**
- Fold workflow `wu3yvil3x` results into `docs/02`, `docs/04`, `docs/05`, and
  `data/compat.json`. Run the game once to capture the `UE4SS.log` version banner.
  See [`next-session.md`](next-session.md).

---

## 2026-07-13 — Verified research landed; leading hypothesis OVERTURNED

**Done**
- Workflow `wu3yvil3x` completed: 5 research finders → 14 adversarial verifications
  (**12 confirmed / 1 refuted / 1 uncertain**) → synthesis. ~1.1M tokens, 20 agents,
  0 errors.
- Rewrote `docs/02`, `docs/03`, `docs/04`, `docs/05`, `docs/00`, patched `docs/01`;
  replaced `data/compat.json` (5 rows) + `data/ue4ss-timeline.json`; pivoted the mod
  pillar (renamed `TFWWorkbenchCompatShim` → `TFWWorkbenchDoctor`, added
  `mod/rebuild-recipe.md` + `mod/README.md`).

**Learned (Verified)**
- **Root cause = C++ mod ABI mismatch**, not a behavior change. TFWWorkbench is a
  **C++/Lua hybrid** ([smotti/TFWWorkbench-Cpp](https://github.com/smotti/TFWWorkbench-Cpp))
  shipping a precompiled `dlls/main.dll` (219,136 B) that imports UE4SS symbols by
  decorated name. Newer UE4SS drops/renames one → `0x7F ERROR_PROC_NOT_FOUND` at
  load. Live: TFWWorkbench issue #2 (open); upstream RE-UE4SS #696 confirms 0x7F ==
  ABI incompatibility.
- **No stable UE4SS since v3.0.1 (2024-02-14).** "Latest" = one rolling
  `experimental-latest` prerelease, git-describe `v3.0.1-<N>-g<hash>`; current
  ~`v3.0.1-1011-gb50986bd`. xmake→CMake migration (PR #1067) *"cannot guarantee ABI
  compatability"* — the enabler.
- **Recommended pin:** ~`v3.0.1-848/-849` (~Jan 2026) — Nexus floor + inferred ABI
  baseline. But the Nexus "OR HIGHER" advice is now stale.
- **TFWWorkbench is authored/maintained by smotti** (GitHub repo owner).

**Overturned (this is why we verify)**
- The `FName` `FNAME_Find`→`FNAME_Add` flip — my day-1 leading suspect (H1, "HIGH")
  — is a **refuted red herring**: mod passes `FNAME_Add` explicitly; a C++ default
  isn't in the mangled symbol. Verification also refuted the Lua-default sub-claim.

**Learned (Inferred / open)**
- Exact first-breaking commit between `-849` and `-1011`: **not bisected**.
- Which specific export changed: resolvable via `dumpbin /exports` vs `main.dll`
  imports — **not yet done**.
- Direction ("newer breaks it") rests on mechanism + the origin-log complaint +
  issue #2, since no issue records the reporter's UE4SS build and issue #1's 0x7F was
  a user install error.

**Next**
- First-hand confirm via `UE4SS.log`; bisect; export-diff; pursue a rebuild. See
  [`next-session.md`](next-session.md).

---

## 2026-07-14 — H1 PROVEN at the symbol level (export-diff)

**Done**
- Downloaded TFWWorkbench v0.2.1 (official release; `main.dll` SHA-256 `24b05dc2…`,
  219,136 B) and statically diffed its imports against the local UE4SS.dll exports
  with `pefile`. Added a reusable [`tools/abi-diff.py`](../tools/abi-diff.py) and
  wrote up [`local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md).

**Learned (Verified — this is now proof, not inference)**
- `main.dll` imports **81** UE4SS symbols; **80 resolve** against the current
  UE4SS.dll (4,106 exports); **exactly 1 is missing**:
  `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ` = `UStruct::GetMinAlignment() ->
  int&`. One unresolved import → deterministic `0x7F ERROR_PROC_NOT_FOUND`. **H1 confirmed.**
- **What changed:** UE4SS narrowed `UStruct::MinAlignment` from `int32` to `int16`
  (return `H`→`F`) and moved the old `int&` accessor to a private `GetMinAlignmentBase`.
  It's a **re-signature, not a removal** — so a **clean recompile (no source change)
  fixes it** (`short&`→`int` converts implicitly).

**Learned (Inferred / open)**
- Exact upstream commit that narrowed `MinAlignment` lives in UE4SS's **Unreal SDK
  submodule** (not the main repo tree); not pinned. Doesn't affect the proof.

**Next**
- Task #2: recompile `main.dll` against current UE4SS and confirm it loads. See
  [`next-session.md`](next-session.md).

---

## 2026-07-14 — Rebuild attempt blocked by a private UE4SS dependency

**Done**
- Installed a full C++ toolchain (CMake 4.4.0, Ninja, Rust 1.97 msvc, MSVC Build
  Tools) and cloned RE-UE4SS @ `b50986bd`. Confirmed the mod build model (`cppmods/`
  + `add_subdirectory`, mode `Game__Shipping__Win64`).

**Learned (Verified) — the blocker**
- The public RE-UE4SS **does not build from a clean clone**: its Unreal SDK submodule
  `deps/first/Unreal` → `git@github.com:Re-UE4SS/UEPseudo.git` is **inaccessible** (the
  `Re-UE4SS` org 404s; `UEPseudo` 404s via web/API/SSH/HTTPS/codeload; no public forks;
  current `main` still points at the dead URL; the official CPP template inherits it).
  So `<Unreal/*>` headers (`UStruct.hpp`, …) can't be obtained → no compile.
- Consequence: a clean recompile is only possible for someone with an existing
  `UEPseudo` checkout / access — realistically the maintainer (smotti). Full forensics:
  [`local-evidence/2026-07-14-build-attempt.md`](../local-evidence/2026-07-14-build-attempt.md).

**Unaffected**
- The fix analysis stands: one re-signatured symbol, zero source changes. The build
  *environment* is gated, not the fix.

**Next**
- Either escalate the rebuild to the maintainer (smotti), or test the experimental
  no-recompile import-table patch in-game. User's call.

## 2026-07-15 — Bundle forensics: the AIO dispute is a *silent* version gap, not the ABI break

Triggered by a modding-chat dispute: Modder B circulated an "AIO packet" (the
Construction Vendor easy-install with the CV mod stripped); Modder A said it was
"incompatible with my mod / version of TFWWorkbench" and that his own All-In-One
works. Three bundles were analysed to settle which versions are correct.

**Learned (Verified — byte-identical, downloaded and hashed)**
- Both AIOs ship **stock upstream artifacts, unmodified**. Modder A's AIO = TFWWorkbench
  **0.2.1** + UE4SS **`v3.0.1-894-g2172883`**; Construction Vendor easy-install =
  TFWWorkbench **0.1.2** + UE4SS **`v3.0.1-848-g91b70e5`**. Each `UE4SS.dll` hashes
  identically to the DLL inside its official archive zip; each `Scripts/main.lua`
  hashes identically to its release.
- **TFWWorkbench has 5 releases, not 2** (0.1.0/0.1.1/0.1.2/0.2.0/0.2.1, all Jan 2026;
  0.2.1 is latest). `main.dll` is byte-identical across 0.1.0–0.2.0 — identify a copy
  by hashing `main.lua`, not the DLL.
- **The real finding:** every Codex Vendor JSON uses `"Action": "AddTo"`, added in
  **0.2.0**. 0.1.2's dispatch is an `if/elseif` over Add/Replace/Remove with **no
  `else`** → `AddTo` is dropped with **no error, no crash, no log line**. Modder B's
  packet doesn't fail; it **silently no-ops**. That is the whole dispute.
- **This is NOT the ABI break.** All four `main.dll` × `UE4SS.dll` combinations
  resolve **100%** of imports (81/81 and 83/83). Both shipped UE4SS builds predate the
  narrowing. Also: 0.2.1's `main.dll` works on `-848` too → the good ABI is a
  **window**, not a point.
- **Runtime proof:** Modder A's AIO ships its own `UE4SS.log` showing
  `Starting C++ mod 'TFWWorkbench'` (no `0x7F`) → `AddTo (Property) VendorData …
  001_CodexPatch.json` → `Set FName property 'RowName' to value: Codex.Grabber`. It
  demonstrably works end-to-end.

**Corrected (previous entries in this repo were WRONG)**
- ❌ *"The narrowing landed 2026-07-10..07-12."* Derived from **DLL mtimes**, which in
  a redistributed bundle are the **repacker's** timestamps. Modder A's `UE4SS.dll` is
  stamped 2026-07-10 but its banner `Git SHA #2172883` = commit `21728830cb49`,
  **2026-01-28** — and the byte hash proves the banner honest. **Real window:**
  UEPseudo `2d115713` (01-28) → `b2e876da` (06-25), one of **13** submodule bumps.
  **Never date a build from an mtime.**
- ❌ *"There is no tidy download for an old experimental build."* The **`experimental`**
  tag is a permanent archive of **851** builds that are never deleted (it is
  `experimental-**latest**` that wipes assets each build). Both bundles' UE4SS
  versions downloaded cleanly today. `docs/05` rewritten.
- ❌ *"Recommended pin `-848/-849`, confidence medium."* → **`-894`, verified**, with
  runtime proof. `-848` retained as verified ABI-only.
- ❌ *"Bisection needs building from source."* It needs **download + export dump** —
  `abi-diff.py` against each archived zip. The private UEPseudo blocks *source-level*
  bisection only.
- Also corrected: the user's install is `-1009`/`-1011` (not confidently `-1011`), and
  **downgrading within `-998..-1011` is useless** — all six pin the same broken
  submodule `b2e876da`.

**Changed**
- `data/compat.json` rewritten: 5-release map, 6 entries, 3 verified `works` rows.
  Added a `recommended` flag to the schema + `compat.py pin` (several combos now
  legitimately "work", so confidence alone silently fell back to file order).
- `docs/03` (release map + silent-failure section), `docs/05` (pin, downloads,
  bisection), `data/ue4ss-timeline.json` (source of record → `experimental`).
- New: [`local-evidence/2026-07-15-aio-bundle-forensics.md`](../local-evidence/2026-07-15-aio-bundle-forensics.md).

**Next**
- Bisect the 13 candidate bumps via archived zips → pin the exact breaking build.
- Unchanged: escalate the rebuild to smotti, or in-game test the patched `main.dll`.

## 2026-07-15 (later) — **BISECTED: the first breaking build is `v3.0.1-929-gcd556d70`**

Triggered by Modder C (TFW modding chat) posting `UE4SS_v3.0.1-823-g3e2d111.zip` as
"the version that was used while developing TFWWorkbench", and recalling that someone
had once bisected the break but the messages were lost. So we bisected it ourselves.

**Learned (Verified) — the answer**
- **Last good: `v3.0.1-894-g2172883`** (2026-01-28, UEPseudo `2d115713`, `int32&`).
- **First broken: `v3.0.1-929-gcd556d70`** (2026-01-30, UEPseudo `3a756005`, `int16&`).
- **The commit: `cd556d706a680af35379913006153e9807aabf4a`** — narknon,
  2026-01-30T23:02:24Z, *"chore: update UE submodule for FUObjectArray changes"*.
  Its **only** changed file is `deps/first/Unreal`.
- **Provably that commit:** `compare 21728830...cd556d70` = 35 commits, of which
  `cd556d70` is the **only** one touching the submodule → builds `895`–`928` still pin
  `2d115713` and are **good** (never archived). Good range = **`-823`…`-928`**;
  `-894` is the newest *downloadable* good build.
- **Mechanism:** those 35 commits are a **UVTD (vtable-dumper) overhaul** (2026-01-28..30),
  incl. `2313a76620` *"update macrosetter, membervar and vtable templates for UVTD
  changes"*. The regenerated Unreal layer emitted versioned getters
  (`GetMinAlignment506` / `GetMinAlignmentBase`) and narrowed `UStruct::GetMinAlignment`
  to `int16&`. **`GetMinAlignment` appears in no commit message** — collateral damage of
  an FUObjectArray refactor, which is why the community never found it.
- **UE 5.6 support (PR #977) is definitively NOT the cause** — merged 2025-08-22, an
  ancestor of good build `-894`.
- **Method:** binary search over the **39 archived builds** in `[894..1011]`, reading
  each zip's `UE4SS.dll` export table **in memory** (no disk writes). **5 downloads.**
  Shipped as [`tools/ue4ss-bisect.py`](../tools/ue4ss-bisect.py).

**Learned (Verified) — Modder C's `-823`**
- `-823-g3e2d111` (narknon, 2025-12-28) is real and **ABI-good**: 0.2.1's `main.dll`
  resolves **81/81** against it, 0.1.2's **83/83**; exports the `int32&` symbol.
- **PE `TimeDateStamp` corroborates his account independently:** 0.2.1's `main.dll` was
  linked **2026-01-20 15:26:44 UTC** (1h before the 0.2.1 release) → its SDK is a build
  **on/before 2026-01-20**, which **excludes `-894`** as the compile baseline and leaves
  `-823`/`-848`. Import analysis cannot separate those two (all 81 resolve on both).
- New general technique: **PE `TimeDateStamp` is the antidote to the mtime trap** — the
  linker stamps it inside the DLL, so it survives repacking. Added to `CLAUDE.md`.
- **Known blind spot recorded:** `-823`/`-848`/`-894` pin *different* UEPseudo commits
  (`4d476af9`/`53f54bb0`/`2d115713`), so struct/vtable **layout drift** is possible
  between them; `abi-diff.py` proves symbols *resolve*, not that layouts match. `-894`
  is empirically fine (Modder A's runtime log), but `-823` is closest to baseline.

**Changed**
- `data/compat.json`: the "-895..-997 unknown" bisection-gap entry **replaced** by a
  verified `-929` first-breaking entry; added verified `-823` entry; `-894` notes now
  state it is NOT the compile baseline. 7 entries, 4 works / 2 broken.
- `data/ue4ss-timeline.json`: exact breaking commit + the UVTD mechanism.
- `docs/02`, `docs/05` (bisection section → **SOLVED**), `CLAUDE.md` (answer banner +
  PE-timestamp rule + abi-diff blind spot).
- New tool: [`tools/ue4ss-bisect.py`](../tools/ue4ss-bisect.py).

**Next**
- Still open: the **fix** pillar — smotti rebuild (blocked on private UEPseudo), or
  in-game test of the patched `main.dll`. The *diagnosis* is now complete enough to
  hand upstream: `meta/issue-2-report.md` can name the exact breaking commit.
- Ask Modder C whether `-823` vs `-848` can be settled from the lost chat history.
