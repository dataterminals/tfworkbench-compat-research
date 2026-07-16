# 👋 Next session — desktop pickup (written 2026-07-16)

Root cause is identified (C++ ABI mismatch) and the bisect is **closed**. What's left is
one **open contradiction**, the fix pillar, and outreach. See
[`research-log.md`](research-log.md) — newest entry last.

---

## 🚩 1. Start here: the marker contradiction (blocks two edits)

Last night's ghost-log find
([`local-evidence/2026-07-16-ghost-log-from-cv-aio/`](../local-evidence/2026-07-16-ghost-log-from-cv-aio/NOTES.md))
proved that **`Starting C++ mod` is a false-negative marker** — zero hits across 2,294
lines of a log whose C++ half demonstrably loaded. The real marker is
`[TFWWorkbench] Registered Lua functions for mod` (no `[Lua]` prefix ⇒ emitted by
`main.dll`).

But [`data/compat.json`](../data/compat.json)'s **`-894` entry still cites**
*"the bundle's own shipped UE4SS.log (2026-07-14) shows `Starting C++ mod TFWWorkbench`"*
as its runtime proof — a string absent from every log we hold.

**Resolve before editing either entry.** Re-check **`Desktop.7z`** — it holds **G's `-894`
log**, which is a *separate artifact* from the AIO-shipped `-894` log the compat.json entry
quotes. Don't conflate them. Either the entry quotes a log we haven't re-examined, or the
note is wrong.

> The `-894` **runtime claim itself is not in doubt** — the `AddTo (Property) VendorData`
> and `Set FName property RowName` lines are independent proof the edit landed. Only the
> *marker* is in question. Fix the citation, not the verdict.

**Then land these two together** (held back deliberately — they touch the same entries):
- Upgrade the **`-848 (cross-tested)`** entry from ABI-only → **runtime-verified for the
  0.1.2 pairing**; drop its *"NOT runtime-tested"* caveat. (`-848` + **0.2.1** stays
  ABI-only — the ghost log says nothing about it.)
- Correct the `-894` entry's marker citation per whatever `Desktop.7z` shows.
- `python tools/compat.py validate` after editing.

## ⚠️ 2. TFWWorkbenchDoctor rewrite — retarget before implementing

The proposal on record (*"parse UE4SS.log for `Starting C++ mod 'TFWWorkbench'` + absence
of `[0x7f]`"*) **would reproduce the exact false negative it exists to fix.** Retarget it at
`[TFWWorkbench] Registered Lua functions for mod`.

Also: grep the **bracketed** `[0x7f]` — bare `0x7f` matches inside every `0x7ff6…` address
the scanner prints. Keep the mod read-only.

## 3. Ship a fix — ⚠️ rebuild still externally BLOCKED

- A from-source rebuild is **blocked**: UE4SS's Unreal SDK submodule (`Re-UE4SS/UEPseudo`)
  is private/removed — see
  [`local-evidence/2026-07-14-build-attempt.md`](../local-evidence/2026-07-14-build-attempt.md).
  Needs **smotti** or someone holding a pre-existing `UEPseudo` checkout. The fix itself is
  trivial: one symbol, zero source changes.
- **Escalate:** [`meta/issue-2-report.md`](issue-2-report.md) can now name the exact
  breaking commit (`cd556d706a68`) + the UVTD mechanism + the working pin. **Still not
  posted — outward-facing, confirm with the user first.**
- **Experimental patch:** the no-recompile import-table patch needs an **in-game load
  test** (only the user can run the game). See [`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md).
- **Or just pin (SOLVED 2026-07-15):** UE4SS **`-894-g2172883`** + TFWWorkbench **0.2.1**,
  in-game verified. `https://github.com/UE4SS-RE/RE-UE4SS/releases/download/experimental/UE4SS_v3.0.1-894-g2172883.zip`

## 4. Tell the TFW scene the pin

TFWWorkbench 0.2.1 + UE4SS `-894` (or `-823`, closest-to-baseline). Correct the stale
*"-848 or higher"* folklore — **"or higher" is what breaks it.** That floor is about
Construction Vendor, not TFWWorkbench.

---

## ✅ Closed — don't redo these

- **Bisection (2026-07-15).** First breaking build = **`v3.0.1-929-gcd556d70`** (2026-01-30,
  *"chore: update UE submodule for FUObjectArray changes"*); last good = **`-894-g2172883`**.
  Safe range `-823`…`-928`. Rode in on a **UVTD regeneration**, named in no commit message.
  See [`tools/ue4ss-bisect.py`](../tools/ue4ss-bisect.py). **The question this repo was
  created to answer is closed.**
- **Exact changed export (2026-07-14).** `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ`
  — narrowed by UE4SS from `int32&` to `int16&`. See
  [`local-evidence/2026-07-14-abi-symbol-proof.md`](../local-evidence/2026-07-14-abi-symbol-proof.md).
- **Runtime proof for `-848` + 0.1.2 (2026-07-16).** The ghost log. Its *compat.json* entry
  is item 1 above.

## Open questions parking lot

- Exact UE4SS commit smotti built 0.2.1 against. Bounded: PE `TimeDateStamp` =
  2026-01-20 15:26:44 UTC ⇒ a build on/before that date ⇒ **`-823` or `-848`**, not `-894`.
  Import-set analysis **cannot** separate `-823` from `-848` (all 81 resolve on both).
- Ask **Modder C** whether `-823` vs `-848` can be settled from the lost chat history.
- Will smotti rebuild? (No repo activity since 2026-01-20.)
- Does H2 (TObjectPtr rework, PR #850) ever manifest as load-then-crash instead of a clean
  `0x7F`? Only relevant once a rebuilt DLL loads.

---

## Traps this repo has already fallen into (re-read before trusting a log)

1. **Never date a build from an mtime.** In a redistributed bundle the mtime is the
   *repacker's*. Use the PE `TimeDateStamp`, the `Git SHA #` banner, or the DLL SHA-256.
   A previous session was wrong by ~5 months this way.
2. **Never trust a `UE4SS.log` without checking its paths resolve on the machine you're
   standing on.** MO2's Overwrite never self-clears and outranks every mod — a log that
   arrived *inside a mod archive* sits in exactly the right drawer looking authoritative
   forever. That's the whole 2026-07-16 story.
3. **Import/export diffing has a blind spot.** It proves symbols *resolve*; it cannot see
   struct/vtable layout drift. "81/81 resolve" means *will load*, not *is the baseline*.

> To resume: **"resolve the marker contradiction — check Desktop.7z, then land the compat.json edits."**
