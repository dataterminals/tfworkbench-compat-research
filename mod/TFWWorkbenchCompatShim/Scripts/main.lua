--[[
  TFWWorkbenchCompatShim  -  UE4SS mod skeleton
  ------------------------------------------------------------------
  Purpose: host a fix that restores the UE4SS behavior TFWWorkbench
  assumes, so TFWWorkbench works on newer (experimental) UE4SS builds.

  STATUS: INERT SKELETON. This file intentionally applies NO patch yet.
  The root cause is still under investigation (see docs/04-the-breakage.md).
  Shipping a shim against the wrong cause is worse than shipping none, so
  the compensation code stays behind ENABLE_FIX = false until a hypothesis
  in docs/04-the-breakage.md is CONFIRMED.

  Load order: this mod must initialize BEFORE TFWWorkbench. UE4SS loads mods
  in mods.txt order (top = first). Place "TFWWorkbenchCompatShim : 1" ABOVE
  "TFWWorkbench : 1" in Mods/mods.txt.
--]]

local MOD_NAME = "TFWWorkbenchCompatShim"
local ENABLE_FIX = false   -- flip to true ONLY when a confirmed fix is implemented below

local function log(msg)
    -- UE4SS exposes print(); output lands in UE4SS.log / the UE4SS console.
    print(string.format("[%s] %s\n", MOD_NAME, msg))
end

log("loaded (skeleton, ENABLE_FIX=" .. tostring(ENABLE_FIX) .. ")")

-- Best-effort environment fingerprint to help diagnose which build we're on.
-- Wrapped in pcall so a missing/renamed API on some build can never crash the game.
local function fingerprint()
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
    if ok and info and #info > 0 then
        log("env: " .. info)
    else
        log("env: (version API unavailable on this build)")
    end
end
fingerprint()

-- ---------------------------------------------------------------------------
-- THE FIX GOES HERE once docs/04-the-breakage.md confirms a root cause.
--
-- Example scaffolding for the leading hypothesis (H1: FName default flip).
-- If confirmed that TFWWorkbench needs FName lookups to use FNAME_Find, the
-- shim would, before TFWWorkbench runs, ensure name resolution behaves as the
-- authored build did (exact mechanism depends on the confirmed cause).
--
-- if ENABLE_FIX then
--     -- e.g. RegisterHook / ExecuteInGameThread to install compensation
--     -- BEFORE the DataTables are read by TFWWorkbench.
-- end
-- ---------------------------------------------------------------------------

if ENABLE_FIX then
    log("ENABLE_FIX is true but no fix is implemented - refusing to pretend. See docs/04-the-breakage.md.")
else
    log("no-op: awaiting confirmed root cause. See docs/04-the-breakage.md.")
end
