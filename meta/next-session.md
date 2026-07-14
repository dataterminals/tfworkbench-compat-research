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

## 2. Identify the exact changed export  (makes H1 airtight)
On the installed build: `dumpbin /exports UE4SS.dll` (or `llvm-nm`) and
`dumpbin /imports main.dll`; diff the decorated names to find which UE4SS symbol
`main.dll` needs that current UE4SS no longer provides. That names the precise break.

## 3. Bisect the first-breaking build  (optional precision)
Between `-849` (works) and `-1011` (broken), build `main.dll` against successive
UE4SS commits (or just check export presence per build) to find the boundary. Log
each result to [`data/compat.json`](../data/compat.json) with its `UE4SS.dll` SHA-256.

## 4. Ship a fix
- **Preferred:** follow [`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md) —
  recompile `main.dll` against current UE4SS, test, add a `works` row, and offer it
  upstream to smotti (maintainer; issue #2 is open and unanswered).
- **Fallback for users now:** document a reliable way to obtain a ~`v3.0.1-848/-849`
  UE4SS build (a working download/mirror is currently **unconfirmed** — see the
  fragility notes in [`docs/05`](../docs/05-known-good-and-workarounds.md)).

## Open questions parking lot
- Exact UE4SS commit smotti built v0.2.1 against (not pinned in the repo).
- Is an archived `v3.0.1-848` zip obtainable (Nexus old-files / TFW Discord)?
- Will smotti (maintainer) rebuild? (no repo activity since 2026-01-20.)
- Does H2 (TObjectPtr smart-pointer rework, PR #850) ever manifest as a
  load-then-crash instead of a clean 0x7F? Only relevant if a rebuilt DLL loads but
  crashes at apply time.
