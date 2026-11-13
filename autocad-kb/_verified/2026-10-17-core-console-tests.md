# AutoCAD 2027 Core Console (accoreconsole.exe): tests run on one Windows PC, 2026-10-17

Script: `scripts/core_tests.py` (inputs made with PyMuPDF and ezdxf; accoreconsole launched with Python subprocess, `/i <dxf> /s <scr> /l en-US`, CRLF script ending in a blank line). Primary pages: -PDFIMPORT (G:ADEE1DE4), PDFIMPORTFILTER (G:79A946C3), PDFIMPORTMODE (G:669F39FF), IMAGEASYNCWAIT (G:BE447BB9).

## -PDFIMPORT works headless (VERIFIED)
- Earlier notes said PDF import is impossible in the Core Console. That was the dialog command PDFIMPORT. The command-line form works:
  `_.FILEDIA` `0`, `_-PDFIMPORT`, `_F` (File), `<pdf path>`, `<page>` (e.g. `1`), `<insertion point>` (`0,0`), `<scale>` (`1`), `<rotation>` (`0`).
  Log: `Select PDF underlay or [File] <File>: _F`, `Enter page number or [?] <1>: 1`, `Importing page 1 of PDF file: ...`.
- Units (test page with no /VP measure): 1 PDF inch = 1 drawing unit at scale 1 (72 pt -> 1.0). A PDF that carries a /VP /Measure (a TrueView plot tested later did) imports at the source drawing's units instead. The page's lower-left corner lands on the insertion point; y is the right way up. A plan plotted at 1/16" = 1'-0" imports to model inches at scale 192; 1/8" = 1'-0" at scale 96. (The help says page import ignores INSUNITS.)
- Settings matter and live in the registry. As read 2026-10-18, the console's copy is under ACAD-A101:409 `<<Unnamed Profile>>`; the MEP GUI key ACAD-A106:409 stores none. On the test machine (example values from one machine) PDFIMPORTFILTER was 1 (excludes geometry: only text came in) and PDFIMPORTMODE was 3 (combine into a block + lineweights). With PDFIMPORTFILTER 8 (everything except raster) and PDFIMPORTMODE 6 (lineweights + join segments into polylines), geometry came in as LWPOLYLINE on layer `PDF_Geometry` and text as MTEXT on `PDF_Text`.
- Pattern (save, set, import, restore, so the user's GUI defaults do not change):
```
(setq oldf (getvar "PDFIMPORTFILTER") oldm (getvar "PDFIMPORTMODE"))
(setvar "PDFIMPORTFILTER" 8)
(setvar "PDFIMPORTMODE" 6)
_-PDFIMPORT
_F
C:/path/plan.pdf
1
0,0
192
0
(setvar "PDFIMPORTFILTER" oldf)
(setvar "PDFIMPORTMODE" oldm)
```
(Corrected 2026-10-18: the first version also set FILEDIA 0 and never restored it, which left the user's file dialogs off. A script does not need it; see "FILEDIA in scripts" below. Scale 192 is for a PDF with no /VP measure; a PDF that carries /VP imports at full size at scale 1.)
- PDFIMPORTFILTER bits: 0 all, 1 no geometry, 2 no TrueType text, 4 no solid fills, 8 no raster. PDFIMPORTMODE bits: 1 combine into a block, 2 apply lineweights, 4 join line/arc segments into polylines, 8 fills as solid hatches, 16 merge collinear segments. PDFIMPORTLAYERS (0 default) picks layer assignment. SHX text in a PDF comes in as geometry; PDFSHXTEXT converts it back.
- Also tested 2026-10-18 on a large real-world plan PDF (/Rotate 270) with a PyMuPDF comparison. Still not tested: scanned (raster-only) PDFs.

## FILEDIA in scripts (VERIFIED 2026-10-18)
- The FILEDIA help page (G:99736BD7): 0 = no file dialogs; 1 (initial value) = dialogs. The page adds that a plain command prompt is shown instead of a dialog whenever a script, an AutoLISP program or an ObjectARX program is running. Saved in the registry (`FixedProfile\General Configuration\FileDialog` under each product key).
- Test (`scripts/fd_test.py`): console script set FILEDIA 1, then `_-PDFIMPORT` `_F` `<pdf>` `1` `_non` `0,0` `1` `0`. Log: `Enter filename for PDF import: <path>`, `Importing page 1 of PDF file`, 3 objects imported, exit 0 with no hang. The script restored FILEDIA to the value it found, and the registry read the same before and after.
- Rule: never set FILEDIA in a .scr script; it is not needed and it persists. Only commands typed into the GUI through SendCommand (no script active) may need FILEDIA 0, and then save and restore it.
- Second test, a real two-sheet build: a sheet-building script with its `FILEDIA 0` and `CMDDIA 0` lines removed, run from a scratch copy, console script started with FILEDIA 1 and CMDDIA 1. `_.SAVEAS` wrote the DWG, each `-PLOT` took `Enter file name` at the prompt, both sheet PDFs came out, exit 0 in 31 s, registry unchanged.
- The console's own values before the fix (A101 key): FILEDIA 0 and CMDDIA 0 (both initial 1, left by earlier scripts); LOGFILEMODE 0 and BACKGROUNDPLOT 2 (initial values).
- Where the values live (tested 2026-10-18):
  - A GUI window (MEP, `scripts/test_uservars.py`) writes FILEDIA to `FixedProfile\General Configuration\FileDialog` the moment it is set, in both directions, and does not write it again at close.
  - The Core Console always starts with FILEDIA 0 and never saves it: after a console script set FILEDIA 1, and again after the registry value was set to 1 directly, a fresh console still read 0. A plain AutoCAD window started with `/product ACAD` (as a desktop shortcut does) read FILEDIA 1 from the same registry value.
  - The console does save CMDDIA: set to 1 in one console run, a fresh console read 1.
  - Registry names (per product key, ACAD-A101:409 or ACAD-A106:409): FILEDIA = `FixedProfile\General Configuration\FileDialog`; CMDDIA = `FixedProfile\General Configuration\CommandDialogs`; LOGFILEMODE = `Profiles\<profile>\General\LogFileOpen`, which MEP removes on close when LOGFILEMODE is 0. After one MEP test, LogFileOpen read 1 for "AutoCAD MEP (US Imperial)"; set to 0, a fresh MEP window read LOGFILEMODE 0, FILEDIA 1, CMDDIA 1.
- Fix: FileDialog set to 1 under ACAD-A101:409 (plain AutoCAD) and ACAD-A106:409 (MEP); fresh AutoCAD and MEP windows read FILEDIA 1 and CMDDIA 1 (`scripts/check_gui_dialogs.py`).
- Caveat: for a short time, separate processes read different A101 FileDialog values while other scripts were opening and closing AutoCAD windows; later every process read 1 under both keys. The cause was not found; the tool sandbox was ruled out. Read FileDialog right before you rely on it. If dialogs are off again, read FileDialog first and look for a script that sets FILEDIA without restoring it.
- `uservars.py` in the autocad skill (`../../claude/skills/autocad/scripts/uservars.py`) for GUI drivers: `save()` before setvar, `restore()` after; it also restores at exit and writes FileDialog straight to the registry if MEP no longer answers. Live test 10 of 10 (`scripts/test_uservars.py`, `scripts/uv_child.py`).

## Raster images in headless plots (VERIFIED, partly)
- AutoCAD 2026 and later load raster images in the background after a drawing opens; IMAGEASYNCWAIT waits for them (help lists PLOT, -PLOT, PUBLISH, -EXPORT, SAVE, SAVEAS among the affected commands).
- Test: one IMAGE (PNG) plus a line, model-space -PLOT to PDF.
  - Without IMAGEASYNCWAIT: "Effective plotting area: 17.00 wide by 0.00 high" (the image was not loaded, extents ignored it); no image in the PDF.
  - With `_IMAGEASYNCWAIT` first: "Effective plotting area: 17.00 wide by 10.21 high" (the image loaded and counted in extents), but the PDF still had no image.
- Conclusion: in the Core Console the image loads but does not render into the plot. Keep stamping PNGs into the plotted PDF with PyMuPDF (`page.insert_image`), and run IMAGEASYNCWAIT anyway before plotting or saving drawings that hold images.

## The Core Console help page itself (primary source, fetched 2026-10-17)
`https://help.autodesk.com/cloudhelp/2027/ENU/AutoCAD-Core-Console/files/AUTOCAD_CORE_CONSOLE.html`
- Usage: `AcCoreConsole.exe [/i <input dwg>] /s <script> [/product <product>] [/l <language>] [/isolate <userid> <userDataFolder>] [/readonly] [/p[rofile] <profile>] [/loadmodule <module>]`. There is no `/ld` switch (an earlier MEP probe used `/ld`).
- No command that shows a dialog or palette runs; use command-line forms (-LAYER for LAYER, CHPROP/CHANGE for PROPERTIES). Listed as unsupported include NEW, CLOSE, PDFATTACH, -PDFATTACH, DGNATTACH, -DGNATTACH, PROPERTIES, LAYER, CLASSICLAYER, CLASSICXREF, CUI, PASTECLIP, PAN, QUICKCALC, SCALELISTEDIT, ULAYERS, MLEDIT, MLSTYLE, RIBBON.
- The ActiveX API is NOT available in the Core Console (no vla-/vlax- from AutoLISP, no COM). .NET plug-ins must not reference AcMgd.dll (can crash it); ObjectARX apps for it are CRX files.
- Custom programs must sit in a trusted location or loading fails (`; error: File load canceled`), which fits the NETLOAD refusal in `2026-10-17-dotnet-plugin-build.md`.

## Reading MEP drawings headless (VERIFIED)
- Opening an AutoCAD MEP drawing in a plain Core Console run (no extra switches) auto-loads the MEP object enablers (`(arx)` listed aecbase.dbx, aecbpipebase.dbx, aecbhvacbase.dbx, aecbbldsrv.dbx, aecbplumbingbase.dbx, aecbelecbase.dbx ...). Objects come in as real `AECB_PIPE` and `AECB_PIPEFITTING`, not proxies; `/product MEP` and `/loadmodule AecBase.dbx` changed nothing.
- `entget` on them returns only the common header (type, handle, layer). `vla-` calls print nothing (no ActiveX).
- `_.LIST` + `_ALL` + blank prints the full data per object: Length, Cut Length, Start Point, End Point, Slope, Routing Preference, System Reference (name and description), Style Reference (e.g. "4 Inch Commercial Pipe", "4.00 Inch Glued - Sch 40 - PVC Elbow 90.0 Deg"), Insulation Thickness, and Connection Points for fittings, in feet-inch format. Parse the UTF-16 log for a headless takeoff (pipe length by size and system, fitting counts) with no MEP window open.
- (2026-10-18) `_ALL` leaves out objects on frozen layers; pass an `(ssget "X")` set as `!name` instead. Built into `mep_takeoff.py` in the autocad skill (`../../claude/skills/autocad/scripts/mep_takeoff.py`); proof in `2026-10-18-mep-takeoff-test.md`.
