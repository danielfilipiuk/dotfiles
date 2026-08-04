
------------------------------- ZOOM  -------------------------------
---------------------------------------------------------------
-- GLASS MAGNIFIER ZOOM
local MAX_ZOOM = 6
local MIN_ZOOM = 1
local ZOOM_TOGGLE_FACTOR = 2

---@param offset number
---@return nil
local function zoom(offset)
    local current = hl.get_config("cursor.zoom_factor")
    if offset ~= nil then
        current = current + offset
    elseif current ~= MIN_ZOOM then
        current = MIN_ZOOM
    else
        current = ZOOM_TOGGLE_FACTOR
    end
    current = math.max(MIN_ZOOM, math.min(MAX_ZOOM, current))
    hl.config({ cursor = { zoom_factor = current } })
end

hl.bind("SUPER + Z", zoom , {description = "activate zoom"}) 
hl.bind("SUPER + KP_ADD", function()
    zoom(1)
end)
hl.bind("SUPER + KP_Subtract", function()
    zoom(-1)
end)---
--------------------------------------------------------------

