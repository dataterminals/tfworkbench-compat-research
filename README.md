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

> **Status:** `v0.1.0` — **root cause identified (2026-07-13),** via a verified,
> adversarially-checked research pass (12 confirmed / 1 refuted / 1 uncertain). One
> first-hand confirmation (read `UE4SS.log`) and a commit-level bisect remain open —
> tracked honestly in [`meta/research-log.md`](meta/research-log.md).

---

## ⚠️ The answer

**It's a C++ mod ABI mismatch.** TFWWorkbench ships a **precompiled C++
`main.dll`** (219 KB) that imports UE4SS symbols by decorated name. UE4SS has
shipped **no stable release since v3.0.1 (Feb 2024)** — "latest" is a **single
rolling experimental build** (now ~`v3.0.1-1011-gb50986bd`) whose changelog admits
the xmake→CMake migration *"cannot guarantee ABI compatability."* A build ~160
commits past the mod's ~Jan-2026 baseline no longer exports a symbol the DLL needs,
so Windows aborts the load with **`0x7F ERROR_PROC_NOT_FOUND`**. Live proof:
[TFWWorkbench issue #2](https://github.com/smotti/TFWWorkbench/issues/2) (open).

- **Ruled out** (our original suspect): the `FName` `FNAME_Find`→`FNAME_Add` default
  flip — the mod passes `FNAME_Add` explicitly; a C++ default isn't part of a mangled
  symbol.
- **Fix:** recompile `main.dll` against current UE4SS (keeps latest — the *"fixable
  probably"* path), or pin UE4SS to ~`v3.0.1-848/-849`.
- **Who's who:** TFWWorkbench is by **smotti** (GitHub repo owner). `terraru` (the
  origin-log modder) runs mods that *depend on* it — his complaint is about the
  dependency, not a mod he authored.

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
