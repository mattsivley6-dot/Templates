# 09 - Construction Documents II: Schedules, Property Sets, Display Themes, Callouts, Sections and Elevations

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

This section covers the data side of AutoCAD MEP 2027 construction documents: property set definitions (manual, automatic, formula, field and other property types), property data formats, schedule table styles, schedule tables (quantities, totals, export), schedule tags and MEP part number tags, classifications, list definitions, display themes and fields.
It then covers views generated from the model: section lines, 2D and 3D sections, live sections, elevation lines and elevations, 2D Section/Elevation styles, material boundaries, callouts, model space views and the view/sheet chain in Project Navigator.
For each item: the ribbon path or command, what a script can and cannot reach, and the traps that waste runs.
AutoCAD MEP uses the same AEC schedule, property set, section and elevation objects as AutoCAD Architecture, so most citations are Architecture 2027 help pages; MEP pages are used where MEP adds rules.

Contents
- 9.1 Read this first: what a script can reach
- 9.2 How schedule data flows (order of operations)
- 9.3 Property set definitions and property types
- 9.4 Attaching, editing and cleaning property set data
- 9.5 Formula properties
- 9.6 Property data formats and units
- 9.7 Schedule table styles
- 9.8 Schedule tables: add, place, update, edit, export
- 9.9 Schedule troubleshooting (?, INVALID, missing rows)
- 9.10 Schedule tags, MEP tags, renumbering, part number tags
- 9.11 Classifications and list definitions
- 9.12 Display themes
- 9.13 Fields
- 9.14 Sections: section lines, 2D and 3D sections, live sections
- 9.15 2D Section/Elevation styles, display components, materials
- 9.16 Updating sections and elevations (Refresh, Regenerate, Batch Refresh)
- 9.17 Elevations
- 9.18 Material boundaries, linework edits, hidden line projection
- 9.19 Callouts, model space views, view drawings and sheets
- 9.20 Consolidated limits and gotchas

Conventions
- Citations: G: codes link to the Autodesk 2027 help page with that ID (AutoCAD Architecture, AutoCAD MEP or AutoCAD help); KB: codes link to Autodesk support articles. Support articles are not covered by the CC license above: the KB items here are short summaries in our own words with a link to the article, not copies. A code shown without a link has no known URL.
- [AUTO] = a command line, system variable or API path exists. [GUI] = ribbon, palette, dialog, grip or Style Manager only.
- VERIFIED = tested live on a test PC with AutoCAD MEP 2027.
- (inference) = writer's reasoning, not stated in a source.

## 9.1 Read this first: what a script can reach

The help documents nearly all schedule, property set, display theme, section, elevation and callout work as Style Manager, Properties palette, ribbon, tool palette, grip or dialog steps. No hyphen (command-line) form is documented for schedule table styles, property set definitions, display themes, Generate Section/Elevation, or callouts. The Style Manager command name itself is not given in these pages; they say only Manage tab > Style & Display panel > Style Manager (for example [G:FC65DF0E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FC65DF0E-0EB2-46B2-9F09-567BEC7ADC83)).

Command-line and API surface that IS documented:

Schedules and property sets
- [AUTO] SCHEDULEADD: the add-schedule command. Named on the MEP interference report page ("tag the interferences ... then use the SCHEDULEADD command"); no prompt list given ([G:4BA467DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BA467DF-3395-492A-B6C9-C5CF46BE4C74)). Prompt order from the schedule tool steps: select objects, Enter (or Enter with nothing selected = schedule an external drawing); upper-left corner of the table; Enter to size automatically or pick the lower-right corner ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244), [G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662)). (inference) Which table style a typed SCHEDULEADD uses is not documented; palette tools carry their style in tool properties. Test on a scratch drawing first.
- [AUTO] AECSCHEDULEEXPORT: opens the Export Schedule Table dialog (dialog blocks a script). Works with no schedule table in the drawing ([G:C01D38C1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C01D38C1-E8E5-4760-99CD-E212A2223D6D)).
- [AUTO] PROPERTYSETDEFMERGE: four command-line answers, no dialog ([G:6CDC423D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6CDC423D-E006-4AFC-A42F-E5998F094999)). See 9.4.
- [AUTO] PROPERTYSETCLEAN: one answer, no dialog ([G:91799292](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91799292-41A2-4D13-92A1-2A10BA1EDDCC)). See 9.4.
- [AUTO] System variables AECPSDAUTOATTACH, AECXREFPSDAUTOATTACH ([G:DFAE2FBC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DFAE2FBC-447C-4C1B-8B75-6C6E68BC6BAB), [G:C3269688](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3269688-6A43-4A35-9ED8-9C215CE1C059)), AECPSDVISIBILITY ([G:D787E2D9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D787E2D9-0DDD-4263-A578-9864C1C16221)).
- [AUTO] AECBSCHEDULETAGPARTNUMBERING: command name listed for MEP part number tags; the task itself is a dialog ([G:4A11FFB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4A11FFB0-8C02-4BCF-93B0-70CA2F7BACAA)).
- [AUTO] At a tag tool prompt, `m` then Enter lets you pick many objects ([G:120058F4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-120058F4-8919-4CA4-AC60-7A2DB83930CF), [G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)).

Fields
- [AUTO] FIELDDISPLAY: 1 = grey field background (default), 0 = none ([G:D48BB799](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D48BB799-F5C9-428A-9F47-163FF2D4187D)).

Sections and elevations
- [AUTO] Names only, no syntax in these sources: BLDGSECTIONLINE, VERTICALSECTION, 2DSECTIONEDITLIVE (page metadata), BLDGSECTIONUPDATE, BLDGSECTIONLINEGENERATE, 2DSECTIONRESULTUPDATE (related reference) ([G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB), [G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B)).
- [AUTO] 2DSECTIONRESULTUPDATE opens the Generate Section dialog, so it still needs the dialog ([G:D17AE7B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D17AE7B3-0D04-4A62-A70D-409A3E1F91AA)).
- [AUTO] AEC2DSECTIONRESULTABORTCHANGES: undoes one display component's linework edits and leaves edit-in-place mode ([G:C8448BEF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8448BEF-5CD3-4D83-82FD-052BA99EDEA1)).
- [AUTO] AECENABLESECTIONCLEANUP system variable ([G:1F32A976](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1F32A976-C9F7-4ECF-A631-13D4AC39FC4A)).
- [AUTO] Pure prompt sequences exist for Section Line, Horizontal Section, Elevation Line, Hidden Line Projection and the y/n answers of material boundary edits (see 9.14, 9.17, 9.18).

COM / LISP
- VERIFIED: ProgID `AecX.AecScheduleApplication.8.9` is registered on the test PC (AEC ProgIDs carry version 8.9 on AutoCAD 2027). Entry pattern: `acad.GetInterfaceObject("AecX....8.9")`.
- VERIFIED: `AecScheduleApplication.PropertySetDefs(doc.Database)` returned the 5 property set definitions in the test drawing; `PropertySets(entity)` returned the sets on an object (0 on a newly drawn pipe).
- NOT tested: creating a schedule table by `ModelSpace.AddCustomObject("AecScheduleTable")` (stated in the API help).
- MEP objects (pipe, duct, fitting, MvPart) cannot be created by COM: the API help lists "Create using: N/A" for every Aecb entity, and `vla-AddCustomObject "AecbDbPipe"` was refused in a live test. Draw them with `_-AECBPIPEADD` etc. through SendCommand, then attach data and schedule them.
- 2027 fixed crashes in "LISP functions that read Property Set data" (function names not given) ([G:C901BBAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C901BBAD-C2B9-4299-8B64-35A7C2DF1D4F)).

Dialogs and modes that stall an unattended run
- Edit Property Set Data worksheet: pops up at every tag insertion, ON by default. Turn off at Options > AEC Content tab > clear "Display Edit Property Data dialog box During Tag Insertion" ([G:E2246F50](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E2246F50-4651-4593-B195-31CBE0A33680)). No system variable is given for it.
- Generate Section/Elevation dialog (Generate, Regenerate, 2DSECTIONRESULTUPDATE) ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618), [G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33), [G:D17AE7B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D17AE7B3-0D04-4A62-A70D-409A3E1F91AA)).
- Export Schedule Table dialog and, for XLS, the Format dialog ([G:C01D38C1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C01D38C1-E8E5-4760-99CD-E212A2223D6D)).
- Place Callout dialog, Batch Refresh dialog, Style Manager, Display Manager, Edit Object Display, Data Renumber dialog ([G:DA42867B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA42867B-ED99-45F8-9547-F3155918B662), [G:E8108182](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8108182-5409-4B7E-AE28-541CDE7F8D6A), [G:11679460](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-11679460-4BCB-420A-BB0D-ADC76D1A9D7D)).
- Global update of legacy drawings shows a conversion warning (OK, or Ctrl+Break to cancel) ([G:9938C56F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9938C56F-A23B-4F64-BDCB-10900A6EF7F4)).
- Section results set to Refresh on Open = Yes: you cannot work until every one has refreshed ([G:DC846586](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DC846586-489E-4BCE-ACDE-8862AD8A7AF5)).
- (inference) A modal dialog reached through SendCommand leaves the command waiting; plan every scripted step around the [AUTO] items above.

## 9.2 How schedule data flows (order of operations)

- Schedule tables and tags store NO data. They read property sets attached to objects or to object styles ([G:52325092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52325092-A648-4B6A-9B7B-2343228ECD26), [G:6A74241E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6A74241E-8972-4920-934D-2CB1C7E6EF67), [G:77F8B132](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-77F8B132-6A45-483B-AB92-AD3BD5D47660)).
- Chain: property set definition (PSD) in Style Manager > property set attached to an object, style, definition or classification > schedule table (formatted by a schedule table style) and tags ([G:C7BD8A5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C7BD8A5D-899E-4166-BC53-768C9AD2F2DE), [G:0C27882D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0C27882D-A4BA-4910-9853-951A9EF8937F), [G:A527A2A3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A527A2A3-B973-4D44-A820-25E7B1031A3D)).
- Order ([G:9F9D2456](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F9D2456-7BED-4A80-B1F5-805C55E1A0A5), [G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662), [G:52325092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52325092-A648-4B6A-9B7B-2343228ECD26), [G:46034F58](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-46034F58-0A93-4453-BF14-B7D5000321A3)):
  1. PSDs and property data formats exist in the drawing. Copying a schedule table style into a drawing also copies the PSDs and formats it uses ([G:52325092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52325092-A648-4B6A-9B7B-2343228ECD26)).
  2. Attach property sets to objects or styles, or set AECPSDAUTOATTACH = 1. In MEP, tagging a part attaches the tag's PSDs ([G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)).
  3. Schedule table style: set Applies To FIRST, then add columns ([G:9F9D2456](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F9D2456-7BED-4A80-B1F5-805C55E1A0A5)).
  4. Place the table with a schedule table tool or SCHEDULEADD.
  5. Update the table before every plot ([G:EE2772AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EE2772AE-492F-4059-A88C-5D0111694F4A)).
- MEP rule: "Before creating a schedule, you must add tags to the parts that you want to schedule" ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244)). Property sets can also be added on the Properties palette Extended Data tab ([G:663F867F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-663F867F-4A5F-4193-8D5F-F5AAC2C6E960), [G:1558D688](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1558D688-1909-4C48-B886-83FB05804D92)).
- MEP shipped content: schedule tags for HVAC, piping, equipment, plumbing fixtures, light fixtures and circuits; schedule table styles for equipment, fixtures and lighting; stored in drawings under `\ProgramData\Autodesk\MEP <version>\enu\Styles` ([G:663F867F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-663F867F-4A5F-4193-8D5F-F5AAC2C6E960)).
- Architecture help gives `C:\ProgramData\Autodesk\ACA <version>\enu\Styles\<Imperial or Metric>\Schedule Tables.dwg` for default schedule styles, tags and PSDs ([G:3034E3CE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3034E3CE-1745-4703-B2BE-43986515DC29), [G:120058F4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-120058F4-8919-4CA4-AC60-7A2DB83930CF)).
- On the test PC, `C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\` exists (VERIFIED). The schedule drawing names in that folder are not listed here.
- Palettes: MEP calls it the "Tag and Schedule" tool palette ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244), [G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)); Architecture calls it the Scheduling palette in the Document tool palette set, with more tools in the Documentation Tool Catalog in Content Browser ([G:8DBD8501](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8DBD8501-D675-4424-AF78-E4ABEC2D7996)). Ribbon: Annotate tab > Scheduling panel > Tags and Schedules drop-downs ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244), [G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)).

## 9.3 Property set definitions and property types

Where [GUI]
- Manage tab > Style & Display panel > Style Manager > Documentation Objects > Property Set Definitions ([G:FC65DF0E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FC65DF0E-0EB2-46B2-9F09-567BEC7ADC83)). New: right-click > New, type a name, Enter. Or right-click a definition > Copy, right-click > Paste, right-click the copy > Rename ([G:F180E4F5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F180E4F5-7405-4B60-8802-C33D2BF5AAA9)).
- Tabs: General (Description, Notes, Reference Docs) ([G:9B85E960](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9B85E960-5011-4DC0-975E-C48DDB78DE5E)), Applies To ([G:8B199079](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8B199079-3676-4BE0-92F5-6893C0818ADD)), Definition ([G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)).
- A PSD is a named group of properties (example DoorProps: DoorNumber, DoorWidth, FireRating). Each property has name, description, data type, data format, default value. A property set is the instance made from a PSD once attached ([G:C7BD8A5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C7BD8A5D-899E-4166-BC53-768C9AD2F2DE)).
- MEP ships PSDs based on industry-standard schedules; they load into the drawing when shipped schedule tags or tables are used. PSDs can be merged, edited, deleted and shared between drawings ([G:E8DEA481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8DEA481-1953-418A-9A1C-5603D9180DFC)).

Applies To tab ([G:8B199079](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8B199079-3676-4BE0-92F5-6893C0818ADD))
- Pick Objects (object-based) or Styles and Definitions (style-based); the matching list unlocks.
- All or none of the items selected = the PSD can go on any object or style.
- Right pane: classification definitions for the same objects. Ticked classifications limit the PSD to objects or styles that carry ALL of them.
- MEP: a PSD can be limited by classification, for example one set for air terminals and another for VAV units ([G:E8DEA481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8DEA481-1953-418A-9A1C-5603D9180DFC)).

Object-based vs style-based ([G:C7BD8A5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C7BD8A5D-899E-4166-BC53-768C9AD2F2DE), [G:3034E3CE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3034E3CE-1745-4703-B2BE-43986515DC29), [G:E8DEA481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8DEA481-1953-418A-9A1C-5603D9180DFC))
- Style-based: same value for every object of a style or definition (wall style, MvBlock definition, MvPart style). MEP example: Manufacturer of a damper or MvPart style. Value saves with the style.
- Object-based: value differs per instance. MEP example: RegisterNumber on each damper. Value saves with the object.
- Put most automatic properties in a style-based PSD even when values vary per instance; each object still reports its own value, and it is more efficient than an object-based set on every object ([G:3034E3CE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3034E3CE-1745-4703-B2BE-43986515DC29), [G:8B199079](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8B199079-3676-4BE0-92F5-6893C0818ADD)).
- Switching a PSD from object-based to style-based after a schedule table exists can mismatch data. Fix: remove the property sets and update the table ([G:3034E3CE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3034E3CE-1745-4703-B2BE-43986515DC29)).

Fields on every property row of the Definition tab ([G:DDE22604](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDE22604-9E99-4219-85EA-41B2F4F6E798), [G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015), [G:2981C808](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2981C808-4C2A-40A7-B1E4-DDDF2BC6CC06))
- Name: rename later by double-clicking the value.
- Description: defaults to the name; becomes the schedule column header; does NOT follow a later rename.
- Format: the property data format; becomes the default column format in a schedule table style; Example column previews it.
- Visible: clear it to hide the property on the Extended Data tab. An invisible property cannot get an Order value ([G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)).
- Order: position on the Extended Data tab. Numbered items list before un-numbered ones; default order is alphabetical ([G:193723FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-193723FD-D6F3-485E-A193-053C12B2C6B5)).
- RULE: property names used with schedule tags must have NO spaces ([G:FC65DF0E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FC65DF0E-0EB2-46B2-9F09-567BEC7ADC83), [G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)). If PSD or property names have spaces, tag attributes cannot show the data ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1)).
- RULE: the property data formats you want must already be in the current drawing ([G:2981C808](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2981C808-4C2A-40A7-B1E4-DDDF2BC6CC06)).

Property types (property type list per [G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E))
- Manual ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)): typed value. "Start With" picks an existing property as a base. Type = List links a list definition (9.11). For Real type, the unit setting controls what is ENTERED and STORED; display comes from the data format. Auto Increment - Integer and Auto Increment - Character types exist.
  - Use a neutral default such as "--". A blank default gives blank table cells you cannot select or edit ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015), [G:917F2C59](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-917F2C59-1EB3-4721-A781-87DAC41E38DB)).
  - DANGER: changing the data type when data already exists in the drawing resets that data to the default ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)).
  - Matrix: Text type, values separated by semicolons; each value gets its own matrix column ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)).
  - RefEdit: if a PSD with an Auto Increment type is attached through RefEdit, set the default to the first number to use in the xref or block, or numbers duplicate ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)).
- Automatic ([G:2981C808](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2981C808-4C2A-40A7-B1E4-DDDF2BC6CC06), [G:B17D83FB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B17D83FB-412B-4939-905C-B837C91BC56F)): read from the object or its style, never typed, read-only. More than 1,000 automatic properties exist in 2027.
  - Automatic Property Source worksheet: pick one property per object type the PSD applies to (Width for windows AND Width for window assemblies); a warning appears if you pick different properties for different types. One-type PSD: multi-select several at once. Multi-type PSD: one at a time. Picking an item picks same-named items for all types; Ctrl overrides.
  - Data type and default value of automatic properties cannot be changed ([G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)). Some automatic properties format their own value and cannot use a data format ([G:1AF042B7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1AF042B7-78D4-442B-A5CF-1D70D368C909)). Automatic data can never be edited in a table cell ([G:9F7D8A35](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F7D8A35-17D7-47CC-9BEE-04AEA79E5D0A)).
- Formula ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5)): computed, read-only. See 9.5.
- Field ([G:FC65DF0E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FC65DF0E-0EB2-46B2-9F09-567BEC7ADC83), [G:D5480424](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D5480424-3E35-4627-8C29-1530E00EA2E2)): fields always live in manual properties. Text type, Start with = *DEFAULT*. Empty Default = placeholder, filled per object later. A field set in the Default column reaches every object or style already using the PSD.
- Location ([G:032A468D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-032A468D-0904-4E72-AC4B-B1943DF59EF6)): reads property data of an AEC polygon or space under the object's Data Location grip. The source property must be in a PSD that can apply to AEC polygons or spaces.
- Classification ([G:DDE22604](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DDE22604-9E99-4219-85EA-41B2F4F6E798)): reads classification data. Default description = definition name - PSD name - property name, which makes a long column header; clear "Use classification name for description" to shorten it ([G:016790BA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-016790BA-B88D-4A54-9CB4-B3F5204E5EDF)).
- Material ([G:1F5D6A1D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1F5D6A1D-3F24-4D6F-B1F3-BFC85404194F)): an object's component material name (left pane), or property data of that material (right pane).
- Project ([G:56759D41](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-56759D41-B60C-44D8-891E-F8F49B751B56)): reads Drawing Management project data. Needs a project currently OPEN and the drawing to belong to it. Otherwise Extended Data shows "No Project" and tags and tables keep the values from the last time both were true and the drawing was saved (can be stale). Editing project details marks dependent schedules out of date.
- Anchor ([G:25F2A859](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-25F2A859-A779-41BA-A734-F589CF8D063D)): reads data from the object this object is anchored to (a door showing its wall's fire rating). Read-only.
- Graphic ([G:16445784](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-16445784-6C46-4B80-A4A7-49BF45E85E5B)): shows a block from the current drawing or an image file (BMP, GIF, JPG, PNG, TIF), scaled to fit the cell (cell = row height x column width). A block shows in a schedule ONLY if it exists in the current drawing and is NOT annotative; copy the blocks too when copying a schedule or style. Relative image paths keep a project portable.

Automatic properties worth knowing
- Structural member start and end X, Y, Z can be an automatic property source (new in 2027), so they can be scheduled and exported to Excel or TXT ([G:8537C649](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8537C649-29BD-4AD1-B088-98F41126939E), [G:F180E4F5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F180E4F5-7405-4B60-8802-C33D2BF5AAA9)). The source page's list of exact property names did not come through in the notes ([G:F180E4F5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F180E4F5-7405-4B60-8802-C33D2BF5AAA9)).
- Structural member Length = logical length between grip points; "Length along Baseline" gives the actual length ([G:0D824BD7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0D824BD7-18BB-471D-A350-CB2408F64183)).
- Spaces: "Base Area Minus Interference" schedules area without interference conditions ([G:2DB986C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2DB986C2-049F-472A-9723-4E8912925B01)).
- Architecture-only traps: wall Area-Right/Left Gross/Net double-count a face when a wall style has an air gap with no air-space component ([G:075B18C8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-075B18C8-CF07-4B45-90DC-890CE6B709DA)); wall Length is start-to-end only ([G:6396B1E1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6396B1E1-37FA-4C1E-B08E-7F1CBD76CA91)).
- MEP: part catalogs can be customized to add part properties usable in PSDs ([G:E8DEA481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8DEA481-1953-418A-9A1C-5603D9180DFC)). Values derived from a part (for example connection size) change only by changing the part ([G:1D9664E1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1D9664E1-943C-420F-9370-D259C194158C)).

Locked and version-mismatched definitions
- With both Architecture and MEP toolsets installed, legacy engineering drawings can show LOCKS on PSDs set programmatically. Locked: Applies To selections and PSD names; anything that affects underlying values; property definition names ([G:3034E3CE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3034E3CE-1745-4703-B2BE-43986515DC29)).
- PSDs introduced in the current release show ? when the drawing is opened in an earlier release ([G:16592EDE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-16592EDE-66E9-4F3E-A3DF-5C0DBFD038E9)).

Load-analysis PSDs (pointer only)
- gbXML export needs property sets SpaceEngineeringObjects, ThermalProperties and ZoneEngineeringObjects on spaces and zones, copied with Style Manager from the drawing "gbxml Property Set Definitions (Imperial)" (Content folder, Styles/Imperial) ([G:9DE7186B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DE7186B-E54B-4E83-BA70-FC07004EC05F)). Space styles take SpaceEngineeringStyles ([G:15D184FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15D184FF-CBE0-4029-91A8-0F916F0A41E3)). Spaces and zones are covered in their own section.

## 9.4 Attaching, editing and cleaning property set data

Attach [GUI]
- To objects: double-click the object(s) > Properties palette > Extended Data tab > Add property sets button > pick sets > OK ([G:0C27882D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0C27882D-A4BA-4910-9853-951A9EF8937F), [G:1558D688](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1558D688-1909-4C48-B886-83FB05804D92)). With several object TYPES selected, only PSDs that apply to ALL of them are offered ([G:0C27882D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0C27882D-A4BA-4910-9853-951A9EF8937F)).
- To styles and definitions: Style Manager > the style or definition > General tab > Property Sets button > attach button > pick > OK twice. Objects inherit the style's set; automatic values still come from each object ([G:8901FCBE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8901FCBE-FC48-4EAC-BF4C-78541E007AB9), [G:1558D688](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1558D688-1909-4C48-B886-83FB05804D92)).
- To classifications: Style Manager > Multi-Purpose Objects > Classification Definitions > definition > Classifications tab > select classification(s) > Property Sets > attach > type values > OK ([G:A527A2A3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A527A2A3-B973-4D44-A820-25E7B1031A3D)).
- MEP: a tag attaches its PSDs when it is placed ([G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)). Device tool properties can name property sets and tags so they attach as devices are added ([G:BC28B896](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BC28B896-8D5C-464C-8542-D8892C48DA14), [G:1558D688](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1558D688-1909-4C48-B886-83FB05804D92)).
- Extended Data tab empty = no property sets attached ([G:0971F319](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0971F319-2F49-49DA-81A3-D7A15A21609C)).

Auto-attach [AUTO]
- AECPSDAUTOATTACH: Integer, saved in Registry, initial 0. 0 = the host drawing's PSDs are not attached automatically; 1 = attached to existing and newly created objects ([G:DFAE2FBC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DFAE2FBC-447C-4C1B-8B75-6C6E68BC6BAB)).
- AECXREFPSDAUTOATTACH: Integer, saved in Registry, initial 1. Acts only while an xref is being attached AND AECPSDAUTOATTACH is on. 0 = host PSDs not attached to xref objects; 1 = attached ([G:C3269688](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3269688-6A43-4A35-9ED8-9C215CE1C059)).
- Same switch: Options > AEC Object Settings tab > AEC Property Set Definitions > Automatically Attach > Apply > OK; or enter AECPSDAUTOATTACH on the command line ([G:03030D7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-03030D7C-1008-4A1C-8C72-5ACA70D75AAE)).
- Performance: both on and a large xref attached into a host with many PSDs = slow attach. Set AECXREFPSDAUTOATTACH to 0 ([G:03030D7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-03030D7C-1008-4A1C-8C72-5ACA70D75AAE)).
- (inference) Registry-saved means the value follows the profile, not the drawing: set it at the start of each scripted session. Whether `(setvar)`/`(getvar)` work on these AEC variables is not documented here; test, else send the name and value through SendCommand.

Edit values [GUI]
- Manual object data: Extended Data tab, type the value. Several objects can be selected to enter one value ([G:0971F319](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0971F319-2F49-49DA-81A3-D7A15A21609C)).
- Style-based data: Extended Data tab > "Edit style property set data" button next to Property Sets From Style > Edit Property Set Data worksheet ([G:45E916C7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45E916C7-251F-4ECE-990A-1FF9FDB46055)). A style value applies to ALL objects of that style ([G:D58DDC3F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D58DDC3F-A8E8-4101-8DB0-C3BDA38B51EC)).
- Objects inside an xref: double-click the xref > Reference Edit > "Prompt to select nested objects" > edit on the Extended Data tab > Save Changes ([G:665E50A5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-665E50A5-4140-493C-8C3F-ECAC8F743A17)).
- MEP: select the parts or their tags (both show the same values) > Extended Data tab > Property Sets. Values from the part style or system style: edit button in the property set heading > Edit Property Set Data dialog ([G:1D9664E1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1D9664E1-943C-420F-9370-D259C194158C)). Update the schedule afterward ([G:1558D688](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1558D688-1909-4C48-B886-83FB05804D92)).
- Fields in manual properties: right-click the row > Update Field or Edit Field ([G:CDE6F8C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CDE6F8C9-C6D5-4709-AAE1-63EE166AAD80)). Convert Field to Text breaks the link for good ([G:6AF7B1B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6AF7B1B3-F944-4D15-BB18-691EFF8AD182)).

Browse Property Data tool [GUI] ([G:FA81E478](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA81E478-0399-4703-812D-FE81F88A6089))
- Stock Tool Catalog > Scheduling and Reporting Tools. Lists every property set with the objects and styles it is attached to. Options: Highlight; Hide objects without property set definitions; Format data (clear it to see raw values). Zoom to button.
- Check an object or style to attach the set; clear it to detach.
- DANGER: detaching deletes manually entered values. If done by mistake, click OK, then Undo at once.

Remove
- [GUI] From objects: Extended Data tab > attach/detach button > select the sets to remove > OK ([G:B16293CC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B16293CC-9FA4-4BD1-91FE-1E73A280F1B4)). From a style: Style Manager > General tab > Property Sets > detach ([G:1B507E1A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1B507E1A-7008-465C-A276-BABAE6E48AD2)). Table cells fed by a removed set then show ?.
- [AUTO] PROPERTYSETCLEAN ([G:91799292](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91799292-41A2-4D13-92A1-2A10BA1EDDCC)): type a property set name to remove that set, or press Enter to remove ALL property sets from all objects and styles. Needed because taking an object type off a PSD's Applies To list does NOT detach sets already attached (on purpose, so manual data can be recovered).
- DANGER (MEP): deleting a TAG also removes the PSDs the tag assigned, so ALL property set values for that part are lost ([G:1D9664E1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1D9664E1-943C-420F-9370-D259C194158C)). Remove Part Number also deletes the part number property sets ([G:4A11FFB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4A11FFB0-8C02-4BCF-93B0-70CA2F7BACAA)).

[AUTO] PROPERTYSETDEFMERGE ([G:6CDC423D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6CDC423D-E006-4AFC-A42F-E5998F094999))
- Replaces one PSD with another for all objects or object styles. Command line only, no dialog.
- Answers in order:
  1. Name of the PSD to KEEP, Enter.
  2. Name of the PSD to MERGE, Enter.
  3. Purge the merged PSD? y + Enter = purge; Enter = keep it in the drawing (kept, it is attached to no objects).
  4. Remove property sets that do not apply after the merge? y + Enter = remove; Enter = keep them attached even if they may not apply.
- The page gives these answers, not the exact prompt strings.
- (inference) Test a PSD name that contains spaces before scripting it: at the -AECBPIPEADD routing preference prompt a space ended the answer (VERIFIED).

Visibility and order override ([G:D787E2D9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D787E2D9-0DDD-4263-A578-9864C1C16221))
- Options > AEC Object Settings tab > AEC Property Set Definitions > Property Override: None (Visible and Order columns rule); Visibility (all properties listed, Order still used); Visibility and Order (all properties, alphabetical). Apply, OK. Applies to ALL drawings in the current session.
- [AUTO] System variable AECPSDVISIBILITY sets this override. Its values are not listed in these sources.

Data-loss traps
- Copying an object or style into a drawing that already has a property set of the SAME NAME keeps the target's set; source manual values that the target set lacks are lost ([G:6A74241E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6A74241E-8972-4920-934D-2CB1C7E6EF67)).
- Overwriting a PSD with another can lose manual values and flags the schedule columns that used them as invalid ([G:C7BD8A5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C7BD8A5D-899E-4166-BC53-768C9AD2F2DE)).
- Property data formats, PSDs and schedule table styles cannot be changed through RefEdit: edits look fine, then revert when saved back. Open the xref drawing and edit there ([G:C3C3288D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3C3288D-E40C-4B7A-9DE0-655DA2C1583E), [G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)).
- Renumber Data during RefEdit can leave duplicate PSD names prefixed "$1$" ([G:11679460](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-11679460-4BCB-420A-BB0D-ADC76D1A9D7D)).

Selecting by property data
- 2026 added Quick Select Property Set: filter a selection by object type and property set values ([G:E833B312](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E833B312-0F36-447D-B2A6-1F7F36CEABD2)). MEP: filter a window selection for a schedule with Quick Select in the Properties palette ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244)).

COM
- VERIFIED: ProgID `AecX.AecScheduleApplication.8.9`; `PropertySetDefs(doc.Database)` lists the drawing's PSDs; `PropertySets(entity)` lists the sets on one object (0 on a newly drawn pipe). Entry pattern `acad.GetInterfaceObject("<ProgID>")` (VERIFIED for AecbPipeDatabase; the test notes give it as the pattern for all AecX objects).
- Writing property set values over COM was NOT tested.

## 9.5 Formula properties

Build [GUI] ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5), [G:A891301A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A891301A-03AB-4B03-8CA0-6FFE4D3D38A8))
- Style Manager > Property Set Definitions > PSD > Definition tab > add formula property > Formula Property Definition worksheet: Name; "Use formula for description" (clear it to type your own); Formula pane; Insert Property Definitions list; Insert VBScript code list; Enter Sample Values pane (value and data format drive the Sample Result). OK twice.
- Language: VBScript. Plain expressions (2+3 shows 5), VBScript statements (If...Then...Else, Select Case, For...Next, Function, Dim and the rest) and standard VBScript functions (math, string, date, conversion, Round, Format*, CreateObject and others) ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5)).
- RESULT: if the formula text contains the word RESULT anywhere, it runs as a VBScript FUNCTION and the property value is the last value assigned to RESULT. Without RESULT it is evaluated as a math expression ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5), [G:FDEC75A1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FDEC75A1-1B28-404D-A488-27E88DB02E1E), [G:A891301A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A891301A-03AB-4B03-8CA0-6FFE4D3D38A8)).
- Evaluation order for each referenced property: (1) value read from the object or style; (2) formatted with the data format chosen as the sample value format; (3) that TEXT replaces the bracketed name in the formula string. Then the string is evaluated ([G:FDEC75A1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FDEC75A1-1B28-404D-A488-27E88DB02E1E)).
- (inference) Because the substitution is formatted text, a format that adds unit marks (6'-0") breaks arithmetic. Use a plain decimal format for values you calculate with, or convert with CDbl inside RESULT code as the shipped example does.
- NO unit conversion is done on a formula result ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5), [G:7495AEEE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7495AEEE-0BA4-41AF-8254-5BE6ACAE8CB0)).
- References show in brackets: [Width]; from another PSD with the set name: [DoorObjects:Height]. Referenced properties must apply to the SAME objects as the PSD holding the formula ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5)).
- Blocked: the formula's own property shows [Self]; any property that ends up using the formula's value shows [Circular Reference] ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5)).
- GOTCHA: a property name typed by hand, or pasted from another formula, is plain text, not a live reference. Insert every property from the Insert Property Definitions list (double-click, or right-click > Insert) ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5), [G:7495AEEE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7495AEEE-0BA4-41AF-8254-5BE6ACAE8CB0)).
- Red fields = code still required; gray bracketed fields = optional. A formula with red or gray fields can be saved (with a warning) but will not evaluate correctly ([G:A891301A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A891301A-03AB-4B03-8CA0-6FFE4D3D38A8)).
- A PSD the formula uses but that is not attached to the object or style gives ? in the table ([G:FDEC75A1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FDEC75A1-1B28-404D-A488-27E88DB02E1E)). A referenced property deleted from its PSD gives INVALID ([G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)).

Shipped worked example ([G:A891301A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A891301A-03AB-4B03-8CA0-6FFE4D3D38A8)): space height override. Manual Text property HeightOverride and formula property HeightDisplayed in SpaceObjects; SpaceStyles PSD imported from the schedule table styles drawing. Sample values on the page: HeightOverride = Vaulted, SpaceStyles:Height = 108, format Length - Long. Formula as built by the page's steps (layout reconstructed, inference; bracketed names must be inserted from the list):
```
strHeightOverride = "[HeightOverride]"
If strHeightOverride = "" Then
    RESULT = CDbl([SpaceStyles:Height])
Else
    RESULT = strHeightOverride
End If
```

MEP uses
- Cost from length: length x $2.00 per foot = cost ([G:E8DEA481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8DEA481-1953-418A-9A1C-5603D9180DFC)). Formula column: unit cost x quantity = total cost ([G:7495AEEE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7495AEEE-0BA4-41AF-8254-5BE6ACAE8CB0)).
- (inference, outside these sources, not verified in testing) Microsoft has announced that VBScript is being phased out of Windows as an optional feature. Formula properties depend on VBScript. Before building pipe or equipment schedules on formulas, test one formula in a scratch drawing; if cells come back empty or wrong, check that VBScript is still installed under Windows optional features.

## 9.6 Property data formats and units

What they are ([G:F82CD8A2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F82CD8A2-EA50-41F7-AA2A-2CED4B6E7D69), [G:6DBEA744](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6DBEA744-FBE6-4437-B119-B34B0AD9F578))
- Style-based documentation objects that set how a value shows in schedule tables, tags, the Edit Property Set Data worksheet and the Properties palette. Data come off the object raw; the format makes the shown value.
- Four data types, each with its own settings: Text, True/False, Integers, Real numbers.
- One property can use different formats in the PSD, the table style and the tag (more digits in the set, fewer in the table).
- Formats available = those stored in the CURRENT drawing. Copying a PSD or a schedule table style copies the formats it uses. Changing a format changes every PSD, table and tag that uses it.

Create [GUI] ([G:1AF042B7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1AF042B7-78D4-442B-A5CF-1D70D368C909))
- Style Manager > Documentation Objects > Property Data Formats > right-click > New > name > Enter > Formatting tab:
  - Prefix, Suffix. If you override the unit type in a manual PSD, change the Suffix so units read right.
  - Undefined = text when the property is not attached (typical "?"). Not applicable = text when the property does not apply (typical "NA"). (The page labels both rows "Undefined".)
  - Case: As Is, Upper, Lower, Sentence, Title.
  - Zero Padding: max digits incl. leading zeros (3 turns 6 into 006; 0 = none). ID numbers: store an integer, Prefix D, padding 2 = D01..D99.
  - True / False display strings (Yes / No).
  - Real numbers: Unit Type (length, area, volume...); Units (stored drawing units); Unit Format (Architectural, Scientific, Decimal, Engineering, Fractional; 14.25 shows 1'-2 1/4" in Architectural); Precision; Fraction Format (Horizontal, Diagonal, Not Stacked); Scale (multiplier before display, 2.54 turns inches into cm); Round Off (Nearest, Up, Down; 0.25, 1.0, or 0.0 = none); Zero Suppression (Leading, Trailing, 0 Feet, 0 Inches); decimal and whole-number separators.
  - Set from Dimension Style copies a dim style's formatting; Undefined, Not Applicable, Case, Zero Padding and True/False are NOT copied.
- (inference) The ? in schedule cells is the format's Undefined string. If that text was changed, missing property sets will not show as ?.

Units ([G:D77765F5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D77765F5-D28A-4529-B6BD-2B283F91BB39), [G:34A18E06](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-34A18E06-1B64-48B8-802E-E062B726C03B))
- Automatic properties: units read from the object; default = Units tab of Drawing Setup; a data format overrides and converts for display.
- Manual properties: units set in the PSD control what is STORED; the Extended Data tab displays per the data format. For Real type a format and unit type in the PSD override the format when entering values.
- Example: format Length-Long = inches, Architectural. In the PSD choose Feet; typing 84 on the Extended Data tab then shows 7'-0" ([G:34A18E06](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-34A18E06-1B64-48B8-802E-E062B726C03B)).

## 9.7 Schedule table styles

Where [GUI]
- Style Manager > Documentation Objects > Schedule Table Styles. New = defaults; or Copy then Paste on an existing style; type a name, Enter ([G:D3EF3B68](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D3EF3B68-98CF-4710-990B-3406A6BF4117)).
- Copy between drawings: open both; Style Manager; source drawing > Documentation Objects > Schedule Table Styles > right-click the style > Copy; receiving drawing > right-click Schedule Table Styles > Paste ([G:17321505](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17321505-569E-4FED-AD60-FC6DFC5B4EFF)). Copying a style also copies its PSDs and data formats ([G:52325092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52325092-A648-4B6A-9B7B-2343228ECD26)).
- Make a tool: drag the style from Style Manager onto a tool palette ([G:3061F6F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3061F6F3-2BD8-4536-B333-4ADA745C0007), [G:24178BAC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-24178BAC-FEE7-40B4-8238-504DFC8EACB0)).
- Tabs: General, Applies To, Columns, Layout, Default Format, Sorting; display via right-click > Edit Object Display ([G:A078D3E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A078D3E9-82C0-4380-935D-5B65C1302238)).
- Needs: PSDs for every column and data formats for the column values in the drawing ([G:24178BAC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-24178BAC-FEE7-40B4-8238-504DFC8EACB0)).
- Shipped: door, window, room finish styles ([G:24178BAC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-24178BAC-FEE7-40B4-8238-504DFC8EACB0)); MEP equipment, fixtures, lighting styles ([G:663F867F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-663F867F-4A5F-4193-8D5F-F5AAC2C6E960)).

Applies To tab ([G:4EDBEA36](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4EDBEA36-E61F-4922-8AD8-66F215AFEAA6), [G:1EBA1E4A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EBA1E4A-E16A-4670-9D9C-7E62A2F3AD93))
- Tick the object types the style tracks (several allowed). Set this BEFORE adding columns ([G:9F9D2456](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F9D2456-7BED-4A80-B1F5-805C55E1A0A5)).
- RULE: column properties must come from PSDs that apply to ALL ticked object types.
- Fewer object types = better drawing performance. Select All or Clear All = any object can be included.
- Classification filter: tick classifications under a definition. An object is listed only if it meets ALL ticked criteria ([G:1EBA1E4A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EBA1E4A-E16A-4670-9D9C-7E62A2F3AD93), [G:5C842D9F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5C842D9F-6549-43EB-B820-6284F95427B3)).
- Trap: an object whose style has no classification for that definition is "Unspecified" and is filtered out. To include everything, tick NO classifications ([G:64209805](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64209805-5EA4-4088-9D51-03E474E23798)).
- MEP: MvParts and fittings are classified automatically (an inserted air terminal = MvPart type Air_Terminal); many equipment schedule styles filter by classification ([G:B07A7E8E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B07A7E8E-8224-48C5-8A9D-05F3E3E0673F)). With such a style a mixed selection is fine; only matching parts enter the table ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244)). 2024 fixed tables not updating for classified objects ([G:F209C806](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F209C806-AF58-45C0-8F82-A25E6874812D)).

Columns tab
- Add Column: one property per column; properties used by another column are unavailable; header defaults to the property description; data format defaults to the PSD format. A format chosen here wins and converts stored values ([G:9F9D2456](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F9D2456-7BED-4A80-B1F5-805C55E1A0A5)).
- Column options: Heading; Override Cell Format; Override Header Format; Matrix (max number of columns); Total (total of all values in the column); Hide (display only, data unchanged) ([G:9F9D2456](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F9D2456-7BED-4A80-B1F5-805C55E1A0A5), [G:C3C3288D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3C3288D-E40C-4B7A-9DE0-655DA2C1583E)).
- Edit: select a column > Modify; changes hit every table of that style. Reorder: drag a heading (a group heading moves its group). Delete: select > Delete. To use another property, delete the column and add a new one ([G:C3C3288D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3C3288D-E40C-4B7A-9DE0-655DA2C1583E)).
- Group heading: select ADJACENT columns (click, Ctrl+click) > Add Header > title > OK. Remove: select it > Delete ([G:E509F667](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E509F667-D349-48B5-9A22-00F6BB3FFEF9)).
- Include Quantity Column: objects with the same value in EVERY column collapse into one row with a count; first column by default; required to use quantity in a formula column ([G:25032011](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-25032011-EF21-42C2-9BBA-443DD8A25095)). MEP tip: one row per part means this box is off ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244)).
- Add Formula Column: worksheet with Heading, result data format, Override Cell/Header Format, Total, Hide, Apply Formula to Total, Formula pane with Insert Property Definitions and Insert VBScript code. RESULT and bracket rules as in 9.5. Only properties of the objects or styles the table applies to are offered ([G:7495AEEE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7495AEEE-0BA4-41AF-8254-5BE6ACAE8CB0)).
- Repeat First Column: copies the first column as the LAST column, for wide tables ([G:0FBF31F5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0FBF31F5-5773-453A-AEF3-3974B457473C)).
- Matrix (dot) schedule: headings are properties; a symbol means the object has it. More unique values than Max Columns = shown as a normal column; semicolon-delimited text shows each value separately ([G:24178BAC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-24178BAC-FEE7-40B4-8238-504DFC8EACB0)). Data instead of a symbol: raise Max Columns ([G:84442239](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-84442239-B7B6-4E69-9C0D-03E35F73EE99)).

Layout, Default Format, Sorting
- Layout tab: Table Title; Override Cell Format per title type: Style (existing text style), Alignment, Height, Gap, Rotation. Height and Gap are plotted sizes; Cell Size Height is read-only; overrides show red ([G:E7B96C38](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E7B96C38-DF80-4F8A-813F-8B3018766F30)).
- Default Format tab: Style, Alignment, Height, Gap, Rotation; matrix symbol Check, Dot, Cross or Slash; "Use for True/False"; Fixed Width (0.0 = auto fit) ([G:07786B1C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-07786B1C-2DA4-4205-A3CF-79C3E4B54378)). Most shipped styles already override titles and headers ([G:07786B1C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-07786B1C-2DA4-4205-A3CF-79C3E4B54378)).
- Sorting tab: Add > property (only Columns-tab properties not already used) > Ascending or Descending > Move Up / Move Down > OK ([G:E8978D51](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8978D51-A8E6-4BFC-B522-20468CC798A7)).

Display ([G:A078D3E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A078D3E9-82C0-4380-935D-5B65C1302238), [G:80D99438](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-80D99438-31F5-4860-81B6-ACF5A3BD7DAA))
- Components: outer frame, row and column lines, title, column headers, cell data, Out-of-Date Marker. Data Major Row Lines = every fifth row; Data Minor Row Lines = the rest.
- Style: right-click the style > Edit Object Display > Display Properties tab > representation (bold = current) > Style Override > Layer/Color/Linetype tab. One table: select it > right-click > Edit Object Display.

Style FAQs
- Add Column unavailable: no PSDs apply to the same objects or styles as the table style ([G:7AF2F2AB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7AF2F2AB-6C46-44B4-9C65-F283283DA5BC)).
- Property sets not listed: PSD not in the CURRENT drawing, or not applying to ALL ticked types ([G:51018954](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-51018954-F4EF-4716-BFA1-646338493C78)).
- No classification option: the style must use PSDs that contain classification properties ([G:3F8A52DB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3F8A52DB-A0AF-443F-8F9C-D92D01DC2DDE)).

## 9.8 Schedule tables: add, place, update, edit, export

Add a schedule
- [GUI] MEP: Tag and Schedule palette > schedule tool for the part type, or Annotate tab > Scheduling panel > Schedules drop-down ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244)). Architecture: Scheduling palette, or Annotate tab > Scheduling panel ([G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662)).
- [AUTO] Prompt order ([G:A253002D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A253002D-4816-40F5-85A3-161A9FD04244), [G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662)): select objects (window or crossing; wrong object types are filtered out), Enter; OR press Enter with nothing selected to schedule an external drawing; pick the upper-left corner; Enter = size automatically (scales to the current drawing scale), or pick the lower-right corner.
- [AUTO] SCHEDULEADD is the command name ([G:4BA467DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BA467DF-3395-492A-B6C9-C5CF46BE4C74)). See 9.1 for the table-style caveat.
- Default tools need no style edits when the property sets are already attached ([G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662)).
- On a sheet: a schedule can be placed only after a viewport is added: View tab > Viewports panel > Named, pick the viewport window ([G:BE4BC78E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE4BC78E-2642-4417-BB20-D8A7A1BA44C7)).
- Schedules are NOT annotative: a schedule keeps the annotation scale current when it was inserted ([G:32BCA5AF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32BCA5AF-AA85-4CAE-B3AB-7429BB0E5DEA)).
- Interference report: tag the interference mass elements, then SCHEDULEADD; a default interference schedule ships ([G:4BA467DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BA467DF-3395-492A-B6C9-C5CF46BE4C74)).
- Electrical panel schedules: Circuit Manager > right-click a panel > Insert Panel Schedule, or the Panel Schedule tool ([G:60C27ECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-60C27ECD-5DB4-497E-B64E-48971498D24A)).

Table properties (select or double-click the table > Properties palette) [GUI]
- Basic > General: Description, Layer, Style (swaps the table style), Title, Scale, Update automatically (Yes = refresh when drawing data change; slows large drawings) ([G:3E451D9B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3E451D9B-9D08-4BB5-BA68-CB6F339A82FA)).
- Basic > Selection: Add new objects automatically; Scan xrefs; Scan block references; layer wildcard filter, comma-separated ([G:5E6C9FC3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5E6C9FC3-35E0-428F-ADD0-9C03B06429D0)).
- Advanced > External Source: Schedule external drawing = Yes shows External drawing (drop-down of the current project's View directory drawings; with no active project, drawings in the last browsed directory; Browse) ([G:5BFDFCB0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5BFDFCB0-884C-45B6-89F1-0A6E43186880)).
- Advanced > Table Breaks and Documentation ([G:A417BE90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A417BE90-9C43-4B08-BD72-B2C33237A78D), [G:AE34636C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AE34636C-ABC5-46AC-BC65-4E2943E3324C)).
- The schedule table TOOL has the same General and Selection properties plus Layer Key, Layer Overrides, Style and Style Location (external DWG holding the style) ([G:3061F6F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3061F6F3-2BD8-4536-B333-4ADA745C0007)).

Xrefs, blocks and external drawings
- To schedule objects inside an xref or block, select the xref or block itself, set Scan xrefs / Scan block references = Yes, and make the layer filter name BOTH the layer of the xref/block reference AND the layer of the object inside it. Single objects inside cannot be picked ([G:364D2DC7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-364D2DC7-6EE4-4BD1-98E1-486BFB210B5B), [G:5E6C9FC3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5E6C9FC3-35E0-428F-ADD0-9C03B06429D0), [G:3061F6F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3061F6F3-2BD8-4536-B333-4ADA745C0007)).
- Objects cannot be added through RefEdit: rows appear, then vanish when changes are saved back (you picked temporary copies) ([G:364D2DC7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-364D2DC7-6EE4-4BD1-98E1-486BFB210B5B)).
- Tag objects in an xref attached as Reference type, not Overlay, to avoid broken links ([G:AD45BCC3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD45BCC3-6FFC-4845-828C-9072B9A93AAE)).
- External source: the table schedules another drawing as if it were an xref, without generating its graphics. Whole project: one container drawing that xrefs every project drawing, used as the external drawing ([G:5BFDFCB0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5BFDFCB0-884C-45B6-89F1-0A6E43186880)).
- MEP recommended: schedule in its own drawing (its own view drawing in Project Navigator) linked to the construct ([G:0E4A026B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E4A026B-E634-4D4A-91A8-371D3CD861E2)). Steps: schedule tool > Enter (external) > upper-left corner, Enter > select the table > Properties palette Design tab > Advanced External Source > Schedule External Drawing = Yes > External Drawing = Browse > pick the drawing > Schedule Table tab > Modify panel > Update ([G:0E4A026B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E4A026B-E634-4D4A-91A8-371D3CD861E2)).
- Limits: Add All Property Sets does not work on an external-drawing table ([G:64C01D54](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64C01D54-0851-4975-946C-5B311AD8827B)); its cells cannot be edited ([G:9F7D8A35](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F7D8A35-17D7-47CC-9BEE-04AEA79E5D0A)).

Change the object set [GUI]
- Schedule Table tab > Scheduled Objects panel: Add (no duplicates) ([G:364D2DC7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-364D2DC7-6EE4-4BD1-98E1-486BFB210B5B)); Remove ([G:E8751674](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8751674-0DC3-47DC-B502-9C813667A6C3)); Reselect (the table then holds ONLY the new set) ([G:B0A0C960](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B0A0C960-3EC6-435C-9116-254A31B0F4ED)); Show (pick the border = highlight all objects; pick a cell = that row's object) ([G:78E620FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-78E620FD-35F3-4C04-AB6C-AA6DFA556E9C)). MEP: right-click the table > Selection Add ([G:7E4D1FE0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E4D1FE0-8558-4A7B-85CC-A9DB239AFB63)). Selecting a row highlights its object ([G:106183CE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-106183CE-DF1F-45C9-858A-CD624528D611)).

Update [GUI]
- Schedule Table tab > Modify panel > Update. Always update before plotting ([G:EE2772AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EE2772AE-492F-4059-A88C-5D0111694F4A)).
- Three separate staleness rules: new objects are listed only if Add new objects automatically = Yes ([G:FFAA1897](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FFAA1897-7AAA-4BEC-8B57-D0D2C1E9F5B6)); edits flow in only if Update automatically = Yes ([G:EC783387](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EC783387-E626-4219-96E5-0C6068A7B5D2)); Update never renumbers objects ([G:7754D6B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7754D6B9-1AE7-4745-A732-49E6525E8535)).
- Some changes (for example reference editing) show only after the drawing is closed and reopened; reopen before plotting to be safe ([G:EE2772AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EE2772AE-492F-4059-A88C-5D0111694F4A)).
- Out-of-date marker: a line (diagonal slash) through the table until it is updated ([G:D8728D90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8728D90-90D2-4E6D-A021-411C6E02F5AA), [G:24178BAC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-24178BAC-FEE7-40B4-8238-504DFC8EACB0)). CONFLICT on the default: [G:D8728D90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8728D90-90D2-4E6D-A021-411C6E02F5AA) says it "appears by default"; [G:A078D3E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A078D3E9-82C0-4380-935D-5B65C1302238) says the component "is turned off by default". Check the drawing. Both say it can slow large drawings. Toggle: select table > right-click > Edit Object Display > General representation > Out-of-Date Marker > Visible ([G:D8728D90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8728D90-90D2-4E6D-A021-411C6E02F5AA)).
- MEP pages also differ: [G:73091186](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73091186-11D6-4773-B1F8-F22C16AAAD73) says schedule data follow part changes; [G:7E4D1FE0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E4D1FE0-8558-4A7B-85CC-A9DB239AFB63) says the table shows a line until Update unless Update Automatically = Yes. (inference) Treat every table as needing Update.

Edit cells [GUI] ([G:9F7D8A35](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F7D8A35-17D7-47CC-9BEE-04AEA79E5D0A))
- Schedule Table tab > Modify panel > Edit Table Cell. Hover = source object highlights; tooltip gives data type, whether editable, data problems. Ctrl+click = zoom to the source object(s).
- Select a cell > Edit Referenced Property Set Data worksheet. Select the table border = edit every instance of a property.
- Only MANUAL data can be edited; automatic data cannot. A cell with an xref icon edits the xref drawing (fails if another user has it locked). A style-based cell changes every object of that style.

Table breaks ([G:A417BE90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A417BE90-9C43-4B08-BD72-B2C33237A78D))
- Advanced > Table Breaks: Direction (Right or Down), Repeat title, Repeat headers, Manual heights, Maximum height, Spacing. Grips: Maximum Page Height (Manual heights = No); Insert Page and Page Height (Manual heights = Yes).

Export
- [GUI] Select the table > Schedule Table tab > Modify panel > Export > Export Schedule Table dialog: Save As type (XLS, CSV, tab-delimited TXT), file name > OK ([G:FDD1C9B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FDD1C9B9-4D3D-48CE-A14A-B900F63E32E7), [G:F011C387](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F011C387-98CC-44E2-92F4-1329754BD260)). XLS needs Microsoft Excel installed and adds a Format dialog: Use Unformatted Decimal Value, or Convert to Formatted Text (6'-0" in Excel), per column or Apply to All Columns. An existing file gives an overwrite, rename or cancel warning.
- [AUTO] AECSCHEDULEEXPORT ([G:C01D38C1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C01D38C1-E8E5-4760-99CD-E212A2223D6D)): opens the same dialog and works with NO table in the drawing. Steps: Save As type; file name or Browse; clear Use Existing Table; pick the table style (its columns decide what is exported); layer wildcard; scan xrefs / block references; OK; select objects; Enter; XLS Format dialog. Dialog-driven: blocks a headless run.
- (inference) For a dialog-free takeoff, read data over COM and write the CSV from Python. VERIFIED readable pipe properties: SizeName, NominalSize, CrossSectionSize, Length, CutLength, SystemName, SystemAbbreviation, SystemFamily, PartDescription, Elevation, TopElevation, BottomElevation, InsulationThickness, Layer, Handle; fittings: PartDescription, SizeName, SystemName.

Convert to Table ([G:8DBD8501](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8DBD8501-D675-4424-AF78-E4ABEC2D7996), [G:52325092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52325092-A648-4B6A-9B7B-2343228ECD26))
- Schedule table contextual tab > Convert to Table makes a plain AutoCAD table copy. Update and Add All Property Sets no longer work on it. A character such as = in a heading can misbehave; put an apostrophe (') in front first.

## 9.9 Schedule troubleshooting

- ? in cells: property set not attached to the object or its style, or removed. Fix: Schedule Table tab > Modify panel > Add All Property Sets, or Edit Table Cell per cell ([G:269E4649](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-269E4649-ABFE-40FC-869B-E88137ADA4E5), [G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662), [G:64C01D54](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64C01D54-0851-4975-946C-5B311AD8827B)).
- Empty cell or dash: set attached, no data ([G:29CD719E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-29CD719E-37AA-4086-BADA-15B1081D2662)). Empty cell you cannot select: manual property with no default; enter data on the object or style ([G:917F2C59](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-917F2C59-1EB3-4721-A781-87DAC41E38DB)).
- INVALID in a whole column: the property was deleted from its PSD; remove the column or restore the property ([G:995DFFAB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-995DFFAB-4E35-49F5-8B47-91FF25EFC03A), [G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)).
- New object missing: Add new objects automatically is off, or a classification filter excludes it ([G:FFAA1897](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FFAA1897-7AAA-4BEC-8B57-D0D2C1E9F5B6), [G:64209805](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64209805-5EA4-4088-9D51-03E474E23798)).
- Quantity column does not group: some cell differs (numbers, remarks) ([G:C636731B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C636731B-8264-43A6-A162-0198A2585253)).
- Numbers out of order: renumber (9.10); Update does not ([G:7754D6B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7754D6B9-1AE7-4745-A732-49E6525E8535)).
- ? on new PSDs in an older release: release mismatch ([G:16592EDE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-16592EDE-66E9-4F3E-A3DF-5C0DBFD038E9)).

## 9.10 Schedule tags, MEP tags, renumbering, part number tags

What a tag is
- A multi-view block with attributes. It shows property set data of the object it is anchored to; the data live on the object, not in the tag ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1), [G:77F8B132](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-77F8B132-6A45-483B-AB92-AD3BD5D47660)).
- MEP: the main job of a tag is to attach property set data to a part so equipment schedules for that part type fill automatically; its second job is annotation (a diffuser tag showing airflow) ([G:0046C357](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0046C357-5B5E-436A-B951-82D60EE3277D), [G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)).
- An attribute reads data only if its attribute tag text holds BOTH the PSD name and the property name, colon-separated: `DoorStyles:DoorHeight` ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1)), `DoorProps:FireRating` ([G:185BF421](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-185BF421-746C-4E2F-945A-B9C03028A15A)). Attribute tags cannot contain names with spaces, so keep PSD and property names space-free ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1)).
- Tags are stored as multi-view block definitions under Multi-Purpose Objects in Style Manager ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1)).

Place tags
- [GUI] Tag tool on the palette (MEP: Tag and Schedule palette), or Annotate tab > Scheduling panel > Tags drop-down; more in the Documentation Tool Catalog in Content Browser ([G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0), [G:120058F4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-120058F4-8919-4CA4-AC60-7A2DB83930CF)).
- [AUTO] Prompts (MEP, [G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)): select the object; Enter = center the tag on the part, or click a location; Edit Property Set Data dialog (automatic fields gray, read-only) > OK; Enter ends.
- [AUTO] Multi-tag: after the first tag type `m`, Enter, select more parts of the SAME part type, Enter. Each gets the same relative location and the same property set values ([G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0), [G:120058F4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-120058F4-8919-4CA4-AC60-7A2DB83930CF)).
- Numbering order: with the multiple option pick ONE object at a time; with a crossing window the auto-increment order is undefined ([G:AD45BCC3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD45BCC3-6FFC-4845-828C-9072B9A93AAE)).
- Placement: the first tag's position relative to its object sets the rest. Walls: midpoint. Spaces: center of geometric extents. Other objects: leader end at the geometric center; no leader = same distance and direction from the object center ([G:0D4A23C4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0D4A23C4-5807-4A25-B4D0-3539779312C6)).
- An object with no property set yet: the tag can attach one from the current drawing or from Schedule Tables.dwg (path in 9.2) ([G:120058F4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-120058F4-8919-4CA4-AC60-7A2DB83930CF)).
- STALL: the Edit Property Set Data worksheet opens at every tag insertion (ON by default). Before scripted tagging: Options > AEC Content tab > clear "Display Edit Property Data dialog box During Tag Insertion" ([G:E2246F50](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E2246F50-4651-4593-B195-31CBE0A33680)).
- MEP: tag data tied to a system style or object style may be inactive; edit it afterward on the Properties palette. Electrical devices can be tagged automatically as they are added ([G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)).
- Project-based tags (tagging in project view drawings) know the object's project level; standard tags do not ([G:4BA28253](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4BA28253-AF46-4462-A730-B8AED4657B3F), [G:3B19057B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B19057B-1918-42AE-8744-BDE84C8376DB)).

Create a tag [GUI] ([G:185BF421](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-185BF421-746C-4E2F-945A-B9C03028A15A))
- Draw the symbol and placeholder text (or explode an existing tag down to plain objects) > Annotate tab > Scheduling panel > Create Tag > select the objects > Enter > Define Schedule Tag worksheet: tag name; per attribute Type = Property (pick Property Set and Property Definition) or Type = Text > insertion point.

Tag tools [GUI] ([G:068A5372](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-068A5372-826D-4F33-A37D-64ACFFA98A38))
- Drag a tag from the drawing onto a palette, or copy/paste a tool; right-click > Properties.
- General: Type = Tag, or "Property set data" (attaches the property data with NO tag drawn; data still appear in schedules and the Properties palette). Property Data (the PSDs); Property def location (external DWG).
- Tag group: Layer key, Layer key overrides, Tag name, Tag location (source file), Constrain to object (Yes = tag moves with its object), Rotate to object. Leader type: None, Straight, Spline. Attribute text style: As defined by content, or Target drawing text style. Attribute text angle: As inserted, Force horizontal, Right reading.
- (inference) A "Property set data" tool attaches property sets to many objects without drawing tags.

Anchors
- Tags are anchored by default (tool setting). A tag copied to another object stays anchored to the ORIGINAL. Re-anchor: select tag > Tag tab > Anchor panel > Set > pick object ([G:EAD45174](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EAD45174-FDBF-439D-B97E-D2375FCFAB41), [G:B72E2C39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B72E2C39-9CD3-433B-8B6F-A1E7D1F490FA)). Release: Tag tab > Anchor panel > Release ([G:6D9DB253](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6D9DB253-7DD2-49E7-8BC5-EF157E82E283)).
- Show links: Manage tab > Display Manager > Sets > current display set > Display Representation Control tab > set Anchor Tag To Entity and Anchor Extended Tag to Entity to General; links draw as arcs from tag to object ([G:05DFD4C8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-05DFD4C8-05D8-4E28-B605-97EC5DC00266)). Per [G:B72E2C39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B72E2C39-9CD3-433B-8B6F-A1E7D1F490FA), Anchor Tag To Entity shows tags NOT constrained and Anchor Extended Tag to Entity shows constrained ones.
- MEP: a tag follows its part but can be moved alone without releasing it ([G:B842CB52](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B842CB52-C0E4-404A-AC2C-41361A392DE0)).

Renumber
- Renumber Data tool (Stock Tool Catalog > Scheduling and Reporting Tools) > Data Renumber dialog: property set holding the number (DoorObjects for doors), Start number, Increment (start 1, increment 3 = 1, 4, 7, 10), Attach New Property Set; OK; pick objects or tags in order; Enter ([G:11679460](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-11679460-4BCB-420A-BB0D-ADC76D1A9D7D)).
- ONLY "Auto Increment - Integer" properties can be renumbered ([G:11679460](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-11679460-4BCB-420A-BB0D-ADC76D1A9D7D)). MEP: change start number or increment of an auto-increment set (register numbers) on the Extended Data tab ([G:1558D688](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1558D688-1909-4C48-B886-83FB05804D92)).
- Tags follow renumbering because they read the property ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1)).

MEP part number tags ([G:4A11FFB0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4A11FFB0-8C02-4BCF-93B0-70CA2F7BACAA), [G:CCD406DD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CCD406DD-53C5-428D-A6F1-2AA3AF3C303D))
- [AUTO] Command name AECBSCHEDULETAGPARTNUMBERING; the task itself is a dialog [GUI].
- Annotate tab > Scheduling panel > Tags drop-down > Text Part Numbering Tag > Rectangular, Oval or Text Part Number tool > Select System button > tag individual objects or connected objects > operation: Add Part Number (new set), Update Part Numbers, Remove Part Number (deletes the set INCLUDING its property sets) > starting value, optional prefix and suffix > Include run number (run designator for separate but connected runs) > Use the same part number for identical parts > OK starts tag insertion.
- Valid sequences: 1,2,3...; A,B,C...Z,AA,AB...; a,b,c...z,aa,ab...; A1,A2...A9,B0,B1...; 1A,1B...1Z,2A...
- Any MEP object, MvParts included. The property set can be configured to a pipe or duct specification; itemized duct or pipe schedules can go to fabrication or ordering vendors. The Tags and Schedules palette offers these schedule tools only for duct and piping systems ([G:CCD406DD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CCD406DD-53C5-428D-A6F1-2AA3AF3C303D)).

Labels that show property data
- Label curve style option "Use Property Set": pick a PSD and the property to show. Objects without property sets need them added first (Properties palette or tagging) ([G:CCF59C17](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CCF59C17-9C8B-419C-A175-3D7F55B708DA)).

## 9.11 Classifications and list definitions

Classification definitions ([G:708C0F2B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-708C0F2B-56F0-40C7-BBC9-6E3E208AC345), [G:87EC407C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-87EC407C-051A-42A0-9AAE-E3DBE4A4C618), [G:CB474F39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CB474F39-9065-4073-8D10-1A4AB20B48A9), [G:9D16AA40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9D16AA40-A4F7-414E-AEB7-3FFE9ACF84BF))
- A named hierarchy of classifications for object types (Existing / Demo / New; vendor; project phase). Used to filter schedules, show as a column, carry property sets, and show or hide objects per display set.
- Create: Style Manager > Multi-Purpose Objects > Classification Definitions > right-click > New (or Copy/Paste) > name > Enter ([G:889F9140](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-889F9140-A76A-47BF-A55A-D455019C48E6)). Set object types on the Applies To tab FIRST or the classifications are unavailable ([G:CB474F39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CB474F39-9065-4073-8D10-1A4AB20B48A9), [G:9D16AA40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9D16AA40-A4F7-414E-AEB7-3FFE9ACF84BF)). Classifications tab: Add, name under Item, Description; drag to nest.
- Apply: on the object style's Classifications tab (all objects of that style), or per object on the Extended Data tab > Select Classification worksheet; a warning shows if the change hides the object ([G:87EC407C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-87EC407C-051A-42A0-9AAE-E3DBE4A4C618), [G:1EEF6038](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EEF6038-EA5C-4315-81AD-F3B645C63631)).
- Remove a classification only when no object type uses it ([G:428374B8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-428374B8-EBDD-4C7B-9E0B-FF5218314E95)). Purge a definition only when no display set filters by it: in Display Manager check all its classifications on every display set's Display Options tab ([G:CB474F39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CB474F39-9065-4073-8D10-1A4AB20B48A9)).
- Empty Classifications tab on a style = no definition applies to that object type ([G:49381E99](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-49381E99-D644-4E88-A4E9-DD4F1D8659EA)).
- MEP: classification styles are stored in the object style; MvParts and fittings classify automatically ([G:B07A7E8E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B07A7E8E-8224-48C5-8A9D-05F3E3E0673F)).

List definitions ([G:B02424E1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B02424E1-7CCE-4E67-87BE-A69D5DD21C93), [G:233049F3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-233049F3-3138-450E-A07F-6AC0A776C0BB), [G:3D2FD84A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3D2FD84A-4BAC-4208-B764-A30DD63C8591))
- Value lists for manual properties (manufacturers, paint colors); they stop typos.
- Create: Style Manager > Multi-Purpose Objects > List Definitions > New > Applies To tab: Manual Property Definition (or space and zone names) > Items tab: Add (Name, Description). "Allow individual property values to vary from this list" lets users type values not in the list.
- Use: manual property Type = List ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)); pick items on the Extended Data tab ([G:3D2FD84A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3D2FD84A-4BAC-4208-B764-A30DD63C8591)).

## 9.12 Display themes

What they do ([G:BCF4D44E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BCF4D44E-72C2-4B91-91CE-4DE51D25DC1C), [G:E2F7AFE0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E2F7AFE0-C3EF-4DBD-A9AA-2A4DD0560B95), [G:8AB54DF7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8AB54DF7-E5B9-48ED-B3BE-00E12BCC0037))
- Show non-graphic data with colors, fills and hatches. Examples: all 2-hour fire-rated walls get a red fill; rooms whose Function = "storage" get solid yellow.
- The display theme LEGEND activates the theme in the drawing and explains it. Inserting a legend overrides the objects' current display properties.
- Data come from property sets on objects or styles. The property sets named in the theme style must be attached BEFORE the theme is applied.
- Display theme styles live in Style Manager under Documentation Objects. A drawing must contain one to add a legend. Copying a style copies the PSDs and data formats it uses.
- Style anatomy: one or more theme SETTINGS (a color fill, hatch or linetype), each with one or more theme RULES that pick the objects; plus legend format and legend display.
- Uses named: changes not in the contract, project staging, objects that do or do not meet standards. Theme style versions can be synchronized with project standards ([G:8AB54DF7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8AB54DF7-E5B9-48ED-B3BE-00E12BCC0037)).

Create a display theme style [GUI] ([G:E4CF071A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E4CF071A-69F3-4B6B-8BAD-8200A571DFDF))
- Style Manager > Documentation Objects > Display Theme Styles > right-click > New > name, Enter > Description. PSDs used by the rules must already exist.
- Design Rules tab: add a theme setting (unnamed, index 1). Per setting: Name; light bulb (yellow = setting shows in the legend); Color (button reads BYBLOCK); Hatch pattern (button reads SOLID; Hatch Pattern worksheet > Type); Scale/Spacing; Angle; global vs object orientation; X Offset; Y Offset; Linetype, Lineweight, Plot Style (ByBlock); Lt Scale.
- Theme Rules for selected Theme Settings: add rule (index 1.1 = rule 1 of setting 1; many rules per setting). Rule = PSD (drop-down of PSDs in the drawing) + property + condition + value + operator; choices depend on earlier picks.
- Legend Format tab: Title; key symbol round or square; text style; text height; gap between words. Legend Display Properties tab: representation + Style Override > Layer/Color/Linetype.

Tools and legends [GUI] ([G:EBE110C7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EBE110C7-82DD-4890-ACBB-3407FF3C83A8), [G:E53CCA0C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E53CCA0C-FDED-40C6-9D3F-2065F72236A9))
- Tool: drag a display theme style from Style Manager onto a palette, or copy/paste a tool. Properties: name, Description, Layer key, Layer overrides, Style, Style location (external DWG), Scale (legend scale).
- Three sample tools are on the default Scheduling palette; more in the Documentation Tool Catalog and Stock Tool Catalog > Scheduling and Reporting Tools.
- Insert: pick the tool, click the upper-left insertion point, then the lower-right corner or Enter to scale to the current drawing scale.
- Legend in paper space = applies to that viewport. Legend in model space = all model space viewports. New objects join the legend if they meet the rules.

One active theme ([G:B54AB329](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B54AB329-FA32-4FFE-AB08-0D1A0DB8F9F7), [G:3992CC97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3992CC97-6634-4F37-9015-AAC87C181B42))
- Only ONE display theme is active at a time. Adding a theme disables the others; a disabled legend shows a marker through it and still plots.
- Activate: select the disabled legend > Display Theme tab > Modify panel > Apply Display Theme. Disable: select the active legend > Display Theme tab > Modify panel > Disable Display Theme.
- Xrefs: attach or overlay imports the xref's themes by default; if the host has themes, the host's active theme overrides the xref's.
- No command-line form for display themes is documented in these sources.

## 9.13 Fields

Where fields live ([G:4EFD2CC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4EFD2CC6-C559-4CC3-8E1B-98BA0051A1A2), [G:76C68393](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-76C68393-2FC7-4203-862B-14C849E6BD4D), [G:A9EB91E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A9EB91E9-E570-474C-A957-B6B6D08E4FB4), [G:3AA08FF7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3AA08FF7-511B-4A62-AA97-BEA3564F63F3))
- Text, MText, table cells, attributes and attribute definitions, manual properties in PSDs, object properties (Extended Data), object styles, project details. A field inserted directly in the drawing becomes an MText object.
- In PSDs, fields always sit in manual properties ([G:D5480424](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D5480424-3E35-4627-8C29-1530E00EA2E2)). Callout symbols use sheet set fields because property set data work only in MV blocks ([G:7B46657F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7B46657F-63CA-44D4-A04A-1E75D76247C3)).

Insert [GUI]
- Directly: Annotate tab > Text panel > Field > category and field > OK. [AUTO] Placement prompt: pick the point; or h, Enter, height, Enter, then the point; or j, Enter, justification code, Enter, then the point ([G:77EA3BF4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-77EA3BF4-84C4-4716-998A-2AF63C3E6A71)).
- Text: select > right-click > Text Edit > right-click at the spot > Insert Field. MText: click in the text > Text Editor tab > Insert panel > Field. Table cell: double-click > right-click > Insert Field (or Table Cell tab > Insert panel > Field). Attribute definition: Insert tab > Attributes panel > Define Attributes > insert-field button by Value ([G:D4F43D90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D4F43D90-123F-4BE2-9503-4BFECB78F0DA), [G:5994E4B5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5994E4B5-66BD-41AC-861B-E483AFBA3BA0), [G:AF59E11B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AF59E11B-6394-4633-A89E-461477DF8F22), [G:15DFE005](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-15DFE005-4A05-488B-A980-1A4126FDDE25)).
- PSD default field: Style Manager > PSD > Definition tab > add manual property (example Keynote) > Start With = DEFAULT > Type = Text > right-click the Default field > Insert Field ([G:D5480424](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D5480424-3E35-4627-8C29-1530E00EA2E2)). Per-object placeholder: leave Default EMPTY; on the object, Extended Data tab > add the property set > right-click the empty property > Insert Field ([G:DB46310F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DB46310F-94BB-4CB1-A529-2438E1639E8D)).
- Object style: put the field in a PSD, then attach that PSD to the style (General tab > Property Sets) ([G:2DFB55BA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2DFB55BA-5042-410B-954E-2AD210FCA4C2)).

AEC field categories ([G:30A18F28](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-30A18F28-3AFA-4A8C-A5EF-587C4EEC7D56), [G:530181AF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-530181AF-E49A-4712-A9D1-35AB7B76BCA4), [G:9CA03795](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9CA03795-0964-460C-903F-C83B342B3C30), [G:9C466FAE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9C466FAE-1A3B-4884-826C-62B9A1C98B9D), [G:E76A8729](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E76A8729-7A84-4B22-A0A9-2BB3978BF035), [G:79BE068E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-79BE068E-7B22-4C77-91C6-16C77E3BCE8A), [G:76D44ED7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-76D44ED7-1CD7-424D-8EB7-43DF7BFA3AA6))
- AEC Project: Project Name, Project Number, Project Description, Project Location, Project Details (pick the detail under Project Information), Number of Levels, Number of Divisions. Text formats Uppercase, Lowercase, First Capital, Title case.
- SheetSet: Current Sheet ... fields, SheetSet (any sheet; can be a hyperlink), SheetSetPlaceholder, CurrentSheetCustom and CurrentSheetSetCustom (pick the custom property). Works with AEC project sheet sets and plain AutoCAD sheet sets.
- Sheet Set Placeholder types: Sheet Number and Title, Sheet Title, Sheet Number, Sheet Description, Sheet custom, (Model Space) View Number and Title, View Title, View Number, Viewport Scale. They resolve when the callout's model space view is placed on a sheet.
- AEC Keynotes: Reference Key only, Reference Note only, Reference Key and Note, Sheet Key only, Sheet Note only, Sheet Key and Note; Select Keynote button; Insert as placeholder.
- AEC Database: DatabaseField.

Database fields ([G:E8DDFA3E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8DDFA3E-FEC0-46D0-BD32-1B67E851E5A8), [G:F4CCFDE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F4CCFDE3-ABEC-4030-905D-9CA8DC81CDA1), [G:8ACCAB6B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8ACCAB6B-A5F2-4518-9576-48BE9EB2B945), [G:C7BE41AF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C7BE41AF-618A-4057-8667-CD83D6F1B50B))
- One formatted cell from one field of a table or query. Sources: Access MDB, Excel XLS, TXT/CSV, through Microsoft Jet 4.0 OLE DB Provider or Microsoft OLE DB Provider for ODBC Drivers. Data types Text, Memo, Date/Time, Integer, Real, Boolean only; others are ignored. XLSX is not listed (inference: not covered).
- Three new-UDL buttons: 32-bit computer; 64-bit computer to 32-bit source; 64-bit computer to 64-bit source. Building the ODBC data link is a chain of dialogs (blocks scripts).
- Retrieval: table with a primary key = by key value; table without a key, or a query = by row index. (inference) Re-sorting or inserting rows in the source can change what a row-index field returns.
- Field expression form (backslashes were lost in the source text): `%<AecDb "DatabaseField" "<udl path>" "<connection string>" "<table or query>" "<field>" "<key type 1 or 2>" "SELECT ...">%` ([G:F4CCFDE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F4CCFDE3-ABEC-4030-905D-9CA8DC81CDA1)).

Update, display, convert
- Fields update automatically when the drawing is opened, saved, plotted, regenerated or sent by e-transmit ([G:7763D9C8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7763D9C8-F270-4D78-BDDD-2DDB1223FD5D)). Manual: select the field text > right-click > Update Field. All: Annotate tab > Text panel > Update Fields, select, Enter.
- (inference, core AutoCAD, not in these sources) FIELDEVAL controls which events update fields; verify in core help before relying on it.
- [AUTO] FIELDDISPLAY: 1 = grey field background (default), 0 = no background ([G:D48BB799](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D48BB799-F5C9-428A-9F47-163FF2D4187D)).
- Convert Field to Text cannot be reversed; the live link is lost ([G:76C68393](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-76C68393-2FC7-4203-862B-14C849E6BD4D), [G:6AF7B1B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6AF7B1B3-F944-4D15-BB18-691EFF8AD182)).
- Edit: right-click the field > Edit Field (route depends on the container) ([G:A9EB91E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A9EB91E9-E570-474C-A957-B6B6D08E4FB4)).

## 9.14 Sections: section lines, 2D and 3D sections, live sections

Three kinds of result ([G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B), [G:91CE3B2C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91CE3B2C-EBB5-4CDF-865D-37D2223C3098), [G:D43AA1C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D43AA1C2-205C-493E-84E7-7FFC98748CE6))
- 2D section ("2D Section/Elevation Object with Hidden Line Removal"): drawn WITHOUT hidden and overlapping lines; styled by a 2D Section/Elevation style; can be dimensioned; lines can be reassigned and geometry merged in.
- 3D section ("3D Section/Elevation Object"): 3D isometric object; uses NO style; only subdivision display is controllable. Hidden Line Projection can flatten any view of it to 2D.
- Live section view: a view of the model, not a new object; covers ALL objects in the drawing (no selection set); objects stay editable.
- Section objects stay linked to the model unless EXPLODED ([G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B), [G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33)).
- 2D sections and 2D elevations are the same object type and share styles ([G:074C9A40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C9A40-4F35-4638-BBF1-282DC68F53EE), [G:6540E996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6540E996-66CA-46B5-824A-ADFEBA8F8E3B)).

Workflow ([G:91CE3B2C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91CE3B2C-EBB5-4CDF-865D-37D2223C3098))
1. Draw a section line (sets length, depth, height).
2. Generate the section. Objects in the section volume are selected automatically EXCEPT hidden objects and objects on frozen or off layers.
3. Edit the line or the model.
4. Update the section, one at a time or for a whole project or folder (9.16).

Draw a section line [AUTO prompts] ([G:5BA9CA72](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5BA9CA72-1AD0-4F6C-99DC-47C218FC540C))
- Home tab > Section & Elevation panel > Section Line, or Design palette > Vertical Section tool. Command names in page metadata: BLDGSECTIONLINE ([G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B)) and VERTICALSECTION ([G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB)); the pages do not say which tool each one is (inference: test both).
- Prompts: start point; more points (optional jogs); endpoint, then Enter; length of section, or Enter to take the length from the line's endpoints.
- Direction: the marks point in the direction of the section, set by the direction you draw the line.
- Xrefs: when several xrefs link to a main drawing, draw the section line in the MAIN drawing.
- Marks are multi-view blocks anchored to the line. Bubble text: double-click the mark > Properties palette > Advanced > Attributes > Value ([G:291FCA1E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-291FCA1E-38D6-4E10-A49D-3745A1D6FA3C)).
- Default line height = model height. For a fixed height set "Use Model Extents for Height" = No on the Properties palette, or click the Model Extents grip off ([G:E16A5EB3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E16A5EB3-2A9E-48D4-BE6D-B29FD06FA44B), [G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B), [G:BC26262A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BC26262A-625E-4F0A-8C35-4A8D9677616C)).
- Inclusion test: every object whose bounding box overlaps the bounding box of the section volume goes into the selection set ([G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB)).
- When the line is finished you are prompted to place the result: click a point, or use the dialog option to set result type, selection set, display set or X,Y,Z placement ([G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB)). (inference) Test what typed answers this prompt accepts before scripting it.

Section line properties [GUI] (Properties palette, Design tab > Basic)
- Component Dimensions > Angle 1, Angle 2: sides of the section box. Angle 1 apex = line START, Angle 2 apex = line END; 0 to 90 degrees ([G:F8B3DA19](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8B3DA19-FE1A-468F-9CE7-081F57C3C05E)).
- Dimensions > Subdivisions: add (default distance, then edit), edit, delete. Each is a distance from the cutting plane ([G:3DF07385](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3DF07385-3D91-475B-9DED-1D1E70C82BEC)).
- Location > Additional Information: Insertion Point X,Y,Z; Normal (XY plane = Z 1; YZ plane = X 1; XZ plane = Y 1); Rotation Angle ([G:49399F89](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-49399F89-2979-4EE2-A2FF-4BC7444ECC87)).
- Extended Data: hyperlink, notes, reference documents ([G:B76D3F59](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B76D3F59-1C3C-4A97-BDC0-C7FD14397C2D)).
- Grips: start, end, edge, vertex; with a grip active you can type a distance on the command line ([G:32A6DCA1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-32A6DCA1-7476-448D-B323-27F2422B55FA)). Height and Lower Extension grips need a 3D view (View tab > Appearance panel > Views > SW Isometric) and the Model Extents grip turned OFF first ([G:BC26262A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BC26262A-625E-4F0A-8C35-4A8D9677616C), [G:34A85106](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-34A85106-2726-4126-9BB6-7AF6B5097583)). Length grip; Side 1 Endpoint grip (side 1 starts at the line's FIRST point); Side 2 Endpoint grip (starts at the END point); type a value + Enter ([G:82EE8DBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-82EE8DBD-E8F1-4B26-9FA5-1851EF0E241A)). Subdivision Distance grip ([G:DA8F5C7D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA8F5C7D-0D5E-412B-8E83-DCA4512ECDE0)). Right-click > Deselect All ends grip editing.
- Lower extension default, CONFLICT: the section page says that with model extents turned OFF the default lower extension is 1 ft below the XY plane ([G:34A85106](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-34A85106-2726-4126-9BB6-7AF6B5097583)); the elevation page says "If you use model extents, the default for the lower elevation is 1 foot below the XY plane" ([G:8BDA1915](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8BDA1915-B3BE-4A99-8A80-200B485067E4)). Read the value back before relying on it.
- Any change after a section exists needs a section update (9.16).

Generate the section [GUI dialog] ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618))
- Before: THAW and turn ON every layer holding objects to include; objects on frozen or off layers cannot be in the selection set. Turning off unneeded layers speeds the run. (inference) First thing to check when pipes are missing from a section.
- Select the line > Building Section Line tab > Modify panel > Generate Section > dialog:
  - Type: "2D Section/Elevation Object with Hidden Line Removal" or "3D Section/Elevation Object".
  - Style to Generate (2D only; Standard if none chosen).
  - Selection Set: Select Objects button, pick, Enter. Shift+click an included object to remove it.
  - Display Set: controls the representation.
  - Placement: New Object; Pick Point, or type X, Y, Z.
  - OK.
- Related command names with no syntax given: BLDGSECTIONLINEGENERATE, BLDGSECTIONUPDATE, 2DSECTIONRESULTUPDATE ([G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB)). (inference) BLDGSECTIONLINEGENERATE is probably the Generate Section button and would open the same dialog.
- Plan-view trap: a 2D section placed in a Plan view does NOT display if the Plan display set has "Section AEC Objects by Display Range defined in Display Configuration" checked. Clear it: Manage tab > Style & Display panel > Display Manager > Plan display set of the current configuration > Display Options tab ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618)).
- MEP: to leave a material (for example glass) out of the 2D section shrinkwrap, open the system style (Pipe tab > General panel > Edit Pipe Style or Edit System Style; Duct tab > Edit Duct Style; Cable Tray / Cable Tray Fitting tab > Edit System Style) > Other tab > check "Exclude from 2D Section Shrinkwrap" ([G:B9637CDC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B9637CDC-5AD7-4D06-B846-5AB886671869)).
- [AUTO] AECENABLESECTIONCLEANUP ([G:1F32A976](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1F32A976-C9F7-4ECF-A631-13D4AC39FC4A)): Switch, saved in Registry, initial OFF. ON or 1 = remove overlapping lines and segments from the 2D section result; OFF or 0 = keep them. ON makes generating and refreshing slower.

Horizontal section [AUTO prompts] ([G:795D2A09](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-795D2A09-5ACA-482E-BC5D-9E2F6E863997), [G:1D1C1731](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1D1C1731-23C4-489C-959D-C936D7AC13D3))
- Home tab > Section & Elevation panel > Horizontal Section, or Design palette > Horizontal Section. Looks DOWN on a plan without a manual UCS change.
- Prompts: first point of the plane; second corner; elevation of the plane, Enter; depth, Enter; then the Generate dialog as above.

Live section view ([G:2C634742](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2C634742-AE2E-4BC8-91A9-D385D57C68C0), [G:D43AA1C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D43AA1C2-205C-493E-84E7-7FFC98748CE6), [G:B1A77E10](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B1A77E10-106E-456C-907D-208030E7FD4B), [G:202E3A11](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-202E3A11-708F-4E66-A777-50F91688A2EB), [G:D8C8175B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8C8175B-7BA7-45D1-B788-5D9D37E953D8))
- Draw a section line; switch to a 3D view (SW Isometric); select the line > Building Section Line tab > Live Section panel > Enable Live Section. Disable Live Section turns it off; deleting the line removes it.
- Parts outside the line's box are hidden or drawn with the material's Sectioned Body component; the cut edge uses Sectioned Boundary. Set both in the material's display (select object > Edit Object Display > Materials tab > material > display representation > Layer/Color/Linetype). Toggle Body Display is on the Live Section panel.
- Trap: switching to a material whose Sectioned Body and Sectioned Boundary are OFF makes outside parts look deleted.
- Project sheet trap: a live section held in a view drawing and placed on a sheet needs a display configuration override on that view's xref in the sheet.

Edit the model from a section ([G:D4D9812C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D4D9812C-B0A6-4EF7-8C67-30E4FAC68812), [G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB))
- [AUTO] 2DSECTIONEDITLIVE (name only). GUI route: select the result > 2D Section/Elevation tab > Modify > Edit Live Section; edit the geometry (nested xrefs and blocks too); save xref changes when asked; close with the Edit In View button; the model updates.
- Edits to a checked-out xref or block are NOT saved.

## 9.15 2D Section/Elevation styles, display components, materials

Style basics ([G:82CECF32](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-82CECF32-E15B-46F8-8956-CD62F39C8E4F), [G:A8A29A32](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A8A29A32-9CC6-40A6-B88B-FEA9B0377F8C))
- One style type serves 2D sections and 2D elevations: Style Manager > Documentation Objects > 2D Section/Elevation Styles ([G:118F47B4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-118F47B4-6F5A-4783-ACEA-81EC3B8E4E87), [G:9A23958B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9A23958B-E688-4A65-A248-DB104595F57B)). Shortcut from a selected 2D section: 2D Section/Elevation tab > General panel > Edit Style drop-down > Edit Style (edits the current style) ([G:BD66563B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD66563B-EE22-488D-A8DA-CA4B3D5836D5)); the same drop-down also lists 2D Section/Elevation Style ([G:118F47B4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-118F47B4-6F5A-4783-ACEA-81EC3B8E4E87)).
- New: right-click 2D Section/Elevation Styles > New; or Copy, Paste, Rename. Apply saves and keeps Style Manager open ([G:9A23958B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9A23958B-E688-4A65-A248-DB104595F57B), [G:118F47B4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-118F47B4-6F5A-4783-ACEA-81EC3B8E4E87)).
- Tabs: General (Description, Notes), Classifications, Design Rules, Components, Display Properties ([G:5896A664](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5896A664-7A61-4436-B462-46FB5B9D60E5), [G:4F8754D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4F8754D6-936D-4D46-B696-E1AC0FD89D42), [G:D4518557](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D4518557-19F6-4AA5-8D35-9ED31091FF19), [G:B7838CD2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B7838CD2-93B1-42D9-BCBD-074A4857D698)).
- Classifications tab: default Unspecified for every classification definition; none listed = none apply to these styles ([G:5896A664](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5896A664-7A61-4436-B462-46FB5B9D60E5), [G:94D13B89](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94D13B89-E3C8-459B-9914-F993189B0E04)).
- Change the style of one result: double-click it > Properties palette > Design tab > Basic > General > Style ([G:1275EBC1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1275EBC1-1CBF-4A28-905B-67C8998AE6FD), [G:C54381B0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C54381B0-661F-4CF3-A016-260DF79556BD)).
- Style edits do NOT redraw existing results. Update them afterward ([G:9C986A47](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9C986A47-BB5D-460A-B093-D2BF7105FAFF), [G:4F8754D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4F8754D6-936D-4D46-B696-E1AC0FD89D42), [G:3EF05A23](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3EF05A23-783E-44FD-A52B-DFA0BA02ED0E)).
- 3D sections and 3D elevations use NO style ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618), [G:074C9A40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C9A40-4F35-4638-BBF1-282DC68F53EE)).

Design rules ([G:4F8754D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4F8754D6-936D-4D46-B696-E1AC0FD89D42), [G:3EF05A23](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3EF05A23-783E-44FD-A52B-DFA0BA02ED0E), [G:9C986A47](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9C986A47-BB5D-460A-B093-D2BF7105FAFF), [G:3B8C3E21](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B8C3E21-09B9-4416-937A-AA71AC31A584))
- A rule picks lines by (1) Color of the model objects and (2) Context (on the defining line, i.e. the cutting plane, or within subdivision N), and sends them to (3) a display Component. (4) Description is free text.
- Design Rules tab > Add creates a rule with defaults; click each field to change it. Remove: select > Remove ([G:8B57C61A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8B57C61A-FDAB-474F-A474-3B15A48EAE5C), [G:5A030353](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5A030353-FCA4-4195-8CEC-834091F21742)).
- Examples: color 50 + Within Subdivision 2 -> custom component New; color 150 on the defining line -> custom component "Darker"; all blue linework -> Hidden, to hide a staircase behind a wall ([G:4F8754D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4F8754D6-936D-4D46-B696-E1AC0FD89D42), [G:82CECF32](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-82CECF32-E15B-46F8-8956-CD62F39C8E4F)).
- "Keep all hidden linework" check box: sends hidden linework not handled by a rule to the Hidden component (to see every edge, e.g. foundations). Hidden lines can also be chosen by object material ([G:4F8754D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4F8754D6-936D-4D46-B696-E1AC0FD89D42), [G:3EF05A23](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3EF05A23-783E-44FD-A52B-DFA0BA02ED0E)).
- (inference) Rules match on model object color. How ByLayer or system-style colors of MEP objects are matched is not stated; test with one pipe system before relying on rules.

Display components ([G:D4518557](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D4518557-19F6-4AA5-8D35-9ED31091FF19), [G:E03B02BC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E03B02BC-91B9-4AE4-8559-5D5F55496870), [G:2BD6EF97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2BD6EF97-0281-4EE2-9ADC-4351EE442305), [G:6540E996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6540E996-66CA-46B5-824A-ADFEBA8F8E3B))
- Default 2D components named on the style pages: Defining Line, Hidden, Erased, Unknown, Subdivision ([G:D4518557](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D4518557-19F6-4AA5-8D35-9ED31091FF19), [G:E03B02BC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E03B02BC-91B9-4AE4-8559-5D5F55496870)). The component/material map also lists Outer Shrinkwrap, Inner Shrinkwrap, Shrinkwrap Hatch, Surface Hatch Linework, Section Hatch Linework, Subdivision 1-10 ([G:2BD6EF97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2BD6EF97-0281-4EE2-9ADC-4351EE442305)).
- Add a custom one: Components tab > Add > click Unnamed to name it > Description; then Display Properties tab > Style Override > Layer/Color/Linetype ([G:D4518557](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D4518557-19F6-4AA5-8D35-9ED31091FF19), [G:E03B02BC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E03B02BC-91B9-4AE4-8559-5D5F55496870)).
- Remove: only CUSTOM components can be removed; removing one also deletes every design rule that uses it (a warning shows) ([G:B1E0F73C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B1E0F73C-6A63-4558-B6E9-618A91EB6272), [G:BA0B1295](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA0B1295-DE6C-43DC-96E3-0D329DCD86A2)).
- On one result: double-click > Properties palette > Display tab > Display component must read *NONE* > Display controlled by: This object / Drawing default setting / <style name> > Object Display Properties Advanced > Additional Properties > Add (double-click Unnamed to name) ([G:86A35B27](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-86A35B27-1393-45BF-8AEF-97569E347F18), [G:2C6F9B3B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2C6F9B3B-F37B-4C4D-BFD9-E3301E357E36)).
- Meanings:
  - Defining Line: the cut at the cutting plane; material component 2D Section/Elevation Linework or 3D Body. One cut color for everything = give it a color and do not use materials; color by cut object = use materials ([G:B30218E2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B30218E2-ADC6-4C7F-95A4-9B06598D10BC), [G:2BD6EF97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2BD6EF97-0281-4EE2-9ADC-4351EE442305)).
  - Hidden: lines hidden behind other components. OFF by default. 2D only. No material link ([G:A89D0516](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A89D0516-3B22-4659-80A4-2BD3253E4B04), [G:07591AB2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-07591AB2-021B-4427-8807-E7CE93A460DC)).
  - Erased: lines you do not want to see (floor lines between stories). OFF by default. 2D only. No material link ([G:6CF252CC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6CF252CC-A7D9-41D8-B18F-6B4F8E4B208C), [G:4BF35F18](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4BF35F18-784C-42CB-9F65-7360C57E514D)).
  - Outer / Inner Shrinkwrap: outline of solid parts / of holes, from the union of all cut faces. 2D only. No material link. Single objects (window glass) can be excluded ([G:082487C1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-082487C1-E4F6-4E9A-8540-07F1327A7190)).
  - Shrinkwrap Hatch: hatch of that union. 2D only. No material link. It overlaps Section Hatch: give it a SOLID hatch, or use only one of the two ([G:B5F147D7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B5F147D7-A155-41A3-A0BE-51F548B81B75), [G:B98AA0FC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B98AA0FC-7E2C-48D0-B09B-0DE3F2CCE8CB)).
  - Section Hatch Linework: hatches on every cut face, not merged. 2D only. From the material's Section Hatch component ([G:B98AA0FC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B98AA0FC-7E2C-48D0-B09B-0DE3F2CCE8CB)).
  - Surface Hatch Linework: hatches on faces NOT cut. From the material's Surface Hatch component. Shows in 3D results but is settable only in 2D ([G:DEE09EA0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DEE09EA0-3821-4262-9DC1-1E6B403F80EE), [G:D6D0E8A7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D6D0E8A7-3A11-4BB1-AC7F-F6CE2EA5C732)).
  - Subdivision 1-10: slices at distances from the cutting plane; 2D and 3D. From the material's 2D Section/Elevation Linework or 3D Body component. Subdivision 1 = closest to, but not on, the cutting plane ([G:39C611B0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-39C611B0-5B2F-48D6-9838-CC86C3D234E9), [G:01D56092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-01D56092-0EE6-4533-9CCC-15D0D6EBE450), [G:60109CA6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-60109CA6-DC9F-4C04-B52D-CADFE525D2B3)).
  - Unknown: listed as a default component; its meaning is not explained in these sources.

Materials ([G:2BD6EF97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2BD6EF97-0281-4EE2-9ADC-4351EE442305), [G:6540E996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6540E996-66CA-46B5-824A-ADFEBA8F8E3B), [G:A1BE7822](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A1BE7822-0530-446D-8746-D3D9951D48FF), [G:B4F05E64](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B4F05E64-1288-45E4-906B-EDEB3E60D57C))
- A material is never assigned to a section or elevation directly; the result inherits materials from the cut objects (brick wall gives a brick hatch; change the wall to concrete and update: gray concrete).
- Per component: Display Properties tab > representation > Style Override > Layer/Color/Linetype > By Material. Hidden, Erased and the shrinkwrap components cannot be By Material; custom components cannot use materials ([G:82CECF32](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-82CECF32-E15B-46F8-8956-CD62F39C8E4F), [G:A1BE7822](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A1BE7822-0530-446D-8746-D3D9951D48FF)).
- To ignore materials, deactivate material assignments in the result's or the style's display properties ([G:2BD6EF97](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2BD6EF97-0281-4EE2-9ADC-4351EE442305)).
- Other tab, "Use 3D Body Display Component for By Material Linework": cleared by DEFAULT = linework from the material's 2D Section/Elevation Linework component; selected = from its 3D Body component ([G:7B82B726](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7B82B726-3559-4E95-8039-EF6CBF2514D5), [G:98FCE6FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-98FCE6FD-C164-4064-976D-BE0F1FA722A6)).
- Subdivision plus material: clear By Material on the subdivision, set its layer, color, linetype; Other tab > "Use Subdivision properties for surface hatching". Result: hatch pattern from the material, color and linetype from the subdivision ([G:CA0C1F50](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CA0C1F50-59A0-4DB0-A80D-CCC8C5A602CC), [G:7DCACEA5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7DCACEA5-2097-4CC8-8C0A-881C91A746D8), [G:2C6F9B3B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2C6F9B3B-F37B-4C4D-BFD9-E3301E357E36)).
- Hatching tab of the 2D section display changes the shrinkwrap hatch pattern ([G:01D56092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-01D56092-0EE6-4533-9CCC-15D0D6EBE450)).

Display scope
- 2D: Drawing Default (all results without a style override); 2D Section/Elevation Style + Style Override (all of that style); 2D Section/Elevation + Object Override (this one) ([G:AD82DC7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD82DC7E-C297-4C1F-BB44-A143A578CDF7), [G:01D56092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-01D56092-0EE6-4533-9CCC-15D0D6EBE450)).
- 3D: select > right-click > Edit Object Display > Display Properties tab > "Sub-divisions" (Subdivisions) representation > Object Override, or Drawing Default for all 3D results ([G:D31672AB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D31672AB-A29C-4FE2-9875-4429185B729D), [G:5E422D36](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5E422D36-988C-445F-9B4D-4900E2FC3741)). Per Subdivision n: visibility, layer, color, linetype, lineweight, linetype scale. "Defining line" = the cutting plane.
- Every 2D component: visibility, layer, color, linetype, lineweight, linetype scale; Other tab adds a custom component ([G:AD82DC7E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD82DC7E-C297-4C1F-BB44-A143A578CDF7), [G:01D56092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-01D56092-0EE6-4533-9CCC-15D0D6EBE450)).

## 9.16 Updating sections and elevations (Refresh, Regenerate, Batch Refresh)

When an update is needed ([G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33), [G:012EF996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-012EF996-078C-404E-9940-26B56EADF4DA))
- After model changes; after section/elevation line changes (height, length, angles, lower extension, subdivisions, reverse); after 2D style changes (design rules, components, display).
- LIMIT: an EXPLODED section or elevation is unlinked from the model and can never be updated ([G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33), [G:012EF996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-012EF996-078C-404E-9940-26B56EADF4DA)).

Refresh and Regenerate [GUI] ([G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33), [G:012EF996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-012EF996-078C-404E-9940-26B56EADF4DA), [G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB))
- Refresh (2D only): select the result > 2D Section/Elevation tab > Modify panel > Refresh. Re-runs at once with the same object set; no dialog.
- Regenerate (2D or 3D): select > 2D (or 3D) Section/Elevation tab > Modify panel > Regenerate > Generate Section/Elevation dialog:
  - result type; Style to Generate (2D);
  - if linework was edited: a style to hold edits that cannot be reapplied (pick one that makes them visible);
  - Selection Set: keep the prior set, Select Additional Objects (pick, Enter), or Reselect Objects (new set, Enter); Shift+click removes an object;
  - Display Set;
  - Placement: New Object (click a point or type X, Y, Z; the original stays) or Replace Existing.
- Regenerate's Select Objects works per object only, not per style or object type ([G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB)).
- Reverse: select the line > Building Section Line (or Building Elevation Line) tab > Modify panel > Reverse. The line and its box mirror; the existing result changes only after Regenerate, or Refresh for a 2D result with the same objects ([G:03CA6325](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-03CA6325-428A-4A7D-9034-11EAC18E50C0), [G:503FF27A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-503FF27A-CE4E-4B61-8993-056038D3348A)).

Refresh on Open ([G:DC846586](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DC846586-489E-4BCE-ACDE-8862AD8A7AF5), [G:E0F1D08D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E0F1D08D-FAFD-4BB7-AD59-9C47775FD3CB))
- Select the result > Properties palette > Refresh on Open = Yes (default No). Refreshes every time the drawing opens; works per result and for results inserted as xrefs; a progress bar shows per result.
- With it on you cannot start working until every such result has refreshed; time grows with count and size; xref results are slower.

New objects missing from a result ([G:D17AE7B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D17AE7B3-0D04-4A62-A70D-409A3E1F91AA))
- A legacy drawing not last saved in AutoCAD Architecture 2016 auto-excludes every NEW object from the section result. Fix: refresh the result before adding objects, or open and save the drawing in ACA 2016 first.
- Still missing: [AUTO] type 2DSECTIONRESULTUPDATE, then in the Generate Section dialog make sure the new objects are included. The dialog is required.

MEP project views ([G:0FDE6F42](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0FDE6F42-962D-4157-A71E-F64F87C93DBC))
- Project Navigator > Views tab > open the drawing that holds the section or elevation view (the drawing with the marks need not be open) > click the section/elevation geometry > 2D Section/Elevation tab > Modify panel > Regenerate > Generate Section/Elevation dialog > OK.
- A view already on a sheet updates the next time the sheet is opened.

Batch Refresh, global update [GUI dialog] ([G:E8108182](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8108182-5409-4B7E-AE28-541CDE7F8D6A), [G:5F09E47B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5F09E47B-E32B-4B6D-95E5-82280FACA120), [G:AEE4C8F7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AEE4C8F7-C2AC-4BF7-8BA2-DB42DE49A17C), [G:62609546](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-62609546-0375-4F12-A8BC-7371D5B61B0F), [G:9938C56F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9938C56F-A23B-4F64-BDCB-10900A6EF7F4))
- Home tab > Section & Elevation panel > Batch Refresh. Scope: Current Project (needs a current project, else an error) or Folder (Browse; tick Process subfolders). Begin; a status window names each drawing; Stop works during the run.
- Project scope covers 2D sections and elevations in project VIEWS and SHEETS, not elements or constructs. A chosen folder updates every section and elevation in it, any drawing type. All model and paper space layouts of each drawing are updated.
- Each drawing is opened, updated and saved. Older-version drawings are CONVERTED to the current version after a warning (OK, or Ctrl+Break to cancel the whole update).
- Fails per drawing (message in the status window) when: the drawing is read-only; the result is on a locked layer; user edits cannot be reapplied. Fix: make it read/write, unlock the layer, undo the edit.
- Large projects are slow: run one subfolder at a time.

## 9.17 Elevations

Workflow ([G:ED623D71](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ED623D71-2771-4DCD-B513-A40A90B90528), [G:76879DE6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-76879DE6-874B-4348-8E96-AE1D35786D5E), [G:4967984F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4967984F-C388-4110-AA85-2F22C9F4E083))
1. Draw an elevation line and mark (sets width, height and length to extract).
2. Generate a 2D or 3D elevation from it.
3. Edit the line, the elevation or the model.
4. Update one elevation or Batch Refresh (9.16).
- 2D elevation = "2D Section/Elevation" object with hidden and overlapping lines removed; same object type and styles as 2D sections. 3D elevation = 3D isometric object, no style, only subdivision display ([G:4967984F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4967984F-C388-4110-AA85-2F22C9F4E083), [G:074C9A40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C9A40-4F35-4638-BBF1-282DC68F53EE)).

Draw an elevation line [AUTO prompts] ([G:F49E90F1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F49E90F1-5DCE-49D8-A4B5-A0A044D41448))
- Home tab > Section & Elevation panel > Elevation Line. Prompts: start point, then endpoint. No typed command name is given in these sources.
- The direction you draw sets which way the mark and the view point. The boundary box uses the line as its LEFT side; in plan, select the line to see the box.
- Start and end must run past the face of the model so every object falls inside.
- Several xrefs linked to a main drawing: draw the line in the MAIN drawing.
- The mark is a multi-view block anchored to the line; bubble text: double-click > Properties palette > Advanced > Attributes > Value ([G:1257256B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1257256B-E623-4F27-A081-035412BE0975)). The page intro mentions a mark at each end; later text says "an elevation mark".
- Elevations can also be made with callout tools (9.19).

Elevation line properties and grips
- Angle 1 / Angle 2: Properties palette > Basic > Component Dimensions; 0 to 90 degrees; Angle 1 apex = line START, Angle 2 apex = line END ([G:943E6E53](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-943E6E53-098A-471D-87E9-9F3FAFAFAC84)).
- Height: floating View panel > View drop-down > SW Isometric; select the line; click the Model Extents grip to turn it OFF; drag the Height grip or type a value. With model extents ON, height follows the objects and cannot be changed dynamically. Objects are cut at this height ([G:DE9BDA12](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DE9BDA12-A1DE-4FC9-9E36-91256D0CC1E0)).
- Lower Extension: same steps with the Lower Extension grip ([G:8BDA1915](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8BDA1915-B3BE-4A99-8A80-200B485067E4)). Default conflict with the section page: see 9.14.
- Length grip (whole boundary); Side 1 Endpoint grip (side 1 starts at the line's FIRST point); Side 2 Endpoint grip (starts at the line's END point). Drag and click, or type a value + Enter ([G:9EAB5B87](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9EAB5B87-D24C-4FF4-B5AD-E487080D1B7C)).
- Start, end and edge grips: drag, or move in a direction and type a distance ([G:6DEE6737](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6DEE6737-DD40-451A-8842-8D1F5D330C65)).
- Subdivisions: Properties palette > Basic > Dimensions > Subdivisions > add / edit value / delete. Use heavier lines near, lighter far ([G:6FFB0602](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6FFB0602-5969-42BF-AD3C-629FCDAA8A15), [G:FAEE8533](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FAEE8533-9AD5-42B1-8CA8-29FE856C948D)).
- Location: Basic > Location > Additional Information > Insertion Point, Normal, Rotation Angle ([G:F21FD5F2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F21FD5F2-6527-4CDF-91F0-EAF766D41BD2)).
- Extended Data tab: hyperlink, notes, reference documents ([G:77712BBC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-77712BBC-5153-4468-B1AF-3C38B35BC5C1)).
- All of these can be set before or after the elevation exists; after = update it. Right-click > Deselect All ends grip editing.

Generate the elevation [GUI dialog] ([G:074C9A40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C9A40-4F35-4638-BBF1-282DC68F53EE))
- Thaw and turn ON the layers of every object to include; frozen or off objects cannot be selected. Turning off unneeded layers speeds the run.
- Select the line > Building Elevation Line tab > Modify panel > Generate Elevation > Type ("2D Section/Elevation Object with Hidden Line Removal" or "3D Section/Elevation Object"), Style to Generate (2D only; Standard if none), Selection Set (Select Objects, Enter; Shift+click removes), Display Set, Placement (New Object; Pick Point or X, Y, Z) > OK.
- The elevation stays linked to the model; update it after changes.
- Move or re-orient the elevation: Properties palette > Basic > Location > Additional Information ([G:A0228306](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A0228306-4679-45DE-AF6A-47E3AAFADC7E)). Notes and files on the elevation: Extended Data tab ([G:0CC7A0EB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0CC7A0EB-2579-4E03-A974-031E8A2A88DF)).
- Editing options after creation: subdivisions, reverse, move, notes, another style (2D), linework display, merged detail linework ([G:8A110F70](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8A110F70-CC26-4B28-95AD-277582923E2D)).

Reverse ([G:503FF27A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-503FF27A-CE4E-4B61-8993-056038D3348A))
- Select the line > Building Elevation Line tab > Modify panel > Reverse > select the elevation > 2D or 3D Section/Elevation tab > Modify panel > Regenerate (or Refresh for 2D with the same objects; Reselect Objects to change the set).

## 9.18 Material boundaries, linework edits, hidden line projection

Material boundary (2D sections and 2D elevations)
- Purpose: Limit (highlight) or Erase (mask) part of a 2D result: cleaner hatching for construction documents, highlight a region, mask an area to draw more detail, crop an irregular portion ([G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B), [G:4967984F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4967984F-C388-4110-AA85-2F22C9F4E083)).
- Create: draw a closed polyline around the area > select the result > 2D Section/Elevation tab > Material Boundary panel > Add > select the polyline > [AUTO] prompt: y = erase the polyline, n = keep it > dialog > OK ([G:8E31B38B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8E31B38B-838E-4741-B5A6-2634683ECC36), [G:D99DE6BD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D99DE6BD-D702-4D1B-9E16-5D680454C52F)).
- Dialog fields:
  - Purpose: Limit (highlight inside) or Erase (mask inside).
  - Apply to, section page: Surface and Section Hatching / Section Hatching Only / Surface Hatching Only / Edge Linework Only / All Linework, plus check boxes "Apply to section shrinkwrap linework" and "Apply to section shrinkwrap hatching" ([G:8E31B38B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8E31B38B-838E-4741-B5A6-2634683ECC36)). Elevation page: Surface Hatch / Edge Linework / All Linework ([G:D99DE6BD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D99DE6BD-D702-4D1B-9E16-5D680454C52F)).
  - Material Selection: All Materials, or Specific Materials (pick from the list).
- Edit content: select the result > Material Boundary panel > Edit In Place > Edit In Place tab > Profile panel > Edit Material Boundary > same fields > OK > Edits panel > Finish (save) or Cancel (undo) ([G:BCF5FCC7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BCF5FCC7-125C-47DD-AF89-EE855ED19AFC), [G:36AB6F95](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-36AB6F95-33C6-4F2A-BEBE-07202A4AAD95)).
- A boundary can hold several closed rings ([G:D6F3DC4C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D6F3DC4C-BF7F-4473-A1A9-730DF7E5107D), [G:A040C089](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A040C089-DC50-4A75-8F4F-F446253705E3)). Shape edits all start with Material Boundary panel > Edit In Place:
  - Add Ring: draw the polyline first; Profile panel > Add Ring (elevation page: Edit Material Boundary, then Add Ring); pick the polyline; [AUTO] y/n erase; Finish or Cancel ([G:D6F3DC4C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D6F3DC4C-BF7F-4473-A1A9-730DF7E5107D), [G:A040C089](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A040C089-DC50-4A75-8F4F-F446253705E3)).
  - Replace Ring: draw a closed polyline first; Profile panel > Replace Ring; pick the ring, then the polyline; [AUTO] y/n; Finish or Cancel ([G:F605FA2B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F605FA2B-B36A-4CDE-9D1F-84C5B02BCD09), [G:4802BEF0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4802BEF0-7E17-4C04-B686-09E72118D6B2)).
  - Remove Ring: Profile panel > Remove Ring > pick the ring > Finish or Cancel. The LAST ring cannot be removed ([G:E8DD4E76](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8DD4E76-9CFF-40A6-A8A6-A34DE939509E), [G:41E57AB3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-41E57AB3-10C2-44AF-9D1C-5FB90586DD21)).
  - Add Vertex / Remove Vertex: right-click > Add Vertex (or Remove Vertex) > pick points > Enter > Finish or Cancel; the elevation pages finish with select the boundary > right-click > Save Changes or Discard All Changes ([G:AC9422D1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AC9422D1-C300-4D10-B508-987DDFA3047C), [G:CB558CE8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CB558CE8-29C9-4B19-9501-8773F684B982), [G:084C398E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-084C398E-1A2D-46FC-AFBA-1D96BE4A4447), [G:EEA39ACE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EEA39ACE-F06E-4C2A-BA1F-AE7A9B286631)).

Linework edit and merge (2D results only)
- Edit: select the result > 2D Section/Elevation tab > Linework panel > Edit, or the Edit Linework grip > contextual Edit In Place: Linework tab > Profile panel > Zoom To (optional) > select lines > Profile panel > Modify Component > pick a component ("Erased Vectors" for Linework Component = invisible) or Match existing linework (click a line to copy its component) > OK > Edits panel > Finish (save all) or Cancel (discard all) ([G:C8448BEF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8448BEF-5CD3-4D83-82FD-052BA99EDEA1), [G:69653A2B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-69653A2B-2540-41D6-ACF5-021D3C216BA9), [G:6FACA0F8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6FACA0F8-182A-4198-A110-AA4C04022796), [G:64385943](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64385943-862E-461B-8A36-7BB2E05A900F)).
- [AUTO] AEC2DSECTIONRESULTABORTCHANGES, then select the component: undoes all changes to that component made in this edit-in-place session AND exits edit-in-place mode ([G:C8448BEF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8448BEF-5CD3-4D83-82FD-052BA99EDEA1)).
- Lines put on a fixed (default) component follow that component's display in every result you generate; custom components can be used too. Then set visibility, color, layer, lineweight, linetype, linetype scale of the component ([G:C8448BEF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8448BEF-5CD3-4D83-82FD-052BA99EDEA1), [G:6FACA0F8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6FACA0F8-182A-4198-A110-AA4C04022796)).
- Merge: draw the geometry > select the result > Linework panel > Merge > select geometry, Enter > pick a component, or Match existing linework > OK. Merged lines are then selected with the result ([G:549B1A1E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-549B1A1E-48E5-476B-A88E-AA243B5C3288), [G:75DD2C6D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-75DD2C6D-8E11-4F1B-B477-ABE6A90C7AB1)).
- Use: put small-detail lines on a lighter component so they are not lost when plotted ([G:AB045123](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AB045123-2DB3-4A9D-8FBD-50B7DFC45E36), [G:0156E6C6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0156E6C6-96D6-43A6-BE4B-8C6A3A6D53CA)).
- On Regenerate, edits that cannot be reapplied go to a style you choose in the dialog ([G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33), [G:012EF996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-012EF996-078C-404E-9940-26B56EADF4DA)).

Hidden Line Projection ([G:ECC0BCFF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ECC0BCFF-3398-4B47-91E9-EA2F06AD427F))
- [GUI] Home tab > Section & Elevation panel > Hidden Line Projection, or a hidden line projection tool (Stock Tool Catalog > Helper Tools). The page calls it "the Hidden Line Projection command" but gives no typed name.
- [AUTO] Prompts from the source page: (1) in a 3D view select one or more objects, Enter; (2) specify an insertion point; (3) then Enter = insert the 2D block in PLAN view, or n (No) = insert it in the CURRENT view. The page words steps 3 and 4 both as "insertion point", so test the exact order before scripting.
- Output: the selected 3D objects are copied into an unnamed (anonymous) 2D block with hidden background lines removed. It is NOT linked to the 3D objects: edit or re-create it after model edits. It can be edited or exploded; define a block to reuse it by name in another drawing.
- Uses: quick 2D elevations and sections, hatching cut areas, details; also flattens any view of a 3D section or 3D elevation ([G:FE43AB5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE43AB5D-622A-45B0-9F70-D9E49FEC832B), [G:4967984F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4967984F-C388-4110-AA85-2F22C9F4E083)).

Escarpment (Architecture annotation, for completeness) ([G:34A5D10A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-34A5D10A-85A2-41BD-A00D-E15CFFE7D2D5))
- Vision Tools tab > Graphics panel > Escarpment > select the upper and lower boundary > [AUTO] type the spacing of the pattern lines on the command line. Makes a block on the CURRENT layer; edit it in the Block Editor. Page metadata command id: AECID_AECESCARPMENT. 2027 fixed repeat use of the Escarpment tool ([G:C901BBAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C901BBAD-C2B9-4299-8B64-35A7C2DF1D4F)).

## 9.19 Callouts, model space views, view drawings and sheets

Concepts ([G:45853BC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45853BC2-D6D9-41B6-B75A-F76CFAC41898), [G:9088C49A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9088C49A-32D0-44B1-83F0-3266FCF04280), [G:9497A447](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9497A447-0698-4DE1-845C-7CE7A2BF496E), [G:2AA8D871](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2AA8D871-5CF9-451A-B44F-6A2493C497E7))
- A callout tool marks part of the model as a detail, section or elevation and puts it in a MODEL SPACE VIEW: a named view with a defined boundary and its own description, display configuration, layer snapshot, drawing scale, layer state and view direction (an evolution of AutoCAD Named Views).
- A model space view can go in the current view drawing, an existing project view drawing, or a new one.
- View drawing types (Project Navigator > Views tab): General, Detail, Section/Elevation; each has its own view template in project settings. The 2027 help describes the Detail and Section/Elevation types and the four-way elevation tools as enhancements ([G:45853BC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45853BC2-D6D9-41B6-B75A-F76CFAC41898)).
- Detail callout: enlarged view of items not in the model (bolts, connectors); can also call out part of an existing section. Section callout: a section of the model, can be the base for a detail. Elevation callout: interior or exterior elevations; interior elevations can use spaces as the boundary.
- Callouts and model space views belong to Drawing Management projects; outside a project they work only partly ([G:45853BC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45853BC2-D6D9-41B6-B75A-F76CFAC41898)).

Place a callout [GUI with prompts] ([G:2DA336FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2DA336FE-C4DB-4B6C-ACDE-8C5297933281), [G:DA42867B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA42867B-ED99-45F8-9547-F3155918B662), [G:D7B13548](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7B13548-EEAD-4277-AA27-191D63773D74))
- Project Navigator > Views tab > right-click the view drawing > Open > Tool Palettes > Properties > Document > Callouts palette; or Annotate tab > Callouts panel.
- Single elevation: Elevations drop-down > Elevation (Single) or Elevation (Single, Inverted Text). Order: mark location; direction; Place Callout dialog; first corner of the region; opposite corner; insertion point of the result.
- Four-way exterior: Elevation (Exterior). Order: first corner of the region; opposite corner; dialog; height of the elevations; insertion point; distance between elevations and their orientation.
- Four-way interior: Elevation (Interior. 1, 2, 3, 4) or Elevation (Interior. N, S, E, W). Order: mark location; direction of the first elevation number; dialog; region (select a space then Enter, or Enter and pick two points); depth; height; insertion point; spacing and orientation.
- Place Callout dialog: New Model Space View Name (four-way: name of the first view); Generate Section/Elevation; Place Titlemark; Scale; Create in = Current Drawing / Existing View Drawing / New View Drawing; Callout Only button (symbol only, no view).
- The 2D Section/Elevation style and display set of the new views come from the callout tool, not from this dialog.
- If the view lands in another drawing, you still pick the insertion point in the CURRENT drawing; the result goes into the chosen drawing.
- Callout tool properties: right-click the tool > Properties (the property list is on a page not in these notes) ([G:A8561D33](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A8561D33-2278-4E60-8257-E9E58EB3690D)).

MEP project workflow for detail, section and elevation views ([G:052CBAD9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-052CBAD9-1039-4A77-B2B8-03379634E6DC), [G:4AE2D1E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AE2D1E8-7C11-45C3-AE95-2E2317AA6270), [G:4BEE1C40](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BEE1C40-14D6-4F2D-A715-AC023E3DAC5D))
1. Open the general view drawing.
2. Annotation palette > detail mark, detail boundary, section mark or elevation mark tool (or Annotate tab > Callouts panel).
3. Pick the mark points (detail: leader points and tail direction; section: section line points, Enter at the mark location, then the extents; elevation: mark location, viewing direction).
4. Place Callout dialog: name; detail = CLEAR Generate Section/Elevation; section and elevation = keep it checked; Scale; Create in = New View Drawing.
5. Add view dialog: Name (file name), Category (folder), Drawing Template (from project settings) > Next > floors (constructs must be assigned to those floors) > Next > constructs (attached as reference drawings) > OK.
6. Pick the region (detail: two corners; elevation: region corners), then the insertion point. The view is NOT inserted into the general view; the point is its location in the NEW drawing. Pick away from geometry; zoom and pan work during the command.
7. The new view drawing is created but NOT opened. Mark numbers show "?". Save and close the general view drawing; double-click the new one on the Views tab; Zoom Extents.
- OVERLAY trap: a drawing referenced as an overlay in a view drawing is NOT included when the view goes on a sheet. If a construct holds an overlay reference (such as a floor plan), select that reference drawing too or it will not show.
- A detail boundary drawn with the detail boundary tool is annotation only; it does not define the detail region ([G:052CBAD9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-052CBAD9-1039-4A77-B2B8-03379634E6DC)).
- Layers of the source objects are kept in the section or elevation view ([G:4AE2D1E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AE2D1E8-7C11-45C3-AE95-2E2317AA6270), [G:4BEE1C40](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BEE1C40-14D6-4F2D-A715-AC023E3DAC5D)).
- Updating these views: 9.16 ([G:0FDE6F42](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0FDE6F42-962D-4157-A71E-F64F87C93DBC)).

Fields in callout symbols ([G:BFCD066E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BFCD066E-4C43-4F42-A00F-6F3C31FFEFB4), [G:98E4380B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-98E4380B-2F78-4E96-BE40-33FFF575BB19), [G:704295C4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-704295C4-41A7-44C7-AB43-2295EA2FBEDB), [G:7B46657F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7B46657F-63CA-44D4-A04A-1E75D76247C3))
- Predefined callouts carry sheet number and view number placeholders. They show "?" until the model space view is placed on a sheet: Project Navigator > Sheets tab > open the sheet > Views tab > drag the model space view onto the sheet, or right-click it > Place on Sheet > insertion point. Afterward Ctrl+click the sheet number to open that sheet.
- Callout Only symbols show raw field names ("Viewnumber", "Sheetnumber"). Link one later: select it, then drag it onto a model space view (fields become "?") or a sheet view (fields resolve) in Project Navigator.
- Sheet set fields mostly refer to the CURRENT sheet: use them only in sheet drawings. Callouts use fields because property set data work only in MV blocks.

Title marks ([G:64625EBC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64625EBC-3524-4789-A63D-E97638B1EA4F), [G:BC91D617](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BC91D617-B7DE-4EE3-B717-775F5AC27FE4))
- Annotate tab > Callouts panel > Title drop-down > Title (or a Callouts palette tool) > select the model space view (its boundary highlights) > start point > end point.
- A title mark cannot create a model space view; it links to an existing one. Shipped title marks show view number, view title and viewport scale fields.

Outside a project ([G:DEF514A8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DEF514A8-2D91-4A43-A70A-42296A4E1A15), [G:EC37863C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EC37863C-0D59-4DB8-867B-691FDEA38AB2))
- Model space views only in the current drawing, reachable only through the Named Views dialog.
- Detail, section and elevation templates cannot be used.
- View and sheet field placeholders never resolve: type the values by hand.
- Placement: as above with Create in = Current Drawing.

Sheets ([G:BE4BC78E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE4BC78E-2642-4417-BB20-D8A7A1BA44C7))
- Project Navigator > Sheets tab > right-click a subset > New Sheet > number and title > OK. The sheet is created but NOT opened; double-click to open.
- Drag a view drawing from the Views tab onto the sheet; right-click the placed view to change scale. Only the detail, section or elevation view lands on the sheet, not the referenced plan.
- A schedule needs a viewport first: View tab > Viewports panel > Named.
- Renaming or moving a view drawing breaks the mark and sheet number link; the mark may need to be recreated.
- Sheet list tables, DWF publishing and other sheet set work are covered with sheets and publishing.

## 9.20 Consolidated limits and gotchas

Checklist before a scripted schedule run
1. PSDs and data formats are in the drawing. Copying the schedule table style brings its PSDs and formats with it ([G:52325092](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52325092-A648-4B6A-9B7B-2343228ECD26)).
2. The Edit Property Set Data worksheet is turned off (Options > AEC Content tab) before any tagging ([G:E2246F50](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E2246F50-4651-4593-B195-31CBE0A33680)).
3. AECPSDAUTOATTACH (registry, initial 0) and AECXREFPSDAUTOATTACH (registry, initial 1) are set on purpose for this session ([G:DFAE2FBC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DFAE2FBC-447C-4C1B-8B75-6C6E68BC6BAB), [G:C3269688](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3269688-6A43-4A35-9ED8-9C215CE1C059)).
4. PSD and property names have no spaces ([G:306E5BBD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-306E5BBD-FAA3-4E22-84CD-6AFED73B3EC1)).
5. Table style: Applies To set before columns; every column's PSD applies to ALL ticked object types ([G:9F9D2456](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9F9D2456-7BED-4A80-B1F5-805C55E1A0A5), [G:4EDBEA36](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4EDBEA36-E61F-4922-8AD8-66F215AFEAA6)).
6. Table: "Add new objects automatically" and "Update automatically" chosen; Update before every plot; reopen the drawing before plotting after RefEdit work ([G:3E451D9B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3E451D9B-9D08-4BB5-BA68-CB6F339A82FA), [G:5E6C9FC3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5E6C9FC3-35E0-428F-ADD0-9C03B06429D0), [G:EE2772AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EE2772AE-492F-4059-A88C-5D0111694F4A)).
7. Xref schedules: Scan xrefs = Yes and a layer filter naming the xref's layer AND the inner object's layer ([G:5E6C9FC3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5E6C9FC3-35E0-428F-ADD0-9C03B06429D0)).
8. Sections and elevations: layers of the objects to include are thawed and ON before Generate ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618), [G:074C9A40](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-074C9A40-4F35-4638-BBF1-282DC68F53EE)).

Data-loss traps
- Deleting an MEP tag deletes the PSDs it assigned and ALL their values for that part ([G:1D9664E1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1D9664E1-943C-420F-9370-D259C194158C)).
- Detaching a set in Browse Property Data deletes manual values; Undo at once ([G:FA81E478](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA81E478-0399-4703-812D-FE81F88A6089)).
- PROPERTYSETCLEAN answered with Enter removes ALL property sets from all objects and styles ([G:91799292](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91799292-41A2-4D13-92A1-2A10BA1EDDCC)).
- Changing a manual property's data type resets existing data to the default ([G:1EE615FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1EE615FE-74A9-435A-B129-CEE34C148015)).
- Copying into a drawing with a same-name property set: the target's set wins; source manual values it lacks are lost ([G:6A74241E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6A74241E-8972-4920-934D-2CB1C7E6EF67)).
- Overwriting a PSD: manual values lost, schedule columns flagged invalid ([G:C7BD8A5D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C7BD8A5D-899E-4166-BC53-768C9AD2F2DE)).
- Edits to PSDs, data formats and table styles through RefEdit revert on save ([G:C3C3288D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C3C3288D-E40C-4B7A-9DE0-655DA2C1583E), [G:2ADC3FF1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2ADC3FF1-1D50-4357-9EBE-AD863A53970E)).
- One-way actions: Convert to Table ([G:8DBD8501](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8DBD8501-D675-4424-AF78-E4ABEC2D7996)), Convert Field to Text ([G:76C68393](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-76C68393-2FC7-4203-862B-14C849E6BD4D)), exploding a section or elevation ([G:699D2679](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-699D2679-BC8C-4DE5-ADCB-D5554CA1BA33), [G:012EF996](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-012EF996-078C-404E-9940-26B56EADF4DA)).

Wrong-looking output: cause
- ? in cells: property set not attached or removed; it is the data format's Undefined text ([G:269E4649](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-269E4649-ABFE-40FC-869B-E88137ADA4E5), [G:1AF042B7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1AF042B7-78D4-442B-A5CF-1D70D368C909)).
- INVALID column: property deleted from its PSD ([G:995DFFAB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-995DFFAB-4E35-49F5-8B47-91FF25EFC03A)).
- Blank cells you cannot select: manual property with no default ([G:917F2C59](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-917F2C59-1EB3-4721-A781-87DAC41E38DB)).
- Quantity column not grouping: one cell differs, such as numbers or remarks ([G:C636731B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C636731B-8264-43A6-A162-0198A2585253)).
- Graphic property blank: block not in this drawing, or annotative ([G:16445784](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-16445784-6C46-4B80-A4A7-49BF45E85E5B)).
- Formula wrong: property names typed instead of inserted; formatted text substituted into math; RESULT missing in function-style code; a used PSD not attached ([G:0B4CB2DA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0B4CB2DA-BE4F-469E-B933-ADB4068A82A5), [G:FDEC75A1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FDEC75A1-1B28-404D-A488-27E88DB02E1E)).
- Objects missing after a classification filter: their classification is Unspecified ([G:64209805](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-64209805-5EA4-4088-9D51-03E474E23798)).
- Objects missing from a section: frozen or off layers, hidden objects, or a legacy drawing that auto-excludes new objects ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618), [G:91CE3B2C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-91CE3B2C-EBB5-4CDF-865D-37D2223C3098), [G:D17AE7B3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D17AE7B3-0D04-4A62-A70D-409A3E1F91AA)).
- 2D section invisible in Plan view: Plan display set has "Section AEC Objects by Display Range defined in Display Configuration" checked ([G:3FE52AE3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3FE52AE3-B330-4EE5-9735-996E2A390618)).
- Double hatching in a 2D section: Shrinkwrap Hatch and Section Hatch both on ([G:B5F147D7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B5F147D7-A155-41A3-A0BE-51F548B81B75)).
- Live section objects look deleted: the material's Sectioned Body and Sectioned Boundary are off ([G:D8C8175B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8C8175B-7BA7-45D1-B788-5D9D37E953D8)).
- Callout fields show "?": view not placed on a sheet. Raw field names: Callout Only symbol ([G:BFCD066E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BFCD066E-4C43-4F42-A00F-6F3C31FFEFB4), [G:704295C4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-704295C4-41A7-44C7-AB43-2295EA2FBEDB)).
- View missing from a sheet: it came through an overlay reference ([G:052CBAD9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-052CBAD9-1039-4A77-B2B8-03379634E6DC), [G:4BEE1C40](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BEE1C40-14D6-4F2D-A715-AC023E3DAC5D)).
- Copied tag reports the wrong object: it is still anchored to the original; use Tag tab > Anchor panel > Set ([G:EAD45174](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EAD45174-FDBF-439D-B97E-D2375FCFAB41)).

Performance drags
- Update automatically on big tables ([G:3E451D9B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3E451D9B-9D08-4BB5-BA68-CB6F339A82FA)); Out-of-Date Marker on ([G:A078D3E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A078D3E9-82C0-4380-935D-5B65C1302238), [G:D8728D90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8728D90-90D2-4E6D-A021-411C6E02F5AA)); many object types in one table style ([G:4EDBEA36](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4EDBEA36-E61F-4922-8AD8-66F215AFEAA6)).
- AECENABLESECTIONCLEANUP = ON ([G:1F32A976](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1F32A976-C9F7-4ECF-A631-13D4AC39FC4A)); Refresh on Open = Yes on many results ([G:DC846586](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DC846586-489E-4BCE-ACDE-8862AD8A7AF5)).
- Auto-attach on while attaching large xrefs ([G:03030D7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-03030D7C-1008-4A1C-8C72-5ACA70D75AAE)); Batch Refresh of a whole large project ([G:E8108182](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E8108182-5409-4B7E-AE28-541CDE7F8D6A)).

Conflicts between sources (unresolved; check the drawing)
- Out-of-Date Marker default: "appears by default" ([G:D8728D90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8728D90-90D2-4E6D-A021-411C6E02F5AA)) vs "turned off by default" ([G:A078D3E9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A078D3E9-82C0-4380-935D-5B65C1302238)).
- Lower extension 1 ft below the XY plane: stated for model extents ON on the elevation page ([G:8BDA1915](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8BDA1915-B3BE-4A99-8A80-200B485067E4)) and for model extents OFF on the section page ([G:34A85106](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-34A85106-2726-4126-9BB6-7AF6B5097583)).
- MEP schedule refresh: data follow part changes ([G:73091186](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73091186-11D6-4773-B1F8-F22C16AAAD73)) vs a line through the table until Update ([G:7E4D1FE0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E4D1FE0-8558-4A7B-85CC-A9DB239AFB63)).

Not documented in these sources (do not assume)
- Prompt strings for SCHEDULEADD; exact prompt text of PROPERTYSETDEFMERGE (only the answers are given).
- Syntax of BLDGSECTIONLINE, VERTICALSECTION, BLDGSECTIONLINEGENERATE, BLDGSECTIONUPDATE, 2DSECTIONEDITLIVE.
- Values of AECPSDVISIBILITY.
- Typed command names for Style Manager, Display Manager, Elevation Line, Generate Elevation, Hidden Line Projection and Batch Refresh.
- Any hyphen (command-line) form for schedule table styles, tags, display themes, sections, elevations or callouts.
- COM: creating schedule tables (`AddCustomObject("AecScheduleTable")`) and writing property set values were NOT tested; reading PSDs and property sets was VERIFIED.
