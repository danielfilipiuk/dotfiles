-- Ten analog-needle VU meters, one per cliamp spectrum band. Needles
-- are drawn at sub-pixel resolution using Unicode braille
-- (U+2800..U+28FF, 2x4 dots per cell) so diagonals stay smooth at
-- any angle. Sibling of led-burst and block-burst.

local p = plugin.register({
    name = "vu-meter",
    type = "visualizer",
})

local ESC = string.char(27)
local RESET = ESC .. "[0m"
-- Use ANSI 16-color SGR codes (30-37 / 90-97) so the terminal theme
-- (Omarchy, etc.) drives the actual RGB values. 256-color slots would
-- be hardcoded and ignore the theme.
local function sgr(n) return ESC .. "[" .. n .. "m" end

local TICK_C     = sgr(90)  -- bright black (grey)
local TICK_HOT   = sgr(91)  -- bright red
local ZERO_C     = sgr(93)  -- bright yellow
local LABEL_C    = sgr(90)  -- bright black (grey)
local NEEDLE_C   = sgr(97)  -- bright white
local NEEDLE_HOT = sgr(91)  -- bright red

local nMeters       = 10
local NEEDLE_CELL_H = 3                   -- braille rows in the needle area
local TOTAL_ROWS    = 2 + NEEDLE_CELL_H   -- scale + needle area + label
local SWING_DEG     = 60                  -- max swing each side of vertical
-- Candidate meter widths (cells). The layout picker tries them from
-- widest to narrowest so wide panels get fat meters and lots of swing.
local METER_WIDTHS  = { 13, 11, 9, 7, 5 }
local MIN_GAP       = 2                   -- still keeps + / − apart, but
                                          -- lets the picker grab wider meters
local MAX_GAP       = 8                   -- cap so meters don't spread too thin
local FALLBACK_GAP  = 1                   -- if nothing fits at MIN_GAP

local floor = math.floor
local abs   = math.abs
local sin   = math.sin
local cos   = math.cos
local rad   = math.rad
local schar = string.char

-- ============================================================ braille
-- Bit value at sub-cell position (col 0..1, row 0..3) inside a braille
-- cell. The wonky order matches the Unicode braille spec (rows 0..2 use
-- bits 0/1/2 + 3/4/5, row 3 uses bits 6 + 7).
local BR_BIT = {
    [0] = { [0] = 1, [1] = 2, [2] = 4, [3] = 64 },
    [1] = { [0] = 8, [1] = 16, [2] = 32, [3] = 128 },
}

local function brailleChar(bits)
    return schar(0xE2, 0xA0 + floor(bits / 64), 0x80 + (bits % 64))
end

-- ============================================================ scale row
local function buildScale(meterW)
    local cells = {}
    for c = 1, meterW do cells[c] = " " end
    local pivotCol  = floor((meterW + 1) / 2)
    cells[1]        = TICK_C   .. "-" .. RESET
    cells[meterW]   = TICK_HOT .. "+" .. RESET
    cells[pivotCol] = ZERO_C   .. "0" .. RESET
    for c = 3, meterW - 2, 2 do
        if c ~= pivotCol then
            local color = (c < pivotCol) and TICK_C or TICK_HOT
            cells[c] = color .. "·" .. RESET
        end
    end
    return table.concat(cells)
end

-- ============================================================ needle render
-- Returns the NEEDLE_CELL_H rows of braille characters for one meter.
-- The needle has a CONSTANT length so it looks the same at every
-- angle. Length is fixed at ~full canvas height (gives a long visible
-- stick), and the swing angle is automatically reduced for narrow
-- meters so the tip just reaches the side wall instead of overshooting.
local function renderNeedleRows(level, meterW)
    local subW       = meterW * 2
    local subH       = NEEDLE_CELL_H * 4
    local pivotSubX  = floor(subW / 2)
    local pivotSubY  = subH - 1
    local halfSwingX = subW - 1 - pivotSubX

    local L         = pivotSubY * 0.92
    local widthCap  = math.asin(math.min(1, halfSwingX / L))
    local thetaMax  = math.min(rad(SWING_DEG), widthCap)
    local theta     = (level * 2 - 1) * thetaMax
    local tipSubX   = pivotSubX + floor(L * sin(theta) + 0.5)
    local tipSubY   = pivotSubY - floor(L * cos(theta) + 0.5)

    local dotsPerCell = {}
    local function setDot(sx, sy)
        if sx < 0 or sx >= subW or sy < 0 or sy >= subH then return end
        local cx = floor(sx / 2)
        local cy = floor(sy / 4)
        local sc = sx - cx * 2
        local sr = sy - cy * 4
        local bit = BR_BIT[sc][sr]
        local key = cy * meterW + cx
        local d = dotsPerCell[key]
        if not d then d = {}; dotsPerCell[key] = d end
        d[bit] = true
    end

    -- Bresenham from pivot to tip, single sub-pixel wide (thin line).
    do
        local x0, y0 = pivotSubX, pivotSubY
        local x1, y1 = tipSubX, tipSubY
        local dx = abs(x1 - x0)
        local dy = abs(y1 - y0)
        local sx = (x0 < x1) and 1 or -1
        local sy = (y0 < y1) and 1 or -1
        local err = dx - dy
        while true do
            setDot(x0, y0)
            if x0 == x1 and y0 == y1 then break end
            local e2 = 2 * err
            if e2 > -dy then err = err - dy; x0 = x0 + sx end
            if e2 <  dx then err = err + dx; y0 = y0 + sy end
        end
    end

    -- Pivot blob (three sub-pixels at the bottom row for visibility).
    setDot(pivotSubX - 1, pivotSubY)
    setDot(pivotSubX,     pivotSubY)
    setDot(pivotSubX + 1, pivotSubY)

    local color = (level > 0.92) and NEEDLE_HOT or NEEDLE_C
    local lines = {}
    for cy = 0, NEEDLE_CELL_H - 1 do
        local cells = {}
        for cx = 0, meterW - 1 do
            local d = dotsPerCell[cy * meterW + cx]
            local bits = 0
            if d then
                for b, _ in pairs(d) do bits = bits + b end
            end
            cells[#cells + 1] = brailleChar(bits)
        end
        lines[cy + 1] = color .. table.concat(cells) .. RESET
    end
    return lines
end

-- ============================================================ helpers
-- Pick the widest meter that fits, then the biggest gap that still
-- fits — so wide panels actually use their width instead of leaving
-- empty space on the sides.
local function pickLayout(cols)
    for _, w in ipairs(METER_WIDTHS) do
        for g = MAX_GAP, MIN_GAP, -1 do
            if w * nMeters + (nMeters - 1) * g <= cols then
                return w, g
            end
        end
    end
    -- Narrow-panel fallback: relax the min gap.
    for _, w in ipairs({ 7, 5 }) do
        for g = MIN_GAP - 1, FALLBACK_GAP, -1 do
            if w * nMeters + (nMeters - 1) * g <= cols then
                return w, g
            end
        end
    end
    return 0, 0
end

local function padCenter(s, w)
    local diff = w - #s
    if diff <= 0 then return s end
    local l = floor(diff / 2)
    return string.rep(" ", l) .. s .. string.rep(" ", diff - l)
end

-- ============================================================ state + render
local needlePos = {}

function p:init()
    needlePos = {}
end

function p:render(bands, frame, rows, cols)
    local meterW, meterGap = pickLayout(cols)
    if meterW == 0 or rows < TOTAL_ROWS then return "" end

    -- Direct tracking — needle follows the raw band level each frame.
    for i = 1, nMeters do
        needlePos[i] = bands[i] or 0
    end

    local metersW = nMeters * meterW + (nMeters - 1) * meterGap
    local padN    = floor((cols - metersW) / 2)
    if padN < 0 then padN = 0 end
    local pad     = string.rep(" ", padN)
    local gap     = string.rep(" ", meterGap)

    -- Pre-render each meter's needle block.
    local blocks = {}
    for i = 1, nMeters do
        blocks[i] = renderNeedleRows(needlePos[i] or 0, meterW)
    end

    local lines = {}

    -- Scale row.
    do
        local parts = {}
        for i = 1, nMeters do
            parts[#parts + 1] = buildScale(meterW)
            if i < nMeters then parts[#parts + 1] = gap end
        end
        lines[#lines + 1] = pad .. table.concat(parts)
    end

    -- Needle rows — stitched column-by-column so meters stay aligned.
    for br = 1, NEEDLE_CELL_H do
        local parts = {}
        for i = 1, nMeters do
            parts[#parts + 1] = blocks[i][br]
            if i < nMeters then parts[#parts + 1] = gap end
        end
        lines[#lines + 1] = pad .. table.concat(parts)
    end

    -- Label row (band numbers 1..10) — below the needles.
    do
        local parts = {}
        for i = 1, nMeters do
            parts[#parts + 1] = LABEL_C .. padCenter(tostring(i), meterW) .. RESET
            if i < nMeters then parts[#parts + 1] = gap end
        end
        lines[#lines + 1] = pad .. table.concat(parts)
    end

    return table.concat(lines, "\n")
end
