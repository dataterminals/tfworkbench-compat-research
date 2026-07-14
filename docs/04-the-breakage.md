# 04 — The breakage: root-cause analysis

> **Status: hypotheses under verification.** This is the analytical heart of the
> repo. Each hypothesis below pairs a UE4SS change
> ([`02-ue4ss-versions.md`](02-ue4ss-versions.md)) with a TFWWorkbench dependency
> ([`03-tfworkbench.md`](03-tfworkbench.md)) and a predicted symptom. The research
> workflow (`wu3yvil3x`) + an in-game repro will confirm/refute each and promote
> the winner to **Verified**.

## Method

1. Establish the **known-good** build (the one TFWWorkbench v0.2.1 was authored
   against) and the **known-bad** build (a current experimental, e.g. the local
   2026-07-12 install).
2. For each candidate cause, ask: *does it produce the symptom users report, and
   does its introduction date line up with the break?*
3. Confirm with a **bisect** across experimental builds (see
   [`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md)) and, if
   possible, by reading the TFWWorkbench source to see which call actually fails.

## Candidate root causes (ranked, pending confirmation)

### H1 — `FName` default `FNAME_Find` → `FNAME_Add` mismatch  ·  likelihood: HIGH
DataTable rows are keyed by `FName`. TFWWorkbench must turn a row-name string into
an `FName` to find the row. If it (or the UE4SS API it calls) relied on the old
default meaning "find existing," a build where the default is "add if missing"
changes lookup behavior — a wrong/new name entry instead of the intended row.
- **Predicted symptom:** rows silently not applied, or a mismatched/`None` row;
  possibly a name-table entry created that never matches.
- **Confirm by:** checking whether TFWWorkbench passes an explicit `EFindName`, and
  whether the break coincides with a build that changed this default.

### H2 — resolver / engine-offset drift on UE5.4.2  ·  likelihood: MEDIUM-HIGH
patternsleuth resolvers (`StaticFindObject`, `GUObjectArray`, `FUObjectHashTables`,
`StaticConstructObjectInternal`, `fname`) can shift or mis-fire between experimental
builds on the same engine. A mis-resolved object-lookup path means TFWWorkbench
never finds the DataTables.
- **Predicted symptom:** "table not found," nothing applied, or a hard crash during
  the workbench's scan/apply step; often correlates with a UE4SS-side warning in
  `UE4SS.log`.
- **Confirm by:** diffing resolver behavior across the good/bad builds; reading
  `UE4SS.log` at the failure.

### H3 — `FName` alignment 8 → 4 layout mismatch  ·  likelihood: LOW-MEDIUM
If a build changes `FName` alignment and TFWWorkbench (or a cached AOB) reads
`FName` fields at the old layout, comparisons/keys corrupt.
- **Predicted symptom:** garbled names, wrong rows, intermittent crashes.

### H4 — Lua API/behavior change  ·  likelihood: LOW-MEDIUM
Changes to `FindObject`/`StaticFindObject` return semantics, `ObjectProperty = nil`
support, or `IsValid()` reachability could make previously-valid TFWWorkbench code
mis-behave.
- **Predicted symptom:** Lua error in `UE4SS.log` naming a changed function.

## Evidence board (fill as it arrives)

| Signal | Source | Supports | Status |
| --- | --- | --- | --- |
| `FName` default flip exists (3.0.0) | UE4SS releases | H1 | Verified (recon) |
| patternsleuth resolvers present in local DLL | local binary scan | H2 | Verified |
| TFWWorkbench issue: "broke after UE4SS update" | ⏳ workflow | H1–H4 | pending |
| Exact good/bad build dates line up with a change | ⏳ workflow | (winner) | pending |
| `UE4SS.log` error at failure | ⏳ in-game repro | (winner) | pending |

## Deciding the winner

The confirmed cause is the one that (a) has a source-level or log-level fingerprint
in the TFWWorkbench failure, **and** (b) whose introduction date matches the
good→bad boundary from the bisect. Once confirmed, it drives the fix design in
[`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md) and the shim
in [`mod/TFWWorkbenchCompatShim/`](../mod/TFWWorkbenchCompatShim).
