//@version=6  
// \=============================================================================  
// 3SL Liquidity Windows — v20  
//   \- Session boxes and headings now anchor to the real session open via  
//     f\_curOpen() instead of assuming the first in-window bar starts exactly  
//     windowMins before the open. Fixes boxes/labels drifting late on higher  
//     timeframes (1h, 4h) or when the first bar after a gap lands mid-window.  
//   \- DST handling unchanged: each session stays anchored to its own market  
//     timezone, labels convert to the display timezone.  
//   \- Everything else unchanged from v19.  
// \=============================================================================

indicator("3SL Liquidity Windows", overlay \= true, max\_labels\_count \= 500, max\_boxes\_count \= 60\)

// \--- Focus mode \--------------------------------------------------------------  
focusMode \= input.bool(false, "Focus mode — show only the current or next window",  
     group \= "Focus mode",  
     tooltip \= "When ON: hides every session except the one live right now (or the next upcoming one if none is live). Overrides shading, headings and the forecast toggle.")  
showFocusBorder  \= input.bool(false, "Show live window border", group \= "Focus mode",  
     tooltip \= "Off by default to match the borderless session bands.")  
focusBorderStyle \= input.string("Solid", "Live window border style", options \= \["Solid", "Dashed", "Dotted"\],  
     group \= "Focus mode", tooltip \= "Ignored if border is off.")  
focusBorderWidth \= input.int(1, "Live window border width", minval \= 1, maxval \= 5, group \= "Focus mode")

// \--- Global window size \------------------------------------------------------  
windowMins \= input.int(60, "Minutes before/after open", minval \= 5, maxval \= 240,  
     group \= "Window", tooltip \= "Half-width of each band. 60 \= 1h before to 1h after the open.")

// \--- Labels \------------------------------------------------------------------  
dispTz \= input.string("Australia/Brisbane", "Display timezone",  
     options \= \["Australia/Brisbane", "Australia/Sydney", "Asia/Tokyo", "Asia/Singapore",  
                "Asia/Dubai", "Europe/London", "America/New\_York", "America/Chicago",  
                "America/Los\_Angeles", "UTC"\],  
     group \= "Labels",  
     tooltip \= "Only changes the clock times shown in the labels. Zones stay anchored to each session's real market time.")  
showHeading \= input.bool(true, "Show session headings", group \= "Labels")  
showTime    \= input.bool(true, "Show time in labels",   group \= "Labels")  
labelBg     \= input.color(color.new(color.black, 10), "Label background", group \= "Labels")  
rangeLb     \= input.int(150, "Chip lookback (bars)", minval \= 10, maxval \= 500,  
     group \= "Labels", tooltip \= "Used to scale how far ALL chips float above price.")  
liftPct     \= input.float(6.0, "Chip lift above high (%)", minval \= 0, maxval \= 50, step \= 0.5,  
     group \= "Labels", tooltip \= "How far above price to float chips, as a % of the chip lookback range.")

// \--- Box size (shared by ALL boxes — session fills, Focus box, Forecast box) \--  
boxPadPct \= input.float(25.0, "Box height padding (% of price)", minval \= 5, maxval \= 300, step \= 5,  
     group \= "Box Size",  
     tooltip \= "Box top/bottom sit this % above/below current price. Generous by design so it reads as full-height at normal zoom levels.")

// \--- Forecast box (normal mode, all sessions shown) \--------------------------  
showFc        \= input.bool(true,   "Show next-window forecast", group \= "Forecast")  
showFcBorder  \= input.bool(false,  "Show border", group \= "Forecast",  
     tooltip \= "Off by default to match the borderless session bands.")  
fcBorderStyle \= input.string("Dashed", "Border style", options \= \["Solid", "Dashed", "Dotted"\], group \= "Forecast",  
     tooltip \= "Ignored if border is off.")  
fcBorderWidth \= input.int(1, "Border width", minval \= 1, maxval \= 5, group \= "Forecast")  
fcBorderMatch \= input.bool(true, "Border matches session colour", group \= "Forecast")  
fcBorderColor \= input.color(color.gray, "Border colour (if not matching)", group \= "Forecast")

// \--- Asia \--------------------------------------------------------------------  
asiaOn      \= input.bool(true,          "Enabled", group \= "Asia", inline \= "a1")  
asiaTz      \= input.string("Asia/Tokyo","TZ",      group \= "Asia", inline \= "a1")  
asiaH       \= input.int(9,  "Open  H",  minval \= 0, maxval \= 23, group \= "Asia", inline \= "a2")  
asiaM       \= input.int(0,  ":M",       minval \= 0, maxval \= 59, group \= "Asia", inline \= "a2")  
asiaCol     \= input.color(color.new(color.yellow, 88), "Fill", group \= "Asia", inline \= "a2")  
asiaLabel   \= input.string("Asia 3SL", "Heading text", group \= "Asia")  
asiaTextCol \= input.color(color.yellow, "Heading text colour", group \= "Asia")

// \--- London \------------------------------------------------------------------  
lonOn      \= input.bool(true,             "Enabled", group \= "London", inline \= "l1")  
lonTz      \= input.string("Europe/London","TZ",      group \= "London", inline \= "l1")  
lonH       \= input.int(8,  "Open  H",     minval \= 0, maxval \= 23, group \= "London", inline \= "l2")  
lonM       \= input.int(0,  ":M",          minval \= 0, maxval \= 59, group \= "London", inline \= "l2")  
lonCol     \= input.color(color.new(color.aqua, 88),  "Fill", group \= "London", inline \= "l2")  
lonLabel   \= input.string("London 3SL", "Heading text", group \= "London")  
lonTextCol \= input.color(color.aqua, "Heading text colour", group \= "London")

// \--- New York \----------------------------------------------------------------  
nyOn      \= input.bool(true,                 "Enabled", group \= "New York", inline \= "n1")  
nyTz      \= input.string("America/New\_York", "TZ",      group \= "New York", inline \= "n1")  
nyH       \= input.int(9,  "Open  H",         minval \= 0, maxval \= 23, group \= "New York", inline \= "n2")  
nyM       \= input.int(30, ":M",              minval \= 0, maxval \= 59, group \= "New York", inline \= "n2")  
nyCol     \= input.color(color.new(color.fuchsia, 88),"Fill", group \= "New York", inline \= "n2")  
nyLabel   \= input.string("NY 3SL", "Heading text", group \= "New York")  
nyTextCol \= input.color(color.fuchsia, "Heading text colour", group \= "New York")

// \--- Helpers \-----------------------------------------------------------------  
f\_pad2(int v)              \=\> (v \< 10 ? "0" : "") \+ str.tostring(v)  
f\_clock(int t, string tz)  \=\> f\_pad2(hour(t, tz)) \+ ":" \+ f\_pad2(minute(t, tz))  
f\_bstyle(string s)         \=\> s \== "Solid" ? line.style\_solid : s \== "Dotted" ? line.style\_dotted : line.style\_dashed

// Next occurrence of a session's open (its own TZ). Rolls to tomorrow if passed.  
f\_nextOpen(string tz, int oh, int om) \=\>  
    y  \= year(time, tz)  
    mo \= month(time, tz)  
    d  \= dayofmonth(time, tz)  
    t0 \= timestamp(tz, y, mo, d, oh, om)  
    t0 \<= time ? timestamp(tz, y, mo, d \+ 1, oh, om) : t0

// Open of the window we're CURRENTLY inside (closest open to now, wrap-safe).  
f\_curOpen(string tz, int oh, int om) \=\>  
    y  \= year(time, tz)  
    mo \= month(time, tz)  
    d  \= dayofmonth(time, tz)  
    c0 \= timestamp(tz, y, mo, d,     oh, om)  
    cP \= timestamp(tz, y, mo, d \- 1, oh, om)  
    cN \= timestamp(tz, y, mo, d \+ 1, oh, om)  
    best \= c0  
    best := math.abs(cP \- time) \< math.abs(best \- time) ? cP : best  
    best := math.abs(cN \- time) \< math.abs(best \- time) ? cN : best  
    best

// \--- Is this bar inside \[open \- windowMins, open \+ windowMins\]? \---------------  
inWindow(string tz, int openH, int openM, int half) \=\>  
    curMin  \= hour(time, tz) \* 60 \+ minute(time, tz)  
    openMin \= openH \* 60 \+ openM  
    d       \= math.abs(curMin \- openMin)  
    d      := math.min(d, 1440 \- d)  
    d \<= half

aIn \= asiaOn and inWindow(asiaTz, asiaH, asiaM, windowMins)  
lIn \= lonOn  and inWindow(lonTz,  lonH,  lonM,  windowMins)  
nIn \= nyOn   and inWindow(nyTz,   nyH,   nyM,   windowMins)

// \--- Chip float range — used for ALL chip text positions \-----------------------  
hh    \= ta.highest(high, rangeLb)  
ll    \= ta.lowest(low,  rangeLb)  
chipY \= hh \+ (hh \- ll) \* liftPct / 100.0

// \--- Box height — generous % of price, shared by every box in the script \------  
boxPad \= close \* boxPadPct / 100.0  
boxTop \= close \+ boxPad  
boxBot \= close \- boxPad

// \--- Session shading — drawn as a box spanning the FULL window width the  
// moment it opens. Anchored to the real session open (f\_curOpen) so it stays  
// centred on every timeframe. Borderless, persists as history (not deleted),  
// bounded automatically by max\_boxes\_count.  
f\_sessionBox(bool isIn, bool wasIn, int win, color fill, string tz, int oh, int om) \=\>  
    var box bid \= na  
    if isIn and not wasIn  
        openT \= f\_curOpen(tz, oh, om)  
        bid := box.new(openT \- win \* 60000, boxTop, openT \+ win \* 60000, boxBot,  
             xloc \= xloc.bar\_time, bgcolor \= fill,  
             border\_color \= color.new(color.black, 100), border\_width \= 0\)  
    bid

if not focusMode  
    f\_sessionBox(aIn, aIn\[1\], windowMins, asiaCol, asiaTz, asiaH, asiaM)  
    f\_sessionBox(lIn, lIn\[1\], windowMins, lonCol,  lonTz,  lonH,  lonM)  
    f\_sessionBox(nIn, nIn\[1\], windowMins, nyCol,   nyTz,   nyH,   nyM)

// \--- Session headings, per-window (OFF in focus mode) \-------------------------  
// Also anchored to the real session open via f\_curOpen.  
f\_heading(bool isIn, bool wasIn, string txt, color ink, float y, string tz, int oh, int om) \=\>  
    var label lid \= na  
    if isIn and not wasIn  
        openT \= f\_curOpen(tz, oh, om)  
        lid := label.new(openT, y, showTime ? txt \+ "\\n" \+ f\_clock(openT, dispTz) : txt,  
             xloc \= xloc.bar\_time, yloc \= yloc.price, style \= label.style\_label\_down,  
             color \= labelBg, textcolor \= ink, size \= size.small)  
    else if isIn and not na(lid)  
        label.set\_y(lid, y)  
    lid

if not focusMode and showHeading  
    f\_heading(aIn, aIn\[1\], asiaLabel, asiaTextCol, chipY, asiaTz, asiaH, asiaM)  
    f\_heading(lIn, lIn\[1\], lonLabel,  lonTextCol,  chipY, lonTz,  lonH,  lonM)  
    f\_heading(nIn, nIn\[1\], nyLabel,   nyTextCol,   chipY, nyTz,   nyH,   nyM)

// \--- Pick the soonest upcoming window — fill matches its session's own colour \--  
f\_nextPick() \=\>  
    int    bestNo \= na  
    string bTxt   \= ""  
    color  bInk   \= na  
    color  bFill  \= na  
    if asiaOn  
        t \= f\_nextOpen(asiaTz, asiaH, asiaM)  
        if na(bestNo) or t \< bestNo  
            bestNo := t, bTxt := asiaLabel, bInk := asiaTextCol, bFill := asiaCol  
    if lonOn  
        t \= f\_nextOpen(lonTz, lonH, lonM)  
        if na(bestNo) or t \< bestNo  
            bestNo := t, bTxt := lonLabel, bInk := lonTextCol, bFill := lonCol  
    if nyOn  
        t \= f\_nextOpen(nyTz, nyH, nyM)  
        if na(bestNo) or t \< bestNo  
            bestNo := t, bTxt := nyLabel, bInk := nyTextCol, bFill := nyCol  
    \[bestNo, bTxt, bInk, bFill\]

// \--- Draw one window as a box \+ chip (Focus mode / Forecast) \-------------------  
f\_drawBox(int center, string txt, color ink, color fill, bool isForecast) \=\>  
    sT   \= center \- windowMins \* 60000  
    eT   \= center \+ windowMins \* 60000  
    bcol \= isForecast ? (fcBorderMatch ? ink : fcBorderColor) : ink  
    bsty \= isForecast ? f\_bstyle(fcBorderStyle) : f\_bstyle(focusBorderStyle)  
    bw   \= isForecast ? (showFcBorder ? fcBorderWidth : 0\) : (showFocusBorder ? focusBorderWidth : 0\)  
    arr  \= isForecast ? "→ " : ""  
    b \= box.new(sT, boxTop, eT, boxBot, xloc \= xloc.bar\_time, bgcolor \= fill,  
             border\_color \= bcol, border\_width \= bw, border\_style \= bsty)  
    l \= label.new(center, chipY, showTime ? txt \+ "\\n" \+ arr \+ f\_clock(center, dispTz) : txt,  
             xloc \= xloc.bar\_time, yloc \= yloc.price, style \= label.style\_label\_down,  
             color \= labelBg, textcolor \= ink, size \= size.small)  
    \[b, l\]

// \--- Current / next rendering on the last bar (Focus mode / Forecast only) \-----  
var box   fb \= na  
var label fl \= na

if barstate.islast  
    if not na(fb)  
        box.delete(fb)  
    if not na(fl)  
        label.delete(fl)  
    fb := na  
    fl := na

    if focusMode  
        if aIn or lIn or nIn  
            int   co \= aIn ? f\_curOpen(asiaTz, asiaH, asiaM) : lIn ? f\_curOpen(lonTz, lonH, lonM) : f\_curOpen(nyTz, nyH, nyM)  
            string ct \= aIn ? asiaLabel   : lIn ? lonLabel   : nyLabel  
            color  ci \= aIn ? asiaTextCol : lIn ? lonTextCol : nyTextCol  
            color  cf \= aIn ? asiaCol     : lIn ? lonCol     : nyCol  
            \[b, l\] \= f\_drawBox(co, ct, ci, cf, false)  
            fb := b  
            fl := l  
        else  
            \[no, t, ink, fill\] \= f\_nextPick()  
            if not na(no)  
                \[b, l\] \= f\_drawBox(no, t, ink, fill, true)  
                fb := b  
                fl := l  
    else if showFc  
        \[no, t, ink, fill\] \= f\_nextPick()  
        if not na(no)  
            \[b, l\] \= f\_drawBox(no, t, ink, fill, true)  
            fb := b  
            fl := l