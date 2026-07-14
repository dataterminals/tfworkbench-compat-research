# Next session — what to do next

Priority order. Check [`research-log.md`](research-log.md) for the latest state.

## 1. Fold in the research workflow results  (blocked on workflow `wu3yvil3x`)
When the verified-research workflow finishes, take its `synthesis` object and:
- Extend the UE4SS timeline table in [`docs/02-ue4ss-versions.md`](../docs/02-ue4ss-versions.md)
  and [`data/ue4ss-timeline.json`](../data/ue4ss-timeline.json).
- Promote/refute hypotheses in [`docs/04-the-breakage.md`](../docs/04-the-breakage.md).
- Fill the pin + downgrade links in [`docs/05-known-good-and-workarounds.md`](../docs/05-known-good-and-workarounds.md).
- Add `compatMatrix` rows to [`data/compat.json`](../data/compat.json) (set
  `confidence` honestly: `reported` for community claims, `verified` only for
  first-hand tests). Re-run `python tools/compat.py validate`.

## 2. Capture the local UE4SS version banner  (first-hand, high value)
Launch TFW once with UE4SS active, then read the top of
`…\Binaries\Win64\ue4ss\UE4SS.log` — it prints the exact version/commit. Record it
in [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md)
and as a `compat.json` entry keyed by the `UE4SS.dll` SHA-256 `a79b894d…`.

## 3. Read the TFWWorkbench source
Confirm which UE4SS calls it uses (Lua vs C++; `StaticFindObject`, `FName` handling,
row iteration). This turns the H1–H4 hypotheses in `docs/04` from inferred to
grounded. Link exact files/lines.

## 4. Bisect (if a repro is set up)
Follow the bisect protocol in `docs/05`. Swap only `UE4SS.dll`(+`dwmapi.dll`)
between experimental builds with TFWWorkbench v0.2.1 fixed; log each result to
`compat.json` with its SHA-256. Binary-search to the boundary build.

## 5. Only after a cause is CONFIRMED: implement the shim
Flip `ENABLE_FIX` in [`mod/TFWWorkbenchCompatShim/Scripts/main.lua`](../mod/TFWWorkbenchCompatShim/Scripts/main.lua)
and implement compensation for the confirmed cause. Test load-order (shim above
TFWWorkbench in `mods.txt`).

## Open questions parking lot
- Does the Vortex extension (Nexus 121) pin a UE4SS build, or pull `experimental-latest`?
- Did smotti ever note a target UE4SS build for v0.2.1?
- Is there already a community fork/patch of TFWWorkbench for newer UE4SS?
