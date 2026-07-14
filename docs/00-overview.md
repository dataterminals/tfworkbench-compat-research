# 00 — Overview: the TFWWorkbench × UE4SS compatibility problem

## The one-sentence problem

On **The Forever Winter** (Unreal Engine 5.4.2), updating **RE-UE4SS** to a newer
build breaks **TFWWorkbench** — because TFWWorkbench ships a **precompiled C++ DLL**
that is **ABI-locked** to the UE4SS it was built against, and UE4SS's rolling
experimental builds keep changing that ABI.

## Where this came from

A modder (terraru) in a TFW modding chat:

> "you can't use the latest ue4ss version when having TFWorkbench as a dependency…
> Not sure what version introduced some changes that breaks the mod."

Another modder: *"fixable (probably)."* ([`seed/running-log.txt`](../seed/running-log.txt).)

> **Plot twist we found:** `terraru` is the **C++ author of TFWWorkbench**
> (`ModAuthors = "terraru"` in `dllmain.cpp`), and the *"UE4SS MUST BE v3.0.1-848 OR
> HIGHER"* note on TFW Nexus mod 77 is theirs. terraru was describing the breakage
> of **their own mod's** dependency. The loop closes.

## The answer (verified 2026-07-13)

> **Root cause — C++ mod ABI mismatch.** TFWWorkbench's `dlls/main.dll` (219,136
> bytes) imports UE4SS C++ symbols by decorated name. UE4SS has shipped **no stable
> release since v3.0.1 (2024-02-14)**; "latest" is a **single rolling experimental
> build** (currently ~`v3.0.1-1011-gb50986bd`) whose own changelog says the
> xmake→CMake migration *"cannot guarantee ABI compatability."* A build ~160 commits
> past the mod's ~Jan-2026 baseline no longer exports a symbol the DLL needs, so the
> Windows loader aborts with **`0x7F ERROR_PROC_NOT_FOUND`** and `main.dll` never
> loads. Live proof: TFWWorkbench [issue #2](https://github.com/smotti/TFWWorkbench/issues/2)
> (open, 2026-07-14).

> **Ruled out:** the `FName` default flip (`FNAME_Find`→`FNAME_Add`) — *this was our
> original leading suspect, refuted by verification*: the mod passes `FNAME_Add`
> explicitly and a C++ default isn't part of a mangled symbol. Also ruled out: FName
> alignment (UE≤4.21 only) and any engine-version-support gap (UE5.4 supported since
> May 2024).

> **The fix (two options):**
> - **Recompile** `main.dll` against current UE4SS — no source change needed; keeps
>   you on latest. The *"fixable (probably)"* path. ([`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md))
> - **Pin** UE4SS to ~`v3.0.1-848/-849` (~Jan 2026), the ABI the shipped DLL
>   matches. Fragile to obtain (no historical zips retained).
>   ([`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md))

> **Honest caveat:** the *mechanism* (ABI) is strongly supported; the *direction*
> ("newer UE4SS specifically breaks it") rests on that mechanism + terraru's
> complaint + the open issue, since **no issue records the reporter's UE4SS build**,
> and issue #1's identical `0x7F` was closed as a user install error. Confirming
> first-hand = one game launch to read `UE4SS.log`.

## What this repo is

| Pillar | Where | What |
| --- | --- | --- |
| **Knowledge base** | [`docs/`](.) | the stack, UE4SS version reality, how TFWWorkbench's ABI is fragile, root-cause analysis, the fix. Verified-vs-inferred throughout. |
| **Compatibility tracker** | [`data/compat.json`](../data/compat.json) + [`tools/compat.py`](../tools/compat.py) | machine-readable *(UE4SS build × TFWWorkbench) → works/broken* matrix, queryable from the CLI (`pin`, `check --sha`, …). |
| **Fix pillar** | [`mod/`](../mod) | [`rebuild-recipe.md`](../mod/rebuild-recipe.md) (the real fix) + [`TFWWorkbenchDoctor`](../mod/TFWWorkbenchDoctor) (a diagnostic mod). |
| **Evidence** | [`local-evidence/`](../local-evidence), [`seed/`](../seed) | ground-truth forensics + the origin log. |

## How to read this repo

1. [`01-the-stack.md`](01-the-stack.md) — how TFW + bypass + UE4SS + TFWWorkbench fit.
2. [`02-ue4ss-versions.md`](02-ue4ss-versions.md) — no-stable-since-3.0.1, git-describe, the ABI enabler.
3. [`03-tfworkbench.md`](03-tfworkbench.md) — the C++/Lua hybrid and why its ABI is fragile.
4. [`04-the-breakage.md`](04-the-breakage.md) — root-cause analysis (H1–H4 + ruled out).
5. [`05-known-good-and-workarounds.md`](05-known-good-and-workarounds.md) — pin, downgrade, rebuild.

Provenance + what's next: [`meta/research-log.md`](../meta/research-log.md),
[`meta/next-session.md`](../meta/next-session.md).
