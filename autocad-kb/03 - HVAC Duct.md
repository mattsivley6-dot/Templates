# 03 - HVAC Duct

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

Duct work in AutoCAD MEP 2027 (HVAC workspace, US Imperial): the duct settings each drawing carries (duct system definitions, system groups, routing preferences, Duct Layout Preferences, sizing method), drawing rigid and flexible duct runs, fittings, takeoffs and turning vanes, air terminals and other duct MvParts with flow values, duct sizing (instant sizing, Duct Size Calculator, DDXML round trip), spaces and zones for gbXML load analysis, modifying and checking duct systems, and duct display.
Most duct tasks are documented only through the Properties palette, dialogs and grips. Only a few duct commands have documented command-line prompts; they are in 3.1. The prompt sequence of DUCTADD itself is not documented in any source used for this section.
Legend: [G:xxxxxxxx] links go to the Autodesk AutoCAD MEP 2027 help page; [KB:n] links go to an Autodesk support article (linked, not copied); [AUTO] marks a command-line or scripting note; [GUI] marks a step that needs a dialog, palette or grip.

## Contents
- 3.1 Command reference for scripting
- 3.2 Before the first duct: product, profile, catalogs, template
- 3.3 Duct settings stored in the drawing
- 3.4 Duct Layout Preferences
- 3.5 Duct Properties palette (Add and Modify mode)
- 3.6 Drawing duct runs
- 3.7 Fittings, takeoffs, transitions, custom fittings, turning vanes
- 3.8 Part-choice dialogs and routing failures
- 3.9 Flexible duct
- 3.10 Air terminals and duct equipment (MvParts)
- 3.11 Duct sizing
- 3.12 External duct analysis (DDXML round trip)
- 3.13 Spaces and zones for load analysis (gbXML)
- 3.14 Modifying duct: grips, location, size, system, break and merge
- 3.15 Connectivity checks and xref connections
- 3.16 Duct display, labels, flow arrows, hatching
- 3.17 Symptom index

## 3.1 Command reference for scripting

Key: "prompts documented" = the help gives the command-line sequence. "Name only" = the name appears (often only in page metadata) with no prompts. "Dialog" = the documented flow opens a modal dialog or palette, which blocks an unattended .scr or SendCommand run. No hyphen (dash) command forms, system variables, AutoLISP functions or COM members for duct appear in these sources.

### Command-line forms with documented prompts [AUTO]
- [AUTO] DISPLAYSTRAIGHTCENTERLINES: straight centerlines on elbows, result stored in the drawing. Prompts: domain `c` (Conduit), `d` (Duct), `p` (Pipe) or `a` (All); then `y` to display straight centerlines on all applicable objects. No dialog. ([G:4FA23AC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FA23AC2-D39F-4C6B-B98E-4BE63629E722))
- [AUTO] BREAK (plain AutoCAD) on a duct segment: select the segment, `f`, pick the break point, `@` (second point = first). One break, connectivity kept between the two new segments. No dialog. ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F))
- [AUTO] DUCTVANESADD (named in page metadata; the documented start is: select a fitting > Duct Fitting tab > Duct Vanes panel > Add Vanes). Current vane settings print on the command line. `s` changes settings: radius, arc angle (45 degrees = 1/8 of the circular vane path), number of vanes (equal spacing), mirror current vanes (tees), keep vane path (no = hide path). Then start point = inside corner of the fitting, endpoint = outside corner. If mirroring: start and end of the mirror line. Vanes go on every fitting of the same size and subtype. DUCTVANESREMOVE removes. ([G:F1A76643](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F1A76643-58BE-464E-86B7-AD6E360A972A))
- [AUTO] DUCTCONVERT: AutoCAD line to duct. Select the line(s), Enter; Enter or `n` keeps the line, `y` erases it. Then the Modify Run dialog opens (dialog). ([G:5448A6AC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5448A6AC-D223-4AEE-BD87-130EDBA17426))
- [AUTO] DUCTFLEXADD: flex duct, properties from the palette. During layout `l` (line), `a` (arc), `sp` (spline) switch segment mode; `p` toggles the plane through X, Y, Z. Spline mode asks for a start tangent point and an end tangent point (Enter = none). Enter ends (line or arc: Enter or Close). ([G:7577C1D9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7577C1D9-9900-4E7D-8F49-C249FC4256C6))
- [AUTO] DUCTCUSTOMFITTING (named in page metadata; the documented start is Home tab > Build panel > Duct Fitting drop-down > Duct Custom Fitting): select centerlines (lines, arcs, polylines), Enter; the Create Custom Fitting dialog opens (dialog); after Finish, `y` erases the centerlines, `n` keeps them; Enter. ([G:9A30B6FF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A30B6FF-3139-4A6D-9FAE-E816A95070C0))
- [AUTO] Convert to Flex Duct (right-click menu on a selected polyline, line, arc or spline): Enter or `n` keeps the geometry, `y` erases it. ([G:A983903E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A983903E-912A-42E3-AB00-EF330F629555))
- [AUTO] Takeoff placement (ribbon Duct Fitting tool, Type = Takeoff): after the spot is picked, `Y` or `Z` chooses the rotation axis; Enter ends. Command name not given. ([G:7241CA26](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7241CA26-81C7-410A-BB0A-5E4F6C9D1571))
- [AUTO] Rotate grip on a fitting, takeoff or in-line part: the angle can be typed at the command window. ([G:1AE4B5FA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1AE4B5FA-FC1A-46B6-91B4-66FF60B463E5))

### Palette-driven, dialog, or name-only commands
- [AUTO] DUCTADD (also written DuctAdd): adds rigid duct; all settings come from the Properties palette in Add mode (3.5). A fitting or connection-type override made during the command ends when DUCTADD ends. "About Drawing Ductwork" lists command DUCT in its metadata. Prompts not documented. ([G:DE02A772](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DE02A772-C93A-48F3-A207-2E30A7E8F2EA), [G:09C498A1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-09C498A1-74A1-4CC6-A37A-30EDE81E8607), [G:23ED7114](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-23ED7114-9620-41E5-97F9-983F47CBA9D2), [G:FCC029C0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCC029C0-B289-4968-B13C-21F3DF7B4539))
- [AUTO] DUCTADDSELECTED, DUCTFLEXADDSELECTED: names only ([G:23ED7114](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-23ED7114-9620-41E5-97F9-983F47CBA9D2)). Ribbon Add Selected (Duct, Duct Flex, Duct Fitting, Equipment tabs > General panel) starts a new object from the selected one ([G:DE02A772](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DE02A772-C93A-48F3-A207-2E30A7E8F2EA)). (inference) These are the Add Selected commands.
- [AUTO] DUCTFLEX: name only ([G:1E52BA86](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E52BA86-4D5C-4024-A89F-9D1493313C9D)). DUCTFLEXMODIFY, DUCTFLEXPROPS, DUCTFLEXSTYLEEDIT, DUCTFLEXCONVERT: names only ([G:BE7964FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE7964FC-CD2E-41FD-8CFE-4B6C928B738D)).
- [AUTO] DUCTMODIFY: name only ([G:EE45CEAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE45CEAA-EF11-4671-B530-DDD771A72998)). DuctFittingModify, DuctSystemResizeCalc: named for Transition - Offset fittings, no prompts ([G:86B7661B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-86B7661B-7444-48A6-912D-3DCB41879F60)).
- [AUTO] DUCTLENGTH: name only, lengthen grip page ([G:C5BDD2E7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C5BDD2E7-E453-4563-8F59-A79869C64136)). Ribbon Duct tab > Modify panel > Duct Length opens the Duct Length dialog ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F)).
- [AUTO] DUCTVANES: name on the Modify Turning Vanes page ([G:DAA4FAAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DAA4FAAA-945E-4BC3-AD56-F0306CF6BCDB)).
- [AUTO] DUCTPREFERENCES (DUCTSTYLEEDIT also listed): Duct Layout Preferences dialog. ([G:ECEF01FB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ECEF01FB-8528-4D13-961F-B55DF98448DD), [G:5931AC68](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5931AC68-5627-43B1-AD63-623C08CFC1A9))
- [AUTO] DUCTSYSTEMDEF, DUCTSYSTEMDEFEDIT: duct system definitions in Style Manager. ([G:329A8AE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-329A8AE1-9D9B-4A41-B407-DD76DE5B5F47))
- [AUTO] DUCTSYSTEMSIZECALC: Duct Size Calculator dialog. ([G:066594C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066594C7-8E6C-47B4-8594-89C29C2D69D6))
- [AUTO] DUCTXMLEXPORT, DUCTXMLIMPORT: DDXML dialogs. ([G:08B52ECC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08B52ECC-F47F-4075-BC9D-89CE965A8039), [G:6358DFD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6358DFD5-650D-4B7A-B025-5599DBADA170))
- [AUTO] MVPARTMODIFY: Multi-view Part Modify dialog. ([G:B836B203](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B836B203-E58F-4F8B-998B-5BEEBCE44942))
- [AUTO] GBXMLEXPORT, GBXMLIMPORT: gbXML dialogs. ([G:A0B1F680](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A0B1F680-EA50-404C-80C1-CA0888393F48), [G:A4A0E175](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A4A0E175-1DA6-497A-B510-730EF3C07A7B))
- [AUTO] DUCTCUSTOMFITTINGPROPS, DUCTCUSTOMFITTINGSTYLE, DUCTCUSTOMFITTINGSTYLEEDIT: names only. ([G:9A30B6FF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A30B6FF-3139-4A6D-9FAE-E816A95070C0))
- [AUTO] SLINECONVERT: lines to schematic lines (used when turning exploded duct into a 1-line schematic, 3.16). ([KB:000629105](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-it-possible-to-convert-existing-duct-systems-into-1-line-schematic-undefined-systems-in-AutoCAD-MEP.html))
- [AUTO] UNITS: HVAC "Air Flow Units" set here, dialog only. ([KB:000599508](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-flow-rate-units-in-AutoCAD-MEP.html))
- The command to place a duct MvPart and the one to add a duct fitting are not named in these sources; only ribbon paths are given ([G:7755CBC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7755CBC9-2AEB-4F80-89A5-CD5B46751449), [G:7241CA26](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7241CA26-81C7-410A-BB0A-5E4F6C9D1571)).

### Modal prompts that stop an unattended run
- Choose a Part, Multiple Parts Found, Part Size Not Found, Connection Type Mismatch (3.8). ([G:D8B4F5CB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D8B4F5CB-B0B2-43AC-8A17-23E2FD119F6D), [G:22777004](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-22777004-4E33-42A4-8701-DAA82C6AD0A9), [G:4AC09C1B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AC09C1B-BC44-45F9-A419-4E02957B2B82))
- A message that no layout solution can be found with the parts available for automatic layout, asking what to do next. ([KB:000289163](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-trying-to-insert-tap-into-duct-with-AutoCAD-MEP.html))
- A warning that the selected routing preference has no parts for the current shape, followed by "No Duct Found"; the object is not created. ([KB:000509388](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Conflicting-between-Routing-Preference-and-Shape-when-using-an-MEP-object-command-in-AutoCAD-MEP.html))
- Duct Size Calculator substitute-part prompt: the preferred part cannot be used because of size or angle limits, so pick another. ([KB:000510274](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-size-calculation-in-AutoCAD-MEP-keeps-prompting-you-for-choosing-parts-manually.html))
- Modify Run (after DUCTCONVERT), Maintain Connection (size edits), Save to Xref (connecting to xref duct). ([G:5448A6AC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5448A6AC-D223-4AEE-BD87-130EDBA17426), [G:18B490E5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-18B490E5-20C4-4B3D-B0A0-AD873BC7EC13), [G:EB4AC5CA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB4AC5CA-8873-461B-A7E9-4A80D08673C5))
- (inference) Before a scripted run, put every part, size, angle and connection type it needs into the routing preference so none of these dialogs appears.

## 3.2 Before the first duct: product, profile, catalogs, template
- Run AutoCAD MEP, not plain AutoCAD. Launching the "as AutoCAD" shortcut, or having the plain AutoCAD profile current, leaves MEP commands unknown and MEP tools missing. Check that the title bar names AutoCAD MEP and that OPTIONS > Profiles shows the MEP profile as current. ([KB:000572458](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-Browser-can-t-be-opened-in-AutoCAD-Architecture.html), [KB:000373008](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Detail-Component-Manager-missing-in-AutoCAD-Architecture.html), [KB:000441760](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Contentbrowser-and-other-AutoCAD-Architecture-MEP-specific-commands-do-not-work.html), [KB:000339989](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-MEP-or-Architecture-tools-in-AutoCAD-MEP-or-AutoCAD-Architecture.html))
- The desktop shortcut runs acad.exe with switches that load AecBase.dbx (/ld), pick the MEP profile (/p), the MEP toolset (/product MEP) and the language (/language). Compare a broken shortcut's Target with a working one. ([KB:000339989](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-MEP-or-Architecture-tools-in-AutoCAD-MEP-or-AutoCAD-Architecture.html), [KB:000251041](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Startup-switches-for-AutoCAD.html))
- Set the HVAC workspace current. Duct and equipment tools: Home tab > Build panel, and the HVAC tool palette group ([KB: Adding HVAC Equipment](https://www.autodesk.com/support/technical/article/caas/tsarticles/ts/5qgshFhOVC2zKayLzVwo5f.html), [G:647085B2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-647085B2-580A-43FB-8E82-1F96599E58A7)).
- MEP catalogs: OPTIONS > MEP Catalogs tab. Wrong or empty catalog paths cause the routing preference/shape conflict and "No Duct Found". Fix by resetting settings to defaults, or by adding each catalog (.apc) back from the MEPContent folder under the product's ProgramData folder, for example `<ProgramData>\Autodesk\MEP <version>\enu\MEPContent\Global\Duct\Duct (Global).apc`. ([KB:000509388](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Conflicting-between-Routing-Preference-and-Shape-when-using-an-MEP-object-command-in-AutoCAD-MEP.html))
- Odd duct or conduit sizes in the lists are a profile problem ([KB:000262829](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Odd-pipe-sizes-are-displaying-when-trying-to-run-pipes-in-AutoCAD-MEP.html)).
- Reset to defaults: the "Reset Settings to Default" item in the product's Start menu folder. It offers to back up current settings first, then relaunches and rebuilds the support folders. No command-line switch is given for it. ([KB:000219733](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-Browser-does-not-work-in-AutoCAD-Architecture-or-AutoCAD-MEP.html), [KB:000373008](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Detail-Component-Manager-missing-in-AutoCAD-Architecture.html))
- Tell-tale of the wrong product: in plain AutoCAD an AEC object shows only the General section in Properties and is named AEC_<object> (AEC_WALL), where ACA/MEP show just the object name. ([KB:000466060](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-entries-in-the-properties-palette-when-selecting-an-AEC-object-in-AutoCAD-Architecture-MEP.html)) (inference) MEP duct objects show the same symptom.
- Start from an AutoCAD MEP 2027 template so duct system definitions and routing preferences exist; otherwise import them with Style Manager ([G:E7C4DBC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7C4DBC8-ED10-4641-ACE8-F9F7C831A90F)). The Aecb Model template carries a placeholder routing preference, the "Mechanical - Duct 1-line" display configuration and a Work layout tab with 2 viewports ([G:764224DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-764224DC-22C3-454C-9256-014074EA15BA), [G:A2F7AF29](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A2F7AF29-3741-4E7F-9442-4C4361814A54), [G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE)).

## 3.3 Duct settings stored in the drawing

- Duct layout preferences, duct system definitions and routing preferences are stored in the drawing and can be shared between drawings. Set them up before drawing. ([G:9EE97DB4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9EE97DB4-6044-47DC-B8B9-85AD48C247D7), [G:ECEF01FB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ECEF01FB-8528-4D13-961F-B55DF98448DD), [G:23ED7114](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-23ED7114-9620-41E5-97F9-983F47CBA9D2), [G:939BE697](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-939BE697-29E7-413A-88DC-EDEAE66C72AD))
- Routing preferences apply to every new duct run and set the parts and connections used. The system definition picked when adding a run controls how the run displays. ([G:40F43E02](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-40F43E02-D73A-4958-AE51-D48D53B23641), [G:10758110](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10758110-DAC9-4A4A-9ADA-7CC066558E0D))

### Systems (concept)
- A system is a network of connected parts (duct, fittings, equipment) standing for one real building system. Connected parts share one look. ([G:E7C4DBC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7C4DBC8-ED10-4641-ACE8-F9F7C831A90F))
- New parts inherit the CURRENT system's defaults (size, shape). Changes can be applied to the whole network at once. ([G:E7C4DBC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7C4DBC8-ED10-4641-ACE8-F9F7C831A90F))
- Define a set of systems at project start and keep them. Predefined systems carry a system abbreviation, layer keys and display properties. ([G:E7C4DBC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7C4DBC8-ED10-4641-ACE8-F9F7C831A90F))
- Systems are style based (Style Manager) and come from the AutoCAD MEP 2027 templates. Without one, import definitions from other drawings with Style Manager; more are in System Definitions.dwg in a subfolder of `<ProgramData>\Autodesk\MEP <version>\enu\Styles` ([G:E7C4DBC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7C4DBC8-ED10-4641-ACE8-F9F7C831A90F)). Imperial file: `<ProgramData>\Autodesk\MEP <version>\enu\Styles\Imperial\System Definitions (US Imperial).dwg` ([KB:000446628](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-Part-appears-when-attempting-to-connect-ducts-with-fittings-parts-in-AutoCAD-MEP.html)).

### Duct system definitions
- Holds: layer key style (layer, color, linetype), rise and drop display style, display properties, duct sizing parameters. Name each for its use (supply, return air). Per drawing, shareable; templates ship many. ([G:9EE97DB4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9EE97DB4-6044-47DC-B8B9-85AD48C247D7), [G:4CA2F84D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4CA2F84D-6632-410D-8F3B-5E5FE874B318), [G:2801A5D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2801A5D1-F63A-49B3-85A5-FB41554F4BD6))
- Routing Preferences tab: shows which routing preference the definition uses ("-" means none); an assigned one decides which parts go in as duct is drawn. Duct styles are HVAC duct system definitions. ([KB:000446628](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-Part-appears-when-attempting-to-connect-ducts-with-fittings-parts-in-AutoCAD-MEP.html)) The drop-down ties the system to a default routing preference; the link also shows in the Properties palette and the Modify Run dialog. ([G:E0DF2675](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0DF2675-67B0-4A76-8BC3-027670A9FBFE))
- Changing the system of one segment updates every component validly connected to that segment. ([G:2801A5D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2801A5D1-F63A-49B3-85A5-FB41554F4BD6))
- Create (DUCTSYSTEMDEF, DUCTSYSTEMDEFEDIT) [GUI]: HVAC workspace > Manage tab > Style & Display panel > Style Manager drop-down > HVAC System Definitions. New: right-click "Duct System Definitions" > New > name. Copy: right-click a definition > Copy; right-click "Duct System Definitions" > Paste; right-click the copy > Rename. Then General > Description, the general system properties, and a sizing method. ([G:329A8AE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-329A8AE1-9D9B-4A41-B407-DD76DE5B5F47))
- No Single Line Graphics tab for duct system definitions, by design: single-line graphics is for piping only. ([KB:000553810](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Single-Line-Graphics-tab-is-missing-on-the-Duct-System-Definitions-dialog-box-in-AutoCAD-MEP.html))
- Hatch per system: see 3.16. ([G:A8B0676F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A8B0676F-D2A1-4A0E-A521-67A57EDD3BA0))

### Sizing method: Design Parameters tab [GUI]
- Style Manager > HVAC System Definitions > a definition under Duct System Definitions > Design Parameters tab. ([G:CA33E443](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA33E443-DFA2-4A21-BD90-03B664D018AA))
- Velocity + value = constant velocity method. Friction + value = equal friction method. Roughness = duct material roughness. Density = medium in the system; initial default is air at sea level at 68 F (20 C). Repeat per system, OK. ([G:CA33E443](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA33E443-DFA2-4A21-BD90-03B664D018AA))
- The Add Duct dialog marks the fixed parameter with an asterisk (*). The fixed parameter first gives the exact size, then a catalog size is picked; after sizing, the fixed value shown in Add or Modify dialogs may differ from Design Parameters. ([G:CA33E443](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA33E443-DFA2-4A21-BD90-03B664D018AA))
- Friction and Velocity on the Properties palette are read-only copies of these values. ([G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26), [G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7))
- The Duct Size Calculator can override Velocity or Friction for one run without changing the definition (3.11). ([G:066594C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066594C7-8E6C-47B4-8594-89C29C2D69D6))

### System groups
- A system group ties systems together without changing any system's properties; each keeps its own display. Any number of systems per group. ([G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90))
- Runs with different system definitions cannot connect unless the connecting run's system is changed. Connecting two systems that are NOT in one group prompts you to change the connecting run's system to match the receiving run. Decline: the right fitting is still inserted, but the run is NOT part of the receiving system, so edits to that system skip it. ([G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90), [G:2801A5D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2801A5D1-F63A-49B3-85A5-FB41554F4BD6))
- If dissimilar systems were allowed to connect with no group, the connection is invalid (a solution tip marker shows when solution tips are on). Creating the group later turns those connections valid dynamically. ([G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90))
- Fix: assign one group to several definitions, for example Supply - High Pressure and Supply - Medium Pressure; the runs connect and each keeps its own system. Best set when the systems are created. Mechanical example: one system per zone, grouped as one heating supply. ([G:2801A5D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2801A5D1-F63A-49B3-85A5-FB41554F4BD6), [G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90))

### Routing preferences (duct part routing preferences)
- A routing preference says which duct part to insert; fittings are added automatically as you lay out the run. It holds one or more size ranges of parts and fittings (elbows, tees, cross, takeoff, transitions) organized by nominal duct size. Available parts depend on the connection type (doc example: Slip Joint, by shape, Global profile). Metadata command: DUCTPREFERENCES. ([G:10758110](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10758110-DAC9-4A4A-9ADA-7CC066558E0D))
- Size range rules ([G:10758110](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10758110-DAC9-4A4A-9ADA-7CC066558E0D)):
  - Parts in one size range must share common nominal sizes. The Size Upper Limit list shows only sizes common to all selected parts.
  - The lower limit is the smallest size common to all selected parts (the page says it is "shown in Size Upper Limit").
  - If a mid-range upper limit is set lower than the prior range's upper limit, the ranges swap.
  - Drawings from Autodesk Building Systems 2007 were never validated for common nominal sizes. MEP 2027 validates them on open, which can reset some upper limits and set some parts to *NONE*.
  - The Properties palette size list, when adding a segment, groups nominal sizes by the preference's size ranges.
- Find, apply, change [GUI]: Styles Browser > Object Type > HVAC Objects > Duct Part Routing Preferences; or select a duct > Properties palette > Basic > Dimensions > Routing Preference button. ([G:10758110](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10758110-DAC9-4A4A-9ADA-7CC066558E0D))
- Styles Browser swap: select the object, Properties palette > Routing Preference button, pick one in the Styles Browser (search other open drawings, Content Library drawings, or by name), click Apply Style To Selection. Applying also imports it into the drawing. Works for duct, pipe and conduit. ([G:65A24793](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-65A24793-DB0D-48C8-B6A3-FA5031805C4C))
- Placeholder parts: 1-line, dimensionless parts for preliminary design; segments and fittings are inserted like any other duct. Needs a routing preference that uses placeholder parts; the Aecb Model template has one. Convert later by modifying the part subtype. ([G:764224DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-764224DC-22C3-454C-9256-014074EA15BA))
- Shipped routing preference to borrow: "Generic Flanged" in System Definitions (US Imperial).dwg (above). Copy it into the drawing with Style Manager, assign it as the routing preference of the duct system definition in use, and new duct uses it. ([KB:000446628](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-Part-appears-when-attempting-to-connect-ducts-with-fittings-parts-in-AutoCAD-MEP.html))
- The default duct layer (example M-HVAC-Duct) comes from Layer Keys. ([KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html))

## 3.4 Duct Layout Preferences
- Command DUCTPREFERENCES (dialog). Or HVAC workspace > Manage tab > Preferences panel > Duct, or Properties palette > Advanced > Routing Options > Preferences button. Stored WITH the drawing, shareable. Sets layout preferences for a run and the terminal duct connection types. ([G:ECEF01FB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ECEF01FB-8528-4D13-961F-B55DF98448DD))
- General tab ([G:5931AC68](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5931AC68-5627-43B1-AD63-623C08CFC1A9)):
  - Slope format (stored with the drawing; drives the palette Slope property): Angle (degrees, e.g. 2); Percentage, 100% = 45 degrees; Percentage, 100% = 90 degrees; Rise/Run (fraction like 1/48 or 1/100, shown as a fraction in the palette).
  - Rise and Run units: active only after a slope format is picked; from the current profile and Drawing Setup (Imperial: feet or inches).
  - Constant value: Rise editable only with Rise/Run with Constant Rise; Run only with Rise/Run with Constant Run.
  - Ratio divider: slash (/) or colon (:).
  - Elevation preference: "Automatically create riser at new elevation".
  - Label preferences: a label style (stored in the REGISTRY, not the drawing); None skips the next step. By quantity = labels per straight segment; By distance = interval, a segment shorter than the interval gets none.
  - Flow arrow preferences: same pattern.
  - Elbow layout options: Use Reducing Elbow (one fitting when direction and size both change); Use Reducing Elbow if needed (page wording: "to not add a reducing elbow fitting when the duct size does not change"); Use Straight Elbow and Reducer (two fittings, elbow plus reducer).
- Gotcha: with "Use Reducing Elbow if Needed", a round-to-rectangular tap or a duct ending on an MvPart can fail with the "no layout solution" message, because MEP tries an elbow where a tap or a plain 90 is needed. Fix: set "Use Straight Elbow and Reducer" in DUCTPREFERENCES, or route through an intermediate point before the end point. ([KB:000289163](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-trying-to-insert-tap-into-duct-with-AutoCAD-MEP.html))
- The terminal-duct connection (Flexible, Elbow with Rigid Duct, Extend duct) is also chosen per run on the palette (3.5). ([G:F4589F16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F4589F16-477E-49D5-AD9D-A0461905BD59))

## 3.5 Duct Properties palette (Add and Modify mode)

- The Design tab has Basic (expanded by default) and Advanced (collapsed; click the down arrow). ([G:63906BF0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-63906BF0-280D-4D7F-923E-CE1210FF9625), [G:9787D110](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9787D110-3193-43F4-BA59-6DD87FDAEBE6), [G:F4589F16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F4589F16-477E-49D5-AD9D-A0461905BD59))
- Palette edits apply only to the selected objects, NOT to other connected objects in the system. With several objects selected, only shared editable properties show; differing values show *VARIES*. ([G:1F826880](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1F826880-6322-48A5-BBF0-C85483E31B02), [G:9B7F778C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9B7F778C-40F1-48E0-B9AD-FEFF4D400664), [G:31E0D398](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-31E0D398-44B0-486D-9B4D-61B3A7AAD668))
- The palette Display tab edits display components (contours, center lines) in the current display representation, optionally in others too. ([G:1F826880](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1F826880-6322-48A5-BBF0-C85483E31B02), [G:9B7F778C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9B7F778C-40F1-48E0-B9AD-FEFF4D400664), [G:31E0D398](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-31E0D398-44B0-486D-9B4D-61B3A7AAD668))

### Add mode, Basic ([G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26))
Page marks: * only when adding duct, ** only flex duct, *** only fittings.
- General: Description (optional). System (default Standard; others from the catalog; an icon beside it searches, imports and adds a system definition through the Styles Browser, [G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95)). ***Part (image opens the Select a Part dialog). ***Current Size (drop-down; sizes are standardized).
- Dimensions:
  - Routing preference: default Standard (Styles Browser icon beside it, [G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95)).
  - Shape: default Rectangular, afterwards the last used shape.
  - Size: within the range of the current routing preference. Rectangular and Oval = Width and Height; Round = Diameter. Default = last used.
  - Calculate Size: sizes from Flow Rate, Friction, Roughness, Density. Rectangular or Oval: one dimension must be fixed to calculate the other.
  - Size lock: Unlocked (default) / Locked.
  - ***Connections: customize sizes of the fitting being added.
  - *Flow Rate: read from MvParts connected to the run, or typed. Default 0. Refreshes automatically when connected to an MvPart.
  - *Friction, *Velocity: read-only, from the Duct System Definition.
  - Cut Length: No (default) hides it; Yes lets you enter a length, which splits the duct into shorter pieces ([G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95), [G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F)).
- Placement: Elevation (Z above or below the XY plane of the current UCS; default 0, then last used). Elevation lock: Unlocked (default) / Locked; resets to OFF every time you add duct ([G:1747B47F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1747B47F-8F85-4BE9-84AD-E08E7A5DBE33), [G:320071DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-320071DC-E53C-46A4-A7C5-AB74CDC83A9C)). Start elevation (connector 1; same as Elevation; default 0).
- Justification: Justify = Top Left, Top Center, Top Right, Center (default), Center Left, Center Right, Bottom Left, Bottom Center, Bottom Right. Horizontal offset, Vertical offset: default 0, then last used.
  - Justify applies only while creating. It is not reflected in Elevation when the duct is reselected; the stored elevation always refers to the duct center. ([KB:000556470](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Justification-when-creating-ducts-in-AutoCAD-MEP.html))
- Routing:
  - *Bend method: Elbow (default), Offset, Transition - Offset.
  - *Bend method lock: Unlocked (default) / Locked; shown only for Offset or Transition - Offset. Unlocked = reverts to Elbow after one such bend is inserted.
  - *Bend angle: values come from catalog content. *Bend angle lock: button shown only for user defined angles.
  - **Segment: Line, Arc, Spline. **Radius factor: radius value when Segment = Line.
  - *Branch fitting: Takeoff or Tee.
- New Run icon (palette): ends the current run and starts a new one. ([G:8BDDB3DD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8BDDB3DD-AE44-4BEE-923D-DAB89E5C16D5))

### Add mode, Advanced ([G:F4589F16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F4589F16-477E-49D5-AD9D-A0461905BD59))
- Connection details: opens the Connection Details worksheet.
- Lining thickness, Insulation thickness: default 0.
- Assigned engineering ID (fittings; page spells it "Assinged"): fitting ID used for fabrication; holds the ASHRAE fitting number (3.12).
- Slope format: Angle; Percentage (100%=45); Percentage (100%=90); Rise value/Run value. Preferences button edits it in Duct Layout Preferences.
- Slope: default 0 (rise/run in earlier releases). Changing slope while adding parts to a run inserts a fitting to adjust the slope.
- Branch fitting: Tee or Takeoff. Terminal-Duct connection: Flexible; Elbow with Rigid Duct; Extend duct.
- Fitting settings: opens the Fitting Settings dialog (override parts, 3.6). Preferences: opens Duct Layout Preferences.
- Labels Style and Flow arrows Style: *NONE* (default), By Quantity, By Distance, as this page lists them. The label task pages treat style and layout method as separate fields ([G:ADA2A49E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ADA2A49E-3F61-4C48-A929-0AD33E821AEA), [G:45C53834](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45C53834-08D5-4AAA-9D6E-782DECFACC23), [G:3C1E794E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C1E794E-9799-4084-B96C-90AEF5B89467)).
- Graphics (flex): flex pattern. Vanes (fittings): Yes (default) / No (row mislabeled "Graphics" on the page).

### Modify mode, Basic ([G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7))
Page marks: * flange connection type related, ** takeoff fittings, *** flex duct; marked rows show only for that kind of object.
- General: Description, Layer (layer style of the object), System.
- Dimensions: Routing preference, Shape, Size, Duct Calculator (same inputs as Calculate Size), Size lock (prevents nominal size edits while modifying the run).
- Sizing: Flow Rate (read from the connected MvPart; 0 with none connected); Friction (read-only, from the system); Velocity (row text repeats the System description, likely a copy error (inference)); Cut length (reported length).
- Placement: Elevation; Start elevation and End elevation; Move attached segments (default Yes); Additional information (opens the Location worksheet, 3.14).
- Routing: Slope format and Slope, display only.

### Modify mode, Advanced ([G:004D52D0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-004D52D0-AA1E-4CDF-B90B-3D91409D209E))
- Connection details; Lining thickness and Insulation thickness (current segment); Takeoff Position (opens the Takeoff Position dialog; the row shows only if takeoff fittings exist in the drawing, [G:87730B56](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-87730B56-1086-4457-A3C3-9E7F104726BF)); Assigned Engineering ID; Vanes On/Off; Slope format and Slope (not editable).
- Flange extension and Flange thickness: depend on duct shape; segments and fittings of the same shape share the values.
- Flex only: Graphics (pattern), Pitch, Geometry (vertex editing, 3.9).
- [G:004D52D0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-004D52D0-AA1E-4CDF-B90B-3D91409D209E) and [G:F4589F16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F4589F16-477E-49D5-AD9D-A0461905BD59) share the title "About Advanced Properties". Which is Add and which is Modify is read from their related-topic links (inference). Their asterisk legends do not match every row; go by property names.

### Flow Rate notes
- [KB:000619735](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-Enter-Flow-Rate-in-AutoCAD-MEP-Properties.html) ("Unable to enter flow rate") answers only that Flow Rate is read from MvParts connected to the run or can be entered, and defaults to 0 with no MvPart connected. ([KB:000619735](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-Enter-Flow-Rate-in-AutoCAD-MEP-Properties.html))
- New duct from the "+" (Add) grip comes out a different size than the selected duct: while drawing the new run, switch off the automatic sizing toggle beside the diameter field so the size you set is kept. ([KB:000578024](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/When-adding-a-duct-to-an-existing-one-the-size-is-wrong-in-AutoCAD-MEP.html))
- Flow on air terminals and VAV boxes is set in the MvPart dialogs, Flow tab (3.10).

## 3.6 Drawing duct runs

### Order of work
- Duct system workflow ([G:8063EAD9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8063EAD9-7E4E-405E-826E-22B1D29922C9)): (1) preliminary 1-line design; (2) lay out equipment (diffusers, VAV boxes, coils, dampers) as HVAC parts; (3) draw duct to connect it; (4) size duct: verify flow values, calculate sizes; (5) modify and recalculate as needed; (6) label, flow arrows, schedules; (7) refine with grips without breaking connections.
- Mechanical workflow ([G:53FA9DB5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-53FA9DB5-6CCA-41CB-A1EB-2067BDC3E04D)): define HVAC design parameters (routing and auto-layout behavior, sizing parameters, rise and drop display style); define a project (tool catalogs); link floor plans (Project Navigator, attach the architectural plan as an xref); add spaces (room takeoff, gbXML); loads with a 3rd-party tool.
- Insert the architectural floor plan as a reference, then add equipment, then duct runs ([G:DE02A772](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DE02A772-C93A-48F3-A207-2E30A7E8F2EA)). Equipment first, duct second ([G:FCC029C0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCC029C0-B289-4968-B13C-21F3DF7B4539)). Set design preferences and system definitions before drafting ([G:939BE697](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-939BE697-29E7-413A-88DC-EDEAE66C72AD)).

### Ways to start adding duct, HVAC workspace ([G:DE02A772](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DE02A772-C93A-48F3-A207-2E30A7E8F2EA))
- Home tab > Build panel > Duct drop-down > Duct. Home tab > Build panel > Duct Fitting. Home tab > Build panel > Equipment drop-down.
- Add grips on duct objects.
- Type DuctAdd at the command line [AUTO].
- Select a duct object > Duct, Duct Flex or Duct Fitting tab > General panel > Add Selected. Select an MvPart > Equipment tab > General panel > Add Selected.
- Duct tool palette tool. A tool with a predefined system (example Supply - Low Pressure) gives the duct that system's design parameters, display properties and rise and drop style. ([G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95), [G:CD1FF206](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD1FF206-BB7F-455E-83CE-189BD1424B83))
- Styles Browser [GUI]: Home > Tools > Styles Browser > Object Type > HVAC Objects > Duct; Drawing Source and Drawing File drop-downs; Search by name; pick in the gallery; one icon imports into the drawing, another starts drawing with it. Home > Tools > Styles Browser > Object Type > Duct > Gallery adds a duct with a predefined system directly. ([G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95))

### To draw a duct run with the Properties palette ([G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95)) [GUI]
1. Open the palette (Duct tool, ribbon, or an Add grip on a part, fitting or segment).
2. Description, System.
3. Routing preference, Shape, Size. Instant sizing (calculator button):
   - Round: accept or type Flow rate, click calc; Diameter fills.
   - Oval or rectangular, fixed height: set Height, calc gives Width; repeat to tune. Fixed width: set Width, calc gives Height.
   - Outlets not yet connected: click the icon, choose Add or Remove, pick single flow devices; flow = their sum; calc.
   - Friction and velocity are read-only and refresh when flow rate changes.
4. Specify Cut Length = Yes plus a Cut Length value splits the duct into shorter pieces.
5. Elevation:
   - Defined elevation: pick an elevation name.
   - Relative to a wall, duct or other object: type the elevation, set justify and offset, pick points on the object with AutoCAD or MEP snaps.
   - Branch on a riser at an elevation: type it, MEP snap a point on the riser. Branch from a vertical run: type it, MEP snap on the vertical run.
   - Extend a sloped duct to an elevation: type it, set Slope format and Slope, MEP snap the sloped duct endpoint.
   - With the elevation LOCKED, a duct that connects to an object does NOT inherit the object's elevation.
6. Offset: horizontal = Left, Center or Right justification plus distance from the wall or object; vertical = Top, Center or Bottom plus distance from the ceiling or object.
7. Bend method and angle:
   - Default: every bend is an elbow.
   - Fixed: choose offset or transition-offset and click the Lock icon beside bend method; all bends use it.
   - Mixed: pick elbow, offset or transition-offset from the drop-down as you draw; no choice = elbow.
   - Bend angle: pick a predefined angle; or User Defined and pick a point (with or without the Compass); or type a value. Lock icon beside bend angle holds it for later segments.
8. Pick a start point, keep picking points. Connection fittings are inserted as you draw.
9. Change elevation and keep picking. A vertical segment is added by default when the elevation changes.

### Auto layout
- You pick points; segments and fittings are inserted automatically. Which ones is set beforehand by the duct layout preferences and routing preference. Helpers: compass (angle), tracking lines (alignment), MEP snaps (connectors or geometric points). ([G:BCD0871A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BCD0871A-CC82-4C37-B25E-23770AE5EACF))
- Rise and drop symbols are inserted as needed from the rise/drop style of the run's system. Same process for 1-line and 2-line. Runs can go in all 3 dimensions. ([G:FCC029C0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCC029C0-B289-4968-B13C-21F3DF7B4539))

### Start a run from existing duct ([G:95A99724](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-95A99724-310E-42BB-B2A9-02AE67E9DE15))
- At a duct end: hover the end until the duct END connector snap shows, click. The new run takes the existing size and system. A different size or shape inserts a transition; if the layout preference has no suitable transition, you are prompted to choose a part.
- Along a segment: hover until the duct CURVE connector snap shows, click. A takeoff or tee is inserted per the connection type in the layout preference.
- End a run on existing duct: hover until a curve or end connector shows, click.
- END connectors sit at object ends; CURVE connectors sit at any point along a segment. ([G:F42E3857](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F42E3857-8F0F-4B3A-9541-33FCD94D399B))

### Connect a run to equipment ([G:CD1FF206](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD1FF206-BB7F-455E-83CE-189BD1424B83))
- Starting or ending on an MvPart snaps to its nearest connection point. Simple MvParts (terminals, fans, humidifiers) have one; complex ones several; some span domains (furnace: duct and pipe).
- With MEP snaps on, click the start point at the MvPart connector, keep picking, Enter to end. Default direction comes from the connector, normally perpendicular to its face.
- The MvPart connector type and the drawing's connector rules decide which segment type can attach. The equipment must already be in the drawing.

### Add grips ([G:68589CA2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68589CA2-23DE-4959-BD2E-51F9241B8B8C), [G:73D20042](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73D20042-79CD-40E3-B515-AE94BABEB76D)) [GUI]
- Add grips start a run with guaranteed connectivity: segment end; segment midpoint (tee or takeoff per Fitting Settings); MvPart connection; on a fitting, the grip pointing the way the new run goes.
- An elbow's add grip turns the elbow into a tee and starts the run from the new connection; existing branches stay connected.
- From an MvPart you must pick a system; from a segment or fitting the run inherits it.
- Changing size before the first segment inserts a transition after the first point; if the routing preference has none, you are prompted to choose a part.
- Ctrl+click the Add grip on an MvPart or duct segment starts flex duct. ([G:7577C1D9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7577C1D9-9900-4E7D-8F49-C249FC4256C6))

### Elevation lock
- OFF by default every time you add duct. ON keeps the run at one elevation, so it will not snap to or connect with objects at another elevation; turn it off before connecting. Can be on for part of a run. ([G:320071DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-320071DC-E53C-46A4-A7C5-AB74CDC83A9C), [G:1747B47F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1747B47F-8F85-4BE9-84AD-E08E7A5DBE33))
- Toggle while drawing: lock button beside the elevation value in the palette ([G:1747B47F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1747B47F-8F85-4BE9-84AD-E08E7A5DBE33)). After placement: Properties palette > Placement > Lock/Unlock; a mixed selection shows "Varies", and clicking it locks all ([G:ECD2BA92](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ECD2BA92-B471-4E1F-BA81-4AE212D00488)).
- Horizontal into vertical duct: hover the vertical segment for a curve connector, click; use a side or isometric view if it fights you. ([G:1747B47F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1747B47F-8F85-4BE9-84AD-E08E7A5DBE33))

### Vertical and sloped runs
- Vertical: pick where the vertical segment starts, set the Elevation of its endpoint in the palette, keep picking. ([G:CFF47BCB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFF47BCB-F1E4-4F36-94CE-43C24C62C28C)) Layout preference "Automatically create riser at new elevation". ([G:5931AC68](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5931AC68-5627-43B1-AD63-623C08CFC1A9))
- Sloped: stop where the slope begins; palette Routing Options: Slope format and Slope; pick the end of the sloped segment. Slope 0 returns to level. A vertical segment at the end of a sloped one may prompt for a part; if no fitting has the angle, accept the custom transition offered. ([G:6A891AEB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6A891AEB-0DA3-49D8-9CC6-A761929A5C43))

### Parallel runs and offsets from geometry
- Parallel run ([G:A2F7AF29](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A2F7AF29-3741-4E7F-9442-4C4361814A54)): begin a run, then set the palette offset. Horizontal offset = same elevation, shifted in X or Y (+ = +X/+Y, - = -X/-Y). Vertical offset = same X-Y, other elevation (+ = +Z, - = -Z). Pick a point on the existing run (MEP snaps pick duct connectors; object snaps pick points on geometry), keep picking.
- Easier when the existing run shows 1-line: switch to the "Mechanical - Duct 1-line" display configuration (default Aecb Model template). ([G:A2F7AF29](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A2F7AF29-3741-4E7F-9442-4C4361814A54))
- The pipe version of this task adds: turn OFF Object Snap and Object Snap Tracking, start on the end connector of the existing run, and at elbows pick only the curve connector (at the logical intersection of the fitting centerlines) so the offset holds; runs drawn close together can merge when plotted at small scale ([G:91F68772](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-91F68772-247F-4D9D-A710-1B81E43593D4)). The duct page does not say this; (inference) the same technique applies to duct.
- Offset from existing geometry ([G:2662D03D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2662D03D-907F-40A3-A837-C6B93E0627BE)): AutoCAD lines or blocks, MEP building objects, MEP objects, including geometry in a reference drawing. Properties palette > Placement > Justification > Horizontal Offset or Vertical Offset (same sign rules), then pick points with object snaps or the "Offsetting Duct From Existing Geometry" snaps.

### 1-line duct ([G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE))
- Undefined duct shown as one line: a placeholder for preliminary routes and for connecting equipment before parts are chosen.
- Start from an MvPart Add grip, or the 1-Line tool on the Duct tool palette (HVAC tool palette group). Check that Shape (palette) and Connection Type (Duct Routing Preference) are both Undefined. Set System and Elevation (from an MvPart Add grip it takes the MvPart elevation).
- Pick points. At a part on another elevation several routing options may appear; preview with 2 viewports (Aecb Model template Work layout tab).
- Enter, then start a new Duct Run for branches (MEP snaps on segments, or Add grips). 1-line fittings: 1-Line tool on the Fitting tool palette.
- Check connectivity: select a part > right-click > Connected Objects > Show Connected Run. Any unconnected part makes duct size tools fail or give wrong results.
- The Duct Size Calculator converts a 1-line system to sized 2-line (3.11). ([G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE), [G:9D9C77E6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D9C77E6-5EE5-4C37-91D2-C963648F77F1))
- A 1-line duct object is not a schematic line: it is a placeholder for a sized 2-line duct and converts directly to one of a set size and shape. ([G:FCC029C0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCC029C0-B289-4968-B13C-21F3DF7B4539), [G:8D3D71FA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D3D71FA-1738-4309-BCFB-2F9965C9AAB8))

### Override a fitting during layout ([G:09C498A1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-09C498A1-74A1-4CC6-A37A-30EDE81E8607))
- Overrides the routing preference for the current run (example: flange connections instead of the default slip joint).
- While adding duct: Properties palette > Advanced > Routing Options > Fitting Settings button (dialog). Pick the Connection Type; to change a part, select the fitting type and pick a part from the list. Lay out the run; the override part is inserted automatically.
- Lasts only until DUCTADD ends. The next DUCTADD uses the routing preference defaults again. [AUTO]

### Connectors and connection types ([G:48B543C4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-48B543C4-DF20-4494-A891-4C67E8197863))
- Connectors sit at each end of segments and fittings and let segments, fittings and duct MvParts form one intelligent system.
- MvPart and fitting connectors carry a connection type. Duct segments have NONE: they inherit the connection type of the connected fitting.

## 3.7 Fittings, takeoffs, transitions, custom fittings, turning vanes

### Add a fitting by hand, takeoff example ([G:7241CA26](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7241CA26-81C7-410A-BB0A-5E4F6C9D1571)) [GUI]
- Fittings normally insert automatically per the layout preferences; add one by hand when it is not in them. ([G:FCC029C0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCC029C0-B289-4968-B13C-21F3DF7B4539))
- Tools palette > Fitting > Takeoff, or Home tab > Build panel > Duct Fitting.
- Properties palette > General > click the part image > Select a Part dialog > Type = Takeoff > pick > OK. Pick Current Size. Click a spot along the segment.
- Right-click menu: Compass toggles the compass; Slide drags the fitting along the segment.
- Rotation: right-click rotate Y or rotate Z, drag and pick, or type an angle. On the command line `Y` or `Z` picks the axis. Enter ends.
- Off-center while adding: right-click > Offcenter, or Advanced > Takeoff Position > Offcenter. The Offcenter tab (Add Duct Fittings dialog) opens with "Enable offcenter placing" checked. Cells: Side (center, top, bottom, left, right; left and right follow the direction the segment was drafted); Justification (left, center, right, top, bottom, by side); Offset (distance measured from the justification); Rotate Around X (click, drag or type), Y and Z (right-click rotate Y / rotate Z or the Y / Z values).
- Rotate the takeoff later with its Rotate grips.

### Takeoffs, concept ([G:0D6B31FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D6B31FD-F755-4AF9-A831-9FB433CA1391))
- A takeoff puts a fitting at any spot on a segment. It attaches to the segment center line or curve, then rotates to a set angle around the segment.
- Off-center = attached away from the center line (example: side of the duct above the center line). Offset distance = segment center line to takeoff fitting center line.
- Tip: attach takeoffs in an isometric view.
- The palette Branch fitting setting (Takeoff or Tee) decides which one a branch gets. ([G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26))

### Move an off-center takeoff ([G:87730B56](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-87730B56-1086-4457-A3C3-9E7F104726BF), [G:D7A02257](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D7A02257-5F0F-43CC-9EFC-1EE31EF92118)) [GUI]
- Switch to a 3D view first. Select the takeoff > Properties palette > Advanced > Takeoff Position (row shows only if takeoffs exist in the drawing). Opens the Takeoff Position tab (Duct Fitting Properties).
- Fields: Side (center, top, bottom, left, right); Justification (center, top, bottom, left, right, by side); Offset; From (Start, Mid Point, End), To (Starting Edge, Center, Ending Edge), Distance; Flip X, Flip Y, Flip Z (rotation along the segment; display may not change for some axes and positions). A new rotation angle can also be set here.

### Transition - Offset fittings ([G:86B7661B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-86B7661B-7444-48A6-912D-3DCB41879F60))
- Edited with DuctFittingModify and DuctSystemResizeCalc (no prompts given) through the fitting's geometric parameters: l length; x or l2 tap length; e horizontal offset; f vertical offset; b rectangular duct width; a rectangular duct height; d oval duct width; c oval duct height.
- If the fitting was not created as "DIN Transition - Offset", offset distance and direction change with the eccentricity value.
- Resizing one duct re-adjusts the fitting parameters and moves the other duct. The fitting is removed when the two ducts are resized equal.

### Custom fittings ([G:9A30B6FF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A30B6FF-3139-4A6D-9FAE-E816A95070C0), [G:D03CAF9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D03CAF9C-4ED7-4F2C-AD8A-B34C1BBCAB18))
- For fittings not in the part catalog or for unique designs. Converts lines, arcs and polylines into an MEP object with connectors; size, shape and system definition are inherited from the connecting parts.
- Style based: each custom fitting is one style (Style Manager). It CANNOT be added to a part catalog; reuse by copy and paste between drawings.
- Steps: (1) draw centerlines (drawn from the endpoints of an existing duct, that end segment inherits the duct's shape and size); (2) Home tab > Build panel > Duct Fitting drop-down > Duct Custom Fitting (DUCTCUSTOMFITTING); (3) select, Enter; (4) Create Custom Fitting dialog: name and system; (5) per segment, shape and size at start and end, Mitered End where needed (the Object Viewer highlights the current segment); (6) "Apply to All Segments" if all match (this disables Next); (7) Next for a segment that differs; (8) Finish, then `y` erases the centerlines, `n` keeps them; (9) Enter.
- Missing size or shape on any segment: no fitting, error "Missing Size or Shape Information".
- AutoCAD commands on a custom fitting: EXPLODE once gives the active view block, twice gives the linework. ERASE, MOVE, ROTATE, ROTATE3D and SCALE break system connections. COPY, MIRROR, OFFSET and ARRAY keep the part properties and property sets. ([G:D03CAF9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D03CAF9C-4ED7-4F2C-AD8A-B34C1BBCAB18))

### Turning vanes ([G:F1A76643](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F1A76643-58BE-464E-86B7-AD6E360A972A), [G:DAA4FAAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DAA4FAAA-945E-4BC3-AD56-F0306CF6BCDB))
- Annotation, not objects. Command-line flow in 3.1 (DUCTVANESADD).
- Add Vanes from the ribbon puts vanes on every fitting of the same size and subtype; the vane graphic is added to the fitting style. The number and layout of vanes CANNOT be changed once added.
- Per fitting: select fittings, Properties palette > Advanced > Vanes Yes or No (Add mode default Yes).
- Remove: Duct Fitting tab > Duct Vanes panel > Remove Vanes, or Vanes = No. The page puts two headings ("from all fittings of the same size and subtype", "from selected fittings only") over one list; (inference) Remove Vanes acts on all fittings of that size and subtype, Vanes = No on the selection only.

## 3.8 Part-choice dialogs and routing failures

Fittings insert automatically per the current preferences, but you can be asked for a part that is not in the current routing or part preference. Every one of these is a modal dialog. ([G:24B53791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24B53791-3230-42F3-84A2-99D462ECA392))

### Choose a Part ([G:D8B4F5CB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D8B4F5CB-B0B2-43AC-8A17-23E2FD119F6D)) [GUI]
- Shows when you add or modify a part in a run that is not in your preferences, so you pick a catalog substitute.
- When it shows (adding / modifying):
  - Part not in the current routing preference: yes / yes.
  - Preference has the part but not the angle: yes / yes.
  - Part size not in the preference: yes, you are asked to select a reducer / yes.
  - Extra part needed and your reducer does not meet the size: no / yes (a reducer is added automatically).
  - Different connection types (example slip joint and flange) not in the preference: no / no. When adding, the Connection Type Mismatch dialog appears instead: choose whether to change the connection type of the new segment or of the last segment.
- When modifying, the dialog zooms to the part needing action; the view returns after you pick. The last choice per domain is remembered; it can be made the default.
- The pick applies only to that location. If the Add command is still running and the case repeats, you are asked again.
- If the preferred part or connection type is not offered, click Cancel and add the fitting by hand.
- Connecting objects with different connection types or unaligned centerlines can ask several times; the chosen parts build one or more routing solutions.

### Multiple Parts Found ([G:22777004](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-22777004-4E33-42A4-8701-DAA82C6AD0A9)) and Part Size Not Found ([G:4AC09C1B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AC09C1B-BC44-45F9-A419-4E02957B2B82)) [GUI]
- Multiple Parts Found: the fitting being added exists in more than one size; pick one. When modifying, the view zooms to the spot; clear "Zoom to the object" to stop that (remembered).
- Part Size Not Found: the size you set does not meet the catalog criteria (shown at the top, example a takeoff height not matched by the part filter). Choices: pick a size and "Use selected part size from catalog"; "Create custom sized part" (keeps your values); "Undo change".

### "Choose Part" keeps coming back ([KB:000446628](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-Part-appears-when-attempting-to-connect-ducts-with-fittings-parts-in-AutoCAD-MEP.html), MEP 2021-2027)
- Repeats while connecting, adding or extending duct when the part or angle you need is not in the catalog and routing preference, or when a parametric part has no insertion behavior set.
- Look at the duct system definition's Routing Preferences tab in Style Manager ("-" means none is assigned). Then add the routing to a routing preference, pick one of the offered parts, build a part that fits, fix the insertion behavior, or borrow "Generic Flanged" (3.3).

### Routing preference and shape conflict, then "No Duct Found" ([KB:000509388](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Conflicting-between-Routing-Preference-and-Shape-when-using-an-MEP-object-command-in-AutoCAD-MEP.html), MEP 2021-2027)
- DUCTADD or PIPEADD warns that the routing preference has no parts for the current shape, then reports that no duct of that shape and connection type is in the catalog. Nothing is created.
- Usual cause: the MEP catalog paths in Options are wrong or empty. Reset settings, or add the catalogs back (3.2).

### Other routing failures
- "A layout solution cannot be determined...": round-to-rectangular tap or a duct with an MvPart on one end; see 3.4 ([KB:000289163](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-trying-to-insert-tap-into-duct-with-AutoCAD-MEP.html)).
- Duct Size Calculator asks for parts on each new system: see 3.11 ([KB:000510274](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-size-calculation-in-AutoCAD-MEP-keeps-prompting-you-for-choosing-parts-manually.html)).
- DW144 Rectangular Duct Square Elbow Flanged has one connector on the outer side of the elbow in MEP 2025 and 2026; the article's fix is to use the MEP 2026 Global profile ([KB:000578727](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/DW144-Rectangular-Duct-Square-Elbow-Flanged-shows-incorrectly-in-AutoCAD-MEP-2025.html)). Per the MEP 2027 fixed-issues list, the elbow's geometry and connector placement are fixed in 2027 ([KB:000646540](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-2027--Fixed-Issues.html)).

## 3.9 Flexible duct

### Concept ([G:1E52BA86](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E52BA86-4D5C-4024-A89F-9D1493313C9D), [G:DD190ABA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DD190ABA-7D1A-4599-A72E-516899C8CAAC))
- Flex runs connect to rigid runs, equipment and MvParts. Flex is usually round, so the right transition is inserted where it meets another shape.
- A system can be assigned to flex like rigid duct; flex and rigid can share one system.
- Segment modes while drafting: Line, Arc, Spline (palette Segment; Radius factor for Line). ([G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26))
- Display components: Contour, Contour - Details (interior contour lines), Connector (lines at start and end), Annotation (graphics pattern).
- Flex Graphics tab: changes the flex annotation pattern and its pitch (interval between pattern repeats, based on drawing scale) in 1-line and 2-line display representations.
- Terminal-Duct connection = Flexible on the palette connects terminals with flex. ([G:F4589F16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F4589F16-477E-49D5-AD9D-A0461905BD59))

### Draw flex duct, DUCTFLEXADD ([G:7577C1D9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7577C1D9-9900-4E7D-8F49-C249FC4256C6))
- Styles Browser [GUI]: Home > Tools > Styles Browser > Object Type > HVAC Objects > Duct Flex; Drawing Source, Drawing File, Search; pick in the gallery; import, then draw.
- Palette route: Home tab > Build panel > Duct drop-down > Flex Duct; or the Flex Duct tool on the Duct tool palette; or Ctrl+click the Add grip on an MvPart or duct segment.
- Set description, system, routing preference, diameter, elevation.
- Line segment mode offsets: horizontal = Left, Center or Right Justification plus distance from a wall or horizontal object; vertical = Top, Center or Bottom plus distance from the ceiling or vertical object.
- Routing icons Line, Arc, Spline. Justification and Radius do not apply to Arcs and Splines.
- Pick a start point (Spline: start tangent point or Enter for none), keep picking. [AUTO] `l`, `a`, `sp` switch segment mode; `p` toggles the plane through X, Y, Z.
- Line and arc segments join into ONE segment of the run; spline segments stay separate.
- End: Enter. Spline: end tangent point or Enter for none. Line or arc: Enter or Close. New Run (palette) ends the run and starts another without leaving the command.

### Convert geometry to flex ([G:A983903E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A983903E-912A-42E3-AB00-EF330F629555))
- Make the curve with AutoCAD Fillet or Spline. Select the polyline, line, arc or spline > right-click > Convert to Flex Duct. Enter or `n` keeps the geometry, `y` erases it. Edit flex properties in the palette afterward. DUCTFLEXCONVERT is listed in metadata ([G:BE7964FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE7964FC-CD2E-41FD-8CFE-4B6C928B738D)); (inference) it is the typed form.

### Modify a flex layout ([G:BE7964FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE7964FC-CD2E-41FD-8CFE-4B6C928B738D))
- By vertices (Spline mode only): select the flex segment > Properties palette > Advanced > Geometry; arrows step along the spline; enter X, Y, Z for the vertex.
- By grips (any mode): click the location grip to move the segment or a control point. After clicking, Ctrl ONCE keeps the connection with the MvPart; Ctrl TWICE breaks it.
- Elevation grips are not available on flex or sloping duct segments. ([G:6FB70D2C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6FB70D2C-0D69-4030-9AFB-621DB9071277))

### Flex shows solid ([KB:000615813](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Flex-Duct-shows-up-as-solid-in-AutoCAD-MEP.html))
- Cause: visual style. Fix: use the Wireframe visual style.

## 3.10 Air terminals and duct equipment (MvParts)

- MvParts can be placed standalone, connected to duct runs, or added in-line or anchored on a duct. ([G:72F3C98B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-72F3C98B-0C29-41FD-8A98-3194DBC41474))
- Terms: "targets" receive air and "sources" distribute it; example: target = air terminal, source = VAV box. ([KB: Adding HVAC Equipment](https://www.autodesk.com/support/technical/article/caas/tsarticles/ts/5qgshFhOVC2zKayLzVwo5f.html))

### Place a duct MvPart ([G:7755CBC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7755CBC9-2AEB-4F80-89A5-CD5B46751449)) [GUI]
- HVAC workspace: Home tab > Build panel > Equipment drop-down (air handler, air terminal, fan, damper, VAV unit) or the Equipment tab of the tool palettes ([KB: Adding HVAC Equipment](https://www.autodesk.com/support/technical/article/caas/tsarticles/ts/5qgshFhOVC2zKayLzVwo5f.html)). The Add MvParts dialog opens on the catalog folder tied to that tool.
- Part tab: pick a part subtype; Details shows sizes; "Display/Hide additional parameters" expands the parameter table.
- Part Filter tab: criteria under "Filter by Dimensions". Part catalogs and content locations decide what can be added; a missing part means building a custom part with Content Builder.
- Choose Part Size Name; set Elevation.
- Flow tab (only when airflow can be assigned): outlet devices get a Flow value; supply devices get an airflow value per connector.
- Pick an insertion point, set rotation with the compass, Enter to end.

### Placing terminals and VAV boxes, practical notes ([KB: Adding HVAC Equipment](https://www.autodesk.com/support/technical/article/caas/tsarticles/ts/5qgshFhOVC2zKayLzVwo5f.html))
- The Diffuser tool opens the MvPart dialog on the supply diffuser category. Elevation in the dialog is the Z of the insertion point (set it to the ceiling height). The Flow tab shows for any MvPart with HVAC connectors.
- Set the connector's system (System tab) before drawing duct from it, so the duct takes that system.
- Place with one click (snaps work); the compass sets rotation and Enter accepts 0.
- VAV boxes have a very long size list: narrow it with the Part Filter tab and pick the connection size from the list instead of typing it, so a standard size is used.
- For more parts, reuse the dialog or COPY placed parts.

### Parts in-line on a duct ([G:E54C7844](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E54C7844-F412-46EE-A44C-6D696DD374B8))
- Pick the MvPart, hover a duct segment to show a duct end or duct curve connector, click it to place the part in-line or anchored to the duct end, set rotation with the compass, Enter.
- After insertion, grips rotate the part about the duct centerline and flip in-line parts (fans) to match flow direction.

### Part behavior of a block-based MvPart ([G:8BDB9297](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8BDB9297-67E3-4B9E-8BF5-133FA537B130)) [GUI, Content Builder wizard]
- Type: main category; drives behavior (example: flow annotation on an HVAC part). Types are predefined and CANNOT be modified; pick the closest.
- Layer Key: pick a key that matches the part type. Subtype: pick or type a new one; used as a filter in MvPart Add.
- "This part family automatically BREAKS INTO existing runs": part and duct stay separate pieces (move a valve without moving either segment).
- "This part family automatically ANCHORS to existing runs": part and duct act as one (move the run and the louver moves with it).
- Next is shaded until steps 1 to 5 are complete.

### Flow values (needed before any sizing)
- Equipment tab > Modify panel > Equipment Properties > Multi-view Part Properties dialog > Flow tab: outlet device (example ceiling diffuser) = Flow value; supply device (example VAV box) = air flow per connector. ([G:1A5B5DA9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1A5B5DA9-1B83-48C2-A0B7-4A72F4290AFF))
- Equipment tab > Modify panel > Modify Equipment > Multi-view Part Modify dialog > Flow tab > "Flow (Each Terminal)" for a fan, VAV box or ceiling diffuser. ([G:62254257](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-62254257-A9A1-4DA8-A0F8-E83FB9D3132B)) Both routes are documented; the field name differs.
- A duct's Flow Rate is read from these connected MvParts (3.5). ([G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26), [G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7))

### Flow annotation on air terminals ([G:94A69E68](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-94A69E68-14CE-4E1F-8393-834A27B2C3A7)) [GUI]
- Select the terminal > Equipment tab > Modify panel > Equipment Properties > Multi-view Part Properties > Flow tab. The Flow Annotation tab exists only after an air terminal has been added to the drawing.
- Up to 8 flow arrow locations around the terminal. One arrow block for all or one per location. Per arrow: rotation angle, offset from the terminal, flow value.

### Systems on MvPart connectors ([G:557BB7CB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-557BB7CB-A284-4296-8EAA-8D71F84EB949)) [GUI]
- Equipment Properties > Multi-view Part Properties > Systems tab > System column cell per connector.
- A new MvPart has no systems on its connectors. Connecting a duct gives the connector that duct's system. Runs drawn from the MvPart's Add grips already have the system set.
- Changing the system on a connector that has a run attached makes the run take the connector's system properties.

### Modify equipment, MVPARTMODIFY ([G:B836B203](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B836B203-E58F-4F8B-998B-5BEEBCE44942)) [GUI]
- Select the equipment > Equipment tab > Modify panel > Modify Equipment > Multi-view Part Modify dialog.
- Part tab: under All Installed MvParts pick a part. Part Size Name lists sizes in range of the current part.
- Missing size: Part Filter tab > Connections > Nominal Connection as a range (format like 4-72); Display limits how many sizes are listed. Step through sizes with the arrows under the graphic.
- Elevation: connected objects follow and connections are kept.
- Flow tab: outlet = Flow; supply devices = airflow per connector.
- Match another part: Multi-view Part Modify > Match (lower left) > pick the MvPart to match > Enter matches part and elevation (example valve to pump). ([G:063DC9CC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-063DC9CC-E47B-4232-B680-360FFEC49AB3))

### Exact location of an MvPart ([G:105943C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-105943C5-93B3-4CC2-A7CE-8404337D3D4F), [G:C7659914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C7659914-4448-4B57-ABD0-3AAAA23472DB))
- Equipment Properties > Multi-view Part Properties > Location tab: world or current coordinates; Insertion X, Y, Z; Normal X, Y, Z; Rotation in the current plane. This does NOT maintain connectivity. ([G:105943C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-105943C5-93B3-4CC2-A7CE-8404337D3D4F))
- Properties palette > Placement: Elevation; Rotation about the normal axis; Additional Information > Location worksheet (Insertion Point X, Y, Z; Normal: 1 for the normal axis, 0 for the other two). ([G:C7659914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C7659914-4448-4B57-ABD0-3AAAA23472DB))

## 3.11 Duct sizing

### How sizing works
- Connected systems can be sized automatically. A duct run = ductwork connected to one or more outlet devices with a defined outlet flow; outlets (example air diffusers) are the ends of the system. Each segment carries the flows of all outlets downstream of it, and that flow sizes it. ([G:731E8501](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-731E8501-5CB0-47B6-9D68-C70BB013D6DE))
- Three tools, usable any time ([G:9D9C77E6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D9C77E6-5EE5-4C37-91D2-C963648F77F1)):
  - Duct System Size Calculator: whole system or selected parts; converts 1-line to sized 2-line; also sizes defined shapes. For preliminary design and changes.
  - Instant Sizing Calculator: single segments; best for discrete changes.
  - Third-party external analysis tools (3.12).
- REQUIRED before calculating: flow values on ALL outlet parts ([G:72D5BDE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-72D5BDE1-1D7B-47F0-A826-2F57C87D43C2)), and every part connected, or size tools fail or give wrong results ([G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE)). Flow is set on the MvParts (3.10).

### Methods and math ([G:0D61887B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D61887B-31E6-483D-838E-43274CA944A8))
- Equal friction or constant velocity, chosen per system in Design Parameters (3.3).
- Friction loss follows the Darcy and Altshul-Tsal equations, 2001 ASHRAE Fundamentals Handbook, Chapter 34: friction loss eq. 19; friction factor eq. 21; Reynolds number eq. 23; equivalent round diameter of rectangular duct eq. 25; of flat oval duct eqs. 26, 27, 28.
- Rectangular and oval duct: friction sizing uses the equivalent round diameter and its velocity.
- The Add Ducts and Modify Duct dialogs list the ACTUAL velocity for the chosen CFM and size, not the velocity used in the friction calculation. The actual velocity is the one used for fitting and acoustical analysis.
- If no CFM shows in those dialogs, the friction or velocity shown is the Design Parameters value.
- The palette shows a value next to Velocity when the size came from the constant velocity method (the fixed velocity used).

### Instant sizing ([G:3E072A98](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3E072A98-53B4-4297-AF2B-5DB351B54BD7))
- Works while drawing and while modifying. The method comes from the system's sizing parameters.
- Capacity = sum of the flows of all outlets detected in the run; 0 if no outlet has a flow. A segment drawn from an outlet with a flow picks it up automatically. A branch not yet attached: pick the outlets to count, or type the flow.
- Calculate size: (1) exact size from the flow and the one fixed parameter (friction or velocity); (2) the NEXT LARGER catalog size is picked, then velocity and friction are recalculated from that size.
- Palette use: Round = flow, then calc. Rectangular or oval = fix Height and calc Width, or fix Width and calc Height; repeat to tune. ([G:18B490E5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-18B490E5-20C4-4B3D-B0A0-AD873BC7EC13), [G:1E076CAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1E076CAA-BE5F-40E4-ACB1-B2795B6C0B95))

### Duct Size Calculator, DUCTSYSTEMSIZECALC ([G:066594C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066594C7-8E6C-47B4-8594-89C29C2D69D6)) [GUI dialog]
- Select any object in a connected system (1-line is fine) > Duct tab or Duct Flex tab > Calculations panel > Calculate Duct Sizes.
- Scope: Calculate complete system; or Calculate selected objects (select button, pick, Enter).
- Shape: All plus one shape; or Individual with shapes for Trunk and Runouts (Trunk "Inherit from Fan" needs a fan at the start of the system). "Use shape and size from air terminals on runouts" copies the terminal connection and deactivates the Runout shape box.
- Ducts that already have a defined shape keep it: sizes are calculated but the shape is not overridden.
- Design parameters:
  - "Override design parameters from system definition(s)": choose Velocity or Friction and enter a value. Used for THIS calculation only; the system definition keeps its values for later runs.
  - "Round max. size": largest round diameter. If a duct must be bigger, "For larger size" = Rectangular or Oval; their height will not exceed the max round size.
  - "Rectangular/Oval Max. Height".
  - Catalog sizes to use: All, 1 inch increment, or Even sizes only.
  - "Apply sizing to parts with defined shape".
- Start. The system is resized in the drawing. Errors: View Event Log.
- Segments are NOT split; the calculated size applies to the whole segment. To step down (example after two diffusers), break the duct into segments first (3.14), then recalculate.

### Calculator keeps asking for parts ([KB:000510274](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-size-calculation-in-AutoCAD-MEP-keeps-prompting-you-for-choosing-parts-manually.html), MEP 2021-2027)
- Sizing an undefined 1-line layout prompts for a substitute part whenever the calculator meets a part combination the drawing's routing preferences do not cover.
- The parts you pick are remembered for those combinations in that drawing, so the prompts drop off with use. No setting turns them off. If the first run is not fully successful, read the View Event Log and fix the listed errors. (inference) A new drawing starts without the learned picks.

### Air flow units
- UNITS > HVAC > "Air Flow Units". Dialog only, no command-line form given. ([KB:000599508](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-flow-rate-units-in-AutoCAD-MEP.html))

## 3.12 External duct analysis (DDXML round trip)

### Workflow ([G:02E835BB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-02E835BB-24E5-455B-9E0A-2BF76739F0BB), [G:2D49B3DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2D49B3DF-7B7A-4D85-BBA9-45B055D3A833))
1. Review the system for accepted design practice so the external tool can handle it.
2. Assign ASHRAE fitting numbers to all fittings if the tool needs them.
3. Meet the export criteria below.
4. Export DDXML (Duct Design Extensible Markup Language).
5. Analyze in the external tool, which writes calculated sizes into the DDXML file; import it.
6. Resize the system from the results.
- Tools named by the help: Trane VariTrane Duct Designer and Elite Duct size. ([G:2D49B3DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2D49B3DF-7B7A-4D85-BBA9-45B055D3A833))
- Every step is dialog based. No command-line form is documented. ([G:08B52ECC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08B52ECC-F47F-4075-BC9D-89CE965A8039), [G:6358DFD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6358DFD5-650D-4B7A-B025-5599DBADA170), [G:9B227DE8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9B227DE8-76CC-4D1E-8C6F-176F33A89A3D))

### Export prerequisites ([G:32819FD7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32819FD7-2070-4535-8A4A-67C1AE679534))
- Each system needs at least one start point and one end point.
- Start point: a fan or other air handling device (fans, air handling units, or MvParts such as VAV boxes, mixers, economizers). No air handler in the drawing = the system cannot be exported.
- End points: outlet devices such as air terminals, each with a flow value, or sizing is not proper. An end cap as an outlet gets flow 0.
- VAV with 2 connectors (single duct, shutoff): part of the run unless it ends a branch; at a branch end it needs a flow value, otherwise its flow is ignored.
- VAV with more than 2 connectors (dual duct): treated as an end point; ductwork past it is ignored; the VAV connector flow is used.
- A segment with takeoffs exports as ONE plenum duct. To let the tool size parts differently, break it into segments and insert transitions.
- Preview connectivity: select an object > Duct, Duct Flex or Duct Fitting tab > Modify panel > Show Connected Objects drop-down > Show Connected Run.

### Export, DUCTXMLEXPORT ([G:08B52ECC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08B52ECC-F47F-4075-BC9D-89CE965A8039)) [GUI dialog]
- Click Export Duct XML. Duct System XML Export dialog: path and file name (DDXML extension *.ddx); Select Object, then pick any segment or fitting of the system; choose the system in Select System Type; Start. Errors: View Event Log.
- The page does not say which ribbon panel holds Export Duct XML; Import Duct XML is on Analyze tab > HVAC panel.

### Import, DUCTXMLIMPORT ([G:6358DFD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6358DFD5-650D-4B7A-B025-5599DBADA170)) [GUI dialog]
- Open the drawing that holds the exported system. Analyze tab > HVAC panel > Import Duct XML. Pick the DDXML file, Open. The optimized data is assigned to the system.

### Resize from external data ([G:9B227DE8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9B227DE8-76CC-4D1E-8C6F-176F33A89A3D)) [GUI]
- HVAC workspace, Analysis tool palette > External Data Resize. System Resize dialog: Select Object, pick a segment or fitting of the system.
- "Allow parts with custom size" checked = custom parts allowed. Unchecked = catalog parts only; then choose how a part is picked when the calculated size does not match a catalog size exactly.
- Start; the system resizes when the command ends. Check that all fittings and ducts resized; errors in View Event Log.

### ASHRAE fitting numbers ([G:FCDDCD3E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCDDCD3E-63E0-4A3F-BA09-720255266D92))
- ASHRAE publishes loss coefficient tables with a unique number per fitting; the external tool may require one on every fitting.
- Palette: select the fitting (tip: select one, then Duct Fitting tab > General panel > Select System drop-down > Select Similar to get all of that type), Properties palette > Advanced > Engineering Data > Assigned Engineering ID. Pick a listed number (check the ASHRAE Duct Fitting Database if several; some depend on flow direction or system type, supply or exhaust) or type it if not listed. Esc, next fitting.
- At export: View Event Log in the export dialog > select a multiple-fitting-ID warning > Modify Fitting ID icon > pick or type the ID > OK. The ID is stored on the fitting. Repeat until the warnings clear; rerun the export.

## 3.13 Spaces and zones for load analysis (gbXML)

### Purpose and order
- Spaces model interior room volumes; spaces are grouped into zones (real zones with their own heating and cooling needs). Flow: create spaces and zones, add engineering data, export gbXML (Green Building XML) to an external tool, import the results, read loads and airflows per space and zone, size ducts from them. ([G:4338C784](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4338C784-5A0F-40AE-884B-D066EB5B45D2))
- Ten-step workflow ([G:5607D12D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5607D12D-CB83-445C-A1FE-CAA70E19CAD0)): (1) space styles with lighting and equipment load per area and a classification; (2) zone styles; (3) add spaces, using objects in an xref'd floor plan as bounding objects; (4) property set data and engineering data on spaces; (5) create zones and attach property sets BEFORE export; (6) attach spaces to zones (zones can attach to zones); (7) export zones as gbXML; (8) review in Space/Zone Manager; (9) import results; (10) show results in tags and schedules.

### Spaces from the floor plan ([G:BE533BFC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE533BFC-C062-490B-A6A1-AF92D87EB0E5), [G:61087166](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-61087166-E1E4-4B72-9F52-DB4F88343E1E), [G:8D160282](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D160282-7001-4CB4-8952-6101281228FD), [G:08D2AE63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08D2AE63-FA8F-4D7A-AC02-072BD513D11A))
- Space tool: Analysis palette, HVAC tool palette group. Bounds by AEC objects (walls, floors) or AutoCAD lines and blocks, including xref'd plans. Pick the right space style when adding. ([G:BE533BFC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE533BFC-C062-490B-A6A1-AF92D87EB0E5))
- Load analysis needs extruded 3D or free form 3D spaces, NEVER 2D, so room volumes are right. Extruded 3D: floor perimeter extruded to a set height (from 3D AEC objects, 3D lines or 2D lines). Free form: irregular volumes, only from a plan built in 3D. ([G:61087166](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-61087166-E1E4-4B72-9F52-DB4F88343E1E))
- Generated spaces are associative by default: linked to their bounding objects, re-fit on one manual update, and not editable. From an MEP/AEC plan they detect openings; keep associative if plans will be updated; set non-associative to edit openings or surfaces (openings stay, the link goes). From AutoCAD linework: generate, set non-associative, add openings and surface types by hand. With spaces and bounding objects in one drawing, spaces can update automatically. ([G:61087166](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-61087166-E1E4-4B72-9F52-DB4F88343E1E))
- Openings: AEC objects in an AutoCAD Architecture 2027 drawing give automatic openings. Extruded spaces from 2D linework must be set non-associative before openings can be added. Manual spaces are non-associative by default. Converting free form to extruded loses openings that miss the base profile. ([G:8D160282](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D160282-7001-4CB4-8952-6101281228FD))
- Surface types are not required for gbXML: no adjacent space = exterior; wall surface below grade (z = 0) = underground. They can be set in Space/Zone Manager. ([G:08D2AE63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08D2AE63-FA8F-4D7A-AC02-072BD513D11A))

### Space styles and classification ([G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A), [G:A714AE64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A714AE64-2026-477C-9A38-90DA3FBF3B63), [G:8F31F992](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8F31F992-6701-430C-826E-18F33134913D))
- One style per room type (office, warehouse...). The classification on the style sets occupant density and outside air flow automatically (values ship with the software, per the mechanical standard or code). ([G:A714AE64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A714AE64-2026-477C-9A38-90DA3FBF3B63))
- Create [GUI]: Style Manager > current drawing > Architectural Objects > Space Styles > right-click > New, rename. General tab > Property Sets > Add Property Sets > SpaceEngineeringStyles. That definition exists only in drawings from Autodesk Building Systems 2007 or AutoCAD MEP 2027 templates; otherwise copy it from the Aecb Model template (Documentation Objects > Property Set Definitions). Enter area lighting and equipment loads. Optional gbXML space type override restricts the style to one space type and overrides its classification. Classifications tab > Space Occupancy browse > pick a space type. ([G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A))
- A classification is REQUIRED for gbXML export: on the style, as the override in the style property set, or by hand on the Extended Data tab. ([G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A))
- View classification values: Style Manager > Multi-Purpose Objects > Classification Definitions > Space Occupancy > Classifications tab > Property Sets. Per-space overrides go in the Properties palette. ([G:8F31F992](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8F31F992-6701-430C-826E-18F33134913D), [G:A714AE64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A714AE64-2026-477C-9A38-90DA3FBF3B63))
- Zone styles (display and design rules) are in Style Manager under Documentation Objects. ([G:65E47860](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-65E47860-E8B0-4877-89F7-14ED1DA0D228))

### Engineering data on spaces ([G:4159AD9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4159AD9D-7786-4024-A761-22C9DCA8D83D))
- Get the definitions: Style Manager > File > Open Drawing > `\ProgramData\Autodesk\MEP <version>\enu\Styles\Imperial` > "gbXML Property Set Definitions" > Documentation Objects > Property Set Definitions > copy into the current drawing, OK.
- Apply: select spaces > Home tab > Build panel > Tools drop-down > Properties > Extended Data tab > Add Property Sets.
- Conflict on the page itself: the intro says add SpaceEngineeringObjects, ThermalProperties and ZoneEngineeringObjects to every space; step 10 says tick SpaceEngineeringCalculatedData, SpaceEngineeringObjects and SpaceObjects. ([G:4159AD9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4159AD9D-7786-4024-A761-22C9DCA8D83D))
- Space Occupancy under Classification must not read *Unspecified*.
- Values: Occupancy (0 = use the classification's occupant density for outside air); ConditionType; LightingLoad and EquipmentLoad (typed values override DefaultLightingLoad / DefaultEquipmentLoad computed from the style's per-area values); OutsideAirFlow (typed value overrides the classification); SupplyAirFlow and ReturnAirFlow (leave empty for export; room totals, not per area or per person). RequiredOAFlow is read-only.

### Zones ([G:7E4CEE93](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E4CEE93-09A3-4158-81FE-ED656E6371E7), [G:0D76480A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D76480A-59A7-4AE8-B7B9-DBE7BFCD2EBA))
- Select all zones > Properties > Extended Data > Add Property Sets > ZoneEngineeringObjects; set design heating and cooling temperatures.
- Every space must belong to one or more zones. Attach: the zone's Add grip, or Zone tab > Modify panel > Attach, then pick spaces or zones. Spaces and zones in xrefs can attach to a zone in the current drawing.
- Export skips empty zones. An xref zone is exported only when attached to a zone in the current drawing, and not even then if its spaces already belong to zones in the export map.

### Export and import ([G:A0B1F680](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A0B1F680-EA50-404C-80C1-CA0888393F48), [G:A4A0E175](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A4A0E175-1DA6-497A-B510-730EF3C07A7B)) [GUI dialogs]
- GBXMLEXPORT: Analyze tab > HVAC panel > Export gbXML. Dialog: File name; Select Objects (all zones in the current drawing auto-detected; xref zones only if attached); Building Type and postal ZIP code; Start; errors open the event log.
- GBXMLIMPORT: open the drawing used for the export (with xref spaces, import into every drawing that holds spaces). Analyze tab > HVAC panel > Import gbXML, pick the file, Open.
- Import reports NO success or failure. Check SpaceEngineeringCalculatedData (spaces) and ZoneEngineeringCalculatedData (zones) on the Extended Data tab. Calculated SupplyAirFlow feeds space tags and schedules; return air can be typed.

### Review, tags, schedules
- Space/Zone Manager: Space tab or Zone tab > Helpers panel, or the Properties palette button. Tick Show All Zones and Spaces and Show Space Surfaces; set surface Type per surface. ([G:0C85A82D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0C85A82D-CE4B-4703-AD42-7652626D9A99))
- Content Browser > "MEP Documentation Tool Catalog - Imperial" > HVAC > HVAC Tags > Text Tags (Space tag) and HVAC > HVAC Schedules (Space Engineering Schedule); i-drop them onto a tool palette. ([G:295A0C99](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-295A0C99-6FF3-438A-A288-526D4FEFDDCA))

## 3.14 Modifying duct: grips, location, size, system, break and merge

- You can change system, elevation, shape, size and part type of a segment; move single objects or connected groups; recalculate sizes; change a fitting, an off-center fitting position or a custom fitting, at any point in the design. Metadata command: DUCTMODIFY. ([G:EE45CEAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE45CEAA-EF11-4671-B530-DDD771A72998), [G:52AC5F8B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-52AC5F8B-A0A7-4A8B-BC55-DE1A130AF6AE))

### Size or shape ([G:18B490E5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-18B490E5-20C4-4B3D-B0A0-AD873BC7EC13)) [GUI]
- Select the segment > Properties palette > Dimensions: routing preference and shape; type sizes or use instant sizing (3.11).
- Duct tab > Modify panel > Modify Run: Modify Run dialog for routing preference and other settings tied to the selection.
- Maintain Connection dialog: "Modify to maintain connection to next part" prompts to add a transition and leaves the rest of the run alone. "Modify to next junction/transition" resizes the branch up to the next junction or transition; the junction fitting is replaced by the right transition so the junction stays valid.
- Size lock: a locked segment or fitting keeps its size when the whole branch is resized; transitions are added at each end (example: a tight clearance). Lock icon under Dimensions. ([G:B36C61AD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B36C61AD-B8E4-45B6-93EC-011880F09958))

### System ([G:1B208821](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B208821-56A0-478E-AA4F-78D7235D1BAA), [G:557BB7CB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-557BB7CB-A284-4296-8EAA-8D71F84EB949), [G:2801A5D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2801A5D1-F63A-49B3-85A5-FB41554F4BD6))
- Duct tab > Modify panel > Modify Run > System drop-down. Changing one segment's system updates every component validly connected to it. Connector systems on MvParts: 3.10.

### Location by numbers ([G:C7659914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C7659914-4448-4B57-ABD0-3AAAA23472DB))
- Duct or MvPart: Properties palette > Placement > Elevation; Rotation (MvPart, about its normal); Additional Information > Location worksheet: Insertion Point X, Y, Z; Normal = 1 for the normal axis, 0 for the other two.
- Fitting: deselect the part, select the fitting, Additional Information > Location worksheet: Rotation Angle, Insertion Point, Normal. OK.

### Grip types ([G:A906409C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A906409C-8BFB-484F-BEFE-B8B48FCB6C4E), [G:5B72421C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5B72421C-5AFD-4207-88B6-00B370F15B31), [G:BA7F84A3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BA7F84A3-5276-467F-9443-D40FE8AEFDB8))
- Grips are an alternative way to draw or modify a run; selecting an object shows all its available grips. [GUI]
- Location (ducts, fittings, MvParts), Elevation (same), Rotate (in-line or anchored MvParts, fittings, takeoffs; also flips for flow direction), Lengthen (duct only), Add (3.6).

### Location grip ([G:9469D8C6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9469D8C6-46A4-476E-B546-CE13491EB49F), [G:0FB5EB44](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0FB5EB44-1B15-42FA-9648-977204ECCB10))
- Blue square. Click and move: connectivity kept, MvParts stay put (an MvPart oriented along the same vector also keeps the object fixed).
- Ctrl once: connectivity kept, MvParts along the same vector move with the object. Ctrl twice: the object moves alone and is disconnected.
- With connectivity kept, connected objects in the same plane stretch in the move direction; connected objects move in the current XY plane.
- Unconnected segment: Start and End grips change angle and length (XYZ of that end); handy for snapping a segment onto an existing run.

### Elevation grip ([G:6FB70D2C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6FB70D2C-0D69-4030-9AFB-621DB9071277), [G:DE7A2153](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DE7A2153-DBC4-4B71-864B-6F5040E5790B))
- Use a side or isometric view. MvPart: grips at the insertion point and connectors. Segment: elevation relative to top, centerline or bottom.
- Connected: continue = only fittings and segments adjust, part locations stay, connectivity kept; Ctrl = everything including parts adjusts, connectivity kept; Ctrl twice = connectivity broken.
- Tab to the input field, type the absolute elevation (relative to a point such as the centerline), Enter; or drag, Tab, type the change, Enter.
- NOT available on flex or sloping segments.
- No-grip route: Properties palette > Placement > Elevation; connected fittings and segments adjust, part locations stay.

### Rotate grip ([G:1299647C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1299647C-9F34-44A6-89B4-8083DF1B01E4), [G:1AE4B5FA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1AE4B5FA-FC1A-46B6-91B4-66FF60B463E5))
- Arrow-shaped: click = 180 degrees; Ctrl+click = 90 degrees (rectangular and oval parts swap height and width).
- Any angle: type it in the dynamic input field; or drag, Tab, type the change; or drag to a spot; or type the value at the command window.
- Diamond-shaped (isometric views): parts with round connectors on opposite ends rotate about their centerline to any angle.
- Grips show only on parts with connectors on opposite ends, and are limited or hidden to protect connectivity (example: a wye whose branch is connected).
- Rotating a connected object adjusts its neighbors (small length changes); if it cannot, it disconnects them.

### Lengthen grip ([G:C5BDD2E7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C5BDD2E7-E453-4563-8F59-A79869C64136))
- Duct only; keeps the current angle. On a connected end you choose whether to keep connectivity. In the moveable MvParts mode, connected objects including parts adjust (stretching a horizontal segment moves the vertical segment and the diffuser on its branch). Unconnected: Start and End grips change length and angle.

### Break and merge ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F), [G:69CB8895](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-69CB8895-0F35-4B45-9A18-616B2388A4A7))
- One break: BREAK, `f`, pick, `@` (3.1); connectivity kept.
- Several: select ducts > Duct tab > Modify panel > Duct Length > Duct Length dialog: Apply to Duct Run; Select Objects; Break with a Duct Length value (or Pick Length, two points); Merge with Select Object. Merging CANNOT cross fittings.
- Break while drawing: palette Sizing > Specify Cut Length = Yes, then Cut length.

### Insulation and lining ([G:F5FD464E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F5FD464E-9724-499D-BF63-3210A759DC0C), [G:44A8487F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-44A8487F-122C-48F8-A70A-1373619D4E02))
- Annotation only, visible only in 2-line display. Properties palette > Advanced > Lining Thickness or Insulation Thickness on segments and fittings, while drawing or after.
- The pipe page adds that insulation is not an object and cannot be scheduled ([G:6CD8EF5E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CD8EF5E-2987-4A96-ADD8-FDC4E2224C00)); (inference) the same holds for duct.

## 3.15 Connectivity checks and xref connections

### Check connectivity ([G:D9EB0BF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D9EB0BF1-C494-426F-8745-3760D74DCBD0))
- All systems: View tab > MEP View panel > Show Solution Tips; every disconnect shows in red.
- Neighbors: select a part > Duct, Duct Flex or Duct Fitting tab > Modify panel > Show Connected Objects drop-down > Show Connected Objects. Whole run: same drop-down > Show Connected Run (also right-click > Connected Objects, [G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE)).
- Branches: General panel > Select System drop-down > Select Connected Branches; Tab cycles upstream and downstream branches.

### What breaks a connection, collected
- Ctrl twice on a location, elevation or flex location grip ([G:9469D8C6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9469D8C6-46A4-476E-B546-CE13491EB49F), [G:6FB70D2C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6FB70D2C-0D69-4030-9AFB-621DB9071277), [G:BE7964FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE7964FC-CD2E-41FD-8CFE-4B6C928B738D)).
- MvPart coordinates on the Location tab ([G:105943C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-105943C5-93B3-4CC2-A7CE-8404337D3D4F)). A rotation the software cannot absorb ([G:1AE4B5FA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1AE4B5FA-FC1A-46B6-91B4-66FF60B463E5)).
- ERASE, MOVE, ROTATE, ROTATE3D, SCALE on a custom fitting ([G:D03CAF9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D03CAF9C-4ED7-4F2C-AD8A-B34C1BBCAB18)).
- Declining the system change when joining runs of different systems with no shared group ([G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90)).
- Kept: BREAK `f` `@` ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F)); plain grip moves ([G:9469D8C6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9469D8C6-46A4-476E-B546-CE13491EB49F)); elevation change in Modify Equipment ([G:B836B203](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B836B203-E58F-4F8B-998B-5BEEBCE44942)).

### Connect to duct in an xref ([G:EB4AC5CA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB4AC5CA-8873-461B-A7E9-4A80D08673C5), [G:8D39C1F4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D39C1F4-6071-45B8-8EE3-BE8C502647AA))
1. The xref holding the duct must be loaded, and the referenced drawing itself must NOT be open.
2. Draw a run from your system to the xref system.
3. Use the elevation lock so the run connects at its own elevation; unlocked, it will likely attach to a duct END connector on the xref object.
4. Answer Yes in the Save to Xref dialog (blocks a script). The change is saved PERMANENTLY to the duct in the referenced drawing.
- Tip: 2 viewports to preview the routing and the connection point.
- Multi-floor use: a vertical trunk in one reference drawing, each floor connecting to it; the joining fittings (example takeoffs) are saved into the reference drawing automatically. Later changes to connected objects in the current drawing do NOT propagate to the xref (resize the connected duct and only the current-drawing duct changes). ([G:8D39C1F4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D39C1F4-6071-45B8-8EE3-BE8C502647AA))

## 3.16 Duct display, labels, flow arrows, hatching

### 1-line, 2-line, graphical 1-line ([G:8D3D71FA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D3D71FA-1738-4309-BCFB-2F9965C9AAB8), [G:36B45F86](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-36B45F86-6A73-43B4-9D1B-BA5F475CBBDB), [G:AFD39FEB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AFD39FEB-2A50-46FD-91EC-EB5E3EC617F0), [G:60FA4712](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-60FA4712-EFD3-4B84-8D3C-3414A72DAF83))
- All three show the same 3D model parts at their real location. You do not declare a system 1-line or 2-line: build it once from parts, which keep part type, size and connection type in any display.
- Display configurations and system definitions control the display. Switch the drawing's display configuration to go 1-line or 2-line; to mix by nominal size, pair a system definition with the right display configuration.
- All three can be combined in one drawing, plotting included. Suggested: large duct as scaled 2-line, medium as scaled 1-line, small as graphical 1-line.
- 1-line: preliminary layouts, space allocation, simpler views. NOT a schematic: it keeps real geometry and all properties, also in isometric views. Fittings show at their actual envelope dimensions; in-line and anchored components as scaled 1-line; MvParts as scaled 2-line.
- 2-line: scaled 2D objects, 3D in isometric views; fittings and equipment follow their physical contours. For large duct, space allocation and interference checks.
- Graphical 1-line: generalized routing with non-scaled components; equipment as schematic symbols sized for the plot, not real dimensions. Use it for small runs whose fittings would plot too small. Components are unchanged and can switch back to scaled 1-line or 2-line.
- Single-line graphics display (a System Definition tab for piping) does not exist for duct, by design. ([KB:000553810](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Single-Line-Graphics-tab-is-missing-on-the-Duct-System-Definitions-dialog-box-in-AutoCAD-MEP.html))
- Per object: Properties palette > Display tab edits display components (contours, center lines). ([G:1F826880](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1F826880-6322-48A5-BBF0-C85483E31B02))

### Straight centerlines on elbows ([G:D6ABB64A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D6ABB64A-F890-40A3-A3C2-9103BE3BA5C0), [G:26CB4F59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-26CB4F59-C162-4F61-944B-E5816EAEE254), [G:4FA23AC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FA23AC2-D39F-4C6B-B98E-4BE63629E722))
- Shows an elbow's intersection point with straight centerlines in 1-line, 2-line, model and plan displays, for fabrication and installation drawings. Normally the centerline follows the curve, based on the path and orientation of connectors 1 and 2.
- Turn on with DISPLAYSTRAIGHTCENTERLINES, `d`, `y` (3.1). The result is stored in the drawing.

### Labels and flow arrows ([G:ADA2A49E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ADA2A49E-3F61-4C48-A929-0AD33E821AEA), [G:45C53834](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45C53834-08D5-4AAA-9D6E-782DECFACC23), [G:3C1E794E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C1E794E-9799-4084-B96C-90AEF5B89467), [G:36757F7F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-36757F7F-B3E9-4736-BCA7-7917D6630F34))
- While drawing: Properties palette > Advanced > Labels and Flow Arrows > pick a style; style NONE turns them off. Default style and spacing for new runs: Duct Layout Preferences (3.4; label preference stored in the registry).
- On existing duct [GUI]: HVAC workspace > Annotate tab > Label panel > MEP Label, or a label tool on the Annotation tool palette; Properties palette > General > Style; select the ducts, Enter.
- Layout Method: By quantity (Number of labels per straight segment); By distance (Distance between; a shorter segment gets none); One by one (click each spot; the label sits along the duct; hold Ctrl before picking to place it off the duct).
- Label styles can show properties such as duct size or system type. Labels update when the duct changes (example: resized duct shows the new size).
- Modify with grips: Add Label (Ctrl = even spacing); Remove Label; Location (drag along the curve; Ctrl after clicking offsets it); Repeat Distance (click along the curve to set spacing; Ctrl+click = even spacing).
- Label tab ribbon: General panel > Add Selected > New Label Node; Modify panel > Delete, Offset (distance; one label or all in the drawing), Rotate (one or all), Move To Object (re-anchor).
- Double-click a label > Properties > General > Style. The label curve style decides whether labels are annotative. Properties > Dimensions > layout method.
- Schedules can sort or group ducts by size. ([KB:000537314](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Schedules-grouping-and-sorting-MEP-objects-of-the-same-size-in-AutoCAD-MEP.html))
- Flow arrows around air terminals: Flow Annotation tab (3.10). Duct tags that shrink when moved in Edit-in-Elevation: [KB:000635992](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Labels-and-tags-shrink-or-change-size-when-moving-MEP-objects-ducts-in-Elevation-view-in-AutoCAD-MEP.html) (schedules and tags section).

### Hatching ([G:A8B0676F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A8B0676F-D2A1-4A0E-A521-67A57EDD3BA0), [G:EE45CEAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE45CEAA-EF11-4671-B530-DDD771A72998), [KB:000347605](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-turn-off-hatching-on-ducts-in-AutoCAD-MEP.html), [KB:000578471](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Visual-representation-of-Ducts-is-different-in-other-views-then-in-the-top-view-in-AutoCAD-Architecture-or-MEPVisual-representation-of-Ducts-is-different-in-other-views-then-in-the-top-view-in-AutoCAD-Architecture-or-MEP.html))
- Hatch a system [GUI]: Manage tab > Style & Display panel > Style Manager drop-down > HVAC System Definitions > the duct system > Display Properties tab > double-click Plan under Display Representations > Layer/Color/Linetype tab > make Hatch visible > Hatching tab > pattern > OK three times. Use: supply vs return on busy sheets; ductwork to be demolished. ([G:A8B0676F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A8B0676F-D2A1-4A0E-A521-67A57EDD3BA0), [G:EE45CEAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE45CEAA-EF11-4671-B530-DDD771A72998))
- Unwanted hatch on duct in plan: the active display set has the duct Plan hatch component on. Turn it off for all duct in Display Manager (Representation by Object > Duct > Plan), for one object on its Properties palette Display tab, or copy the Duct display settings from a drawing that looks right. ([KB:000347605](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-turn-off-hatching-on-ducts-in-AutoCAD-MEP.html))
- Hatch shows in plan but not in a front view: the "2 Line" representation for duct is not ticked in the current display set in Display Manager. ([KB:000578471](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Visual-representation-of-Ducts-is-different-in-other-views-then-in-the-top-view-in-AutoCAD-Architecture-or-MEPVisual-representation-of-Ducts-is-different-in-other-views-then-in-the-top-view-in-AutoCAD-Architecture-or-MEP.html))
- Other display articles, titles only here: lower or crossed ducts not dashed ([KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html)); ducts become skeletons when hatched ([KB:000598575](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-turns-into-skeleton-when-attempting-to-hatch-in-AutoCAD-MEP.html)); fittings not 3D solids on export ([KB:000479482](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Exporting-to-AutoCAD-from-AutoCAD-MEP-will-create-fittings-not-as-3D-solids.html)).

### Turn duct into a 1-line schematic ([KB:000629105](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-it-possible-to-convert-existing-duct-systems-into-1-line-schematic-undefined-systems-in-AutoCAD-MEP.html))
- There is no one-step conversion. Workaround: on a backup copy, show duct 1-line, delete the MvParts and fittings, explode the segments down to plain lines, join them with FILLET, then run SLINECONVERT and set the system. The 1-line display configuration ships in the Aecb Model template if the drawing lacks it. ([KB:000629105](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Is-it-possible-to-convert-existing-duct-systems-into-1-line-schematic-undefined-systems-in-AutoCAD-MEP.html))

### Palettes used for duct work ([G:647085B2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-647085B2-580A-43FB-8E82-1F96599E58A7), [G:3CD5CEB8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3CD5CEB8-21CE-4B4A-8F82-9DC36B119C07), [G:0904ED37](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0904ED37-F8B8-46B6-9225-2350D866D7F4), [G:1B767377](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B767377-87DB-4397-982D-25B7D49B66D3))
- Home tab > Build panel > Tools drop-down > Tools (tool palettes) or Content Browser (all catalogs).
- The tool palette set = palettes named for the current profile under OPTIONS > Files > Tool Palettes File Locations. Shipped profile groups: HVAC, Piping, Electrical, Plumbing, Schematic, Architectural. A current project appends its tool catalog; switching or closing the project removes it.
- Title bar Properties icon: Transparency (not when docked or with hardware acceleration on), Allow Docking, palette group switch; Auto-hide button.

## 3.17 Symptom index
- "Unknown command" for DUCTADD or other MEP commands: plain AutoCAD or the AutoCAD profile is running (3.2). ([KB:000572458](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-Browser-can-t-be-opened-in-AutoCAD-Architecture.html), [KB:000339989](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-MEP-or-Architecture-tools-in-AutoCAD-MEP-or-AutoCAD-Architecture.html))
- Ribbon Build panel, HVAC tools or palettes missing or dimmed: wrong shortcut or profile, unloaded menu, corrupt profile or CUIX (3.2). ([KB:000339989](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-MEP-or-Architecture-tools-in-AutoCAD-MEP-or-AutoCAD-Architecture.html), [KB:000263285](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-tool-palette-groups-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- "Conflicting between Routing Preference and Shape" / "No Duct Found": catalogs not set in OPTIONS > MEP Catalogs (3.8). ([KB:000509388](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Conflicting-between-Routing-Preference-and-Shape-when-using-an-MEP-object-command-in-AutoCAD-MEP.html))
- Choose a Part keeps coming back: part, angle or size missing from the routing preference (3.8). ([KB:000446628](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Choose-Part-appears-when-attempting-to-connect-ducts-with-fittings-parts-in-AutoCAD-MEP.html), [G:D8B4F5CB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D8B4F5CB-B0B2-43AC-8A17-23E2FD119F6D))
- "A layout solution cannot be determined...": switch to Use Straight Elbow and Reducer (3.4). ([KB:000289163](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-trying-to-insert-tap-into-duct-with-AutoCAD-MEP.html))
- Duct Size Calculator asks for parts on every new system: expected; picks are learned per drawing (3.11). ([KB:000510274](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-size-calculation-in-AutoCAD-MEP-keeps-prompting-you-for-choosing-parts-manually.html))
- Sizing fails or gives wrong sizes: a flow is missing on some outlet, or a part is not connected (3.11, 3.15). ([G:72D5BDE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-72D5BDE1-1D7B-47F0-A826-2F57C87D43C2), [G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE))
- Calculated size did not step down after a diffuser: segments are not split; break first (3.11). ([G:066594C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066594C7-8E6C-47B4-8594-89C29C2D69D6))
- New duct from the "+" grip has the wrong size: turn off auto size by the diameter (3.5). ([KB:000578024](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/When-adding-a-duct-to-an-existing-one-the-size-is-wrong-in-AutoCAD-MEP.html))
- Flow Rate stays 0: no MvPart with a flow connected (3.5, 3.10). ([KB:000619735](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-Enter-Flow-Rate-in-AutoCAD-MEP-Properties.html), [G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7))
- A run joined to another system ignores edits to that system: the systems share no group and the change was declined (3.3). ([G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90))
- Run will not connect to an object at another elevation: elevation lock is on (3.6). ([G:320071DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-320071DC-E53C-46A4-A7C5-AB74CDC83A9C))
- Run to an xref duct lands on its end connector: turn the elevation lock on (3.15). ([G:EB4AC5CA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB4AC5CA-8873-461B-A7E9-4A80D08673C5))
- Elevation looks wrong after a non-center Justify: stored elevation is always the duct center (3.5). ([KB:000556470](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Justification-when-creating-ducts-in-AutoCAD-MEP.html))
- Override part not used on the next run: the Fitting Settings override ends with DUCTADD (3.6). ([G:09C498A1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-09C498A1-74A1-4CC6-A37A-30EDE81E8607))
- No elevation grip: flex or sloped segment (3.14). ([G:6FB70D2C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6FB70D2C-0D69-4030-9AFB-621DB9071277))
- Merge fails: merging cannot cross fittings (3.14). ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F))
- Insulation or lining not visible: shows only in 2-line display (3.14). ([G:44A8487F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-44A8487F-122C-48F8-A70A-1373619D4E02))
- Vane count cannot be edited: by design (3.7). ([G:DAA4FAAA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DAA4FAAA-945E-4BC3-AD56-F0306CF6BCDB))
- Custom fitting lost its connections: ERASE, MOVE, ROTATE, ROTATE3D, SCALE break them (3.7). ([G:D03CAF9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D03CAF9C-4ED7-4F2C-AD8A-B34C1BBCAB18))
- Flex duct shows solid: use the Wireframe visual style (3.9). ([KB:000615813](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Flex-Duct-shows-up-as-solid-in-AutoCAD-MEP.html))
- Hatch on ducts in plan, or missing in front view (3.16). ([KB:000347605](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-turn-off-hatching-on-ducts-in-AutoCAD-MEP.html), [KB:000578471](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Visual-representation-of-Ducts-is-different-in-other-views-then-in-the-top-view-in-AutoCAD-Architecture-or-MEPVisual-representation-of-Ducts-is-different-in-other-views-then-in-the-top-view-in-AutoCAD-Architecture-or-MEP.html))
- No Single Line Graphics tab for duct: by design (3.16). ([KB:000553810](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Single-Line-Graphics-tab-is-missing-on-the-Duct-System-Definitions-dialog-box-in-AutoCAD-MEP.html))
- DW144 square elbow connector on the outer side: MEP 2025/2026 issue, fixed in 2027 (3.8). ([KB:000578727](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/DW144-Rectangular-Duct-Square-Elbow-Flanged-shows-incorrectly-in-AutoCAD-MEP-2025.html), [KB:000646540](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-2027--Fixed-Issues.html))
- Equipment shows only its connectors: listed as fixed in MEP 2027. ([KB:000646540](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-2027--Fixed-Issues.html))
- gbXML export misses a zone: empty zone, or an xref zone not attached to a current-drawing zone (3.13). ([G:0D76480A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D76480A-59A7-4AE8-B7B9-DBE7BFCD2EBA))
- gbXML import shows nothing: it never reports; check the calculated data property sets (3.13). ([G:A4A0E175](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A4A0E175-1DA6-497A-B510-730EF3C07A7B))
