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
