# 02 - Piping

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

How AutoCAD MEP 2027 (US Imperial) pipe works, for chilled-water and hydronic layout: the tested way to draw pipe from a script, reading and editing pipe over COM, routing preferences, pipe system definitions, pipe layout preferences, adding and connecting pipe and fittings, joints and cut length, slope, sizing, modifying runs, flex pipe, custom fittings, pipe display and pipe annotation.
Tags: [AUTO] = works from the command line or a script. [GUI] = dialog, palette or grip only. [VERIFIED] = tested live on a test PC (notes in the `_verified/` folder). (inference) = the writer's conclusion, not stated in a source. Citations: G:xxxxxxxx links open the Autodesk help page with that GUID; KB: links open the Autodesk support article, summarized here in our own words. Unlinked codes are plain references.
Plumbing lines are a different object and are covered here only where they get confused with pipe.

Contents
1. Draw pipe from a script: the tested recipe (part 1)
2. COM: read and edit pipe; 2b. what stops an unattended run (part 2)
3. Profile, catalogs, routing preferences (part 3)
4. System definitions, pipe layout preferences, layout rules (part 4)
5. Adding pipe: palette properties and defaults, runs, risers, elevation lock, offsets, cut length (part 5)
6. Connecting: snaps, Add grips, existing pipe, takeoffs, routing solutions, fitting override, part-choice dialogs, parallel routing (part 6)
7. Connectors, joints, CEL and cut length, fitting tolerance, sloped piping (part 7)
8. Sizing and modifying: size rules, new catalog sizes, Modify Run, break/merge, fittings, grips, selection, match (part 8)
9. Pipe equipment (MvParts), flow direction, flex pipe, custom fittings (part 9)
10. Pipe display and annotation (part 10)
11. Troubleshooting, command index, untested items (part 11)

## 1. Draw pipe from a script (tested recipe)

### Ground rules
- Pipe, pipe fittings, ducts and MvParts cannot be created through COM. The MEP COM API reference installed with the product lists no create method for any Aecb entity, and `vla-AddCustomObject "AecbDbPipe"` was refused in a test. Draw them on the command line with SendCommand. [VERIFIED]
- The help documents PIPEADD, which runs off the Properties palette ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697), [G:24D620D6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24D620D6-32CA-4378-8B02-C7F2E1583DF7)). The command-line form tested on the test PC is `_-AECBPIPEADD`. [VERIFIED]
- About Adding Pipes lists PIPEADD, PIPEADDSELECTED, PIPEFLEXADDSELECTED and PIPECONVERT ([G:6854A352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6854A352-8B0C-4DBE-94B5-F644B91AFB04)). No -PIPEADD dash form and no pipe system variable is documented.
- Why the name is AECBPIPEADD: the help's command search page says the typed names of MEP toolset commands carry an Aecb prefix ("aecbPipeAdd instead of PipeAdd") ([G:C4C54B64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C4C54B64-5775-4AA1-862B-3541F57EE6B4)). So `-AECBPIPEADD` is the dash (no palette) form of PIPEADD (inference from that rule plus the live test). Same pattern: `-AECBMVPARTADD` also ran in an earlier test. Other `-AECB...ADD` names follow the rule but are not tested.

### -AECBPIPEADD prompts [AUTO] [VERIFIED]
Exact text from the AutoCAD command log (LOGFILEMODE 1):
```
Start point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Slope/Match/preFerences]:
  R  -> Routing Preference name, index number or [?] <Glued>:
  SY -> System name, index number or [?] <Standard>:
  SI -> Nominal Size or [?] <1">:
Next point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Compass/Plane/roTAte/Slope/Match/New run/preFerences]:
After the 2nd point, SYstem drops out and Undo is added:
Next point or [Routing preference/SIze/Lock size/Tolerance off/Elevation/Justification/Compass/Plane/roTAte/Slope/Match/New run/preFerences/Undo]:
```
- Only R, SY and SI were tested. By the AutoCAD capital-letter rule the other keywords should be L, T, E, J, S, M, F, C, P, TA, N, U (inference).
- System cannot be changed after the 2nd point of a run (the option is gone). [VERIFIED]
- Defaults seen in the test drawing: routing preference <Glued>, system <Standard>, size <1">. The help gives palette defaults of Standard, Standard and 2" the first time, then the last used size ([G:E85C2D51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E85C2D51-3AFD-4F3D-9567-ACC9A7D2FCF5)). Defaults change with drawing and session, so always answer R, SY and SI (inference).

### Sequence that worked [VERIFIED]
SendCommand string, every answer followed by a newline (Enter):
```
_-AECBPIPEADD\nR\nGlued\nSY\nCHWS\nSI\n4"\n_non\n0,0,120\n_non\n240,0,120\n_non\n240,240,120\n\n
```
Result and observations:
- 2 pipes and 1 elbow "Glued - Sch 40 - PVC Elbow" (SizeName "4.00 Inch Glued - Sch 40 - PVC Elbow 90.0 Deg"). The elbow was inserted automatically at the 90 degree turn.
- Each pipe was 237.3 in long: the elbow took 2.7 in of each 240 in leg.
- Pipe Elevation read 120.0, the z of the typed points.
- `_non` before each point turns off running object snaps for that pick.
- The size answer was typed as `4"` (with the inch mark).
- Two final blank Enters ended the command; AutoCAD was idle afterward.
- No dialogs appeared (the probe ran a dialog watcher; it logged "dialogs seen: []").
- Material came from the parts, not the routing preference name: under routing preference Glued the pipes reported PartDescription "Commercial Pipe", SizeName "4 Inch Commercial Pipe", CrossSectionSize "4 1/2" (the OD), while the elbow was PVC. Read material from the objects.
- Length and CutLength were both 237.3 on these pipes, so no connector engagement length was added at this glued elbow. Do not assume CEL is always added (cause not known; see part 7).

### Rules for values sent to prompts
- A space ends an answer at the command line. Routing preference names with spaces cannot be typed. Use a space-free name (Glued, Grooved, Standard, Placeholder) or answer with the index number. [VERIFIED]
- Name your own system definitions without spaces (CHWS, CHWR, HWS, HWR) so they can be typed at the SYstem prompt. CHWS was made this way and accepted. [VERIFIED for CHWS]
- Never send an unchecked value. One early test sent an error string with spaces as the routing preference name. MEP spun at the prompt (about 60% of a core), rejected every COM call ("Call was rejected by callee") and had to be killed. The next launch stopped on a "Drawing Recovery" dialog that blocked COM until it was closed with WM_CLOSE. [VERIFIED]
- Validate every name against the drawing dictionaries first (part 2). [VERIFIED method]
- (inference, not tested) `?` at the R or SY prompt should list names with their index numbers. Index base and order are not verified; read the list before answering by number.
- (inference, not tested) AutoLISP `(command "_-AECBPIPEADD" "_R" "<name with spaces>" ...)` passes each string argument whole and may get around the space problem. WARNING: in an earlier test, sending MEP pipe commands through LISP `(command ...)` opened the Properties palette and hung MEP. Try it only in a throwaway session with a dialog watcher, never in a working session. Answering by index number is the safe route.

### Other keywords at the add prompt [AUTO]
- `n` = New run while laying out; then set the new run's properties ([G:BD4D846C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BD4D846C-105D-4779-9095-8109FEAB0EA1)). Shown as "New run" in -AECBPIPEADD [VERIFIED prompt].
- Slope: type `S`, Enter, then the value. To force a new pipe exactly level: click the first point, `S`, Enter, `0` with no decimal digits, Enter, then the end point ([KB:000496823](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-grip-for-MEP-objects-like-conduits-is-missing-in-AutoCAD-MEP.html)). For vertical or sloped routing: `S`, then the angle (90 = vertical), Enter, then route ([KB:000550597](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Vertical-routing-in-AutoCAD-MEP.html)). How the value is read follows the drawing's slope format ([G:58EFC45B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58EFC45B-7BF0-4378-BD88-4B76DF549576)) (inference for the command line).
- Match: copy properties from an existing object. For pipe: System, Elevation, Justification, Routing preference, Size, Insulation ([G:535EEBD2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-535EEBD2-4C3A-4D0B-B755-F40536D66000)). The page's example is CONDUITADD; Match is in the -AECBPIPEADD option list [VERIFIED prompt].
- Plane (with the compass on): each `p` switches the UCS plane, rotating the axes X to Y, Y to Z, Z to X; `p` three times returns to the start ([G:9F8199F2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F8199F2-616E-4458-9CAA-D77BC4396DFE), [G:2CC1B7FF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2CC1B7FF-22E1-4B4D-84BD-11BEADCDB609)).
- preFerences: opens the Pipe Layout Preferences dialog (inference: a dialog, so it stops a script).
- Tolerance off: (inference) the command-line form of Use fitting tolerance = No, which the help recommends for pressure piping ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697), [G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- Lock size: (inference) the command-line form of the palette's Size lock ([G:E85C2D51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E85C2D51-3AFD-4F3D-9567-ACC9A7D2FCF5)).
- Routing solutions, when the new pipe meets an object at another elevation or off its centerline: `n` (Next) or `p` (Previous) + Enter steps through solutions; `a` + Enter accepts the previewed one; a solution number then Accept takes that one ([G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926)). This prompt waits for input, so a script must answer it.

## 2. COM: read and edit pipe [VERIFIED]

All facts in this chapter were tested in AutoCAD MEP 2027, profile "AutoCAD MEP (US Imperial)", from Python over raw IDispatch, on a scratch copy of the shipped routing preference library drawing `<ProgramData>\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg`. [VERIFIED]

### Entry points
- AEC/MEP ProgIDs carry version 8.9 on AutoCAD 2027: `AecX.AecbPipeDatabase.8.9`, `AecX.AecbDatabase.8.9`, `AecX.AecScheduleApplication.8.9`, `AecX.AecbApplication.8.9`, `AecX.AecBaseApplication.8.9`.
- Pattern: `pdb = acad.GetInterfaceObject("AecX.AecbPipeDatabase.8.9")`, then `pdb.Init(doc.Database)`, then read collections: PipeSystemDefs, PipeStyles, PipeFittingStyles, PipeFlexStyles, PipeCustomFittingStyles, PipeRiseDropStyles.
- Same Init pattern for `AecbDatabase` (gives Graphs, below).
- `PRODUCT` reads "AutoCAD" even in AutoCAD MEP. Check `CPROFILE` instead; it read "AutoCAD MEP (US Imperial)".
- Time from launch to the first COM answer varied from under a minute to several minutes in tests. Poll until COM answers before sending work.

### Read names before answering prompts
- Routing preferences: AutoLISP `(dictsearch (namedobjdict) "AECB_PIPE_PARTROUTINGPREFERENCES_STYLES")`, take the group-3 entries.
- Pipe system definitions: `(dictsearch (namedobjdict) "AECB_PIPESYSTEMDEFS")`, group-3 entries.
- The probe got LISP output back by having LISP write a file: `(progn (setq f (open "<path>" "w")) <body> (close f) (setq f nil) (princ))` sent with SendCommand, then reading the file.
- Do NOT use `AecbPipeDatabase.PipePartCatPrefStyles` for routing preferences. It reported Count 1 and `Has("Glued")` False in a drawing that holds 25.
- The 25 routing preferences in `Routing Preferences (US Imperial).dwg`: Brazed Copper; Butt Welded; Butt Welded and Socket Welded; Cast Iron Soil Pipe - Bell x Spigot; Cast Iron Soil Pipe - No Hub Fittings; D.I. Mechanical Joint; D.I. Push On Joint; D.I. Threaded Flanged - 150 Lb.and Threaded; D.I. Threaded Flanged - 250 Lb.and Threaded; DWV Copper; Generic Flanged; Generic Socket Weld; Generic Threaded; Glued; Grooved; Grooved and Threaded; HDPE - IPS; Placeholder; Sanitary PVC DWV; Sanitary PVC Hub x No Hub; Slip on Flanged - 150 Lb. and Threaded; Socket Weld 3000-lb.; Standard; Threaded 2000-lb.; Weld Neck Flanged - 150-lb. and Threaded.
- That drawing holds only one pipe system definition, "Standard".
- Chilled water: the help's example chilled-water spec is threaded commercial steel at 3" and smaller and 150 class weld neck flanged commercial steel at 3 1/2" and larger ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)). The shipped name "Weld Neck Flanged - 150-lb. and Threaded" reads like that spec (inference: its size ranges were not inspected). It has spaces, so pick it by index number at the prompt.

### Create a pipe system definition [VERIFIED]
- `sd = PipeSystemDefs.Add("CHWS")`, then `LabelName`, `FamilyName`, `Description` are writable (test: LabelName "CHWS", FamilyName "Chilled Water").
- The new system appears in `AECB_PIPESYSTEMDEFS` and works at once at the -AECBPIPEADD SYstem prompt.
- Pipes drawn in it report SystemName "CHWS (CHWS)", SystemAbbreviation "CHWS", SystemFamily "Chilled Water".
- `LayerKey` is read-only over COM (get only in the type library). A COM-made system has an empty layer key, so its pipes land on the default layer `M-Pipe-Std`. Set `Layer` on each object instead (test: `M-CHWS` worked).

### Read a pipe (AecbDbPipe)
- Works: StartPoint, EndPoint, MidPoint, Length, CutLength, SizeName ("4 Inch Commercial Pipe"), CrossSectionSize ("4 1/2", the OD), NominalSize (4.0), SystemName, SystemAbbreviation, SystemFamily, PartDescription ("Commercial Pipe"), Name, Type ("Pipe"), SubType ("Undefined"), Elevation, TopElevation, BottomElevation, LockSize, InsulationThickness, Layer, Handle, Description.
- TopElevation 122.25 and BottomElevation 117.75 for a 4" pipe (4.5 OD) at Elevation 120. So Elevation is the centerline and Top/Bottom are centerline plus or minus OD/2. Use BottomElevation for a bottom-of-pipe value (inference: with insulation 0 in the test, whether insulation is included was not checked).
- `StyleName` raises an error.
- Fittings (AecbDbPipeFitting): PartDescription, SizeName, SystemName.

### Edit a pipe
- `Elevation` (put) moves the whole pipe. It then lost its connection to the elbow (ConnectedMembers None) until it was moved back. A COM move does not drag connected parts (inference from that result).
- `InsulationThickness` (put) works.
- `StartPoint` / `EndPoint` (put) work ONLY with a typed double array: `win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))`. A plain Python tuple fails with E_INVALIDARG.
- `Break(point)` works with the same VT_R8 array; it returns the new object's id and adds a pipe.
- `SystemName` (put) needs the full display string `"CHWS (CHWS)"` (name plus abbreviation in parentheses). `"CHWS"` alone fails (E_FAIL). `"Standard"` works as is.
- `Layer` (put) works like any AutoCAD entity.
- Not tested over COM: routing preference, nominal size, slope. Change those with the add command or the GUI (Modify Run, part 8).

### Connectivity
- `Connectors.Count` reports 3 on a straight pipe and on an elbow, but only Item(0) and Item(1) are valid; Item(2) raises. Loop to Count-1 inside try, or stop at the first error.
- Connector: Location, Direction (unit vector), ConnectionType, WidthorDiameter (4.0), ConnectedMembers (a tuple of the connected objects, or None when open).
- ConnectionType read "Undefined_Connection_Type" on the glued PVC pipe connectors, even where connected to the elbow. Pipe segments have no connection type of their own ([G:8837917F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8837917F-72AD-4718-B51C-0ADF5072994A)).
- `AecbDatabase.Graphs` (after Init) returns one graph per connected network; `graph.Count` and `graph.Item(k)` list its members (pipes and fittings). `graph.Iterator` is not reachable by name over IDispatch ("Unknown name").
- After the probe moved the pipe back, edited endpoints and broke a pipe, Graphs.Count was 1 with 4 members (3 pipes, 1 elbow): the network stayed one piece.

### Property sets
- `AecScheduleApplication.PropertySetDefs(doc.Database)` returned 5 definitions in the test drawing (PipeFittingElbowStyles, PipeStyles, SpaceEngineeringObjects, ThermalProperties, ZoneEngineeringObjects). `PropertySets(entity)` returned 0 sets on a new pipe.

### Found in the type libraries, NOT tested
`AecX.AecbGuiSize.8.9` (GetSizeListFromRoutingPreference, SizeExistsInRoutingPreference, GetBendAngles), `AecX.AecbGuiModify.8.9` (Modify/Modify2/Modify3 resize objects by ObjectIds, GetElbowList, GetCutLengths), `AecX.AecbPartQuery.8.9` (catalog query by Domain/Type/SubType/parameters), `AecX.AecbDuctInstantSizing.8.9`. Internal UI helpers; test on a scratch copy first. (inference) SizeExistsInRoutingPreference could check a size before it is sent to the SI prompt.

## 2b. What stops an unattended pipe run
Each of these waits for a person. Avoid them or answer them.
- Choose a Part dialog: part, angle or size not in the routing preference; different joint types on add ([G:7A80C9F6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7A80C9F6-94DB-4510-9ADB-BA29AC4FE18B)). Wrong profile or catalog mix makes it appear on every routing action ([KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)).
- Multiple Parts Found dialog: more than one size of a fitting fits ([G:0D3CACEE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D3CACEE-1923-4486-8FF1-B9F4FC16A30B)).
- Part Size Not Found dialog: a size that does not meet the catalog criteria ([G:4AC09C1B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AC09C1B-BC44-45F9-A419-4E02957B2B82); documented under duct, page says duct, conduit and others).
- "No Part Found" warning ([KB:000290750](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-The-current-catalog-contains-no-parts-which-could-be-automatically-inserted-in-this-situation-in-AutoCAD-MEP.html)).
- Routing solution prompt (n, p, a, number then Accept) when connecting at another elevation, slope or off-line ([G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926), [G:0AC20AE4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC20AE4-5F17-403D-A5B4-A3A4ACC7F11D)).
- Options > MEP Layout Rules set to "Prompt for user input" or "Prompt when Non-Standard Parts are Needed" ([G:C5BB7DCB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C5BB7DCB-9254-4A4E-B376-9242B576A7B9), [G:258A9D37](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-258A9D37-933F-4F36-B3EB-C1C17F86A730)).
- The preFerences option, Style Manager editors and Fitting Settings (dialogs).
- Import/Export - Duplicate Names Found dialog when pasting system definitions ([G:76C3538A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-76C3538A-BF9B-4499-B28F-05B5B3EB0869)).
- "Drawing Recovery" dialog at launch after a killed session [VERIFIED].
- Prevention (inference): use the US Imperial profile with US Imperial catalogs; keep routing preferences complete for every size and fitting the job needs; set the Layout Rules to non-prompting choices; draw connections at matching elevations; keep a dialog watcher running and log every prompt (LOGFILEMODE 1).

## 3. Before drawing: profile, catalogs, routing preferences

### Profile and catalogs must match the units
- Start MEP with the profile that matches the drawing units. [KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html): "US Imperial" = inches and feet; "US Metric" (called "soft" metric) = decimal feet; "Global" = true metric. [KB:000482051](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-created-via-the-Add-grip-are-using-wrong-size-and-type-of-pipe-in-AutoCAD-MEP.html) words it: US Imperial = feet and inches; US Metric = decimal feet and inches or US metric; Global = UK metric.
- Using a catalog that does not match the units creates placeholder parts ([KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)).
- Mismatch symptoms: Choose a Part on every routing action ([KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)); "No Part Found" ([KB:000290750](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-The-current-catalog-contains-no-parts-which-could-be-automatically-inserted-in-this-situation-in-AutoCAD-MEP.html)); the Add grip makes a pipe of another type or size ([KB:000482051](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-created-via-the-Add-grip-are-using-wrong-size-and-type-of-pipe-in-AutoCAD-MEP.html)); odd sizes such as .5906 instead of 3/4" ([KB:000262829](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Odd-pipe-sizes-are-displaying-when-trying-to-run-pipes-in-AutoCAD-MEP.html); .5906 in = 15 mm, inference).
- Fix [GUI]: make the matching profile current on the Profiles tab of OPTIONS, start MEP from the shortcut for that profile, and point the DWG file association at it if drawings are opened by double-click ([KB:000262829](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Odd-pipe-sizes-are-displaying-when-trying-to-run-pipes-in-AutoCAD-MEP.html), [KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)).
- Check the active profile with CPROFILE; a US Imperial setup reads "AutoCAD MEP (US Imperial)". [VERIFIED]
- To mix catalogs on purpose, add the Global and Metric pipe catalogs on the MEP Catalogs tab of OPTIONS while in the US Imperial profile ([KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)).

### Part catalogs (Options > MEP Catalogs tab) [GUI] ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0))
- Per domain, a list of catalog files with the APC (Autodesk Part Catalog) extension. Add, Remove, Browse (replace), Move Up, Move Down.
- List order = order shown in part selection. If two catalogs hold a part with the same ID or name, only the one higher in the list shows (examples given: adding MvParts, picking pipe fittings for a routing preference).
- Style-Based Content Paths (electrical devices, electrical panels, plumbing fittings, schematic symbols) and the Shared Content Path (part templates, primitives, config files needed by every content pack).
- Put custom parts in custom catalogs, never in the shipped ones, so they move cleanly at upgrade ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0), [G:64884E3A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-64884E3A-15B2-472E-B641-B72C425C8468)).
- A catalog part needs 3 files: DWG (geometry), BMP (preview), XML (sizes and properties). If one is missing the part is not offered ([G:19546C46](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19546C46-F201-4822-8963-F639FF96298C)).
- Folder conflict: the help puts the definition files under `\ProgramData\Autodesk\MEP <version>\enu\AEC Content` ([G:19546C46](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19546C46-F201-4822-8963-F639FF96298C)). [KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html) (written for MEP 2020) shows pipe catalogs in a MEPContent folder instead, with Global and USM pipe subfolders split by material. Check the 2027 folders on disk before scripting a path.
- Catalog layout ([G:7686F1CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7686F1CF-0A04-479A-87A7-B6E38978FAB4)): catalogs hold chapter folders, chapters hold part families, a family holds the sizes; picking a part = picking one size of a family. Layout depends on the profile.

### Pipe parts catalog ([G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7))
- Piping part types: Connector, Coupling, Cross, Elbow, Endcap, Offset wye (lateral), P-Trap, Takeoff, Tee, Transition, Wye, Undefined.
- US Imperial and US Metric: organized by material: Cast iron, Copper, Ductile iron, Plastic, Steel. Fittings inside are grouped by connection type (example: threaded).
- Global: organized by type and outside diameter: Commercial pipe, Ductile iron, copper tubing, Placeholder.
- Each pipe directory holds fittings for that pipe, classed by part type, connection type and pressure rating (example: class 3000 socket weld coupling).
- Pipe MvParts sit under the Mechanical chapter.
- File prefixes CSW = Carbon Steel Welded, CSP = Carbon Steel Pressed ([KB:000445584](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/What-does-CSW-CSP-on-pipe-parts-stand-for-in-AutoCAD-MEP.html)).

### Routing preferences: what they control
- A pipe part routing preference tells auto layout which pipe and fittings to insert; couplings go in at the proper pipe length and at break points ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)).
- It holds one or more size ranges by nominal diameter; each range names the pipe and fittings (elbows, tees, laterals, transitions) ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)).
- Auto layout always uses the CURRENT routing preference ([G:AFC86914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AFC86914-6495-41E7-9307-766EC241D3B5)).
- The sizes offered when drawing are only the sizes common to every pipe and fitting in the routing preference, grouped by size range. If a size is missing, pick another routing preference or change the parts in the size range ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697), [G:455FEA4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-455FEA4C-CD65-4AF6-A69B-2A394E0B1989), [G:0E26F347](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E26F347-F8B2-48CB-9048-4DFA1C6456E3)).
- Shipped pressure samples (US Imperial): Butt welded; Grooved and threaded; Slip on flanged - 150 lb. and threaded; Threaded 2000 lb. Gravity samples: cast iron soil pipe (bell and spigot, no hub), ductile iron mechanical joint, HDPE, sanitary DWV ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)). The full list found in the routing preference library drawing is in part 2. [VERIFIED]
- Multiple size ranges let one preference follow a spec such as the chilled-water example (threaded at 3" and below, 150 class weld neck flanged at 3 1/2" and up) ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)).
- The default Aecb Model template has a Placeholder routing preference ([G:D6FEC85D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D6FEC85D-75AC-4326-8CE9-73122BF53D60)).

### Edit routing preferences [GUI]
- Piping workspace > Manage tab > Style & Display panel > Style Manager drop-down > Routing Preference Definitions. Left pane node: "Pipe Part Routing Preferences" ([G:A5D422E3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A5D422E3-E7CD-477C-8A8B-82C700E3E88D)). Also reachable from STYLEMANAGER under Piping Objects; each size range is one block on the Preferences tab ([KB:000606939](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Perpendicular-branching-not-possible-for-some-pipes-in-AutoCAD-MEP.html)).
- [AUTO: names only] Page metadata lists commands SETACTIVERP and PIPEPREFDEF; no prompts or options are documented ([G:C581B422](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C581B422-8822-47B9-9547-E95F9B98D2FD)).
- New: right-click the node > New > type a name. Copy: right-click a preference > Copy; right-click the node > Paste; right-click the copy > Rename ([G:C581B422](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C581B422-8822-47B9-9547-E95F9B98D2FD)).
- Delete: right-click the preference > Purge > OK ([G:C651D795](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C651D795-F8EF-43FE-8FED-F914B1E37E6E)).
- General tab: Name; Description; Notes (Notes tab, for example revision history); Reference Docs tab > Add to link a document such as the piping spec ([G:A5D422E3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A5D422E3-E7CD-477C-8A8B-82C700E3E88D)).

### Size ranges (Preferences tab) ([G:CFDBE63D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFDBE63D-103A-41B7-A3A7-4B6FF9BEC2A0), [G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8))
- Part: pick a part for each part type. The list is every unfiltered catalog part of that type.
- *NONE* for a part type = you are asked to choose a part during layout every time that type is needed (a dialog; blocks a script).
- Picking a part that shares no sizes with the other parts in the range resets those parts to *NONE*. You are told which, and can cancel.
- Size Upper Limit: lists only sizes common to all parts in the range. Changing it moves the next range's lower limit. Need a bigger size than listed: choose other parts.
- Lower limit of Size Range 1 is set by the selected parts. Lower limit of later ranges = previous range's upper limit.
- Example: pipe 1/8" to 60" with an elbow 1" to 24" gives lower limit 1" and upper limit up to 24".
- If a range's value is set below the previous range's upper limit, the ranges swap order.
- Add range: appended at the end; lower limit = next catalog size above the previous upper limit; upper limit = largest catalog size. Remove: select the range name > Remove Size Range.
- Invalid ranges can be saved (for example an upper limit already used by another range). Size Upper Limit then shows *Invalid Size Range*, and those sizes disappear from the palette.
- Drawings from Autodesk Building Systems 2007 are revalidated on open in 2027; this can reset upper limits and set parts to *NONE*.

### Routing preference gotchas
- Perpendicular branch impossible, odd fittings or a branch not square: the routing preference's "Lateral" is an angled branch. In EVERY size range set Lateral to NONE or to a part that allows a perpendicular branch; a "45 deg Branch" will not work ([KB:000606939](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Perpendicular-branching-not-possible-for-some-pipes-in-AutoCAD-MEP.html)).
- Blank routing preferences, or ones set to *NONE*, are listed as a cause of lost connections ([KB:000293474](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipe-fittings-connection-problem-in-AutoCAD-MEP.html)). The two articles differ on NONE (inference: one slot vs the whole preference).
- Style Manager shows no values for the fittings: copy the drawing content into a new drawing through the Windows clipboard ([KB:000578897](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/No-values-for-pipe-or-duct-fittings-in-Routing-Preferences-with-in-Style-Manager-in-AutoCAD-MEP.html)).
- Adding a size to a catalog: the size must exist in every part the routing preference uses (part 8, [KB:000233324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Adding-a-new-pipe-size-to-a-pipe-catalog.html)).

### Apply or change a routing preference
- [AUTO start, palette] Styles Browser palette (command STYLESBROWSER, [G:21566B25](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-21566B25-BB2E-434B-B2BC-E557758C18C0)): Object Type > Piping Objects > Pipe Part Routing Preferences ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)).
- On a selected pipe [GUI]: Properties palette > Routing Preference button > Styles Browser > pick > Apply Style To Selection. Applying also imports it into the drawing ([G:65A24793](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-65A24793-DB0D-48C8-B6A3-FA5031805C4C)).
- Drawing Source: Content Library Drawings or Currently Open Drawings. Drawing File: All Drawings, Current Drawing, All Without Current Drawing, System Definitions, Manage Content Library ([G:21566B25](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-21566B25-BB2E-434B-B2BC-E557758C18C0)).
- On a connected run [GUI]: select a segment > Properties palette > Dimensions > Routing preference, then Nominal size, then Pipe tab > Modify panel > Modify Run ([G:0E26F347](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E26F347-F8B2-48CB-9048-4DFA1C6456E3)). Changing the preference changes connection types (flanged to grooved) or pipe type (commercial to iron pipe).
- New pipe from a script: answer `R` at the -AECBPIPEADD prompt [VERIFIED].

## 4. System definitions, pipe layout preferences, layout rules

### Pipe system definitions: what they do
- A pipe system definition carries display: pipe display by size (1-line or 2-line by size), layer key (sets layer, color, linetype), rise/drop display style and other display properties. It is normally tied to a system type such as chilled water or steam ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549)).
- Stored in the drawing. Each drawing can have its own; they can be shared between drawings ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549), [G:CA50AF07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA50AF07-B6A9-47AC-82C5-3080E3FCB903)).
- The default templates include chilled water, heating hot water, steam and others ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549)). The routing preference library drawing holds only "Standard" [VERIFIED]. More definitions: `System Definitions.dwg` in a subfolder of `\ProgramData\Autodesk\MEP <version>\enu\Styles` ([G:76C3538A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-76C3538A-BF9B-4499-B28F-05B5B3EB0869)).
- Rise and drop symbols are inserted per the rise/drop style of the run's system ([G:BD4D846C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BD4D846C-105D-4779-9095-8109FEAB0EA1)).

### Connecting different systems
- Pipe runs with different system definitions cannot connect unless the connecting run's system is changed. Fix: give both definitions the same system group; the runs then connect and each keeps its own system (example: Heating Hot Water - Supply and Heating Hot Water - Recirculation) ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549)).
- A connection is valid only if the parts are in the same system group AND the connector style rules are met ([G:01DC838A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-01DC838A-0C23-4DD8-9683-88A85A5CC2EF)). Pipe to pipe normally needs the same size and system ([G:16ADED4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16ADED4B-13A1-47F2-8F99-06C3FFDFC16F)).
- What happens on a mismatch is set by Options > MEP Layout Rules > Connection Test Mismatch (below).
- (inference) For CHWS/CHWR or HWS/HWR pairs that must join at a bypass or a coil, put both definitions in one system group.

### Create or copy a pipe system definition [GUI]
- Piping workspace > Manage tab > Style & Display panel > Style Manager drop-down > Piping System Definitions ([G:13267A31](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13267A31-5CA1-4F26-B41F-670E747D342E)).
- New: right-click "Pipe System Definitions" in the left pane > New > type a name > Enter. Copy: right-click a definition > Copy; right-click Pipe System Definitions > Paste; right-click the copy > Rename ([G:13267A31](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13267A31-5CA1-4F26-B41F-670E747D342E)).
- General tab: description, then properties shared by all disciplines: design rules, rise and drop style, display properties, attached notes and files; then the pipe-specific tabs ([G:13267A31](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13267A31-5CA1-4F26-B41F-670E747D342E), [G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370)).
- [AUTO: names only] Page metadata lists PIPESYSTEMDEF and PIPESYSTEMDEFEDIT; no prompts are documented ([G:13267A31](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13267A31-5CA1-4F26-B41F-670E747D342E)).
- Script route: `PipeSystemDefs.Add` over COM, but no layer key (part 2). [VERIFIED]
- Sanitary rule: a gray or black water system must have system type Waste (Design Rules tab), or Size Sanitary Pipe does not see it as sanitary and cannot size it ([G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370), [G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F)).

### Copy system definitions between drawings [GUI] ([G:76C3538A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-76C3538A-BF9B-4499-B28F-05B5B3EB0869))
- Manage tab > Style & Display panel > Style Manager. Open drawings show in the tree; File > Open Drawing for others.
- Expand System Definitions under the source drawing; right-click a definition > Copy (or right-click System Definitions to copy all); right-click the destination drawing > Paste.
- A duplicate name opens Import/Export - Duplicate Names Found: Leave Existing, Overwrite Existing, or Rename to Unique (a number is appended). Click OK, or Apply to keep working. Blocks a script.

### Other system tasks
- Apply a system from a content library drawing: select the object > Properties palette > Advanced > System > System > Styles Browser, Drawing Source = Content Library Drawings, pick Drawing File, pick a system ([G:B39DFFA3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B39DFFA3-DEB5-4EB7-85AF-E6DA86D6EA19)).
- Attach notes or files to a system [GUI]: Style Manager drop-down > Piping System Definitions > select system > General tab > Notes > Notes tab or Reference Docs tab (Add, Edit, Delete; double-click opens the file) ([G:97AE94C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97AE94C9-DDB2-48CD-ABD1-51889E29261E)).
- Change the system of a pipe: select a segment > Properties palette > System. For a connected run: Pipe tab > Modify panel > Modify Run > System ([G:ACA46DC5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ACA46DC5-126F-49C2-8F99-A1508AB5D432)). COM: put SystemName "CHWS (CHWS)" [VERIFIED].
- Changing the system on one connection can change the system of the connected parts, depending on the connector style rules ([G:6B598B33](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6B598B33-839B-4C03-8A02-FA52FECE3B68)).
- MvPart connectors start with no system. The first run connected passes its system to the connector. Changing the system on a connected connector changes the run's system. Pre-set it so a run started from the MvPart's Add grip already has the system. [GUI] Select MvPart > Equipment tab > Modify panel > Equipment Properties > Multi-view Part Properties > Systems tab > System column cell ([G:025A0623](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-025A0623-315D-4B98-96C2-EDC869D44BB2)).
- Display of a system (1-line, 2-line, graphical 1-line by size) is set on the Single Line Graphics tab (part 10).

### Pipe Layout Preferences dialog [GUI]
- Open: Piping workspace > Manage tab > Preferences panel > Piping; or Properties palette > Routing > Preferences button ([G:8751D01F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8751D01F-91CD-4C13-877B-66CA2A53DC55)). Stored with the drawing; can be shared between drawings ([G:74F8C98B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-74F8C98B-0142-43B9-AC46-6B4F7890AABB)).
- It also sets the branch connection used when a new pipe starts or ends along an existing pipe: a tee or a takeoff is inserted "depending on the connection specified" in the layout preferences ([G:455FEA4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-455FEA4C-CD65-4AF6-A69B-2A394E0B1989), [G:6D79ED53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6D79ED53-1ED2-4AB0-AA13-E87A86F56538)).

General tab ([G:58EFC45B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58EFC45B-7BF0-4378-BD88-4B76DF549576)):
- Slope format (stored with the drawing; changes how the palette Slope reads):
  - Angle: degrees (example 2 degrees).
  - Percentage: 100% = 45 degrees.
  - Percentage: 100% = 90 degrees.
  - Rise/Run: a fraction (example 1/48 or 1/100); palette shows a fraction.
  - Rise/Run with Constant Rise: decimal; palette shows the Run part. Page example: "20, where run is 1" (reads oddly; with a constant rise of 1 the run would be 20, inference).
  - Rise/Run with Constant Run: decimal; palette shows the Rise part.
  - Rise/Run with Fractional Rise, Constant Run: a fraction, example 1/4 = 1/4" rise per 12" run.
  - The palette lists the same 7 as: Angle; Percentage (100%=45); Percentage (100%=90); Rise value/Run value; Run value, Rise= constant value; Rise value, Run=constant value; Fractional Rise value, Run= constant value ([G:E85C2D51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E85C2D51-3AFD-4F3D-9567-ACC9A7D2FCF5)).
- Rise and Run units: enabled only after a slope format is picked; Imperial = feet or inches (from the profile and Drawing Setup).
- Constant value: Rise editable only with Constant Rise; Run editable only with Constant Run.
- Ratio divider: slash (/) or colon (:).
- Elevation: "Automatically create riser at new elevation", or "Override slope based on elevation and placement point" (slope computed from current elevation and cursor). Override slope is grayed out while auto riser is checked.
- Labels: label style (label preferences are stored in the registry); By quantity (labels per straight segment) or By distance (interval; a segment shorter than the interval gets none).
- Flow arrows: style; By quantity or By distance, same rule.
- Elbow reducer preference: Use Reducing Elbow (one fitting when direction and size change together); Use Reducing Elbow if needed (no reducing elbow when the size does not change; the page says "duct size"); Use Straight Elbow and Reducer (elbow plus separate reducer).

Connection Assignments tab ([G:441C2FD4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-441C2FD4-41C8-463C-BF7F-818D4F052E95), [G:69B70DE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-69B70DE1-7A26-4D04-B910-8D850B1D40A3)):
- Maps each female connection type (left column) to the male type it accepts: under Male Connection click the type, open the list, pick.
- A connection type set to Undefined that attaches to a female connector displays as male and follows this mapping.
- Must follow the connector behavior rules based on CEL; assignments come from the catalog content. Connection types are assigned in Content Builder's Connector Properties dialog ([G:1EBC5DC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1EBC5DC2-D2AE-4D5F-97A2-D8A84888577A)).

### Layout rules (Options > MEP Layout Rules tab) [GUI]
Connection Test Mismatch ([G:C5BB7DCB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C5BB7DCB-9254-4A4E-B376-9242B576A7B9)):
- Do not make connection: the part is drawn to the picked point but not connected.
- Prompt for user input: asks before connecting dissimilar systems; accept = change the new part's system to match (valid) or ignore the system (invalid connection).
- Automatically match and make connection: always connects and changes the new part's system to match.
- The help recommends Prompt for user input until you know the toolset ([G:01DC838A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-01DC838A-0C23-4DD8-9683-88A85A5CC2EF)). For unattended runs avoid it (inference).

Part Selection ([G:258A9D37](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-258A9D37-933F-4F36-B3EB-C1C17F86A730), [G:F36E8B05](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F36E8B05-BFBC-4096-A969-934EAC8A29F1)):
- Use Catalog Parts Only: catalog sizes only.
- Prompt when Non-Standard Parts are Needed: asks before a custom size; accept = custom part made; decline = the last segment drawn is removed.
- Use Non-Standard Parts: custom sizes always allowed (example: an elbow at an angle not in the catalog is made automatically).
- Custom parts made this way live only in the current drawing, not in a catalog.

### Initialization vs layout preferences ([G:032119B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-032119B1-17CD-47C2-9624-62CB0436D177), [G:A9A4E2DB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A9A4E2DB-A1BF-463A-9FBE-1CDE5706126B), [G:984B1AC0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-984B1AC0-F135-44D5-8B56-9F4913E4A1E0))
- Initialization preferences: set at project start, rarely changed (crossing settings, connection rules, catalog and content locations), reached from Options.
- Layout preferences: per system, changed as needed (default parts, connections). Both can be saved in a template shared by the team.
- Default parts: each system can have its own; if a needed part has no default, you are prompted to pick one ([G:35056FB5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-35056FB5-E47C-4697-A440-C05C72FFE251)).

## 5. Adding pipe

### Ways to start ([G:24D620D6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24D620D6-32CA-4378-8B02-C7F2E1583DF7), [G:78FBD0E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78FBD0E8-2CB4-40CA-80D0-92B7676887C4))
- [AUTO] PIPEADD at the command line (palette-driven), or `_-AECBPIPEADD` for full command-line control [VERIFIED].
- [GUI] Home tab > Build panel > Pipe drop-down > Pipe. Home tab > Build panel > Pipe Fitting. Home tab > Build panel > Equipment drop-down.
- [GUI] Styles Browser gallery: Home > Tools > Styles Browser > Object Type > Piping Objects > Pipe, Pipe Flex.
- [GUI] Tool palette: Home tab > Build panel > Tools drop-down > Tools. The Piping palette has a Pressure Pipe tab (non-sloped designs) and a Gravity Pipe tab (sloped designs) ([G:78FBD0E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78FBD0E8-2CB4-40CA-80D0-92B7676887C4)). Chilled water and hydronic are pressure piping (inference).
- [GUI] Add grips on pipe objects; or select a pipe, Pipe tab / Pipe Flex tab / Pipe Fitting tab > General panel > Add Selected; or select an MvPart > Equipment tab > General panel > Add Selected.
- Best practice: set routing preferences and system definitions before drawing ([G:6854A352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6854A352-8B0C-4DBE-94B5-F644B91AFB04)).
- Design workflow in the help ([G:3F1F7003](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3F1F7003-4B05-4D96-BD57-0035AA20C770)): 1 set up the project and pipe standards, xref the architectural plan; 2 preliminary 1-line design; 3 pick pipes and fittings (spec); 4 system definitions, size ranges, display; 5 place boilers, chillers, pumps, heat exchangers; 6 connect equipment and lay out runs; 7 modify; 8 construction documents.

### Add-mode Properties palette (PIPEADD) with defaults ([G:E85C2D51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E85C2D51-3AFD-4F3D-9567-ACC9A7D2FCF5), [G:0050A936](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0050A936-D029-46C9-9E8E-39E158EDC765))
`*` = sloped-layout property, `**` = flex pipe only.
Basic, General:
- Description: optional. System: Standard (default); the page says the choices are derived from the catalog.
Basic, Dimensions:
- Routing preference: Standard (default; choices derived from the catalog per the page). Nominal size: 2" the first time, then the last used. Size lock: Unlocked (default) / Locked. Specify cut length: No (default); Yes shows Cut length.
- Tip: lock the nominal size to prevent accidental change ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697)).
Basic, Placement:
- Elevation: 0 (default); Z above or below the XY plane of the current UCS.
- Elevation lock: Unlocked (default); stops snapping to objects at another elevation.
- Start elevation: 0 (default); elevation of connector 1, same as Elevation.
Basic, Justification:
- Justify: Top Left, Top Center, Top Right, Center (default), Center Left, Center Right, Bottom Left, Bottom Center, Bottom Right. Horizontal offset 0, Vertical offset 0.
Basic, Routing:
- `*`Slope format: the 7 formats in part 4; the Preferences button edits it.
- `*`Slope: 0 (default). Changing slope while adding to a run adds a fitting to adjust the slope.
- `*`Bend method: Elbow (default) or Offset. `*`Bend method lock (shows only for Offset): if Unlocked, the method reverts to Elbow after one offset is inserted.
- `*`Bend angle and `*`Bend angle lock: angles come from the catalog content.
- `*`Branch angle (for example 45 or 90) and `*`Branch angle lock: choices from the catalog; with a lateral picked, only that lateral's angles show.
- `**`Segment (Line, Arc, Spline), `**`Radius factor (with Line).
Advanced (collapsed by default):
- Connection details button. Insulation thickness: 0 (default).
- `**`Graphics (1-Line, 2-Line): Circle, Curve, Oval, Single line, Single line 2, Vertical, Vertical 2. `**`Pitch.
- Routing options: `*`Use fitting tolerance: Yes (default) / No. `*`Joint direction: Male into female (default) / Female out to male. `*`Branch fitting: Tee or Wye (Lateral) (default), Tee only, Takeoff only, Wye (Lateral) only, Wye (Lateral) or Tee (a two-fitting choice tries the first, then the second). Fitting settings button. `*`Preferences button.
- Labels Style and Flow arrows Style: *NONE* (default), By Quantity, By Distance.
Pressure piping tip: for faster response and more directed auto-layout solutions set Use fitting tolerance = No, set the Bend angle, and set the preferred Branch fitting ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697), [G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
Doc wording conflict: the sloped-piping task says to pick the routing preference and branch angle "under General" ([G:68D9D62C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68D9D62C-1FC7-4960-B636-79C8CA5C9F9B)); the property tables list Routing preference under Dimensions and Branch angle under Routing ([G:E85C2D51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E85C2D51-3AFD-4F3D-9567-ACC9A7D2FCF5)).

### Draw a run ([G:BD4D846C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BD4D846C-105D-4779-9095-8109FEAB0EA1))
- Pick a start point, keep picking. Fittings are inserted from the routing preference and the pipe layout preferences.
- If the geometry needs a part the preference lacks, or a size or angle it lacks, you are prompted to substitute (part 6).
- Layout aids: compass, object snaps, AutoCAD MEP snaps, Ortho, tracking lines.
- `n` (New run) at the command line starts a new run; set its properties on the palette.
- Rise and drop symbols are inserted from the rise/drop style of the run's system.
- Pipe that stops after every direction change, with no message, so you must click the "+" grip to go on: corrupted settings; reset AutoCAD MEP to defaults ([KB:000578805](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-draw-pipe-continuously-in-AutoCAD-MEP.html)). (inference) A scripted run that ends after one segment for no reason may be this.

### Compass ([G:9F8199F2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F8199F2-616E-4458-9CAA-D77BC4396DFE), [G:8E5472C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8E5472C8-F7B9-45EB-8C33-F390E42CE475), [KB:000625708](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Polar-tracker-is-set-to-22-5-45-but-pipes-keep-routing-at-angles-15-30-45-in-AutoCAD-MEP.html))
- [AUTO] Commands: AECBCOMPASS, AECBCOMPASSBAR (prompts not documented). [GUI] View tab > MEP View panel > Compass: Compass Diameter, color, Enable Snap + snap increment, Enable Tick Marks + tick increment.
- Pipes routing at 15, 30, 45 degrees while polar tracking is set to 22.5/45: View tab > MEP View > uncheck Enable Compass ([KB:000625708](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Polar-tracker-is-set-to-22-5-45-but-pipes-keep-routing-at-angles-15-30-45-in-AutoCAD-MEP.html); the article heading says enable, its numbered step says uncheck).

### Vertical segments and risers
- [GUI] Start the run, click the point where the vertical starts; its elevation is the start elevation. Set the endpoint elevation on Properties palette > Placement, then keep picking ([G:9F4198F0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F4198F0-531B-45A8-8616-94BB09A3D2D2)).
- A vertical segment is added by default when elevation changes (duct page [G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95)). For pipe, the layout preference "Automatically create riser at new elevation" controls this ([G:58EFC45B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58EFC45B-7BF0-4378-BD88-4B76DF549576)).
- Command line: `S` then 90 routes vertically ([KB:000550597](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Vertical-routing-in-AutoCAD-MEP.html)). The -AECBPIPEADD prompt also has an Elevation option [VERIFIED prompt; behavior not tested].
- New vertical segments stay vertical to the current UCS ([G:D69BAA6F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D69BAA6F-F571-47B7-AB6E-7A39EF894F87)).
- Joining a horizontal pipe to a vertical one: hover the vertical until a pipe curve connector shows, click it; use a side or isometric view if it fails ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C)).

### Elevation lock ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C), [G:5BE180D2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5BE180D2-1261-4ECA-AC43-01665B174D44))
- Locks the elevation while drawing a HORIZONTAL run, so it will not snap to an object at another elevation.
- By default the lock is off whenever PIPEADD starts, and it resets to Unlocked when the command ends ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C)). A script that needs it must set it inside each add session (inference).
- Cannot be locked on a sloped segment. While locked you cannot connect to an object at a different elevation. Lock part of a run, unlock for the rest.
- Riser technique: in top view only the riser's pipe end connector shows, and picking it gives routing solutions at the wrong elevation. Lock the elevation first, then pick the pipe snap on the riser; the joint lands at the run's elevation. Use two viewports (top + isometric) to preview.

### Justification and offsets
- Justification = orientation of the pipe relative to the draw direction (connector 1 to connector 2). Default is centerline, no offsets: the centerline lands on the picked points ([G:13477BFA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13477BFA-EFC2-4990-B708-1FDE63C839F0)).
- Starting from a fitting connected to a segment copies that segment's justification; otherwise the last used justification applies. MIRROR across a wall flips Left/Right automatically ([G:13477BFA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13477BFA-EFC2-4990-B708-1FDE63C839F0)).
- Three setups ([G:0B6F7CA3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0B6F7CA3-918B-4C1F-9D33-878C12DD9F7B)): centerline on the points (Center, enter offsets); one side on the points (one of the 9 Justify values); uniform offset (enter horizontal and vertical offsets).
- The Elevation property is the object's center no matter the justification ([KB:000568090](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-of-MEP-objects-displays-wrong-value-in-AutoCAD-MEP.html), written for MEP 2025). Consistent with the test: Elevation 120.0 with center justification at z 120 [VERIFIED].
- Offset from existing geometry (walls, lines, blocks, MEP objects, xrefs): Placement > Justification > Horizontal offset (same elevation, X or Y) or Vertical offset (Z); positive = positive direction; set back to 0 to stop offsetting ([G:D53E065C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D53E065C-DAD3-4068-8422-C20E28727B9B)).

### Parallel run by offsets ([G:91F68772](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-91F68772-247F-4D9D-A710-1B81E43593D4))
1. MEP pipe snaps ON. Object Snap and Object Snap Tracking OFF (status bar).
2. Add pipe; set Justification horizontal or vertical offset (positive = +X/+Y or up).
3. Pick the pipe end connector at the start of the existing run, then a point at each end of each segment.
4. At elbows pick only the pipe curve connector (it sits at the logical intersection of the fitting centerlines); this holds the offset along the run.
- Tip: show the existing run in 1-line for fewer and exact picks. Plot warning: runs too close plot as one line at small scales.
- For several pipes at once use PARALLELROUTING (part 6).

### Cut length ([G:369D2D94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-369D2D94-DBD9-4ABF-BC94-1CBA5CD22678), [G:E85C2D51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E85C2D51-3AFD-4F3D-9567-ACC9A7D2FCF5))
- Properties palette > Dimensions > Specify cut length = Yes, then Cut length. Example: 10 ft stock breaks straight runs into 10 ft pieces as drawn, adds joints (couplings) at each break, and the pieces stay one connected system.
- Cut length applies to ALL pipe system definitions at once (chilled water, steam, gas, any). For different stock lengths per system, change it before drawing each system.
- Break or merge after drawing: PIPELENGTH (part 8).

## 6. Connecting pipe, fittings and equipment

### MEP pipe snaps ([G:C14F32A4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C14F32A4-9493-42A1-908B-7520C27394A8), [G:16ADED4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16ADED4B-13A1-47F2-8F99-06C3FFDFC16F))
- Pipe end connector: connect a pipe, fitting or MvPart to the END of a segment.
- Pipe curve connector: connect at any point ALONG a segment. 1-line pipe: shows over the centerline; 2-line pipe: shows over the contour lines ([G:96EEA3F0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-96EEA3F0-15BD-4EAE-B666-3BBE21244435)).
- MEP snaps find connectors the way object snaps find a midpoint. A new object takes the system, elevation, shape and size of the object it connects to ([G:16ADED4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16ADED4B-13A1-47F2-8F99-06C3FFDFC16F)).
- (inference, not tested) Typed coordinates with `_non` bypass snaps. Whether a typed point that lands exactly on an existing open pipe end connects automatically was not tested. Check `ConnectedMembers` after drawing (part 2).

### Add grips [GUI] ([G:455FEA4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-455FEA4C-CD65-4AF6-A69B-2A394E0B1989), [G:928EC9ED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-928EC9ED-6C78-4602-AEEC-25565CB284E4))
- Segment end: Add grip at that end starts a run from it.
- Segment midpoint: Add grip there inserts a tee or takeoff, per the connection in the pipe layout preferences.
- MvPart: Add grip on the MvPart connection. Under Dimensions set a system and a routing preference; the software remembers both. Routing preference and slope follow the connected object.
- Fitting (elbow, tee): click the Add grip pointing where the run should go. The part and male-to-female orientation in the routing preference are used if possible; otherwise Choose a Part asks for a part at that angle. An Add grip on an elbow turns the elbow into a tee automatically; existing branches stay connected ([G:928EC9ED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-928EC9ED-6C78-4602-AEEC-25565CB284E4)).
- Add a joint to a run: hold Ctrl while clicking the Add grip, then click to add pipe. With Use fitting tolerance = Yes a coupling is added, only within the allowed fitting tolerance angle; with No an elbow is added.
- Starting from a segment or fitting, the new run inherits its preferences. Changing the nominal size before the first point inserts a transition automatically after the first point.
- Add grip makes the wrong pipe type or size (example: butt welded steel source gave cast iron in a slightly different size): profile/catalog mismatch, or a missing or incomplete routing preference. Fix the profile; in STYLEMANAGER check every definition in the routing preference's Preferences tab ([KB:000482051](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-created-via-the-Add-grip-are-using-wrong-size-and-type-of-pipe-in-AutoCAD-MEP.html)).

### Connect to existing pipe ([G:6D79ED53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6D79ED53-1ED2-4AB0-AA13-E87A86F56538))
- Start at a pipe end: hover the existing end until the pipe end connector snap shows, click. Routing preference, size and system match the existing pipe. A different nominal size inserts a transition.
- Start along a pipe: hover the segment for the pipe curve connector, click. A takeoff or tee is inserted per the connection type in the pipe layout preferences.
- End on existing pipe: click a pipe curve connector or pipe end connector; a takeoff or tee is inserted per the layout preferences.
- Pipes at different elevations: one or more routing solutions are offered to preview and apply.

### Takeoffs ([G:96EEA3F0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-96EEA3F0-15BD-4EAE-B666-3BBE21244435))
- A takeoff sits perpendicular to the pipe centerline and can rotate to any angle around the pipe.
- Easiest: connect a new pipe to a pipe curve connector on an existing segment; if Takeoff is the connection type in the layout preferences, a takeoff is inserted automatically. Branch fitting = Takeoff only does the same during layout ([G:0050A936](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0050A936-D029-46C9-9E8E-39E158EDC765)).
- Manual [GUI]: Home tab > Build panel > Tools drop-down > Tools; pick a fitting, tap or takeoff tool; Properties palette > General > part image > Select a Part (parts by material in US Imperial) > Display/Hide additional parameters, Filter by Dimensions > size > OK; click the pipe curve connector.
- [AUTO] After placing: `sl` (slide) moves the insertion point; then type an angle (or use the compass) to rotate it around the pipe. Rotate grips also work.
- Takeoffs are anchored fittings; the Properties palette shows an Anchor button and worksheet only when the selected fitting uses anchors ([G:8A80B779](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8A80B779-5F19-425B-A736-BB03B3F2924A)).

### Routing solutions and auto layout
- Generated when you connect objects at different elevations or slopes, or with misaligned centerlines ([G:0AC20AE4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC20AE4-5F17-403D-A5B4-A3A4ACC7F11D)).
- [AUTO] At the prompt: `n` Next, `p` Previous (+ Enter); `a` + Enter accepts the previewed solution; or enter a solution number, then Accept. The run updates ([G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926)).
- If the two objects differ in size or routing preference you may first be asked to choose a part ([G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926)).
- Tip: preview with two viewports (plan + isometric); 3D Orbit works while previewing. If no solution fits, take the closest and fix it with grips ([G:0AC20AE4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC20AE4-5F17-403D-A5B4-A3A4ACC7F11D)).
- Example from the help: pipe to a chiller at another elevation and not in line: select the last segment, click the Add grip on its open end, move to the chiller connection, click its pipe end connector; two solutions result, built from the current routing preference, with angles from the allowed angles of the selected elbow ([G:0AC20AE4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC20AE4-5F17-403D-A5B4-A3A4ACC7F11D)).
- Auto layout: picks are turned into pipes, fittings and transitions from the CURRENT routing preference. Angles stored in the elbow content set the available angles ([G:AFC86914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AFC86914-6495-41E7-9307-766EC241D3B5)).
- Constrained layout (pipe to pipe, sloped or not): horizontal routing between objects at different elevations is supported; new vertical segments stay vertical to the current UCS; the actual slope of the current segment is shown ([G:D69BAA6F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D69BAA6F-F571-47B7-AB6E-7A39EF894F87)).

### Fitting override during layout ([G:A18DE50D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A18DE50D-2333-4473-BCAE-A997EE0278F6))
- [GUI] Properties palette > Advanced > Routing Options > Fitting Settings button > Fitting Settings dialog (current description and size range from the catalog; "- -" = no value) > pick fitting type > pick part > draw. The override part is inserted automatically.
- Lasts only until the Pipe Add command ends. The next PipeAdd uses the routing preference default again. A script must re-apply it in each add session (inference).
- Use case in the help: a threaded takeoff instead of the default butt-welded takeoff.

### Part-choice dialogs [GUI] (block a script)
Choose a Part, pipe domain ([G:7A80C9F6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7A80C9F6-94DB-4510-9ADB-BA29AC4FE18B)):
- Part not in the current routing preference: on add yes, on modify yes.
- Preference has the part but not the angle: yes, yes.
- Size not in the preference: on add yes (asks for a reducer); on modify yes.
- Extra part needed and the given reducer does not fit the size: on add no; on modify yes (a reducer is added automatically).
- Different joint types (example butt welded and fusion) not in the preference: on add yes; on modify no.
- On modify it zooms to the part that needs action, then restores the view. The last choice per domain is kept; it can be made the default.
- The substitution applies only to that location. While Add is still active the same case asks again.
- If the wanted part or connection type is not offered, Cancel and add the fitting by hand.
- Different connection types or misaligned centerlines can ask several times; the picks feed one or more routing solutions.
- [KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html) describes a message that a part cannot be used because of size or angle limits. If it appears on every routing action, the profile or catalogs are wrong (part 3).
Multiple Parts Found ([G:0D3CACEE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D3CACEE-1923-4486-8FF1-B9F4FC16A30B)): more than one size of the fitting fits; pick one. On modify it zooms; clear "Zoom to the object" to stop that (remembered).
Part Size Not Found ([G:4AC09C1B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AC09C1B-BC44-45F9-A419-4E02957B2B82), documented under duct; applies to duct, conduit and others): Use selected part size from catalog / Create custom sized part / Undo change.
No Part Found warning ([KB:000290750](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-The-current-catalog-contains-no-parts-which-could-be-automatically-inserted-in-this-situation-in-AutoCAD-MEP.html)): no part in the routing preference can be inserted automatically. Causes: profile and catalogs do not match the drawing units, sizes outside the catalog range from wrong scaling or units, corrupt settings. Fix the profile/catalog match, scale model objects if switching units, or reset MEP to defaults.
Prevention: put every part, angle, size range and connection type the job needs into the routing preference before drawing ([G:CFDBE63D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFDBE63D-103A-41B7-A3A7-4B6FF9BEC2A0); inference that this avoids the dialogs).

### Parallel routing (PARALLELROUTING) [AUTO] ([G:76A66EAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-76A66EAD-90BE-4498-9852-4EEB2A2A429A), [G:D66E353F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D66E353F-06BB-4764-A4E7-D975410B01DD), [G:B37254A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B37254A9-CA34-4B8C-860B-20C5DF270BEC))
- Also Home tab > Build panel > Pipe drop-down > Parallel Pipes. Meant for hot and cold piping, radiant heating pipework, conduit; the software computes the turns and avoids conflicts.
- Steps: draw 2 or more starting parallel segments, each with its routing preference and system; PARALLELROUTING; pick the baseline pipe (routing starts at its open end; if both ends are open, pick near the start end); pick the parallel pipes, Enter; pick points. Segments are added to all pipes at a constant spacing where possible.
- `b` = make another pipe the baseline. To end at a valve: click the Pipe End Connector on the valve, `a` to accept the displayed solution; another pipe becomes baseline. With one pipe left it behaves like PIPEADD. End by connecting the last pipe or pressing Enter.
- Connect two parallel runs: PARALLELROUTING, baseline, parallel pipes, Enter, pick the other run at its END CONNECTOR, Next/Previous through bend options, Accept ([G:D66E353F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D66E353F-06BB-4764-A4E7-D975410B01DD)).
- While active: Justification and Compass apply to the baseline only; Size and Insulation Thickness apply to all; a new Elevation moves all pipes (spacing kept unless it conflicts); System, Routing Preferences, Fitting Settings and Layout Method cannot be changed.
- Limits: no sloped parallel pipes (slope properties disabled). Choose a Part appears if a routing preference lacks a needed part.

## 7. Connectors, joints, cut length, fitting tolerance, slope

### Connectors ([G:8837917F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8837917F-72AD-4718-B51C-0ADF5072994A), [G:16ADED4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16ADED4B-13A1-47F2-8F99-06C3FFDFC16F), [G:3709FC34](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3709FC34-7650-42CE-BCBD-5AFA4C534181))
- Connectors sit at each end of pipe segments and fittings and make segments, fittings and pipe MvParts one intelligent system.
- Exception: grooved couplings have their connectors INSIDE the coupling at the CEL depth (pipe ends insert into it), so cut length with grooved joints is reported differently.
- Fittings and MvPart connectors carry a connection type (base-mounted pump = flange; threaded coupling = threaded). An MvPart connector behaves like a fitting connector.
- Pipe SEGMENTS have no connection type; each end inherits it from the connected fitting (a socket weld coupling on one end makes that end socket weld). Over COM a segment connector read "Undefined_Connection_Type" even when connected [VERIFIED].
- Connector styles hold the rules: which properties are compared and whether the connection is allowed. One object can have connectors in several domains (an AHU with duct, gas pipe and power connectors) ([G:16ADED4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16ADED4B-13A1-47F2-8F99-06C3FFDFC16F)).

### Connection types and what each joint adds ([G:1EBC5DC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1EBC5DC2-D2AE-4D5F-97A2-D8A84888577A))
- Flanged (all types): fitting to pipe = the fitting has its own flange and a separate flange is added to the pipe; pipe to pipe = a separate flange on each pipe end; fitting to fitting = fittings with built-in flanges join directly.
- Threaded, Socket weld, Glued, Brazed: fitting to pipe = the pipe's male end goes into the female fitting; pipe to pipe = a female coupling is inserted; fitting to fitting = direct.
- Grooved: pipe and fittings are grooved ends; a coupling is added for fitting-pipe, pipe-pipe and fitting-fitting.
- Butt weld: nothing added; parts connect directly.
- Same Connection (piping domain): on a pipe object attached to a hub, connector 1 inherits the connection type of connector 2 of that hub.
- Connection types are assigned in Content Builder (Connector Properties dialog) and then show on the Connection Assignments tab of Pipe Layout Preferences.

### Joints ([G:D9B8A7EA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D9B8A7EA-D140-4F65-BCA9-1F9F231708F7), [G:69B70DE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-69B70DE1-7A26-4D04-B910-8D850B1D40A3))
- Joints (flanges, couplings) are separate objects. A flanged segment = 3 objects: 1 pipe + 2 flanges. They can be counted and scheduled ([G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7)).
- Joints are added while drawing, per the Routing Options on the Pipe Properties palette. You can change a joint's connection type or move it along the run.
- In the catalog, joints are fittings in the couplings directory and the asymmetric connectors directory (example: socket weld flange, socket side to pipe, flange face to the neighbor).
- The number of joints depends on the connection type. Example: an undefined pipe, a grooved coupling with female connectors and an elbow with male undefined connectors: the pipe and elbow inherit the grooved type from the coupling ([G:69B70DE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-69B70DE1-7A26-4D04-B910-8D850B1D40A3)).

### Connector engagement length (CEL) and cut length ([G:287DD32A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-287DD32A-C717-48D9-8245-536B73021BAE), [G:40FA7E16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-40FA7E16-3EB6-42B0-8405-CAE981F8F4DC), [G:78F05619](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78F05619-64FA-4D21-B218-0FAD9CB438C6))
- Every catalog fitting has one or more CELn values = length of pipe that goes into the fitting connection; values follow industry standards.
- The drawing shows pipe meeting the fitting end; in the field the pipe goes in. CEL corrects pipe length and joint location for that.
- Cut length (Properties palette) = actual pipe length including the depth to engage the fittings = distance between the connectors inside the segment, based on CEL. Pipe length and cut length differ.
- Adding a part to a pipe end:
  - Flange joint: overall pipe+joint length unchanged; the pipe end moves to the flange connector; pipe length drops by the flange width; flange CEL is added to get cut length.
  - Coupling: coupling midpoint sits at the old pipe end; the pipe end moves to the coupling face.
  - Elbow: pipe end stays; pipe length unchanged; cut length grows by the elbow CEL.
  - Hub flange couplings: the overall length includes the coupling.
- Lengthen grips and dynamic length dimensions do NOT include CEL. With a fixed stock length, adding or changing a fitting can change a segment's cut length.
- Test result: on pipes joined by "Glued - Sch 40 - PVC Elbow", Length and CutLength were equal (237.3) [VERIFIED]. (inference) That part may carry no CEL; check CutLength on the real spec before using it for takeoffs.
- For fittings, cut length variable CL1 is usually half the cut length set for the connector ([KB:000233324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Adding-a-new-pipe-size-to-a-pipe-catalog.html)).

### Male/female and joint direction ([G:7CCE5361](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CCE5361-D654-4301-837D-909B31B7AF0C), [G:0050A936](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0050A936-D029-46C9-9E8E-39E158EDC765), [G:E775B16A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E775B16A-E06C-4F3B-A009-4E50059B6DC5))
- Joint direction: Male into female (default) = the male connector is drawn first, the female after the joint. Female out to male is the reverse.
- Draw with the flow: Male into Female. Draw against the flow: Female out to Male.
- Only matters for routing preferences with male-female fittings. Auto layout follows connector rules; couplings go in at proper pipe length and at break points; the software can reverse the orientation on a run when needed.
- Content Builder can make male, female or both connectors; set CEL to the real depth and AoD to the maker's tolerance.

### Angle of deflection (fitting tolerance) ([G:4F5FA490](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4F5FA490-0E26-4041-A211-DD62B6088794), [G:0050A936](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0050A936-D029-46C9-9E8E-39E158EDC765), [G:AFC86914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AFC86914-6495-41E7-9307-766EC241D3B5), [G:D69BAA6F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D69BAA6F-F571-47B7-AB6E-7A39EF894F87))
- AoD = whether a joint with a tolerance angle may deflect. Stored in catalog content; exists only for female fittings whose maker spec allows it.
- Use fitting tolerance = Yes (default) turns it on. If the part has no AoD, Yes is ignored.
- AoD is split equally between the female connectors of a fitting that supports sloped pipe, and can never exceed the value stored on the part (example: slope 10 degrees with 2 female connectors = 5 degrees each).
- Coupling or elbow: example tolerance 10 degrees: a 5 degree layout angle gets a coupling, a larger angle gets an elbow ([G:68D9D62C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68D9D62C-1FC7-4960-B636-79C8CA5C9F9B)). Ctrl + Add grip joint: Yes = coupling within tolerance, No = elbow ([G:455FEA4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-455FEA4C-CD65-4AF6-A69B-2A394E0B1989)).
- For pressure piping set Use fitting tolerance = No for faster, more directed routing ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697)).

### Connection details and connector edits
- [GUI] Select pipe or fitting > Properties palette > Advanced > Connection Details button: Nominal size; Flow direction (in, out, bidirectional); Connection type; Maximum and Current tolerance angle (AoD) for female fittings; Location (X, Y); Elevation (Z). Only Location and Elevation are editable; Add mode shows fewer rows ([G:5E0D135C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5E0D135C-5E03-4948-9077-5C217362D967)).
- [AUTO] AECBBASICCONNECTOREDIT = Pipe Connection Point Editor: Pipe Units (Metric or Imperial), Pipe Size, End Type ([G:494AB729](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-494AB729-410F-481D-BF84-8FFF50B7D396)).

### Checking connectivity ([G:5463DC12](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5463DC12-61E4-467F-9BF4-753003E2CC28))
- All systems [GUI]: View tab > MEP View panel > Solution Tip; disconnects show in red.
- Neighbors: select a pipe > Pipe tab > Modify panel > Show Connected Objects drop-down > Show Connected Objects. A run up to a junction: same drop-down > Show Connected Run.
- Branches: select a pipe > Pipe tab > General panel > Select System drop-down > Select Connected Branch; Tab cycles upstream and downstream branches.
- Script check: Connector.ConnectedMembers and AecbDatabase.Graphs (part 2) [VERIFIED].
- Solution-tip marks that come and go while drawing or after paste are normal (the connection check lags). If frequent: check pipes and fittings sit at exactly the same elevation; hover the tip; turn the indicator off; limit 3D object snaps to the MEP snaps needed; for large drawings or far-off coordinates copy into a new file with the same units ([KB:000571081](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Solution-tips-appear-and-disappear-in-AutoCAD-MEP.html)).
- Warning triangles on connections after edits (lost connections): blank or *NONE* routing preferences, damaged objects, third-party plug-ins, or incompatible types and sizes. Fix: copy and paste the objects into a new drawing, complete the routing preference, replace damaged objects ([KB:000293474](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipe-fittings-connection-problem-in-AutoCAD-MEP.html)).

### Sloped (gravity) piping ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92), [G:68D9D62C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68D9D62C-1FC7-4960-B636-79C8CA5C9F9B))
- For sanitary drain, waste, vent, storm. Slope is applied in the Z direction of the current UCS. Fittings rotate about their attach point to follow the sloped centerline.
- Auto layout solves sloped runs only if the current routing preference supports AoD (fitting tolerance).
- Steps [GUI]: start a run; pick a gravity-based routing preference; size; Routing > Slope format (example: Rise/Run with Fractional Rise = 1/4" per foot); Slope value in that format; Advanced > Use fitting tolerance = Yes; Joint direction; Branch fitting (example Tee or Wye (Lateral)); branch angle ("Values from catalog selection" = all angles in the preference; an angle outside standard plus tolerance opens Choose a Part); keep picking. The slope value displays on the segment.
- A NEGATIVE slope pitches the pipe down from the main or branch (example -1/4" = down 1/4" per foot).
- Gravity Pipe tab tools (drain, process drain, sanitary, sanitary vent, storm) support 1/8", 1/4" and 1/2" per foot.
- Branches to sloped mains use wyes (laterals) or angled tees; reducers can be eccentric or concentric. A sloped straight run needs fittings of the matching angle.
- Slope readout while drawing: shown in constrained and unconstrained layouts; a segment's slope can differ from the palette value if a routing solution needs it. [AUTO] Turn the readout off: PIPESLOPEDISPLAY, then `n` at the next prompt.
- Slope format and Slope are read-only in Modify mode ([G:FA4BD010](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FA4BD010-6E8E-41F8-81C7-592D9894D771)). Elevation lock does not work on sloped segments ([G:5BE180D2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5BE180D2-1261-4ECA-AC43-01665B174D44)). Elevation grips are not available on sloped segments; adjust the connected fittings' elevations ([G:774CA8F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-774CA8F1-DE69-4097-90E3-9679B9DA7460)).
- Not possible in 2027: sloped flexible pipe ([G:F5CB8ED8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F5CB8ED8-2D20-4597-8678-E1D3CF6BCA08)); sloped parallel pipes ([G:76A66EAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-76A66EAD-90BE-4498-9852-4EEB2A2A429A)).
- Accidental slope: if a pipe or conduit shows no elevation grip and Start elevation differs from End elevation, the add command applied a slope too small to show on the command line. Set End elevation = Start elevation; for new pipe, after the first point type `S`, Enter, `0` (no decimals), Enter ([KB:000496823](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-grip-for-MEP-objects-like-conduits-is-missing-in-AutoCAD-MEP.html)). (inference) A script drawing level chilled water should send `S` and `0` in every add session; the Slope option is on both the Start point and Next point prompts of -AECBPIPEADD [VERIFIED prompt], but its follow-up prompt text was not captured.

## 8. Sizing and modifying pipe

### Size rules
- The nominal size list holds only sizes common to every pipe and fitting in the routing preference, grouped by its size ranges. Missing size: choose another routing preference or change the parts in that size range ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697), [G:0E26F347](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E26F347-F8B2-48CB-9048-4DFA1C6456E3)).
- Changing nominal size before the first point of a run started from an object inserts a transition automatically ([G:455FEA4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-455FEA4C-CD65-4AF6-A69B-2A394E0B1989)). Starting from a pipe end with a different size inserts a transition ([G:6D79ED53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6D79ED53-1ED2-4AB0-AA13-E87A86F56538)).
- Size lock ([G:C02E5CF2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C02E5CF2-6396-4ED8-AE3C-01C675D74D3C)): Properties palette > Dimensions > Size lock = Locked. The size list goes inactive and the diameter cannot change; length and elevation still can. Use it where a run passes close to structure or other systems. In Modify mode it blocks size edits while rerouting ([G:FA4BD010](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FA4BD010-6E8E-41F8-81C7-592D9894D771)).
- Catalog sizes vs custom sizes are set in Options > MEP Layout Rules > Part Selection (part 4) ([G:258A9D37](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-258A9D37-933F-4F36-B3EB-C1C17F86A730), [G:F36E8B05](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F36E8B05-BFBC-4096-A969-934EAC8A29F1)).
- No hydronic pipe sizing calculator is described in the sources for this section. Sizing tools in them are the duct instant sizing tool and plumbing sizing (Size Sanitary Pipe with fixture units).
- Plumbing sizing uses fixture unit values on the fixtures. Default fixture units come from the fixture unit table: match by fixture type, then subtype, then keywords in the subtype name; no match = no default value. A sample table ships; make tables for local code ([G:AA5D861C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA5D861C-2B58-4774-9975-2EB42C1A3053)).

### Add a new size to a pipe catalog ([KB:000233324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Adding-a-new-pipe-size-to-a-pipe-catalog.html))
- The size must be added to EVERY part the routing preference uses (pipe, elbows, tees, couplings, taps) plus the connector. Otherwise set the unused fittings to None in the routing preference.
- [GUI] In Content Builder, open the part in its pipe catalog chapter, add a row with the new size to its size parameter values, and save the part family. Repeat for every part.
- Then regenerate the catalog from the MEP Content panel so the size reaches the master pipe catalog; answering `P` at the command line regenerates only the pipe catalog [AUTO prompt answer].
- Then make or edit a routing preference that uses the new size range, and assign it to the pipe.
- Catalog Editor (Manage ribbon) does the same job.

### Modify commands and palette
- [AUTO] PIPEMODIFY: modify type, size, location, system and connected runs of pipe, flex pipe and fittings ([G:6027B864](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6027B864-4FD9-4C8D-8B50-CECA79F73093)). PIPEPROPS opens pipe properties ([G:A939750A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A939750A-4190-4BAA-8EAC-2D037050F5CA)). Prompts are not documented.
- Modify-mode Properties palette ([G:FA4BD010](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FA4BD010-6E8E-41F8-81C7-592D9894D771)):
  - General: Description, Layer, System.
  - Dimensions: Routing preference, Nominal size, Size lock, Cut length (reported).
  - Placement: Elevation, Start elevation, End elevation, Move attached segments (default Yes), Additional information button (Location worksheet).
  - Routing: Slope format and Slope shown but NOT editable.
  - Advanced: Connection details, Anchors (fittings), Insulation thickness, flex Graphics, Pitch, Geometry.
- Modify Run [GUI] ([G:E775B16A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E775B16A-E06C-4F3B-A009-4E50059B6DC5), [G:0E26F347](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E26F347-F8B2-48CB-9048-4DFA1C6456E3)): select a pipe > Pipe tab > Modify panel > Modify Run. Tick routing preference, nominal size, system or elevation and pick new values; optional Joint direction. Changes reach only up to the next MvPart, reducer, tee or cross. A part substitution prompt may appear (stated on the duct page, [G:D828D796](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D828D796-2BBA-45FC-904C-CA86079BF3B8)). Match can be picked at the prompt while the dialog is shown ([G:535EEBD2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-535EEBD2-4C3A-4D0B-B755-F40536D66000)).
- Location [GUI] ([G:4CE1273E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4CE1273E-7697-4E7D-B37A-5B3DC6EA32AB)): segment: Placement > Elevation, Rotation, or Additional information > Location worksheet (Insertion Point X, Y, Z; Normal = 1 on the normal axis, 0 on the other two). Fitting: deselect, select the fitting, then the same worksheet (Rotation > Angle).
- Over COM: Elevation, StartPoint, EndPoint, InsulationThickness, SystemName and Layer are writable and `Break(point)` works; a COM Elevation change disconnected the pipe from its elbow (part 2) [VERIFIED].

### Break or merge segments: PIPELENGTH [AUTO start, dialog] ([G:34893C2F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-34893C2F-61A2-43E7-BC90-E7DB35EEC2D2))
- Select a segment > Pipe tab > Modify panel > Pipe Length > Pipe Length dialog.
- Scope: Apply to Pipe Run, or Select Objects. Break: enter Pipe Length, or pick start and end with the Pipe Length button; pieces get that cut length. Merge: segments must be adjacent, connected and on one centerline. The last used routing preference is kept; Joint direction applies.
- Script alternative: COM `Break(point)` with a VT_R8 point array adds a pipe [VERIFIED].

### Fittings
- Change a fitting's part [GUI] ([G:3C01D8C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C01D8C8-551C-47B8-BD22-E06DEBD87246)): select > Properties palette > part image > Select a Part > catalog part (Filter by Dimensions). [AUTO start] Commands listed: PIPEFITTINGMODIFY, PIPEFITTINGPROPS, PIPEFITTINGSTYLEEDIT (prompts not documented).
- Only within its type: standard radius elbow to long radius elbow is fine; elbow to cross is not. To change type, erase and add a new fitting ([G:3C01D8C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C01D8C8-551C-47B8-BD22-E06DEBD87246), [G:73216623](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73216623-5772-4890-8B6C-41F8B33062B7)).
- If the new fitting size differs, the connected segments can be modified. A fitting inserted into an existing run takes the run's elevation and system ([G:3C01D8C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C01D8C8-551C-47B8-BD22-E06DEBD87246)).
- [AUTO] FITTINGREPLACE ([G:8C802D27](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C802D27-83B7-4DDF-94B1-1D7074AD08D8)): replaces Tee, Reducing Tee, Cross, Reducing Cross, Elbow, Reducing Elbow or Transition in a pipe, duct or conduit run with a matching part. Ribbon: fitting tab > Replace > Replace Fitting. After the first command-line choice (not named on the page), Choose a Part lists candidates. Then options: Next (next instance), Accept (stop), Previous, More (Choose a Part again), Undo (revert the last one).

### Grips [GUI] ([G:AA2DD445](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA2DD445-8B6A-42A6-8C3F-7BDFB96093D2), [G:60DAFD39](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-60DAFD39-9725-4695-BC43-4469B80CEECF), [G:9AC34B55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9AC34B55-C967-43FC-BB0A-FD63F4CF432E))
- Types: Location, Elevation, Flip/Rotate, Lengthen, plus Add grips (part 6).
- Grip modes: click = default mode; press and release Ctrl to step to the 2nd mode, again for later modes; the tooltip lists the modes.
- Location ([G:548847B7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-548847B7-C1E5-4AB8-AB6B-5C1CDA02278D), [G:FCF459BE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCF459BE-6FA2-4D5E-9855-2012EF242509), [G:98A0F223](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-98A0F223-B56E-4E63-8E14-2CF2B93D6AEF)): moves an MvPart, fitting or segment in the CURRENT XY plane and keeps the run connected. Moving a pump: attached pipes and fittings follow, the rest stays. Moving a segment: attached fittings and elbows move, pipes beyond the elbows change length.
- Location modes on duct ([G:9469D8C6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9469D8C6-46A4-476E-B546-CE13491EB49F)): plain = connected, MvParts fixed; Ctrl once = MvParts on the same vector move too; Ctrl twice = object moves alone, connection broken (inference: pipe follows the same pattern). Flex pipe: Ctrl once keeps the MvPart connection, Ctrl twice breaks it ([G:2CCFA1A7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2CCFA1A7-189D-4953-B9FE-E0BAF037ED13)).
- Elevation ([G:9ADD3D9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9ADD3D9D-4496-4A73-90A3-4B102E13174F), [G:774CA8F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-774CA8F1-DE69-4097-90E3-9679B9DA7460)): use a side or isometric view. On connected objects: nothing pressed = adjust fittings and segments, parts stay; Ctrl once = adjust everything including parts; Ctrl twice = break connectivity. Tab to the input field and type the overall elevation or a relative change. Needs Dynamic Input and Dimension Input on; otherwise pick or type coordinates. Not on flexible or sloped segments.
- Flip/Rotate ([G:7792088D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7792088D-7B55-4ADF-AAE5-7023E88EC77D), [G:AD9FB96F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AD9FB96F-12B3-49D6-992B-1F5A840E3467)): flip grip = 180 degrees, Ctrl + flip = 90 degrees; rotate grip = any angle, which can be typed in the command window [AUTO entry]. Diamond rotate grips in isometric views turn about the centerline. Grips are limited or hidden when rotating would break connectivity (a wye with a connected branch cannot rotate). Connected objects adjust slightly or are disconnected.
- Lengthen ([G:78F05619](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78F05619-64FA-4D21-B218-0FAD9CB438C6)): keeps the segment angle; on a connected end you choose whether to keep connectivity. An unconnected segment's Start/End grip changes length AND angle (moves the XYZ point). The dynamic dimension shows pipe length, not cut length.
- Grip override options "Lengthen" (without moving connected elements) and "Lengthen, fixed MvParts" (with them) ([KB:000627171](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Enabling-or-disabling-of-the-move-for-connected-objects-in-AutoCAD-MEP.html)). (inference) The wording reads opposite to the name; test before relying on it.
- Elevation grip missing: the pipe has a slight slope ([KB:000496823](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-grip-for-MEP-objects-like-conduits-is-missing-in-AutoCAD-MEP.html), part 7).

### Selecting and filtering runs
- [GUI] Select an MEP object > contextual tab > General panel > Select System drop-down: Select System, Select System Group, Select Domain, Select Connected Branches (Tab cycles, Enter accepts) ([G:C8B48192](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C8B48192-169E-49E6-971C-24E978FDEFD2)).
- Filter by part property: Select Connected Branches, then Quick Select on the Properties palette (Object type, Properties, Operator, Value); example: only the elbows of a run ([G:AF38D131](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AF38D131-E519-4341-B8D3-6A0B2883175C)).

### Match properties ([G:535EEBD2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-535EEBD2-4C3A-4D0B-B755-F40536D66000), [G:4DD8EE16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4DD8EE16-2752-4F6C-9F39-2D9B0E9A50B7))
- Match at an add prompt or from Add Selected, ParallelRouting, or the Modify Run dialog prompt.
- Pipe: System, Elevation, Justification, Routing preference, Size, Insulation (Elevation, Justification, Size, Insulation also in Parallel Routing). Pipe fitting: System, Elevation, Insulation, Part, Size. Custom pipe fitting (from PIPECUSTOMFITTING): System, Insulation, Size. Flex pipe: System, Elevation, Insulation, Part, Size, Annotation. MvParts: Elevation, Part.
- Home tab > Modify panel > Match Properties copies display properties (and system definition and routing preference for pipe and pipe fitting) between objects of the same type; to change one representation use the Display tab of the Properties palette ([G:4DD8EE16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4DD8EE16-2752-4F6C-9F39-2D9B0E9A50B7)).

## 9. Pipe equipment, flow direction, flex pipe, custom fittings

### Pipe equipment (MvParts): place and connect
- Pipe MvParts range from chillers, boilers and cooling towers to valves and sprinklers. Types split into subtypes (Valves: ball, butterfly, gate, globe). An MvPart can change type (ball valve to butterfly valve) ([G:7CEC8CE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CEC8CE1-F652-41AA-9F22-80DE105C5F2B)).
- MvParts can be parametric or block-based and have one or more connection points ([G:58B39CF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58B39CF1-38D7-4319-9A07-343A7A6B3619)). Some have connectors in more than one domain (a furnace with duct and pipe connections) ([G:CD1FF206](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD1FF206-BB7F-455E-83CE-189BD1424B83), duct page).
- Place [GUI] ([G:23747395](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-23747395-EDC8-431A-BCB9-2D4B0614B7C0)): Piping workspace > Home tab > Build panel > Equipment drop-down > pick a pipe MvPart > Add MvParts dialog: Part tab (subtype folder; Details shows sizes), Part Filter tab (Filter by Dimensions), Part Size Name, Elevation; click the insertion point; compass for rotation. MVPARTADD is the add command named on the electrical and plumbing equipment pages ([G:B412560B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B412560B-4408-40A6-AF30-1E8BA6C5170E), [G:2DC6F9D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2DC6F9D1-14AA-4448-842B-99E5C81EDE70)); no command-line form is documented. The Add dialog appears for MvParts ([G:0FCFF73F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0FCFF73F-2691-4071-A3A6-3E0E05438AA7)), so placement is not script-friendly (inference).
- More of the same part: select it > Equipment tab > General panel > Add Selected ([G:23747395](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-23747395-EDC8-431A-BCB9-2D4B0614B7C0)).
- In-line or anchored on a pipe ([G:D8E43062](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D8E43062-9006-4832-9DA1-F4BB1737C6F5)): with the MvPart add active, hover the pipe until a pipe end or pipe curve connector shows, click; compass for rotation. Afterward grips rotate it about the pipe centerline, and an in-line part (check valve) can be flipped to match flow.
- Equipment must be in the drawing before a run can start from it. A run starts perpendicular to the connector face; the connector type and the connector rules decide what can attach ([G:CD1FF206](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD1FF206-BB7F-455E-83CE-189BD1424B83), duct page).
- Missing part: build it in Content Builder ([G:23747395](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-23747395-EDC8-431A-BCB9-2D4B0614B7C0)).

### Pipe equipment: modify (MVPARTMODIFY [AUTO start]) ([G:17B723C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17B723C5-1135-4B04-B549-C0FFC4433E9E))
- Editable: location, elevation, size, system on connectors.
- Size or part [GUI] ([G:E0C02042](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0C02042-C775-46FA-948D-86F2A25BE2C9)): select > Equipment tab > Modify panel > Modify Equipment > Multi-view Part Modify dialog > Part tab > All Installed MvParts > part > Part Size Name (sizes in the current part's range). Size missing: Part Filter tab > Connections > Nominal Connection, pick a range (format like 4-72); Display = how many sizes show; arrows under the image step through sizes.
- Elevation through Modify Equipment keeps the connections; connected objects move to the new elevation ([G:E0C02042](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0C02042-C775-46FA-948D-86F2A25BE2C9)).
- Location or elevation through the Properties palette (Placement: Elevation, Rotation, Additional information > Location worksheet) or Equipment Properties > Location tab BREAKS the MvPart away from its pipe runs ([G:FD561C54](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FD561C54-8386-4CA5-BB5E-AB6327679DD3)).
- Match one MvPart to another: Modify Equipment > Match > pick the source > Enter (matches part and elevation) > OK ([G:BDBDBC01](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BDBDBC01-6F7F-47FA-AA13-E247A3547994)).
- Sprinkler K-Factor: Modify Equipment > K Factor tab ([G:8609FB09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8609FB09-E480-4784-8736-E348FFFC46CA)).
- Connector systems: Equipment Properties > Systems tab (part 4) ([G:025A0623](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-025A0623-315D-4B98-96C2-EDC869D44BB2)).
- Turn a block, MvBlock, solid or mass element (even in an xref) into an MvPart with connectors: MVPARTCONVERT, right-click > Convert to Multi-view Part; Behavior page (name, Type, Subtype, layer key); Connectors page (connector type, Part Family Connector Properties); Edit Placement in the Connector Editor; flow direction by vector or Normal (pipe connector flowing out downward = 0,0,-1); Finish. The result is a separate drawing-only MvPart (not in a catalog); the original block stays ([G:AA3A85B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3A85B6-8F56-416A-9541-02DACF6F4472)). All dialog-driven [GUI].

### Flow direction ([G:83D7B32A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-83D7B32A-5F03-4744-9458-2C4385BE0ECC))
- [GUI] Select a segment > Pipe tab > Calculations panel > Set Flow Direction. An arrow at the segment center shows the current direction; with none set, the segment start point is upstream.
- [AUTO] Prompt: `y` reverses, `n` accepts. The direction applies to the run between branches; it stops at branch fittings (3 or more connectors: tees, crosses) and at MvParts.
- [AUTO] Reverse one segment: select it, right-click > ReverseSegment, or type `reversesegment`.
- Show Flow (Calculations panel) toggles flow markers (solid 2D arrows at segment midpoints) for runs that have a direction. Turn them off before plotting. Flow labels (flow arrows) are separate annotative objects (part 10).
- Draw with the flow and use Joint direction Male into Female (part 7).

### Flex pipe
- [AUTO start] PIPEFLEX, PIPEFLEXADD; holding Alt while picking the tool also works ([G:F5CB8ED8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F5CB8ED8-2D20-4597-8678-E1D3CF6BCA08)). PIPEFLEXADDSELECTED is listed ([G:6854A352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6854A352-8B0C-4DBE-94B5-F644B91AFB04)).
- [GUI] Home > Build > Tools drop-down > Tools > flexible pipe tool on the Piping palette. Properties palette: General > System; Dimensions > routing preference and nominal size per pipe connector; Placement > elevation.
- Routing Options > Segment: Line (straight segments; Radius factor used at every angled transition), Arc (series of arcs), Spline (complex curve).
- Advanced > Graphics for 1-Line and 2-Line: Circle, Curve, Oval, Single line, Single line 2, Vertical, Vertical 2; Pitch = pattern spacing, scaled to drawing scale ([G:F5CB8ED8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F5CB8ED8-2D20-4597-8678-E1D3CF6BCA08), [G:0050A936](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0050A936-D029-46C9-9E8E-39E158EDC765)).
- Flex and rigid pipe can share a system and stay connected through pipe curve or pipe end connectors.
- Flex pipe = predefined properties plus ONE user-defined centerline ([G:58B39CF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58B39CF1-38D7-4319-9A07-343A7A6B3619)).
- Limits: sloped flex pipe cannot be drawn in 2027 (slope properties are absent) ([G:F5CB8ED8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F5CB8ED8-2D20-4597-8678-E1D3CF6BCA08)). Elevation grips are not available on flex pipe; change the start point elevation on the Properties palette ([G:774CA8F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-774CA8F1-DE69-4097-90E3-9679B9DA7460)).
- Convert geometry to flex pipe [AUTO]: PIPEFLEXCONVERT, or select a polyline, line, arc or spline > right-click > Convert to Flex Pipe. Prompt: `n` keeps the source geometry, `y` erases it. A part substitution may be asked. Then set the pipe properties ([G:A5CE3352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A5CE3352-0C57-4CD0-B379-784763028553)).
- Edit vertices [GUI]: select > Properties palette > Advanced > Geometry > step with the Vertex arrows > type X, Y, Z (spline mode). [AUTO start] Commands listed: PIPEFLEXMODIFY, PIPEFLEXPROPS, PIPEFLEXSTYLEEDIT ([G:46877824](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-46877824-32EA-4A62-B334-346878FF825D)). Location grip moves control points in any segment mode ([G:2CCFA1A7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2CCFA1A7-189D-4953-B9FE-E0BAF037ED13)).
- A line, plumbing line or flex pipe cannot be converted into a (rigid) pipe object ([KB:000486834](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-it-possible-to-convert-either-a-line-pipe-flex-or-a-plumbing-line-into-pipe-in-AutoCAD-MEP.html)). PIPECONVERT is listed on [G:6854A352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6854A352-8B0C-4DBE-94B5-F644B91AFB04) with no description; do not plan on line-to-pipe conversion (inference); draw with -AECBPIPEADD.

### Custom pipe fittings ([G:FB38FC13](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FB38FC13-7FFB-4154-9E88-7682FA418AE5))
- [AUTO start] Commands: PIPECUSTOMFITTING, PIPECUSTOMFITTINGPROPS, PIPECUSTOMFITTINGSTYLE, PIPECUSTOMFITTINGSTYLEEDIT. The fitting itself is defined in a dialog (below).
- For a fitting the catalog lacks or a one-off design. AutoCAD lines, arcs and polylines become an MEP object with connectors.
- Size, shape and system come from the connecting parts. CEL and AoD are stored with the drawing. A custom fitting is style-based; one fitting = one style (shows in Style Manager).
- Steps: draw centerlines > Home tab > Build panel > Pipe Fitting drop-down > Pipe Custom Fitting > pick the lines, Enter > Create Custom Fitting dialog [GUI]: name, system, diameter at start and end of each segment, Mitered End if needed; Apply to All Segments, or Next twice per segment (Next is unavailable when Apply to All is checked) > Finish.
- [AUTO] Prompt after Finish: `y` erases the original centerlines, `n` keeps them.
- If any segment's size or shape is incomplete, creation fails with a prompt.
- Limit: custom fittings cannot be added to a part catalog. Reuse by copy and paste between drawings.
- Match from PIPECUSTOMFITTING: System, Insulation, Size ([G:535EEBD2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-535EEBD2-4C3A-4D0B-B755-F40536D66000)).
- Editing (stated for duct custom fittings, [G:D03CAF9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D03CAF9C-4ED7-4F2C-AD8A-B34C1BBCAB18); same for pipe is an inference): first EXPLODE gives the active view block, second gives linework; ERASE, MOVE, ROTATE, ROTATE3D and SCALE break system connections; COPY, MIRROR, OFFSET and ARRAY keep the part properties and property sets.

### Related MEP basics that affect pipe
- Part kinds ([G:E63ED223](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E63ED223-BF7D-488A-8C6C-41FC0C055E30)): block-based parts (one AutoCAD block per view direction) and parametric parts (3D model blocks generated on demand from properties). Parts can carry behaviors (automatic cleanup when connecting, default insertion) and components (centerline, insulation, lining).
- Pipe segments and pipe fittings are generated from predefined properties and trimmed when fittings connect. Components: connector, annotation, centerline, rise/drop, contour, insulation, lining ([G:58B39CF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58B39CF1-38D7-4319-9A07-343A7A6B3619)).
- Anchors ([G:B0888C4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B0888C4D-80D6-425B-9C84-BD4E18F07F59), [G:8A80B779](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8A80B779-5F19-425B-A736-BB03B3F2924A)): curve anchor (to another object's centerline), system anchor (slides along a whole run and onto other runs of the same system), reference anchor (keeps the connection when moved). In the piping domain the fittings that use anchors are takeoffs. Release [GUI]: select > right-click > Curve Anchor Release, Systems Anchor Release or Reference Anchor Release; [AUTO] commands AECBANCHORRELEASE, REFERENCEANCHORRELEASE ([G:0DF1F3AA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0DF1F3AA-47E2-415F-BC74-8D0C34FE3647)).
- Catalog part sizes ([G:2FCF9C77](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2FCF9C77-E356-44C9-9D65-A1233DDEEDC9)): the XML holds common parameters (domain, type, subtype) and size parameters stored as Basic Tables (one row per size), Constant Lists (independent lists combined), Constants, or Calculations (formulas). Parameter attributes: Name (D1, A2, user-defined), Description, Context, Index, Data Type, Visible, Units.
- Tooltips show object name, system and elevation; set them in Options > Display tab > Window Elements ([G:DFDFD34B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DFDFD34B-B80B-46C7-AE9C-232FBD212ACD)).
- Switch workspace: the workspace drop-down on the application status bar (example: Piping) ([G:35AC471A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-35AC471A-5B2C-4E05-BFB6-867B0CD937E1)).

## 10. Pipe display and annotation

### How pipe display works ([G:62483160](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-62483160-700B-401D-ABA4-8DA3BD4E3723))
- A pipe system can show as 1-line, graphical 1-line, 2-line or single line graphics. Every display maps to the real 3D model location.
- You do NOT draw a system as 1-line or 2-line. Draw it once with real parts; parts keep type, size and connection type in every display.
- Control = display configuration + system definition. Switch the drawing's display configuration for all 1-line or all 2-line. For a mix by nominal size (small pipes 1-line, large 2-line), set it in the system definition and use the matching display configuration.
- Plot guide from the help: large diameter = scaled 2-line, medium = scaled 1-line, small = graphical 1-line. 1-line is not a schematic: it keeps true geometry and location, and both 1-line and 2-line work in isometric views.
- 1-line ([G:8D92AE3D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D92AE3D-750D-4D65-A91F-6748652291E5)): fittings draw at their real envelope; in-line components (valves) as scaled 1-line; MvParts (pumps) as scaled 2-line.
- 2-line ([G:F8B86C88](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F8B86C88-EAB4-4B6E-8856-FC738A9E9141)): scaled 2D (3D in isometric views); follows real contours; used for large lines, space reservation, interference checks.
- Graphical 1-line ([G:1B4DDD6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B4DDD6A-DCF8-4375-B562-E14CBB872A54)): not to scale; equipment as schematic symbols plotted at a set size, readable on large plots of small pipe. Components keep size, type and system and can switch back. The page both says fitting and joint types are not shown and shows an example where they are (threaded gas, soldered hot water).
- Placeholder parts ([G:D6FEC85D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D6FEC85D-75AC-4326-8CE9-73122BF53D60)): dimensionless 1-line parts for preliminary layout, placed like real pipe and converted later by changing the routing preference or part subtype. The Aecb Model template has a Placeholder routing preference. Placeholder parts also appear when the catalog does not match the units ([KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)).

### Set 1-line / 2-line by size in a system definition [GUI] ([G:1B921A51](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B921A51-9E73-44FC-B21A-90C27F92E010))
- Piping workspace > Manage tab > Style & Display panel > Style Manager drop-down > Piping System Definitions > left pane Piping Objects > Pipe System Definitions > system > Single Line Graphics tab.
- Scaled 1-line: check "Show pipe and inline/anchored components as Single Line displays" (table wording; the steps and [KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html) say "Display pipe and inline/anchored components as single line displays"), then "pipe sizes less than or equal to" = upper limit diameter.
- Graphical 1-line: check "Display pipe and inline/anchored components as graphical 1-line", set the size limit, then "Inline/anchored MvPart plot length".
- 2-line: clear both check boxes (step 7 on the page; inference from the run-together steps).
- Single Line Graphics Style (connector graphics): its blocks show in this system's 1-line displays.

### Single Line Graphics styles [GUI] ([G:D0CA96ED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D0CA96ED-C825-430D-B9D9-B02F0F22146E))
- Style Manager > Piping Objects > Pipe Single Line Graphics Styles > style > Single Line Graphics tab.
- Connector Graphics Block per connection type. Unique blocks are named Aecb_ConnectionType; many types share Aecb_StandardPipe1LineGraphic.
- Scaling: Use Annotation Scale (block sized to annotation plot size) and/or Override Scale X, Y, Z. Default: the block scales to the nominal diameter.

### Display configuration and display manager
- Change the configuration: click the current display configuration name on the status bar, pick another ([G:D422E350](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D422E350-208A-4887-8F96-DC4FEC2E0D15)). Example used in the help: "Mechanical - Pipe by Size" ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)).
- Display representations control the look per view; configurations group them for a task (1-line vs 2-line, discipline views) ([G:D422E350](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D422E350-208A-4887-8F96-DC4FEC2E0D15)).
- In DISPLAYMANAGER the current configuration (bold) names its display set; that set's Display Representation Control tab shows which representation each object uses ([KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html), [KB:000626223](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-see-pipes-and-ducts-for-a-project-in-AutoCAD-MEP.html)). Layer, color and linetype per representation sit under the Representations node ([KB:000626223](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-see-pipes-and-ducts-for-a-project-in-AutoCAD-MEP.html)).
- Regenerate Model [GUI]: View tab > Appearance panel > Regenerate drop-down > Regenerate Model; select objects or Enter for all. Use after many changes, new display representations, xrefs, or when objects look wrong after REGEN; select only the bad objects in large drawings ([G:E6B78962](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6B78962-FCDA-410F-92A5-C33466412F6F)). No command name is given.

### Straight centerline display of elbows
- Elbow centerlines normally follow the curve. Straight centerlines show where the elbow centerlines intersect (fabrication, process piping) ([G:9D5D60B5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D5D60B5-148A-4489-83B3-7BF1BCD1969E)).
- [AUTO] DISPLAYSTRAIGHTCENTERLINES, then domain `c` (Conduit), `d` (Duct), `p` (Pipe) or `a` (All), then `y` (Yes). Stored in the drawing ([G:19347A63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19347A63-8656-4AD1-9DE6-49EB41225D8B)).

### Display troubleshooting
- Pipes show as one line instead of two, in 2D or 3D ([KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html)). Likely causes: plumbing lines drawn instead of pipe, placeholder pipe from missing catalogs or content packs, a system definition set to single line graphics, a display configuration that uses the 1-Line representation, or corrupt settings. Fix it on the system definition's Single Line Graphics tab (clear the check box or lower the size limit), or switch the display configuration or the representation it uses.
- Pipes show as single lines in Navisworks: the pipe system definitions display small pipe as single line. Turn that off in each affected system definition, save, and reload the model in Navisworks ([KB:000241264](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-pipes-objects-display-in-2D-wireframe-in-Navisworks.html)).
- Pipes (or ducts, lights) not visible: wrong display configuration or Display Manager settings; check the configuration, its Set, the representation per object, and the representation's layer state ([KB:000626223](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-see-pipes-and-ducts-for-a-project-in-AutoCAD-MEP.html)).

### Labels and flow arrows ([G:539E7A39](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-539E7A39-EE46-4CE4-BEE3-4DCA062F6BCB), [G:58EFC45B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58EFC45B-7BF0-4378-BD88-4B76DF549576), [G:0050A936](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0050A936-D029-46C9-9E8E-39E158EDC765))
- While drawing [GUI]: Properties palette > Advanced > Label and Flow Arrows. Pick a label style (styles can show pipe diameter or system type) and a flow arrow style; default *NONE*.
- Layout Method: By quantity = number per straight segment, added automatically; By distance = uniform interval; a segment shorter than the interval gets none.
- Defaults for new runs are in Pipe Layout Preferences > General tab; label preferences are stored in the registry ([G:58EFC45B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58EFC45B-7BF0-4378-BD88-4B76DF549576)).
- The Properties palette assigns the label style and flow arrow style of a piping object ([G:5EBE07D6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5EBE07D6-4230-4B99-819F-DA408CEA195F)). A Label Curve object is style-based, reads part data through attributes, and each label stays anchored yet editable ([G:58B39CF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58B39CF1-38D7-4319-9A07-343A7A6B3619)).
- Flow arrows (labels) are annotative, scaled by annotation scale, editable and deletable. Flow markers (Show Flow) are different; both need a flow direction set ([G:83D7B32A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-83D7B32A-5F03-4744-9458-2C4385BE0ECC)).

### Insulation ([G:6CD8EF5E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CD8EF5E-2987-4A96-ADD8-FDC4E2224C00), [G:4670FFB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4670FFB0-CEE5-4CFE-BFB6-80886B163780))
- Annotation only, not an object: you change where and how it shows. Cannot be scheduled. Visible only in 2-line display.
- Properties palette > Advanced > Insulation thickness (default 0; 0 removes it). Turned on while adding, it is applied across all pipe system definitions as you draw; a new pipe or fitting copies the insulation of the part it attaches to ([G:6CD8EF5E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CD8EF5E-2987-4A96-ADD8-FDC4E2224C00)).
- Over COM: InsulationThickness is writable [VERIFIED].

### Other annotation facts
- Rise and drop symbols come from the rise/drop style of the run's system ([G:BD4D846C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BD4D846C-105D-4779-9095-8109FEAB0EA1)). The test drawing had 2 PipeRiseDropStyles [VERIFIED].
- Joints (flanges, couplings) are separate objects that can be counted and scheduled ([G:D9B8A7EA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D9B8A7EA-D140-4F65-BCA9-1F9F231708F7), [G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7)).
- Schedule tables: per the local API help, `ModelSpace.AddCustomObject("AecScheduleTable")` creates one over COM (per the MEP COM API reference installed with the product; NOT tested).
- Bottom of pipe: Elevation is the centerline ([KB:000568090](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-of-MEP-objects-displays-wrong-value-in-AutoCAD-MEP.html)). A formula property definition on the pipe of the form `LocationZ-Height/2-Insulation Thickness` gives bottom of pipe; confirm what Height holds for round pipe before trusting it (inference). Over COM, BottomElevation and TopElevation give centerline minus/plus OD/2 [VERIFIED].
- Pipe break symbol at the end of a run ([KB:000348493](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-Pipe-Break-symbols-for-end-of-Pipe-runs-in-AutoCAD-MEP.html), written for MEP 2017 to 2019): set the Cut Line tool's symbol to a pipe break symbol with scaled behavior, then run the tool across the end of the run.

### Plumbing lines are not pipes
- Plumbing lines are style-based, always single line, with no 3D data; used for schematic plumbing ([KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html), [G:58B39CF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58B39CF1-38D7-4319-9A07-343A7A6B3619)). A plumbing line cannot be converted to a pipe ([KB:000486834](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-it-possible-to-convert-either-a-line-pipe-flex-or-a-plumbing-line-into-pipe-in-AutoCAD-MEP.html)).
- Their sizes come from the line style's Standard Sizes tab ([G:A6C2E76A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6C2E76A-D4C1-4195-BDDE-5D0463365E16)). Crossing display: higher elevation wins; at the same elevation the line drawn second decides ([G:F7B32454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7B32454-C651-4A0F-B627-37B110DD955E)). Label and flow arrow defaults: PLUMBINGPREFERENCES (Space Evenly or Repeat Every) ([G:5BA1B246](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5BA1B246-229E-40AC-8EB7-7F81AEE67B34)).

## 11. Troubleshooting and command index

### Symptom, cause, fix
- -AECBPIPEADD hangs, CPU busy, COM calls rejected ("Call was rejected by callee"): an invalid answer (a string with spaces) at a name prompt. Kill MEP; at the next launch close the "Drawing Recovery" dialog (WM_CLOSE) before COM works. Validate names first [VERIFIED].
- COM `SystemName` put fails (E_FAIL): use "Name (Abbrev)", for example "CHWS (CHWS)" [VERIFIED].
- COM `StartPoint`/`EndPoint` put fails (E_INVALIDARG): pass a VT_ARRAY | VT_R8 VARIANT, not a tuple [VERIFIED].
- COM routing preference list shows 1 item: wrong collection; read `AECB_PIPE_PARTROUTINGPREFERENCES_STYLES` from the named object dictionary [VERIFIED].
- New pipes land on `M-Pipe-Std`: the COM-made system has no layer key (read-only over COM); set `Layer` per object [VERIFIED].
- `Connectors.Item(2)` raises on a pipe or elbow that reports Count 3: only items 0 and 1 are valid [VERIFIED].
- Pipe disconnected after a COM Elevation change: moving it back restored the connection in the test [VERIFIED]. (inference) COM moves do not carry connected parts, so move whole runs with grips or redraw them.
- Choose a Part on every routing action: wrong profile, or catalogs from another unit system; set the matching profile or add the needed catalogs ([KB:000434286](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-part-message-constantly-appears-when-routing-pipes-in-AutoCAD-MEP.html)).
- "No Part Found": profile/catalog vs drawing units, wrong scaling, corrupt settings ([KB:000290750](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-The-current-catalog-contains-no-parts-which-could-be-automatically-inserted-in-this-situation-in-AutoCAD-MEP.html)).
- Add grip makes a different pipe type or size: profile/catalog mismatch or incomplete routing preference ([KB:000482051](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-created-via-the-Add-grip-are-using-wrong-size-and-type-of-pipe-in-AutoCAD-MEP.html)).
- Odd sizes (.5906 for 3/4"): MEP launched with the wrong profile (Start menu instead of the desktop shortcut, file association, corrupted or migrated profile). Set the profile current; reset or reinstall if it is missing ([KB:000262829](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Odd-pipe-sizes-are-displaying-when-trying-to-run-pipes-in-AutoCAD-MEP.html)).
- Branch cannot be perpendicular, odd fittings: routing preference "Lateral" is angled; set it to NONE in every size range ([KB:000606939](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Perpendicular-branching-not-possible-for-some-pipes-in-AutoCAD-MEP.html)).
- Warning triangles on connections: blank or *NONE* routing preference, damaged objects, third-party plug-ins, incompatible types or sizes; copy and paste into a new drawing, fix the preference, replace objects ([KB:000293474](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipe-fittings-connection-problem-in-AutoCAD-MEP.html)).
- Routing preference fittings show no values in Style Manager: clipboard copy into a new drawing ([KB:000578897](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/No-values-for-pipe-or-duct-fittings-in-Routing-Preferences-with-in-Style-Manager-in-AutoCAD-MEP.html)).
- Pipe stops at each direction change with no message: corrupted settings; reset to defaults ([KB:000578805](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-draw-pipe-continuously-in-AutoCAD-MEP.html)).
- Elevation grip missing, Start and End elevation differ: tiny slope; set End = Start, or `S` `0` while adding ([KB:000496823](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-grip-for-MEP-objects-like-conduits-is-missing-in-AutoCAD-MEP.html)).
- Crash with an unhandled access violation when auto-routing past a tee rotated to 45 degrees: corrupted drawing; repair it ([KB:000444897](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-crashes-when-trying-to-auto-route-pipe.html)).
- Pipes route at 15/30/45 degrees despite polar settings: compass angles; uncheck Enable Compass ([KB:000625708](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Polar-tracker-is-set-to-22-5-45-but-pipes-keep-routing-at-angles-15-30-45-in-AutoCAD-MEP.html)).
- Solution tips flicker: normal background check; see part 7 ([KB:000571081](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Solution-tips-appear-and-disappear-in-AutoCAD-MEP.html)).
- Pipes single line in plan, 3D or Navisworks; pipes invisible: part 10 ([KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html), [KB:000241264](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-pipes-objects-display-in-2D-wireframe-in-Navisworks.html), [KB:000626223](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-see-pipes-and-ducts-for-a-project-in-AutoCAD-MEP.html)).
- A line, plumbing line or flex pipe will not convert to pipe: not supported ([KB:000486834](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-it-possible-to-convert-either-a-line-pipe-flex-or-a-plumbing-line-into-pipe-in-AutoCAD-MEP.html)).
- A file hangs on open because of a corrupt pipe or conduit fitting: see the performance section ([KB:000243116](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Long-delay-opening-file-and-changing-views-in-AutoCAD-MEP-drawing.html)). Object color not following layer: see the display section ([KB:000467587](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MEP-component-not-matching-layer-color-in-AutoCAD-MEP.html)).
- Piping workspace or MEP tools missing: MEP running on the wrong profile, corrupted settings, or damaged install ([KB:000318927](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Workspaces-such-as-HVAC-or-Electrical-are-missing-in-AutoCAD-MEP.html)). A shortcut can load the right profile with `/ld AecBase.dbx /p <profile> /product "MEP"` ([KB:000643429](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/User-Interface-not-loading-when-importing-custom-user-settings-in-AutoCAD-MEP.html)). After installing plain AutoCAD the MEP toolset is a separate download and install ([KB:000340839](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/After-installing-AutoCAD-2019-vertical-tools-such-as-Architecture-tools-like-walls-are-not-available-in-the-ribbon.html)).

### Commands [AUTO unless marked]
- `_-AECBPIPEADD`: command-line pipe add; prompts and tested sequence in part 1 [VERIFIED].
- PIPEADD: palette-driven add ([G:3379178E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3379178E-CA55-496A-B68E-90055E6D0697)). Elevation lock and fitting override reset when it ends ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C), [G:A18DE50D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A18DE50D-2333-4473-BCAE-A997EE0278F6)).
- PIPEADDSELECTED, PIPEFLEXADDSELECTED, PIPECONVERT: listed, no usage documented ([G:6854A352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6854A352-8B0C-4DBE-94B5-F644B91AFB04)).
- PIPEFLEX, PIPEFLEXADD ([G:F5CB8ED8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F5CB8ED8-2D20-4597-8678-E1D3CF6BCA08)). PIPEFLEXCONVERT: `n` keep / `y` erase source geometry ([G:A5CE3352](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A5CE3352-0C57-4CD0-B379-784763028553)). PIPEFLEXMODIFY, PIPEFLEXPROPS, PIPEFLEXSTYLEEDIT ([G:46877824](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-46877824-32EA-4A62-B334-346878FF825D)).
- PIPECUSTOMFITTING (`y` erase / `n` keep centerlines after Finish), PIPECUSTOMFITTINGPROPS, PIPECUSTOMFITTINGSTYLE, PIPECUSTOMFITTINGSTYLEEDIT ([G:FB38FC13](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FB38FC13-7FFB-4154-9E88-7682FA418AE5)).
- PIPEMODIFY ([G:6027B864](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6027B864-4FD9-4C8D-8B50-CECA79F73093)). PIPEPROPS ([G:A939750A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A939750A-4190-4BAA-8EAC-2D037050F5CA)). PIPELENGTH: dialog ([G:34893C2F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-34893C2F-61A2-43E7-BC90-E7DB35EEC2D2)).
- PIPEFITTINGMODIFY, PIPEFITTINGPROPS, PIPEFITTINGSTYLEEDIT ([G:3C01D8C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C01D8C8-551C-47B8-BD22-E06DEBD87246)). FITTINGREPLACE: Next, Accept, Previous, More, Undo ([G:8C802D27](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C802D27-83B7-4DDF-94B1-1D7074AD08D8)).
- PARALLELROUTING: `b` new baseline, `a` accept solution, Next/Previous/Accept when joining runs ([G:76A66EAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-76A66EAD-90BE-4498-9852-4EEB2A2A429A), [G:D66E353F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D66E353F-06BB-4764-A4E7-D975410B01DD)).
- PIPESLOPEDISPLAY: `n` turns the slope readout off ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- DISPLAYSTRAIGHTCENTERLINES: `c`/`d`/`p`/`a`, then `y` ([G:19347A63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19347A63-8656-4AD1-9DE6-49EB41225D8B)).
- AECBBASICCONNECTOREDIT: pipe connection point editor ([G:494AB729](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-494AB729-410F-481D-BF84-8FFF50B7D396)).
- PIPESYSTEMDEF, PIPESYSTEMDEFEDIT ([G:13267A31](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13267A31-5CA1-4F26-B41F-670E747D342E)); SETACTIVERP, PIPEPREFDEF ([G:C581B422](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C581B422-8822-47B9-9547-E95F9B98D2FD)): named in page metadata only, prompts unknown. PIPE: named on About Pipe Systems ([G:91CB307A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-91CB307A-2C8D-4476-B883-41C444B30ED4)).
- MVPARTADD, MVPARTMODIFY, MVPARTCONVERT: dialog-driven ([G:B412560B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B412560B-4408-40A6-AF30-1E8BA6C5170E), [G:17B723C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17B723C5-1135-4B04-B549-C0FFC4433E9E), [G:AA3A85B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3A85B6-8F56-416A-9541-02DACF6F4472)).
- Set Flow Direction prompt `y` reverse / `n` accept; `reversesegment` ([G:83D7B32A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-83D7B32A-5F03-4744-9458-2C4385BE0ECC)).
- AECBCOMPASS, AECBCOMPASSBAR ([G:9F8199F2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F8199F2-616E-4458-9CAA-D77BC4396DFE)).
- STYLESBROWSER ([G:21566B25](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-21566B25-BB2E-434B-B2BC-E557758C18C0)). STYLEMANAGER ([KB:000606939](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Perpendicular-branching-not-possible-for-some-pipes-in-AutoCAD-MEP.html); [KB:000568090](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-of-MEP-objects-displays-wrong-value-in-AutoCAD-MEP.html) types STYLESMANAGER). DISPLAYMANAGER ([KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html)).
- Regenerate Catalog: answer `P` for the pipe catalog only ([KB:000233324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Adding-a-new-pipe-size-to-a-pipe-catalog.html)).
- PLUMBINGPREFERENCES ([G:5BA1B246](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5BA1B246-229E-40AC-8EB7-7F81AEE67B34)); PLUMBINGSYSTEMDEF, PLUMBINGSYSTEMDEFEDIT ([G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F)).

### Keywords typed at prompts
- `n` New run ([G:BD4D846C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BD4D846C-105D-4779-9095-8109FEAB0EA1)). `sl` slide a takeoff, then an angle ([G:96EEA3F0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-96EEA3F0-15BD-4EAE-B666-3BBE21244435)).
- Routing solutions: `n`, `p`, `a`, or a number then Accept ([G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926)).
- `S` then `0` = level pipe ([KB:000496823](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Elevation-grip-for-MEP-objects-like-conduits-is-missing-in-AutoCAD-MEP.html)); `S` then `90` = vertical routing ([KB:000550597](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Vertical-routing-in-AutoCAD-MEP.html)).
- `p` (Plane) cycles the UCS plane with the compass on ([G:2CC1B7FF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2CC1B7FF-22E1-4B4D-84BD-11BEADCDB609)).
- -AECBPIPEADD: `R`, `SY`, `SI` tested [VERIFIED]; other option letters by inference (part 1).

### System variables and checks used in scripts
- LOGFILEMODE 1, then read the file named by LOGFILENAME to capture every prompt and answer [VERIFIED use].
- CPROFILE = "AutoCAD MEP (US Imperial)" confirms the profile; PRODUCT reads "AutoCAD" even in MEP [VERIFIED].
- No pipe-specific system variables are documented in the sources for this section.

### Not yet tested (worth a probe before relying on it)
- Prompt text and behavior of the -AECBPIPEADD options Elevation, Slope, Tolerance off, Lock size, Justification, Match, Compass, Plane, roTAte.
- Answering R or SY with an index number; the `?` listing.
- Whether a typed point on an open pipe end or along a pipe connects (tee or takeoff) without MEP snaps.
- Routing preference and nominal size changes over COM; the AecbGuiSize helpers.
- Whether PIPEADD and AECBPIPEADD are the same command, and command-line forms for MvPart placement.
