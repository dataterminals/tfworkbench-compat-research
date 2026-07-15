#!/usr/bin/env python3
"""Bisect the RE-UE4SS build where UStruct::GetMinAlignment narrowed int32& -> int16&.

Good  = exports ?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ  (int32&, what TFWWorkbench imports)
Broken= that symbol is gone (only ...AEAFXZ / int16& remains)
"""
import io, json, re, sys, urllib.request, zipfile
import pefile

API = "https://api.github.com"
REPO = "UE4SS-RE/RE-UE4SS"
GOOD_SYM = "?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ"
CACHE = {}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bisect", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def list_assets():
    rel = get(f"{API}/repos/{REPO}/releases/tags/experimental")
    rid, out, page = rel["id"], [], 1
    while True:
        batch = get(f"{API}/repos/{REPO}/releases/{rid}/assets?per_page=100&page={page}")
        if not batch:
            break
        out += batch
        page += 1
    return out


def submodule_at(sha):
    if sha in CACHE:
        return CACHE[sha]
    try:
        r = get(f"{API}/repos/{REPO}/contents/deps/first/Unreal?ref={sha}")
        CACHE[sha] = r.get("sha", "?")
    except Exception as e:
        CACHE[sha] = f"err({e})"
    return CACHE[sha]


def exports_of_zip(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bisect"})
    with urllib.request.urlopen(req, timeout=300) as r:
        blob = r.read()
    z = zipfile.ZipFile(io.BytesIO(blob))
    name = next((n for n in z.namelist() if n.lower().endswith("ue4ss.dll")), None)
    if not name:
        raise RuntimeError("no UE4SS.dll in zip")
    dll = z.read(name)
    pe = pefile.PE(data=dll, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    syms = {s.name.decode(errors="replace") for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    return syms, len(blob)


def main():
    assets = list_assets()
    pat = re.compile(r"^UE4SS_v3\.0\.1-(\d+)-g([0-9a-f]+)\.zip$")
    builds = []
    for a in assets:
        m = pat.match(a["name"])
        if m:
            builds.append({"n": int(m.group(1)), "sha": m.group(2), "url": a["browser_download_url"], "name": a["name"]})
    builds.sort(key=lambda b: b["n"])
    lo_n, hi_n = 894, 1011
    window = [b for b in builds if lo_n <= b["n"] <= hi_n]
    print(f"archive assets parsed: {len(builds)}   candidates in [{lo_n}..{hi_n}]: {len(window)}")
    print("  " + ", ".join(f"-{b['n']}" for b in window))
    print()

    # Known endpoints (already verified this session) — don't re-download them.
    known = {894: True, 1011: False}
    lo, hi = 0, len(window) - 1
    tested = {}

    def is_good(idx):
        b = window[idx]
        if b["n"] in known:
            tested[b["n"]] = known[b["n"]]
            print(f"  -{b['n']:<5} (known)      -> {'GOOD' if known[b['n']] else 'BROKEN'}")
            return known[b["n"]]
        if b["n"] in tested:
            return tested[b["n"]]
        syms, size = exports_of_zip(b["url"])
        good = GOOD_SYM in syms
        sub = submodule_at(b["sha"])
        tested[b["n"]] = good
        print(f"  -{b['n']:<5} g{b['sha']:<9} {size/1e6:5.2f}MB  exports={len(syms):<5} "
              f"UEPseudo={sub[:8]}  -> {'GOOD (int32&)' if good else 'BROKEN (int16&)'}")
        return good

    print("binary search:")
    assert is_good(lo), "lower bound must be GOOD"
    assert not is_good(hi), "upper bound must be BROKEN"
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if is_good(mid):
            lo = mid
        else:
            hi = mid
    last_good, first_bad = window[lo], window[hi]
    print()
    print("=" * 74)
    print(f"LAST GOOD : -{last_good['n']}-g{last_good['sha']}   UEPseudo {submodule_at(last_good['sha'])}")
    print(f"FIRST BAD : -{first_bad['n']}-g{first_bad['sha']}   UEPseudo {submodule_at(first_bad['sha'])}")
    print("=" * 74)
    print(f"downloads used: {len([k for k in tested if k not in known])}")
    return last_good, first_bad


if __name__ == "__main__":
    main()
