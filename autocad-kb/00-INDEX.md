# AutoCAD MEP 2027 knowledge base

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

Reference notes on AutoCAD MEP 2027, condensed from Autodesk's own documentation, plus notes from live tests on a test PC. Every fact in the sections cites its source page.

Citations: G:xxxxxxxx links open the Autodesk help page with that GUID; KB: links open the Autodesk support article, summarized here in our own words. Unlinked codes are plain references.

Not affiliated with or endorsed by Autodesk. Autodesk, AutoCAD and AutoCAD MEP are trademarks of Autodesk, Inc.

## How to use it
1. Find the section below and read the part you need.
2. Click the citation to open the Autodesk page and confirm a fact before relying on it for a deliverable. Docs describe dialogs; scripts still need a live test.

## Sections
Tags: [AUTO] works from a script or the command line, [GUI] dialog, palette or grip only, [VERIFIED] tested live on a test PC, (inference) the writer's conclusion, not stated in a source.

| File | What |
|---|---|
| `01 - MEP Foundations and Drawing Essentials.md` | Connectors, domains, systems, system groups, routing preferences, catalogs; profiles, templates, workspaces, Options tabs, layout rules |
| `02 - Piping.md` | Tested script recipe for pipe, pipe read/edit over COM, routing preferences, system definitions, connecting, slope, sizing, flex pipe, display |
| `03 - HVAC Duct.md` | Duct systems and routing, fittings, takeoffs, air terminals and flows, duct sizing, display |
| `04 - Plumbing, Radiant Heating and Schematics.md` | Pipe vs plumbing lines vs schematic lines, fixture units, supply and sanitary sizing, radiant heating |
| `05 - Electrical.md` | Devices, panels, circuits, the .epd database, wires, conduit, cable tray, panel schedules |
| `06 - Parts, Catalogs, MvParts and Content Builder.md` | Catalog files on disk, MvParts, catalog commands, Catalog Editor, Content Builder |
| `07 - Styles, Display System and Layers.md` | Display representations, sets and configurations, 1-line and 2-line, rise/drop, layer keys and standards |
| `08 - Annotation, Tags, Labels and Fields.md` | Tags, labels, flow arrows, elevation labels, keynotes, AEC dimensions, fields |
| `09 - Schedules, Property Sets, Sections and Elevations.md` | Property set definitions, schedule tables, display themes, sections, elevations, callouts |
| `10 - Projects, Standards and Interoperability.md` | Project Navigator, constructs, views, sheets, project standards, Content Browser, IFC and export |
| `11 - Spaces, Zones and Analysis.md` | Spaces, zones, boundaries, gbXML export and load round trip, duct sizing from terminal flows |
| `12 - Automation I - COM and AutoLISP.md` | Driving AutoCAD from Python over COM, SendCommand, the MEP COM API, ActiveX object model, AutoLISP |
| `13 - Automation II - Scripts, Plug-ins, .NET.md` | .scr scripts, startup switches, trusted paths and SECURELOAD, .NET 10 plug-ins, the Core Console |
| `14 - Output I - Sheet Sets, Text, Tables, Blocks.md` | Text and fonts, mtext codes, multileaders, tables, blocks and attributes, sheet sets, eTransmit |
| `15 - Output II - Dimensions, Plotting, Publishing, Xrefs.md` | Layouts, viewports, dimensions, plot styles, PDF and PUBLISH, data extraction, xrefs, PDF underlays |

When the sections were built, every citation was checked against the Autodesk page it names, and every command and variable name a cited line uses was found in Autodesk's own pages.

## Lookup tables (`index/`)
| File | What |
|---|---|
| [`MEP-and-AEC-commands.md`](index/MEP-and-AEC-commands.md) | 384 MEP and AEC command names, with the help pages that document them |
| [`Support-articles-by-cases.md`](index/Support-articles-by-cases.md) | 514 Autodesk support articles for AutoCAD MEP, most-cited first |

For core AutoCAD commands, system variables, AutoLISP functions and the ActiveX reference, use the Autodesk help at [help.autodesk.com](https://help.autodesk.com).

## Test notes (`_verified/`)
Live tests on a test PC with their scripts: the MEP COM API, Core Console -PDFIMPORT and raster plotting, a .NET plug-in build.

## Sources
- Autodesk 2027 help at [help.autodesk.com](https://help.autodesk.com): AutoCAD MEP, AutoCAD Architecture, AutoCAD core, ActiveX, AutoLISP, Customization, DXF, the .NET developer and migration guides, and What's New.
- Autodesk support articles for AutoCAD MEP at [autodesk.com/support](https://www.autodesk.com/support). These are not covered by the CC license; the sections summarize them in their own words and link to them.
- For a few automation facts, the MEP COM API reference installed with the product and the installed COM type libraries.

## Coverage and gaps
- Fully read and condensed: all AutoCAD MEP 2027 help (1,037 pages), all 514 MEP support articles, the AEC platform chapters MEP shares (display system, styles, layers, project navigator, annotation, schedules, property sets, sections, elevations, spaces, interoperability), the ActiveX and AutoLISP developer guides, the customization guide (scripts, loading, plug-ins, plotters), the .NET developer and migration guides, and the AutoCAD output chapters (sheet sets, eTransmit, text, tables, blocks, dimensions, data extraction, layouts, plotting, publishing, xrefs, underlays).
- Used for lookup but not condensed into the sections: the AutoCAD command and system variable reference (use the Autodesk help pages), the full ActiveX and AutoLISP references, AEC architectural objects (walls, doors, stairs), the managed .NET class references, AutoLISP tutorials, DXF reference.
- Not covered: Autodesk University classes, forums and blogs (secondary sources), ObjectARX C++ reference, help for releases before 2027 (except What's New 2024 to 2026).
