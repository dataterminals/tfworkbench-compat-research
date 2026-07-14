# 00 — Overview: the TFWWorkbench × UE4SS compatibility problem

## The one-sentence problem

On **The Forever Winter** (Unreal Engine 5.4.2), updating **RE-UE4SS** to a newer
build can break **TFWWorkbench** and every mod that depends on it — and nobody has
written down *which* build introduced the break or *why*.

## Where this came from

A modder (terraru) in a TFW modding chat:

> "you can't use the latest ue4ss version when having TFWorkbench as a dependency…
> Not sure what version introduced some changes that breaks the mod."

Another modder replied that it's *"fixable (probably)."* That exchange
([`seed/running-log.txt`](../seed/running-log.txt)) is the seed of this repo.

## Why it matters

TFWWorkbench is a **framework dependency**: it lets multiple content mods add/modify
items, weapons, and recipes at runtime by editing Unreal **DataTables**, instead of
each mod shipping conflicting static-asset overrides. If TFWWorkbench is down, a
whole class of TFW mods that depend on it are down too. And because UE4SS for a
UE5.4 game is delivered as **rolling experimental builds** (not tidy version
numbers), "just don't update" is harder advice to follow than it sounds — users
grab "latest" and it silently breaks.

## What this repo is

Four things, one investigation:

| Pillar | Where | What |
| --- | --- | --- |
| **Knowledge base** | [`docs/`](.) | The stack, UE4SS version history, how TFWWorkbench works, the root cause, and the fix. Verified-vs-inferred throughout. |
| **Compatibility tracker** | [`data/compat.json`](../data/compat.json) + [`tools/compat.py`](../tools/compat.py) | Machine-readable matrix of *(UE4SS build × TFWWorkbench version) → works/broken*, queryable from the CLI. |
| **Mod / patch** | [`mod/TFWWorkbenchCompatShim/`](../mod/TFWWorkbenchCompatShim) | A UE4SS mod skeleton to host the fix/shim once the root cause is confirmed. |
| **Evidence** | [`local-evidence/`](../local-evidence), [`seed/`](../seed) | Ground-truth forensics from a real install + the origin log. |

## Current status (2026-07-13)

> **Verified so far:**
> - TFW is UE **5.4.2**; the UE4SS it uses is a **patternsleuth experimental CI
>   build**, not stable 3.0.1 (see [`local-evidence/2026-07-13-local-install.md`](../local-evidence/2026-07-13-local-install.md)).
> - TFWWorkbench ([smotti/TFWWorkbench](https://github.com/smotti/TFWWorkbench),
>   latest **v0.2.1**, 2026-01-20) edits DataTables at runtime.
> - UE4SS **3.0.0** flipped the `FName` constructor default from `FNAME_Find` to
>   `FNAME_Add` — a prime suspect for name-keyed DataTable lookups.

> **Still open (being researched):**
> - The exact experimental build that first broke TFWWorkbench.
> - The precise mechanism (FName default? resolver change? engine-offset drift?).
> - The known-good build to pin to, and whether a code fix is viable.

Track the open items in [`meta/research-log.md`](../meta/research-log.md) and
[`meta/next-session.md`](../meta/next-session.md).

## How to read this repo

1. [`01-the-stack.md`](01-the-stack.md) — how TFW + signature bypass + UE4SS +
   TFWWorkbench fit together (the mental model).
2. [`02-ue4ss-versions.md`](02-ue4ss-versions.md) — the UE4SS release/experimental
   timeline and which changes are dangerous to a DataTable mod.
3. [`03-tfworkbench.md`](03-tfworkbench.md) — what TFWWorkbench does and the exact
   UE4SS surface it depends on.
4. [`04-the-breakage.md`](04-the-breakage.md) — root-cause analysis.
5. [`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md) — the pin
   + downgrade steps + the shim plan.
