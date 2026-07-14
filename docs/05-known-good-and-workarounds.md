# 05 — Known-good build, downgrade steps, and the fix plan

> **Status: interim guidance.** The specific known-good build and the confirmed fix
> land here once [`04-the-breakage.md`](04-the-breakage.md) is resolved. Until then,
> follow the safe interim advice below.

## Interim guidance (safe today)

1. **Do not update UE4SS on a working TFWWorkbench setup.** If TFWWorkbench works
   for you now, record your `UE4SS.dll` SHA-256 (`python tools/compat.py check
   --sha <hash>`… add it if untracked) and keep that build. This is exactly the
   "don't use latest" advice from the origin log.
2. **If you're already broken,** downgrade UE4SS to the last build that predates the
   break (see the pin once confirmed), reinstall TFWWorkbench v0.2.1, and re-test.
3. **Capture your build's identity** before changing anything: SHA-256 of
   `UE4SS.dll`, and the `UE4SS.log` banner after one launch.

## The recommended pin

> ⏳ **Pending confirmation.** `tools/compat.py pin` will name the best `works`
> entry once one is recorded in [`data/compat.json`](../data/compat.json). Right
> now there is no confirmed-working build on record — only the local untested
> experimental build.

When known, this section states: the exact build (label + date + `UE4SS.dll`
SHA-256 + download URL), and why it's the recommended floor.

## How to downgrade / get an old experimental build

UE4SS experimental builds are CI artifacts. Sources, in order of durability:
- **GitHub Releases** assets (stable + any retained experimental tags):
  <https://github.com/UE4SS-RE/RE-UE4SS/releases>
- **GitHub Actions artifacts** for a specific commit (via the Actions tab or
  `nightly.link`), when a precise commit is needed.
- **TFW Nexus mod 61** old-files section (if it archives the UE4SS build the TFW
  community standardized on).

> ⏳ Exact links + the specific good build are filled after research.

## Reproducing the break (bisect protocol)

To pin the good→bad boundary precisely:
1. Fix the variables: TFWWorkbench **v0.2.1**, one TFW version, one signature-bypass
   build, one representative content mod that depends on TFWWorkbench.
2. Swap **only** `UE4SS.dll` (+ matching `dwmapi.dll`) between candidate builds.
3. Launch once per build; record from `UE4SS.log`: does TFWWorkbench load, find its
   tables, and apply rows? Note the symptom on failure.
4. Log each result as a row in [`data/compat.json`](../data/compat.json)
   (`confidence: verified`, with the `UE4SS.dll` SHA-256).
5. Binary-search the experimental builds between the newest **works** and oldest
   **broken** to find the boundary build; correlate with the UE4SS changelog/commits.

## The fix (compat shim) — plan

If the root cause is a UE4SS-side behavior change that a mod can compensate for
(e.g. an `FName` default or a lookup that now needs an explicit flag), the fix ships
as a small UE4SS mod that loads **before** TFWWorkbench and restores the assumed
behavior, or as a patched TFWWorkbench fork. Skeleton and design notes:
[`mod/TFWWorkbenchCompatShim/`](../mod/TFWWorkbenchCompatShim).

Decision gate: **do not** write shim code until H-whatever is confirmed in
[`04-the-breakage.md`](04-the-breakage.md) — a shim against the wrong cause is worse
than none.
