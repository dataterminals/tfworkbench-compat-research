# 👋 Next session — desktop pickup (written 2026-07-16)

Root cause is identified (C++ ABI mismatch) and the bisect is **closed**. The marker
contradiction that used to head this file is **closed too** (2026-07-16, later — see
[`research-log.md`](research-log.md), newest entry last). What's left is **one command on the
desktop**, the fix pillar, and outreach.

---

## ✅ 1. RESOLVED — the marker contradiction was never a contradiction

`Starting C++ mod 'TFWWorkbench'` is **mechanism-dependent**, not absent:

| Mod started via | Log line |
|---|---|
| **`mods.txt`** (`TFWWorkbench : 1`) | `Starting C++ mod 'TFWWorkbench'` |
| **`enabled.txt`** (per-mod file) | `Mod 'TFWWorkbench' has enabled.txt, starting mod.` |

Both of our logs use `enabled.txt` (TFWWorkbench is absent from the stock `mods.txt` and
ships its own `enabled.txt`), so neither emits it. Modder A's `-894` log used `mods.txt` and
does. **So `data/compat.json`'s `-894` citation is CORRECT — leave it.** And `Desktop.7z`
does **not** need re-checking for this: G's log has the marker because
[ForeverWinterModSetup](https://github.com/dataterminals/ForeverWinterModSetup) appends
`TFWWorkbench : 1` to `mods.txt`. That note was right.

> **Inferred, not source-confirmed.** The mechanism→marker mapping rests on a near-natural
> experiment (Modder A's log and ours are the same `-894` build, differing only in enable
> path). **Confirm against UE4SS `-894` source before relying on it.**

**Still true:** use `[TFWWorkbench] Registered Lua functions for mod` as the load probe — it
is `main.dll`'s own output and mechanism-independent.

## 🚩 2. Start here: one command on the desktop closes the `-848` datum

The `-848` log in
[`local-evidence/2026-07-16-stale-log-from-own-desktop/`](../local-evidence/2026-07-16-stale-log-from-own-desktop/NOTES.md)
is **the desktop's own** (it was found on the laptop, hence the original "ghost"). It proves
`-848` loads *some* TFWWorkbench `main.dll` at runtime — but **which version is unknown**, and
the earlier "0.1.2" claim was an unfounded inference (it came from the dead AIO story).

**On the desktop, run:**

```powershell
Get-FileHash "<game>\Windows\ForeverWinter\Binaries\Win64\ue4ss\Mods\TFWWorkbench\Scripts\main.lua" -Algorithm SHA256
# 2230fa8c… = 0.2.1   |   afe9a5b2… = 0.1.2
```

**Then** land the `-848 (cross-tested)` edit with an honest version half — and only then
drop its *"NOT runtime-tested"* caveat. **Do not** land it as previously written
(`runtime-verified for the 0.1.2 pairing`): that would put `confidence: verified` on a row
whose version half is a guess, and `tools/compat.py validate` would happily accept it.
`python tools/compat.py validate` after editing.

## ⚠️ 2. TFWWorkbenchDoctor rewrite — retarget before implementing

The proposal on record (*"parse UE4SS.log for `Starting C++ mod 'TFWWorkbench'` + absence
of `[0x7f]`"*) **must not ship as written.** Per §1 that line only appears on the `mods.txt`
path, so the probe reports **"broken"** for every install started via `enabled.txt` — which
is every **MO2** install and the **CV AIO's** own layout. Narrower than once thought, but it
lands squarely on our users. Retarget it at
`[TFWWorkbench] Registered Lua functions for mod` (mechanism-independent).

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
