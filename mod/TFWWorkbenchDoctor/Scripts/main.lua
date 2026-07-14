--[[
  TFWWorkbenchDoctor  -  a UE4SS diagnostic mod (Lua)
  ------------------------------------------------------------------
  Purpose: help a user figure out WHY TFWWorkbench isn't working, by
  fingerprinting the UE4SS build and checking whether TFWWorkbench's
  C++ side actually loaded.

  Why this is a DIAGNOSTIC, not a fix:
  TFWWorkbench breaks because its precompiled C++ main.dll is ABI-locked
  to an older UE4SS (see docs/04-the-breakage.md). That DLL fails to LOAD
  before any Lua runs, so a Lua mod CANNOT patch around it. The real fix
  is to recompile main.dll (see ../rebuild-recipe.md) or pin UE4SS
  (see docs/05-known-good-and-workarounds.md). What Lua CAN do is tell you
  which situation you're in.

  Everything here is wrapped in pcall so it can never crash the game on any
  UE4SS build. Output goes to UE4SS.log / the UE4SS console.
--]]

local MOD_NAME = "TFWWorkbenchDoctor"

local function log(msg)
    print(string.format("[%s] %s\n", MOD_NAME, msg))
end

log("loaded")

-- 1) Fingerprint the UE4SS build (git-describe version if the API exposes it).
local function report_ue4ss()
    local ok, info = pcall(function()
        local parts = {}
        if UE4SS and UE4SS.GetVersion then
            local maj, min, patch = UE4SS.GetVersion()
            parts[#parts + 1] = string.format("UE4SS %s.%s.%s", tostring(maj), tostring(min), tostring(patch))
        end
        if UnrealVersion and UnrealVersion.GetMajor then
            parts[#parts + 1] = string.format("UE %s.%s", tostring(UnrealVersion.GetMajor()), tostring(UnrealVersion.GetMinor()))
        end
        return table.concat(parts, "  |  ")
    end)
    log("ue4ss env: " .. ((ok and info and #info > 0) and info or "(version API unavailable on this build)"))
    log("note: the authoritative version is the git-describe banner at the TOP of UE4SS.log (e.g. v3.0.1-1011-gb50986bd).")
end

-- 2) Check whether TFWWorkbench's C++ side registered its Lua functions.
--    If main.dll failed to load (the 0x7F ABI break), these globals are absent.
local function check_workbench()
    local expected = { "AddDataTableRow", "ConfigureDataTables" }
    local missing = {}
    for _, name in ipairs(expected) do
        if type(_G[name]) ~= "function" then
            missing[#missing + 1] = name
        end
    end
    if #missing == 0 then
        log("TFWWorkbench C++ side looks LOADED (registered: " .. table.concat(expected, ", ") .. ").")
    else
        log("TFWWorkbench C++ functions MISSING: " .. table.concat(missing, ", "))
        log("=> main.dll almost certainly failed to load. Look in UE4SS.log for:")
        log("   'Failed to load dll ...main.dll... error: [0x7f] The specified procedure could not be found'")
        log("   If present -> C++ ABI mismatch. Fix: recompile main.dll (../rebuild-recipe.md) or")
        log("   pin UE4SS to ~v3.0.1-848/-849 (docs/05-known-good-and-workarounds.md).")
        log("   If ABSENT and the mod folder isn't under ue4ss/Mods/TFWWorkbench -> install error (issue #1).")
    end
end

pcall(report_ue4ss)
pcall(check_workbench)
log("done. This mod only reports; it does not modify anything.")
