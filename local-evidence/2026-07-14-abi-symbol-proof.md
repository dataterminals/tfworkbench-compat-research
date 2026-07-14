# ABI symbol proof — 2026-07-14

The C++ ABI hypothesis (H1 in [`docs/04-the-breakage.md`](../docs/04-the-breakage.md))
is no longer inferred. A static PE import/export diff **names the exact missing
symbol**, and the result is fully reproducible from two files:

- **TFWWorkbench v0.2.1** `dlls/main.dll` — SHA-256
  `24b05dc267dc6e9faa6cbcb4e85a8491733e0a86b86fbac92f5aa1a0950aa6ca` (219,136 B),
  from the official release <https://github.com/smotti/TFWWorkbench/releases/tag/0.2.1>.
- **Local UE4SS.dll** (the broken build) — SHA-256
  `a79b894d4a499c066985b47354d2a3a1fc9069cebefe585ba458bb8f572930b5`, experimental
  `~v3.0.1-1011` (see [`2026-07-13-local-install.md`](2026-07-13-local-install.md)).

Reproduce: `python tools/abi-diff.py <main.dll> <UE4SS.dll>` (needs `pip install pefile`).

## Result

```
main.dll imports from UE4SS.dll : 81
current UE4SS.dll total exports  : 4106
  -> RESOLVED (present)          : 80
  -> MISSING (cause of 0x7F)     : 1
```

**The one missing symbol:**

```
?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ
```

A single unresolved import is enough: the Windows loader cannot bind it, so it
fails the whole `main.dll` load with `0x7F ERROR_PROC_NOT_FOUND`. This is a
deterministic loader outcome, not a probabilistic one — which is why H1 can be
called **proven** at the ABI level (the in-game log line is still worth capturing as
a courtesy confirmation, but the load *cannot* succeed with this mismatch).

## What actually changed (return type narrowed int32 → int16)

The MSVC mangling encodes the return type, so the diff shows precisely what UE4SS
changed to `RC::Unreal::UStruct::GetMinAlignment()`:

| Where | Mangled symbol | Demangled | Return |
| --- | --- | --- | --- |
| **main.dll needs** | `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEA**H**XZ` | `public: … UStruct::GetMinAlignment(void)` | **`int&`** (`H`=int32) |
| current UE4SS has | `?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEA**F**XZ` | `public: … UStruct::GetMinAlignment(void)` | **`short&`** (`F`=int16) |
| current UE4SS has (const) | `?GetMinAlignment@UStruct@Unreal@RC@@QEBAAEBFXZ` | `public: … UStruct::GetMinAlignment(void) const` | `short const&` |
| current UE4SS added | `?GetMinAlignment**Base**@UStruct@Unreal@RC@@AEAAAEA**H**XZ` | `private: … UStruct::GetMinAlignmentBase(void)` | `int&` |

So UE4SS **narrowed `UStruct::MinAlignment` from `int32` to `int16`** and moved the
old `int&` accessor to a private `GetMinAlignmentBase`. `main.dll` was compiled
against the `int&` (`H`) version and imports `…AEAHXZ`, which no longer exists.

> MSVC type codes used above: `F` = `short`/int16, `H` = `int`/int32; `AEA_` = lvalue
> reference (`&`), `AEB_` = const reference; `QEAA` = public member, `QEBA` = public
> const member, `AEAA` = private member.

The `GetMinAlignment506` variants and the `MemberVariableLayout` hits in the UE4SS
source indicate `MinAlignment` is a **config-driven member-variable accessor** (its
width comes from UE4SS's member-layout system), which is consistent with a
deliberate int32→int16 correction.

> **Open (minor):** the exact upstream commit/date that narrowed it lives in UE4SS's
> **Unreal SDK submodule** (the `RC::Unreal` layer), not the main repo tree, so it
> wasn't pinned here. It doesn't affect the proof — the ABI break is demonstrated
> directly from the two binaries.

## Why this is great news for the fix

The method still **exists** — it was re-signatured, not removed. So recompiling
`main.dll` against the current UE4SS SDK makes it import the `short&` (`F`) version,
and the consuming C++ (which just reads the alignment as an `int`) compiles
unchanged because `short&` → `int` converts implicitly. **A clean recompile with
zero source changes should fix it** — see [`mod/rebuild-recipe.md`](../mod/rebuild-recipe.md).

> ⚠️ Do NOT try to "fix" this by binary-patching `main.dll`'s import to point at the
> `short&` export: the old code dereferences the reference as a 4-byte `int`, but the
> field is now 2 bytes, so it would read 2 bytes of `MinAlignment` + 2 adjacent
> bytes → a corrupted alignment value. Recompilation is the correct fix.
