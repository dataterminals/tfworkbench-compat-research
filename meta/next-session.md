# Next session — what to do next

Root cause is identified (C++ ABI mismatch). Remaining work is first-hand
confirmation, precision, and shipping a fix. See [`research-log.md`](research-log.md).

## 1. Confirm the failure mode first-hand  (cheap, high value)
Launch TFW once with TFWWorkbench v0.2.1 installed and UE4SS active, then read
`…\Binaries\Win64\ue4ss\UE4SS.log`:
- Look for `Failed to load dll …main.dll… error: [0x7f]` → confirms the ABI break (H1).
- Capture the **git-describe version banner** at the top → record it + the
  `UE4SS.dll` SHA-256 (`a79b894d…`) in
  [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md)
  and flip the local `compat.json` row from `inferred` to `verified`.
- Or run [`mod/TFWWorkbenchDoctor`](../mod/TFWWorkbenchDoctor) for the same signal.

## 2. Identify the exact changed export  ✅ DONE (2026-07-14)
Proven via [`tools/abi-diff.py`](../tools/abi-diff.py): the single missing symbol is
`?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ` (`UStruct::GetMinAlignment()->int&`,
narrowed by UE4SS to `int16&`). See
[`local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md).

## 3. Bisect the first-breaking build  (optional precision)
Between `-849` (works) and `-1011` (broken), build `main.dll` against successive
UE4SS commits (or just check export presence per build) to find the boundary. Log
each result to [`data/compat.json`](../data/compat.json) with its `UE4SS.dll` SHA-256.

## 4. Ship a fix  ⚠️ rebuild is externally BLOCKED (2026-07-14)
- A from-source rebuild was attempted; it is **blocked** because UE4SS's Unreal SDK
  submodule (`Re-UE4SS/UEPseudo`) is private/removed and unobtainable — see
  [`local-evidence/2026-07-14-build-attempt.md`](../local-evidence/2026-07-14-build-attempt.md).
  A clean recompile therefore needs the **maintainer (smotti)** or someone with a
  pre-existing `UEPseudo` checkout. The fix itself is still trivial (one symbol, zero
  source changes).
- **Options from here:**
  - **Escalate:** post the diagnosis (exact symbol + "clean recompile") on TFWWorkbench
    issue #2 so smotti can rebuild. (Outward-facing — confirm with the user first.)
  - **Experimental patch:** try the no-recompile import-table patch and **load-test it
    in-game** (only the user can run the game). See [`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md).
  - **Pin instead (SOLVED, 2026-07-15):** install **UE4SS `v3.0.1-894-g2172883`** +
    **TFWWorkbench 0.2.1** — verified working with in-game proof. One permanent URL:
    `https://github.com/UE4SS-RE/RE-UE4SS/releases/download/experimental/UE4SS_v3.0.1-894-g2172883.zip`.
    See [`docs/05`](../docs/05-known-good-and-workarounds.md).

## ✅ Bisection — DONE (2026-07-15)
First breaking build = **`v3.0.1-929-gcd556d70`** (2026-01-30); last good =
**`-894-g2172883`**. See [`docs/05`](../docs/05-known-good-and-workarounds.md) and
[`tools/ue4ss-bisect.py`](../tools/ue4ss-bisect.py). **The "which build breaks it"
question this repo was created to answer is now closed.**

## Top of the list now
- **Hand the diagnosis upstream.** [`meta/issue-2-report.md`](issue-2-report.md) can
  now name the exact breaking commit (`cd556d706a68`) + the UVTD mechanism + the
  working pin. Still **not posted** — outward-facing, confirm with the user first.
- **Tell the TFW scene the pin:** TFWWorkbench 0.2.1 + UE4SS `-894` (or `-823`).
  Correct the stale *"-848 or higher"* folklore — "or higher" is what breaks it.

## Open questions parking lot
- Exact UE4SS commit smotti built v0.2.1 against (not pinned in the repo). Bounded:
  ABI-compatible with both `-848` and `-894`, so it's a pre-narrowing build.
- Will smotti (maintainer) rebuild? (no repo activity since 2026-01-20.)
- Does H2 (TObjectPtr smart-pointer rework, PR #850) ever manifest as a
  load-then-crash instead of a clean 0x7F? Only relevant if a rebuilt DLL loads but
  crashes at apply time.
