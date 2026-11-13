# 12 - Automation I: COM/ActiveX and AutoLISP

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

How to drive AutoCAD 2027 and the AutoCAD MEP 2027 toolset with no hands on the mouse: from outside over COM (Python, raw IDispatch) and from inside with AutoLISP.
Covers attaching to the running program, SendCommand and getting results back, the AEC/MEP COM API (ProgIDs 8.9, the Init pattern, what COM can and cannot create or change), the property set and schedule API, and the AutoCAD ActiveX object model (documents, collections, entities, selection, layouts, plotting, events).
Then AutoLISP: command and command-s, entity and selection functions, dictionaries and xrecords, the vla-/vlax- ActiveX functions and reactors.
Facts tested live on a test machine in October 2026 are marked VERIFIED. Everything else comes from the Autodesk 2027 help, the local API help or the installed type libraries.

Legend: (G:XXXXXXXX) links to the Autodesk help page cited. VERIFIED = live test on a test machine (2026-10-16/17; write-ups in the `_verified/` folder; "the probes" are those test scripts). (TLB:name) = the installed COM type library of that name. (CHM:book/page) = the API help installed with the product. (REG) = AEC ProgIDs read from the registry. (user) = earlier hands-on experience, not re-tested. [AUTO] = usable from a script; (inference) = a conclusion, not stated in the source.

Contents
- 12.1 Attaching from outside AutoCAD (Python COM)
- 12.2 SendCommand, PostCommand and getting results back
- 12.3 AutoCAD MEP and AEC COM API (verified)
- 12.4 Property set and schedule API
- 12.5 ActiveX object model: documents, collections, arrays, Utility
- 12.6 Entities, blocks, attributes, xrefs, raster, xdata, selection sets over COM
- 12.7 Layouts, viewports, views, zoom and plotting over COM
- 12.8 ActiveX events
- 12.9 AutoLISP ActiveX layer: vl-load-com, vla- and vlax- functions
- 12.10 AutoLISP talking to AutoCAD: command, command-s, variables, input, conversions
- 12.11 AutoLISP entities, xdata and selection sets
- 12.12 AutoLISP symbol tables, dictionaries and xrecords (and the MEP dictionaries)
- 12.13 AutoLISP reactors
- 12.14 Compatibility, loading and admin facts that break automation

## 12.1 Attaching from outside AutoCAD (Python COM)

### The root object
- The Application object is the root. Every object has an `Application` property that leads back to it. ([G:8B061754](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8B061754-6592-4BA5-B189-D366C0478676))
- [AUTO] ProgID in the 2027 help sample: `AutoCAD.Application.26.0`. VBA attaches to the running session with `GetObject(, "AutoCAD.Application.26.0")`, which needs no drawing open. ([G:C584A219](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C584A219-3E90-4D1B-B382-6000F00CE9B0)) AutoCAD 2027 is release 26.0. ([G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A))
- `ThisDrawing` exists only in VBA. From outside, use `Application.ActiveDocument`. ([G:C5BD40D8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C5BD40D8-A0B0-4E65-9090-02924E3877AE); inference for Python)
- [AUTO] The test scripts get the Application object through a small attach helper, then walk Application > Documents > Document > Database or ModelSpace. VERIFIED
- Application members shown in a dump: ActiveDocument, Caption, Documents, FullName, Height, HWND, LocaleId, MenuBar, MenuGroups, Name, Path, Preferences, StatusId, VBE, Version, Visible, Width, WindowLeft, WindowState, WindowTop. ([G:FE43302E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE43302E-AC21-4C0B-B61B-A10751A9E263))
- [AUTO] `Application.GetInterfaceObject(ProgID)` loads the named object into AutoCAD as an in-process server. This is how the AEC/MEP objects are made (12.3). (TLB:acax26enu)
- [AUTO] `Application.GetAcadState()` returns an AcadState object; its `IsQuiescent` tells whether AutoCAD is idle and ready to take out-of-process Automation calls. Not tested. (TLB:acax26enu)

### Window
- `Visible = False` hides AutoCAD. `WindowState`: acNorm 1, acMin 2, acMax 3. Width, Height, WindowTop, WindowLeft are pixels. ([G:BCE7E749](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BCE7E749-DCCB-4914-9E52-CC1265A3574F); values TLB:acax26enu)
- [AUTO] The probes minimize AutoCAD with `WindowState = 2` before working. VERIFIED

### Zero-document state
- All drawings can be closed in a session. Then only open, new, import and exit work; any other call raises an error. ([G:83045B84](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83045B84-E056-4AE6-AEF5-D48AFB4F9F78))
- [AUTO] Check `Documents.Count` (0 = no drawing) before touching `ActiveDocument`. ([G:83045B84](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83045B84-E056-4AE6-AEF5-D48AFB4F9F78))
- Ribbon, toolbars and the command line are not available then. AutoLISP never runs with zero documents. ([G:83045B84](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83045B84-E056-4AE6-AEF5-D48AFB4F9F78))

### Startup and idle (VERIFIED)
- In testing, MEP 2027 answered COM 46 s after launch; other launches took about 3.5 min.
- [AUTO] Wait for COM: poll `Documents.Count` every 5 s, give up at 420 s.
- [AUTO] After `Documents.Open`, and after every write or command, wait until AutoCAD is idle before the next call. The probes allow 120 s after Open and 30 to 90 s after edits and commands.
- The `PRODUCT` system variable reads "AutoCAD" even in AutoCAD MEP. `CPROFILE` reads "AutoCAD MEP (US Imperial)". Use CPROFILE to tell which product is running.

### Raw IDispatch from Python
- pywin32 name lookup fails on MEP objects, so call them through raw IDispatch. (user)
- [AUTO] Property put used by the probes: `o.Invoke(o.GetIDsOfNames(name), 0, pythoncom.DISPATCH_PROPERTYPUT, False, value)`. VERIFIED
- [AUTO] Pass points as typed double arrays: `win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))`. A plain tuple fails: E_INVALIDARG on a StartPoint put, E_ABORT on Pipe.Break. VERIFIED
- Points read back as Python tuples. ConnectedMembers comes back as a tuple of objects, or None. VERIFIED
- On the ActiveX side all arrays travel as Variants; a 3D point is 3 doubles, a 2D point 2 doubles; every output array comes back as a Variant. ([G:F6B0A90B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F6B0A90B-B484-4B2E-A0E1-FE6B7441ADBC), [G:192B537E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-192B537E-8F89-4F21-BD5D-28B9E3918C88))
- `Layers("ABC")` is VBA default-member shorthand. From Python call `.Item("ABC")`. (inference)
- Named constants do not exist over raw IDispatch; pass the numbers. The values given in this section come from (TLB:acax26enu).

### HRESULTs seen (VERIFIED; hex worked out from the decimal)
| Code | Hex | Name | Seen when |
|---|---|---|---|
| -2147352567 | 0x80020009 | DISP_E_EXCEPTION | Outer code for every AutoCAD error; the real code is inside the tuple |
| -2147467259 | 0x80004005 | E_FAIL | Item() of a missing name; SystemName "CHWS" without "(CHWS)"; the third pipe connector |
| -2147024809 | 0x80070057 | E_INVALIDARG | StartPoint put with a plain tuple |
| -2147467260 | 0x80004004 | E_ABORT | Pipe.Break with a plain tuple |
| -2147467263 | 0x80004001 | E_NOTIMPL | StyleName read on an AecbDbPipe |
| -2147352570 | 0x80020006 | DISP_E_UNKNOWNNAME | AecbGraph.Iterator looked up by name |

- "Call was rejected by callee": AutoCAD is busy, or a command is waiting at a prompt. (user; VERIFIED) Its standard COM name is RPC_E_CALL_REJECTED, 0x80010001 (general COM knowledge, not from the Autodesk pages).

### Things that hang or kill a COM session
- A command left waiting at a prompt makes every later COM call fail with "Call was rejected by callee". (user)
- VERIFIED: a probe sent an error string with spaces as a routing preference name. MEP spun at the prompt at about 60% of a core, rejected every COM call and had to be killed. The next launch stopped on a "Drawing Recovery" dialog (no #32770 buttons except Close) that blocked COM until it was closed with WM_CLOSE.
- [AUTO] The test scripts run a dialog watcher that cancels any dialog for the whole run; no dialog appeared in the later test runs. VERIFIED
- These wait for a person and hang an unattended run: every `Utility.Get*` input method, `SelectionSet.SelectOnScreen`, `Application.ZoomPickWindow`. ([G:2F1938FE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2F1938FE-DE63-456B-9C29-612DA4539EB0), [G:6D85F583](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6D85F583-2B0D-4C8B-9E17-0A072EBCB41C), [G:A675254F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A675254F-08B2-4048-95CB-DD7195616BC1)) `Plot.DisplayPlotPreview` opens the Plot Preview dialog (TLB:acax26enu); never call it unattended. (inference)

### Type libraries
- AutoCAD 2027: `acax26<lang>.tlb` (AutoCAD) and `axdb26<lang>.tlb` (ObjectDBX); `<lang>` = enu on English installs. 2025 and 2026 use 25; 2021 to 2024 use 24. ([G:927E71C2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-927E71C2-E515-438E-9D7A-246D97BEF93F))
- Replaced libraries: `acETransmit20.tlb`; `AcSmComponents26.tlb` (Sheet Set Object API); `cao20<lang>.tlb` (Connectivity Automation Object API). ([G:927E71C2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-927E71C2-E515-438E-9D7A-246D97BEF93F))
- AEC/MEP libraries: `C:\Program Files\Common Files\Autodesk Shared\*89.tlb`. VERIFIED
- For exact member lists and dispids dump the installed type libraries with a COM type library viewer and read them, do not guess: `acax26enu` (AutoCAD), `AecbXPipeBase89` (pipe objects and AecbPipeDatabase), `AecbXUIBldSrv89` (AecbApplication, AecbDocument, AecbPartQuery, AecbUtility, AecbPreferences objects), `AecbXGuiBldSrv89` (AecbGuiSize, AecbGuiModify, AecbGuiPartFactory, AecbDuctInstantSizing, property palette helpers), `AecXSchedule89` (property sets and schedule tables).

## 12.2 SendCommand, PostCommand and getting results back

### SendCommand rules
- [AUTO] `Document.SendCommand(string)` sends ONE string to the command line: the command name plus every answer, in the order the prompts ask for them. ([G:0A56CD7D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A56CD7D-C18E-4A94-B0A7-6F70956A21A9))
- A blank space or a carriage return in the string = Enter. End the string with a space or newline for the final Enter. ([G:0A56CD7D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A56CD7D-C18E-4A94-B0A7-6F70956A21A9))
- Calling it with no argument is invalid (unlike LISP `(command)`). ([G:0A56CD7D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A56CD7D-C18E-4A94-B0A7-6F70956A21A9))
- Help sample: `SendCommand "_Circle 2,2,0 4 "` then `SendCommand "_zoom a "`. ([G:0A56CD7D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A56CD7D-C18E-4A94-B0A7-6F70956A21A9))
- SendCommand is asynchronous: the call can return before the command is done. Wait for idle before the next COM call. (user)
- In LISP sent by SendCommand a newline is Enter. (user) Spaces inside the parentheses of a LISP expression do not end it: the probes send `(progn ...)` full of spaces, ended by one `\n`. VERIFIED
- [AUTO] Put `_` before command names and keywords so they work in any language build; a leading `.` runs the built-in command even if it was redefined; `._LINE` and `_.LINE` are both valid. ([G:D156B6ED](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D156B6ED-B1B4-42CB-BE1D-CA251BFC08C3); written for LISP `command`, applied to SendCommand by inference)
- [AUTO] Use the hyphen forms that stay on the command line (`_-AECBPIPEADD`, `-LAYER`). Dialog forms block a run.
- Never call SendCommand from an ActiveX event handler. ([G:2FF2F1B5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2FF2F1B5-FFAC-420A-A741-15D1FC1A571E))

### PostCommand
- `Document.PostCommand(string)` posts a command string to the document to be processed. It arrived in AutoCAD 2015. (TLB:acax26enu; [G:E69C877D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E69C877D-F84B-4282-807D-E084C931D533))
- The 2027 migration notes say to review every SendCommand call for a switch to PostCommand ([G:E69C877D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E69C877D-F84B-4282-807D-E084C931D533)), and to pick SendCommand or PostCommand "based on if the string should be executed asynchronously or synchronously". Neither page says which method is which. ([G:4CD0B52A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4CD0B52A-9D16-455B-BB8D-E7DBC14E75C8))
- The LISP Import sample zooms a newly opened document with `(vla-PostCommand newDoc "_zoom a ")`, "instead of vla-ZoomAll because the document might not be current yet". ([G:F51F1C9E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F51F1C9E-D750-423B-9462-EA1CB2E98E55))
- PostCommand was not tested. SendCommand plus an idle wait is the verified path.

### Verified MEP example: -AECBPIPEADD (VERIFIED)
Sent as one string (`\n` = Enter):
```
_-AECBPIPEADD\nR\nGlued\nSY\nCHWS\nSI\n4"\n_non\n0,0,120\n_non\n240,0,120\n_non\n240,240,120\n\n
```
Prompts, copied from the command log (LOGFILEMODE 1):
```
Start point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Slope/Match/preFerences]:
  R  -> Routing Preference name, index number or [?] <Glued>:
  SY -> System name, index number or [?] <Standard>:
  SI -> Nominal Size or [?] <1">:
Next point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Compass/Plane/roTAte/Slope/Match/New run/preFerences]:
```
- After each option answer the Start point prompt comes back, so options can be chained before the first point.
- After the second point the SYstem option drops out of the list and Undo appears.
- `_non` before each point is the object snap override "none" (inference on its meaning; the sequence itself is verified).
- Result: 2 pipes and one "Glued - Sch 40 - PVC Elbow" (SizeName "4.00 Inch Glued - Sch 40 - PVC Elbow 90.0 Deg"). Each pipe is 237.3 in long: the elbow takes 2.7 in of each 240 in leg. All three landed on layer `M-Pipe-Std`.
- [AUTO] A space ends an answer at these prompts. Names with spaces (most routing preferences) cannot be typed. Use a space-free name (Glued, Grooved, Placeholder, Standard) or the index number. The index base was not tested.
- [AUTO] Check every value before sending it. One bad value strands the command at its prompt and the session dies (12.1).

### Getting results back (VERIFIED patterns)
SendCommand returns nothing. The probes use two ways back.
1. LISP writes a file; Python polls for it:
```
(progn (setq f (open "C:/scratch/out.txt" "w")) <body that calls (write-line x f)> (close f) (setq f nil) (princ))
```
   - Send it with one final newline. Delete the old file first; poll until it exists and has size > 0 (probes: 0.3 s steps, 30 s limit).
   - A body that worked: `(foreach p (dictsearch (namedobjdict) "AECB_PIPESYSTEMDEFS") (if (= (car p) 3) (write-line (cdr p) f)))`.
   - In LISP strings write paths with forward slashes or doubled backslashes. ([G:CB21D8A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB21D8A9-1A88-477F-95CA-74F665609A42))
2. The command log:
   - `SetVariable("LOGFILEMODE", 1)`, then get the file name from `GetVariable("LOGFILENAME")`.
   - Note the file size before sending; read only the new bytes after. This captured the exact prompts above.
- System variables need no LISP: `Document.GetVariable(name)` and `Document.SetVariable(name, value)`. ([G:AE8193CC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AE8193CC-CEAE-4B0A-BC38-808742B1750C))

### What blocks a SendCommand run
- A prompt still waiting: a missing answer, a pick, or a value that was rejected and asked again. (user; VERIFIED)
- Dialogs and palettes. Example: INSERT opens the Blocks palette since 2020; CLASSICINSERT opens the old dialog. ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))
- PAUSE, any getXXX, entsel or getfiled inside the LISP. ([G:93E25253](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-93E25253-F42A-4E85-84AD-4DCA66DB48A6), [G:7F024C1B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7F024C1B-EFB8-4F6C-9EFE-A6491210A4CD), [G:CB21D8A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB21D8A9-1A88-477F-95CA-74F665609A42))
- Raster images still loading after open (2026 and later): run `IMAGEASYNCWAIT` after opening and before editing or plotting. No syntax or options are given. ([G:945E9BA6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-945E9BA6-A91A-46EA-9394-2D84114842BA), [G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))

### Jobs ActiveX cannot do: send a command instead
- No ActiveX method clips blocks or xrefs: use XCLIP through SendCommand. The page gives no scripted option sequence. ([G:577D96C5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-577D96C5-9B22-4771-87DD-38D32ACF9F09))
- No ActiveX method sets object snaps, measures intervals or divides objects (MEASURE, DIVIDE style). ([G:A8CD0FE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A8CD0FE0-9D03-42F3-8A20-EAC331FF3499))
- MEP objects (pipe, duct, fittings, MvParts) cannot be created over COM: draw them with the hyphen commands. VERIFIED (12.3)

## 12.3 AutoCAD MEP and AEC COM API (verified)

Test setup: a scratch copy of `C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg`, opened in AutoCAD MEP 2027 (profile "AutoCAD MEP (US Imperial)") over COM from Python with raw IDispatch. VERIFIED

### ProgIDs
- AEC/MEP ProgIDs on AutoCAD 2027 end in `.8.9`. VERIFIED (REG)
- Only versioned AecX ProgIDs are registered; none exists without the `.8.9`. The help shows `GetInterfaceObject("AecX.AecScheduleApplication")` with no version (CHM:scheduleauto-reference/html_idh_object_aecscheduleapplication). Use the `.8.9` form, which was tested. (REG; the version-less form was not tried)
- Tested: `AecX.AecbPipeDatabase.8.9`, `AecX.AecbDatabase.8.9`, `AecX.AecScheduleApplication.8.9`. The test notes also list `AecX.AecbApplication.8.9` and `AecX.AecBaseApplication.8.9` as entry points. VERIFIED
- Registered but not tested: `AecX.AecbHvacDatabase.8.9`, `AecX.AecbPlumbingDatabase.8.9`, `AecX.AecbElecDatabase.8.9`, `AecX.AecScheduleDatabase.8.9`, `AecX.AecArchBaseApplication.8.9`, `AecX.AecbPartQuery.8.9`, `AecX.AecbGuiSize.8.9`, `AecX.AecbGuiModify.8.9`, `AecX.AecbDuctInstantSizing.8.9`, `AecX.AecbPanelSchedule.8.9`. (REG)

### The Init pattern (VERIFIED)
```
acad = app()                                          # AutoCAD.Application
doc  = acad.Documents.Open(copy_path)                 # or acad.ActiveDocument
db   = doc.Database
pdb  = acad.GetInterfaceObject("AecX.AecbPipeDatabase.8.9")
pdb.Init(db)                                          # required before any collection
sds  = pdb.PipeSystemDefs
bdb  = acad.GetInterfaceObject("AecX.AecbDatabase.8.9")
bdb.Init(db)
graphs = bdb.Graphs
sa   = acad.GetInterfaceObject("AecX.AecScheduleApplication.8.9")
psds = sa.PropertySetDefs(db)                         # no Init on the schedule application
```
- AecbPipeDatabase collections read in the test: PipeSystemDefs, PipeStyles (count 1), PipeFittingStyles (1), PipeFlexStyles (1), PipeCustomFittingStyles (1), PipeRiseDropStyles (2), PipePartCatPrefStyles (1). VERIFIED (test log)
- `Init(AcadDatabase)` also exists on AecbPipeDatabasePreferences, AecScheduleDatabase and AecScheduleDatabasePreferences. (TLB:AecbXPipeBase89, TLB:AecXSchedule89)
- AecbDatabase "Extends AcadDatabase". Its properties are the MEP style and system collections (cable tray, conduit, duct, pipe, DuctSystemDefs, ElecSystemDefs, PipeSystemDefs, MvPartStyles, Graphs and more). (CHM:buildingauto-reference/HTML_idh_abs_object_aecbdatabase)
- Many help pages print "Access via: Document.bPipeSystemDefs" and the like. That text does not match the working route; use the database object plus Init. (CHM; VERIFIED)
- The installed building API help has an objects list; each object page gives "Create using" and "Access via". (CHM:buildingauto-reference)

### What COM can and cannot create
| Item | Create over COM? | Evidence |
|---|---|---|
| Pipe, duct, fittings, MvParts, all MEP entities | NO | Entity pages say "Create using: N/A" (CHM). `vla-AddCustomObject "AecbDbPipe"` was refused on 2026-10-16 (VERIFIED) |
| Pipe system definition | YES: `PipeSystemDefs.Add(name)` | VERIFIED |
| Pipe styles, fitting styles, routing preferences (PartCatPrefStyles), rise/drop styles | No Add method | (TLB:AecbXPipeBase89): IAecbPipeSystemDefs is the only collection in it with Add |
| Connector style, dictionary record | Help: `AecbConnectorStyles.Add`, `AecbDictRecords.Add` | (CHM); not tested |
| Schedule table | Help: `ModelSpace.AddCustomObject("AecScheduleTable")` | (CHM:scheduleauto-reference/html_idh_object_aecscheduletable); not tested |
| Property set definition, property definition, schedule table style | `Add(Name)` | (TLB:AecXSchedule89); not tested (12.4) |
- 112 object pages in the building help say "Create using: N/A"; AecbConnectorStyle and AecbDictRecord are the only two with a create route. (CHM:buildingauto-reference)
- [AUTO] Draw MEP objects with the hyphen commands sent by SendCommand (12.2), then read and adjust them over COM.

### Pipe system definitions (VERIFIED)
- [AUTO] `sd = PipeSystemDefs.Add("CHWS")`, then put `LabelName` ("CHWS"), `FamilyName` ("Chilled Water"), `Description`.
- The new system shows at once in the drawing dictionary `AECB_PIPESYSTEMDEFS` and works at the `-AECBPIPEADD` SYstem prompt.
- Pipes drawn in it report SystemName "CHWS (CHWS)", SystemAbbreviation "CHWS", SystemFamily "Chilled Water".
- `LayerKey` is read-only over COM (type library: get only). A COM-made system has an empty layer key, so its pipes land on the default layer `M-Pipe-Std`. Set `Layer` on each object instead.
- `MinimumNominalDiameter` read -1.0 on the new system. (test log)
- Use a name with no spaces: a space ends input at MEP prompts.
- The help page lists only Has, Item and Remove for AecbPipeSystemDefs (CHM:buildingauto-reference/HTML_idh_abs_object_aecbpipesystemdefs). The type library also has Add, Count and Rename (TLB:AecbXPipeBase89). Add works.

### Routing preferences (VERIFIED)
- `AecbPipeDatabase.PipePartCatPrefStyles` is NOT the routing preference list. In a drawing holding 25 routing preferences it reported Count 1, `Has("Brazed Copper")` False, and `Item("Brazed Copper")` raised E_FAIL.
- [AUTO] Read the names from the dictionary: `(dictsearch (namedobjdict) "AECB_PIPE_PARTROUTINGPREFERENCES_STYLES")`, group 3 entries (file pattern in 12.2).
- The 25 in `Routing Preferences (US Imperial).dwg`: Brazed Copper; Butt Welded; Butt Welded and Socket Welded; Cast Iron Soil Pipe - Bell x Spigot; Cast Iron Soil Pipe - No Hub Fittings; D.I. Mechanical Joint; D.I. Push On Joint; D.I. Threaded Flanged - 150 Lb.and Threaded; D.I. Threaded Flanged - 250 Lb.and Threaded; DWV Copper; Generic Flanged; Generic Socket Weld; Generic Threaded; Glued; Grooved; Grooved and Threaded; HDPE - IPS; Placeholder; Sanitary PVC DWV; Sanitary PVC Hub x No Hub; Slip on Flanged - 150 Lb. and Threaded; Socket Weld 3000-lb.; Standard; Threaded 2000-lb.; Weld Neck Flanged - 150-lb. and Threaded.
- Only Glued, Grooved, Placeholder and Standard can be typed at a prompt (no spaces). Answer the others by index number at `Routing Preference name, index number or [?] <Glued>:`.
- Before the test this drawing held one pipe system, "Standard".

### Reading pipes and fittings (VERIFIED)
- [AUTO] Find MEP objects by class name: loop `ModelSpace.Item(i)` for i = 0 to Count - 1 and test `ObjectName`: `AecbDbPipe`, `AecbDbPipeFitting`.
- Readable on AecbDbPipe: StartPoint, EndPoint, MidPoint, Length, CutLength, SizeName ("4 Inch Commercial Pipe"), CrossSectionSize ("4 1/2", the OD), NominalSize (4.0), SystemName, SystemAbbreviation, SystemFamily, PartDescription ("Commercial Pipe"), Name ("Commercial Pipe"), Type ("Pipe"), SubType ("Undefined"), Elevation, TopElevation, BottomElevation, LockSize (False), InsulationThickness, Layer, Handle.
- A 4 in pipe drawn at Z 120 read Elevation 120.0, TopElevation 122.25, BottomElevation 117.75. So Elevation is the centerline and Top/Bottom are centerline plus or minus half the OD. (numbers verified; reading is inference)
- `StyleName` raises E_NOTIMPL on AecbDbPipe, though the help lists it. (VERIFIED; CHM:buildingauto-reference/HTML_idh_abs_object_aecbpipe)
- Fittings (AecbDbPipeFitting): PartDescription ("Glued - Sch 40 - PVC Elbow"), SizeName ("4.00 Inch Glued - Sch 40 - PVC Elbow 90.0 Deg"), SystemName.
- Full member lists: (TLB:AecbXPipeBase89). Help object pages: AecbPipe, AecbPipeFitting, AecbMvPart and AecbConnector in the building API help (CHM:buildingauto-reference).

### Changing pipes (VERIFIED)
| Write | Result |
|---|---|
| `Elevation = 132.0` | Moves the whole pipe. It lost its connection to the elbow (ConnectedMembers None at both ends; Graphs.Count read 2 afterward). Setting 120.0 again put it back: Graphs.Count read 1. |
| `InsulationThickness = 1.0` | Works |
| `StartPoint`, `EndPoint` = VT_R8 array | Works; Length follows (start moved 24 in: 237.3 became 261.3). A plain tuple gives E_INVALIDARG. |
| `Break(point)`, point as VT_R8 array | Splits the pipe; returns the new object's id (a large integer); ModelSpace count goes up by 1. A plain tuple gives E_ABORT. |
| `SystemName = "CHWS (CHWS)"` | Works. `"CHWS"` alone gives E_FAIL. `"Standard"` works as typed and reads back "Standard". |
| `Layer = "M-CHWS"` | Works, as on any AutoCAD entity (layer made first with `Layers.Add`). |
- [AUTO] Wait for idle after each write before the next call (the probes allow 30 s).
- (inference) Moving a pipe end with StartPoint/EndPoint or Elevation can break its joint; re-read ConnectedMembers or Graphs after edits.

### Connectors and graphs (VERIFIED)
- `Connectors.Count` reports 3 on a straight pipe and on an elbow, but only connectors 0 and 1 are real.
- Two test runs disagreed. One recorded that Item(2) raises. The other shows `Item(2)` returning an object whose `Location` and `WidthorDiameter` raise E_FAIL while `Direction` repeats connector 0. Either way: loop to Count - 1 inside try, and keep only connectors that return a Location.
- Connector values read: Location, Direction (unit vector), ConnectionType ("Undefined_Connection_Type" on Glued PVC), WidthorDiameter (4.0), ConnectedMembers (tuple of the connected objects, or None when the end is open). Other members: (CHM:buildingauto-reference/HTML_idh_abs_object_aecbconnector).
- [AUTO] `AecbDatabase.Graphs` (after Init) holds one graph per connected network. `graph.Count` and `graph.Item(k)` list its members, pipes and fittings. After the Break the run was one graph of 4 (pipe, elbow, pipe, pipe).
- `graph.Iterator` gives DISP_E_UNKNOWNNAME by name over IDispatch, though the help lists Iterator on AecbGraph and Step, Stop, Done, Start on AecbGraphIterator. Use Count and Item. (VERIFIED; CHM:buildingauto-reference/HTML_idh_abs_object_aecbgraph, HTML_idh_abs_object_aecbgraphiterator)

### Undocumented helpers in the type libraries (NOT tested)
- `AecX.AecbGuiSize.8.9`: GetSizeListFromRoutingPreference, SizeExistsInRoutingPreference, GetBendAngles.
- `AecX.AecbGuiModify.8.9`: Modify, Modify2, Modify3 (resize objects by ObjectIds), GetElbowList, GetCutLengths.
- `AecX.AecbPartQuery.8.9`: catalog query by Domain, Type, SubType and parameters.
- `AecX.AecbDuctInstantSizing.8.9`.
- They are internal UI helpers (TLB:AecbXGuiBldSrv89, TLB:AecbXUIBldSrv89). Test on a scratch copy before relying on them. (test notes)

### MEP drawing dictionaries seen (VERIFIED)
The probe printed the first 60 AEC and AECB keys of the named object dictionary in the routing preference library drawing:
- AEC_: AEC_PROPERTY_SET_DEFS, AEC_PROPERTY_FORMAT_DEFS, AEC_SCHEDULE_TABLE_STYLES, AEC_LIST_DEFINITIONS, AEC_LAYERKEY_STYLES, AEC_MVBLOCK_DEFS, AEC_CLASSIFICATION_SYSTEM_DEFS, AEC_DISP_REP_CONFIGURATIONS, AEC_DISP_REP_SETS, AEC_DISP_REPS, AEC_DISPLAY_PROPS_DEFAULTS, AEC_DISPLAYTHEME_STYLES, AEC_MATERIAL_DEFS, AEC_PROFILE_DEFS, AEC_VARS, plus the architectural style dictionaries (walls, doors, windows, slabs, stairs, spaces, zones).
- AECB_ (list cut off at 60): AECB_CABLETARY_RISEDROP_STYLES (spelled that way), AECB_CABLETRAY_PARTCATPREF_STYLES, AECB_CABLETRAY_STYLES, AECB_CIRCUITS, AECB_CONDUIT_PARTCATPREF_STYLES, AECB_CONDUIT_RISEDROP_STYLES, AECB_CONDUIT_STYLES, AECB_CONNECTOR_STYLES, AECB_DEMAND_FACTOR_STYLES, AECB_DEVICE_STYLES, AECB_DEVICECATEGORYDEFS, AECB_DUCT_PARTCATPREF_STYLES.
- Read directly: `AECB_PIPE_PARTROUTINGPREFERENCES_STYLES` (routing preferences), `AECB_PIPESYSTEMDEFS` (pipe systems).
- [AUTO] List every key: `(foreach p (entget (namedobjdict)) (if (= (car p) 3) (write-line (cdr p) f)))` inside the 12.2 file pattern.

## 12.4 Property set and schedule API

### Verified
- `sa = GetInterfaceObject("AecX.AecScheduleApplication.8.9")`, then `sa.PropertySetDefs(doc.Database)` returned 5 definitions in the routing preference drawing: PipeFittingElbowStyles, PipeStyles, SpaceEngineeringObjects, ThermalProperties, ZoneEngineeringObjects. VERIFIED
- `sa.PropertySets(pipe)` returned Count 0 on a new pipe. VERIFIED
- Nothing else in this API was tested.

### Object map (help pages, CHM:scheduleauto-reference)
| Object | Create using | Access via | Members to know |
|---|---|---|---|
| AecScheduleApplication | VBA `New AecScheduleApplication`; VB `GetInterfaceObject("AecX.AecScheduleApplication")` (use `.8.9` here, 12.3) | N/A | PropertySetDefs(AcadDatabase), PropertySets(AcadObject) |
| AecSchedulePropertySetDefs | N/A | `app.PropertySetDefs(db)` | Add, Has, Item, Remove, Count |
| AecSchedulePropertySetDef | N/A on the page; `Defs.Add(Name)` in the TLB | `Defs.Item` | Name, AlternateName, Description, AppliesTo, StyleBased, Visible, Writeable, PropertyDefs |
| AecSchedulePropertyDefs | N/A | `PSD.PropertyDefs` | Add, Item, Remove, Count, Owner |
| AecSchedulePropertyDef | N/A | `PropertyDefs.Item` | Name, Type, Default, Format, Automatic, QueryExpression, Index, Description |
| AecSchedulePropertySets | N/A | `app.PropertySets(obj)` | Add, Item, Remove, Count, Owner |
| AecSchedulePropertySet | N/A | `Sets.Item` | Name, AlternateName, Description, Properties, Visible, Writeable |
| AecScheduleProperties | N/A | `PropertySet.Properties` | Item, Count, Owner |
| AecScheduleProperty | N/A | `Properties.Item` | Name, Value, Automatic, Index |
| AecScheduleTable | `ModelSpace.AddCustomObject("AecScheduleTable")` | ModelSpace, PaperSpace, Block, SelectionSet or Group `.Item` | Style, StyleName, Location, ScaleFactor, Direction, AutoUpdate, AddNewAutomatically, LayerWildcard, ScanXrefs, ScanBlockRefs, ExternalDrawing, ScheduleExternalDrawing, RepeatHeaders, RepeatTitle, MaximumHeight, ManualHeights, Spacing; AttachAnchor, GetAnchor, ReleaseAnchor, Update, plus the usual entity edit methods |
| AecScheduleTableStyles | N/A | `AecScheduleDatabase.ScheduleTableStyles` | Add, Has, Item, Remove, Rename |
| AecScheduleTableStyle | `ScheduleTableStyles.Add("Name")` | `Styles.Item` | Name, AlternateName, Description |
| AecScheduleDatabase | N/A (VBA `New AecScheduleDatabase`) | | `Init(AcadDatabase)` (TLB), ScheduleTableStyles, Preferences |
| AecAnchorTagToEnt, AecAnchorExtendedTagToEnt | `New ...` | `AecGeo.GetAnchor` | `AttachEntity(entity)` attaches a schedule tag to an AEC object; ForceHorizontal (extended one only) |
- AecScheduleDatabasePreferences (`AecScheduleDatabase.Preferences`, has Init) holds many of the drawing setup options (the old ADT Format menu, Drawing Setup) and can set ADT system variables. (CHM:scheduleauto-reference/html_idh_object_aecscheduledatabasepreferences)
- Exact members and signatures: (TLB:AecXSchedule89). In it, Add exists on PropertySetDefs `Add(Name)`, PropertyDefs `Add(Name)`, ScheduleTableStyles `Add(Name)`, and PropertySets `Add(PropertySetDef)` (attaches a definition to the object).

### Rules stated on the pages
- A property set definition is a group of property definitions applied to chosen object types or object styles. `AppliesTo` is a Variant array of strings, read-write: the object types it applies to. (CHM: html_idh_object_aecschedulepropertysetdef, html_idh_property_appliesto)
- `StyleBased` says whether the set belongs on styles rather than objects. (inference from the name and the sample's "Style-based" label)
- PropertyDefs: read existing definitions or add new ones. PropertyDef: read and update existing definitions, or define a new one.
- `PropertyDef.Type` (AecSchedulePropertyDefType, read-write): 0 Integer, 1 Real, 2 Text, 3 True/False, 4 Auto increment.
- PropertySet: read-only itself, but existing property sets can be added to objects.
- Property: schedule properties can be updated when they are not set automatically (so properties with Automatic = True are computed; inference)
- AecScheduleTableDirection (page overflow): 0 Right, 1 Down. The page labels value 1 "aecSchedulePropertyTypeReal", a doc error; its description says Down.
- The anchor tag objects are available only when the drawing holds at least one MVBlock style.
- The PropertySetDefs method page names its argument AcadDatabase but describes it as "The object with property sets attached"; the collection page writes `PropertySetDefs(AcadObject)`. The VBA samples and the live test pass the drawing's Database. (CHM; VERIFIED)
- Mirror and other read-write methods cannot run while you iterate a collection (the iteration holds it open for read). Finish the loop first. TransformBy returns an error if the matrix is not a valid transformation. (CHM: html_idh_method_mirror, html_idh_method_transformby)

### Untested sequence (inference from the TLB and the pages; try on a scratch copy)
```
psd = sa.PropertySetDefs(db).Item("<set name>")    # must apply to this object type, not style-based
sa.PropertySets(obj).Add(psd)
ps  = sa.PropertySets(obj).Item(0)
ps.Properties.Item("<property name>").Value = "X"  # only works when Automatic is False
```

## 12.5 ActiveX object model: documents, collections, arrays, Utility

### Shape of the model
- Root = Application. Kinds of objects: graphical (lines, arcs, text, dimensions), style (linetypes, dim styles), organizational (layers, groups, blocks), display (views, viewports), and the drawing and application themselves. ([G:68D6EFA7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-68D6EFA7-ED2D-482C-BBA6-EB22F2854348))
- Application: `Preferences` = Options dialog settings stored in the registry; name, version, window size and position, visibility; load, unload and list ObjectARX apps; quit; `Documents`, `MenuBar`, `MenuGroups`; `VBE` (AutoCAD only). ([G:B8D2A641](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B8D2A641-4D52-4EE0-A0E6-12B1DA43D77F), [G:9091E614](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9091E614-25B8-452E-A67A-301939B52161))
- Document = one drawing. `ModelSpace` and `PaperSpace` hold graphical objects; like-named collections (Layers, Linetypes, TextStyles ...) hold the rest; also `Plot`, `Utility`, `SummaryInfo`, `DatabasePreferences` (options stored in the drawing). ([G:A5144865](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A5144865-30BA-40C5-9BC2-9FD6F366A5C5), [G:EC28388C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC28388C-2D1D-4262-B4AC-CE3C2D8E4FDF))
- Collections: Documents, ModelSpace, PaperSpace (entities of the ACTIVE paper layout only), Block, Blocks, Dictionaries, DimStyles, Groups, Hyperlinks, Layers, Layouts, Linetypes, Materials, MenuBar, MenuGroups, PlotConfigurations, PopupMenus, RegisteredApplications, SelectionSets, TextStyles, Toolbars, UCSs, Views, Viewports, FileDependencies. ([G:A73AB626](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A73AB626-5DAF-4F03-936A-655F772263E0), [G:B81C818A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B81C818A-B50C-48B0-A8F1-3DA65C6E41B3))
- Documents, MenuBar and MenuGroups come from the Application; the others are properties of the Document. ([G:7B31FE08](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7B31FE08-D868-49B7-8BE1-41A160EE6D58))
- 2027 migration: remove references to IAcadFileDependency and IAcadFileDependencies. ([G:E69C877D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E69C877D-F84B-4282-807D-E084C931D533))

### Collection rules
- Common members: `Add` (entities use `Add<Entityname>`), `Count`, `Item`. ([G:589F246A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-589F246A-41BE-4D38-AA91-9FDA3ABABEA6))
- [AUTO] `Item(identifier)` takes a zero-based index or a name string; Item is the default member, so VBA `Layers("ABC")` = `Layers.Item("ABC")`. ([G:05AC034B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-05AC034B-3E51-4EC3-85BE-B3153B8CC40B))
- [AUTO] Item with a name that does not exist RAISES an error. Wrap it (Python try; LISP `(vl-catch-all-apply 'vla-Item (list coll "Name"))` then `vl-catch-all-error-p`). ([G:05AC034B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-05AC034B-3E51-4EC3-85BE-B3153B8CC40B)) The MEP collections also have `Has(name)`. (TLB:AecbXPipeBase89)
- Add a member with the collection's Add: `Layers.Add("MyNewLayer")` returns the new layer. ([G:E7D4B944](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E7D4B944-5C97-4B31-83C8-FDD424A0E11D))
- Delete with the MEMBER's Delete: `Layers.Item("ABC").Delete()`. Never touch that object again afterward. ([G:8527D1AF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8527D1AF-8167-4D8B-9562-B698D3296647)) A View is deleted with `View.Delete`, not through Views. ([G:3371E240](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3371E240-8B1C-4EB8-91A2-AC27EE6960A9))
- [AUTO] Do not call edit methods (Copy, Array, Mirror ...) on members while looping a collection with For Each. Finish the loop, or copy the members into a list and edit from that. ([G:05AC034B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-05AC034B-3E51-4EC3-85BE-B3153B8CC40B)) Adding or removing members while iterating can raise an error. ([G:100F8BDB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-100F8BDB-2852-4986-BC09-53F77AFCDB96))
- Any drawing object can be held as AcadEntity; `ObjectName` gives its class name ("AcDbPolyline", "AcDbMText", "AcDbArc", "AecbDbPipe"). First model space object = `ModelSpace.Item(0)`; check Count > 0 first. ([G:D4FF317D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D4FF317D-16DA-42D8-8309-8260B7427E55), [G:4805C525](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4805C525-0E7F-4407-A473-D83ECAF1A940); VERIFIED for AecbDbPipe)

### Variants and arrays
- Arrays go in and out of ActiveX as Variants. A Variant can also be Empty, Error, Nothing or Null. VBA converts input arrays; output arrays always come back as Variants. ([G:F6B0A90B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F6B0A90B-B484-4B2E-A0E1-FE6B7441ADBC), [G:FD389E86](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FD389E86-030B-414D-B3EE-64A13DF2BC12))
- `Utility.CreateTypedArray(outVar, type, v1, v2, ...)` builds a typed Variant array, e.g. fit points for `AddSpline(fitPoints, startTan, endTan)`. LISP: `(vla-CreateTypedArray util 'fitPoints vlax-vbDouble 0 0 0 5 5 0 10 0 0)`. ([G:5004997B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5004997B-3086-4D07-A0A1-AEB32B7727A2))
- From Python, build typed arrays with `win32com.client.VARIANT(...)` (12.1). VERIFIED for 3D points.
- `AddLightWeightPolyline` takes one flat Double array of 2D vertices x0,y0,x1,y1,...; `SnapBasePoint` takes 2 doubles. ([G:5DE8E17F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5DE8E17F-6B23-4D99-9CA5-75ADB79465F5), [G:BA4EDDE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BA4EDDE0-EA74-434F-8FC8-FCDB292AC39D))

### Documents ([G:EF30D5C5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF30D5C5-6A02-48FE-82C9-14E0EAEAFB79); signatures TLB:acax26enu)
- [AUTO] `Documents.Open(Name, [ReadOnly], [Password])` opens a DWG and makes it active.
- [AUTO] `Documents.Add([TemplateName])` makes a new drawing, e.g. `Add("acad.dwt")`.
- `Documents.Close()` closes EVERY open drawing in the session.
- [AUTO] Document: `Save()`, `SaveAs(FullFileName, [SaveAsType], [SecurityParams])`, `Close([SaveChanges], [FileName])`, `Activate()`, `Saved` (False = unsaved changes), `ReadOnly`, `FullName`, `Path`, `Name`, `Database`.
- SaveAsType values: ac2018_dwg = acNative = 64, ac2013_dwg 60, ac2010_dwg 48, ac2007_dwg 36, ac2004_dwg 24, ac2000_dwg 12. From 2000 on, the DXF type is the DWG value + 1 and the template + 2 (2018: 64, 65, 66). (TLB:acax26enu)
- Check that the file exists before Open (VBA `Dir`, LISP `findfile`). ([G:EF30D5C5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF30D5C5-6A02-48FE-82C9-14E0EAEAFB79))
- The SaveAs sample passes a bare file name ("MyDrawing.dwg"). Pass a full path. (inference)
- [AUTO] Routine used by the probes (VERIFIED): copy the source DWG to a scratch folder, Open the copy, work, `SaveAs(new_path)`, wait for idle, `Close(False)`. Never edit library drawings in place. (inference)
- [AUTO] `StartUndoMark()` and `EndUndoMark()` mark the start and end of a block of operations. (TLB:acax26enu; not tested)
- Other Document methods: `HandleToObject(handle)`, `ObjectIdToObject(id)`, `PurgeAll()`, `AuditInfo(FixErr)`, `Wblock(FileName, SelectionSet)`, `CopyObjects(Objects, [Owner], [IdPairs])` (deep clone), `LoadShapeFile(name)`. (TLB:acax26enu)
- Programs that assign a drawing password must be changed for 2027. ([G:E69C877D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E69C877D-F84B-4282-807D-E084C931D533))

### Display refresh
- Not every ActiveX change repaints, by design. `obj.Update()` redraws that one object. `Document.Regen(which)` regenerates the whole drawing, recomputes screen coordinates and view resolution, and reindexes the database. Batch the edits, then refresh once. ([G:8D9140F0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8D9140F0-3676-41D7-B618-27D94AB9DE7E))
- Regen argument: acActiveViewport 0, acAllViewports 1. (TLB:acax26enu) The samples pass False and True. ([G:9DCF17E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9DCF17E7-717B-4766-AFFE-D3C9ED506BB8))
- Active layer and linetype changes show at once. Changes to the active text style, active UCS and active viewport do NOT: assign the object back, `doc.ActiveViewport = doc.ActiveViewport` (sample), or `doc.ActiveTextStyle = ts`, `doc.ActiveUCS = ucs`. The page also says to call Regen; its sample does not. ([G:F8F39BA9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F8F39BA9-558C-4EE6-847C-C09EBA66B321))

### System variables and options
- [AUTO] `Document.SetVariable(name, value)` and `Document.GetVariable(name)`. Sample: `SetVariable "MAXSORT", 100`. They also reach settings not in the Options dialog. ([G:AE8193CC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AE8193CC-CEAE-4B0A-BC38-808742B1750C), [G:9091E614](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9091E614-25B8-452E-A67A-301939B52161))
- (inference) Pass the Variant type the variable expects (int for integer variables, float for real ones); LISP `setvar` with a wrong type raises an error. ([G:529819FD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-529819FD-9E9C-4789-BA18-B981BA32DD23))
- `Preferences`: 9 objects, one per Options tab, stored in the registry: Display, Drafting, Files, OpenSave, Output, Profile (object PreferencesProfiles), Selection, System, User. Samples: `Preferences.Display.CursorSize = 100`, `Preferences.Display.DisplayScrollBars = False`, `Preferences.Files.TempFilePath`. AutoCAD LT has no profile members. ([G:EC28388C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC28388C-2D1D-4262-B4AC-CE3C2D8E4FDF), [G:86F7BD62](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-86F7BD62-D51C-49FF-B0C8-AC5AB6FEAC80))
- `DatabasePreferences` = options saved in the drawing; ObjectDBX programs can read them without AutoCAD running. ([G:EC28388C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC28388C-2D1D-4262-B4AC-CE3C2D8E4FDF))
- `Preferences.SetProjectFilePath` sets the project search paths used to find missing raster images. ([G:4F957B32](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4F957B32-EF14-4E07-A9B8-83D06344C356))
- A program that declares an interface new in one AutoCAD version must not be used with earlier versions. ([G:110B7176](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-110B7176-A9C0-4743-A340-AA80E07A27F5))

### Export and Import
- [AUTO] `Document.Export(FileName, Extension, SelectionSet)`: formats WMF, SAT, EPS, DXF, BMP. Give the name WITHOUT extension and the extension as the second argument (`Export(TempFilePath & "DXFExport", "DXF", ss)` writes DXFExport.dxf). ([G:605EBB90](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-605EBB90-D3A8-4150-9BFC-F321B1316948))
- WMF, SAT and BMP need a NON-EMPTY selection set; an empty one raises a trappable "invalid argument" error. EPS and DXF export the whole drawing and ignore the set, but the argument is still REQUIRED (leaving it out is a syntax error). ([G:605EBB90](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-605EBB90-D3A8-4150-9BFC-F321B1316948))
- The sample makes a throwaway set `SelectionSets.Add("NEWSSET")` and deletes it after. A set left over from a crashed run makes the next Add with that name fail; use unique names or delete leftovers first. ([G:605EBB90](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-605EBB90-D3A8-4150-9BFC-F321B1316948); inference)
- [AUTO] `Document.Import(FileName, InsertionPoint, ScaleFactor)`: DXF, SAT, WMF (the type library text also names EPS). File name includes the extension; insertion point is a 3-double array. ([G:F51F1C9E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F51F1C9E-D750-423B-9462-EA1CB2E98E55); TLB:acax26enu)

### Utility object
- `doc.Utility`. Its input methods print a prompt and WAIT for a person: GetString(hasSpaces, prompt), GetPoint([fromPoint], prompt), GetInteger, GetReal, GetDistance, GetAngle, GetOrientation, GetCorner, GetKeyword(prompt), GetInput. Never use them in an unattended run. ([G:2F1938FE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2F1938FE-DE63-456B-9C29-612DA4539EB0), [G:9111F796](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9111F796-1331-48E2-BA27-EE5DA7FD8E46), [G:B6F21049](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B6F21049-4C5D-4895-99CD-CD0FAC7E5D54), [G:5D322A2D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5D322A2D-3BC9-44F4-AFFD-C5770A357858))
- `InitializeUserInput(bits, "Kw1 Kw2")` sets rules for the next Get* call (not GetString). Bit 1 = no empty input. A keyword or a bare Enter at GetInteger raises an error (VBA Err.Number -2145320928); read the text with GetInput. ([G:1E17B5E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1E17B5E6-92FC-433C-97B7-760A0BEB73AC))
- Helpers that do not prompt: AngleFromXAxis, AngleToReal, AngleToString, DistanceToReal, PolarPoint, TranslateCoordinates, CreateTypedArray. ([G:D60D53D7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D60D53D7-5692-465B-BCEC-5090FF7F2027))

### Limits of ActiveX geometry
- No method sets object snaps, measures intervals or divides objects. ([G:A8CD0FE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A8CD0FE0-9D03-42F3-8A20-EAC331FF3499))
- `Area` exists on arc, circle, ellipse, lightweight polyline, polyline, region and planar closed spline. Combine areas by adding them up, or merge regions with the region Boolean method and read one Area. ([G:A8CD0FE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A8CD0FE0-9D03-42F3-8A20-EAC331FF3499), [G:07538761](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-07538761-7F5B-45E5-916C-F71510CB3788))
- Ortho is ignored for typed coordinates and object snaps, so it never changes script-fed points. ([G:E16359AE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E16359AE-88A0-4FA6-87CA-66510937DFA4))
- `AddXLine(point1, point2)` (first point = root) and `AddRay(base, second)` are infinite. Extents commands ignore them. Read `BasePoint` and `DirectionVector` (writable); the second creation point is not stored. ([G:39A4106D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-39A4106D-AE1A-4073-B973-92554E95FDF3), [G:379063FE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-379063FE-D9B0-488C-ABE3-E0CFC22B6FF5), [G:0D5E3D38](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0D5E3D38-71C1-4F94-8865-DB15EC677C25))

## 12.6 Entities, blocks, attributes, xrefs, raster, xdata, selection sets over COM

### Creating and editing entities
- Graphical objects are made with `Add<Entityname>` on ModelSpace, PaperSpace or a Block: AddLine(p1, p2), AddCircle(center, radius), AddLightWeightPolyline(flat 2D array), AddSpline, AddXLine, AddRay, AddRaster, InsertBlock, AttachExternalReference; AddPViewport in paper space. ([G:647C6D1B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-647C6D1B-AB3D-4D8E-83EC-3AF96584DC67) and the pages below)
- Common entity methods: Copy, Delete, Move, Mirror, Rotate, ScaleEntity, ArrayPolar, ArrayRectangular, GetBoundingBox, Highlight, Update, GetXData, SetXData. Common properties: Layer, Linetype, TrueColor, Handle, ObjectName; plus type ones such as Center, Radius, Area. ([G:647C6D1B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-647C6D1B-AB3D-4D8E-83EC-3AF96584DC67))
- `Offset` exists only on a few classes (Arc, Circle, Ellipse, Line); Mirror and Move apply to most objects. ([G:D9ED98F3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D9ED98F3-69E4-43AD-AAF5-D6B5B3A086D2))
- Non-graphical objects (Layers, Linetypes, DimStyles, SelectionSets ...) come from the collection's `Add`; each deletes itself with Delete. ([G:647C6D1B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-647C6D1B-AB3D-4D8E-83EC-3AF96584DC67))
- `GetBoundingBox` on an infinite object (Ray) fails with "Automation Error. Invalid extents". ([G:9205DA3B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9205DA3B-9186-48C7-A477-E4C8FF88E1BB))
- [AUTO] `ent.IntersectWith(otherEnt, option)` returns the intersection points as a flat Variant array of doubles; nothing comes back if they do not meet. Options: acExtendNone 0, acExtendThisEntity 1, acExtendOtherEntity 2, acExtendBoth 3 (the remarks call the last one "acExtendBothEntities"). (CHM:scheduleauto-reference/html_idh_method_intersectwith; values TLB:acax26enu)

### Blocks
- [AUTO] `Blocks.Add(InsertionPoint, Name)` makes a definition; add geometry to it, e.g. `block.AddCircle(center, radius)`. ([G:888C0CC5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-888C0CC5-AE4B-4BE4-BF34-B2A3A9DC38A9))
- [AUTO] `space.InsertBlock(InsertionPoint, Name, XScale, YScale, ZScale, Rotation)` returns the block reference. Name is a block name or a DWG path. The page does not state the rotation unit (inference: radians, like other ActiveX angles such as SnapRotationAngle, [G:BA4EDDE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BA4EDDE0-EA74-434F-8FC8-FCDB292AC39D)). ([G:0A650525](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A650525-85E8-4462-9F46-A1DD18A998F6))
- An inserted DWG becomes an ordinary block named after the file (rename with `Name`). Later edits to the source DWG do NOT flow in; reinsert it with InsertBlock to redefine. Its paper space objects are NOT part of the block. Base point is 0,0,0 unless INSBASE was set in the source drawing. The file's WCS is laid parallel to the CURRENT UCS. ([G:0A650525](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A650525-85E8-4462-9F46-A1DD18A998F6))
- `AddMInsertBlock` inserts an array of a block and returns an MInsertBlock. ([G:0A650525](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A650525-85E8-4462-9F46-A1DD18A998F6))
- A block reference cannot be iterated for its parts: iterate the Block definition, or `Explode` it (returns a Variant array of the new objects). ([G:0A650525](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A650525-85E8-4462-9F46-A1DD18A998F6), [G:77744360](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-77744360-91AB-4289-8287-7F861522A0DF))
- Redefine by changing the Block object: every reference updates (call `Update`). Constant attributes are replaced by the new ones; variable attributes stay. ([G:B213D3A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B213D3A9-AABE-44E1-BDCB-29166BB7BF91))
- `WBlock` writes objects to a new DWG. ([G:888C0CC5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-888C0CC5-AE4B-4BE4-BF34-B2A3A9DC38A9))

### Attributes
- [AUTO] `block.AddAttribute(Height, Mode, Prompt, InsertionPoint, Tag, Value)`. ([G:906149DF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-906149DF-53E2-49F3-AC61-A79721C2C76E))
- Mode values, added together: acAttributeModeNormal 0, Invisible 1, Constant 2, Verify 4, Preset 8 (the type library adds LockPosition 16, MultipleLine 32). ([G:906149DF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-906149DF-53E2-49F3-AC61-A79721C2C76E); values TLB:acax26enu)
- Tag: no spaces or "!"; lowercase is made uppercase. The page's own samples use tags with spaces; do not copy them. ([G:906149DF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-906149DF-53E2-49F3-AC61-A79721C2C76E))
- A definition belongs to the block it was added to; one made straight in model or paper space belongs to no block. ([G:906149DF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-906149DF-53E2-49F3-AC61-A79721C2C76E))
- [AUTO] `blockRef.GetAttributes()` returns the LIVE attribute references (TagString, TextString). There is no SetAttributes: set `TextString` on an element and the drawing changes. `GetConstantAttributes()` returns the constant DEFINITIONS. ([G:C34E2AE8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C34E2AE8-A2D0-4781-8B5B-BC3E226E8B94))
- Edit a definition through Alignment, Backward, FieldLength, Height, InsertionPoint, Mode, PromptString, Rotation, ScaleFactor, TagString, then `Update`. ([G:78E5448F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-78E5448F-F0DA-47FB-876E-3EA911F9FB91))
- Invisible attributes are stored but not shown or plotted; the ATTDISP command overrides that. ([G:2133E7A1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2133E7A1-44FA-4F69-A79D-1220B889CA06), [G:906149DF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-906149DF-53E2-49F3-AC61-A79721C2C76E))

### External references
- [AUTO] `space.AttachExternalReference(PathName, Name, InsertionPoint, XScale, YScale, ZScale, Rotation, Overlay)` returns an ExternalReference. The sample path uses forward slashes. The xref also appears as a Block definition. ([G:3472CC4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3472CC4B-99CB-4242-9D6D-AC4F9E36E195))
- `Overlay = True` makes an overlay: when this drawing is itself attached somewhere, its overlays are not read in. ([G:6AD94981](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6AD94981-F99D-4566-84E5-B514A68AB6D9))
- [AUTO] Bind, Detach, Reload and Unload are methods of the xref's Block definition: `Blocks.Item(xref.Name).Bind(bPrefixName)`, `.Detach()`, `.Reload()`, `.Unload()`. ([G:288FF849](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-288FF849-9398-4B6B-A87E-13D03BE25B42), [G:FC86754D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FC86754D-B783-4204-8BAB-7AA092EF6CAC), [G:02993703](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-02993703-273F-4ACC-BDA0-834D5BA4BFB5), [G:9BA45055](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9BA45055-D4D8-4E3E-B292-DB6F15D4691E))
- `Bind(True)` renames dependent symbols `<blockname>$x$<name>` so nothing is overwritten; `Bind(False)` merges names and keeps the host's symbol on a duplicate. ([G:288FF849](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-288FF849-9398-4B6B-A87E-13D03BE25B42))
- Detach removes the definition, every instance and the dependent symbols. A nested xref cannot be detached. If every instance is erased, the definition goes at the next open. ([G:FC86754D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FC86754D-B783-4204-8BAB-7AA092EF6CAC))
- No ActiveX clip method: use XCLIP through SendCommand. ([G:577D96C5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-577D96C5-9B22-4771-87DD-38D32ACF9F09))
- Demand loading: `XRefDemandLoad` property (owning object not named on the page): acDemandLoadDisabled 0, acDemandLoadEnabled 1, acDemandLoadEnabledWithCopy 2 (loads a temporary copy so others can edit the source). Set `INDEXCTL` in the SOURCE drawings: 0 none (new drawings), 1 layer index, 2 spatial index, 3 both. XLOADCTL is the matching system variable. ([G:31577C7F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31577C7F-55C4-4137-9D05-3F6C0F18DA79); values TLB:acax26enu)
- VISRETAIN on keeps xref-dependent layer changes in the host. AutoCAD reloads every xref on open and on plot. ([G:3472CC4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3472CC4B-99CB-4242-9D6D-AC4F9E36E195), [G:5695F327](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5695F327-F7B2-4E31-9AC5-02B15E23F959))
- A block (not an xref) stores the geometry in the host and never follows the source; an xref cannot be exploded. ([G:1D1A4F18](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1D1A4F18-4CEB-49EB-8139-BBE883D47981))

### Raster images
- [AUTO] `space.AddRaster(ImageFileName, InsertionPoint, ScaleFactor, RotationAngle)` returns a RasterImage. The image is linked, not stored. A missing file raises an error. ([G:8B77C386](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8B77C386-4AFD-4266-95A8-D1DF59B4EF31))
- Default scale: 1 image unit = 1 drawing unit. Scanned 1 in = 50 ft (1:600) blueprint in an inch drawing: ScaleFactor 600. No DPI in the file: width in drawing units = ScaleFactor. ([G:8B77C386](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8B77C386-4AFD-4266-95A8-D1DF59B4EF31))
- Clip: `ClippingEnabled = True`, then `ClipBoundary(points)` with a flat array of 2D WCS points, first point repeated at the end, every vertex inside the image; then `Regen(acActiveViewport)`. ([G:68230A95](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-68230A95-1159-4EDF-A5AF-F110A18BD6D1), [G:AD786012](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AD786012-0C11-4267-896C-526960470A10), [G:20C47CE4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-20C47CE4-A25A-49A5-AE58-AD4C6B8D93E2))
- `ImageFile` = the path AutoCAD loads. If not found there, AutoCAD strips the path and searches the project paths (`Preferences.SetProjectFilePath`). `Name` renames the image only, not the file. ([G:4F957B32](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4F957B32-EF14-4E07-A9B8-83D06344C356))
- `Width`, `Height` = pixels; `ImageWidth`, `ImageHeight` = drawing units; `Origin`; `ShowRotation`; `Brightness`, `Contrast`, `Fade` change display and plot only; `Transparency` for bitonal backgrounds; `TrueColor` = bitonal foreground. ([G:9FBD3DD9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9FBD3DD9-DAAC-46ED-A085-126D736B1C73), [G:4C8C08CC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4C8C08CC-CD6E-4998-A0E6-D5EDD66CC8E1), [G:393426D9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-393426D9-A8EA-434C-A258-15B1A4036D76))
- `ImageVisibility = False` hides images (not shown, not plotted) for the session; only the boundary shows. ([G:0B4F60E2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0B4F60E2-CFE3-4DEF-8D08-A841B614CEAC))
- Conflict: one page says `ClippingEnabled` shows or hides image BOUNDARIES for all images in the drawing ([G:7F6138B4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7F6138B4-35E5-439D-B8DA-77BC54A88D0F)); the clip pages use it to turn one image's clipping on or off ([G:68230A95](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-68230A95-1159-4EDF-A5AF-F110A18BD6D1)). Test before relying on either reading.
- 2026 and later: images load in the background after open; run IMAGEASYNCWAIT before editing or plotting. ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))

### Xdata over COM
- [AUTO] `ent.SetXData(types, values)`: two parallel arrays, types as Integers (1001 = application name, 1000 = string ...), values as Variants. `ent.GetXData(appName, typesOut, valuesOut)`; empty types back = no xdata for that application. ([G:A675254F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A675254F-08B2-4048-95CB-DD7195616BC1))
- The page's sample never registers its application name. In LISP the name must be in the APPID table (`regapp`) ([G:8F373105](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8F373105-67D5-4CBD-931D-D0869F2A7EB5)); over COM use `RegisteredApplications.Add(name)` first (inference from the collection list, [G:A73AB626](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A73AB626-5DAF-4F03-936A-655F772263E0)).
- Group codes and size limits: 12.11.

### Selection sets over COM
- [AUTO] `ss = doc.SelectionSets.Add("NAME")` makes an empty set; `SelectionSets.Item("NAME")` fetches it later; `ss.Delete()` when done. Walk it with Count and Item. ([G:A675254F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A675254F-08B2-4048-95CB-DD7195616BC1), [G:605EBB90](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-605EBB90-D3A8-4150-9BFC-F321B1316948))
- `SelectOnScreen` asks the user to pick: never unattended. ([G:A675254F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A675254F-08B2-4048-95CB-DD7195616BC1))
- Members that do not prompt (TLB:acax26enu; not tested here): `Select(Mode, [Point1], [Point2], [FilterType], [FilterData])`, `SelectAtPoint(Point, [FilterType], [FilterData])`, `SelectByPolygon(Mode, PointsList, [FilterType], [FilterData])`, `AddItems(objects)`, `RemoveItems(objects)`, `Clear()`, `Erase()`, `Highlight(flag)`.
- AcSelect Mode: Window 0, Crossing 1, Fence 2, Previous 3, Last 4, All 5, WindowPolygon 6, CrossingPolygon 7. (TLB:acax26enu)
- (inference) FilterType and FilterData are parallel arrays of DXF group codes and values, the same idea as LISP ssget filters (12.11). From Python they must be typed arrays (VT_I2 codes, VT_VARIANT values). Not tested.
- (inference) Add with a name already in use fails: use unique names or delete leftovers first.
- `Document.ActiveSelectionSet` and `Document.PickfirstSelectionSet` also exist. (TLB:acax26enu)
- A simpler verified way to find objects: loop ModelSpace and test ObjectName (12.3), or run `ssget "X"` in LISP and write the handles to a file (12.2, 12.11).

## 12.7 Layouts, viewports, views, zoom and plotting over COM

### Layout model
- All geometry lives in layouts. Model space is the one layout named "Model": it cannot be renamed and there is only one. Paper space layouts: any number, renameable. ([G:10344852](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-10344852-4888-4237-8EB6-5EBE24D5C87C))
- [AUTO] `ModelSpace` = the Model layout's geometry. `PaperSpace` = the LAST ACTIVE paper layout, not a fixed one. For a given layout's geometry use `Layout.Block`. ([G:10344852](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-10344852-4888-4237-8EB6-5EBE24D5C87C), [G:10F797AA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-10F797AA-5032-4298-A2A5-C69449275F0E); route by inference)
- Each Layout has exactly one Block (`Layout.Block`) and that Block one Layout (`Block.Layout`). Layout = plot settings and how the layout looks in the UI; Block = the geometry. ([G:10F797AA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-10F797AA-5032-4298-A2A5-C69449275F0E))
- PlotConfiguration = the same plot settings with no Block: a named set usable with any geometry (PlotConfigurations collection). ([G:7DC14E4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7DC14E4B-5198-428C-9919-F3B814370504))
- Model space plot settings live on `ModelSpace.Layout`. ([G:0366CF9B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0366CF9B-4112-42AD-B6CB-0949022250EA))

### Spaces and floating viewports
- Tiled model viewports are `Viewport` objects (`Document.Viewports`). Floating paper viewports are `PViewport` objects. ([G:E8C0910B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E8C0910B-9DF3-4F18-B04B-293DCCDA801A))
- `ActiveSpace = acModelSpace` (1) equals TILEMODE on; `acPaperSpace` (0) equals TILEMODE off. ([G:4EAB8372](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EAB8372-859A-4C6E-BEE5-B2C8EBA31AD7); values TLB:acax26enu)
- `MSpace = True` = the MSPACE command (work inside a floating viewport); `False` = PSPACE. With a Viewport, ActiveSpace must be acModelSpace; with a PViewport it may be either. ([G:4EAB8372](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EAB8372-859A-4C6E-BEE5-B2C8EBA31AD7))
- [AUTO] At least one PViewport must have Display on before `MSpace = True`, or setting MSpace raises an error. ([G:4EAB8372](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EAB8372-859A-4C6E-BEE5-B2C8EBA31AD7))
- Switches: to the last paper layout, `ActiveSpace = acPaperSpace` then `MSpace = False` ([G:EF299927](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF299927-9413-440E-9FD1-5E8866EBA1FD)); into floating viewports, `ActivePViewport.Display(True)` then `MSpace = True` ([G:C01CFA23](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C01CFA23-F78C-4A93-B633-5AF357C4B5F0)); to tiled viewports, `ActiveSpace = acModelSpace` ([G:33972F54](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33972F54-B030-4EE9-AC29-7E33FD276661)).
- The probes set TILEMODE to 1 right after opening a drawing. VERIFIED (scripts)

### Floating viewport build order ([G:9DCF17E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9DCF17E7-717B-4766-AFFE-D3C9ED506BB8)) [AUTO]
Follow the command-line order:
1. `doc.ActiveSpace = 0` (acPaperSpace).
2. `vp = doc.PaperSpace.AddPViewport(center, width, height)` (center = 3-double array).
3. Set view properties (`Direction`, `LensLength`) while Display is OFF.
4. `vp.Display(True)`: a viewport must be on before it can be made current.
5. `doc.MSpace = True`, then `doc.ActivePViewport = vp`.
6. Zoom: `app.ZoomExtents()`, then `app.ZoomScaled(factor, 2)` (2 = acZoomScaledRelativePSpace).
7. `doc.MSpace = False`.
- Also settable on the viewport: GridOn, Layer, Linetype, LinetypeScale. ([G:9DCF17E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9DCF17E7-717B-4766-AFFE-D3C9ED506BB8))
- Four-view sample: reuse the existing ActivePViewport as the top view; add front `Direction = (0,1,0)`, right `(1,0,0)`, iso `(1,1,1)`; each gets Display on, MSpace True, made active, ZoomExtents, `ZoomScaled 0.5, acZoomScaledRelativePSpace`; end with `Regen True` (all viewports). Model space must hold something to see. ([G:9DCF17E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9DCF17E7-717B-4766-AFFE-D3C9ED506BB8))
- The edit page shows `ThisDrawing.ActiveViewport = MyViewportObject` for making a floating viewport active; the creation samples use `ActivePViewport = vp` after `MSpace = True`. Use the sample form. ([G:F7A6E5C6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F7A6E5C6-2D39-4329-A4C7-7E97E9678801), [G:9DCF17E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9DCF17E7-717B-4766-AFFE-D3C9ED506BB8))
- PViewports can freeze or turn off layers per viewport, turn a viewport's display on or off, align views between viewports, and scale views relative to the layout. ([G:4EAB8372](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EAB8372-859A-4C6E-BEE5-B2C8EBA31AD7))

### Viewport scale and linetypes
- Scale each viewport relative to paper space units, not to the previous view or the full-size model. Factor = paper units / model units; quarter scale (1:4) = 0.25. ([G:D2923334](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D2923334-0F8D-4417-BDA4-F8B3DE27BDDD))
- (inference) Architectural scales in an inch drawing: 1/4" = 1'-0" is 0.25/12 = 1/48; 1/8" = 1'-0" is 1/96.
- The page lists three inputs for ZoomScaled (viewport, factor, basis) but the samples call `ZoomScaled factor, basis` on the current viewport. ([G:D2923334](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D2923334-0F8D-4417-BDA4-F8B3DE27BDDD), [G:9DCF17E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9DCF17E7-717B-4766-AFFE-D3C9ED506BB8))
- `PSLTSCALE` keeps pattern linetype scale uniform in paper space units across viewports of different zoom; it also affects line display in 3D views. Set it with SetVariable. ([G:62CE7A57](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-62CE7A57-2B8E-4D4B-8F25-7D62374B80A7))

### Tiled viewports and named views
- [AUTO] `vp = doc.Viewports.Add("NAME")`; make it current with `doc.ActiveViewport = vp`. ([G:7E989F77](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7E989F77-7073-4284-8AFD-D35F2A77AD3B), [G:1F0D1ED9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1F0D1ED9-2CA1-44DA-B8E5-C346B8112F17))
- `vp.Split(type)`: acViewport2Horizontal 0, 2Vertical 1, 3Left 2, 3Right 3, 3Horizontal 4, 3Vertical 5, 3Above 6, 3Below 7, acViewport4 8. ([G:75D8D986](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-75D8D986-8F90-4C66-856E-C67E702D1310); values TLB:acax26enu)
- Tiles of one configuration share its Name; tell them apart by `LowerLeftCorner` and `UpperRightCorner` (0 to 1 fractions of the screen). Four-way split: VP1 (0,.5)-(.5,1), VP2 (.5,.5)-(1,1), VP3 (0,0)-(.5,.5), VP4 (.5,0)-(1,.5). ([G:75D8D986](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-75D8D986-8F90-4C66-856E-C67E702D1310))
- Points are entered and objects selected only in the current viewport. ([G:1F0D1ED9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1F0D1ED9-2CA1-44DA-B8E5-C346B8112F17))
- [AUTO] Viewport settings `GridOn`, `OrthoOn`, `SnapBasePoint` (2 doubles), `SnapRotationAngle` (radians; 0.5236 = 30 degrees) take effect only after the viewport is assigned back to `doc.ActiveViewport`. ([G:BA4EDDE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BA4EDDE0-EA74-434F-8FC8-FCDB292AC39D), [G:E16359AE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E16359AE-88A0-4FA6-87CA-66510937DFA4), [G:F8F39BA9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F8F39BA9-558C-4EE6-847C-C09EBA66B321))
- [AUTO] `doc.Views.Add("NAME")` saves the current position and scale with the drawing. Names: up to 255 characters, letters, digits, `$`, `-`, `_`. Get with `Views.Item(name)`; delete with `View.Delete()`. ([G:3371E240](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3371E240-8B1C-4EB8-91A2-AC27EE6960A9))

### Zoom (methods of the Application)
- `ZoomAll`: shows the whole drawing (object extents if objects go past the limits, else the limits). In 3D views it equals ZoomExtents. ([G:911F75FD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-911F75FD-2CAF-4F90-90F7-CA502ACD3703))
- `ZoomExtents`: extents of the ACTIVE VIEWPORT, not the current view; limits if the drawing is empty. ([G:911F75FD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-911F75FD-2CAF-4F90-90F7-CA502ACD3703))
- Both may regenerate; frozen or off layers are not regenerated; xlines and rays are ignored. Zooming model space from inside a paper space viewport can hide part of the result. ([G:911F75FD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-911F75FD-2CAF-4F90-90F7-CA502ACD3703))
- `ZoomCenter(center3D, magnification)` (magnification relative to the current view), `ZoomWindow(p1, p2)`, `ZoomPrevious`, `ZoomScaled(scale, type)`: acZoomScaledAbsolute 0 (relative to limits), acZoomScaledRelative 1 (current view), acZoomScaledRelativePSpace 2 (paper units). ([G:5733E1A7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5733E1A7-3D52-4A72-8218-7BC46A31AB5F), [G:47D88346](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-47D88346-A2EB-425B-90A5-E7539BB78E20), [G:DEEBD7BD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DEEBD7BD-FE3A-4C48-81DC-735E6AA2E3AC); values TLB:acax26enu)
- `ZoomPickWindow` makes the user pick two points: never unattended. ([G:6D85F583](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6D85F583-2B0D-4C8B-9E17-0A072EBCB41C))

### Plotting
- With nothing set, a model space plot goes to the system printer, plots the current display, scaled to fit, rotation 0, offset 0,0. ([G:0366CF9B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0366CF9B-4112-42AD-B6CB-0949022250EA))
- [AUTO] Help sequence: if `ActiveSpace = acPaperSpace`, set `MSpace = True` and `ActiveSpace = acModelSpace`; then `ModelSpace.Layout.PlotType = acExtents`, `ModelSpace.Layout.StandardScale = acScaleToFit`, `Plot.NumberOfCopies = 1`, `Plot.PlotToDevice`. ([G:0366CF9B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0366CF9B-4112-42AD-B6CB-0949022250EA))
- [AUTO] `BACKGROUNDPLOT` must be 0 before a script can plot several jobs. ([G:FD585AB3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FD585AB3-A5E2-4E2B-8713-B87FD0F59C17))
- Plot object (`doc.Plot`): `PlotToFile(plotFile, [plotConfig])` and `PlotToDevice([plotConfig])` return Boolean; a PC3 passed to PlotToDevice overrides ConfigName; `SetLayoutsToPlot(layoutList)`; `StartBatchMode(entryCount)`; `BatchPlotProgress`; `NumberOfCopies`; `QuietErrorMode` (quiet plot error reporting); `DisplayPlotPreview(mode)` opens a dialog. ([G:FD585AB3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FD585AB3-A5E2-4E2B-8713-B87FD0F59C17), [G:0366CF9B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0366CF9B-4112-42AD-B6CB-0949022250EA); signatures TLB:acax26enu)

| Setting (Layout or PlotConfiguration) | Member | Values and rules |
|---|---|---|
| Device | `ConfigName` | Any valid device name; unset = system default device ([G:B2F56BD0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B2F56BD0-8219-4BA5-9CA5-0740B56C7FA2)) |
| Paper | `CanonicalMediaName` | Sizes come from the device ([G:16AB5D5E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-16AB5D5E-CC71-4A24-8B9F-D78C6D191D3B)) |
| Units | `PaperUnits` | acInches 0, acMillimeters 1, acPixels 2 (raster devices need pixels) ([G:16AB5D5E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-16AB5D5E-CC71-4A24-8B9F-D78C6D191D3B)) |
| Area | `PlotType` | acDisplay 0 (not from a paper layout), acExtents 1, acLimits 2, acView 3 (+ `ViewToPlot`), acWindow 4 (+ `SetWindowToPlot(LowerLeft, UpperRight)`), acLayout 5 (not from model; default for new paper layouts) ([G:77B2BD4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-77B2BD4B-05C2-4B90-9F1F-E24981C93B5C)) |
| Scale | `UseStandardScale` FIRST, then `StandardScale` or `SetCustomScale(Numerator, Denominator)` | acScaleToFit 0, ac1_8in_1ft 6, ac1_4in_1ft 8, ac1_2in_1ft 10, ac1in_1ft 12, ac1_1 16 ([G:D881B237](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D881B237-0040-4A7C-99D5-E82FA8B1EFE0)) |
| Lineweights | `ScaleLineweights` | Default: lineweights plot at their stated width whatever the scale ([G:1B3FAF4A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1B3FAF4A-0CE9-4D45-8D56-B9C6AA290197)) |
| Origin | `PlotOrigin`, `CenterPlot` | CenterPlot True moves the origin ([G:1D14459F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1D14459F-627A-44D2-8D85-24684EB6EDA8)) |
| Rotation | `PlotRotation` | ac0degrees 0, ac90degrees 1, ac180degrees 2, ac270degrees 3 |
| Styles | `StyleSheet`, `PlotWithPlotStyles`, `PlotWithLineweights` | |
| Hidden lines, model tiled | `Layout.PlotHidden` | True removes hidden lines ([G:52DBC632](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-52DBC632-3AF8-4523-A57B-07981FE1C73D)) |
| Shaded floating viewport | `PViewport.ShadePlot` | AsDisplayed 0, Wireframe 1, Hidden 2, Rendered 3 ([G:52DBC632](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-52DBC632-3AF8-4523-A57B-07981FE1C73D)) |
- Numeric values and the Rotation and Styles members: (TLB:acax26enu).
- Device and paper lists: `GetPlotDeviceNames()`, `GetCanonicalMediaNames()`, `RefreshPlotDeviceInfo()`, `GetLocaleMediaName(name)`; copy settings with `CopyFrom(plotConfig)`. (TLB:acax26enu)
- Shaded and rendered floating viewports are previewed, plotted and plotted to file fully shaded. ([G:52DBC632](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-52DBC632-3AF8-4523-A57B-07981FE1C73D))
- (inference) PDF output needs a PDF plotter configuration that exists on the machine. File-output drivers and PC3 files: 12.14. None of the COM plot calls were tested.

## 12.8 ActiveX events

### Levels ([G:ACBA4AF1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-ACBA4AF1-CBF9-4270-823A-3C1912476EC2))
- Application: opening, saving, closing and printing drawings; new drawings; commands; ARX and LISP apps loaded or unloaded; system variable changes; application window changes.
- Document: one drawing and its contents: objects added, erased, modified; shortcut menus; pickfirst set changes; drawing window changes; also open, close, print and LISP/ARX load from that drawing.
- Object: one event only, `Modified` (interface IAcadObjectEvents). ([G:ACBA4AF1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-ACBA4AF1-CBF9-4270-823A-3C1912476EC2), [G:0745E97F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0745E97F-A094-4636-AAA0-22134173A67F))
- Event data (for example the drawing name in BeginOpen) arrives as handler parameters. AutoLISP has the same idea as reactors (12.13). ([G:ACBA4AF1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-ACBA4AF1-CBF9-4270-823A-3C1912476EC2))

### Event names
- Application ([G:07494559](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-07494559-EA6C-4D84-B494-A49930C67E91)): AppActivate, AppDeactivate, ARXLoaded, ARXUnloaded, BeginCommand, EndCommand, BeginFileDrop, BeginLISP, EndLISP, LISPCancelled, BeginModal, EndModal, BeginOpen, EndOpen, BeginPlot, EndPlot, BeginQuit, BeginSave, EndSave, NewDrawing, SysVarChanged, WindowChanged, WindowMovedOrResized.
- Document ([G:679FBC1A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-679FBC1A-DE7B-44BA-9F8B-CD6FF1660D67)): Activate, Deactivate, BeginClose, BeginDocClose, BeginCommand, EndCommand, BeginDoubleClick, BeginLISP, EndLISP, LISPCancelled, BeginPlot, EndPlot, BeginRightClick, BeginSave, EndSave, BeginShortcutMenuCommand, BeginShortcutMenuDefault, BeginShortcutMenuEdit, BeginShortcutMenuGrip, BeginShortcutMenuOsnap, EndShortcutMenu, LayoutSwitched, ObjectAdded, ObjectErased, ObjectModified, SelectionChanged, WindowChanged, WindowMovedOrResized. The overview also mentions regeneration, but no regen event is listed.
- Object: `Modified`. It still fires when the object is deleted, so trap errors before reading it in the handler. ([G:63990AD3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-63990AD3-FB70-4A95-A20C-40E2677916E5))

### Turning events on
- Application and object events are not persistent: every controller must wire them each session. Document events switch on by themselves only inside VBA. ([G:07494559](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-07494559-EA6C-4D84-B494-A49930C67E91), [G:679FBC1A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-679FBC1A-DE7B-44BA-9F8B-CD6FF1660D67), [G:0745E97F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0745E97F-A094-4636-AAA0-22134173A67F))
- VBA pattern: class module with `Public WithEvents App As AcadApplication` (or `Doc As AcadDocument`, or `Object As AcadCircle`); main module `Dim X As New EventClassModule`; `Sub InitializeEvents()` sets `X.App = ThisDrawing.Application` (or `X.Doc = ThisDrawing`, or `X.Object = MyCircle`); then `Call InitializeEvents`. ([G:C584A219](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C584A219-3E90-4D1B-B382-6000F00CE9B0), [G:5AB42CC1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5AB42CC1-54A4-4FEA-AE61-2621BD9CF721), [G:BD2DDACD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BD2DDACD-F650-4691-B73C-BCCEE82B1CE6), [G:675CFE8A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-675CFE8A-2256-4808-A1C8-186E68A69496), [G:F7167688](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F7167688-613A-4180-9799-1CF7DE4E35B4), [G:63990AD3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-63990AD3-FB70-4A95-A20C-40E2677916E5))
- In VBA give every object enabled for Modified a handler, or VBA may terminate unexpectedly. ([G:40EAF8A4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-40EAF8A4-BD25-4D90-A94E-6E76575BA75D))
- BeginFileDrop: set `Cancel = True` to stop the dropped file from loading. ([G:C584A219](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C584A219-3E90-4D1B-B382-6000F00CE9B0))
- A shortcut-menu sample adds an item in `BeginShortcutMenuDefault` with the macro `Chr(vbKeyEscape) + Chr(vbKeyEscape) + "_open "` and deletes it in `EndShortcutMenu` so it is not saved into the user's menus. ([G:4F4377B1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4F4377B1-07C8-4DDA-94D9-23DBF493C871))
- (inference) A Python client would need its own COM event sink; the pages do not describe one and none was tested.

### Handler rules ([G:2FF2F1B5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2FF2F1B5-FFAC-420A-A741-15D1FC1A571E))
- AutoCAD is often in the middle of a command when a handler runs.
- Do not rely on event order. Only "Begin before its matching End" is guaranteed. Opening a drawing may give BeginCommand, BeginOpen, EndCommand, EndOpen, or another order. Erasing A then B may report B first.
- No input calls: GetPoint, GetEntity, GetKeyword and the other input methods, selection set operations, and SendCommand are all out.
- No dialog boxes. Message boxes are allowed, but inside BeginModal, EndModal, Activate, Deactivate or BeginRightClick they give odd sequencing.
- Write to any database object except the one that raised the event; reading that one is safe.
- Never do something that raises the same event (opening a drawing inside BeginOpen opens drawings until the limit).
- No events fire while a modal dialog is showing.

## 12.9 AutoLISP ActiveX layer: vl-load-com, vla- and vlax- functions
All ActiveX support in AutoLISP is Windows only. ([G:62F07541](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-62F07541-9663-4D83-B5EE-24D562351FCE) and every page in this group)

### Bootstrap [AUTO]
- `(vl-load-com)` first, in every program and in every reactor callback. It does nothing if support is already loaded; without it the program fails unless something else loaded it. ([G:62F07541](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-62F07541-9663-4D83-B5EE-24D562351FCE), [G:49DB4EF4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-49DB4EF4-7386-42CC-9633-5ABCDFA9D5D9))
- `(setq acad (vlax-get-acad-object))` returns the Application as a VLA-object. ([G:62F07541](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-62F07541-9663-4D83-B5EE-24D562351FCE))
- `(setq doc (vla-get-ActiveDocument acad))`, `(setq ms (vla-get-ModelSpace doc))`, `(vla-AddCircle ms (vlax-3d-point '(3.0 3.0 0.0)) 2.0)`. ([G:A2813E1F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A2813E1F-8C79-4341-BF07-F44B8305D7E5), [G:49EDE3C1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-49EDE3C1-BB15-4E09-A375-1ED9CD1370B0))
- Fetch Application, Document and ModelSpace once and reuse them; fetching them again and again hurts performance. The page's pattern caches them in globals `*acad-object*`, `*active-document*`, `*model-space*`. ([G:0BB6FC6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0BB6FC6B-AE18-4312-B6B5-F5225E3E9BB8)) (inference) The cache points at the drawing that was active when first filled; reset it per drawing.
- `(vla-Save doc)` saves; `(vla-Update acad)` refreshes. ([G:9C66C307](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9C66C307-9ED1-492B-9CE5-F81F73671C88))
- These pages do not say whether vla-/vlax- functions work in the headless Core Console (accoreconsole.exe). Probe it with `(vl-load-com)` then `(vlax-get-acad-object)` before relying on it. (inference)

### Function families ([G:A0459510](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A0459510-CE7A-4206-9EAA-E25AAB569B20), [G:131DA467](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-131DA467-3B73-455C-8F29-277D5212E0A6), [G:C22BEEA4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C22BEEA4-AF7A-4BC9-BAC5-9FD09C1971D3))
- `vla-<Method>` for every ActiveX method (`vla-AddCircle`); `vla-get-<Prop>` and `vla-put-<Prop>` for every property. Names are not case sensitive.
- The object before the dot in the VBA syntax becomes the FIRST argument: `RetVal = object.AddCircle(Center, Radius)` is `(setq RetVal (vla-AddCircle object center radius))`. Returned AutoCAD objects are VLA-objects.
- [AUTO] Generic forms, for any ActiveX object (other applications, custom objects such as MEP objects, members with no wrapper): `(vlax-invoke-method obj 'Method args...)`, `(vlax-get-property obj 'Prop)`, `(vlax-put-property obj 'Prop value)`. The name may be a symbol or a string. ([G:97BB042C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-97BB042C-BB33-4C42-8122-8765A9401B6A), [G:3221619A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3221619A-85E4-470E-AF2E-34048BB3DED5))
- Sample: `(vlax-get-property (vlax-get-acad-object) 'ActiveDocument)`. ([G:007074DE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-007074DE-ED62-4891-9CD3-9B7B3B9C9638))
- To find a vla- name, take the method name from the ActiveX Reference and add `vla-`. Reference file: `acadauto.chm` in `Program Files\Common Files\Autodesk Shared\en-us` (Windows only). ([G:131DA467](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-131DA467-3B73-455C-8F29-277D5212E0A6), [G:D9ED98F3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D9ED98F3-69E4-43AD-AAF5-D6B5B3A086D2))
- Constants work as values: `(vla-put-color myCircle acGreen)`. ([G:3221619A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3221619A-85E4-470E-AF2E-34048BB3DED5))
- ActiveX is often faster than entget-style access and needs no DXF codes: `(vla-get-radius c)` versus `(cdr (assoc 40 (entget e)))`. ([G:BA470FE7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BA470FE7-6488-4BC9-8FC8-ED93C32D86AA))

### LISP values for ActiveX types ([G:697D55E3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-697D55E3-BEED-41BF-A974-E65614B912AE))
| ActiveX type | LISP value to pass |
|---|---|
| Byte, Integer, Long, Single/Short | integer |
| Double | integer or real |
| String | string |
| Boolean | `:vlax-true` or `:vlax-false` |
| Object | VLA-object |
| Variant | variant |
| Array | safearray |
| Nothing | `:vlax-null` |
| Empty | nil |
- Enames and lists are not accepted as ActiveX values; convert them first (reading of the table). An entget result cannot go to a vla- function: use `(vlax-ename->vla-object e)`. ([G:697D55E3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-697D55E3-BEED-41BF-A974-E65614B912AE), [G:62F07541](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-62F07541-9663-4D83-B5EE-24D562351FCE))

### Safearrays and variants ([G:986313E1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-986313E1-0AEB-41DA-BC8B-093437F42B6A), [G:4BEC64A1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4BEC64A1-05AB-4202-A873-55C8C7EFA67A), [G:04690F92](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-04690F92-A1E6-42DC-917B-83D05755D131), [G:FF4F04CC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FF4F04CC-9DEF-41C7-8C8A-20635DE22A41), [G:88380428](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-88380428-44D9-4088-988D-0E0429EEA73A), [G:5AEC3752](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5AEC3752-6612-4289-89CC-6F9EA6228155))
- Every array passed to an ActiveX method must be a safearray, passed inside a variant.
- [AUTO] Points: `(vlax-3d-point '(x y z))` or `(vlax-3d-point x y [z])`; z defaults to 0. Matrix for `vla-TransformBy`: `(vlax-tmatrix '((a b c d) (e f g h) (i j k l) (m n o p)))`.
- [AUTO] Anything else: `(setq a (vlax-make-safearray vlax-vbDouble '(0 . 3)))`, `(vlax-safearray-fill a '(3.0 6.0 7.2 1.0))`, `(setq v (vlax-make-variant a))`. One `'(lo . hi)` bounds pair per dimension; lower bound may be any integer.
- `vlax-safearray-fill` needs a value for EVERY element or it errors. A 2D array takes a list of lists. Numbers read back as reals.
- `(vlax-safearray-put-element arr i [j] value)` (value last); `(vlax-safearray-get-element arr i [j])`; `vlax-safearray-get-dim`; `(vlax-safearray-get-l-bound arr dim)` and `(vlax-safearray-get-u-bound arr dim)` with dim counted from 1; `vlax-safearray->list`; `vlax-safearray-type`.
- Read a point property: `(vlax-safearray->list (vlax-variant-value (vla-get-Center c)))`. Write it back with `(vla-put-Center c (vlax-3d-point newlist))`. ([G:3221619A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3221619A-85E4-470E-AF2E-34048BB3DED5))
- `(vlax-make-variant 5)` makes a LONG (type 3), not an Integer (type 2). Give the type: `(vlax-make-variant 5 vlax-vbInteger)`.
- Type constants: vlax-vbEmpty, vlax-vbNull, vlax-vbInteger, vlax-vbLong, vlax-vbSingle, vlax-vbDouble, vlax-vbString, vlax-vbObject, vlax-vbBoolean, vlax-vbVariant, vlax-vbArray. Use the names, never the numbers; the numbers can change.
- Other variant functions: `vlax-variant-type`, `vlax-variant-value`, `vlax-variant-change-type`.

### Converting object references ([G:007074DE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-007074DE-ED62-4891-9CD3-9B7B3B9C9638), [G:F0AE18DE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F0AE18DE-4E8F-48C6-8138-0AF7ECE14C49), [G:697D55E3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-697D55E3-BEED-41BF-A974-E65614B912AE))
| From | To | Call |
|---|---|---|
| ename | handle | `(cdr (assoc 5 (entget e)))` |
| handle | ename | `(handent h)` |
| handle | VLA-object | `(vla-HandleToObject doc h)` |
| VLA-object | handle | `(vla-get-Handle o)` |
| VLA-object | object ID | `(vla-get-ObjectID o)` (an integer) |
| object ID | VLA-object | `(vla-ObjectIDToObject doc id)` |
| ename | VLA-object | `(vlax-ename->vla-object e)` |
| VLA-object | ename | `(vlax-vla-object->ename o)` |
- Handles persist across sessions. (stated) Enames and VLA-objects are per session. (inference)
- One task page swaps the descriptions of vla-get-ObjectID and vla-ObjectIDToObject; its code, and the other pages, are right. ([G:F0AE18DE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F0AE18DE-4E8F-48C6-8138-0AF7ECE14C49))

### Errors, output arguments and checks
- [AUTO] ActiveX methods RAISE errors; uncaught, the program stops and leaves the user at the Command prompt. Wrap risky calls: `(setq r (vl-catch-all-apply 'vla-GetBoundingBox (list obj 'll 'ur)))`, then `(vl-catch-all-error-p r)` and `(vl-catch-all-error-message r)`. ([G:9A862CD4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9A862CD4-8CD8-4A03-8B65-0B08BD9BAE4F), [G:9205DA3B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9205DA3B-9186-48C7-A477-E4C8FF88E1BB))
- Output-only arguments are quoted symbols: `(vla-GetBoundingBox obj 'minpt 'maxpt)` returns nil and fills each symbol with a safearray of 3 doubles. Declare them local in the defun `/` list or they leak as globals. ([G:6FD86B0D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6FD86B0D-7E1C-4FC9-ACF7-0965B17D2A5C))
- `(vlax-dump-object obj T)` prints the properties ((RO) = read-only) and, with T, the methods. Indexed properties are not expanded. ([G:4805C525](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4805C525-0E7F-4407-A473-D83ECAF1A940), [G:FE43302E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE43302E-AC21-4C0B-B61B-A10751A9E263))
- `(vlax-method-applicable-p obj "Copy")`; `(vlax-property-available-p obj "Color" T)`, where T means it must also be writable. Calling a member that does not apply raises an error. ([G:F6607E76](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F6607E76-FD9B-4B8B-B714-99CB34C988A5))
- `(vlax-read-enabled-p o)`, `(vlax-write-enabled-p o)`, `(vlax-erased-p o)`: test before touching an object other code (or a reactor) may have changed. After `vla-delete`, read-enabled is nil and erased is T. ([G:303355A2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-303355A2-CB24-4F93-BEDE-0F496EC96832))
- `(vlax-release-object o)` drops your pointer; `(vlax-object-released-p o)` tests it. `equal` is T when two VLA-objects point to the same drawing object. ([G:4A2C849B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4A2C849B-C0E0-4991-905D-A916B2CD3F25))
- Property changes may not repaint at once: `(vla-update obj)`. ([G:3221619A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3221619A-85E4-470E-AF2E-34048BB3DED5))

### Collections ([G:100F8BDB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-100F8BDB-2852-4986-BC09-53F77AFCDB96), [G:B81C818A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B81C818A-B50C-48B0-A8F1-3DA65C6E41B3))
- `(vlax-for item coll ...)` loops a collection and returns the last value. `(vlax-map-collection coll 'func)` applies one function to every member.
- `(vla-item coll i)` with i from 0, `(vla-get-count coll)`; they also work on groups and selection sets.
- Do not add or remove members inside the loop.

### Other ActiveX applications from LISP ([G:4A45548C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4A45548C-2556-4C92-9801-2996A56448DC), [G:B140BF54](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B140BF54-AD94-47EE-BC3E-91AEFA63D0CE), [G:1A6FB991](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1A6FB991-09A9-44BD-9B26-058B79CB0674), [G:7D4E0D6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7D4E0D6B-5714-4D2F-B124-545FCB3EFD75))
- `(vlax-get-object "Excel.Application")` attaches to a running instance (nil if none); `vlax-create-object` starts one; `vlax-get-or-create-object` does either. A new instance is invisible until `(vla-put-visible app :vlax-true)`.
- A ProgID may carry a version ("Word.Application.16"); leave it off to accept any instance.
- `(vlax-import-type-library :tlb-filename "file" :methods-prefix "mp-" :properties-prefix "pp-" :constants-prefix "cp-")` builds wrapper functions. Optional; costs memory; not every member gets a wrapper. Without a path the file is searched on the support path. Import once at top level, guarded by a test of a known constant.
- AutoCAD LT cannot use third-party type libraries.

## 12.10 AutoLISP talking to AutoCAD: command, command-s, variables, input, conversions

### command and command-s ([G:75F19C76](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-75F19C76-78D0-443B-BC39-EB9FEB4650B1)) [AUTO]
- Both run a built-in command or one defined by a loaded ObjectARX or .NET app. First argument = command name; the rest answer the prompts in order: strings, reals, integers, points, entity names, selection set names. `""` = Enter.
- Angles, distances and points may be passed as strings or as numbers and point lists.
- `command-s`: faster, but the command must COMPLETE inside the one call: one argument per prompt, no PAUSE, no LISP runs until it ends. Get input BEFORE the call: `(setq p1 (getpoint ...)) (command-s "._circle" p1 rad)`.
- `command`: LISP calls may sit inside its argument list and the command may stay active across statements.
- Some commands are restricted in command and command-s; the page does not list them.
- Examples: `(command "._circle" "0,0" "3,3")`; `(command "._thickness" 1)` (sets THICKNESS to 1.0); `(command "._-layer" "set" "NEW_LAY" "")`. ([G:75F19C76](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-75F19C76-78D0-443B-BC39-EB9FEB4650B1), [G:93E25253](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-93E25253-F42A-4E85-84AD-4DCA66DB48A6))
- [AUTO] `_` before every command name and keyword (language-proof); `.` forces the built-in command; `"._line"` and `"_.line"` are both valid. Example: `(command "_line" pt1 pt2 pt3 "_c")`. ([G:D156B6ED](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D156B6ED-B1B4-42CB-BE1D-CA251BFC08C3))
- Object plus pick point (TRIM, EXTEND, FILLET) without PAUSE: `(command "._trim" (entlast) "" '(5 7) "")`. ([G:EF2D73CE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF2D73CE-9B75-4532-AF2F-DD6F0C36C3FD))
- [AUTO] Obsolete command from LISP: prefix it with a period (`.BLIPMODE`). Obsolete system variable: use getvar/setvar, not `command`. Removed items cannot be revived. ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))
- INSERT opens the Blocks palette (2020 and later). `(initdia)(command "insert")` needs `(initcommandversion 2)` first to get the old dialog, or use `(command "classicinsert")`. Both dialogs block a headless run. ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))

### PAUSE ([G:93E25253](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-93E25253-F42A-4E85-84AD-4DCA66DB48A6))
- `PAUSE` is a predefined symbol whose value is one backslash string. Use the symbol, not a literal `"\\"`.
- While a command is paused it is "active" and no other LISP expression can be entered. Transparent 'ZOOM and 'PAN work at a pause.
- At a text or attribute-value prompt PAUSE pauses only when TEXTEVAL is nonzero; with TEXTEVAL 0 the backslash is taken as the literal value.
- With PICKFIRST active and objects selected, SELECT with PAUSE takes them and does not pause.
- Examples: `(command "._circle" PAUSE PAUSE)`; `(command "._-insert" blk PAUSE "" "" PAUSE)`.
- [AUTO] In a headless .scr, accoreconsole or SendCommand run there is nobody to answer a PAUSE: supply every value.

### UNDO grouping ([G:4481039B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4481039B-77DA-4500-AE8B-3D2AD6951115))
- Every command and command-s call is its own UNDO group, so one U undoes only the last call.
- [AUTO] Wrap a routine: `(command "._UNDO" "_Begin")` ... `(command "._UNDO" "_End")`. The sample also saves OSMODE, sets it to 0 for exact points, and restores it at the end.
- Over COM the type library has `Document.StartUndoMark` and `EndUndoMark` (not tested). (TLB:acax26enu)

### Variables, environment and registry ([G:529819FD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-529819FD-9E9C-4789-BA18-B981BA32DD23), [G:11BEB9BE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-11BEB9BE-2E76-4180-AB1F-1D05CEFCA9C8))
- `(getvar "name")`, `(setvar "name" value)`: types integer, real, string, 2D or 3D point. A wrong type raises an AutoLISP error. System variable names are not case sensitive.
- `(getenv "Name")`, `(setenv "Name" "value")`: names ARE case sensitive (MaxHatch is not MAXHATCH); the value is always a string, even for numbers: `(setenv "MaxHatch" "50000")`. Save the old value and restore it.
- `getcfg` and `setcfg` (acadxxxx.cfg AppData section) are obsolete; use `vl-registry-read` and `vl-registry-write`.

### Coordinates: trans and the UCS ([G:0F0B833D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0F0B833D-78ED-4491-9918-9481793ED10B)) [AUTO]
- Every point passed to a command, from LISP too, is read in the CURRENT UCS (unless typed with a `*` prefix). Convert WCS, OCS or DCS points with trans first.
- `entget` returns points in the object's OCS; convert back to OCS before `entmod` or `entmake`.
- `(trans pt from to [disp])`: from/to = 0 WCS, 1 current UCS, 2 DCS of the current viewport, 3 paper space DCS (only paired with 2); or an entity name (its OCS); or an extrusion vector. Nonzero disp = pt is a displacement vector.
- Example: UCS rotated 90 degrees about Z, `(trans '(1.0 2.0 3.0) 0 1 0)` returns (2.0 -1.0 3.0).

### Number and string conversions ([G:A38E30D4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A38E30D4-684E-44FA-A910-E08522876414), [G:725BC3DE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-725BC3DE-3D4C-4365-A7F9-FAD5B8AC2DD1), [G:8256416C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8256416C-3302-4BBF-B4C9-98A7973FBC96), [G:A42448EB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A42448EB-3E46-4902-9980-255DBA1EF9CB))
- Angles in LISP and in the drawing are RADIANS. Degrees = `(* 180.0 (/ rad pi))`; radians = `(* pi (/ deg 180.0))`; use a real divisor.
- `(rtos value mode precision)`: mode 1 scientific, 2 decimal, 3 engineering, 4 architectural, 5 fractional. For 17.5 with DIMZIN 0: "1.7500E+01", "17.50", 1'-5.50", 1'-5 1/2", 17 1/2. `distof` reverses it (escape the inch mark as `\"`).
- `(angtos rad mode precision)`: 0 degrees, 1 deg/min/sec, 2 grads, 3 radians, 4 surveyor; `angtof` reverses it. angtos honors ANGBASE: `(angtos (getvar "angbase"))` is always "0".
- Output depends on LUNITS, LUPREC, AUNITS, AUPREC, DIMZIN, UNITMODE, ANGBASE: pass mode and precision explicitly in scripts. (inference)
- `(cvunit 1.0 "inch" "cm")` = 2.54, from `acad.unt` (plain text, editable). For many conversions get the factor once and multiply. Fails for temperature (offset) and unlike quantities.

### User input functions: all wait for a person ([G:5D9F55C4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5D9F55C4-97FE-4FF1-81D2-C9F5905C2E25), [G:7F024C1B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7F024C1B-EFB8-4F6C-9EFE-A6491210A4CD), [G:44553A7D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-44553A7D-EFFF-4C26-8CF9-DF163ECACCB9), [G:3967F2A7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3967F2A7-D347-4A42-9162-6E1E45399AA9))
- getint, getreal, getstring, getpoint, getcorner, getdist, getangle, getorient, getkword, plus entsel, nentsel, grread, getfiled. An unattended run must avoid them or feed every answer.
- getangle honors ANGBASE and ANGDIR (use for block rotation); getorient 0 is always East (use for text angles).
- `(initget bits "Kw1 Kw2")` applies to the NEXT getXXX, entsel, nentsel or nentselp only (not getstring). Bits: 1 no Enter, 2 no zero, 4 no negative, 128 arbitrary text returned as a string. Keywords cannot contain `_`.
- Pass the prompt as the function's own argument, so it is re-shown after bad input.
- getint answers bad input with "Requires an integer value." and asks again; bare Enter returns nil.
- grread and the low-level graphics functions (grtext, grdraw, grvecs) carry no release or hardware guarantee. ([G:7F024C1B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7F024C1B-EFB8-4F6C-9EFE-A6491210A4CD), [G:57942DDA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-57942DDA-8A41-4456-B021-FDEF0475A6AE))

### Date and time ([G:EF8856E5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF8856E5-DB58-4EFC-B223-AB8B8A25F240), [G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))
- CDATE (coded decimal), DATE (Modified Julian); TDCREATE, TDUPDATE, TDINDWG, TDUSRTIMER and the universal variants. Since 2017 all are whole seconds only; use MILLISECS (ms since system start) for finer timing.
- `(rtos (getvar "cdate") 2 6)` gives "20170306.175302"; plain getvar prints scientific notation.

### Files, help, menus, geometry helpers
- `(findfile "acad.pgp")` searches the support paths; nil if not found. Use `/` or `\\` in path strings. ([G:CB21D8A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB21D8A9-1A88-477F-95CA-74F665609A42))
- `getfiled` and `help` open UI and block a script. ([G:CB21D8A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB21D8A9-1A88-477F-95CA-74F665609A42), [G:02866F82](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-02866F82-0BA8-4395-A4EA-9A90EC934045))
- `(menucmd "M=$(edtime,$(getvar,date),H:MMam/pm)")` evaluates DIESEL and returns the string. ([G:92DA21E0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-92DA21E0-1E33-45AD-B2F8-1AB788392E4B))
- `(angle p1 p2)` (radians from the UCS X axis), `(distance p1 p2)`, `(polar base ang dist)`, `inters`. ([G:56A7AF2E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-56A7AF2E-F3CC-45B3-915C-A34290A591DA))
- `(osnap pt "_endp,_midp")`: underscore each mode; nil if nothing qualifies; SORTENTS picks among several, APERTURE sets reach. Since 2016 the `qui` (Quick) mode returns nil. ([G:4EEE5488](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EEE5488-01D8-454F-9386-79E493E55D6E), [G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))
- `(textbox '((1 . "text")))` returns lower-left and upper-right offsets from the insertion point, as if rotation were 0, using the current style unless the list gives one. ([G:DA97206B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DA97206B-85C2-4746-B0E6-67E8ABE99117))
- End routines with `(princ)` so the return value is not echoed. ([G:A7AEB9D4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A7AEB9D4-1E5E-49D2-832A-7AFCE51C10BE))

## 12.11 AutoLISP entities, xdata and selection sets

### Getting entity names without a pick [AUTO]
- `(entlast)` = the most recently created MAIN entity; use it to grab what a `command` call just made. ([G:3EEA3D4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3EEA3D4B-36B6-4E3B-B9E8-62B6265FA68C))
- `(entnext)` = first entity in the drawing; `(entnext e)` = the next; nil at the end. Loop: `(setq e (entnext)) (while e ... (setq e (entnext e)))`. ([G:3EEA3D4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3EEA3D4B-36B6-4E3B-B9E8-62B6265FA68C))
- `(handent "5a2")` = current entity name for a handle; nil if none. It can return a deleted entity's name (deleted objects stay until the drawing closes). ([G:30C33AF6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30C33AF6-4BE3-4334-96BD-F929040C31D3))
- `(ssget "X" filter)` = every matching object in the database (below).
- entsel and nentsel make the user pick: not for unattended runs. ([G:3EEA3D4B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3EEA3D4B-36B6-4E3B-B9E8-62B6265FA68C))
- Entity names and selection-set names change between sessions; handles do not. Store handles (group 5). ([G:9AED35A1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9AED35A1-5CB2-43D8-88ED-CBE95E54798D), [G:1DABEF81](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1DABEF81-C431-442A-8916-7F9079AA7799), [G:30C33AF6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30C33AF6-4BE3-4334-96BD-F929040C31D3))
- INSERT, INSERT*, XBIND and partial DXFIN give incoming objects NEW handles. Attached xref objects keep theirs but handent cannot reach them. ([G:30C33AF6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30C33AF6-4BE3-4334-96BD-F929040C31D3))

### entget ([G:EF8C5586](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF8C5586-BA1F-4EA6-BAD1-6BA792B601F0))
- Returns a DXF-coded list starting with `(-1 . <ename>)`. LINE: (-1) (0 . "LINE") (330 owner) (5 . handle) (100 . "AcDbEntity") (67 . 0) (410 . "Model") (8 . layer) (100 . "AcDbLine") (10 start) (11 end) (210 extrusion).
- [AUTO] Read with `(cdr (assoc code lst))`. Never rely on list order; assoc returns nil if absent.
- Points are lists, not dotted pairs: `(10 1.0 2.0 0.0)`; one group carries X, Y, Z (unlike DXF files).
- Color, linetype, thickness and similar come back only when not the default.
- Points are in OCS (equal to WCS for point, line, 3D line, 3D face, 3D polyline, 3D mesh, dimension). Use trans.
- Before entget on legacy polyline VERTEX entities, read or write that polyline's header first, or widths (40, 41) can be lost.

### entmod, entupd, entdel ([G:125DC058](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-125DC058-BBAA-4CA9-A203-53F0A27B87D0), [G:34D3F07F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-34D3F07F-B93F-4316-B683-6D42E3436E27), [G:7DC692D0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7DC692D0-4FD4-4931-93C3-EFC616397E4C))
- [AUTO] `(setq ed (entget e)) (setq ed (subst (cons 8 "MYLAYER") (assoc 8 ed) ed)) (entmod ed)`.
- entmod cannot change the entity type, the handle, or groups -1, -2, 5 (ignored); viewport entities raise an error; extra limits on dimensions and hatches.
- Referenced styles, linetypes, shapes and blocks must already exist; a NEW layer name is created automatically.
- entmod on a sub-entity (vertex, attribute) does not redraw the whole object: do the edits, then `(entupd e)` once. Edits inside a block definition need REGEN; entupd is not enough.
- Editing an entity inside a block definition changes every reference; non-constant attributes in existing references are not updated.
- Entity data changes show on screen only for objects in a visible area on a visible layer. ([G:000646D0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-000646D0-0597-44A0-B0A7-08D9A3BCA978), [G:34D3F07F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-34D3F07F-B93F-4316-B683-6D42E3436E27))
- entget, entmod, entdel and entmake accept all object types, but each type decides how much it allows. Non-graphical objects (dictionaries, table entries) cannot go to entupd. entmake files an object by its type: a layer into the layer table, a graphic entity into the current space. ([G:984A6964](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-984A6964-E801-4C22-8E41-BF3D05CD122F))
- `(entdel e)` erases; a second entdel on it in the same session restores it. Attributes and legacy polyline vertices cannot be deleted alone; entities inside block definitions cannot be deleted with entdel.

### entmake ([G:DFDAE6CD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DFDAE6CD-E753-4D01-9D9B-4D1F66B1DE6E), [G:7DA0E2BA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7DA0E2BA-963F-4E41-AF33-C6B9D89D4688), [G:EB9BFDAA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EB9BFDAA-487A-4586-A556-1F5F84BCF2F3))
- [AUTO] `(entmake '((0 . "CIRCLE") (8 . "MYLAYER") (10 5.0 7.0 0.0) (40 . 1.0)))` appends a new entity.
- Entity type must be the first or second item (only -1 may come before it).
- Types newer than R13 need subclass markers: `(100 . "AcDbEntity")`, then the type marker. Minimal MTEXT: `(0 . "MTEXT") (100 . "AcDbEntity") (8 . "ALAYER") (100 . "AcDbMText") (10 4.0 4.0 0.0) (1 . "Some\\Ptext")`. Pre-R13 types (3DFACE, ARC, ATTDEF, ATTRIB, CIRCLE, DIMENSION, INSERT, LINE, POINT, POLYLINE, SEQEND, SHAPE, SOLID, TEXT, VERTEX, VIEWPORT) need none.
- entmake CANNOT create viewports. Unknown layer = created; any other unknown style, linetype, block or shape = failure. Objects on a frozen layer do not regenerate until thawed.
- Complex entities (legacy polyline, block, polyface): one at a time, built over several entmake calls, nothing shows until SEQEND or ENDBLK. `(entmake)` with no argument cancels. Calling MSPACE/PSPACE mid-build, or a sub-entity whose group 67 differs, cancels it. Legacy polyline header needs `(66 . 1)`.
- entmake does NOT check block-name conflicts: test with `tblsearch` first or you may redefine a block silently.
- Dotted pairs need a space on both sides of the dot. With variables, build lists with `list` and `cons`, not a quote.
- Anonymous blocks: `*U` names (group 70 bit 1); AutoCAD assigns the number. entmake cannot make `*T` (table), `*D` (dimension) or `*X` (hatch) blocks. Unreferenced ones are purged at open. INSERT cannot take an anonymous block.
- Is a block used? Scan `(ssget "X" '((2 . "NAME")))` and also each block definition for nested uses. ([G:D0E1B3EC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D0E1B3EC-FA5B-4820-83C0-EDEE0BE540E0))

### Xdata ([G:A94BC605](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A94BC605-5517-437F-A6FE-D3EB8116A01A), [G:FA8BBFB8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FA8BBFB8-5C3E-4742-A3A2-CBCDB168FB08), [G:3481BF7B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3481BF7B-73CB-4FD5-B421-C25BE92C6D56), [G:8F373105](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8F373105-67D5-4CBD-931D-D0869F2A7EB5), [G:1A2A0518](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1A2A0518-E9DB-462E-925E-32181D96CE4D), [G:48A12BAA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-48A12BAA-E785-4E2B-B7A7-E3B976E75891), [G:61A8B084](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-61A8B084-BA16-4FDA-8C8A-C2FA73E8DDC9))
- [AUTO] Attach: `(regapp "NEWDATA")`, then `(entmod (append (entget e) '((-3 ("NEWDATA" (1000 . "text"))))))`.
- `regapp` returns nil when the name is already registered; that is normal. Safe test: `(tblsearch "appid" name)`. Pick unique names (company plus product plus a number).
- [AUTO] `(entget e '("APP1" "APP2"))` returns xdata only for the named apps, after a -3 marker; `'("*")` returns all. Edit and entmod: only the requested apps' data changes.
- Group codes: 1000 string (max 255 bytes), 1001 app name (max 31 bytes; letters, digits, `$ - _`; no spaces), 1002 "{" or "}", 1003 layer name, 1004 binary (max 127 bytes, not usable from LISP), 1005 handle, 1010 point, 1011 world position (moves, scales, rotates, mirrors, stretches with the object), 1012 world displacement, 1013 world direction (unit), 1040 real, 1041 distance (scaled), 1042 scale factor (scaled), 1070 16-bit integer, 1071 32-bit long.
- AutoLISP reads 1071 as a REAL: `(1071 . 12.0)`; entmake and entmod accept 12 or 12.0.
- Limit 16 KB of xdata per entity. `xdsize` (slow) and `xdroom` tell size and room left; use them in an error handler after a failed entmod.
- 1005 handles must be NULL or valid in this drawing or AUDIT complains. For objects in xrefs store a 1000 string instead. Xdata survives copy within and between drawings.
- Associative hatches carry ACAD xdata by default.

### Selection sets ([G:1DABEF81](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1DABEF81-C431-442A-8916-7F9079AA7799), [G:BF30AA6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BF30AA6B-AB31-4085-BEC8-ABA518E9DD3C), [G:87466915](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-87466915-82EC-4487-BAB1-9A1E49CADA8A))
- `ssget` modes shown: none = user selects; "P" previous set; "L" last visible object added; a point = object through it; "W" pt1 pt2 window; "F" pt-list fence; "WP" pt-list window polygon; "I" implied (pickfirst); "X" whole database. Crossing and Crossing Polygon options also exist; the page does not print their mode strings. Argument order: mode, pt1, pt2 (leave out if unused), pt-list, filter list LAST. ([G:1DABEF81](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1DABEF81-C431-442A-8916-7F9079AA7799), [G:7BE77062](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7BE77062-C359-4D01-915B-69CF672C653B))
- [AUTO] For unattended runs use `(ssget "X" filter)`.
- `(ssadd)` new empty set; `(ssadd e ss)` adds (duplicates silently ignored); `(ssdel e ss)`; `(sslength ss)`; `(ssname ss i)` (0-based; nil past the end); `ssmemb`.
- LIMIT: at most 128 selection sets open at once (may be lower). At the cap no more are made; call `(gc)` before ssget works again. Set finished sets to nil or keep them local.
- Do not overwrite the only variable holding a set with an ObjectARX function's return value: the set can be garbage collected even if it is the same set. Use a second variable.

### ssget filter lists ([G:7BE77062](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7BE77062-C359-4D01-915B-69CF672C653B), [G:877CEEA5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-877CEEA5-0D88-48DF-8450-B9421031A1B7), [G:11EA0ABD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-11EA0ABD-AE29-4DD7-92A5-DFF6EC1C9799), [G:84C3CDF5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-84C3CDF5-DF88-4473-A10D-C7778EE037C8), [G:5CB54129](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5CB54129-22A1-42B9-B97C-2D2F5597F90E))
- A filter is an entget-style association list checked against each object's MAIN entity fields. Items AND together; objects lacking a listed group are dropped; nil when nothing matches.
- Ignored groups: -1 (name), 5 (handle), anything above 1000 (xdata). Invalid group codes are ignored. Use -3 for xdata.
- [AUTO] Examples: `(ssget "X" '((0 . "CIRCLE")))`; `(ssget "W" pt1 pt2 '((8 . "FLOOR9")))`; `(ssget "X" (list (cons 0 "CIRCLE") (cons 8 lay) (cons 62 3)))`.
- Color filters match the object's own color: `(62 . 5)` does not match objects blue by ByLayer or ByBlock.
- Quote the list only when every code and value is literal; with variables build it with `list` and `cons`.
- Relational tests on numbers: put `(-4 . "op")` before the item: `(ssget "X" '((0 . "CIRCLE") (-4 . ">=") (40 . 2.0)))`. Operators: `*` (always true), `=`, `!=` `/=` `<>`, `<`, `<=`, `>`, `>=`, `&` (any mask bit set, integers only), `&=` (all mask bits set, integers only). Points take one operator per axis: `">,>,*"`. Group 210 allows only `*`, `=` and not-equal.
- Strings take wildcard patterns (same as `wcmatch`), not relational operators. Anonymous block names start with `*`: escape it with a backquote, `(ssget "X" '((2 . "`*U2")))`.
- Xdata: `(ssget "X" '((-3 ("APPNAME"))))`; with a type: `'((0 . "CIRCLE") (-3 ("APPNAME")))`. Several names in one -3 group = AND; wildcards work (`"APP[12]"`, `"APP1,APP2"`). The page text says -3 must be first, but its own example puts (0 . "CIRCLE") before it.
- Grouping: `"<AND"`/`"AND>"`, `"<OR"`/`"OR>"` (one or more), `"<XOR"`/`"XOR>"` (exactly two), `"<NOT"`/`"NOT>"` (exactly one), as -4 groups. They must balance or ssget fails; not case sensitive; not allowed inside a -3 group (put separate -3 groups inside the operator pair instead).
- A set may hold model and paper space objects (group 67); a command given the set uses only the current space.

## 12.12 AutoLISP symbol tables, dictionaries and xrecords (and the MEP dictionaries)

### Symbol tables ([G:7DBE1715](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7DBE1715-16DA-4236-BD1C-BAD73844FC7D), [G:7B91F774](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7B91F774-B0CD-4F5B-9FFA-1130443E659B))
- Tables: APPID, BLOCK, DIMSTYLE, LAYER, LTYPE, STYLE, UCS, VIEW, VPORT. Functions: tblnext, tblsearch, tblobjname, entget, entmod, entmake, entdel, handent.
- [AUTO] `(tblnext "BLOCK" 1)` rewinds to the first entry; later calls on the same table step on. `(tblsearch "LAYER" "NAME")` returns the entry or nil; a non-nil third argument makes the next tblnext continue after it.
- tblsearch and tblnext results carry no -1 entity name. For entmod, get the name with `tblobjname` and read it with entget. Group 70 is ignored by entmod and entmake; handles (5, 105) cannot be set.
- entdel cannot delete table entries; tables themselves cannot be made with entmake; `*ACTIVE` entries cannot be created; duplicate names are allowed only in VPORT.
- VPORT edits made with TILEMODE off show nothing until TILEMODE is on. All viewports of one configuration share a name (`*ACTIVE`, `4VIEW`).
- BLOCK entry: `(0 . "BLOCK") (2 . name) (70 . flags) (10 base) (-2 . first-entity)`; for an empty block -2 is the ENDBLK.

### Dictionaries ([G:7DBE1715](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7DBE1715-16DA-4236-BD1C-BAD73844FC7D), [G:24E52678](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-24E52678-513E-4322-8070-B23C8945DC3D), [G:74E761F9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-74E761F9-08B1-4690-ADA0-396BC9431729))
- `(namedobjdict)` = the root dictionary of all non-graphical objects. A dictionary can also hang off an object as its extension dictionary. Never assume a dictionary exists: drawings differ.
- [AUTO] `(dictsearch dict "KEY")` returns the entry's list; `dictnext` steps through entries. In a dictionary's entget list, group 3 = key and 350 = the entry object.
- entmod can change a dictionary's xdata, not its entries. Add with `dictadd`, rename a key with `dictrename` (keys starting ACAD cannot be renamed), remove with `entdel` on the entry's name. Keys follow symbol-table name rules.
- Group example: `(setq g (dictsearch (namedobjdict) "ACAD_GROUP"))`, then `(dictsearch (cdar g) "G1")`; the GROUP list holds one `(340 . ename)` per member.
- Standard dictionaries in a new 2027 drawing include ACAD_GROUP, ACAD_LAYOUT (Layout1, Layout2, Model), ACAD_MLEADERSTYLE, ACAD_MLINESTYLE, ACAD_PLOTSETTINGS, ACAD_PLOTSTYLENAME, ACAD_SCALELIST, ACAD_TABLESTYLE, ACAD_VISUALSTYLE (2dWireframe, Conceptual, Hidden, Realistic, Shaded, Shaded with edges, Shades of Gray, Sketchy, Wireframe, X-Ray and others), ACAD_MATERIAL, ACAD_COLOR, AcDbVariableDictionary.

### Xrecords ([G:FA5F2E08](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FA5F2E08-24F5-4947-A470-6CA84E404F2A))
- Arbitrary data in normal DXF groups 1 to 369; unlike xdata, no size or order limit.
- [AUTO] `(setq x (entmakex '((0 . "XRECORD") (100 . "AcDbXrecord") (1 . "text") (10 1.0 2.0 0.0) (40 . 3.14159))))` makes an object with no owner; `(dictadd (namedobjdict) "MYKEY" x)` attaches it; `(dictsearch (namedobjdict) "MYKEY")` reads it back (with a handle, an ACAD_REACTORS group and `(280 . 1)` you did not supply).

### MEP drawing dictionaries (VERIFIED)
- [AUTO] Routing preferences: `(dictsearch (namedobjdict) "AECB_PIPE_PARTROUTINGPREFERENCES_STYLES")`, group 3 = names (the COM PipePartCatPrefStyles collection does not list them).
- [AUTO] Pipe systems: `(dictsearch (namedobjdict) "AECB_PIPESYSTEMDEFS")`, group 3 = names; a system added over COM shows here at once.
- All AEC and AECB keys: `(entget (namedobjdict))`, group 3. Keys seen: 12.3.
- Send these through SendCommand and write the result to a file (12.2).

## 12.13 AutoLISP reactors

### Types ([G:EC61BEC2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC61BEC2-39B9-4CD1-BE3B-7781DF1E3530), [G:396A2538](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-396A2538-4C9E-4A12-8174-289A13F6E208))
- A reactor links an AutoCAD event to a callback function in your program. Call `(vl-load-com)` first, also inside callbacks. ([G:49DB4EF4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-49DB4EF4-7386-42CC-9633-5ABCDFA9D5D9))
- Categories: Database `:VLR-AcDb-Reactor` (objects added and so on), Document `:VLR-DocManager-Reactor` (document opened, window activated, lock changes), Editor, Linker `:VLR-Linker-Reactor` (ObjectARX load and unload), Object `:VLR-Object-Reactor` (one object modified, copied, deleted).
- `:VLR-Editor-Reactor` is kept only for backward compatibility and misses editor events added since AutoCAD 2000. Use the specific types: `:VLR-Command-Reactor`, `:VLR-DeepClone-Reactor`, `:VLR-DWG-Reactor` (open, close, save), `:VLR-DXF-Reactor`, `:VLR-Insert-Reactor`, `:VLR-Lisp-Reactor`, `:VLR-Miscellaneous-Reactor`, `:VLR-Mouse-Reactor`, `:VLR-SysVar-Reactor`, `:VLR-Toolbar-Reactor`, `:VLR-Undo-Reactor`, `:VLR-Wblock-Reactor`, `:VLR-Window-Reactor`, `:VLR-XREF-Reactor`.
- [AUTO] `(vlr-types)` lists every type in the running session. `(vlr-reaction-names :VLR-DWG-Reactor)` lists a type's events: beginDwgOpen, endDwgOpen, dwgFileOpened, databaseConstructed, databaseToBeDestroyed, beginSave, saveComplete, beginClose (each with the `:VLR-` prefix). One page summary spells it `vlr-reaction-name`; the plural form is the one with a working result. ([G:396A2538](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-396A2538-4C9E-4A12-8174-289A13F6E208), [G:89966743](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-89966743-6860-42BD-AA34-714E5B28863E))

### Creating ([G:396A2538](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-396A2538-4C9E-4A12-8174-289A13F6E208), [G:373FCF92](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-373FCF92-4E98-448A-9C1C-D15A06880C81)) [AUTO]
- Creation function = type name without the colon: `vlr-dwg-reactor`, `vlr-acdb-reactor`, `vlr-object-reactor`, `vlr-toolbar-reactor` and so on. Each returns a Reactor object.
- Non-object reactor: `(vlr-dwg-reactor data '((:vlr-saveComplete . saveDrawingInfo)))`: data (or nil), then a list of `(event . callback)` pairs.
- Object reactor: `(vlr-object-reactor (list obj) "Circle Reactor" '((:vlr-modified . print-radius)))`: owner list of VLA-OBJECTS (never enames; convert with vlax-ename->vla-object), data, then event pairs.
- Editor reactors fire for every command, typed or from LISP or the UI, so the callback must check which command it got.
- Check that the reactor does not already exist before creating it (sample: `(if (= circleReactor nil) ...)`), or the event gets several callbacks. ([G:10123DBC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-10123DBC-EA95-4300-A441-E028BB441477), [G:BA488DA2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BA488DA2-20A1-430F-8F50-06AF850EBE00))

### Callbacks ([G:B6FD0211](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B6FD0211-23FA-4F65-80EE-142B2BC2E188), [G:BA85008E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BA85008E-FF80-4E91-9365-0F4602AD0181), [G:10123DBC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-10123DBC-EA95-4300-A441-E028BB441477))
- Non-object callback takes 2 arguments: the reactor, and a list of event parameters. Object callback takes 3: the object that fired, the reactor, the parameter list.
- Parameters depend on the event: `:vlr-saveComplete` passes the saved file name; a sysvar change passes the variable name and a success flag. The sample reads the name with `(cadr params)` while the prose says a string; check the real shape before use.
- NOT allowed in a callback: `command`, `entget`, `entmod`, `getpoint`, `entsel`, `getkword`, other input, selection-set operations, dialogs. Message and alert boxes are fine. Use ActiveX functions to touch objects.
- Do not change an object that is in the reactor's own owner list: it raises an error and can make AutoCAD fail. Reading it is fine.
- Never do something that raises the same event (opening a drawing in BeginOpen loops up to the open-drawing limit).
- Do not rely on event order (only Begin before matching End) or on the order between objects; treat reactors as state flags.
- No events fire while a modal dialog is open.
- `vlr-sysVarWillChange` and `vlr-sysVarChanged` can fire several times for one change. ([G:49DB4EF4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-49DB4EF4-7386-42CC-9633-5ABCDFA9D5D9))
- Test callbacks: `vlr-beep-reaction`, `vlr-trace-reaction` (prints arguments to the Visual LISP Trace window).

### List, change, query, disable ([G:89966743](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-89966743-6860-42BD-AA34-714E5B28863E), [G:F6B719E4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F6B719E4-537B-42C2-8D22-9A313FE900A0), [G:61BE0741](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-61BE0741-323D-4DFA-9D6C-FC7C339BA365), [G:DC1713AC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DC1713AC-D79F-456B-87E8-1656130CB23B))
- `(vlr-reactors [type])` lists reactors by type.
- `(vlr-reaction-set r :vlr-modified 'print-area)` (quoted function), `(vlr-data-set r data)`, `(vlr-owner-add r obj)`, `(vlr-owner-remove r obj)`.
- `(vlr-type r)`, `(vlr-current-reaction-name)` (inside a callback), `(vlr-data r)`, `(vlr-owners r)`, `(vlr-reactions r)`.
- Reactors cannot be deleted, only disabled: `(vlr-remove r)`, `(vlr-remove-all [type])`, `(vlr-add r)` re-enables, `(vlr-added-p r)` tests.

### Persistent reactors and documents ([G:0A632CD0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A632CD0-99B8-4E7E-A958-A0723E50ABB5), [G:0A1ECE3A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A1ECE3A-AC63-4140-98A2-448187BD96D2), [G:43BA6D50](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-43BA6D50-C2F0-4699-B3DE-0E2BCFF5A56E))
- Reactors are transient by default (gone when the drawing closes). `(vlr-pers r)` saves one in the drawing; `vlr-pers-release`, `vlr-pers-p`, `(vlr-pers-list [type])`.
- The callback code is NOT saved. Opening a drawing whose persistent reactors have no loaded callbacks shows an error message. To load callbacks on open, ship reactor and callbacks in a separate-namespace VLX.
- By default a callback runs only while its own document is active (`active-document-only`). `(vlr-set-notification r 'all-documents)` makes it fire in any document; then the callback should only set and read LISP variables, or AutoCAD may become unstable. `(vlr-notification r)` reads the setting.
- AutoLISP works only in the active document; a separate-namespace app cannot touch objects in another document. VBA, ObjectARX and .NET can edit a non-active open drawing.

## 12.14 Compatibility, loading and admin facts that break automation

### Loading code
- Secure mode (since 2014): with SECURELOAD set to 1 or 2, AutoCAD loads and runs code only from the trusted locations in TRUSTEDPATHS. The pages do not list which file types count or what each value means. ([G:D54B0935](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D54B0935-1638-4F97-8B37-1EC3635A1E71), [G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94)) (inference) A LSP, VLX or DLL outside a trusted path may fail to load in an unattended run.
- LSP files can be digitally signed since 2016 (no untrusted warning). Signed VLX files do not load in 2015 or earlier. ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94))
- NETLOAD loads .NET apps. AutoCAD 2027 = release 26.0: SDK 2027 only, .NET 10.0. 2026 = 25.1 and 2025 = 25.0, both .NET 8.0. 2021 to 2024 = 24.0 to 24.3, .NET Framework 4.8. ObjectARX 2027 supports only SDK 2027. ([G:D54B0935](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D54B0935-1638-4F97-8B37-1EC3635A1E71), [G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A), [G:C21B8F00](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C21B8F00-C7DE-4E44-8006-D5DC99199F31))
- .NET and ObjectARX programs built for 2026 or earlier must be updated and recompiled for 2027. ([G:4CD0B52A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4CD0B52A-9D16-455B-BB8D-E7DBC14E75C8))
- VBA still works, but its runtime and IDE are a separate download (VBAIDE, VBALOAD). ([G:927E71C2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-927E71C2-E515-438E-9D7A-246D97BEF93F))
- Express Tools library functions (2025 and later): call `(acet-load-expresstools)` first. `Julian.lsp` (CTOJ, DTOJ, JTOC, JTOD, JTOW) is available after the DATE command runs or after `load`. ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94), [G:EF8856E5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EF8856E5-DB58-4EFC-B223-AB8B8A25F240))

### Release changes that break old code ([G:31FD1A96](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31FD1A96-C002-434E-8684-63D50BE0CF94) unless noted)
- LISPSYS: 0 or 2 = MBCS (legacy), 1 = Unicode (2021 and later). `(ascii "€")` is 8364 under Unicode, 128 under MBCS. LSP compiled with LISPSYS 1 will NOT load in 2020 or earlier; set 0 or 2 before compiling for old releases.
- 2026 and later: raster images load in the background after a drawing opens. Run IMAGEASYNCWAIT before modifying or plotting. (also [G:945E9BA6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-945E9BA6-A91A-46EA-9394-2D84114842BA))
- 2026 and later: connected support files. Drawings in an Autodesk project on Forma Data Management share one support set; otherwise support paths come from the current user profile. This can change how a script finds support files. (also [G:945E9BA6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-945E9BA6-A91A-46EA-9394-2D84114842BA))
- 2020 and later: INSERT opens the Blocks palette; CLASSICINSERT opens the old dialog; `(initcommandversion 2)` must come before `(initdia)(command "insert")`.
- 2019 and later: LOCALE returns a 2 or more letter ISO 639 code, not a 3-letter code like ENU.
- 2017 and later: CDATE, DATE and the TD* variables resolve to whole seconds; use MILLISECS for finer timing.
- 2016 and later: `osnap` with Quick mode (`qui`) returns nil.
- EPDFSHX was renamed PDFSHX: getvar on the old name returns nil, setvar fails with "AutoCAD variable setting rejected", command gives Unknown command.
- Obsolete commands still work with a period prefix (`.BLIPMODE`); obsolete system variables through getvar and setvar. No guarantee they survive; removed ones cannot be revived.
- Moving to 2027 ([G:E69C877D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E69C877D-F84B-4282-807D-E084C931D533)): ActiveX/VBA programs that assign drawing passwords must change; review every SendCommand for PostCommand; review code from 2014 and earlier for 64-bit; remove IAcadFileDependency and IAcadFileDependencies. .NET and ObjectARX: password, render preset and FileDependencyInfo/FileDependencyManager (AcFileDependencyInfo/AcFileDependencyManager) code must be changed or removed; code for 2018 and earlier must be recompiled. Scripts and action macros: check for deprecated commands and variables. AutoLISP: check osnap use. JavaScript: no change.
- After an upgrade, check that the support search paths (Files tab of Options) still reach every support file, block and resource. ([G:4CD0B52A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4CD0B52A-9D16-455B-BB8D-E7DBC14E75C8))
- API change history: "New and Changed AutoLISP Functions Reference" in Help; ActiveX history in `<drive>:\Program Files\Common Files\Autodesk Shared\acad_aag.chm`; `arxmgd.chm` and `arxref.chm` in the ObjectARX docs folder. ([G:D54B0935](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D54B0935-1638-4F97-8B37-1EC3635A1E71))

### Customization files (CAD Administrator's Guide)
- Tools: CUI (Customize User Interface), ACTRECORD and ACTRECSTOP (Action Recorder), VLISP or VLIDE (Visual LISP editor), VBAIDE; Visual Studio Code with the AutoCAD AutoLISP Extension also edits LSP. ([G:5302AEAE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5302AEAE-B620-46A2-B3B3-6FBD0F7D4059))
- Action macros are XML `.actmx` files; ACTM files from 2024 or earlier must be migrated before they play. Default folder `%AppData%\Autodesk\<product>\<release>\<language>\Support\Actions`. ([G:B07858CD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B07858CD-9B39-42CD-ADF1-D67B61F8B9A5))
- PAT, LIN, PGP and SCR files are plain ASCII. Only the FIRST PGP found in the support search paths loads. The first acad.lin or acadiso.lin and the first acad.pat or acadiso.pat found are used. ([G:5302AEAE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5302AEAE-B620-46A2-B3B3-6FBD0F7D4059), [G:BD3AD667](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BD3AD667-EBFC-4C0A-A691-C07D4436DAB0), [G:BF849DAF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BF849DAF-309D-450C-B418-5D3D9DBCD655))
- SCRIPT and RSCRIPT run `.scr` files in order; old scripts work unless they use deprecated commands or variables. ([G:945E9BA6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-945E9BA6-A91A-46EA-9394-2D84114842BA))
- Customization folders: roaming `%AppData%\Autodesk\<product>\<release>\<language>\`, local `%USERPROFILE%\AppData\Local\Autodesk\<product>\<release>\<language>\`. Use a network location for many seats. ([G:793F049B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-793F049B-E095-4155-B3F2-8F6746F31600), [G:23D6994C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-23D6994C-8923-4EBD-BDD3-D7138AC54556))
- CUIx: CUI, CUILOAD; main and enterprise CUIx set on the Files tab of Options. Resource DLLs per theme: `mymenu_light.dll` for Light, `mymenu.dll` for Dark. ([G:7103E61A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7103E61A-8317-4834-BB00-0FE23AEB020F))
- Tool palettes: default folder `%AppData%\...\Support\ToolPalette\Palettes`; new palettes go to the first writable folder under Tool Palettes File Locations; their source files (blocks, xrefs, images, PAT files) must sit in a shared location; do not share palettes across releases. ([G:B3EE3EDA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B3EE3EDA-2B10-4F0E-B049-7D7A1CE63307), [G:5FE479F3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5FE479F3-9519-4B58-A0EB-70D6CD88E531))

### Plot-to-file drivers and PC3 files (Driver and Peripheral Guide)
- Shipped file-output drivers: Autodesk ePlot (DWF), PDF (a nonsystem driver; OS virtual PDF printers also work), Adobe PostScript (Level 1, Level 1 Plus, Level 2), DXB (16-bit, vectors only, monochrome, no raster or OLE, ignores lineweights), raster formats (PNG, JPEG and others). ([G:AFA15B89](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AFA15B89-A755-4FC1-9A13-E0F6357AE6BD))
- [GUI] A PC3 is made with the Add-a-Plotter wizard (PLOTTERMANAGER; Application menu > Print > Manage Plotters): My Computer > Manufacturer and Model > Import PCP or PC2: Next > Ports: Plot to File > Plotter Name > Finish. Manufacturers: "Autodesk ePlot (PDF)", "Autodesk ePlot (DWF)", "Adobe", "Raster File Formats", "AutoCAD DXB File". A system printer uses Begin page "System Printer"; a network plotter uses "Network Plotter Server" and a `\\server\share` path. No script form is given. ([G:AFA15B89](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AFA15B89-A755-4FC1-9A13-E0F6357AE6BD), [G:B2A1DAC5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B2A1DAC5-BC79-4C1C-8B68-55A35631040F), [G:54FC1E0E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-54FC1E0E-9509-4BED-824D-E38466871494), [G:AC5C2A9B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AC5C2A9B-0D09-4E97-8E53-2B4F68DECAB8), [G:F8C573FB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F8C573FB-F479-441B-9DEE-14EB19268E43), [G:8FD70C14](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8FD70C14-B534-4E2A-BD80-75C0E7416E5D))
- The PC3 General tab is read-only except Description. PC3 files can be shared when driver and model match; system printer PC3s also need the same OS version. After a driver upgrade try the old PC3 first, then make a new one. ([G:4B27DE4E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4B27DE4E-9432-4D94-AB91-C721F584F0EF), [G:D1786BA2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D1786BA2-1CB1-4585-AA6A-6ED8088D4B28))
- Set newer devices up as OS system printers; HDI nonsystem drivers are for legacy devices the OS cannot set up. ([G:FA27DF82](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FA27DF82-E6F4-48AC-A358-D18A61C9035B))
- If a local plotter has both an HDI nonsystem driver and an OS printer, the HDI driver cannot reach the port and output goes through the OS spooler, one way, like plotting to a file. ([G:14600AD1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-14600AD1-9934-4E79-8679-62DB0C479799))
- Over COM, `ConfigName` must name a device or PC3 that exists on the machine; an unset ConfigName plots to the system default device. ([G:B2F56BD0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B2F56BD0-8219-4BA5-9CA5-0740B56C7FA2))

### Install and deployment (admin; [G:99D6F18C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-99D6F18C-0FB5-4B6F-A22D-107497E4CF47), [G:8E385A66](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8E385A66-FEF1-4E9A-9612-DED9B75AD878), [G:8A832346](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8A832346-AE94-4D46-936A-86C7B8C43EF0), [G:0C9D8CB4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0C9D8CB4-6F63-4F1D-AD69-774466F9A304), [G:B8A7B547](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B8A7B547-6783-4C19-A98B-DA9F50A70372), [G:11D681E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-11D681E6-7B6F-4E52-9E70-AA644804D8F4))
- Tools: Desktop Installer (one seat, tailored per user), Online Deployment (identical installs with custom settings and files, Group Policy capable), Network License Manager, Add/Remove Features, CAD Manager Control Utility, the Options dialog and the CUI Editor.
- Rule of thumb: 5 seats or fewer, or remote users = Desktop Installer; more than 5 = online deployment.
- Since 2022 the Network License Manager and the CAD Manager Control Utility (`cadmanager.msi`; Start > Autodesk > CAD Manager Control Utility) are separate downloads.
- Activate within 30 days of first use. Remove the previous release within 30 days of installing the upgrade (unless on Subscription).
- Offline Help installer: `https://www.autodesk.com/acd-helpdownload-enu`.
- Since 2024 the Base Resolution Materials Image Library installs by default and cannot be removed alone; if missing, reinstall or copy the `Autodesk Shared` folder files from another workstation. The Medium Resolution library is a separate download.
