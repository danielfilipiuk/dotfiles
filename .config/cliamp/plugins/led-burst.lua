-- Stereo LED matrix that bursts outward from a center divider.
-- Color goes green (inner) -> yellow -> red (outer), with peak hold.

local p = plugin.register({
    name = "led-burst",
    type = "visualizer",
})

local ESC = string.char(27)
local RESET = ESC .. "[0m"
-- Use ANSI 16-color SGR codes (30-37 / 90-97) so the terminal theme
-- (Omarchy, etc.) drives the actual RGB values. 256-color slots would
-- be hardcoded and ignore the theme.
local function sgr(n) return ESC .. "[" .. n .. "m" end

local DIM     = sgr(90)  -- bright black: grey in most themes
local DIVIDER = sgr(91) .. "│" .. RESET

-- Distance to center, normalized 0..1 -> LED tier.
-- Orange has no ANSI-16 slot; the gradient drops it and rebalances the
-- thresholds across green (bright + normal), yellow, red.
local function tierColor(d)
    if d < 0.30 then return sgr(92)  -- bright green
    elseif d < 0.60 then return sgr(32)  -- green
    elseif d < 0.85 then return sgr(93)  -- bright yellow (warmest before red)
    else                  return sgr(91)  -- bright red
    end
end

local LED_ON  = "■"
local LED_OFF = "·"
local PEAK    = "■"
local GAP     = " "    -- spacer between LEDs for matrix dot look

local peaks = {}        -- per-row peak level (0..1)
local peakFrame = {}    -- frame the peak was last refreshed

function p:init()
    peaks = {}
    peakFrame = {}
end

-- Map a row (1..nRows) to a band index (1..10) so all 10 bands are
-- represented even if the panel is short.
local function bandForRow(bands, row, nRows)
    local idx = math.floor((row - 1) * 10 / nRows) + 1
    if idx < 1 then idx = 1 end
    if idx > 10 then idx = 10 end
    return bands[idx] or 0
end

-- Render one LED slot: tier-colored ON, PEAK marker, or dim OFF dot.
local function cell(i, lit, peakCell, d)
    if i <= lit then
        return tierColor(d) .. LED_ON
    elseif i == peakCell and peakCell > 0 then
        return tierColor(d) .. PEAK
    end
    return DIM .. LED_OFF
end

function p:render(bands, frame, rows, cols)
    if cols < 9 or rows < 1 then return "" end

    local nRows = math.min(rows, 10)
    -- Layout: nLeds * 2 - 1 chars per half (LED + GAP, no trailing gap),
    -- plus " | " around the divider. So 2 * (2*nLeds - 1) + 3 <= cols.
    local nLeds = math.floor((cols - 3) / 4)
    if nLeds < 2 then nLeds = 2 end

    local lines = {}
    for row = 1, nRows do
        local level = bandForRow(bands, row, nRows)

        -- Peak hold: snap up, slow decay after a short hold.
        local pk = peaks[row] or 0
        if level >= pk then
            pk = level
            peakFrame[row] = frame
        elseif (frame - (peakFrame[row] or 0)) > 6 then
            pk = math.max(level, pk - 0.035)
        end
        peaks[row] = pk

        local lit = math.floor(level * nLeds + 0.5)
        local peakCell = math.floor(pk * nLeds + 0.5)

        -- Left half: outer -> inner so the bar grows from center outward.
        local leftCells = {}
        for i = nLeds, 1, -1 do
            local d = (i - 1) / math.max(1, nLeds - 1)
            leftCells[#leftCells+1] = cell(i, lit, peakCell, d)
        end
        -- Right half: inner -> outer.
        local rightCells = {}
        for i = 1, nLeds do
            local d = (i - 1) / math.max(1, nLeds - 1)
            rightCells[#rightCells+1] = cell(i, lit, peakCell, d)
        end

        lines[row] = table.concat(leftCells, GAP) .. RESET
            .. GAP .. DIVIDER .. GAP
            .. table.concat(rightCells, GAP) .. RESET
    end

    return table.concat(lines, "\n")
end
