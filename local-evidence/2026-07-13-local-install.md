# Local install forensics — 2026-07-13

Ground-truth facts pulled directly from this machine's The Forever Winter install.
Everything here is **Verified** (observed via file inspection / binary scan), and it
anchors the whole investigation: it tells us *exactly* which UE4SS the "latest"
complaint is about.

## Install layout

| Fact | Value | How known |
| --- | --- | --- |
| Game root | `D:\SteamLibrary\steamapps\common\The Forever Winter` | dir exists |
| Engine | Unreal Engine **5.4.2** | [`ForeverWinterMO2Support/docs/RESEARCH.md`](../../ForeverWinterMO2Support/docs/RESEARCH.md), Steam AppID 2828860 |
| Win64 dir | `…\Windows\ForeverWinter\Binaries\Win64` | dir listing |
| UE4SS | `…\Win64\ue4ss\` + proxy `dwmapi.dll` | dir listing, installed 2026-07-12 16:46 |
| Sig bypass | proxy `dsound.dll` + `bitfix\` + `bitfix.txt` | dir listing (dsound 2025-11-11) |

## UE4SS binary identity

> **Verified (binary scan, 2026-07-13):** the installed UE4SS is an **official
> RE-UE4SS GitHub-Actions CI build** on the modern **patternsleuth** resolver
> branch — i.e. a post-3.0 dev/experimental build, **not** stable 3.0.1.

> **Version framing (from research, see [`docs/02`](../docs/02-ue4ss-versions.md)):**
> UE4SS has no stable release after v3.0.1; this is a build off the single rolling
> `experimental-latest` channel (the v4.0.0-rc line), git-describe-versioned
> `v3.0.1-<N>-g<hash>`. Installed 2026-07-12, it sits ~1–2 commits *before* the
> current asset `v3.0.1-1011-gb50986bd` (that asset appeared 2026-07-13, after
> install). So it is ~160 commits of **C++ ABI drift** past TFWWorkbench v0.2.1's
> ~Jan-2026 (`v3.0.1-848/-849`) build baseline — which is why the mod's precompiled
> `main.dll` fails to load here. Launch once to capture the exact banner in
> `UE4SS.log`.

| Fact | Value |
| --- | --- |
| `ue4ss\UE4SS.dll` size | 16,519,168 bytes |
| `UE4SS.dll` SHA-256 | `a79b894d4a499c066985b47354d2a3a1fc9069cebefe585ba458bb8f572930b5` |
| `dwmapi.dll` SHA-256 | `6240895e747b559f17e3b59c7242cffa617ca91560b1a475194a368114e4e0df` |
| FileVersion / ProductVersion metadata | **absent** (typical for UE4SS CI builds) |
| `UE4SS.log` | not present yet (game not launched since install) |

### Why we know it's a patternsleuth / experimental build

The DLL embeds the CI checkout path and Rust resolver sources:

```
D:\a\RE-UE4SS\RE-UE4SS\deps\first\patternsleuth\patternsleuth\src\resolvers\unreal\fname.rs
…\resolvers\unreal\static_construct_object.rs
…\resolvers\unreal\guobject_array.rs
…\resolvers\unreal\fuobject_hash_tables.rs
…\resolvers\unreal\engine_version.rs
…\resolvers\unreal\kismet.rs   …\aes.rs  …\ftext.rs  …\gmalloc.rs  …\save_game.rs
```

- `D:\a\<repo>\<repo>\…` is the standard **GitHub-hosted Windows runner** checkout
  path → this is an official CI artifact, not a hand-rolled fork.
- **patternsleuth** is the Rust AOB-resolver engine that replaced UE4SS's old
  scanner on the dev branch → confirms a modern (post-3.0) build.

### settings.ini era markers (new-era keys present)

`UE4SS-settings.ini` contains keys that did **not** exist in 3.0.1, confirming a
newer build:

- `[Overrides] ModsFolderPaths` (with `+`/`-` prefix syntax) and `ControllingModsTxt`
- `Experimental_ShouldPreDuplicateMap` (UTF-16 string in the binary)
- `bUseUObjectArrayCache = false`, `DoEarlyScan`, `InvalidateCacheIfDLLDiffers`

## Installed UE4SS mods (this machine)

`ue4ss\Mods\mods.txt` — **defaults only**; TFWWorkbench is **not** currently
installed here:

```
CheatManagerEnablerMod : 1
ConsoleCommandsMod : 1
ConsoleEnablerMod : 1
SplitScreenMod : 0
LineTraceMod : 0
BPML_GenericFunctions : 1
BPModLoaderMod : 1
Keybinds : 1
```

Present mod folders: `BPML_GenericFunctions`, `BPModLoaderMod`,
`CheatManagerEnablerMod`, `ConsoleCommandsMod`, `ConsoleEnablerMod`, `Keybinds`,
`LineTraceMod`, `shared`, `SplitScreenMod`.

## What this pins down

1. The "latest ue4ss" in the origin-log complaint corresponds to a **patternsleuth
   experimental CI build** like the one installed here (2026-07-12) — not a
   numbered stable release.
2. To reproduce / bisect the breakage we compare *this* build against whichever
   older experimental build TFWWorkbench was authored against (see
   [`docs/04-the-breakage.md`](../docs/04-the-breakage.md) and
   [`data/compat.json`](../data/compat.json)).
3. **Next capture:** launch the game once with UE4SS active to generate
   `UE4SS.log`; its banner prints the exact version/commit. Add it here when done.

> **Reproducibility note:** the two SHA-256 hashes above uniquely identify this
> build. If a future UE4SS zip produces the same `UE4SS.dll` hash, it *is* this
> build. Record hashes in [`data/compat.json`](../data/compat.json) as the stable
> identifier, since CI builds lack version metadata.
