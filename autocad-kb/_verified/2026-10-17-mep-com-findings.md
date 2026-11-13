# AutoCAD MEP 2027 COM API: what was tested live (2026-10-17)

Primary sources: the live test logs in this folder (`2026-10-17-mep-com-probe2.log`, `...probe3.log`), the probe scripts in `scripts/` (`mep_api_probe2.py`, `mep_api_probe3.py`), the installed type libraries (read from `C:\Program Files\Common Files\Autodesk Shared\*89.tlb`), the AEC ProgIDs registered in the registry, and the local API help (CHM, buildingauto reference).
Test drawing: a scratch copy of `C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg`, opened in AutoCAD MEP 2027 (profile "AutoCAD MEP (US Imperial)") over COM from Python 3.14 with raw IDispatch (`mepcom.py` in the autocad skill, `../../claude/skills/autocad/scripts/mepcom.py`).

## Entry points (VERIFIED)
- AEC/MEP COM ProgIDs carry version 8.9 on AutoCAD 2027: `AecX.AecbPipeDatabase.8.9`, `AecX.AecbDatabase.8.9`, `AecX.AecScheduleApplication.8.9`, `AecX.AecbApplication.8.9`, `AecX.AecBaseApplication.8.9` (503 AEC ProgIDs registered).
- Pattern: `obj = acad.GetInterfaceObject("AecX.AecbPipeDatabase.8.9")`, then `obj.Init(doc.Database)`, then read collections (PipeSystemDefs, PipeStyles, PipeFittingStyles ...). Same Init pattern for `AecbDatabase` (Graphs).
- `AecScheduleApplication.PropertySetDefs(doc.Database)` returned the 5 property set definitions in the test drawing; `PropertySets(entity)` returned the sets on an object (0 on a new pipe).

## Creating things
- MEP objects (pipe, duct, fitting, MvPart) cannot be created by COM: every Aecb entity in the API help says "Create using: N/A", and `vla-AddCustomObject "AecbDbPipe"` was refused (2026-10-16). Draw them with the command line (`_-AECBPIPEADD` etc.) sent by SendCommand. (API help, buildingauto reference)
- Pipe system definitions CAN be created by COM (VERIFIED): `PipeSystemDefs.Add("CHWS")`, then `LabelName`, `FamilyName`, `Description` are writable. The new system shows in the drawing dictionary `AECB_PIPESYSTEMDEFS` and is usable at once at the `-AECBPIPEADD` SYstem prompt. Pipes drawn in it report `SystemName "CHWS (CHWS)"`, `SystemAbbreviation "CHWS"`, `SystemFamily "Chilled Water"`.
- `LayerKey` of a system definition is read-only over COM (type library: get only); a COM-made system has an empty layer key, so its pipes land on the default layer `M-Pipe-Std`. Set the layer per object instead (below).
- Schedule tables can be created by COM per the API help: `ModelSpace.AddCustomObject("AecScheduleTable")` (scheduleauto reference; NOT tested yet).

## Routing preferences
- The COM collection `AecbPipeDatabase.PipePartCatPrefStyles` is NOT the routing preference list: it reported Count 1 and `Has("Glued")` False in a drawing that holds 25 routing preferences (VERIFIED). Read routing preference names from the drawing dictionary instead:
  `(dictsearch (namedobjdict) "AECB_PIPE_PARTROUTINGPREFERENCES_STYLES")`, group-3 entries.
- The 25 routing preferences in `Routing Preferences (US Imperial).dwg`: Brazed Copper; Butt Welded; Butt Welded and Socket Welded; Cast Iron Soil Pipe - Bell x Spigot; Cast Iron Soil Pipe - No Hub Fittings; D.I. Mechanical Joint; D.I. Push On Joint; D.I. Threaded Flanged - 150 Lb.and Threaded; D.I. Threaded Flanged - 250 Lb.and Threaded; DWV Copper; Generic Flanged; Generic Socket Weld; Generic Threaded; Glued; Grooved; Grooved and Threaded; HDPE - IPS; Placeholder; Sanitary PVC DWV; Sanitary PVC Hub x No Hub; Slip on Flanged - 150 Lb. and Threaded; Socket Weld 3000-lb.; Standard; Threaded 2000-lb.; Weld Neck Flanged - 150-lb. and Threaded.
- Most names contain spaces. At the command line a space ends the answer, so type only space-free names (Glued, Grooved, Standard, Placeholder) or answer by index number: the prompt reads `Routing Preference name, index number or [?] <Glued>:` (VERIFIED prompt text).

## -AECBPIPEADD prompts (VERIFIED from the command log, LOGFILEMODE 1)
```
Start point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Slope/Match/preFerences]:
  R  -> Routing Preference name, index number or [?] <Glued>:
  SY -> System name, index number or [?] <Standard>:
  SI -> Nominal Size or [?] <1">:
Next point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Compass/Plane/roTAte/Slope/Match/New run/preFerences]:
(after the 2nd point the SYstem option drops out and Undo appears)
```
Sequence that worked: `_-AECBPIPEADD`, `R`, `Glued`, `SY`, `CHWS`, `SI`, `4"`, `_non`, `0,0,120`, `_non`, `240,0,120`, `_non`, `240,240,120`, blank, blank. Result: 2 pipes plus a "Glued - Sch 40 - PVC Elbow" (SizeName "4.00 Inch Glued - Sch 40 - PVC Elbow 90.0 Deg"); each pipe 237.3 in long because the elbow takes 2.7 in of each leg.
- Never send an unchecked value: v1 of the test sent an error string with spaces as the routing preference name; MEP then spun at the prompt (about 60% of a core), rejected every COM call ("Call was rejected by callee") and had to be killed. After the kill, the next launch stopped on a "Drawing Recovery" dialog (no #32770 buttons except Close) that blocked COM until it was closed with WM_CLOSE.

## Reading pipes (VERIFIED)
`AecbDbPipe` over raw IDispatch: StartPoint, EndPoint, MidPoint, Length, CutLength, SizeName ("4 Inch Commercial Pipe"), CrossSectionSize ("4 1/2" = OD), NominalSize (4.0), SystemName, SystemAbbreviation, SystemFamily, PartDescription ("Commercial Pipe"), Name, Type ("Pipe"), SubType, Elevation, TopElevation (122.25 for a 4 in pipe at 120), BottomElevation (117.75), LockSize, InsulationThickness, Layer, Handle. `StyleName` raised an error.
Fittings (`AecbDbPipeFitting`): PartDescription, SizeName, SystemName.

## Changing pipes (VERIFIED)
- `Elevation` (put) moves the whole pipe; it then lost its connection to the elbow (ConnectedMembers None) until moved back.
- `InsulationThickness` (put) works.
- `StartPoint` / `EndPoint` (put) work ONLY with a typed double array: `win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))`. A plain Python tuple fails with E_INVALIDARG.
- `Break(point)` works with the same VT_R8 array; it returns the new object's id and adds a pipe.
- `SystemName` (put) needs the full display string `"CHWS (CHWS)"` (name plus abbreviation in parentheses); `"CHWS"` alone fails (E_FAIL). "Standard" works as is.
- `Layer` (put) works on MEP pipes like any AutoCAD entity.

## Connectivity (VERIFIED)
- `Connectors.Count` reports 3 on a straight pipe and on an elbow, but only Item(0) and Item(1) are valid; Item(2) raises. Loop to Count-1 with try, or stop at the first error.
- Connector: Location, Direction (unit vector), ConnectionType ("Undefined_Connection_Type" on Glued PVC), WidthorDiameter (4.0), `ConnectedMembers` = a tuple of the connected objects (or None when open).
- `AecbDatabase.Graphs` (after Init) gave one graph per connected network; `graph.Count` and `graph.Item(k)` list its members (pipes and fittings). `graph.Iterator` is not reachable by name over IDispatch ("Unknown name").

## Undocumented helpers found in the type libraries (NOT tested)
`AecX.AecbGuiSize.8.9` (GetSizeListFromRoutingPreference, SizeExistsInRoutingPreference, GetBendAngles), `AecX.AecbGuiModify.8.9` (Modify/Modify2/Modify3 resize objects by ObjectIds, GetElbowList, GetCutLengths), `AecX.AecbPartQuery.8.9` (catalog query by Domain/Type/SubType/parameters), `AecX.AecbDuctInstantSizing.8.9`. They are internal UI helpers: test on a scratch copy before relying on them.

## Session facts (VERIFIED 2026-10-17)
- MEP answered COM 46 s after launch (earlier runs saw about 3.5 min).
- `PRODUCT` system variable reads "AutoCAD" even in AutoCAD MEP; use `CPROFILE` ("AutoCAD MEP (US Imperial)") to tell.
- The registry default profile under `HKCU\Software\Autodesk\AutoCAD\R26.0\ACAD-A106:409\Profiles` can change between launches (seen as "AutoCAD MEP (US Imperial)" and as "AutoCAD Architecture (US Imperial)"). Read it before you rely on it.
