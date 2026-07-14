# Sources

Primary sources for this investigation. Prefer these over memory; cite them in docs.

## UE4SS (RE-UE4SS)
- Releases (source of record): <https://github.com/UE4SS-RE/RE-UE4SS/releases>
- `experimental-latest` tag: <https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/experimental-latest>
- Repo: <https://github.com/UE4SS-RE/RE-UE4SS>
- Docs: <https://docs.ue4ss.com/> · Upgrade/migration guide: <https://docs.ue4ss.com/dev/upgrade-guide.html>
- C++ mod ABI is pinned per build: <https://docs.ue4ss.com/dev/guides/installing-a-c++-mod.html>
- Changelog (v4.0.0-rc1 unreleased; xmake→CMake "cannot guarantee ABI compatability"):
  <https://raw.githubusercontent.com/UE4SS-RE/RE-UE4SS/main/assets/Changelog.md>
- `v3.0.1...main` compare (ahead_by 1011 on 2026-07-13): <https://api.github.com/repos/UE4SS-RE/RE-UE4SS/compare/v3.0.1...main>
- Release-cycle discussion: <https://github.com/UE4SS-RE/RE-UE4SS/discussions/498>
- Key PRs: UE5.4 support #503 · dir restructure #506 · FName flip (red herring) #994 ·
  xmake→CMake #1067 · TObjectPtr rework #850 · UE5.6 #977
- Upstream #696 (maintainer: 0x7F == C++ mod ABI incompatibility): <https://github.com/UE4SS-RE/RE-UE4SS/issues/696>

## TFWWorkbench
- **Author/maintainer: smotti** (GitHub repo owner).
- Release container repo: <https://github.com/smotti/TFWWorkbench>
- C++ source (submodule): <https://github.com/smotti/TFWWorkbench-Cpp>
  - `CMakeLists.txt` (`target_link_libraries(TFWWorkbench PUBLIC UE4SS)`) and
    `dllmain.cpp` (`RC::CppUserModBase`, registers `AddDataTableRow`/`ConfigureDataTables`).
- Releases (v0.1.0 2026-01-14, v0.2.1 2026-01-20; ships `dlls/main.dll` 219,136 B):
  <https://github.com/smotti/TFWWorkbench/releases>
- Issue #2 (OPEN, 2026-07-14, 0x7F main.dll load fail): <https://github.com/smotti/TFWWorkbench/issues/2>
- Issue #1 (2026-03-15, identical 0x7F, closed as user install error): <https://github.com/smotti/TFWWorkbench/issues/1>
- Nexus mod 77 = **"Construction Vendor"** (a mod that *depends on* TFWWorkbench),
  which carries the community floor note "UE4SS MUST BE VERSION v3.0.1-848 OR HIGHER":
  <https://www.nexusmods.com/theforeverwinter/mods/77>
  - Note: a sibling repo's older research labeled mod 77 as TFWWorkbench itself; that
    mapping is contested — treat the TFWWorkbench↔Nexus-mod-number link as unverified.

## The Forever Winter modding
- Steam page (AppID 2828860): <https://store.steampowered.com/app/2828860/>
- Nexus hub: <https://www.nexusmods.com/games/theforeverwinter>
- RE-UE4SS for TFW (Nexus mod 61): <https://www.nexusmods.com/theforeverwinter/mods/61>
- Signature Bypass (Nexus mod 57): <https://www.nexusmods.com/theforeverwinter/mods/57>
- Content-pak install path (Nexus mod 56): <https://www.nexusmods.com/theforeverwinter/mods/56>
- Vortex auto-installer (Nexus mod 121): <https://www.nexusmods.com/theforeverwinter/mods/121>

## UE modding background
- Palworld modding wiki (UE4SS logic mods): <https://pwmodding.wiki/docs/developers/ue4ss-modding/logic-mods/introduction>
- Stalker 2 / general UE4SS usage: <https://modding.wiki/en/stalker2heartofchornobyl/developers/UE4SS>

## Local / sibling-repo corroboration
- `local-evidence/2026-07-13-local-install.md` (this repo)
- `../ForeverWinterMO2Support/docs/RESEARCH.md` (TFW stack, verified local facts)

> Note: Nexus mod pages sometimes return HTTP 403 to direct fetch; corroborate via
> search snippets, the Nexus API, or community mirrors, and mark such facts
> "reported" rather than "verified" until confirmed.
