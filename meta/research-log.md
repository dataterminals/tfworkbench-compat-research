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
- **TFWWorkbench is authored/maintained by smotti** (GitHub repo owner). *(Correction,
  2026-07-14: an earlier draft here claimed terraru was the C++ author, based on a
  `ModAuthors="terraru"` source string + a Nexus credit line — the user, a TFW-modding
  insider, corrected this: smotti made TFWWorkbench. terraru is the origin-log modder
  who runs mods that depend on it; his exact relationship to the project is unverified.)*

**Overturned (this is why we verify)**
- The `FName` `FNAME_Find`→`FNAME_Add` flip — my day-1 leading suspect (H1, "HIGH")
  — is a **refuted red herring**: mod passes `FNAME_Add` explicitly; a C++ default
  isn't in the mangled symbol. Verification also refuted the Lua-default sub-claim.

**Learned (Inferred / open)**
- Exact first-breaking commit between `-849` and `-1011`: **not bisected**.
- Which specific export changed: resolvable via `dumpbin /exports` vs `main.dll`
  imports — **not yet done**.
- Direction ("newer breaks it") rests on mechanism + terraru + issue #2, since no
  issue records the reporter's UE4SS build and issue #1's 0x7F was a user install error.

**Next**
- First-hand confirm via `UE4SS.log`; bisect; export-diff; pursue a rebuild. See
  [`next-session.md`](next-session.md).
