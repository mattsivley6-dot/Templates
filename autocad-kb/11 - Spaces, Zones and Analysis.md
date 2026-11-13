# 11 - Spaces, Zones and Engineering Analysis

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

Legend: (G:XXXXXXXX) links to the Autodesk help page cited. [AUTO] = reachable from the command line or a script; [GUI] = needs the ribbon, a palette or a dialog; (inference) = a conclusion drawn from the pages, not stated in them.

This section covers the AEC space and zone objects that the AutoCAD MEP 2027 toolset uses for room data and HVAC load work: space types, styles and tools; generating associative spaces from the walls of an xref floor plan; boundary objects and the Bound Spaces property; the four space boundaries; surfaces, openings and adjacency; zones; the property sets and classifications that load analysis needs; gbXML export and the trip to and from a load program; and the duct sizing tools (Duct Size Calculator, instant sizing, DDXML round trip) that turn terminal flows into duct sizes.
Most of this area is ribbon, palette and dialog work. The few command-line entry points come first (11.2) so a script writer can see what is reachable before reading the rest.
Source help is mostly the AutoCAD Architecture 2027 Spaces book; it applies because MEP uses the same space and zone objects ([G:DA589D80](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA589D80-D7D1-4101-B3E9-F49EE5199E9D), [G:DDF0540A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDF0540A-2AA7-40A6-A190-B9BACD855DE0)).

Contents
- 11.1 The load-to-duct workflow
- 11.2 Command and setting index (what a script can reach)
- 11.3 Space types, properties and styles
- 11.4 Space tools and non-associative spaces
- 11.5 Generating associative spaces
- 11.6 Boundary objects, Bound Spaces, xrefs and blocks
- 11.7 Updating, dividing and merging associative spaces
- 11.8 Generation troubleshooting (FAQ)
- 11.9 The four boundaries, offset types, area calculation standards
- 11.10 Surfaces, openings, adjacency and the Space/Zone Manager
- 11.11 Editing limits for 3D spaces
- 11.12 Zones
- 11.13 Engineering data for HVAC loads
- 11.14 gbXML export and the round trip
- 11.15 Space data out: schedule properties, evaluation, exports
- 11.16 Duct sizing inputs: terminal flows and system design parameters
- 11.17 Duct Size Calculator and instant sizing
- 11.18 DDXML round trip with external duct tools
- 11.19 Pipe and plumbing calculation tools
- 11.20 Custom area calculation standard (.NET API)
- 11.21 Legacy areas and obsolete command names

## 11.1 The load-to-duct workflow

What the help promises ([G:12BA7941](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-12BA7941-013D-4F8E-A21B-373456B3952C)): create spaces and zones, assign engineering data, export gbXML, analyze in an external tool, import the results, view calculated loads and airflows per space and zone, then design the duct system.

MEP 10-step workflow ([G:5607D12D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5607D12D-CB83-445C-A1FE-CAA70E19CAD0)):
1. Configure space styles: lighting and equipment load per area, classification.
2. Create zone styles (display and design rules).
3. Add spaces to the floor plan, using objects in an xref floor plan as bounding objects.
4. Assign property set data to spaces and edit engineering data.
5. Create zones and attach property sets to them BEFORE exporting.
6. Attach spaces to zones (zones can attach to zones).
7. Export zones for load analysis (gbXML).
8. Review spaces and zones in the Space/Zone Manager.
9. Import load analysis results.
10. Show results in tags and schedules.

Mechanical system workflow ([G:53FA9DB5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-53FA9DB5-6CCA-41CB-A1EB-2067BDC3E04D)): define HVAC design parameters (routing, sizing parameters, rise and drop style); define a project; attach the architectural plan as an xref through Project Navigator; use spaces for room take-off schedules and gbXML; calculate loads with a third-party tool.

Duct system workflow ([G:8063EAD9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8063EAD9-7E4E-405E-826E-22B1D29922C9)): 1-line preliminary design; place diffusers, VAV boxes, coils, dampers; draw duct; size duct (verify flow values, then calculate); change and recalculate; label and schedule; refine with grips.

Gaps and limits:
- Steps 9 and 10 point to "To Import Load Analysis Results" and "To Use Space and Zone Calculated Data" ([G:5607D12D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5607D12D-CB83-445C-A1FE-CAA70E19CAD0)). Neither page was among the help pages condensed here, so this section documents no import command, dialog or file format. Do not plan a headless import until it is tested.
- How spaces feed duct design: the help pages used here show no link that pushes a space's airflow into an air terminal's Flow value. SupplyAirFlow and ReturnAirFlow on a space are "for your reference" ([G:9DE7186B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DE7186B-E54B-4E83-BA70-FC07004EC05F)). Duct sizing reads flow only from MvParts ([G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7)). So plan to enter terminal flows yourself from the load results (inference).

## 11.2 Command and setting index (what a script can reach)

No dash-prefixed (dialog-free) form of any space, zone or sizing command appears in the help pages used here. Prompt text after the command name is mostly undocumented. Test each one before relying on it.

Command line, no dialog documented:
- [AUTO] `AECSPACEAUTOUPDATE`: turns automatic update of associative spaces on or off. Same as Options > AEC Object Settings tab > Space Settings > "Automatically update associative spaces". Prompts not given. ([G:B799FADB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B799FADB-CD29-4F2E-899F-F5DEBE5221A6))
- [AUTO] `AECSPACEMAXGAPSIZE`: largest gap allowed between colinear boundary objects (2D and extruded 3D spaces only, not 3D freeform). Same as Options > AEC Object Settings > Maximum Gap Size. No prompt, unit or range given. ([G:0BA00E72](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0BA00E72-0F6A-4369-9ACE-0D36B00BFDC8))
- [AUTO] `AECSPACEMAXAUTOADJACENCY`: largest distance between two space surfaces still treated as adjacent. Same as Options > AEC Object Settings > Maximum Automatic Adjacency. ([G:DDF0540A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDF0540A-2AA7-40A6-A190-B9BACD855DE0))
- [AUTO] `AECSPACECALCULATIONSTANDARD`: area calculation standard for the drawing. Same as Options > AEC Object Settings > Calculation Standard. ([G:FFF2404B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FFF2404B-6EEC-44D6-BB89-148D50929291))
- [AUTO] `AECSPACESETBOUNDINGOBJECTS`: select xref boundary objects, Enter, then `Y` creates a Bound Spaces override in the host, or `R` (Remove Override), Enter. ([G:38146EFD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-38146EFD-5300-4C2B-BFB6-2BDF982D1649), [G:94AD4E95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94AD4E95-157B-4D0F-AFA1-086BBF92744A))
- [AUTO] `AECSPACEDISPLAYBOUNDSPACESPROPERTY`: shows the Bound Spaces property on AutoCAD linework that came from an older imported ARG profile. ([G:7053C063](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7053C063-C081-47B5-B095-876173983917))
- [AUTO] Adjacency display: page metadata names `AECSHOWSPACEADJACENCIES`; the step text says type `aecshowspaceandadjacencies`. Both spellings are on the same source page. Adjacent surfaces draw as lines; Enter hides them. Test which name exists. ([G:008DDA60](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-008DDA60-8BD8-4A80-9DB9-4C6B5BC85DAC))
- [AUTO] `SPACEREVERSEPROFILE`: reverses all rings of the selected spaces; Enter ends selection. `SPACEREVERSERING`: select a space, run it, pick the ring. Non-associative 2D and extruded 3D spaces only. ([G:EB16E8F5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EB16E8F5-E474-4BAB-BF17-E0F7206801E5), [G:5A1BBFF4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5A1BBFF4-BC96-4435-9CD7-E8AEF38AD9D6))
- [AUTO] `BREAK`, select duct, `f`, pick point, `@`: one break that keeps connectivity. Used to let the sizer give a segment two sizes. ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F))

Command name opens a dialog (blocks an unattended script):
- `GBXMLEXPORT`: Export to gbXML dialog. ([G:D7911DC9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7911DC9-BEA0-4B06-8317-64969AAAFA5E))
- `DUCTSYSTEMSIZECALC`: Duct Size Calculator dialog. ([G:066594C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066594C7-8E6C-47B4-8594-89C29C2D69D6))
- `DUCTXMLEXPORT`, `DUCTXMLIMPORT`: Duct System XML Export and Import dialogs. ([G:08B52ECC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08B52ECC-F47F-4075-BC9D-89CE965A8039), [G:6358DFD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6358DFD5-650D-4B7A-B025-5599DBADA170))
- `MVPARTMODIFY`: Multi-view Part Modify dialog (Flow tab sets terminal flow). ([G:B836B203](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B836B203-E58F-4F8B-998B-5BEEBCE44942))
- `AECEXPORTPROPERTYDATA`: property data export, replaces the old `SpaceInfo` MDB export. ([G:527C3DD0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-527C3DD0-7691-4CCB-B28D-89B2BEEC0186))

Prompt keys inside commands whose command names the pages do not give:
- Generate Space: `G` (Generate all), `sh` (SHow Bounding Objects), `v` (reset Visible boundaries), or pick inside a closed boundary. ([G:3479D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3479D10A-3594-4D0F-9193-9F2851D0AAA7))
- Show Space Boundaries: Enter (boundary objects plus associative spaces), `S` (hide associative Spaces), `X` (eXit and restore visibility). ([G:59FCAE97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-59FCAE97-D385-4048-9085-522B19889FEB))
- Zone > Create Polyline: `D` (Directly attached spaces only) or Enter (all, including through subzones). ([G:B0A3196D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B0A3196D-78F4-4D1B-90CD-D8EA416646F0))
- Convert mass element or mass group to space: Enter keeps the source, `y` erases it. ([G:DDCE9910](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDCE9910-4060-4529-9D86-DE0193350E47), [G:449BDC7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-449BDC7E-FD40-42FE-AACC-91F3E937C622))
- Subtract, Crop, Merge, Boolean Union/Intersect/Subtract: `y` erases the picked object or space, `n` keeps it. ([G:E3FF35E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E3FF35E7-D3E9-4F3C-B319-13918C4CE357), [G:6A2D707E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6A2D707E-1F2A-42C0-9CEB-22B5398248B2), [G:81FFF142](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-81FFF142-D29A-4FEC-B723-5FDA5761022A), [G:C87CF627](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C87CF627-FC07-40B8-AF61-80A876FD8152), [G:3AF0BC17](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3AF0BC17-CFB6-4980-927B-6299D6F7ED55), [G:E2CD81BD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E2CD81BD-7A88-4B3A-9C35-7D2A84AFF47F))

Current command names known only from the obsolete-command maps ([G:6F238740](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6F238740-A50B-459B-B81F-4A69E5AF3098), [G:B3D59002](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B3D59002-3108-41C7-A282-A3FB01176C6C)): `AecSpaceAdd`, `AecSpaceAutoGenerate`, `AecSpaceStyle`, `AecSpaceStyleEdit`, `AecSpaceProps`, `AecSpaceProperties`, `AecSpaceAttach`, `AecSpaceDetach`, `AecSpaceEvaluation`, `AecSpaceCreatePline`, `AecSpaceRemoveVoid`, `AecSpaceVertexModify`, `AecSpaceAddSelected`, `AecZoneAdd`, `AecZoneAttach`, `AecZoneDetach`, `AecZoneLayout`, `AecZoneStyle`, `AecZoneTemplate`, `AecZoneCreateFromTemplate`, `AecZoneCreatePline`, `AecZoneProps`, `AecZoneProperties`, `AecZoneAddSelected`. No prompts are documented for them. `AecSpaceAutoGenerate` is probably what Generate Space runs (inference).

Not scriptable from these pages: Style Manager, Space/Zone Manager, Space Evaluation, Edit In Place, grip edits and Ctrl mode cycling, Properties palette edits.
Watch for: the Bound Spaces property is not shown when the drawing is opened through an Object Enabler (plain AutoCAD, Civil 3D) or when the toolset runs "as AutoCAD" ([G:F80A3137](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F80A3137-EA1F-4329-B834-1DB3BA794F38)). Whether a headless Core Console session exposes it is not documented (inference: test before scripting space generation there).

## 11.3 Space types, properties and styles

What a space is: a 2D or 3D style-based object that holds floor area, wall area, volume and surface data. Used for cost, energy analysis, leasing and FF&E reports. ([G:31B6A74E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-31B6A74E-4760-4249-96F4-666D0982C7B4))

Space types ([G:80F67B48](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-80F67B48-94E9-418B-9161-8C9B325FAD84)):
- Associative: generated from boundary objects; updates when they change. Non-associative: user geometry, stands alone, still calculates. Either can be switched later (Associative property).
- 2D: plan data only. Z is 0 by default and is IGNORED in create, edit and schedule.
- Extruded 3D: 2D profile plus a user height. Has floor and ceiling components plus space above the ceiling and below the floor (the help notes the space above the ceiling is often used for ductwork and cable). Bounded ONLY in X and Y; Z comes from the extrusion height.
- 3D freeform: associative to boundary objects in all three directions. Must be fully closed. Any number of surfaces.

Properties palette, space ([G:FA7BE084](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA7BE084-7575-457B-997C-A68850BDDE86)). Some rows exist only for some types (2D has no heights).
- General: Description; Layer (default from style); Style; Name (drop-down when the style has a list definition); Tag (only while adding or in tool properties); Associative; Offset Boundaries = Manual | By Style | By Standard <name>; Calculation Modifiers; Space/Zone Manager button.
- Create Type (only when adding or in tool properties): Insert (style target sizes), Rectangle, Polygon (Segment type Line or Arc), Generate (associative).
- Generate Space: Allow overlapping spaces. Default No: you cannot generate a space inside boundary objects that already hold one.
- Component Dimensions: Geometry Type = 2D | Extrusion | Freeform.
  - Overall space height = ceiling height + floor thickness + ceiling thickness + height above ceiling + height below floor. Read-only for freeform.
  - Ceiling height = top of floor to bottom of ceiling. Floor thickness 0 = no floor drawn. Ceiling thickness 0 = no ceiling drawn.
  - Height above ceiling = top of ceiling to top of space. Height below floor = bottom of floor to bottom of space.
  - Default surface height = ceiling height + ceiling thickness + height above ceiling.
  - Justification (extruded 3D): Top of floor | Bottom of floor | Bottom of space below floor (only when height below floor > 0). Freeform is always Top of floor.
- Actual Dimensions: Length, Width, Base area, Base perimeter, Base volume (3D).
- Advanced: Calculation Plane 1 and 2 Height (3D freeform; area at two heights, e.g. under a roof).
- Target Dimensions (non-associative): Target, Maximum, Minimum area.
- Location (non-associative only): Rotation, Elevation, Additional Information (Location worksheet: Insertion Point; Normal X/Y/Z, XY plane = Z 1; Rotation Angle). ([G:6428DFB0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6428DFB0-92AA-454D-A509-13FF0B4A1884))

Height rules:
- Extruded 3D (associative or not): edit heights on Properties > Basic > Component Dimensions. Sum of components = overall height. ([G:F82878FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F82878FF-2C9D-42BF-92B0-EBFBEEF7C5E7))
- 3D freeform: overall height comes from boundary objects (associative) or geometry (non-associative). Components shift inside the total, never change it. Ceiling thickness 0 makes height above ceiling 0 and read-only; floor thickness 0 does the same for height below floor; both 0 makes ceiling height read-only. ([G:C31D242B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C31D242B-3C36-4B44-85DD-126BF80BD984))
- 3D freeform overall height: non-associative only. Space tab > Modify panel > Edit In Place, drag the top surface grip, Edit in Place tab > Edits panel > Finish. ([G:69E85645](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-69E85645-F49C-454C-8755-BCCB9125EFFD))
- One surface of an extruded 3D space: 3D isometric view, Edit Surfaces grip, Surface Height grip. If nothing changes, the Surfaces display component is off. ([G:61BE4D24](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-61BE4D24-CE20-44B3-B0A0-4A9BD3CEC226))

Changing geometry type (Properties > Basic > Component Dimensions > Geometry type) ([G:9749632D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9749632D-0BD6-4BBA-AD56-EF8F5DEB0348)):
- Non-associative to associative (any type): length, width, rotation, elevation follow the boundary objects and lock; base boundary is no longer grip-editable.
- To associative extruded or freeform: surface editing turns OFF.
- To 3D freeform: calculation cut planes added; Default surface height and justification go away.
- 2D to extruded 3D: height and justification added; insertion point set to top of floor.
- Openings survive some switches and not others; see 11.10. ([G:A9E71AE2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A9E71AE2-82F6-4211-961F-A847A9032277))

### Space styles
- Create [GUI]: Manage tab > Style & Display panel > Style Manager > Architectural Objects > Space Styles > right-click New, or Copy then Paste. ([G:C0D09363](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C0D09363-5919-412C-8DF8-8D151C7AEEC9))
- One style per room type (office, warehouse...). ([G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3))
- What a style holds ([G:2ACADB4B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ACADB4B-A81D-4AC5-9608-24F7CDD9DDCE), [G:5CF96C56](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5CF96C56-152F-49E2-8365-DC58506D4F0E)):
  - Design Rules tab: Net Offset, Usable Offset, Gross Offset (distance from base boundary; 0 = on top of base) ([G:F667D891](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F667D891-83E2-4587-BFD0-59928DD60A92)); Space Names list definition ([G:9F5E9388](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F5E9388-749D-47B3-B14C-BB861145196B)); Target / Min / Max for Area, Length, Width ([G:5C87168E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5C87168E-3D05-46E8-B516-B8D91EFDE2EC)).
  - Classifications tab: one classification per classification definition; default Unspecified. ([G:25BE186E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-25BE186E-4750-4EC4-8A56-E26F98D8CA72))
  - General tab > Property Sets button: style property sets such as SpaceEngineeringStyles (11.13).
  - Materials tab and Display Properties tab.
- For load calculations the classification is the MOST important style setting: it sets occupant density and outside air requirements automatically. ([G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3))
- Name list change (new style or new list): name in new list stays; not in list but list allows free names: kept as non-standard; otherwise the name is removed and replaced by the FIRST name in the new list. ([G:9F5E9388](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F5E9388-749D-47B3-B14C-BB861145196B), [G:1646318F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1646318F-FFDA-4878-A969-91F9D7658D35))
- Target sizes: an inserted space outside the style range is truncated to the target size and gets a solution tip icon. ([G:5C87168E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5C87168E-3D05-46E8-B516-B8D91EFDE2EC))

Display facts that cause "missing" boundaries:
- Only the base boundary displays by default; turn on the net, usable, gross display components in the style to see them. ([G:2629E8F0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2629E8F0-B8B8-4532-A63E-65F74180F6F1))
- Net, usable and gross show ONLY in plan views; model views show the base boundary and base body. ([G:77162098](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-77162098-8D37-42CD-8332-EE331EED846C))
- Space hatching shows only in Plan display representations. ([G:A53A2873](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A53A2873-A614-498E-A78F-D6B95FCDD15C))
- The style "object cut plane" (Display Properties > Other tab) is display only and unrelated to the calculation cut planes of freeform spaces. ([G:4146A5BF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4146A5BF-63A6-4574-A96D-F7FF660429B3))
- Materials: only physical components (floor, ceiling) and the base linework and base hatch take materials; net, usable, gross boundaries do not. ([G:8122FD0C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8122FD0C-EF88-41FF-8F0F-EFA57262183A), [G:6B411308](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6B411308-6BC2-456E-930D-54E1F8D9C7F5))

## 11.4 Space tools and non-associative spaces

Space tools ([G:5BE73057](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5BE73057-8EAD-440D-9A68-6F0C61598C3B), [G:E7DAC9C4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7DAC9C4-CFD1-4004-9EBC-9C2975EC6601)):
- A palette tool that carries a space style plus preset properties. Default palettes have them; more in the Stock Tool, Sample Palette and Design Tool catalogs.
- Make one [GUI]: drag a space or a space style (from Style Manager) onto a palette, copy and paste a tool, or drag from Content Browser (Home tab > Build panel > Tools drop-down > Content Browser).
- Tool properties: Name, Description, layer key overrides, style and its source drawing, space Name, tag and its source drawing, Create type, Offset boundaries, Allow overlapping spaces, Geometry type (2D, Extrusion, Freeform, or Undefined (--) to allow several), heights (leave Undefined to allow different heights), Justification, Actual Dimensions, Constrain.
- Associative is editable only when Create type = Generate (default Undefined (--)). For Insert, Rectangle, Polygon it is read-only.
- Gotcha: starting an associative-space tool processes all valid boundaries in the drawing; slow on a big model. Name tools to show associativity.
- Any tool setting left Undefined (--) uses the last Properties palette setting. ([G:607DF397](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-607DF397-BEDF-4388-9CA4-BDFC4EEA93E9))

Drawing non-associative spaces [GUI] (start: Space tool, or Home tab > Build panel > Space drop-down > Space). Associative is always No for these three.
- Rectangle ([G:685565AF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-685565AF-7224-46FB-9080-645D622F23DF)): Create type = Rectangle; geometry 2D or Extrusion; pick start point, pick opposite corner; repeat; Enter ends.
- Polygon ([G:22CDD1E3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22CDD1E3-E3ED-4543-83E7-3247A1AB75D4)): Create type = Polygon; Segment type Line or Arc for the first segment. Line: pick start and end. Arc: start, a point on the arc, end. Each segment reuses the last type. Close, Enter.
- Insert with style target sizes ([G:66C602E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-66C602E7-0849-464F-BFEF-87FF9B1E43A1)): Create type = Insert; Specify on screen Yes (pick within target range) or No (type values). Constrain: Area (area fixed, length and width float), Length, Width, or *NONE*. Pick insertion point, then rotation. Enter ends.

Converting objects to spaces:
- Linework and AEC objects ([G:607DF397](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-607DF397-BEDF-4388-9CA4-BDFC4EEA93E9)): right-click the Space tool > "Apply Tool Properties to Linework and Aec objects"; select objects and closed polylines; Enter; Convert to Space worksheet: Cut Plane Height, Erase Layout Geometry (checked erases sources), Specify on Screen; OK. Valid outlines: walls, curtain walls, columns, braces, beams, slabs, doors, windows, window assemblies, roofs, roof slabs, stairs, railings, mass elements and groups, AEC polygons, profiles, closed polylines.
- Mass element ([G:DDCE9910](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDCE9910-4060-4529-9D86-DE0193350E47)): Mass Element tab > Convert To panel > Space; [AUTO] prompt: Enter keeps the mass element, `y` erases it. Box, Cylinder, Extrusion become extruded 3D; all other shapes become 3D freeform. Gotcha: keep the tool Geometry type at Undefined (--); set to Extrusion, a pyramid becomes an extruded box with the pyramid profile.
- Mass group ([G:449BDC7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-449BDC7E-FD40-42FE-AACC-91F3E937C622)): same path and prompt. A group of non-intersecting elements becomes ONE space with several profiles; split the group first.
- 3D solid: not a valid boundary object (11.6). Convert it to a mass element first: right-click a mass element tool > Apply Tool Properties to > 3D Solid; [AUTO] prompts: select solids; erase original? (Enter keeps, `y` erases); `n` (Name), name, Enter twice. Result is a Free Form mass element; FACETDEV sets smoothness only at creation. ([G:E7564FAE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7564FAE-E636-48C1-BDD6-5F35E8C294C2))

## 11.5 Generating associative spaces

How it works ([G:3845A9D8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3845A9D8-FC9E-4234-892B-CC5BB875770E), [G:506D20F9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-506D20F9-64D4-4A07-B4B5-90D42BE57C7C), [G:3479D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3479D10A-3594-4D0F-9193-9F2851D0AAA7)):
- An associative space is built from boundary objects and updates when they change.
- 2D and extruded 3D: boundary objects fix X and Y only. Z is 0 (2D) or a user extrusion height applied uniformly.
- 3D freeform: associative in all three directions. Must be fully bounded on all surfaces.
- A space can be associative to boundary objects inside an xref and follows xref changes. Spaces generated INSIDE an xref do NOT react to boundary objects in the host. ([G:3845A9D8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3845A9D8-FC9E-4234-892B-CC5BB875770E))
- Gap tolerance (2D and extruded 3D only): the software closes gaps between COLINEAR segments, e.g. a line plan drawn with door gaps. No gap closing between objects at an angle, or across a gap that holds another boundary object. AEC doors, windows and wall openings are not gaps. Set the size with `AECSPACEMAXGAPSIZE` or Options > AEC Object Settings > Maximum Gap Size. ([G:3479D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3479D10A-3594-4D0F-9193-9F2851D0AAA7), [G:0BA00E72](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0BA00E72-0F6A-4369-9ACE-0D36B00BFDC8))
- A space can also be generated from an object outline, for example wall outlines. ([G:3479D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3479D10A-3594-4D0F-9193-9F2851D0AAA7))
- New in this version: boundary objects on frozen or hidden layers ARE used in generation and update when their Bound Spaces = Yes. ([G:3479D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3479D10A-3594-4D0F-9193-9F2851D0AAA7))

Steps ([G:3479D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3479D10A-3594-4D0F-9193-9F2851D0AAA7)):
1. Check Bound Spaces = Yes on every needed boundary object. Home tab > Inquiry panel > Show Space Boundaries shows them, including objects on frozen, hidden and locked layers. Fix wrong ones before generating.
2. Pick the Space tool, or Home tab > Build panel > Space drop-down > Generate Space. [GUI]
3. Offset boundaries: Manual | By style | By standard <Standard Name> (11.9).
4. Create type = Generate. Associative then defaults to Yes.
5. Allow Overlapping Spaces = Yes only if the boundary already holds a space you want to keep (example: xref that already has spaces, but you need another area standard). ([G:3AE17D50](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3AE17D50-B1A2-480C-8F97-F6E1848567E7))
6. Geometry type: 2D | Extrusion | Freeform.
7. [AUTO] Optional keys at the prompt: `sh` (SHow Bounding Objects) lists objects with Bound Spaces = Yes; `v` (reset Visible boundaries) refreshes the set after you zoom or pan.
8. [AUTO] Generate: 3D freeform = `G` (Generate all). 2D or extruded 3D = `G` for all visible boundaries, or pick inside each closed boundary.

Script-critical view rules:
- Only boundary objects visible in the drawing area when the space tool STARTS are in the set. After a zoom or pan, type `v`, then generate. ([G:AE1A3C00](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AE1A3C00-7209-4250-AE7C-15A5A34C4ECE))
- Generate all processes every object in the current view. A tighter view is faster. ([G:FF9737F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FF9737F3-738B-4663-9C4F-D8F58AF53459))
- Update Space Geometry uses the CURRENT viewport zoom; zoom out so the whole space and its boundary objects show. ([G:ED369F95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED369F95-74BF-485A-8BB2-FCF3D1586BA2))
- (inference) In a script, set the view (for example ZOOM Extents, or a window around one floor) before starting the generate command. The pages do not show a headless generate.

Show Space Boundaries [AUTO keys after the ribbon button; no command name given] ([G:59FCAE97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-59FCAE97-D385-4048-9085-522B19889FEB)):
- Zoom until all wanted spaces are visible, then run it.
- Enter = show boundary objects and associative spaces (includes frozen, hidden, locked-layer objects).
- `S` = hide associative Spaces, boundary objects only.
- `X` = eXit and restore visibility (frozen and hidden boundary objects disappear again).
- Use it when a space comes out as one room instead of two: the separating object usually has Bound Spaces = No.

Deducting enclosed objects ([G:C2B86E49](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C2B86E49-C604-42D7-AAB9-157F5F712652)): columns or shafts fully inside an associative space are deducted automatically, if each is a valid boundary object with Bound Spaces = Yes.

## 11.6 Boundary objects, Bound Spaces, xrefs and blocks

The rule: an object bounds an associative space only if it is a valid boundary TYPE for that space type AND its Bound Spaces property = Yes. Set it BEFORE generating. ([G:DD3C6486](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DD3C6486-9C52-405B-A22B-5A5332867652), [G:7053C063](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7053C063-C081-47B5-B095-876173983917))

Where Bound Spaces is set:
- In the object style [GUI]: Manage tab > Style & Display panel > Style Manager > Architectural Objects > category > style > General tab > check "Objects of this style may act as a boundary for associative spaces". Example: set toilet-stall or half-height counter wall styles to No. ([G:8703CFFC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8703CFFC-E315-45F8-BECF-D526E29E0598))
- On the object [GUI]: Properties palette, General category (architectural objects) or Advanced category (linework). Values By Style | Yes | No. The palette value overrides the style. ([G:F80A3137](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F80A3137-EA1F-4329-B834-1DB3BA794F38))
- Gotcha: walls that must NOT bound spaces need a different wall cleanup group from walls that do. A non-boundary wall in the same cleanup group makes the boundary wall act as non-boundary, and no space forms. ([G:F80A3137](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F80A3137-EA1F-4329-B834-1DB3BA794F38), [G:AE1A3C00](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AE1A3C00-7209-4250-AE7C-15A5A34C4ECE))
- Gotcha: the property does not show under an Object Enabler or with the toolset run "as AutoCAD". ([G:F80A3137](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F80A3137-EA1F-4329-B834-1DB3BA794F38))
- Gotcha: lines, arcs and polylines from an older imported ARG profile do not show Bound Spaces until you run [AUTO] `AECSPACEDISPLAYBOUNDSPACESPROPERTY`. ([G:7053C063](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7053C063-C081-47B5-B095-876173983917))

Valid boundary objects ([G:599D8ABD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-599D8ABD-B7DE-4311-8D01-73148B40FA07)). Columns: 3D freeform / 2D and extruded / default Bound Spaces.
- Wall: Yes / Yes / Yes (by style). Space sits at the near face of the wall body. Plan and body modifiers, interferences, sweeps, end caps count. A modifier hole narrower than the max gap size may be ignored.
- Curtain wall, curtain wall unit: Yes / Yes / Yes (by style). Empty cells are treated as closed.
- Door and window assembly: Yes / Yes / Yes (by style).
- Door, window, opening: Yes / Yes / Yes. When anchored in a wall, the wall's setting also applies. Openings cut openings in freeform surfaces.
- Mass element: Yes / Yes / No (by style). 2D or extruded space made at the near face at the element bottom.
- Roof, roof slab, slab: Yes / NO / Yes (by style). They bound ONLY 3D freeform spaces, never 2D or extruded, even with Bound Spaces = Yes. ([G:7053C063](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7053C063-C081-47B5-B095-876173983917))
- Structural member: Yes / Yes / No (by style).
- Multi-view block: Yes / Yes / No (by style). Model-view geometry is used.
- Custom display block: Yes / No / Yes (by style).
- Block: Yes (needs 3D-valid contents) / Yes / follows contents.
- External reference: Yes (needs 3D-valid contents) / Yes / Yes.
- Line, circle, polyline, 3D polyline, ellipse, spline, arc: No / Yes / No.
- AutoCAD 3D solids are NEVER valid. Convert to a mass element (11.4) or wrap a polyline around it.
- Frozen or hidden layer objects still bound spaces. To exclude one: thaw or unhide its layer, set Bound Spaces = No. ([G:599D8ABD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-599D8ABD-B7DE-4311-8D01-73148B40FA07), [G:B1B502B7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B1B502B7-A4D2-426C-BE2B-523E90F2EDF6))

Xrefs ([G:B6E397DE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B6E397DE-90EF-4F64-9DAC-413B695A61F3)):
- The xref ITSELF must have Bound Spaces = Yes (Properties palette > Advanced). Default on insert = Yes. If No, everything inside is ignored whatever its own setting.
- Project Navigator defaults: xrefs attached to elements, constructs and views = Yes; xrefs attached to SHEETS = No.
- Steps: set Bound Spaces = Yes on the objects in the source drawing; xref it; select the xref, confirm Bound Spaces = Yes; generate.
- Auto update now covers xref-bounded spaces: changes reach host spaces when the xref is RELOADED with auto update on. ([G:F51C80FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F51C80FE-3B37-43E8-8A20-2850D07AFDD9))

Blocks ([G:B6E397DE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B6E397DE-90EF-4F64-9DAC-413B695A61F3)):
- Default Yes if at least one object inside is Yes, otherwise No.
- Nesting: any block or xref set to No up the chain blocks everything under it.
- Changing Bound Spaces inside the Block Editor does not refresh the host on save; update the affected spaces by hand.
- Legacy drawings: blocks and xrefs holding boundary objects default to Yes.

Overriding xref objects from the host (the engineer's case: an architect's plan you must not edit) ([G:38146EFD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-38146EFD-5300-4C2B-BFB6-2BDF982D1649)):
1. Xref the plan; select it; Properties > Advanced > Bound Spaces = Yes.
2. Home tab > Inquiry panel > Show Space Boundaries to see what bounds now.
3. [AUTO] `AECSPACESETBOUNDINGOBJECTS`, select the xref objects, Enter, `Y`, Enter.
4. Generate spaces. Overridden objects are used.
- The override lives only on THAT xref instance in THAT host. Another host, or a second insert of the same xref, has none.
- If no xref object is Yes and no overrides exist, a task dialog asks you to pick objects that should bound spaces (blocks a script). Picking sets Yes, or adds an override for xref objects.
- Remove an override [AUTO]: `AECSPACESETBOUNDINGOBJECTS`, select, Enter, `R` (Remove Override), Enter; then update spaces. ([G:94AD4E95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94AD4E95-157B-4D0F-AFA1-086BBF92744A))
- Each space uses the offsets and calculation standard of the drawing that contains it; check every drawing in a project uses the same standard. ([G:8999676F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8999676F-B45E-44C5-895B-F8A4CFBFBF45))

## 11.7 Updating, dividing and merging associative spaces

Automatic update:
- Toggle [GUI]: Options > AEC Object Settings tab > Space Settings > "Automatically update associative spaces". [AUTO] `AECSPACEAUTOUPDATE` does the same; its prompts are not documented. ([G:B799FADB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B799FADB-CD29-4F2E-899F-F5DEBE5221A6))
- Why turn it off: avoid double updates while you swap a wall; manual update is faster but spaces and boundaries can be out of sync meanwhile. Turning it off is also the documented fix for lag from xref-bound spaces. ([G:B799FADB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B799FADB-CD29-4F2E-899F-F5DEBE5221A6), [G:D8C35179](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8C35179-9FCE-41F0-8971-00C78CE5D240))
- With auto update off and a calculation standard in use, the standard's offsets reach changed spaces only after auto update is back on or a manual update runs. ([G:B799FADB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B799FADB-CD29-4F2E-899F-F5DEBE5221A6), [G:DFBC0D7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DFBC0D7E-BB6D-4D29-B311-4D058B79E1A5))
- GOTCHA: when auto update is turned back on, only spaces that got NO new boundary objects while it was off are updated. A dividing wall added while off does not divide the space. Fix per [G:B799FADB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B799FADB-CD29-4F2E-899F-F5DEBE5221A6): update that space manually. Fix per [G:D644B8FC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D644B8FC-AB21-4286-8236-BB93155A3A75): boundary objects added while off are never used later, so delete the wall and insert it again with auto update on. Try the manual update first; re-insert if it still does not divide.
- Solution tip icons right after turning auto update on mean space and boundaries are out of sync: Update > Selected Space. ([G:D643C23C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D643C23C-7BF5-4AD9-AD05-D94DA58470D0))

Manual update [GUI] ([G:7D5CB049](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7D5CB049-B45B-4D70-A823-46E0E75769DD), [G:B15F34C0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B15F34C0-1A19-491B-BA2C-B24E65B9F6D9)):
- Selected: select the space(s) > Space tab > Modify panel > Update drop-down > Selected Space.
- All: select any associative space > Space tab > Modify panel > Update drop-down > All Associative Spaces.
- Needed when: auto update is off and boundaries changed; a boundary object was added while off; auto update failed on a generation problem. ([G:DFBC0D7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DFBC0D7E-BB6D-4D29-B311-4D058B79E1A5))
- Also needed when a grip edit adds a new boundary object (tip icon appears), and when a trimmed boundary object is replaced by a new one (the new one is not recognized). ([G:ED369F95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED369F95-74BF-485A-8BB2-FCF3D1586BA2), [G:504B1F12](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-504B1F12-80B4-4A77-8F4D-799354942707))
- Update Space Geometry uses the current zoom; show the whole space first. ([G:ED369F95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED369F95-74BF-485A-8BB2-FCF3D1586BA2))

Dividing an associative space:
- Add a boundary object across it with Bound Spaces = Yes; auto update divides it. A new object with Bound Spaces = No does nothing. ([G:074C734F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C734F-202E-45B4-B319-5D77F2947DB7))
- Manual divide: auto update off; draw the new boundary object; select the space > Update > Selected Space (it shrinks to one side); generate a new space in the empty side. ([G:074C734F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C734F-202E-45B4-B319-5D77F2947DB7))
- No real wall (open office, lobby zones): Space Separator tool on the Spaces tool palette (or search "Space Separator" in Content Browser), or select the space > Space tab > Modify panel > Divide Space. Draw the separator polyline, Enter. Remove it by deleting it or setting its Bound Spaces = No. ([G:255A6943](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-255A6943-FEBF-4B1C-ACFA-56AF82A265EB), [G:C350325C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C350325C-CE87-415E-AF70-272B26CD6CDF))

Merging associative spaces ([G:592B153E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-592B153E-A0A8-4857-8BE2-FCC0A81A5720)):
- Delete the boundary object between them; auto update merges.
- Which space's properties survive, highest priority first: (1) only one has object property set data; (2) only one has classification data; (3) both have either: the LARGER space wins; (4) only one has style-defined property set data; (5) otherwise the OLDER space. Check the result; this can surprise.
- Manual merge (you choose the survivor): auto update off; delete the separating boundary object; delete the space you do not want; select the other > Update > Selected Space.

Roundtrip with older releases ([G:F51C80FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F51C80FE-3B37-43E8-8A20-2850D07AFDD9)): old releases picked boundaries with a filter at generation. A filter change made in an old release is IGNORED when the file reopens in 2027. Inspect spaces after any roundtrip.

## 11.8 Generation troubleshooting (FAQ)

Error "Valid boundary not found", 2D or extruded 3D ([G:3F597C6D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3F597C6D-4732-40FD-A25D-8B20C9862235)):
- Needed objects are invalid types or Bound Spaces = No. Check with Show Space Boundaries.
- Maximum gap size is smaller than the colinear gaps, so the outline is open and the space fails or flows into the next room. Raise the max gap above the largest gap.

Error "Valid boundary not found", 3D freeform ([G:ADE11907](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ADE11907-F28D-4539-AB7A-89A238132F29)):
- Objects not 100% closed. Example: interior wall auto-projected to a roof slab with no ceiling, reaching only the exterior wall baseline. Fix: add a ceiling under the roof slab; or extend the interior wall to the outside of the exterior wall; or add a sweep so the wall top meets the sloped slab.
- Objects not valid for freeform (railings, 2D linework) are filtered out and leave a hole. Use valid objects.
- Objects that only touch along an edge count as open. Extend one so they overlap.

No space although the outline looks closed ([G:AE1A3C00](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AE1A3C00-7209-4250-AE7C-15A5A34C4ECE)):
- A non-boundary wall shares a cleanup group with a boundary wall. Put non-boundary walls in their own cleanup group.
- You zoomed or panned after starting the tool. Type `v`, then generate.

Wrong shapes:
- Segmented or odd boundaries from wall outlines: max gap size too large. Recreate the space with a very small max gap. ([G:0DD7D038](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0DD7D038-9AAF-4322-AEB1-E2F8D8C2CF17))
- Sweeps and wall modifiers ignored: set the cut plane height of that wall to 0. ([G:115295AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-115295AE-1B64-461A-AA91-08E936B75562))
- Extra spaces inside walls after in-place edits of walls with modifiers or cleanups: delete them. ([G:19CB2F00](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-19CB2F00-89F4-4A42-90A3-1D78D9CCE465))
- Spaces do not match the visible objects: frozen or hidden boundary objects are counted. Thaw, set Bound Spaces = No if unwanted. ([G:B1B502B7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B1B502B7-A4D2-426C-BE2B-523E90F2EDF6))

Space will not update after a boundary moves ([G:ED369F95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED369F95-74BF-485A-8BB2-FCF3D1586BA2)):
- Associative = No on the Properties palette: never updates and shows NO tip icon.
- Auto update is off: Update > Selected Space.
- The edit opened a gap, or made a boundary wall meet a non-boundary wall in the same cleanup group.
- Zoom so the space and its boundaries are fully visible, then update.

Speed:
- Generate all is slow: zoom in first; it processes everything in view. ([G:FF9737F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FF9737F3-738B-4663-9C4F-D8F58AF53459))
- Lag compared with older versions: xref-bound spaces now auto update. Turn auto update off to stop the lag. The first open of a converted host drawing with xrefs is slow once; it recovers after host and xrefs are saved in the current version. ([G:D8C35179](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8C35179-9FCE-41F0-8971-00C78CE5D240))

Boundary offsets (net, usable, gross):
- They do not move when the base updates: the space uses Manual offsets. Set By Style or By Standard. ([G:122A33A9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-122A33A9-51A8-4E33-9520-5F11632D9036))
- Tip icons while generating with a standard: the standard could not build them. Install the standard or support file the tip names, OR set those spaces to Manual and grip-edit. Do NOT switch back to By Standard; the next update overwrites the fix. ([G:0E2E9B32](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0E2E9B32-A5E4-4A01-8CF9-68B8C339B840))
- Wrong standard offsets: on mirrored spaces, run a manual update; with arc walls, switch to Manual and grip-edit. ([G:B6C9C2AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B6C9C2AE-5388-4D4A-AD97-22533679F22E))
- Spaces generated from an xref inserted with a SCALE never get correct standard offsets. Re-insert the xref unscaled, or use By Style or Manual. ([G:755D160B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-755D160B-8BE7-49CB-844D-94AA63443EC8))
- Drawing opened on a machine without its standard: EVERY space shows a tip icon. Copy the standard DLL into the Space Calculation Standards folder (11.9). ([G:8999676F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8999676F-B45E-44C5-895B-F8A4CFBFBF45))

## 11.9 The four boundaries, offset types, area calculation standards

Four boundaries per space ([G:833A18AF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-833A18AF-8F5C-4520-A50C-055B45C9F6D9)):
- Base: inner area of the room. For an associative space, the area the boundary objects enclose. Usually equals net (not in SIS).
- Net: planning and detailed design (cleaning, fit-out).
- Usable: renting, tax, statistics. Typically inside face of exterior walls to middle of interior walls.
- Gross: cost and key building numbers. Normally outside face of exterior walls to middle of interior walls.
- They may lie on top of each other (offset 0). Extra boundary display components can be turned off.

Offset types ([G:25C7279F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-25C7279F-5629-47AA-9584-0C5F1C19A76B), [G:E7DAC9C4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7DAC9C4-CFD1-4004-9EBC-9C2975EC6601)):
- Manual: net, usable, gross edited with grips. New manual space: all offsets 0. ([G:4FC2DA14](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4FC2DA14-20B0-495E-AB59-669305BF4E0B))
- By Style: offsets from the space style Design Rules tab. ([G:F667D891](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F667D891-83E2-4587-BFD0-59928DD60A92))
- By Standard <name>: the drawing's area calculation standard. ASSOCIATIVE spaces only.
- Set it on Properties > Offset boundaries before creating, or change it on a selected space. The base boundary itself never changes on a switch.

Which boundaries can be grip-edited ([G:77162098](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-77162098-8D37-42CD-8332-EE331EED846C), [G:4FC2DA14](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4FC2DA14-20B0-495E-AB59-669305BF4E0B), [G:014ADC37](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-014ADC37-08E1-402A-84FC-F1882EFC0850), [G:9765CA13](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9765CA13-33F4-4A01-8427-7C78CB506B31)):
| Space | Offset type | Grip-editable |
|---|---|---|
| Associative | Manual | Net, Usable, Gross |
| Associative | By Style | None |
| Associative | By Standard | None |
| Non-assoc 2D or extruded 3D | Manual | Base, Net, Usable, Gross |
| Non-assoc 2D or extruded 3D | By Style | Base |
| Non-assoc 3D freeform | Manual | Net, Usable, Gross |
| Non-assoc 3D freeform | By Style | None |
An associative space's base boundary is never editable; it follows the boundary objects.

Working with manual boundaries [GUI]:
- Activate first: Plan view only, Offset Boundaries = Manual, click the boundary's trigger grip; or right-click > Edit Boundary > pick the boundary. Required before any grip edit or Boolean operation. ([G:B7050327](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B7050327-30C9-4200-9F94-84A499DA9F3A))
- Only ACTIVATED boundaries are cut by Divide, Trim, Subtract (holes) and Crop, and only the first space's activated boundaries merge in Merge or Crop. An inactive one is skipped and its partner can be deleted. Activate all of them first. ([G:041CD9E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-041CD9E7-F83E-4C5F-BE47-F329C7F24F1B), [G:F6A48C80](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F6A48C80-3AA6-4C09-BB5A-C24580B353DD), [G:E3FF35E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E3FF35E7-D3E9-4F3C-B319-13918C4CE357), [G:6A2D707E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6A2D707E-1F2A-42C0-9CEB-22B5398248B2), [G:F97035B6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F97035B6-464A-40F6-922C-83574CBA8783))
- Move one boundary: hold the space location grip and press Ctrl: once base, twice net, 3 times usable, 4 times gross. Manual offsets only. ([G:905AF18A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-905AF18A-2138-4C42-87B5-5A155C63BB2D))
- Edge grip modes (Ctrl cycles): Offset (default), Add Vertex, Convert to Arc / Convert to Line, Offset All. ([G:C86F611A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C86F611A-1E32-4588-9EE9-BB31CC9B1137), [G:1A7F5ABB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1A7F5ABB-6A59-4017-B5CB-215EE8416A5C))
- Undo all manual grip edits: Space tab > Boundary panel > Reset All. ([G:F0593DAA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F0593DAA-D5F1-4A71-A854-957C95CB170D))

Area calculation standards:
- Set one per drawing: [AUTO] `AECSPACECALCULATIONSTANDARD`, or Options > AEC Object Settings tab > Calculation Standard. Only ONE standard applies to a drawing. ([G:FFF2404B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FFF2404B-6EEC-44D6-BB89-148D50929291), [G:F5F589C4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F5F589C4-F66C-4FE6-8BC1-B00EC37C670D))
- Works ONLY on associative spaces. Non-associative boundaries come from the style or manual edits. ([G:FFF2404B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FFF2404B-6EEC-44D6-BB89-148D50929291))
- Shipped: BOMA (USA), DIN-277 (Germany), SIS (Sweden), Basic (generic). ([G:FFF2404B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FFF2404B-6EEC-44D6-BB89-148D50929291))
- Each standard is a .NET DLL plug-in in the `Space Calculation Standards` folder under the program folder. The help writes it as `C:\Program Files\AutoCAD Architecture <version>\Space Calculation Standards\` ([G:12A78DAF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-12A78DAF-BC91-468E-B8EA-3E41A2E733E8), [G:8436CEBA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8436CEBA-179A-440E-AB27-16FAD3F4DEF9)) and also as `\Autodesk AutoCAD Architecture <version>\Space Calculation Standards\` ([G:8999676F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8999676F-B45E-44C5-895B-F8A4CFBFBF45)). The Basic standard sits in the application folder itself; do not move or delete it. ([G:8999676F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8999676F-B45E-44C5-895B-F8A4CFBFBF45), [G:27A46657](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-27A46657-53AE-472B-B87D-9393BEFC72C2)) (inference: on an AutoCAD 2027 install with the MEP toolset the real folder may differ from these ACA paths; check the machine.)
- A DLL copied in while the program runs loads only after a restart. ([G:8436CEBA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8436CEBA-179A-440E-AB27-16FAD3F4DEF9))
- Changing a drawing's standard recalculates every space and inserts the new standard's classification definition. Spaces may need re-classifying (a SIS "Shaft" becomes BOMA "Unspecified"). The old definition stays; delete it in Style Manager only after no space uses it. ([G:B54939D7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B54939D7-2903-4BCE-8E5C-14A8598725EB))
- Classify a space [GUI]: select it, Properties > Extended Data tab > Classification > Select Classification worksheet. ([G:1534A2AC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1534A2AC-59AD-4F90-9569-7E3B926F2DA3))

What the US standards do:
- Basic (generic US practice; no classifications) ([G:3B015299](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B015299-DED5-4B6E-B799-678087746577)): Net at door in a shared wall = centerline of door panel; at an opening = centerline of opening frame; at walls = adjacent face. Gross at a wall with no neighbor = opposite face; with a neighbor = wall centerline.
- BOMA (subset) ([G:EA028DDE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EA028DDE-8C0E-4460-AA88-8D4705A4CBE2)): classifications Office Area, Store Area, Major Vertical Penetration (stairs, shafts, vertical ducts, atria), Floor Common Area (washrooms, electrical, telephone, mechanical rooms, public corridors), Building Common Area (lobbies, conference, mail, fully enclosed mechanical or equipment rooms), Exterior, Street frontage. Note: the page lists mechanical rooms under both FCA and BCA.
  - Net = inside of wall.
  - Usable at exterior walls = inside of glass if window height >= 50 percent of ceiling height, otherwise inside of wall.
  - Usable between spaces depends on both classifications. Same class, or any Office/Store/BCA pair = wall centerline. Office, Store or BCA next to FCA or MVP = inside face. FCA next to Office, Store or BCA = outside face; FCA next to MVP = inside face. MVP next to any other class = outside face. Store next to Street frontage = outside face.
  - Gross = outside face where there is no neighbor or the neighbor is street frontage; centerline otherwise.
- Closed polylines or rectangles can generate a deduction space inside an associative space (construction or unavailable area). Fixed rule because plain AutoCAD objects cannot be classified: BOMA deducts from net only; Basic and DIN 277 from net but not gross; SIS from net and usable but not gross. ([G:EA028DDE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EA028DDE-8C0E-4460-AA88-8D4705A4CBE2), [G:3B015299](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B015299-DED5-4B6E-B799-678087746577), [G:5624DD14](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5624DD14-88F0-4FD5-8211-62B4B042474C), [G:4C3F946C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4C3F946C-7AE8-4C5D-87AE-3DAAB24F6FAA))
- DIN 277 and SIS are European rule sets (space types A/B/C; 0.15 m usable offsets; SIS room-height rule of 1.90 m, new in 2027, can change legacy SIS spaces). See [G:5624DD14](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5624DD14-88F0-4FD5-8211-62B4B042474C) and [G:4C3F946C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4C3F946C-7AE8-4C5D-87AE-3DAAB24F6FAA) if needed.

Calculation modifiers ([G:93F4CD18](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-93F4CD18-7724-4381-A96F-957678BEF1F8), [G:3944F97C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3944F97C-9B8D-4CD8-BC37-2D6684A89FF7)):
- A value or formula applied to area and perimeter (plaster deduction, balcony at 50 percent). Attach to a space or to a zone (then it hits all attached spaces).
- By default it changes only BASE area and BASE perimeter. To affect net, usable, gross, add a property set definition with calculated-area and perimeter properties for those boundaries. ([G:81674590](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-81674590-7A97-4E5E-AA63-79015CC0B05C))
- Order matters and they stack: on 25 m2, deduct 0.3 then halve = 12.35; halve then deduct = 12.2. 50 percent on a space plus 50 percent on its zone = 25 percent. ([G:3944F97C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3944F97C-9B8D-4CD8-BC37-2D6684A89FF7), [G:1CB8F8D7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1CB8F8D7-F954-4188-AF8C-7DD0FEE8D828))
- Style [GUI]: Style Manager > Documentation Objects > Calculation Modifier Styles; Apply To tab (Area, Perimeter or both); Definition tab: variables (Name, Value) and Expression, e.g. `AreaValue * Plaster_Deduction`. Type `AreaValue`, `PerimeterValue` or `Value` exactly as the Data field shows. Variable names: no spaces, no special characters except underscore, no accents, no Visual Basic key words. Test with Input/Output. ([G:3E7544C3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3E7544C3-E0E4-4F58-86D3-F090C1587EAD), [G:0CAFC306](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0CAFC306-D95E-4E9A-AD0F-18A3E3F05C9E))
- Attach [GUI]: double-click the space, Properties > Basic > General > Calculation modifiers; multi-select works only if all have the same modifiers in the same order. ([G:81674590](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-81674590-7A97-4E5E-AA63-79015CC0B05C))

## 11.10 Surfaces, openings, adjacency and the Space/Zone Manager

Why it matters: 3D space surfaces and openings feed building heating and cooling load calculations in an engineering application. Adjacent spaces and surface types are detected automatically for all spaces at gbXML export. ([G:F929DD78](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F929DD78-6E3F-4CEF-933E-86155A4124FC), [G:41FD87E1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-41FD87E1-5766-46F5-957F-4DDA8876D378), [G:D7911DC9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7911DC9-BEA0-4B06-8317-64969AAAFA5E))

Space/Zone Manager [GUI] ([G:87BCC569](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-87BCC569-4535-4163-8A15-AF95BA750904)):
- Open: select a space > Space tab > Helpers panel > Space/Zone Manager. Also the Space/Zone Manager button on the space or zone Properties palette ([G:FA7BE084](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA7BE084-7575-457B-997C-A68850BDDE86), [G:26C10722](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-26C10722-B05F-4618-B033-604C9D92F8F6)).
- Check both "Show all Zones and Spaces" and "Show Space Surfaces" to see every space with its surfaces and openings.
- Tree: spaces sit under their zone or under the Unattached Spaces folder; surfaces under the space; openings under the surface. Unattached spaces are easy to spot here before a gbXML export (inference).
- Other way in (non-associative only): Edit Surfaces grip > Edit Surface Properties grip.

What can be edited ([G:F929DD78](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F929DD78-6E3F-4CEF-933E-86155A4124FC)):
- Non-associative 3D space: surface name, type, style; surface height (extruded only); openings and their name, type, style, size, area.
- ASSOCIATIVE space: ONLY surface name, surface type, and ceiling and floor style. Everything else, including openings taken from the walls, is read-only.

Surface fields ([G:CE289BED](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CE289BED-1947-4398-9099-BE6132787559), [G:45363341](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45363341-FA69-4A73-8914-E653CC5E7DAC)):
- Wall surface Type: Interior Wall, Exterior Wall, Shade, Air, Underground Wall. Style: any wall or curtain wall style. Surface type (3D freeform only): Ceiling, Floor, Surface.
- Height / Area (extruded 3D only): tick Override Default Surface Height, enter Height or Area (both change only the height).
- Ceiling Type: Ceiling, Roof, Underground ceiling; Style = slab or roof slab style.
- Floor Type: Interior Floor, Raised Floor, Slab on Grade, Underground Slab; Style = slab style.
- Add or remove an opening: right-click the surface > Add Opening, or the opening > Remove Opening.

Opening fields ([G:19912531](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-19912531-C148-4E08-9B14-3FF5FFCFF30C)):
- Type: Fixed Window, Operable Window, Fixed Skylight, Operable Skylight, Non sliding Door, Sliding Door, Air.
- Style: any window, door, or door/window assembly style. Area, Height, Width.
- 3D freeform: height and width are not editable here (use grips). Reported area = the part of the opening on this surface; read-only.

Openings by grips [GUI]:
- Openings go only on NON-associative extruded 3D (rectangles only) and 3D freeform (any shape) spaces. Associative spaces take openings from their boundary walls. ([G:41FD87E1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-41FD87E1-5766-46F5-957F-4DDA8876D378))
- Add: select space > Edit Surfaces grip > (freeform: surface grip) > Add Window grip; Ctrl+click for a door. Freeform doors sit at the bottom of the surface; extruded doors at the top of the floor surface. No openings on dome or sphere surfaces. Exit with the Exit Editing Surfaces grip. ([G:6BC850C8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6BC850C8-1A78-422E-92A0-1703B7CC28C9), [G:DD0C4722](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DD0C4722-10C1-4FBC-B0B4-C5CFBB5D9C50))
- Ceiling and floor openings of extruded spaces always sit on the bottom or top surface; justification does not move them. ([G:DD0C4722](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DD0C4722-10C1-4FBC-B0B4-C5CFBB5D9C50))
- Edit extruded openings: corner grip stretches; Ctrl moves; Ctrl twice copies. ([G:32484C85](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-32484C85-0650-4511-AA3F-55D976F8581E))
- Freeform opening shape: Edge grip modes Offset, Add Vertex (Ctrl), Convert to Arc/Line (Ctrl x2), Offset All (Ctrl x3); Vertex grip Move, Remove (Ctrl), Offset Edges (Ctrl x2). Extruded spaces cannot have non-rectangular openings; convert to freeform first. ([G:94FB0F15](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94FB0F15-4CB0-449E-8719-631A68CD6EE4), [G:731836E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-731836E7-3F1E-4201-856B-63D8ED631651))
- Moving a freeform opening onto another surface or outside the space makes its reported area zero. ([G:F9B7FF05](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F9B7FF05-04C3-45D8-956C-FA09BAF59629))
- Remove: Remove Opening grip. ([G:E9E725F2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E9E725F2-7C91-4C0A-B34F-07858211B220))
- Openings not shown after editing: the "Surface components" display component is off in the style or object display. ([G:6BC850C8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6BC850C8-1A78-422E-92A0-1703B7CC28C9))

Openings when the space type changes ([G:A9E71AE2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A9E71AE2-82F6-4211-961F-A847A9032277)):
- Extruded 3D to 3D freeform: all kept.
- 3D freeform to extruded 3D: only openings on horizontal roof or floor surfaces and on surfaces that meet the base profile survive, as same-area rectangles. All others are lost.
- Any 3D to 2D: ALL openings lost.
- Associative to non-associative: openings kept and become grip-editable (extruded: non-rectangles become same-area rectangles).
- A freeform edit that moves a surface off its opening's plane deletes the opening; a split through an opening splits it in two.

Adjacency:
- Spaces detect adjacency between surfaces of neighbor spaces; the help says this matters for processing the plan in the AutoCAD MEP 2027 toolset. ([G:DDF0540A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDF0540A-2AA7-40A6-A190-B9BACD855DE0))
- [AUTO] Max distance treated as adjacent: `AECSPACEMAXAUTOADJACENCY`, or Options > AEC Object Settings tab > Maximum Automatic Adjacency. ([G:DDF0540A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDF0540A-2AA7-40A6-A190-B9BACD855DE0))
- [AUTO] Check adjacency before export: `aecshowspaceandadjacencies` (page step) or `AECSHOWSPACEADJACENCIES` (page metadata); lines show adjacent surfaces; Enter hides them. ([G:008DDA60](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-008DDA60-8BD8-4A80-9DB9-4C6B5BC85DAC))

## 11.11 Editing limits for 3D spaces

3D freeform edit in place [GUI] ([G:30001AE8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-30001AE8-CDAB-40FE-B3E0-F59626D21564), [G:F2C8DF5F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2C8DF5F-B933-4E47-8DBF-E27B9809EDBF)):
- NON-associative only. An associative space LOSES associativity when you exit in-place edit. Applies to surface grip edits, Boolean Union, Intersect and Subtract, Split Face, Join Faces and Trim By Plane. ([G:30001AE8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-30001AE8-CDAB-40FE-B3E0-F59626D21564), [G:3AF0BC17](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3AF0BC17-CFB6-4980-927B-6299D6F7ED55), [G:C87CF627](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C87CF627-FC07-40B8-AF61-80A876FD8152), [G:E2CD81BD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E2CD81BD-7A88-4B3A-9C35-7D2A84AFF47F), [G:A479C48F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A479C48F-C7B4-4CC8-B00C-AA09C32ACD08), [G:495B50B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-495B50B3-A367-4626-AEC4-B2E6C7DED0CC), [G:456980DC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-456980DC-8491-4DE2-8135-A38C104D1C6E))
- Path: 3D isometric view > select space > Space tab > Modify panel > Edit In Place > Edit In Place tab > Modify panel (Boolean drop-down, Split Face, Join Faces, Trim By Plane) > Edits panel > Finish. Boolean prompts: `y` erases the picked object, `n` keeps it.
- Starting Edit In Place on an EXTRUDED 3D space converts it to 3D freeform. Converting back drops geometry an extruded space cannot hold. ([G:F2C8DF5F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2C8DF5F-B933-4E47-8DBF-E27B9809EDBF))
- Surface grip: 6 modes cycled with Ctrl (move, pull, push/pull, orthogonal or free). A pull that would make neighbor surfaces non-planar snaps back with a command-line error. ([G:30001AE8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-30001AE8-CDAB-40FE-B3E0-F59626D21564))

Extruded 3D, non-associative only [GUI] (right-click > AEC Modify Tools):
- Divide (pick line start and end; properties copied to both). ([G:041CD9E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-041CD9E7-F83E-4C5F-BE47-F329C7F24F1B))
- Trim (line, then side). ([G:F6A48C80](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F6A48C80-3AA6-4C09-BB5A-C24580B353DD))
- Merge (`y` erases the second space): only spaces on the SAME Z plane. A non-associative freeform can merge into a 2D or extruded space, not the reverse. The FIRST selected space's name, style, zone attachments, heights, offsets and display win. ([G:81FFF142](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-81FFF142-D29A-4FEC-B723-5FDA5761022A), [G:F97035B6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F97035B6-464A-40F6-922C-83574CBA8783))
- Subtract (hole; the cutter can be a closed polyline; `y` erases it) and Crop (overlap of two spaces; first space's properties win). ([G:E3FF35E7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E3FF35E7-D3E9-4F3C-B319-13918C4CE357), [G:6A2D707E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6A2D707E-1F2A-42C0-9CEB-22B5398248B2))
- Remove Void: Space tab > Modify panel > Remove Void (non-associative 2D and extruded 3D). ([G:BEA15E9F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BEA15E9F-FA92-4366-9118-3377C21F9477))

Interference (associative and non-associative) ([G:2DB986C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2DB986C2-049F-472A-9723-4E8912925B01), [G:91A301C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91A301C2-402C-42AC-9391-DA0E677EEAE4)):
- Space tab > Modify panel > Interference drop-down > Add (or Remove), select the intersecting objects, Enter. Any AEC object with 3D geometry or a polyline.
- Deducted from the BASE VOLUME. Schedule "Base Area Minus Interference" for area without it.

Calculation cut planes (3D freeform): Properties > Basic > Advanced Dimensions > Calculation plane height 1 and 2; schedulable. ([G:2FCBAA4B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2FCBAA4B-6EBA-4385-A8AB-F9E8CD6A16F4))

## 11.12 Zones

What a zone is ([G:453139CF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-453139CF-2977-46C0-BDD0-FE297A0B478D), [G:738D6DC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-738D6DC2-D971-4AE2-BC13-43609193B8AC), [G:6B6EE9F9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6B6EE9F9-77E8-4A9C-85F7-982420557430)):
- A container for spaces and other zones. Zones nest (building > floor > apartment > rooms). A zone attached to a zone is a subzone. ([G:BD2E0D45](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD2E0D45-869E-4B45-9576-6866953C9E72))
- A space may sit in several zones unless the zone style forbids it.
- Name lists attach through the zone STYLE. Calculation modifiers attach to the ZONE and hit every attached space and zone.
- For load analysis: EVERY space must be attached to a zone before gbXML export. The zone carries the design heating and cooling temperatures (11.13). ([G:52809F7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52809F7E-D03C-4B88-B78E-A320A6E2804A), [G:89ABC746](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89ABC746-2FE4-4B8D-95F7-D1998FC0501B))
- For load calculation, zone styles have no settings to configure. ([G:3D7A14BA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3D7A14BA-37A6-4EC5-B4C7-86BF8EE0895A))
- (inference) For HVAC use, make one zone per thermal or air-handler zone, use a zone style set to Space Exclusive so a room cannot land in two HVAC zones, and Zone Exclusive to keep HVAC zones apart from lighting or rentable zones.

Create a zone [GUI] ([G:D5999117](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D5999117-A0C0-4D92-85B6-9567D1D2B0F0), [G:B6400C43](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B6400C43-015B-4F2C-B68A-7DB9E83D30B2)):
- Zone tool on a palette, or Home tab > Build panel > Space drop-down > Zone.
- Set properties on the Properties palette BEFORE picking: Name, Style, Tag, Calculation Modifiers, Zone boundary offset, Calculate Area, Calculate Perimeter, Can Contain Spaces, Can Contain Zones.
- Pick the insertion point; repeat; Enter ends.
- Zone tools carry the same settings; make them by dragging a zone or zone style onto a palette. Zone tools ship in the Stock Tool and Sample Palette catalogs. ([G:A9CE82F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A9CE82F3-2E93-46B7-BAA8-A38A9E3237EF), [G:C1F5DF9A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C1F5DF9A-3F58-4C89-BF37-C5035FC0B3B2))

Zone properties (Properties palette) ([G:26C10722](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-26C10722-B05F-4618-B033-604C9D92F8F6)):
- General: Description, Layer, Style, Name (drop-down if the style has a list), Tag (only while adding), Calculation Modifiers, Number of Spaces (direct), Total number of spaces (direct plus via subzones), Number of Zones, Total number of zones, Space/Zone Manager button.
- Dimensions: Base area (all attached spaces), Calculated area (after modifiers), Base perimeter, Calculated perimeter, Base volume, Zone Boundary Offset.
- Calculation: Calculate area, Calculate perimeter (Yes = include attached spaces with their modifiers). ([G:4618C022](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4618C022-8230-4C22-95FE-6916A9360AB4))
- Content: Can contain spaces, Can contain zones. ([G:17A8216E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-17A8216E-C0B8-48EC-9FE9-F7999F30E760))
- Location: Rotation, Elevation, Additional Information.
- Zone boundary offset 0 draws it on top of the space base boundary, where draw order can hide it; use a value above 0. Still not visible: the Zone boundary display component is off in the zone style. ([G:24BC0192](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-24BC0192-07D4-4A3C-BADD-BA490A727168))

Attach and detach [GUI]:
- Attach: select the zone > Add (Plus) grip, or Zone tab > Modify panel > Attach; pick spaces or zones; Enter. ([G:89ABC746](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89ABC746-2FE4-4B8D-95F7-D1998FC0501B), [G:BD2E0D45](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD2E0D45-869E-4B45-9576-6866953C9E72))
- Detach: Detach (Minus) grip on the connection line, or Zone tab > Modify panel > Detach; pick; Enter. Only DIRECT attachments can be detached. ([G:F8401C02](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8401C02-D049-438B-B251-CCDBEB75C0ED))
- Select Attached: Zone tab > Modify panel > Select Attached. Items in an xref are highlighted but NOT selected. ([G:85F6EDFF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-85F6EDFF-9FF5-44F3-B66E-5F9E1C2F0750))
- Zone Layout: Zone tab > Modify panel > Zone Layout; pick the top node; give column and row distances. ([G:FDAD964F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FDAD964F-417D-4AD7-8DDD-204E888B4159))
- Attachments work for spaces and zones inside blocks; EXPLODING the block removes them. ([G:BD2E0D45](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD2E0D45-869E-4B45-9576-6866953C9E72))
- No command name is given for Attach or Detach. The obsolete-command map names `AecZoneAttach` and `AecZoneDetach` as current commands ([G:B3D59002](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B3D59002-3108-41C7-A282-A3FB01176C6C)); prompts undocumented.

Xref rules ([G:738D6DC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-738D6DC2-D971-4AE2-BC13-43609193B8AC), [G:89ABC746](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89ABC746-2FE4-4B8D-95F7-D1998FC0501B), [G:D7911DC9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7911DC9-BEA0-4B06-8317-64969AAAFA5E)):
- You CAN attach spaces or zones in an xref to a zone in the current drawing.
- You CANNOT attach current-drawing spaces or zones to a zone inside an xref.
- Detaching the xref detaches those spaces and zones from the zone; re-attaching the xref means re-attaching them by hand.
- Zones inside an xref export to gbXML only when attached to a zone in the current drawing.
- SIS standard: space and zone interaction works only when the zones are in the same drawing as the spaces. ([G:4C3F946C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4C3F946C-7AE8-4C5D-87AE-3DAAB24F6FAA))

Zone styles ([G:89BEF9C0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89BEF9C0-6E26-4B1C-9EAD-940497556918), [G:A43BCF02](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A43BCF02-4FD3-49E6-B989-5A90A741D5DF)):
- Control display of the zone, its connection lines, zone boundary and hatch; content rules; classifications (Classifications tab, [G:D183A3B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D183A3B9-7E1A-4A57-8860-4A8EE48898F4)); name list (Design Rules tab > Zone Names, [G:761FDCF6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-761FDCF6-1226-42E2-B409-107956DB8C69)).
- Style Manager path conflict: "Documentation Objects > Zone Styles" ([G:A43BCF02](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A43BCF02-4FD3-49E6-B989-5A90A741D5DF), [G:3D7A14BA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3D7A14BA-37A6-4EC5-B4C7-86BF8EE0895A)) vs "Architectural Objects > Zone Styles" ([G:F7A9B81E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F7A9B81E-F69D-47C6-B0A9-51B2FA034CDB), [G:183E80E4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-183E80E4-60E7-4DA2-9E49-7152ADC2B0C7), [G:C0458D19](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C0458D19-6128-46E2-B525-E3EBF6BA093F)). Both appear in the 2027 help; look under both.
- Design Rules tab > Exclusivity ([G:F7A9B81E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F7A9B81E-F69D-47C6-B0A9-51B2FA034CDB), [G:BD2E0D45](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD2E0D45-869E-4B45-9576-6866953C9E72)):
  - Space Exclusive: a space attaches to only ONE zone of this style. Attaching it to a second one silently disconnects it from the first.
  - Zone Exclusive: zones of this style attach only to zones of the same style. A mismatch makes no connection and prints an error on the command line. Help example: HVAC zone only to HVAC zone, Lighting only to Lighting.
  - Both rules are honored in xrefs. Styles converted from legacy area group styles have both turned OFF. ([G:95729605](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-95729605-7238-4B56-A942-9FE65F650844))
- Display components (Display Properties > Layer/Color/Linetype): Zone boundary, Hatch, Name, Marker, Zone Connection Line, Space Connection Line. Zone hatch draws on top of space hatch. ([G:194223A7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-194223A7-E0BA-4B1D-8A82-28076A7D00B7))
- Other tab: hatch "Draw All" cleared = only directly attached spaces get the zone hatch; selected = also spaces attached through subzones. Marker is 1/50 of screen size unless User Defined Scaling is on. ([G:C0458D19](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C0458D19-6128-46E2-B525-E3EBF6BA093F), [G:96DEF613](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-96DEF613-BE82-4277-A6B8-8B7AC64F8820), [G:EDFE04EA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EDFE04EA-19A8-4DF2-A78F-C027BCF0A2BA))

Zone templates ([G:1FA1BC01](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1FA1BC01-FCE5-4A03-B692-4E39986FB92C), [G:1CB8F8D7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1CB8F8D7-F954-4188-AF8C-7DD0FEE8D828), [G:D8A89971](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8A89971-BB76-4C8F-8DEB-60FB9A4A0675)):
- A reusable zone hierarchy. Used ONLY at insert: later template edits do not reach zones already made, and edits to placed zones do not change the template.
- Build [GUI]: Style Manager > Documentation Objects > Zone Templates > template > Content tab. Tree: right-click New (subzone), Rename, Delete; drag to reorder. Per node: description, style, allowed content (spaces, zones, both), calculation type, calculation modifiers.
- Gotcha: if a zone style requires zone exclusivity, only subzones of the same style can be added; another style gives an error.
- Insert: "Zone from Template" tool > Properties > zone template, Row Offset, Column Offset > pick insertion point > Enter.

Zone polylines ([G:B0A3196D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B0A3196D-78F4-4D1B-90CD-D8EA416646F0)):
- Zone tab > Modify panel > Create Polyline; [AUTO] prompt: `D` = directly attached spaces only, Enter = all attached spaces including through subzones.
- One polyline per boundary if net, usable or gross are offset. Polylines sit on top of the spaces; pick the space under one with Ctrl+click cycling or QSELECT filtered to spaces.

## 11.13 Engineering data for HVAC loads

Four property sets carry the load data. Do not mix up the names:
| Property set | Goes on | Holds | Source |
|---|---|---|---|
| SpaceEngineeringStyles | space STYLE | lighting and equipment load per area; optional gbXML space type override | [G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A), [G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3) |
| SpaceEngineeringObjects | each SPACE | ConditionType, LightingLoad, EquipmentLoad, OutsideAirFlow, SupplyAirFlow, ReturnAirFlow | [G:9DE7186B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DE7186B-E54B-4E83-BA70-FC07004EC05F) |
| ThermalProperties | spaces (per page intro) | not described in the pages used here | [G:9DE7186B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DE7186B-E54B-4E83-BA70-FC07004EC05F) |
| ZoneEngineeringObjects | each ZONE | design heating and cooling temperatures | [G:52809F7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52809F7E-D03C-4B88-B78E-A320A6E2804A) |

Load the definitions into the drawing [GUI] ([G:9DE7186B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DE7186B-E54B-4E83-BA70-FC07004EC05F)):
1. Manage tab > Style & Display panel > Style Manager.
2. Style Manager File menu > Open Drawing; in the Open Drawing dialog click Content; go to the `Styles/Imperial` folder; open "gbxml Property Set Definitions (Imperial)".
3. Expand that drawing's Documentation Objects > Property Set Definitions (holds SpaceEngineeringObjects, ThermalProperties, ZoneEngineeringObjects); copy them to the current drawing; OK.
- SpaceEngineeringStyles exists only in drawings made from templates shipped with Autodesk Building Systems 2007 or the AutoCAD MEP 2027 toolset. If missing, copy it with Style Manager from the "Aecb Model" drawing template (Documentation Objects > Property Set Definitions). ([G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A), [G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3))
- (inference) Starting new MEP drawings from the shipped Aecb Model template avoids most of this copying; the help only says that template carries SpaceEngineeringStyles.

Configure space styles for loads [GUI] ([G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A), [G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3)):
1. Style Manager > current drawing > Architectural Objects > Space Styles > right-click New; rename; keep it selected.
2. General tab > Property Sets button (bottom) > Edit Property Sets Data > Add Property Sets > SpaceEngineeringStyles > OK.
3. Enter the area lighting load and area equipment load.
4. Optional: the gbXML space type override restricts the style to ONE space type and OVERRIDES any classification set on the style.
5. Classifications tab > browse button next to Space Occupancy > Select Classification > expand the standard > pick a space type > OK.
6. Repeat per room type. Display Properties tab for looks.
- The classification sets occupant density and outside air requirements automatically, from values built into the software (based on the mechanical standard or code). ([G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3))
- View those values: Style Manager > Space Occupancy (left tree) > Classifications tab > select the space type > Property Sets button > Edit Property Set Data dialog. ([G:19613E89](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-19613E89-C1FF-4667-B22C-77F5B77BCBDD))
- RULE: a classification is REQUIRED for gbXML export. Set it one of three ways: on the space style; as a classification override in the space style property set; or by hand on the space's Extended Data tab. ([G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3), [G:BEC233CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BEC233CF-6E7E-4788-8BF6-8C66905AA52A))

Add engineering data to spaces [GUI] ([G:9DE7186B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DE7186B-E54B-4E83-BA70-FC07004EC05F)):
1. Select the spaces.
2. Properties palette > Extended Data tab > Add property sets button.
3. Add Property Sets dialog: the step text says pick "SpaceEngineeringObjects and SpaceObjects". The same page's intro says spaces need SpaceEngineeringObjects, ThermalProperties and ZoneEngineeringObjects. "SpaceObjects" is not one of the definitions the page lists. Pick SpaceEngineeringObjects plus whatever space sets the list offers from the gbxml drawing (inference: verify in the dialog).
4. Edit values under Property Sets:
   - ConditionType: how the room is conditioned.
   - LightingLoad: if the style gives lighting per area, DefaultLightingLoad computes it from room area. A typed LightingLoad overrides it.
   - EquipmentLoad: same logic with DefaultEquipmentLoad.
   - OutsideAirFlow: outside airflow value.
   - SupplyAirFlow, ReturnAirFlow: for reference only. Room totals, not per area or per person.

Add engineering data to zones [GUI] ([G:52809F7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52809F7E-D03C-4B88-B78E-A320A6E2804A)):
1. Create the zones; select all of them.
2. Extended Data tab > Add property sets > ZoneEngineeringObjects > OK.
3. Enter the design heating and cooling temperatures.

Pre-export checklist (assembled from the pages above; the order is inference):
- Definitions loaded; space styles carry SpaceEngineeringStyles and a classification.
- Spaces generated (associative, from the xref plan) and carry SpaceEngineeringObjects data.
- Zones carry ZoneEngineeringObjects temperatures.
- EVERY space is attached to a zone in the current drawing; the Space/Zone Manager "Unattached Spaces" folder should be empty. ([G:52809F7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52809F7E-D03C-4B88-B78E-A320A6E2804A), [G:87BCC569](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-87BCC569-4535-4163-8A15-AF95BA750904))
- Maximum Automatic Adjacency set; adjacency lines checked. ([G:DDF0540A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDF0540A-2AA7-40A6-A190-B9BACD855DE0), [G:008DDA60](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-008DDA60-8BD8-4A80-9DB9-4C6B5BC85DAC))
- Surface and opening types reviewed in the Space/Zone Manager. ([G:F929DD78](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F929DD78-6E3F-4CEF-933E-86155A4124FC))

## 11.14 gbXML export and the round trip

Export zones for load analysis ([G:D7911DC9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7911DC9-BEA0-4B06-8317-64969AAAFA5E)):
- [AUTO] Command name: `GBXMLEXPORT` (page metadata). The steps say "Click Export gbXML"; the page gives no ribbon tab or panel.
- It opens the Export to gbXML dialog [GUI]. No dash-prefixed or script form is documented, so it blocks an unattended script. Test any headless route before relying on it.
- Prerequisites: spaces configured with property set values and attached to zones.
- Dialog fields:
  - File name: name and location of the gbXML file.
  - Select Objects: auto-detects all zones in the current drawing. Zones in referenced drawings are NOT exported unless attached to a zone in the current drawing. If zones are missed, click Select Objects and pick them.
  - Building Type: building type and postal ZIP code, passed to the analysis program.
  - Progress: Start runs the export.
  - Success: View Event Log lists errors.
- Close. The file then goes to the analysis program.
- Adjacent spaces and space surface types are detected automatically for all spaces at export.
- Whole building: attach zones and spaces from xref drawings (one per floor, for example) to zones in one current drawing, then export from it.

Silent export failures to rule out first:
- A space not attached to any zone. ([G:52809F7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52809F7E-D03C-4B88-B78E-A320A6E2804A))
- Zones only in an xref, not attached to a current-drawing zone. ([G:89ABC746](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89ABC746-2FE4-4B8D-95F7-D1998FC0501B), [G:D7911DC9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7911DC9-BEA0-4B06-8317-64969AAAFA5E))
- A space with no classification. ([G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3))
- Attachments lost because a block holding spaces or zones was exploded. ([G:BD2E0D45](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD2E0D45-869E-4B45-9576-6866953C9E72))
- A space attached to a second zone of a Space Exclusive style, which silently dropped the first attachment. ([G:F7A9B81E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F7A9B81E-F69D-47C6-B0A9-51B2FA034CDB))

The return trip:
- The help promises you can import the analysis results and view calculated loads and airflows per space and zone, then design duct systems. ([G:12BA7941](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-12BA7941-013D-4F8E-A21B-373456B3952C))
- Steps 9 and 10 of the MEP workflow name "To Import Load Analysis Results" and "To Use Space and Zone Calculated Data" (show results in tags and schedules). Those pages were not among the help pages condensed here, so this section documents no command, dialog or file format for the import. ([G:5607D12D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5607D12D-CB83-445C-A1FE-CAA70E19CAD0))
- Duct sizing does not read space airflows. It reads Flow from the air terminals and other MvParts (11.16). Moving load results into terminal flows is a manual step in these pages (inference).

## 11.15 Space data out: schedule properties, evaluation, exports

Output routes for space data ([G:527C3DD0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-527C3DD0-7691-4CCB-B28D-89B2BEEC0186)):
- Schedule table in the DWG (property data readable by any DWG reader, including plain AutoCAD).
- DWF export with property data.
- Database export of space property data to XLS, CSV or TXT.
- Space evaluation (XLS or TXT): only a SUBSET of properties; needed for decomposition data.
- Autodesk MapGuide export of property set data.
- [AUTO] Access MDB: the old `SpaceInfo` command is replaced by `AECEXPORTPROPERTYDATA`. Its prompts or dialog are not documented here.

Automatic (derived) space properties for schedules and tags ([G:6AE1AF64](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6AE1AF64-5B20-4022-AFAC-1875F021797C)). Put them in a property set definition attached to the space or space style:
- Base: Base Area; Base Area Minus Interferences; Base Ceiling Area; Base Perimeter; Base Perimeter Including Interferences; Base Surface Area; Base Volume.
- After modifiers: Calculated Area; Calculated Perimeter; Calculation Modifier.
- Net, Usable, Gross, each: Area; Area Minus Interferences; Calculated Area; Calculated Perimeter; Perimeter; Perimeter Including Interferences. Plus Net to Gross Offset.
- Calculation Plane 1 and 2: Area, Height, Perimeter (3D freeform only; every plane gives the same area in an extruded space).
- Geometry: Ceiling Thickness; Floor Thickness; Height (ceiling height); Length; Width; Space Above Ceiling; Volume Above Ceiling; Volume Below Floor; Volume Overall; Wall Area (wall sides, for paint or plaster). All volumes derive from the base volume.
- Style targets: Target, Minimum, Maximum Area, Length, Width.
- Identity: Name; Description (and from Style); Notes (and from Style); Documents (and from Style); Hyperlink; Layer; Linetype; Color; Color - Text; Style; Handle; Object ID; Object type (always SPACE); Drawing Fingerprint GUID (system value used in export to Building Systems applications); Has Net, Usable, and Gross Boundaries (legacy).
- Adding one [GUI]: Style Manager > Documentation Objects > Property Set Definitions > definition > Definition tab > add automatic property; pick one source property per object type. The Description becomes the default schedule column header and does NOT follow later renames. ([G:2981C808](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2981C808-4C2A-40A7-B1E4-DDDF2BC6CC06))
- A property set definition used by schedule tags must not have spaces in its name. ([G:C4177CD9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C4177CD9-7960-4E6E-947F-4B75DDDBA51E))

Space evaluation (area reports to Excel or text) [GUI]:
- Open: Scheduling tool palette > Space Evaluation tool; Home tab > Inquiry panel > Space Evaluation ([G:EF8B3490](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EF8B3490-53AE-4718-BA59-CDA1071A5342)); or Annotate tab > Scheduling panel > Evaluate Space ([G:E7DE8909](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7DE8909-B0F6-4280-A81D-3D964FAA35F5)). The two pages give different ribbon paths.
- Evaluates selected or all spaces and zones from one or several open drawings and from xrefs (an xref button adds them). ([G:1AB39058](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1AB39058-E219-4DFF-A37C-9304202BC893), [G:E7DE8909](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7DE8909-B0F6-4280-A81D-3D964FAA35F5))
- Check marks: black = selected; gray = a child is selected but the zone itself is not included; blue = included because its zone is checked. If the zone is in the drawing and its spaces are in an xref, check the xref spaces explicitly. ([G:E7DE8909](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7DE8909-B0F6-4280-A81D-3D964FAA35F5))
- XLS needs an XLT template; TXT needs a TXT template. Set defaults in Evaluation Options > Templates tab ("Excel Template File", "Text Template File"). With no default you are asked for a template on EVERY run (a file dialog that blocks a script). Shipped templates: `C:\ProgramData\Autodesk\ACA <version>\enu\Template\Evaluation Templates`. ([G:107BB2A4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-107BB2A4-F02C-40A2-9A2B-296123F9449A))
- XLT named cells: AREA_EVALUATION_BEGIN, AREA_COLUMN_IMAGE, AREA_COLUMN_LABEL, AREA_COLUMN_EXPRESSION, AREA_COLUMN_RESULT, AREA_COLUMN_EXACT_VALUE. ([G:265A283D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-265A283D-55CE-45EB-BC06-709345F95C72))
- TXT has no images; XLS includes bitmap previews. ([G:A2F44DA6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A2F44DA6-05ED-4222-B82B-FC86AAB58583), [G:F90C7165](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F90C7165-552D-472A-BBDD-C3322AB02C52))
- Legacy area-evaluation tools or commands show a prompt; replace them in scripts and palettes with the space evaluation. ([G:1AB39058](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1AB39058-E219-4DFF-A37C-9304202BC893))

## 11.16 Duct sizing inputs: terminal flows and system design parameters

How the sizer sees a system ([G:731E8501](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-731E8501-5CB0-47B6-9D68-C70BB013D6DE), [G:72D5BDE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-72D5BDE1-1D7B-47F0-A826-2F57C87D43C2)):
- A duct run = ductwork connected to one or more outlet devices that have a defined outlet flow. Outlets (diffusers) are the ends of the system.
- Each segment carries the summed flow of every outlet downstream of it. That flow sizes the segment.
- REQUIRED: flow values on ALL outlet parts before any size calculation.
- A duct's Flow Rate property is read from connected MvParts. With no MvPart connected it is 0. In Add mode it can also be typed. ([G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7), [G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26))

Setting terminal and equipment flow [GUI] (no command-line or batch method is documented):
- Equipment tab > Modify panel > Equipment Properties > Multi-view Part Properties dialog > Flow tab. Outlet device (ceiling diffuser): enter Flow. Supply device (VAV box): enter an airflow for EACH connector. ([G:1A5B5DA9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1A5B5DA9-1B83-48C2-A0B7-4A72F4290AFF))
- Or Equipment tab > Modify panel > Modify Equipment (`MVPARTMODIFY`) > Multi-view Part Modify dialog > Flow tab > "Flow (Each Terminal)". ([G:62254257](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-62254257-A9A1-4DA8-A0F8-E83FB9D3132B), [G:B836B203](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B836B203-E58F-4F8B-998B-5BEEBCE44942))
- Or at placement: Home tab > Build panel > Equipment drop-down > Add MvParts dialog > Flow tab (shown only when airflow can be assigned). ([G:7755CBC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7755CBC9-2AEB-4F80-89A5-CD5B46751449))
- The pages show the Flow tab for one selected part at a time. Whether one dialog edit can set flow on many selected terminals is not documented; test it before planning a bulk edit.

System design parameters (the sizing method) [GUI] ([G:CA33E443](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA33E443-DFA2-4A21-BD90-03B664D018AA)):
1. Manage tab > Style & Display panel > Style Manager drop-down > HVAC System Definitions.
2. Duct System Definitions > pick the system (Supply, Return...).
3. Design Parameters tab:
   - Constant velocity method: select Velocity, enter the value.
   - Equal friction method: select Friction, enter the value.
   - Roughness: of the duct material.
   - Density: of the medium. Default = air at sea level, 68 F (20 C).
4. Repeat per system; OK.
- Properties palette Friction and Velocity are read-only copies of these values. ([G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26))
- The Add Duct dialog marks the fixed parameter with an asterisk. The exact size comes from it, then a catalog size is picked, so after sizing the value shown can differ from Design Parameters. ([G:CA33E443](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA33E443-DFA2-4A21-BD90-03B664D018AA))
- Commands for the definitions: `DUCTSYSTEMDEF`, `DUCTSYSTEMDEFEDIT` (Style Manager). ([G:329A8AE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-329A8AE1-9D9B-4A41-B407-DD76DE5B5F47))

The math ([G:0D61887B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0D61887B-31E6-483D-838E-43274CA944A8)):
- Darcy and Altshul-Tsal equations, 2001 ASHRAE Fundamentals Handbook, chapter 34: friction loss eq. 19; friction factor eq. 21; Reynolds number eq. 23; equivalent round diameter of rectangular duct eq. 25; of flat oval duct eq. 26 to 28.
- Rectangular and oval ducts are sized by friction through their equivalent round diameter and its velocity.
- The Add Ducts and Modify Duct dialogs show the ACTUAL velocity for the chosen CFM and size (used for fitting and acoustic analysis), not the velocity inside the friction calculation.
- With no CFM shown, the friction or velocity in those dialogs is the system definition value.
- After constant-velocity sizing, the Properties palette shows the fixed velocity used.

Network prerequisites:
- One connected network. Any unconnected part makes the size tools fail or give inaccurate results. ([G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE))
- Check [GUI]: View tab > MEP View panel > Show Solution Tips (disconnects in red); [Duct / Duct Flex / Duct Fitting] tab > Modify panel > Show Connected Objects drop-down > Show Connected Run; General panel > Select System drop-down > Select Connected Branches (Tab cycles). ([G:D9EB0BF1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D9EB0BF1-C494-426F-8745-3760D74DCBD0))
- Runs with different system definitions connect only if the definitions share a system GROUP; declining the system-change prompt inserts the fitting but leaves the run outside the system. ([G:660EE061](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-660EE061-DEAF-4731-A117-916EAE307A90), [G:2801A5D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2801A5D1-F63A-49B3-85A5-FB41554F4BD6))
- Size lock: a locked segment or fitting keeps its size when the branch is resized; transitions are added at both ends. Use it for tight clearances. ([G:B36C61AD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B36C61AD-B8E4-45B6-93EC-011880F09958))

## 11.17 Duct Size Calculator and instant sizing

Three sizing options ([G:9D9C77E6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D9C77E6-5EE5-4C37-91D2-C963648F77F1), [G:1484E271](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1484E271-AD0A-4935-9334-8E6283C5E699)):
- Duct System Size Calculator: sizes a whole connected system or part of one; converts 1-line systems to sized 2-line; also resizes systems that already have shapes.
- Instant Sizing Calculator: sizes single segments while you draw or modify a run.
- Third-party analysis tools through DDXML (11.18).

Duct Size Calculator ([G:066594C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066594C7-8E6C-47B4-8594-89C29C2D69D6), [G:72D5BDE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-72D5BDE1-1D7B-47F0-A826-2F57C87D43C2)):
- [AUTO] Command name `DUCTSYSTEMSIZECALC`. It opens the Duct Size Calculator dialog [GUI]; no command-line options are documented, so it blocks an unattended script.
- Ribbon: select any object in a connected system (1-line is fine) > Duct tab or Duct Flex tab > Calculations panel > Calculate Duct Sizes.
- Scope: "Calculate complete system", or "Calculate selected objects" (select button, pick, Enter).
- Shape:
  - All: one shape for every part.
  - Individual: one shape for Trunk, one for Runouts. Trunk "Inherit from Fan" needs a fan at the start of the system.
  - "Use shape and size from air terminals on runouts": runouts copy the terminal connection; this disables the Runout shape box.
  - Ducts that already have a shape keep it. Sizes are calculated but the shape cannot be overridden.
- Design parameters:
  - "Override design parameters from system definition(s)": choose Velocity or Friction and a value. Used for THIS run only; the system definition is unchanged.
  - "Round max. size": largest round diameter. "For larger size": Rectangular or Oval; their height will not exceed the max round size.
  - "Rectangular/Oval Max. Height".
  - Catalog sizes: All, 1 inch increment, or Even sizes only.
  - "Apply sizing to parts with defined shape".
- Start. The system is resized in the drawing. Errors: View Event Log.
- Segments are NOT split. One size per whole segment. To step a trunk down after each diffuser, break the duct first, then recalculate:
  - [AUTO] `BREAK`, select the duct, `f`, pick the point, `@`: one break, connectivity kept. ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F))
  - [GUI] Duct tab > Modify panel > Duct Length dialog: Break at a Duct Length (or Pick Length), or Merge (merge cannot cross fittings). Apply to Duct Run for the whole run. ([G:0612CFE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0612CFE6-4571-46F9-B5A9-0ED46F3DC95F))
  - A takeoff on a broken segment stays connected to only ONE of the two new segments; reposition it. ([G:F6FAE92B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F6FAE92B-3DAB-42B6-BBBF-1854F6A7673B))
- 1-line first: draw 1-line duct with shape and Connection Type both Undefined, then let the calculator turn it into sized 2-line duct. ([G:303F3BD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-303F3BD3-216A-4879-AB22-2C5D22758ABE), [G:FCC029C0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCC029C0-B289-4968-B13C-21F3DF7B4539))
- Placeholder parts: dimensionless 1-line parts; the Aecb Model template includes a placeholder routing preference; convert later by changing the part subtype. ([G:764224DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-764224DC-22C3-454C-9256-014074EA15BA))

Instant sizing ([G:3E072A98](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3E072A98-53B4-4297-AF2B-5DB351B54BD7), [G:7E00DA22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E00DA22-CE0D-4199-928C-CBC539FC3F26), [G:4FC48FB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4FC48FB0-A8F1-4360-8CF4-471F62973CD7)):
- Properties palette, Dimensions: "Calculate Size" (Add mode) or "Duct Calculator" (Modify mode). Uses Flow Rate, Friction, Roughness and Density. For rectangular or oval, fix one dimension so the other can be calculated.
- Method (equal friction or constant velocity) comes from the system definition.
- Capacity = sum of the flows of all outlets detected in the run; zero if no outlet has a flow.
- A segment drawn onto an outlet with a flow detects it automatically. A branch not yet connected: pick the outlets to count, or type the capacity.
- Two steps: (1) exact size from flow and the fixed parameter; (2) the NEXT LARGER catalog size is chosen, then velocity and friction are recalculated for that size.

## 11.18 DDXML round trip with external duct tools

What it is ([G:2D49B3DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2D49B3DF-7B7A-4D85-BBA9-45B055D3A833), [G:02E835BB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-02E835BB-24E5-455B-9E0A-2BF76739F0BB)):
- Export the duct system to DDXML (Duct Design Extensible Markup Language), size it in an external tool (help names Trane VariTrane Duct Designer and Elite Duct size), import the sizes, resize.
- Order: (1) review the design for normal practice; (2) assign ASHRAE fitting IDs if the tool needs them; (3) meet the export criteria; (4) export; (5) analyze (sizes are written into the DDXML), import; (6) resize.

Export criteria ([G:32819FD7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32819FD7-2070-4535-8A4A-67C1AE679534)):
- At least one start point and one end point per system.
- Start point = fan or air handling device: fan, AHU, or an MvPart such as a VAV box, mixer or economizer. No air handler in the drawing = the system cannot be exported.
- End points = outlet devices such as air terminals, each with a flow value. An end cap counts as an outlet with flow 0.
- VAV with 2 connectors (single duct): part of the run unless it ends a branch; then it needs a flow value.
- VAV with more than 2 connectors (dual duct): an end point; duct past it is ignored; its connector flow is used.
- A duct segment with takeoffs exports as ONE plenum duct. Break it and add transitions so the tool can size the pieces.
- Preview connectivity: [Duct / Duct Flex / Duct Fitting] tab > Modify panel > Show Connected Objects drop-down > Show Connected Run.

Export [GUI] ([G:08B52ECC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08B52ECC-F47F-4075-BC9D-89CE965A8039)):
- [AUTO] Command name `DUCTXMLEXPORT` (page metadata); button "Export Duct XML". No command-line form documented.
- Duct System XML Export dialog: output path and file name (`*.ddx`); Select Object, pick any segment or fitting of the system; Select System Type; Start; View Event Log on errors.

Import [GUI] ([G:6358DFD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6358DFD5-650D-4B7A-B025-5599DBADA170)):
- [AUTO] Command name `DUCTXMLIMPORT`. Ribbon: Analyze tab > HVAC panel > Import Duct XML.
- Open the drawing that holds the exported system; in the Duct System XML Import dialog pick the DDXML file; Open. The sizes are assigned to the system.

Resize [GUI] ([G:9B227DE8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9B227DE8-76CC-4D1E-8C6F-176F33A89A3D)):
- Analysis tool palette (HVAC workspace) > External Data Resize > System Resize dialog > Select Object (a segment or fitting).
- "Allow parts with custom size" checked = custom sizes allowed. Cleared = catalog parts only; choose how to pick a part when the calculated size has no exact catalog match.
- Start; review the drawing; View Event Log for errors.

ASHRAE fitting IDs ([G:FCDDCD3E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCDDCD3E-63E0-4A3F-BA09-720255266D92)):
- Some tools need every fitting tagged with its ASHRAE fitting number (loss coefficient table).
- Properties palette > Advanced > Engineering Data > Assigned Engineering ID: pick from the list, or type the number if it is not listed. Some fittings depend on flow direction or system type.
- Tag a whole fitting type: select one, Duct Fitting tab > General panel > Select System drop-down > Select Similar.
- From the export: View Event Log > select a multiple-ID warning > Modify Fitting ID icon > Modify Fitting ID dialog > pick or type > OK. The ID is stored on the fitting; rerun the export.

Xref caution: a run connected to a duct in an xref writes the joining fittings into the xref (Save to Xref dialog, blocks a script), and later changes to the connected duct in the host do not propagate into the xref. ([G:EB4AC5CA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB4AC5CA-8873-461B-A7E9-4A80D08673C5), [G:8D39C1F4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D39C1F4-6071-45B8-8EE3-BE8C502647AA))

## 11.19 Pipe and plumbing calculation tools

What the help pages used here cover ([G:0FB67C11](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0FB67C11-0997-4F7B-8EA5-8A37C053B704)):
- Sample sizing tables ship for plumbing supply lines and sanitary lines. Supply tables give equivalent lengths for fittings and valves. Sanitary tables give maximum fixture-unit loads for stacks, branches and offsets. Tables can be edited to match a project or code.
- Plumbing line slope tool: computes start elevation, end elevation or slope of a plumbing line from the run's start or end point; it prompts for one of the three. The task page "To Calculate the Slope of a Plumbing Line" was not among the pages used here.
- A plumbing system type controls pipe sizing, fitting orientation and fixture connections. ([G:E7C4DBC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7C4DBC8-ED10-4641-ACE8-F9F7C831A90F))
- Solution tips mark invalid connections and offer fixes. ([G:A9A4C3BD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A9A4C3BD-6360-4235-B34A-5CC868B14075))
Not covered here: no hydronic (chilled or hot water) pipe size calculator page appears in the help pages used here. Do not assume duct-style system sizing exists for pipe; check the piping section.

## 11.20 Custom area calculation standard (.NET API)

The only API the space help pages expose is the .NET namespace `Autodesk.Aec.SpaceOffsetRulesManager`, used to write an area calculation standard plug-in. No COM or LISP members for spaces or zones appear. ([G:EE8CCD4E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EE8CCD4E-5DCC-4F87-98D5-0A2879C2BCEB), [G:ED1FC905](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED1FC905-7BAF-40A4-9617-48CEF9F8D337))

Project setup ([G:12A78DAF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-12A78DAF-BC91-468E-B8EA-3E41A2E733E8)):
- A .NET class library (DLL). Sample project: AecSpaceOffsetStandardSample. The page is written for Visual Studio 2005.
- Name prefix `AecAreaCalculationStandard` (e.g. AecAreaCalculationStandardBOMA); the software recognizes it and reads the name for diagnostics.
- References from the program folder: `AecSpaceOffsetRuleManager.dll` (the API), `acdbmgd.dll`, `aecbasemgd.dll`, `aecarchmgd.dll`. Set Copy Local = False on each.
- Deploy: copy the DLL (and PDB) into the `Space Calculation Standards` folder (11.9); restart the program after every build. Sample post-build: `@if exist $(TargetPath) @copy $(TargetPath) "C:\Program Files\AutoCAD Architecture <version>\Space Calculation Standards\"`.
- Add `using Autodesk.Aec.SpaceOffsetRulesManager;`. ([G:ED1FC905](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED1FC905-7BAF-40A4-9617-48CEF9F8D337))

Standard class ([G:ED1FC905](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED1FC905-7BAF-40A4-9617-48CEF9F8D337), [G:CEC192C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CEC192C2-4C5B-4849-92C2-893656928D24)):
- Derive from `AecSpaceOffsetStandard`. Parameterless constructor that calls `SetName(string)` (not overridable; the name shows in the standards list).
- Override abstract `InitRules()`; register rules through `NetRules()`, `UsableRules()`, `GrossRules()`, each an `AecSpaceOffsetRuleCollection`.
- Optional virtual database init, called each time the standard is assigned to a drawing. Page text calls it `InitCurrentDatabase()`; the sample and class reference show `InitDatabase(Database)`. Verify in the class reference.
- Also virtual `bool IsStandardStyle(ObjectId idStyle)`.
- GOTCHA: a standard with no rules compiles, loads and can be applied, but produces NO offsets. ([G:C403BE1C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C403BE1C-FC5E-4631-9479-BC475C86FCC8))
- Collection methods: `AppendBoundingAdjacencyRule`, `AppendBoundingObjectRule`, `AppendBoundingOpeningRule`, `SetSpaceRule`. ([G:01B98544](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-01B98544-D0FB-403D-A1B6-7E2D3EFD0D5B))

Rule base class:
- Class reference: `AecSpaceOffsetBaseRule` with `protected void RegisterType(Type type)`; call `RegisterType(Autodesk.Aec.SpaceOffsetRulesManager.kAllTypes)` to run for all object types. ([G:EE8CCD4E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EE8CCD4E-5DCC-4F87-98D5-0A2879C2BCEB))
- Concept pages write it `AecSpaceOffsetRuleBase.RegisterType()`. ([G:362C6731](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-362C6731-25CB-484A-BE9F-3F98BCE8BAEC), [G:9CC2BA9D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9CC2BA9D-3B35-4964-9070-7A05E0BD1ED0)) Use the class reference spelling (inference).

The four rule types:
- Bounding adjacency, `AecBoundingAdjacencyRule`: `AecSpaceOffsetInfo Apply(ObjectId idSpace, ObjectId idObject, ObjectId idAdjSpace)` ([G:2212AB46](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2212AB46-4A82-4968-8A17-E1419CCA0471)). idAdjSpace is `ObjectId.Null` at exterior walls. The concept page prints a bool return in the abstract signature but its sample returns AecSpaceOffsetInfo ([G:362C6731](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-362C6731-25CB-484A-BE9F-3F98BCE8BAEC)). Sample gross rule: no neighbor = Opposite, else Center.
- Bounding object, `AecBoundingObjectRule`: `bool Apply(ObjectId idSpace, ObjectId idObject)`; return false to drop that object from the offset profile (sample: gross ignores columns). ([G:590E3751](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-590E3751-010E-4EB7-B5CF-EDA06C3544D4), [G:D6B7F4D5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D6B7F4D5-8480-43B3-A24E-1F56B0CBD7E1))
- Bounding opening, `AecBoundingOpeningRule`: `AecSpaceOffsetOpeningInfo Apply(ObjectId idSpace, ObjectId idAdjSpace, ObjectId idObject, ObjectId idOpening)`. Only Openings, Doors, Windows and Door/Window Assemblies; registering other types does nothing. ([G:EBE8DD69](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EBE8DD69-872E-4635-B7DC-B9B8B26CF96F), [G:EF698B56](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EF698B56-0F79-425B-862D-AAA2172EE7F3))
- Space rule, `AecSpaceRule`: registered once per offset type, no RegisterType call; return false to switch that boundary off (sample NullSpace removes the usable boundary). Signature conflict: class reference `bool Apply(ObjectId idSpace, Autodesk.Aec.Modeler.Body body)` ([G:10FA31A6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-10FA31A6-EB8F-48F6-A2FC-689E5B10A332)) vs concept page `bool Apply(ObjectId idSpace)` ([G:9CC2BA9D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9CC2BA9D-3B35-4964-9070-7A05E0BD1ED0)).

Result classes:
- `AecSpaceOffsetInfo(AecSpaceOffsetType[, double])`; props OffsetType, OffsetValue. Types: Adjacent (inside face of the bounding object), Center, Opposite, NoChange. Positive value = away from the space. Statics kNoChange, kOffsetToAdjacent, kOffsetToCenter, kOffsetToOpposite. ([G:6D9CADBB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6D9CADBB-C0B5-4117-8344-55AFFDDE4370))
- `AecSpaceOffsetOpeningInfo(AecSpaceOffsetOpeningType[, double])`. Types: WallAdjacent, WallCenter, WallOpposite, FrameAdjacent, FrameCenter, FrameOpposite, PanelAdjacent, PanelCenter, PanelOpposite, OpeningOwner, OpeningBaseCurve, NotApplicable (no offset; later rules keep trying). Door and window ASSEMBLIES do not support Frame or Panel types; they become OpeningBaseCurve. ([G:27A8D8EA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-27A8D8EA-17F2-497C-A53F-AB641B63AF6A))

Classifications ([G:8F26C374](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8F26C374-C153-4B38-BD5E-D3CE06A4252E), [G:C97B6522](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C97B6522-56F6-4175-A891-33A84AA00D5A), [G:888D33CA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-888D33CA-924C-48C7-A7A9-8DB3CB38EC48), [G:830C7FC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-830C7FC6-2DA3-4660-A2AB-9417FE28A7EA)):
- `AecSpaceOffsetClassification.Init(Database, Assembly, CultureInfo, string resBaseName, string classificationSetName)`, called inside the database-init override so each drawing gets the definitions. Culture: `new CultureInfo(SystemObjects.DynamicLinker.ProductLcid, true)`.
- Names live in a string resource table (example: `Office` = "Office Area"); localize the display names.
- `GetClassificationName(ObjectId)` returns the global, non-localized name to compare in rules.
- The help samples contain defects (stray pointer stars, inverted null test); treat them as illustrations. ([G:EF698B56](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EF698B56-0F79-425B-862D-AAA2172EE7F3), [G:D6B7F4D5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D6B7F4D5-8480-43B3-A24E-1F56B0CBD7E1))

## 11.21 Legacy areas and obsolete command names

Auto-conversion on open ([G:DA589D80](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA589D80-D7D1-4101-B3E9-F49EE5199E9D), [G:81300282](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-81300282-9AE2-406D-B6DE-0757EA726DDD), [G:089D7B86](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-089D7B86-81A7-4EAB-ADFF-6952CBF2D08E), [G:6FEFE68A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6FEFE68A-E15D-47A2-97B5-AE6FAA2E0767)):
- Areas become spaces (Geometry = 2D); area groups become zones; area name definitions become list definitions; area group templates become zone templates; area evaluation becomes space evaluation.
- Legacy space boundary objects do not survive: edges become walls (separation and 0-width solid edges become 0-width walls); spaces they managed become associative to the new walls.
- Areas from Architectural Desktop 2006 or earlier lose subtracted areas and hatches; re-subtract voids. A self-intersecting area becomes a self-intersecting space with a solution tip; grip-edit the base boundary.
- Area group to zone: Net area becomes Base area, Net perimeter becomes Base perimeter. Name lists are NOT re-attached; attach them to the zone style.
- Area group styles become zone styles with both exclusivity options OFF. ([G:95729605](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-95729605-7238-4B56-A942-9FE65F650844))
- Since AutoCAD Architecture 2015 space boundaries are part of the space object. ([G:DA589D80](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA589D80-D7D1-4101-B3E9-F49EE5199E9D))

Obsolete command names (old to current). Old scripts must use the current names. ([G:6F238740](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6F238740-A50B-459B-B81F-4A69E5AF3098), [G:B3D59002](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B3D59002-3108-41C7-A282-A3FB01176C6C), [G:FCA5135A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FCA5135A-47E6-402A-88E6-30BAD22E287E))
- AecAreaAdd > AecSpaceAdd; AecAreaDetect > AecSpaceAutoGenerate; AecArea > AecSpace; AecAreaStyle > AecSpaceStyle; AecAreaStyleEdit > AecSpaceStyleEdit; AecAreaProps > AecSpaceProps; AecAreaAttach > AecSpaceAttach; AecAreaDetach > AecSpaceDetach; AecAreaEvaluation > AecSpaceEvaluation; AecAreaCreatePline > AecSpaceCreatePline; AecAreaRemoveRing > AecSpaceRemoveVoid; AecAreaReverseProfile > AecSpaceReverseProfile; AecAreaReverseRing > AecSpaceReverseRing; AecAreaVertexModify > AecSpaceVertexModify; AecAreaAddSelected > AecSpaceAddSelected; AecNameDef > AecListDefinition; AecSlabConvertArea > AecSlabConvertSpace.
- AecAreaDivide > AecLineworkDivide; AecAreaOpIntersect > AecLineworkCrop; AecAreaOpJoin > AecLineworkMerge; AecAreaOpSubtract > AecLineworkSubtract; AecAreaTrim > AecLineworkTrim.
- AecAreaGroup* > AecZone* (Add, Style, StyleEdit, AddSelected, Attach, CreatePline, Detach, Layout, Props); AecGroupTemplate > AecZoneTemplate; AecGroupCreateFromTemplate > AecZoneCreateFromTemplate. AecSpaceProperties and AecZoneProperties are new with no old twin.
- AecSpaceBoundary > AecWall; AecSpaceBoundaryAdd > AecWallAdd.
- No replacement: AecSpaceConvertArea, AecAreaConvert, AecAreaToolToAutoDetection, AecAreaToolToLinework, and every other AecSpaceBoundary* command (Convert, Split, Props, AddEdges, RemoveEdges, Merge, MergeSpace, GenerateWalls, -AecSpaceBoundaryModify, and the rest).
