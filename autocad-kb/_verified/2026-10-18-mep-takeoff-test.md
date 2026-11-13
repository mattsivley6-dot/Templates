# Headless MEP takeoff (mep_takeoff.py): built and proven, 2026-10-18

Tool: `mep_takeoff.py` in the autocad skill (`../../claude/skills/autocad/scripts/mep_takeoff.py`). Test scripts and data: `scripts/mto_probe_list.py`, `scripts/mto_make_test_dwg.py`, `scripts/mto_check_test.py`, `scripts/mto_test/` (design, COM read-back, takeoff output, check report). Builds on "Reading MEP drawings headless" in `2026-10-17-core-console-tests.md`.

## How it works
- `py -3.14 mep_takeoff.py <a.dwg> [b.dwg ...] [--out DIR] [--name NAME]`. Each DWG is copied to `%TEMP%\mep_takeoff\<stamp>_<name>\`; `accoreconsole.exe /i <copy> /s <scr> /l en-US` runs from that folder through Python `subprocess.Popen` (stdout to the log, `CREATE_NO_WINDOW`), `wait(timeout)` (600 s default) and `kill()` on TimeoutExpired; the copy is deleted after. `--log <file>` re-parses a saved log with no AutoCAD.
- Script on the copy: print INSUNITS, LUNITS, LUPREC, AUNITS, AUPREC, TILEMODE; `TILEMODE 1`; `LUNITS 2`, `LUPREC 8`, `AUNITS 0`, `AUPREC 4` (drawing-saved variables, the copy is discarded); `(ssget "X" '((0 . "AECB_*") (410 . "Model")))`; a LISP count by type; xref names from the BLOCK table; `_.LIST` `!mto_ss` (one blank); an END marker; `_.QUIT` `_Y`.
- Output: `<name>_objects.csv` (one row per object: handle, type, layer, system, routing preference, size, part, length and cut length ft, start and end point, slope %, in/ft and degrees, insulation, connection points), `<name>_summary.csv` and `<name>_summary.txt` (pipe ft by system and size with system totals, fittings by type and size, by part and size, insulated pipe, other MEP objects).
- Cross-checks printed in the summary: database count by type = parsed objects, LIST "N found" = parsed, no duplicate handles, END marker seen, no "Press ENTER", console errors, Length = start-to-end distance, xrefs named. Exit 0 ok, 2 a run did not finish, 3 a count check failed.

## Facts found live (2026-10-18)
1. LIST honors LUNITS and LUPREC for MEP objects. With LUNITS 2 and LUPREC 8 a pipe printed `Length : 136.65000000`; with the drawing's own architectural units (LUPREC 5) the same pipe printed `11'-4 21/32"` (rounded to 1/32 in).
2. `_ALL` leaves out objects on frozen layers: a pipe on a frozen layer was skipped ("8 found" of 9). Objects on a locked layer were still listed, although the SELECT help (G:0DD5DA73) describes ALL as skipping both frozen and locked layers. A `(ssget "X")` set given as `!name` at LIST's Select objects prompt lists everything, frozen included.
3. An empty set `(ssadd)` at the prompt gives "0 found" and LIST ends cleanly (tested on a drawing with no MEP objects).
4. No paging: 700 objects listed in one pass (18 s run, 440,024-character log), no "Press ENTER to continue".
5. The LIST `Slope` field is the rise angle in degrees, formatted by AUNITS and AUPREC (`-0.5729` for a 6 in drop over 50 ft; it matched atan2 to 0.001 deg on two sloped pipes in the 700-object drawing), and it reads 0 on vertical risers. The tool computes slope from the start and end points.
6. A drawing saved on a layout tab (TILEMODE 0) lists in full after `(setvar "TILEMODE" 1)`.
7. `CREATE_NO_WINDOW` works for accoreconsole: no window, log still written.
8. Name formats. Pipes: `4 Inch Commercial Pipe`, `1-1/2 Inch Commercial Pipe`, `3/4 Inch Commercial Pipe`. Fittings: `4.00 Inch Glued - Sch 40 - PVC Elbow 90.0 Deg`, `4.00 Inch x 2.00 Inch Glued - Sch 40 - Concentric Reducer`, `1.50 Inch Glued - Sch 40 - PVC Tee`. `System Reference` reads `Name (Description)`; COM `SystemName` reads `Name (Abbreviation)`.
9. `Insulation Thickness` prints only when it is not zero.
10. On a 2 in branch off a 4 in main, MEP placed: 4 in tee, a 5.2031 in piece of 4 in pipe, then the 4 x 2 reducer. So the main size's footage includes these short stubs.
11. A takeoff run leaves the user's settings alone. FILEDIA in the registry key the Core Console uses (`HKCU\...\R26.0\ACAD-A101:409\FixedProfile\General Configuration\FileDialog`) read 1 before and after a run. The script sets only CMDECHO and variables saved in the drawing, and only on the discarded copy.

## Test drawing (scripts/mto_make_test_dwg.py)
Minimized AutoCAD MEP 2027 over raw COM on a copy of `Routing Preferences (US Imperial).dwg`, routing preference Glued, all at z = 120 in, every value checked before it was sent. COM answered 51 s after launch; one "Drawing Recovery" dialog at start was closed by message; 5 runs drawn in 28 s; whole script 103 s. Systems CHWS and CHWR made by COM. The launch changed the registry default profile to MEP; the script put back "AutoCAD Architecture (US Imperial)" and LOGFILEMODE 0.

| Run | System | Size | Drawn path (in) | Drawn |
|---|---|---|---|---|
| R1 | CHWS | 4" | (0,0) > (480,0) > (480,360) | 70.0000 ft |
| R3 | CHWS | 2" | branch from R1 at (240,0) > (240,240) | 20.0000 ft |
| R2 | CHWR | 2" | (0,-60) > (360,-60) > (360,-300); 1-1/2" insulation; layer locked | 50.0000 ft |
| R4 | CHWR | 1-1/2" | (600,0,120) > (1200,0,114) (end moved by COM); layer frozen | 50.0025 ft |
| R5 | Standard | 3/4" | (0,600) > (120,600) | 10.0000 ft |

Total drawn 200.0025 ft. Result: 9 pipes, 4 fittings. Saved on the layout tab.

## Results (scripts/mto_check_test.py: ALL CHECKS PASSED)
- Takeoff run: 7 to 8 s; 13 MEP objects in the database, 13 listed, 13 parsed; no warnings.
- Against MEP's COM read-back, handle by handle (13 of 13): same type, layer, size name and system; length and cut length within 0.000004 in (CSV rounding); start and end points exact; insulation exact; fitting connection points equal the COM connector locations.
- Pipes plus fittings fill every drawn run, no gap and no overlap (difference 0.000000 in):

| Run | Drawn ft | Pipe ft | Fittings ft | Pieces | Fittings |
|---|---|---|---|---|---|
| R1 | 70.0000 | 69.1255 | 0.8745 (elbow 5.4 in, tee run 5.094 in) | 3 | 2 |
| R3 | 20.0000 | 19.6289 | 0.3711 (tee branch 2.547 in, reducer 1.9062 in) | 2 | 2 |
| R2 | 50.0000 | 49.7635 | 0.2365 (elbow 2.8376 in) | 2 | 1 |
| R4 | 50.0025 | 50.0025 | 0 | 1 | 0 |
| R5 | 10.0000 | 10.0000 | 0 | 1 | 0 |

- Summary table, each equal to the COM lengths of the same pipes: CHWS 4" 4 pieces 69.5591 ft; CHWS 2" 1 piece 19.1953 ft; CHWR 2" 2 pieces 49.7635 ft; CHWR 1-1/2" 1 piece 50.0025 ft; Standard 3/4" 1 piece 10.0000 ft. All pipe 198.5204 ft + fittings 1.4821 ft = 200.0025 ft = drawn.
- Fittings by type and size: Elbow 90 4" 1, Elbow 90 2" 1, Tee 4" 1, Reducer concentric 4" x 2" 1 (as expected).
- The pipe on the frozen layer is in the takeoff; slope -1.0 % (-0.12 in/ft, -0.5729 deg).
- Insulated: CHWR 2" with 1-1/2" insulation, 49.7635 ft.
- `--keep-units` (parse the drawing's architectural text): worst piece difference 0.0156 in (1/64 in, the rounding of 1/32 in text).
- Scale: a 700-object MEP drawing in 18 s, counts match. A two-drawing run equals the sum of the separate runs. Two inputs with the same file name from different folders are checked separately.

## Limits and open items
- Objects inside xrefs or blocks are not listed; the summary names any xrefs so their DWGs can be run too. Not yet tried: a drawing with xrefs, ducts, MvParts, a metric drawing, native decimal or engineering units.
- Pipe footage is pipe pieces between fittings (what the drawing holds), not center-to-center; the fitting share was 0.7 % of the drawn length in this test.
- Two MEP instances: a second acad.exe started from the command line cannot be reached by COM, because every instance shares one Running Object Table name and lookups give the first (`2026-10-18-mepcom-two-instances.md`). One started with `mepcom.launch()` can be reached, and `mepcom.bind(pid)` keeps a script on its own instance (`2026-10-18-mepcom-com-launch.md`, which also lists open problems).
