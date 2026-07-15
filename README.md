# tfworkbench-compat-research

Figuring out **why newer [RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) builds
break [TFWWorkbench](https://github.com/smotti/TFWWorkbench)** on **The Forever
Winter** (Fun Dog Studios, Unreal Engine 5.4.2, Steam App ID `2828860`) — and
fixing it.

TFWWorkbench is a runtime **DataTable** editor: it lets multiple content mods add
items/weapons/recipes from JSON without clobbering each other. It's a framework
*dependency*, so when it breaks, a whole class of TFW mods break with it. A modder
put it plainly:

> "you can't use the latest ue4ss version when having TFWorkbench as a dependency…
> not sure what version introduced some changes that breaks the mod." — and someone
> else: *"Fixable (probably)."*
> ([`seed/running-log.txt`](seed/running-log.txt) — the origin of this repo.)

> **Status:** `v0.2.0` — **root cause PROVEN at the symbol level (2026-07-14).** A
> static import/export diff pins the break to a single UE4SS symbol; run it yourself
> with [`tools/abi-diff.py`](tools/abi-diff.py). See
> [`meta/research-log.md`](meta/research-log.md).

---

## ⚠️ The answer

**It's a C++ mod ABI mismatch — and we've proven the exact symbol.** TFWWorkbench
ships a **precompiled C++ `main.dll`** (219 KB) that imports **81** UE4SS symbols by
decorated name. Against the current UE4SS.dll, **80 resolve and exactly 1 doesn't**:

```
?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ   (UStruct::GetMinAlignment() -> int&)
```

UE4SS **narrowed that method's return type from `int32&` to `int16&`**, so the old
mangled symbol vanished. One unresolved import → the loader aborts with **`0x7F
ERROR_PROC_NOT_FOUND`** and `main.dll` never loads. UE4SS has shipped **no stable
release since v3.0.1 (Feb 2024)** — "latest" is a rolling experimental build whose
changelog admits the xmake→CMake migration *"cannot guarantee ABI compatability."*
Reproduce: `python tools/abi-diff.py <main.dll> <UE4SS.dll>`. Live report:
[TFWWorkbench issue #2](https://github.com/smotti/TFWWorkbench/issues/2) (open).

- **Ruled out** (our original suspect): the `FName` `FNAME_Find`→`FNAME_Add` default
  flip — the mod passes `FNAME_Add` explicitly; a C++ default isn't part of a mangled
  symbol.
- **Fix:** recompile `main.dll` against current UE4SS — and the symbol proof shows
  the method still *exists* (just returns `int16&` now), so it's a **clean recompile,
  zero source changes** (`short&`→`int` converts implicitly). Or pin UE4SS to
  **`v3.0.1-894-g2172883`** + TFWWorkbench **0.2.1** (verified working; grab it from
  the permanent [`experimental`](https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental)
  archive) — `python tools/compat.py pin`.
- **Not every "it doesn't work" is the ABI break.** TFWWorkbench **0.1.x silently
  ignores** JSON `Action`s it doesn't know (e.g. `AddTo`, added in 0.2.0) — no error,
  no log line, mod just does nothing. See
  [`local-evidence/2026-07-15-aio-bundle-forensics.md`](local-evidence/2026-07-15-aio-bundle-forensics.md).
- **Author:** TFWWorkbench is by **smotti** (`smotti/TFWWorkbench` on GitHub); the
  origin-log complaint is from a modder whose mods *depend on* it.

Local forensics (the install this was verified against):
[`local-evidence/2026-07-13-local-install.md`](local-evidence/2026-07-13-local-install.md).

---

## What's here (four pillars)

| Pillar | Path | Status |
| --- | --- | --- |
| 📚 **Knowledge base** | [`docs/`](docs) | the stack, UE4SS timeline, how TFWWorkbench works, root-cause analysis, fixes |
| 🧮 **Compat tracker** | [`data/compat.json`](data/compat.json) · [`tools/compat.py`](tools/compat.py) | machine-readable matrix + CLI |
| 🔧 **Fix** | [`mod/`](mod) | [`rebuild-recipe.md`](mod/rebuild-recipe.md) (recompile `main.dll`) + [`TFWWorkbenchDoctor`](mod/TFWWorkbenchDoctor) (diagnostic mod) |
| 🔎 **Evidence** | [`local-evidence/`](local-evidence) · [`seed/`](seed) | forensics + origin log |

## Quick start

```bash
# Is my UE4SS build known-compatible?
python tools/compat.py check --sha <your UE4SS.dll SHA-256>

# What should I install?
python tools/compat.py pin

# See everything tracked
python tools/compat.py list
```

Get your hash: `sha256sum ".../Binaries/Win64/ue4ss/UE4SS.dll"` (or PowerShell
`Get-FileHash … -Algorithm SHA256`). More: [`tools/README.md`](tools/README.md).

## Read the investigation

1. [`docs/00-overview.md`](docs/00-overview.md) — the problem, start here
2. [`docs/01-the-stack.md`](docs/01-the-stack.md) — TFW + bypass + UE4SS + TFWWorkbench
3. [`docs/02-ue4ss-versions.md`](docs/02-ue4ss-versions.md) — UE4SS timeline & dangerous changes
4. [`docs/03-tfworkbench.md`](docs/03-tfworkbench.md) — what TFWWorkbench depends on
5. [`docs/04-the-breakage.md`](docs/04-the-breakage.md) — root-cause analysis
6. [`docs/05-known-good-and-workarounds.md`](docs/05-known-good-and-workarounds.md) — the pin + the fix

## Method & house rules

Verified-vs-inferred is kept explicit throughout; every claim cites *how* we know
it, and provenance goes in [`meta/research-log.md`](meta/research-log.md). This repo
is public and meant to be picked up cold by another modder (or their AI) — see
[`CLAUDE.md`](CLAUDE.md).

## Related repos

- [`ForeverWinterMO2Support`](../ForeverWinterMO2Support) — the TFW modding stack, verified locally
- [`forever-winter-datamine`](../forever-winter-datamine) — TFW data
- [`grb-modding-knowledgebase`](../grb-modding-knowledgebase) — the documentation-discipline template

## License

MIT — see [`LICENSE`](LICENSE).

*Not affiliated with Fun Dog Studios, the RE-UE4SS project, or smotti/TFWWorkbench.
This is independent compatibility research; all trademarks belong to their owners.*
