-- Stereo step meter built from the same LED dots as led-burst, but
-- arranged into nested rectangular tiers. Each side of the center
-- divider shows a pyramid: a small inner block, then progressively
-- larger ones outward (cyan -> green -> yellow -> orange -> red).
-- Each tier responds to a distinct frequency range, lit when its
-- range crosses a threshold AND all inner tiers are also lit, so the
-- pyramid keeps its nested shape. All tier heights scale with the
-- panel height so the pyramid fills the visualizer area.

local p = plugin.register({
    name = "block-burst",
    type = "visualizer",
})

local ESC = string.char(27)
local RESET = ESC .. "[0m"
-- Use ANSI 16-color SGR codes (30-37 / 90-97) so the terminal theme
-- (Omarchy, etc.) drives the actual RGB values. 256-color slots would
-- be hardcoded and ignore the theme.
local function sgr(n) return ESC .. "[" .. n .. "m" end

local LED_ON  = "■"
local LED_OFF = "·"
local GAP     = " "
local DIM     = sgr(90)  -- bright black: grey in most themes

-- Tier table, ordered inner -> outer. Each tier:
--   ledsW     : width in LEDs (chars per row = 2*ledsW - 1)
--   bandLo/Hi : inclusive band index range (1..10) the tier listens to
--   threshold : that band-range level (0..1) at which the tier lights
--   color     : ANSI escape for lit LEDs (bright variant)
--   dimColor  : ANSI escape for the unlit outline (normal variant of
--               the same hue, so the gradient survives in dim form)
-- Heights are derived from the panel rows (see tierHeight), so every
-- tier — including the innermost — grows in fullscreen mode.
-- Orange has no ANSI-16 slot — we substitute magenta so the hi-mid tier
-- still has its own theme color.
local TIERS = {
    { ledsW = 2, bandLo = 1, bandHi = 2,  threshold = 0.15, color = sgr(96), dimColor = sgr(36) }, -- subbass: cyan
    { ledsW = 3, bandLo = 3, bandHi = 4,  threshold = 0.18, color = sgr(92), dimColor = sgr(32) }, -- low-mid: green
    { ledsW = 3, bandLo = 5, bandHi = 6,  threshold = 0.18, color = sgr(93), dimColor = sgr(33) }, -- mid:     yellow
    { ledsW = 3, bandLo = 7, bandHi = 8,  threshold = 0.15, color = sgr(95), dimColor = sgr(35) }, -- hi-mid:  magenta (orange substitute)
    { ledsW = 4, bandLo = 9, bandHi = 10, threshold = 0.12, color = sgr(91), dimColor = sgr(31) }, -- treble:  red
}

-- Show a dim outline of unlit tiers in the background so the pyramid
-- shape is always visible. Set to false for a cleaner look that only
-- shows currently lit tiers.
local SHOW_OUTLINE = true

local DIVIDER = sgr(91) .. "│" .. RESET

-- Per-tier smoothed level state (held across frames).
local tierEnergy = {}

function p:init()
    tierEnergy = {}
end

local function tierCharWidth(t)
    return 2 * t.ledsW - 1
end

-- Tier i (1..nTiers) gets a height proportional to its index, so the
-- outermost fills the full panel and the innermost stays small but
-- still scales: at rows=5 -> {1, 2, 3, 4, 5}, at rows=30 -> {6, 12, 18, 24, 30}.
local function tierHeight(idx, nTiers, maxRows)
    if maxRows <= 0 then return 0 end
    local h = math.floor(idx * maxRows / nTiers + 0.5)
    if h < 1 then h = 1 end
    if h > maxRows then h = maxRows end
    return h
end

-- Top and bottom row (0-indexed, inclusive) for a centered span of height h.
local function tierTopBottom(h, rows)
    local mid = (rows - 1) / 2
    local top = math.floor(mid - (h - 1) / 2 + 0.5)
    if top < 0 then top = 0 end
    local bottom = top + h - 1
    if bottom > rows - 1 then
        bottom = rows - 1
        top = bottom - h + 1
    end
    return top, bottom
end

-- Mean level across a band range (inclusive 1..10).
local function rangeLevel(bands, lo, hi)
    local sum, n = 0, 0
    for i = lo, hi do
        sum = sum + (bands[i] or 0)
        n = n + 1
    end
    if n == 0 then return 0 end
    return sum / n
end

function p:render(bands, frame, rows, cols)
    -- Per-half width: tier rows + 1-char spacer between adjacent tiers.
    local halfW = 0
    for i, t in ipairs(TIERS) do
        halfW = halfW + tierCharWidth(t)
        if i < #TIERS then halfW = halfW + 1 end
    end
    if cols < 2 * halfW + 3 or rows < 1 then return "" end

    local nTiers = #TIERS

    -- Cap the rendered height like led-burst does. Without this, the
    -- meter fills the whole vis area in fullscreen mode, making the
    -- overall cliamp UI tall enough that centerFrame's vertical padding
    -- shrinks and the pyramid drifts off-center in the terminal.
    local maxRows = 21
    local nRows = math.min(rows, maxRows)

    -- Update per-tier smoothed energy: snap up instantly, decay slowly.
    for i, t in ipairs(TIERS) do
        local raw = rangeLevel(bands, t.bandLo, t.bandHi)
        local prev = tierEnergy[i] or 0
        if raw > prev then
            tierEnergy[i] = raw                         -- snap up
        else
            tierEnergy[i] = math.max(raw, prev - 0.08)  -- decay
        end
    end

    -- Vertical layout: each tier has a fixed outline (target shape) AND
    -- a dynamic lit portion that scales with the tier's energy. The
    -- outline keeps the pyramid silhouette visible; the lit portion
    -- pumps with the audio in that frequency range.
    local tierState = {}
    for i, t in ipairs(TIERS) do
        local targetH = tierHeight(i, nTiers, nRows)
        local targetTop, targetBottom = tierTopBottom(targetH, nRows)

        -- Map energy 0..1 onto height 0..targetH. Subtract the tier's
        -- threshold as a noise floor so quiet bands don't pin a row lit.
        local effective = math.max(0, tierEnergy[i] - t.threshold) / math.max(0.01, 1 - t.threshold)
        local litH = math.floor(targetH * effective + 0.5)
        if litH > targetH then litH = targetH end

        local litTop, litBottom = -1, -2
        if litH > 0 then
            litTop, litBottom = tierTopBottom(litH, nRows)
        end

        tierState[i] = {
            targetTop = targetTop, targetBottom = targetBottom,
            litTop = litTop, litBottom = litBottom,
        }
    end

    local function ledRow(t, isLit)
        local color = isLit and t.color or t.dimColor
        local char  = isLit and LED_ON or LED_OFF
        local parts = {}
        for j = 1, t.ledsW do
            parts[#parts+1] = color .. char
            if j < t.ledsW then parts[#parts+1] = RESET .. GAP end
        end
        return table.concat(parts)
    end

    local function halfLine(row, direction)
        -- direction: -1 = outer->inner (left half), 1 = inner->outer (right).
        local startI = (direction == -1) and nTiers or 1
        local endI   = (direction == -1) and 1 or nTiers
        local parts = {}
        for i = startI, endI, direction do
            local t = TIERS[i]
            local s = tierState[i]
            local inTarget = row >= s.targetTop and row <= s.targetBottom
            local inLit = row >= s.litTop and row <= s.litBottom
            if inTarget and inLit then
                parts[#parts+1] = ledRow(t, true)
            elseif inTarget and SHOW_OUTLINE then
                parts[#parts+1] = ledRow(t, false)
            else
                parts[#parts+1] = string.rep(" ", tierCharWidth(t))
            end
            local nextIdx = i + direction
            if nextIdx >= 1 and nextIdx <= nTiers then
                parts[#parts+1] = " "
            end
        end
        return table.concat(parts) .. RESET
    end

    -- Pad each line with left/right spaces so the fixed-width meter
    -- sits horizontally centered inside the wider visualizer panel.
    local lineWidth = 2 * halfW + 3
    local padLeftN = math.floor((cols - lineWidth) / 2)
    local padRightN = cols - lineWidth - padLeftN
    if padLeftN < 0 then padLeftN = 0 end
    if padRightN < 0 then padRightN = 0 end
    local padLeft = string.rep(" ", padLeftN)
    local padRight = string.rep(" ", padRightN)

    local lines = {}
    for row = 0, nRows - 1 do
        lines[#lines+1] = padLeft
            .. halfLine(row, -1)
            .. " " .. DIVIDER .. " "
            .. halfLine(row, 1)
            .. padRight
    end

    return table.concat(lines, "\n")
end
