# Draft report for TFWWorkbench issue #2 (for review before posting)

> This is a **draft** for <https://github.com/smotti/TFWWorkbench/issues/2>. Review /
> edit it, then post it yourself if you're happy with it. Nothing has been posted.
> Adjust the tone/attribution as you like.

---

**Root cause of the `[0x7f] The specified procedure could not be found` on v0.2.1**

The precompiled `dlls/main.dll` fails to load on current RE-UE4SS builds because of a
single re-signatured export. `main.dll` imports 81 UE4SS symbols; on a current
experimental build (`~v3.0.1-1011`, UE 5.4.2) **80 resolve and exactly one does not**:

```
?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ     // UStruct::GetMinAlignment() -> int&
```

UE4SS narrowed `UStruct::GetMinAlignment()`'s return type from `int32&` to `int16&`
(and moved the old `int&` accessor to a private `GetMinAlignmentBase`). Current
UE4SS therefore exports `…QEAAAEAFXZ` (`short&`) instead of `…QEAAAEAHXZ` (`int&`),
so the loader can't bind the import and aborts the whole DLL with
`0x7F ERROR_PROC_NOT_FOUND`.

**It should be a clean recompile — no source change.** The only affected call is
`dllmain.cpp` (`FMemory::Malloc(structSize, rowStruct->GetMinAlignment())`): the
value is just read and passed as an alignment, so `short&` → `int` converts
implicitly. Rebuilding `main.dll` against a current UE4SS SDK and shipping the new
DLL should fix it for everyone. (The other `GetMinAlignment` calls in the file are
`FProperty::GetMinAlignment`, which is unchanged.)

**Reproduction** (no game launch needed): diff the mod's imports against your
installed `UE4SS.dll` exports —
```
81 imports, 80 resolved, 1 missing: ?GetMinAlignment@UStruct@Unreal@RC@@QEAAAEAHXZ
```

**Stopgap for affected users:** the two decorated names differ by a single byte
(`H`→`F`), so repointing that one import in `main.dll` makes all 81 imports resolve
and the DLL load again. It appears to work because the field is small/little-endian,
but it's unverified at runtime and not a substitute for a recompile.

Happy to help test a rebuilt DLL.

---

*(Background: this diagnosis and the tooling to reproduce it live in
<https://github.com/dataterminals/tfworkbench-compat-research>.)*
