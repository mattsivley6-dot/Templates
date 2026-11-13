# 15 - AutoCAD Output II: Dimensions, Data Extraction, Layouts and Viewports, Plotting, Publishing to PDF, Xrefs and Underlays

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See LICENSE.md.

Citations: G:XXXXXXXX links to the Autodesk help page whose GUID starts with those 8 characters. Autodesk and AutoCAD are trademarks of Autodesk, Inc.; this file is not affiliated with or endorsed by Autodesk.

This section turns a model into a sheet set: layouts and page setups, layout viewports and their scale, dimensions and dimension chains, plot styles and plot settings, PDF output and PUBLISH, takeoff data extraction, and owner backgrounds brought in as xrefs or as PDF, DWF or DGN underlays.
It is written for runs with no hands on the mouse: .scr files in accoreconsole, SendCommand over COM, and DXF/DWG files built with ezdxf.
For each command it gives the command-line form when one is documented and names what blocks a script.
The Autodesk pages behind this section do NOT print the -PLOT, -PUBLISH, -XREF or -PDFATTACH prompt lists. That gap is stated first (15.1) so no one builds on a guess.

Contents
- 15.1 Read first: source coverage, field facts, labels
- 15.2 What stops an unattended run
- 15.3 Layouts, page setups, layout templates
- 15.4 Plot settings field by field (what -PLOT and -PAGESETUP answers must cover)
- 15.5 Plot styles, lineweights, transparency, screening
- 15.6 Shaded viewports in plots
- 15.7 PDF output and PUBLISH
- 15.8 Plotters, PC3 and PMP files, plot to file, plot stamp
- 15.9 Layout viewports: create, scale, lock, layers, clip, rotate, MVSETUP
- 15.10 Model space plotting and scale factors
- 15.11 Dimensions: associativity and scale across model and paper space
- 15.12 Dimension chains: continue, baseline, spacing, ordinate
- 15.13 Dimension style variables and DIMOVERRIDE
- 15.14 Dimension edits: breaks, jogs, text, center marks
- 15.15 Blocks that feed sheets and takeoffs
- 15.16 Data extraction for takeoffs
- 15.17 Xrefs: attach, overlay, paths, loading, logging
- 15.18 Xrefs: bind, XBIND, in-place edit, clip, missing and circular
- 15.19 Underlays for owner backgrounds (PDF, DWF, DGN)
- 15.20 Import and export translators (DGN, IGES, STEP, STL, 3D DWF)
- 15.21 ezdxf notes (inference)
- 15.22 System variable quick list
- 15.23 Block Editor, dynamic blocks and wildcards (reference)

## 15.1 Read first

Labels used in this section
- [AUTO] = scriptable, or matters to a scripted run.
- [GUI] = dialog, palette, ribbon, grip or mouse only. Blocks a script as documented.
- (inference) = the writer's reasoning, not stated by a source.
- (field) = seen in hands-on field tests. Not from an Autodesk page.

Not in these sources (each one was searched for)
- No prompt lists for -PLOT, -PAGESETUP, PSETUPIN, -PUBLISH, MVIEW, LAYOUT (except Save As), -INSERT, -DIMSTYLE, -XREF, XATTACH, -XBIND, -XCLIP, -ATTACH, -PDFATTACH, -DWFATTACH. Some appear only as names on index pages: -PAGESETUP and PSETUPIN ([G:99AABBCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99AABBCD-5908-40AD-AF7B-0C3D5594B8F5), [G:A361F313](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A361F313-E1EB-400C-81B2-6B9AA2C0DDB7)), -ATTACH ([G:5F10E306](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F10E306-BC6C-49C4-B9C4-5F05EEC72146)). -PLOT, -PUBLISH and -PDFATTACH are not named at all; PLOT and PUBLISH appear only as dialogs ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE), [G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E)).
- No DSD file keys, no PDF PC3 file names, no BACKGROUNDPLOT value table, no FILEDIA, CMDDIA or CMDECHO text, no accoreconsole text, no ezdxf or DXF group codes.
- No PDFIMPORT page. [G:5F10E306](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F10E306-BC6C-49C4-B9C4-5F05EEC72146) (Commands for Working with Underlays) lists -ATTACH and -DGNBIND as the only hyphen commands, and lists no PDFIMPORT.
- No command-line form for DATAEXTRACTION.
- Get these from the command reference pages, another section, or a live test.

Field facts (from field tests; nothing in these sources contradicts them)
- accoreconsole has no PDFIMPORT command. (field)
- -PDFATTACH crashed accoreconsole. (field) The sources do not explain the crash.
- -PLOT answer sequences differ between a sheet with shaded viewports and a 2D-only sheet. Keep a separate, tested answer list for each sheet type. (field) (inference: the extra answers come from the shaded viewport settings in 15.6.)
- A layout name with spaces breaks the -PLOT answers in a script. Name layouts with no spaces, for example M-101 or M101-LEVEL1. (field) (inference: in a .scr file a space acts like Enter, so the name is cut at the space.)

## 15.2 What stops an unattended run

Each item is a dialog or prompt that waits for a person. Plan around it before the run.

| Stop point | When it shows | How to avoid it | Cite |
|---|---|---|---|
| Update PC3 File With New Printer | PLOT or PAGESETUP, when the layout's PC3 names a missing or invalid device | Use PC3 files that exist on the plotting machine; fix the layout's device first | [G:BA2B77DF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BA2B77DF-0D7A-41C1-9FDC-4671A313887A) |
| Changes to a Printer Configuration File | after a PC3 is edited from the Plot or Page Setup dialog | Build PC3 files beforehand; never edit them during a plot | [G:CA1F0490](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA1F0490-BF3A-4E1E-85A9-E0E735CF11A2), [G:44AA0F62](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-44AA0F62-909B-451E-A23B-8F41B0194757) |
| Paper size warning | the device does not list the layout's saved paper size | Use a size the PC3 lists | [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE), [G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379) |
| Browse for Plot File | Plot to File from the Plot dialog | (inference) give the file name in the command-line answers | [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE) |
| PDF opens in a viewer | PDF Options "Show results in viewer" is on | Turn it off | [G:BE373C38](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE373C38-678A-4AF9-96AB-4195FFD6F806) |
| Page Setup dialog on a new layout | "Display when creating a new layout" is on | Turn it off (Options > Display > Show Page Setup Dialog for New Layouts) | [G:B06031A0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B06031A0-EF7E-4287-8E34-ABDCC40FF8C4) |
| Data Extraction - Outdated Table | DXEVAL trigger (OPEN, SAVE, PLOT, PUBLISH, ETRANSMIT) in a drawing with an extraction table | Set DXEVAL for the run, or update tables first (inference) | [G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E) |
| Missing xref task dialog | on open, when xrefs are not found | Fix paths first; ship every xref with the set | [G:1F7D6EA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1F7D6EA1-9AA8-4D33-819F-09750C295D6B) |
| Circular reference warning | attaching an xref chain that loops back | Do not build loops | [G:1F7D6EA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1F7D6EA1-9AA8-4D33-819F-09750C295D6B) |
| Underlay password | on attach and on EVERY open, once per protected PDF, DWF or DWFx | Do not use protected files | [G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E) |
| URL login | xref attached from a web address that needs a login | Use local copies | [G:D91CFD9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D91CFD9D-44EC-408D-8E60-8C826216EA61) |
| Substitute DWF Name | two DWF underlays with the same name | Unique names | [G:FAB9E38A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FAB9E38A-A459-4AD6-8F57-CE635E09E519) |
| DWF Prompt for Name | multi-sheet DWF publish with that option on | Turn it off | [G:9A17A2C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A17A2C7-F594-4854-ADC8-61CFAC575F8B) |
| CONVERTPSTYLES, CONVERTCTB | alert box plus Select File dialog | Run once by hand, not in a batch | [G:922028F0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-922028F0-C2E2-4203-96D7-C7BCB0D4D9C2) |
| IMPORT of 3D models | runs in the background; result is inserted by clicking a bubble or the status bar icon | No headless route documented (inference) | [G:F5CEE149](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F5CEE149-E2CA-481A-97DE-EB85FE62697D) |
| DGN import or export overwrite | "Prompt to Overwrite" chosen for reference files | Pick Overwrite without Prompting or Do Not Overwrite | [G:2A82AA09](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2A82AA09-4C1A-4737-910A-064D872F12B5), [G:E2FED62A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E2FED62A-14A5-4FC9-8485-5C2353282608) |
| CATIA V4 model chooser | a V4 file holds several models | One model per file | [G:2A5B5616](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2A5B5616-15B6-4B72-876B-20501812054C) |

Dialog-only commands in these sources [GUI]: PLOT, PAGESETUP, PUBLISH, DIMSTYLE, TOLERANCE, DIMINSPECT, DATAEXTRACTION, DBCONNECT, BLOCK, WBLOCK, INSERT, BEDIT, PURGE, XBIND, RENAME, REFEDIT (when the pick hits nested references), XOPEN (nested), EXPORTLAYOUT, VPORTS, UNITS, SCALELISTEDIT, LAYOUTWIZARD, PLOTSTAMP, PLOTTERMANAGER, STYLESMANAGER, DGNIMPORT, DGNEXPORT, DGNMAPPING, 3DSIN.
Use the hyphen form or a system variable where one exists, and test it first.

## 15.3 Layouts, page setups, layout templates

Layout basics
- A layout is one sheet: border and title block, layout viewports, notes, dimensions, tables. A DWG can hold as many layouts as needed. ([G:2DB9EB8C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DB9EB8C-767C-4C91-B0A3-FFFEC4C5863A), [G:93E88E2A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93E88E2A-3BA8-40C1-8BF5-9A50B716EB34))
- Paper space unit = a real inch or mm on the sheet, set by the page setup. Model space is drawn 1:1. ([G:990538B6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-990538B6-DDA1-4190-BCC0-BB5BA94C9879))
- Each layout stores its own page setup: device, paper size, orientation, plot area, scale, offset, plot style table, shaded viewport options, plot options. ([G:2DB9EB8C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DB9EB8C-767C-4C91-B0A3-FFFEC4C5863A), [G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379))
- [AUTO] The FIRST time a layout is displayed it is initialized: it gets a default page setup named with asterisks (*model*, *layout1*, *layout2*), one layout viewport, and the dashed printable-area line. ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0), [G:2DB9EB8C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DB9EB8C-767C-4C91-B0A3-FFFEC4C5863A)) (inference: a script that builds layouts should make each one current once before page setup or publish steps.)
- [AUTO] A layout publishes only when initialized: paper size set in its page setup and not 0 x 0. An uninitialized model layout shows "Uninitialized" in the Publish sheet list; a page setup override can still plot it. ([G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E))
- Default page setups (asterisk names) cannot be imported into other drawings until saved under a real name. ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0))
- Layout commands: LAYOUT (add, copy, Save As template), LAYOUTWIZARD [GUI], MODEL, MSPACE, PSPACE, EXPORTLAYOUT, VPORTS, MVIEW, VPCLIP, VPLAYER, VPMAX, VPMIN. Layout sysvars: CLAYOUT, CTAB, CVPORT, TILEMODE, LAYOUTTAB, MAXACTVP. ([G:A361F313](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A361F313-E1EB-400C-81B2-6B9AA2C0DDB7))
- Tabs hidden: set LAYOUTTAB to 1 [AUTO]. ([G:C5BB2604](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C5BB2604-AD99-4F0C-BEFB-DA77C7D036A3)) Options > Display > "Display Layout and Models Tabs" is the dialog switch. ([G:A8C1E8DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A8C1E8DA-56FA-4957-8FE3-7E54DEF7CC83))
- Add layouts by the LAYOUT command, right-click a layout tab, the Create Layout wizard, or DesignCenter. ([G:93E88E2A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93E88E2A-3BA8-40C1-8BF5-9A50B716EB34))

Named page setups
- PAGESETUP opens Page Setup Manager [GUI]. -PAGESETUP is listed as its own command ([G:99AABBCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99AABBCD-5908-40AD-AF7B-0C3D5594B8F5)); its prompts are not in these sources. PSETUPIN is listed for importing page setups ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0), [G:A361F313](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A361F313-E1EB-400C-81B2-6B9AA2C0DDB7)); prompts not given. [AUTO names]
- Page Setup Manager: New, Modify, Import, Set Current; right-click a setup for Set Current, Rename, Delete. Details pane shows Device Name, Plotter, Plot Size, Where, Description. ([G:B06031A0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B06031A0-EF7E-4287-8E34-ABDCC40FF8C4))
- New Page Setup "Start With": <None>; <Default Output Device> (from Options > Plot and Publish); <Previous Plot> (last plot job); or any named setup in the drawing. OK opens the Page Setup dialog. ([G:B72EDE56](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B72EDE56-D3F9-4C6D-8A41-5E5BF3A29653))
- A layout using a named setup lists as *Layout 1 (Setup Name)*. The current layout itself cannot be set current as a page setup. ([G:B06031A0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B06031A0-EF7E-4287-8E34-ABDCC40FF8C4))
- Import: Page Setup Manager > Import > pick DWG or DWT > Import Page Setups dialog. Model-space and layout setups both import, but each is listed only if the same kind of tab (Model or layout) was current when the Manager opened. Name clash: redefine the existing one or cancel. ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0), [G:C3DE7352](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C3DE7352-1DE5-4F82-A5FE-5884C27B0473))
- Plot-time override: Plot dialog > Add saves the current values as a named setup (Add Page Setup dialog). "Apply to Layout" writes the dialog values into the layout. ([G:50883F6E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-50883F6E-A9F2-4F8F-8CAC-BFF590ACE98D), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
- Model-space page setups apply only to the Model tab or model sheets; paper-space setups only to layouts. ([G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E), [G:FB6BDFE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FB6BDFE4-9F8F-4028-AB27-2741A7C94152))
- A page setup cannot be applied to a whole sheet set after the set is created. From Sheet Set Manager, the Manager lists only named setups in the page setup overrides file (a .dwt) whose Plot Area is Layout or Extents; they apply temporarily to a PUBLISH run. ([G:B06031A0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B06031A0-EF7E-4287-8E34-ABDCC40FF8C4), [G:C3DE7352](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C3DE7352-1DE5-4F82-A5FE-5884C27B0473))
- Autodesk's example setup names: NoScaling (1:1, E-size), Scale 1 to 2 (C-size), Draft, Final, Fit-to-Paper (A-size). ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0))

Layout templates
- A layout template is a layout imported from a DWG or DWT. It brings the page setup and the paper-space objects, viewports included. No model-space objects come in. Blocks, layers and dimension styles used by the layout travel with it. ([G:26B8A9E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-26B8A9E5-02AC-4BFF-9803-982CC9FD5BFB))
- [AUTO] Save one: `LAYOUT` > `sa` > type the layout name > Create Drawing File dialog [GUI] > file name, Files of Type = Drawing Template File (*.dwt) > Save. The file goes to the template folder set on the Options Files tab. ([G:1B4DFAA5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B4DFAA5-4E02-439A-B2AF-A5EA45794F40), [G:26B8A9E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-26B8A9E5-02AC-4BFF-9803-982CC9FD5BFB))
- LAYOUT > Save As is the recommended way because unused definition-table items are left out. A layout pulled from a drawing not made that way also brings definitions used elsewhere in that drawing; PURGE afterward. ([G:26B8A9E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-26B8A9E5-02AC-4BFF-9803-982CC9FD5BFB))
- LAYOUTWIZARD builds a layout from scratch or a template using the configured device's paper sizes and stock title blocks [GUI]. ([G:E6E49EF2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E6E49EF2-421F-4592-B0E6-575939214273))

## 15.4 Plot settings field by field (what -PLOT and -PAGESETUP answers must cover)

The prompt ORDER of -PLOT and -PAGESETUP is not in these sources. Below is every setting the Page Setup dialog ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379)) and Plot dialog ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE)) hold, which is what each answer list has to decide.

1. Page setup name. Plot dialog Name list; Add saves current values as a new named setup. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
2. Printer/plotter. A PC3 file or a Windows system printer (the icon tells which). Properties opens the PC3 editor (avoid in a run, see 15.2). The PDF Options button shows only for a PC3 that makes PDF. Plotter, Where and Description are read from the device. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE), [G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379))
3. Paper size. Sizes come from the chosen device. The size chosen in the page setup is saved with the layout and OVERRIDES the PC3 default. If the device lacks the layout's size, a warning appears and you pick the device default or a custom size. Raster outputs (BMP, TIFF) are sized in pixels. ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
4. Plot area. ([G:627BD290](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-627BD290-8794-4835-A52E-F3902EBC8E7D), [G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
   - Layout: everything inside the printable area, origin at layout 0,0. Layout tabs only.
   - Limits: Model tab only, the grid limits; acts like Extents if the current viewport is not a plan view.
   - Extents: everything in the current space; a regen may run first.
   - Display: the current viewport (Model tab) or current paper space view.
   - View: a view saved with VIEW; unavailable if the drawing has none.
   - Window: two corners, picked or typed as coordinates.
   (inference: these six are likely the -PLOT plot area keywords; not confirmed here.)
5. Plot offset. X and Y in paper inches or mm, positive or negative. Measured from the lower-left of the printable area or from the paper edge, per Options > Plot and Publish > "Specify Plot Offset Relative To" (shown in parentheses in the group title). PLOTOFFSET is listed in the index ([G:99AABBCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99AABBCD-5908-40AD-AF7B-0C3D5594B8F5)) (inference: it holds that choice; verify). Offsets can CLIP the plot. Center the Plot computes X and Y, and is NOT available when Plot Area = Layout. ([G:88080625](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-88080625-C6E0-4FC3-A8FD-226D10DA780D), [G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
6. Plot scale. ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379), [G:44C99121](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-44C99121-7541-4B2B-916A-AE59500AA9E0), [G:89604826](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-89604826-0B55-4994-8214-1CA93FA66985), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
   - Plot Area = Layout plots at 1:1 whatever the scale box says, and Fit to Paper is unavailable.
   - Default: 1:1 for a layout, Fit to Paper on the Model tab.
   - Custom scale = N inches (or mm) = M drawing units. Typing a custom value selects Custom even if it equals a listed scale. 1:12 and 2:24 plot the same.
   - The unit box (Inch(es)=, mm=, Pixel(s)=) follows the paper size and resets whenever the paper size changes. Pixels only for raster output.
   - Fit to Paper shows the computed factor in the custom boxes. A perspective view plotted from model space is always fit to paper, even if a scale is typed.
   - The scale also governs coordinate and distance values on a paper-space layout.
7. Scale lineweights. Scales widths with the plot scale. Layouts only, not the Model tab. Normally lineweights plot at their set width whatever the scale. ([G:E31DF955](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E31DF955-8BCD-4D91-AE38-A75CC42C85DF), [G:60B37EAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60B37EAD-BBEA-46C0-AA76-137625B93ED5), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
8. Plot style table (pen assignments). A table name, or None. See 15.5.
9. Shaded viewport options. Shade Plot, Quality, DPI. See 15.6.
10. Plot options. Plot in Background (system variable BACKGROUNDPLOT), Plot Object Lineweights, Plot Transparency, Plot with Plot Styles, Plot Paperspace Last, Hide Paperspace Objects, Plot Stamp On, Save Changes to Layout. See 15.5, 15.7, 15.8. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
11. Drawing orientation. Portrait (short edge on top), Landscape (long edge on top), Plot Upside-Down (adds 180 degrees). PLOTROTMODE also affects orientation. ([G:E22E8339](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E22E8339-34FA-41D2-8B4D-9FC41D59B6BB), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
12. Plot to file and the file name. Default folder: Options > Plot and Publish > Default Location for Plot-to-File Operations. Number of Copies is not available when plotting to file. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))

Rules that save runs
- [AUTO] Use Plot Area = Layout for sheets drawn to paper size: it forces 1:1 and avoids scale questions. ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379), [G:7AE63760](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7AE63760-2516-4D91-9C9A-E157DEBC7849))
- [AUTO] Keep paper size in the page setup and pick a size the PC3 really lists; otherwise the paper size warning stops the run. ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379))
- Preview runs PREVIEW [GUI]; ESC, Enter or right-click > Exit leaves it. Shade plot and Hide Paperspace Objects effects show only in preview, not in the layout. ([G:6F994ABE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F994ABE-EA9D-4444-BF77-4E60D1EB9043), [G:5C44F977](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5C44F977-EE00-44EE-A4E1-5A3AC10886A6))
- Plot settings are kept in the page setup, so a fixed named setup per sheet type is the reusable unit ([G:9405CF03](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9405CF03-51FA-419F-B7C7-91736803B6B4), [G:46712A7A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-46712A7A-526B-4292-B0AC-3E6C6F54786A)). (inference: put device, paper, area, scale and style table in named setups and let -PLOT or -PUBLISH reuse them, rather than answering every setting per run.)

## 15.5 Plot styles, lineweights, transparency, screening

Two table types; one type per drawing
- CTB (color-dependent): object color picks the style, so all red objects plot alike. Styles can be edited but not added or deleted. Count: 255 styles per [G:133D3E2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-133D3E2C-C016-4543-A4A9-47B1D21C742D) and [G:EA164540](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA164540-48C9-4C85-8EDB-55975D89F22A); [G:2FD01085](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2FD01085-DDD8-49D2-A910-E63EA45A7FED) says 256, one per color. ([G:2FD01085](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2FD01085-DDD8-49D2-A910-E63EA45A7FED))
- STB (named): any number of styles; assign them to objects or layers; same-color objects can plot differently. ([G:2FD01085](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2FD01085-DDD8-49D2-A910-E63EA45A7FED))
- A drawing uses one type at a time. With CTB you cannot assign styles to objects; change object color instead. ([G:2DB9EB8C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DB9EB8C-767C-4C91-B0A3-FFFEC4C5863A))
- A CTB can be assigned to a layout only if the drawing is set to color-dependent styles. ([G:F6DF548E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F6DF548E-DF71-45F7-8DC5-A1EAD73998B1))
- New drawings: Options > Plot and Publish > Plot Style Table Settings > "Use Color-dependent Plot Styles" or "Use Named Plot Styles", plus Default Style Table [GUI]. Existing drawings are not changed. ([G:7BDAFFE3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7BDAFFE3-EFCF-4A21-A9DE-F7D2D0AE043E)) PSTYLEPOLICY and PSTYLEMODE are listed in the plot settings index ([G:99AABBCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99AABBCD-5908-40AD-AF7B-0C3D5594B8F5)) (inference: PSTYLEPOLICY carries the new-drawing choice; verify on its page).

Shipped CTB tables (Plot Styles folder) ([G:F6DF548E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F6DF548E-DF71-45F7-8DC5-A1EAD73998B1))
- acad.ctb (default), monochrome.ctb (all colors plot black), grayscale.ctb, fillPatterns.ctb (first 9 colors use the first 9 fill patterns), screening 100%.ctb, screening 75%.ctb, screening 50%.ctb, screening 25%.ctb. "None" = no table.
- Folder (Windows): `<drive>:\Users\<user name>\AppData\Roaming\Autodesk\<product version>\<release number>\<language>\plotters\Plot Styles`. Search folders can be changed in OPTIONS. STYLESMANAGER opens it. ([G:2FD01085](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2FD01085-DDD8-49D2-A910-E63EA45A7FED), [G:F2D127CB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F2D127CB-0261-48C7-AD6D-259CAB5B7EF9))

Assigning tables
- Each layout can have its own table; it controls model space AND paper space objects in that layout. ([G:5E926DA6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5E926DA6-8CEB-4270-9C9D-6F7F61E84C85), [G:39A58222](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-39A58222-B3FC-4E74-9E1C-59F01250B143))
- Page Setup > Plot Style Table (Pen Assignments): pick a table, New (Add Plot Style Table wizard), Edit (Plot Style Table Editor), Display Plot Styles (show effect on screen; layouts only; run `regen` if it was already ticked). ([G:961E5EA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-961E5EA1-8F21-4B40-A887-CA10E5B2CBCB), [G:4B582E82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4B582E82-6E60-4D31-AB7C-14B2F74D2BA4))
- Assigning on the Model tab raises a Yes/No question: this tab only, or all layouts [GUI]. ([G:4B582E82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4B582E82-6E60-4D31-AB7C-14B2F74D2BA4))
- Inserting an xref also brings in its plot style tables. ([G:5E926DA6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5E926DA6-8CEB-4270-9C9D-6F7F61E84C85))
- Commands for these settings: PLOTSTYLE (Current Plot Style dialog), STYLESMANAGER, CONVERTPSTYLES, CONVERTCTB; sysvars CPLOTSTYLE and DEFPLSTYLE are tagged with the current-style topic, values not given. ([G:922028F0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-922028F0-C2E2-4203-96D7-C7BCB0D4D9C2), [G:928B01A3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-928B01A3-E7F7-43E8-AD7E-EB2A5F162127), [G:929FE8EC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-929FE8EC-EFE3-43BB-A79F-4FF509A91D5A))

Named style rules (STB)
- The first style is NORMAL = the object's own properties. It cannot be edited, renamed or deleted. Style names up to 255 characters. ([G:EA164540](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA164540-48C9-4C85-8EDB-55975D89F22A))
- Object or layer plot styles exist only with named tables. Object style BYLAYER inherits the layer's style. ([G:77881096](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-77881096-24A3-42A9-A85F-A1B30D238070), [G:39A58222](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-39A58222-B3FC-4E74-9E1C-59F01250B143))
- A style not in the layout's table is "missing": objects using it plot with default properties. Example: table Style1 has A and B; objects set to C plot with defaults. ([G:7446370A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7446370A-5ECB-4CC0-8D0D-A8C0BDD9D5D8))
- Deleting a style: objects keep the name but plot as Normal. ([G:EA164540](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA164540-48C9-4C85-8EDB-55975D89F22A))
- A table carrying an AutoCAD Release 14 color mapping table cannot add, delete, copy or rename styles. Delete the mapping table on the editor General tab first; the cost is that pre-2000 drawings can no longer get styles from color. ([G:B15B7EB4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B15B7EB4-B3F3-41A0-8D40-C06C7FDA4E98), [G:EA164540](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA164540-48C9-4C85-8EDB-55975D89F22A))

Converting [AUTO but dialogs]
- CONVERTPSTYLES switches a drawing between color-dependent and named. Alert + Select File dialog. Named to color-dependent loses the style names on objects. Color-dependent to named removes the CTB tables on layouts and attaches named tables. ([G:922028F0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-922028F0-C2E2-4203-96D7-C7BCB0D4D9C2), [G:03433BA8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-03433BA8-BBE5-474D-A56F-7CAD6224F49E))
- CONVERTCTB writes an STB from a CTB (Select File, new name, alert). Rename styles in the new table before use. ([G:922028F0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-922028F0-C2E2-4203-96D7-C7BCB0D4D9C2))
- A CTB can be converted to named; a named table can NOT be converted to color-dependent. [G:2DB9EB8C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DB9EB8C-767C-4C91-B0A3-FFFEC4C5863A) says tables convert either way; [G:03433BA8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-03433BA8-BBE5-474D-A56F-7CAD6224F49E) is the specific rule.

Plot Style Table Editor fields (Form View or Table View) ([G:EA164540](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA164540-48C9-4C85-8EDB-55975D89F22A))
- Color: default Use Object Color; a set color overrides object color at plot time.
- Enable Dithering: usually off (avoids false linetypes in thin lines). Required for screening.
- Convert to Grayscale: only on grayscale-capable devices.
- Use Assigned Pen Number (1 to 32, pen plotters only). Virtual Pen Number (1 to 255): when the device is set for virtual pens, ALL other style settings are ignored.
- Screening: 0 = white, 100 = full intensity.
- Linetype with Adaptive Adjustment: on = completes the pattern; off = keeps linetype scale exact.
- Lineweight (mm), Line End Style, Line Join Style, Fill Style: each overrides the object at plot time. End and join styles apply to lineweights that come from the plot style. ([G:1AA2F7B7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1AA2F7B7-0970-4BD9-A307-08873D586CED))
- Edit Lineweights: 28 lineweights per table; edit values only, no add or delete; 0 = thinnest line the device makes; maximum 100 mm; changing one changes every style that uses it. ([G:5A75B7D7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5A75B7D7-BF01-499B-9DAE-029D0DC91C35), [G:EA164540](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA164540-48C9-4C85-8EDB-55975D89F22A))
- General tab: Description; "Apply Global Scale Factor to Non-ISO Linetypes" + Scale Factor (also scales fill patterns). ([G:9E58C78B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9E58C78B-1D5D-41AB-8B9D-81A6F5C9A399), [G:4E1880AA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E1880AA-8B68-45F5-96DA-6D4AC550D217))
- Changing a style in a table attached to layouts changes every object using it. ([G:56184373](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-56184373-FC19-49A0-9E67-181C4F5C19B7))

Plot options that interact ([G:5C44F977](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5C44F977-EE00-44EE-A4E1-5A3AC10886A6), [G:C82536C0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C82536C0-7460-4D19-B5F9-7C7891968944), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
- Plot with Plot Styles ON also plots lineweights. Plot Object Lineweights can be changed ONLY while Plot with Plot Styles is off. With plot styles off, objects plot with their own properties.
- Plot Transparency: OFF by default for speed. Turn on only for drawings with transparent objects. It applies to wireframe and hidden plots; Realistic, Conceptual and Shaded always plot with transparency. PLOTTRANSPARENCYOVERRIDE can override the check box; by default it follows the page setup and Plot dialog.
- Plot Paperspace Last: plots model space first. Default order is paper space first.
- Hide Paperspace Objects: applies HIDE to paper-space objects in a viewport; layout tab only; seen in preview, not in the layout.
- Lineweights normally print at their set width; Scale Lineweights changes that (15.4).

Screening (faded backgrounds) ([G:FAEE9425](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FAEE9425-37ED-4324-B1C2-48BE042B5154), [G:8D7694B8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8D7694B8-4382-44E9-BB1C-1DB99A648FB0), [G:D73E05F7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D73E05F7-6B93-4C00-990C-E38F3FC643BE))
- Screening 0 to 100 in a plot style (the task steps say 1 to 100). 100 = full ink, 0 = no ink, the object vanishes in that viewport.
- Works only if the device plots color or grayscale AND dithering is on.
- Common practice: set the style's color to black so screening is a percent of black.
- Named tables: give the objects that style. CTB: give the objects the color whose style you screened.
- (inference: a screened style is one way to fade owner background linework on the sheet; underlays have their own Fade setting, 15.19.)

## 15.6 Shaded viewports in plots

Core rules
- Shaded viewport plot options apply to all objects in viewports and in model space. They are saved in the page setup. ([G:9405CF03](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9405CF03-51FA-419F-B7C7-91736803B6B4))
- If you use the Shaded option, plot style tables in the page setup do NOT affect the plot. ([G:9405CF03](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9405CF03-51FA-419F-B7C7-91736803B6B4)) (inference: monochrome.ctb will not turn a shaded 3D iso viewport black and white.)
- Shaded viewport plotting needs a raster-capable device; the page says most modern plotters and printers are. It does not say whether a PDF PC3 counts. ([G:9405CF03](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9405CF03-51FA-419F-B7C7-91736803B6B4))
- Shade Plot and Hide Paperspace Objects effects show in plot preview only, not in the layout. ([G:5C44F977](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5C44F977-EE00-44EE-A4E1-5A3AC10886A6), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))

Where the setting lives [AUTO]
- Model tab: Plot or Page Setup dialog > Shaded Viewport Options > Shade Plot. ([G:37708FB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-37708FB5-CF5E-4E55-8E77-F884687A4131))
- Layout viewport: select the viewport border > Properties > Misc > Shade Plot. Or -VPORTS > Shadeplot. ([G:37708FB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-37708FB5-CF5E-4E55-8E77-F884687A4131), [G:93641503](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93641503-3EA3-4BC3-8E47-A33EAA6CD20A))
- -VPORTS Shadeplot choices: As Displayed, Wireframe, Hidden, Visual Styles (lists every visual style in the drawing, used or not), Render Presets. ([G:93641503](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93641503-3EA3-4BC3-8E47-A33EAA6CD20A))
- Plot dialog Shade Plot list (Model tab): As Displayed, Legacy Wireframe, Legacy Hidden (both use the old SHADEMODE), Conceptual, Hidden, Realistic, Shaded, Shaded with Edges, Shades of Gray, Sketchy, Wireframe, X-ray, Rendered. Any choice but As Displayed forces that look whatever the screen shows. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
- Page Setup dialog list: As Displayed, Wireframe, Hidden, 3D Hidden, 3D Wireframe, Conceptual, Realistic, Rendered. ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379)) The two dialogs print different lists; the Plot dialog page is the longer one.

Quality and DPI ([G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
- Draft: shaded and rendered views plot as wireframe.
- Preview: 1/4 of device resolution, max 150 dpi.
- Normal: 1/2 of device resolution, max 300 dpi.
- Presentation: device resolution, max 600 dpi.
- Maximum: device resolution, no cap.
- Custom: the DPI box value, up to device resolution.

Other
- Hardware acceleration off or without shadow support: 3DCONFIG > Manual Tune > "Emulate unsupported hardware effects in software when plotting". The effects show in the plot or file, not live. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
- PC3 Raster Graphics slider "Raster and Shaded/Rendered Viewports" at None disables raster printing. ([G:025BEBB2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-025BEBB2-EBE4-4966-871D-E91B0811579E)) (inference: check this slider on the PDF PC3 if shaded viewports come out blank.)
- DWF and PDF underlays display ONLY in the 2D Wireframe visual style. ([G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E)) (inference: put owner PDF backgrounds in 2D wireframe viewports; a shaded viewport will not show them.)
- (field) A sheet with shaded viewports needs a different -PLOT answer list than a 2D-only sheet (15.1).

## 15.7 PDF output and PUBLISH

PDF Options dialog ([G:BE373C38](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE373C38-678A-4AF9-96AB-4195FFD6F806)) [GUI; these are the values a script must have preset]
- Opens from the Plot dialog "PDF Options" button (shown only for a PC3 that makes PDF) and from PUBLISH. The page gives no command-line form.
- Show results in viewer: opens the PDF in the default viewer as soon as it is written. Turn it off for unattended runs (inference).
- Quality:
  - Vector quality: resolution of vector graphics and gradients.
  - Raster image quality: resolution of raster images. Cannot exceed vector quality.
  - For a PDF that will be printed, match the printer's resolution. For screen use, pick high (above 2400 dpi). Higher = better, slower, bigger file.
  - Merge control: Lines Overwrite (top line hides bottom) or Lines Merge (colors blend).
- Data:
  - Include layer information: layers can be switched in the viewer.
  - Include hyperlinks: off = links are dropped.
  - Create bookmarks: bookmarks to named views.
  - Capture fonts used in the drawing: embeds TrueType fonts. Never embedded: fonts whose license flag bars it, non-TrueType fonts, vertical Asian fonts.
  - Convert all text to geometry: exact look, bigger file, pixelation at high zoom; text still found by viewer search.
- SHX text is ALWAYS converted to geometry, even with that box cleared, and the text is also stored in the PDF as a comment (search comments to find it). ([G:BE373C38](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE373C38-678A-4AF9-96AB-4195FFD6F806))
- PDFSHX is listed with the publishing variables ([G:3482C5C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3482C5C7-472D-40F6-8323-E0B177DAE5B8)) but no page here describes it. Whether it controls the SHX comment is not stated.

What PDF can and cannot carry
- One multi-sheet PDF or several single-sheet PDFs carry 2D content only. DWF/DWFx carry 2D and 3D content. ([G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD)) (inference: a shaded 3D viewport still plots to PDF as an image of the view; "2D only" means no 3D model data in the file.)
- Underlay layers are not carried into a plotted or published file; only visible geometry is. ([G:BF215599](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BF215599-C96C-4FFF-A2DB-21DEFFAC71C0))

PUBLISH dialog ([G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E), [G:E0618DA9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E0618DA9-79B9-4766-9EF7-D388FD87FA25), [G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD), [G:9A17A2C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A17A2C7-F594-4854-ADC8-61CFAC575F8B)) [GUI]
- Open: Output tab > Plot panel > Batch Plot, or Output tab > Publish panel > Publish. Ctrl-click layout tabs > right-click > Publish Selected Layouts opens it with just those layouts ([G:556BF24C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-556BF24C-3996-4F6B-87AC-2BAC0FD9EE21)).
- Publish To: Plotter Named in Page Setup (paper, or plot-to-file if that PC3 plots to file); DWF format (DWF File or DWFx File); PDF format (PDF File). Output can be one multi-sheet file or one file per sheet. ([G:E0618DA9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E0618DA9-79B9-4766-9EF7-D388FD87FA25), [G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD))
- Plot-to-file output from Plotter Named in Page Setup goes to the location set in Publish Options (default from Options > Plot and Publish > Plot to File); each file is named after its sheet with the right extension (.plt, .jpg, .bmp ...). ([G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E))
- Sheet list:
  - Add Sheets (or drag drawings in): every layout of each drawing becomes a sheet; remove the ones you do not want.
  - "Include Layouts When Adding Sheets" and "Include Model When Adding Sheets" (shortcut menu) must be on to pull those in.
  - Move Sheet Up / Down: sheets plot in list order. Rename Sheet. Remove Sheets / Remove All.
  - Copy Selected Sheets: adds "Name-Copy(n)" at the end (Plumbing > Plumbing-Copy(1)); use it to publish one sheet twice with different page setups. ([G:311039EA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-311039EA-7660-4625-935E-CF0706B3C91A))
  - Page Setup column per sheet, or multi-select > right-click > Change Page Setup. "Import" in that list pulls setups from another DWG or DWT. Model-space setups only on model sheets; paper-space setups only on layout sheets. ([G:FB6BDFE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FB6BDFE4-9F8F-4028-AB27-2741A7C94152))
- Save Sheet List writes a DSD (Drawing Set Descriptions) file. Load Sheet List reads a DSD or a BP3 (Batch Plot) file. A DSD also stores the publish settings for reuse. A sheet set (DST) can be republished too. ([G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E), [G:E0618DA9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E0618DA9-79B9-4766-9EF7-D388FD87FA25), [G:9A17A2C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A17A2C7-F594-4854-ADC8-61CFAC575F8B))
- [AUTO] (inference) the DSD is the file a -PUBLISH run reuses. DSD keys and -PUBLISH prompts are NOT in these sources; build the first DSD in the dialog and test before scripting it.
- PUBLISHALLSHEETS controls which sheets are listed. PUBLISHCOLLATE and BGCOREPUBLISH are named only, no values. ([G:25B7793D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25B7793D-F5E0-46D4-B58A-6CD715D61C0F), [G:3482C5C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3482C5C7-472D-40F6-8323-E0B177DAE5B8), [G:951D5EB1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-951D5EB1-A380-4C8C-BE58-A64318016C79))

PDF set workflow ([G:46712A7A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-46712A7A-526B-4292-B0AC-3E6C6F54786A))
1. Give each layout a named page setup (plot area, paper size, scale).
2. Add the drawings and layouts to a sheet list; save it as a .dsd.
3. Set PDF options and publish.
DWF/DWFx sets follow the same three steps ([G:7889000A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7889000A-30F3-4543-B12C-77C769746335)).

Background publishing and timing [AUTO]
- Published jobs run in the BACKGROUND by default, and only ONE of your jobs can process in the background at a time. ([G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD)) (inference: a script that reads the PDF right after PUBLISH can find it unfinished; turn background publishing off for scripted runs.)
- Switches: Options > Plot and Publish > Background Processing Options > "Enable Background Plot When Plotting" and "... When Publishing"; Publish dialog > Publish Controls > "Publish in background"; Plot dialog "Plot in Background" = system variable BACKGROUNDPLOT. ([G:E531213D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E531213D-3796-4DBE-9E20-3595C0531662), [G:179E9ABE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-179E9ABE-1B52-49FF-9808-D0FD4DBB5D1F), [G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))
- The only BACKGROUNDPLOT values stated in these sources: with DXEVAL = 8 (update on publish) and BACKGROUNDPLOT = 2 or 3, you are prompted to update data extraction tables, but the tables in the published file are NOT updated. Set BACKGROUNDPLOT to 0 or 1 to publish updated tables. ([G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E)) (inference: 2 and 3 are the values with background publishing on.)
- Status: hover the plotter icon in the status tray. Right-click it: Cancel Sheet <sheetname>, Cancel Entire Job, View Plot and Publish Details. ([G:179E9ABE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-179E9ABE-1B52-49FF-9808-D0FD4DBB5D1F))
- VIEWPLOTDETAILS (Plot and Publish Details dialog): jobs and sheets from the CURRENT session only; View All or Errors; Copy to Clipboard. The same details are written to the plot and publish log file; its path is not given here. ([G:CA64FCF4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA64FCF4-A4CC-49C1-AE8D-82A098156D6E), [G:E0618DA9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E0618DA9-79B9-4766-9EF7-D388FD87FA25))

Limits and odd cases
- Publish In Reverse Order (Sheet Set Manager > Publish button) is not available for DWF output. ([G:5D9490A6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5D9490A6-AB56-4D4C-8B19-9FB3B061B3B4))
- 3D DWF sheets cannot go to "Plotter Named in Page Setup"; switch Publish To to DWF format. Publish Options "Precision Override" does not affect model sheets converted to 3D DWF. ([G:25B7793D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25B7793D-F5E0-46D4-B58A-6CD715D61C0F))
- DWF Layer Information and Block Information default to Don't Include. Block Information uses a BLK block template file (Publish Block Template dialog, Scan for Blocks) [GUI]. ([G:9A17A2C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A17A2C7-F594-4854-ADC8-61CFAC575F8B), [G:39ADEA79](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-39ADEA79-C993-418F-A89D-B6D6B9EFD874))
- DWF "Prompt for Name" (Multi-sheet DWF Options) asks for a file name on every publish; leave it off for scripts. ([G:9A17A2C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A17A2C7-F594-4854-ADC8-61CFAC575F8B))
- DWFx uses Microsoft XPS (a ZIP with metadata); its metadata shows only in Autodesk Design Review. ([G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD))
- A drawing that holds a data extraction table can raise the Outdated Table dialog on PLOT or PUBLISH, depending on DXEVAL. ([G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E))

Sheet sets and Vault
- Sheet Set Manager (View tab > Palettes) publishes a whole set or subset in one click, to one multi-sheet DWF, DWFx or PDF, or to paper. Publish button options include Publish Using Page Setup Override, Include Plot Stamp (all sheets) and Plot Stamp Settings. ([G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD), [G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0), [G:69D6F53A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-69D6F53A-8FBC-4988-BE75-0A455C8D0787), [G:64980F13](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-64980F13-1BE6-4FD4-A838-35B8837802B1))
- To set a sheet's page setup: Sheet Set Manager > open the sheet > Page Setup Manager > pick a named setup > Set Current. ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0))
- Block properties and attributes can be published per audience (plumbing fixtures to the plumber, light fixtures to the electrician) from the same sheets. ([G:2415687F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2415687F-0064-4AC8-AC52-AAEF9AD0E6AD))
- Vault commands: vltopensheetset opens a sheet set from the vault; vltsavetodst converts vaulted sheet set data to a DST and ALWAYS overwrites the local DST after backing it up as *._dst.bak_. vltcheckout takes only the latest version of the latest revision. ([G:2B794542](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B794542-5DEA-4D17-A29F-CF8B23FE2F0F))

## 15.8 Plotters, PC3 and PMP files, plot to file, plot stamp

PC3 files ([G:2DB9EB8C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DB9EB8C-767C-4C91-B0A3-FFFEC4C5863A), [G:C8997B02](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C8997B02-271B-47DE-95EF-B260A5E112D8), [G:C7895A4B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C7895A4B-F22E-40D7-B529-917ACEED6518), [G:8E317293](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8E317293-C409-4BF6-A001-4C68FD5170F9), [G:2B96DD20](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B96DD20-D921-4390-8F92-DEC37E40E740), [G:025BEBB2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-025BEBB2-EBE4-4966-871D-E91B0811579E))
- A PC3 holds port, raster and vector quality, paper sizes and device custom properties. One per non-system plotter; you can also make PC3s for Windows printers to change their defaults.
- Folder: the Plotters folder. Find it at Options > Files > Printer Support File Path > Printer Configuration Search Path. [AUTO path]
- Made by the Add-a-Plotter wizard (PLOTTERMANAGER, double-click the wizard shortcut) [GUI]; edited in the Plotter Configuration Editor [GUI].
- Editor tabs: General (only Description is editable); Ports (Plot to the Following Port, Plot to File, AutoSpool, Show All Ports, Configure Port); Device and Document Settings (Media, Graphics, Custom Properties, Initialization Strings, User-Defined Paper Sizes & Calibration).
- Graphics node: Vector Graphics (color depth, resolution, dithering); Raster Graphics slider "Raster and Shaded/Rendered Viewports" (None disables raster printing), OLE slider, trade-off slider; TrueType as Text or as Graphics; Merge Control (Lines Overwrite or Lines Merge; no effect for all-black or PostScript output).
- Changed settings show in angle brackets with a check mark on the node.
- Missing device: PLOT and PAGESETUP raise "Update PC3 File With New Printer" [GUI]. A substitute with another driver can change quality, color depth, resolution, media source, destination and finishing; an unsupported paper size falls back to the default. ([G:BA2B77DF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BA2B77DF-0D7A-41C1-9FDC-4671A313887A))

Paper sizes and PMP ([G:DCBDCEDD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DCBDCEDD-6DBA-4502-A507-1D20411F48B7), [G:29919840](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-29919840-24E1-4FEF-9262-77CAF144C128), [G:025BEBB2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-025BEBB2-EBE4-4966-871D-E91B0811579E))
- Custom sizes: PC3 editor > User-Defined Paper Sizes & Calibration > Custom Paper Sizes > Add (wizard: Start from Scratch or Use Existing; Media Bounds in inches or mm; Printable Area margins; Paper Size Name; PMP file name). [GUI]
- Starting from an existing size gives a user-defined size, not a standard one. Modify Standard Paper Sizes changes only the printable area.
- Filter Paper Sizes controls which sizes the Plot and Page Setup lists show. (The page's Check All / Uncheck All wording contradicts itself.)
- Plotter Calibration rescales EVERY plot from that plotter; use only when the device is inaccurate.
- PMP files are saved in the <product>drv folder.

Plot to file, raster, PostScript
- Plot to File: tick it in the Plot dialog (or set it on the PC3 Ports tab); OK opens Browse for Plot File [GUI]. A PLT is valid only if the PC3 was made for the real output device. Spool batch file example: `copy %1 \\server\printer`, run as `MySpooler.bat MyDrawing.plt`. ([G:6405BB6F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6405BB6F-4350-4F0A-AC09-3E237F20FBD6), [G:2B96DD20](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B96DD20-D921-4390-8F92-DEC37E40E740))
- Raster file driver: output in pixels, not inches (except Dimensional CALS); objects drawn in the background color plot invisible; files get large. BMPOUT, JPGOUT, PNGOUT, TIFOUT are tagged but not described. ([G:1DE891EB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1DE891EB-BEA8-48A7-B67D-1F1FB9FF4B66), [G:5164C465](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5164C465-5BCB-45E8-ACE2-49D540D7CB10))
- PostScript driver: PS for printers, EPS for files; Levels 1, 1.5, 2; if printing fails, clear the optimization options and add them back one at a time. ([G:16093F41](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-16093F41-C0F3-4808-9E50-52033021DB5C))

Plot stamp (PLOTSTAMP) [GUI] ([G:C8CEF1EE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C8CEF1EE-9816-40F8-AA2C-8C320A3C8564), [G:B35E72BB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B35E72BB-417C-4E69-82EE-5CE09B81AF6E), [G:48B87654](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-48B87654-BB76-4E81-86C3-48F3606405F7))
- Fields: Drawing Name (with path), Layout Name, Date and Time, Login Name, Device Name, Paper Size, Plot Scale, plus user-defined fields. Joined with comma and space.
- Settings live in a .pss file; Inches.pss and Mm.pss ship in the Support folder.
- Location default Bottom Left; offsets from the printable area or the paper border; TrueType font only; stamp past the printable area is cut off.
- Log: plot.log in the main application folder by default; one line per plotted drawing; written even when stamping is off.
- Plot dialog "Plot Stamp On" turns it on per plot. ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE))

## 15.9 Layout viewports: create, scale, lock, layers, clip, rotate, MVSETUP

What a layout viewport is
- A paper-space object that shows model space at a scale and orientation you set. COPY, MOVE, ERASE work on it. Edit it with Properties or grips. ([G:2B5D404A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B5D404A-DCAB-4AF6-A5C1-51593B38F519))
- Viewport scale = paper-space units / model-space units. Quarter scale = 1:4. Stretching or scaling the border does NOT change the view scale. ([G:A576A246](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A576A246-5D21-45C8-8C12-F1FA2F9E373D))

Create [AUTO]
- MVIEW ways: two diagonal corners; Named (saved model view); New (temporary model space, pick a rectangle); Object (closed object); Polygonal (PLINE-style). Prompt order is not in these sources. ([G:2B5D404A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B5D404A-DCAB-4AF6-A5C1-51593B38F519), [G:5272B8FC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5272B8FC-88FD-4B58-BC7C-A32C71AA22C2))
- -VPORTS in a layout ([G:93641503](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93641503-3EA3-4BC3-8E47-A33EAA6CD20A)). Options in page order:
  - Corner of viewport, then Opposite corner: rectangular viewport.
  - On: viewport active, objects shown. Off: objects hidden and it cannot be made current.
  - Fit: one viewport filling the paper-space view.
  - Shadeplot: As Displayed, Wireframe, Hidden, Visual Styles, Render Presets.
  - Lock: locks the current viewport's view.
  - New: pick two points in temporarily maximized model space; makes an unnamed view in a sized viewport.
  - Named: inserts a saved model view plus a new viewport.
  - Object: closed polyline (3 or more vertices; arcs and self-intersection allowed), ellipse, spline, region or circle.
  - Polygonal: Next Point, Arc, Close, Length, Undo, as in PLINE.
  - Restore: a saved viewport configuration.
  - Layer Override: "Reset viewport layer property overrides back to global properties." Enter Y to remove all overrides, then select viewports.
  - Layer: the layer new viewports are created on. VIEWPORTLAYER sets the default.
  - 2, 3 (Horizontal, Vertical, Above, Below, Left, Right), 4: split the current viewport.
  - The exact keyword capital letters are not printed on the page.
- New and Named viewports start LOCKED at a convenient default scale or the current annotative scale; unlock and use the scale grip to change. ([G:93641503](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93641503-3EA3-4BC3-8E47-A33EAA6CD20A))
- VPORTS without the hyphen opens the Viewports dialog [GUI]. ([G:B394F068](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B394F068-5731-4ECA-B6A9-E5A4D6BA32D5))
- -VPORTS in model space ([G:9761B629](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9761B629-0844-428D-9187-85886CA4C998)): Save, Restore, Delete, Join (two viewports sharing an edge of equal length; keeps the dominant view), Single, ? (lists ids and corners from 0.0,0.0 to 1.0,1.0), 2, 3, 4, Toggle (no previous set = 4 viewports), MOde (apply count changes to the current viewport or the whole display).
- Named viewport configurations can be SAVED only in model space; restore them in model space or as layout viewports. An unnamed configuration cannot be used in a layout. A layout viewport set cannot be saved. Names up to 255 characters: letters, digits, $ - _. ([G:255E03D0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-255E03D0-6899-4569-8C1C-C04A0A0D4B19), [G:B394F068](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B394F068-5731-4ECA-B6A9-E5A4D6BA32D5))

Set and hold the scale [AUTO]
- Ways: Properties (Standard Scale, or Custom Scale; Display Locked must be No); triangular scale grip (no unlock needed; border adjusts to keep the clip); status bar Viewports Scale; ZOOM with the XP option from inside the viewport. ([G:A576A246](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A576A246-5D21-45C8-8C12-F1FA2F9E373D), [G:9929178F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9929178F-64E4-4B76-BDE2-00BFDAEFC8B6)) (inference: ZOOM nXP is the scriptable route, e.g. 1/48xp for 1/4"=1'-0".)
- Display Locked = Yes stops pan and zoom from changing the scale. Reach it from Properties, the right-click menu, the ribbon or the status bar. ([G:2B5D404A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B5D404A-DCAB-4AF6-A5C1-51593B38F519), [G:F9A37755](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F9A37755-68A8-489D-B508-253EDD88F356))
- Locked viewport, zoom from paper space: zooms the whole layout, scale unchanged ([G:F9A37755](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F9A37755-68A8-489D-B508-253EDD88F356)). Locked viewport, inside model space: ZOOM is blocked ([G:EF13A95F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EF13A95F-380E-4276-B668-C98C9719BB75)). The pages describe different spaces; both hold.
- A drawing made from a template uses the template's scale list. SCALELISTEDIT edits it [GUI]; scales arriving with xrefs are temporary; a scale used by an annotative object cannot be deleted; Reset restores the default list. ([G:A576A246](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A576A246-5D21-45C8-8C12-F1FA2F9E373D), [G:11B58078](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-11B58078-C3D9-4E93-83B6-A330EC66064F))

Layers and display
- Put viewports on their own layer; VIEWPORTLAYER sets it for new ones. Border visibility follows that layer; plotting follows its Plot setting. Turn the layer OFF for output. ([G:79D20005](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-79D20005-DFB3-4D27-9066-628D4B6A910C), [G:93641503](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93641503-3EA3-4BC3-8E47-A33EAA6CD20A), [G:9A301B51](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A301B51-BFFF-4BC9-983C-938D6B5DAB2F))
- Nonrectangular viewports: turn their layer OFF, never FREEZE it, or the viewport clips wrong. ([G:5272B8FC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5272B8FC-88FD-4B58-BC7C-A32C71AA22C2))
- Many active viewports slow things down: Display Viewport Objects = No turns one off. MAXACTVP is listed for this topic. ([G:B0D6ED3E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B0D6ED3E-31BE-4903-8C5E-43F3A8E76D17), [G:A361F313](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A361F313-E1EB-400C-81B2-6B9AA2C0DDB7))
- Per-viewport layer freezing (VPLAYER is listed) is how model-space dimensions are kept to one viewport (15.11). ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1), [G:A361F313](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A361F313-E1EB-400C-81B2-6B9AA2C0DDB7))

### Clip, rotate, align, move between spaces (15.9 continued)

Clip [AUTO]
- VPCLIP: grips on the border, or Layout tab > Layout Viewports > Clip; pick an existing closed object or pick points. The new boundary REPLACES the old one; it does not trim it. A nonrectangular viewport is two objects (viewport and clip boundary); either can be edited. ([G:63873957](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-63873957-B431-4DA0-A5A6-3179BC4A97E2))
- MVIEW or -VPORTS Object turns a closed paper-space object (circle, closed polyline) into a viewport boundary that stays associated. ([G:5272B8FC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5272B8FC-88FD-4B58-BC7C-A32C71AA22C2))

Rotate a view
- Rotate viewport and view together: in paper space set VPROTATEASSOC = 1 [AUTO], select the viewport, Rotate, base point, angle. VPROTATEASSOC = 0: the viewport turns but the view inside does not. Model objects are not changed. ([G:D077CEA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D077CEA3-6EC1-4677-BD4B-372D7364D545))
- ROTATE turns objects only; it never rotates a view. ([G:D077CEA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D077CEA3-6EC1-4677-BD4B-372D7364D545))
- By UCS: inside the viewport, UCS World, then UCS Z 90 (view turns clockwise) or -90, then PLAN Current UCS; viewport scale may need resetting. ([G:64EB33A4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-64EB33A4-945A-4548-AC59-A4C597A41FF9)) (inference: command-line words UCS W, UCS Z, PLAN C.)

MVSETUP (not in AutoCAD LT) [AUTO] ([G:420F621B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-420F621B-9E49-4B81-8C52-3F024F4FA6E2), [G:8FCB2B0B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8FCB2B0B-4381-4878-8DA8-64C128203C55), [G:82672358](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-82672358-3DBA-4CDC-BA0C-CC89E6A15C74), [G:0E596DD0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0E596DD0-5F64-4408-AEB7-1C7DCB4874D3), [G:D077CEA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D077CEA3-6EC1-4677-BD4B-372D7364D545))
- On the Model tab (TILEMODE = 1) the first prompt is `Enable paper space? [No/Yes] <Y>:`
  - Enter or y: sets TILEMODE to 0 and continues on a layout.
  - n: `Enter units type [Scientific/Decimal/Engineering/Architectural/Metric]:` > `Enter the scale factor:` > `Enter the paper width:` > `Enter the paper height:`. Draws a border at the grid limits and ends. Use that scale factor when plotting.
- On a layout, top-level options: Align, Create, Scale Viewports, Options, Title Block, Undo.
- Align: `MVSETUP` > `a` > Horizontal, Vertical or Angled. Make the viewport whose view stays put current; give a base point; select the viewport to realign; give the alignment point in it; Angled adds distance and angle. Use Horizontal only for side-by-side viewports and Vertical only for stacked ones, or the view can pan out of the viewport.
- Rotate view: `MVSETUP` > `a` > `r`; pick the viewport if there are several; base point; angle or second point. It leaves the UCS changed: run `ucs` then `p` (Previous) after.
- Create > Delete Objects (removes layout viewports) or Create Viewports > Layout Number to Load: 0 or Enter = none; 1 = one viewport; 2 = four quadrant viewports (upper-left Top, upper-right SE isometric, lower-left Front, lower-right Right; you give the area and the spacing); 3 = a matrix along X and Y (gaps asked when more than one per direction). Redisplay shows the list again.
- Scale Viewports: Interactively (per viewport: paper-space units, then model-space units; 1 and 4 for quarter scale) or Uniform (one factor for all).
- Options: Layer (title block layer), Limits (reset limits to extents after the title block), Units (inch or mm paper units), Xref (insert or xref the title block).
- Title Block: Delete Objects, Origin (moves the layout origin), Undo, Insert > Title Block to Load (0 or Enter = no border; 1 to 13 = ANSI and DIN/ISO borders), Add (appends a line to mvsetup.dfs, for example `A/E (24 x 18in),arch-b.dwg,(1.12 0.99 0.00),(18.63 17.02 0.00),in`; the last field says inches or mm), Delete, Redisplay.

Line up views without MVSETUP
- XLINE through a point seen in viewport 1; MOVE viewport 2 from the matching point to a Perpendicular snap on the construction line. ([G:3C963F25](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3C963F25-4E6D-409C-B42B-3FEC43BE23A2))

Move objects between spaces, export a layout
- CHSPACE: select objects, Enter. Moves them between paper and model space. ([G:0988D29E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0988D29E-D54E-4C87-ADAF-11AA91B1B691))
- EXPORTLAYOUT: exports every visible object of the current layout, including objects off the paper, to model space of a new drawing. File dialog [GUI]; default folder = the drawing's folder; default name = drawing name + layout name. ([G:653D3843](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-653D3843-AFE5-4569-959F-E06F3866D7D7), [G:E155ED16](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E155ED16-14C8-4C0A-B0A1-E47E0793EED4), [G:3180E1FA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3180E1FA-3049-4F5E-B919-1BDC7E5EF7CA))
  - Not exported: objects on off or frozen layers, model objects not visible in a viewport, wipeouts, named views, materials, cameras, lights.
  - Converted: dimensions past the viewport edge are exploded; blocks past the edge become anonymous blocks with attributes turned into text ("Allow Exploding" ignored); annotative objects become plain; clipped xrefs become clipped block references; viewports become polylines or clipped viewport objects; visual style becomes 2D Wireframe; perspective becomes parallel.
  - An object seen in several viewports becomes several objects, which can break block data extraction.
  - Slower with a model space viewport active. PSLTSCALE = 0 can spoil linetype scale on xref and block objects. Detach or bind unresolved xrefs first.

Model space and paper space switching
- Double-click inside a viewport = model space in it; Ctrl+R cycles viewports; double-click outside = paper space; MSPACE and PSPACE do the same. Status bar MODEL/PAPER toggles. Lock the viewport before working inside it. ([G:C5BB2604](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C5BB2604-AD99-4F0C-BEFB-DA77C7D036A3), [G:EF13A95F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EF13A95F-380E-4276-B668-C98C9719BB75))
- Model tab viewports (tiled) are a different thing from layout viewports; view commands affect only the current tiled viewport. ([G:E3D303C4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E3D303C4-33F4-45D8-8A9A-AB483140EB2D), [G:3E43911D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3E43911D-0A0F-4900-BE32-5EF846AF36D8))

## 15.10 Model space plotting and scale factors

When model-space plotting is enough
- Only for a 2D drawing with ONE view: no multiple views, no per-view layer settings, and every annotation and the title block must be scaled by hand unless annotative. ([G:58CEA276](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58CEA276-414D-4BE6-A878-C2AE054A399E))
- Steps: set units; draw 1:1; insert the title block scaled by the inverse of the plot scale; scale text, dimensions, linetypes, hatch and blocks the same way; plot at the planned scale. ([G:58CEA276](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58CEA276-414D-4BE6-A878-C2AE054A399E))
- Variables involved [AUTO]: DIMSCALE (dimensions), LTSCALE and CELTSCALE (noncontinuous linetypes), HPSCALE (hatch), INSUNITS, INSUNITSDEFSOURCE, INSUNITSDEFTARGET (blocks, border, title block). Text: set the height at creation or a fixed height in STYLE. ([G:58CEA276](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58CEA276-414D-4BE6-A878-C2AE054A399E))

Scale factor = drawing units per plotted unit ([G:58CEA276](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58CEA276-414D-4BE6-A878-C2AE054A399E))

| Plot scale | Scale factor | Text plotted at | Draw text at |
|---|---|---|---|
| 1/8" = 1'-0" | 96 | 1/8" | 12" |
| 3/16" = 1'-0" | 64 | 1/8" | 8" |
| 1/4" = 1'-0" | 48 | 1/8" | 6" |
| 3/8" = 1'-0" | 32 | 1/8" | 4" |
| 1/2" = 1'-0" | 24 | 1/8" | 3" |
| 3/4" = 1'-0" | 16 | 1/8" | 2" |
| 1" = 1'-0" | 12 | 1/8" | 1.5" |
| 1 1/2" = 1'-0" | 8 | 1/8" | 1.0" |
| 1" = 20' | 240 | (not given) | (not given) |

- The same factor is the viewport scale denominator in a layout: 1/4" = 1'-0" is a 1:48 viewport (inference from [G:A576A246](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A576A246-5D21-45C8-8C12-F1FA2F9E373D) and this table).

Paper space sheet order ([G:9A301B51](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A301B51-BFFF-4BC9-983C-938D6B5DAB2F))
1. Build the model in model space at 1:1.
2. Open a layout tab and set the page setup (device, paper, plot area, scale, orientation).
3. Insert the title block (skip if the template has one).
4. Make a layer for viewports; create and place the viewports.
5. Set each viewport's scale, orientation and layer visibility.
6. Add dimensions and notes on the layout.
7. Turn OFF the viewport layer.
8. Plot or publish.
The 9-step dimensioning workflow on [G:8C8DA4BD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C8DA4BD-4558-4271-BD47-019839227DCB) follows the same order (dimension layer, layout, page setup, title block, viewports, viewport scale, then dimension).

## 15.11 Dimensions: associativity and scale across model and paper space

DIMASSOC: what kind of dimension you get [AUTO] ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA))
- The value at the moment a dimension is CREATED decides its type:
  - 2 = associative: location, orientation and value follow the geometry. A layout (paper space) dimension may be tied to model space objects.
  - 1 = non-associative: moves with the geometry only when both are selected and edited together; never updates by itself.
  - 0 = exploded: separate lines, 2D solids and text, not one dimension object.
- EXPLODE on a dimension gives the DIMASSOC 0 result. An exploded dimension can never be re-associated. ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA), [G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D))
- Options > User Preferences > "Make New Dimensions Associative" is the dialog switch [GUI]. ([G:04334508](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-04334508-47C9-43E3-875C-DD5FEC9F9930)) (inference: it is DIMASSOC; set DIMASSOC directly in scripts.)
- Check a dimension's state with LIST or the Properties palette. ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA))

Keeping and repairing association [AUTO]
- DIMREASSOCIATE: select dimensions, Enter; then per dimension enter `s` and pick the object, or pick a point on an object (osnaps allowed) for the extension line shown. ([G:04334508](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-04334508-47C9-43E3-875C-DD5FEC9F9930))
- DIMDISASSOCIATE: select dimensions, Enter. ([G:04334508](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-04334508-47C9-43E3-875C-DD5FEC9F9930))
- DIMREGEN refreshes associative dimensions after a pan or zoom of model space inside a layout viewport, after opening a drawing last saved by an earlier release, and after opening a drawing whose xrefs changed. ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA)) (inference: run DIMREGEN before plotting a set whose xrefs were updated.)
- Association is lost when: the geometry is erased; the geometry goes through a boolean (UNION, SUBTRACT); a grip stretch moves the dimension parallel to its dimension line; an Apparent Intersection snap loses its intersection; an associated block is redefined so the associated edge moves. A warning shows at the Command prompt. ([G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D), [G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA))
- Partially associative: one of two associated objects was erased; the other tie remains. Re-tie with DIMREASSOCIATE. ([G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D))
- The annotation monitor badges dimensions that lost association; its menu offers DIMREASSOCIATE and ERASE. ANNOMONITOR is listed as its system variable ([G:42802E38](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-42802E38-FD91-4550-8160-33B30AFAA875)) (inference: it switches the monitor on and off).
- Cannot be associative targets: hatches, images, UNDERLAYS, multilines, 2D solids. ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA)) (inference: dimensions snapped to an owner PDF underlay will not be associative.)
- Dimensions associated with model documentation drawing views can lose association if saved in a release before 2012. ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA))
- Non-associative dimensions update with an edit only if their definition points are in the selection set; the text midpoint is a definition point of every type. ([G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D))
- Definition points sit on layer Defpoints, which never plots. [AUTO] ([G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D))

Scale method: pick ONE per drawing [AUTO] ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1), [G:17FAE4A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-17FAE4A5-34C7-4D87-BFC5-E3791C083E73))
- Set text height, arrow size and gaps to their real size on paper; DIMSCALE multiplies them. DIMSCALE never changes measured lengths, tolerances, coordinates or angles. ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1))

| Where dimensions are drawn | Settings | Notes |
|---|---|---|
| Model space, plotted from model space | DIMSCALE = inverse of the plot scale (page example: plot 1/4, DIMSCALE 4) | Single-view sheets only ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1)) |
| Model space, shown through layout viewports | DIMSCALE = 0: AutoCAD computes the factor from each viewport | One dimension layer per viewport, frozen in the other viewports. Use when dims must be visible to other drawings through xrefs, or for isometric dims in 3D iso views ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1)) |
| Paper space (layout), on model objects | DIMSCALE = 1, DIMLFAC = 1 | Simplest. Associative dims read the true model value through each viewport's scale. Recommended for organizing and scaling ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1), [G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0)) |
| Annotative style | Tick Annotative in the style | Size follows the current annotation scale ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1), [G:635016D3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-635016D3-8469-45D0-8E3E-7CE20CAA6C2B)) |

- (inference) For architectural scales the model-space DIMSCALE equals the scale factor in 15.10: 1/4" = 1'-0" gives 48, 1/8" gives 96.
- Fit tab "Scale Dimensions To Layout" writes DIMSCALE from the ratio of the current model space viewport to paper space; in paper space outside a viewport, or with TILEMODE = 1, the factor is 1.0. "Use Overall Scale Of" writes a fixed DIMSCALE. ([G:17FAE4A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-17FAE4A5-34C7-4D87-BFC5-E3791C083E73))
- Paper-space dimensions of model objects: the viewport adjustment is combined with DIMLFAC and LIST shows it as a style override. Non-associative paper-space dims need DIMLFAC set by hand. ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1))
- DIMLFAC: leave at 1.0. It multiplies measured linear values (2 makes a 1" line read 2"). Not applied to angular dims, rounding values or plus/minus tolerances. "Apply to Layout Dimensions Only": leave it off except for non-associative layout dims. ([G:2D1177AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D1177AB-3130-4522-A631-AA28493529DC))
- To dimension model objects from a layout: snap to model space points through the viewport with osnaps, or select the model objects. ([G:208E7AC9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-208E7AC9-402C-4DB4-B7E0-58058A77B5E3))
- Automatic dimension breaks do NOT work trans-spatially (dimension and object in different spaces); use a Manual break. ([G:D04569C5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D04569C5-36A2-4DC1-A831-DF2D921FA8F5))
- DIMLAYER puts new dimensions on a named layer whatever the current layer is. [AUTO] ([G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0))

## 15.12 Dimension chains: continue, baseline, spacing, ordinate

DIM command options [AUTO letters] ([G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0), [G:241CB6E3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-241CB6E3-3342-47D5-9A23-AA59D47B06DF), [G:4BB89A0B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4BB89A0B-CAF1-47F7-BB51-E9401A84660E), [G:A2513269](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A2513269-161C-4193-BBC4-1D6717C41A47), [G:83D826E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-83D826E5-278C-41F0-911D-477C3F2E15D4))
- DIM chooses the type from the object under the cursor. Typed options: `a` Angular, `L` Arc Length, `o` Ordinate, `r` Radius, `d` Diameter, `j` Jogged (radius: pick center override, dimension line angle, jog location). Enter ends.
- Angular accepts an arc; a circle and two points; two nonparallel lines; or a vertex and two points.
- Linear: select a line, or give two extension line origins; cursor direction picks horizontal, vertical or aligned. Rotated: after the origins enter `r` and the angle. ([G:DEB94C8F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DEB94C8F-064F-4E44-AB7A-D157DA166581))

Continued (chain) and baseline [AUTO] ([G:DEB94C8F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DEB94C8F-064F-4E44-AB7A-D157DA166581), [G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0))
- A base dimension must exist first: linear, angular or ordinate.
- DIMCONTINUE and DIMBASELINE skip the "select base dimension" prompt when the last linear or angular dimension made can supply the first extension origin. Press Enter at that prompt to choose any dimension as the base instead.
- Pick each next origin with object snaps.
- Press Enter TWICE to end.
- Baseline places each new dimension line at the Baseline Spacing distance = DIMDLI (Lines tab).
- Style used: DIMCONTINUEMODE 0 = the current dimension style; 1 = the style of the dimension being continued. ([G:DE060D4E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DE060D4E-FA55-4740-B3D8-CE9952B45734)) [G:EB019E6B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EB019E6B-384B-4543-B31A-C426A4A4AA44) states that continued and baseline dims take the style of the dimension they continue.
- Placed dims stay put: changing DIMDLI, text size or dimension scale later does NOT move them, so lines and text can overlap. Fix with DIMSPACE. ([G:4701B99C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4701B99C-7895-4265-9CC3-47D3C42A463E))
- Hover menu on a dimension line end grip offers Continue dimension and Baseline dimension [GUI]. ([G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D))

DIMSPACE (Annotate > Dimensions > Adjust Space) [AUTO] ([G:8251AFDE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8251AFDE-C0B5-4BEA-896B-56487C594E05), [G:7CE4EF2B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7CE4EF2B-93C6-423A-9401-664F3FE0829A), [G:E810452E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E810452E-D1B8-41E7-9CEB-F136C9CB8E32), [G:4701B99C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4701B99C-7895-4265-9CC3-47D3C42A463E))
- Select the base dimension; select the dimensions to space; Enter. Then:
  - `a` (Auto) and Enter: equal spacing, automatic.
  - a number and Enter: that spacing.
  - `0`: lines the dimensions up (aligns them).
- Rules: linear or angular only; same type (rotated or aligned); parallel or concentric; on each other's extension lines.

Ordinate [AUTO] ([G:A2513269](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A2513269-161C-4193-BBC4-1D6717C41A47), [G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0))
- The datum is the CURRENT UCS ORIGIN. Move the UCS origin to the datum before dimensioning.
- DIM > `o`; Ortho (F8) on avoids jogged leaders; pick the feature point, then the leader endpoint. X-datum and Y-datum options fix the orientation.
- Ordinate dims do not accumulate error the way chains can.

Rotated views
- Dimension direction follows the UCS at creation. If the view is rotated, run UCS View first so horizontal and vertical follow the drawing. ([G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0))
- Oblique extension lines (isometric work, usually 30 or 60 degrees): DIMEDIT Oblique, select the dimension, give the angle. ([G:DEB94C8F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DEB94C8F-064F-4E44-AB7A-D157DA166581), [G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0))

## 15.13 Dimension style variables and DIMOVERRIDE

Styles
- DIMSTYLE opens the Dimension Style Manager [GUI] (New, Modify, Override, Compare, Set Current; tabs Lines, Symbols and Arrows, Text, Fit, Primary Units, Alternate Units, Tolerances). No command-line form is documented in these sources. ([G:60840416](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60840416-5E03-4CCC-ACEE-1E92D078BDB5), [G:99EA32DC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99EA32DC-F4BC-4095-A927-8DC551E95824))
- Non-dialog routes that ARE documented: set the DIM* system variable at the Command prompt, or DIMOVERRIDE. [AUTO] ([G:1EBBCFE1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1EBBCFE1-AC75-49C2-A889-1B286E96C4E8))
- Default style STANDARD. New dimensions use the CURRENT style. Changing a style updates every dimension that uses it. ([G:60840416](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60840416-5E03-4CCC-ACEE-1E92D078BDB5), [G:5469B348](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5469B348-3425-41C6-9CEC-F267BF6CCCA2))
- A style that is current or in use cannot be deleted. Substyle = "Use For" one dimension type (for example a STANDARD variant for diameter dims only). ([G:60840416](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60840416-5E03-4CCC-ACEE-1E92D078BDB5), [G:635016D3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-635016D3-8469-45D0-8E3E-7CE20CAA6C2B), [G:AE66A0B9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AE66A0B9-44D8-48D2-B26A-03F12CBB112F))
- Xref styles list as Xref:"drawing name"; they cannot be modified, renamed or made current, but can seed a new local style. ([G:135C8E5A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-135C8E5A-7756-433D-B9C8-ABF1EAE6224B), [G:60840416](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60840416-5E03-4CCC-ACEE-1E92D078BDB5))
- Annotate > Dimensions > Update applies the current style (with its overrides) to selected dims; the page tags the command -DIMSTYLE but prints no prompts. ([G:A31420D1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A31420D1-C876-47A5-ACAF-C7DC4F0B3E9E))
- Compare with the same style in both lists = list of every DIM variable, value and description. Overrides are not included. ([G:72E74990](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-72E74990-B2E4-4B3C-B9DA-68D9FB6A29D0), [G:12C6A969](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-12C6A969-A7CB-45C1-813B-7103C1A8652E))

Overrides [AUTO] ([G:1EBBCFE1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1EBBCFE1-AC75-49C2-A889-1B286E96C4E8))
- An override = a DIM variable changed without editing the style. Typing a DIM variable name at ANY prompt while dimensioning sets one. It applies to that dimension and every later one in that style until you set it back, save it as a style, or make another style current. It shows as `<style overrides>` under the style.
- DIMOVERRIDE applies overrides to existing dimensions:
  - `Command: dimoverride`
  - `Enter dimension variable name to override or [Clear overrides]:` dimclrd
  - `Enter new value for dimension variable <BYBLOCK>:` 5
  - `Enter dimension variable name to override:` another name, or Enter
  - `Select objects:` pick, then Enter

Variables by Dimension Style Manager tab ([G:8EA3CEFF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8EA3CEFF-F842-4EFD-B7D8-3D9BA6AFBBCF), [G:E063AF30](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E063AF30-6F14-42D6-B0AB-0CF5C47B5897), [G:38DAEEF0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-38DAEEF0-AB44-4C58-8D0E-955BFCFF71A7), [G:17FAE4A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-17FAE4A5-34C7-4D87-BFC5-E3791C083E73), [G:2D1177AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D1177AB-3130-4522-A631-AA28493529DC), [G:61A63A81](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-61A63A81-1248-4FEB-89B3-50F1D8AFF00D), [G:BE52ACEE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE52ACEE-A046-412D-AEC8-593B9DEB674D))
- Lines: DIMCLRD, DIMLTYPE, DIMLWD, DIMDLE (extend beyond ticks), DIMDLI (baseline spacing), DIMSD1, DIMSD2 (suppress dim line halves); DIMCLRE, DIMLTEX1, DIMLTEX2, DIMLWE, DIMSE1, DIMSE2 (suppress extension lines), DIMEXE (extend beyond dim line), DIMEXO (offset from origin), DIMFXLON and DIMFXL (fixed-length extension lines; the offset never goes below DIMEXO).
- Symbols and Arrows: DIMBLK1 (in the dialog, changing First also changes Second), DIMBLK2, DIMLDRBLK (leader), DIMASZ (size); DIMCEN (0 = none, positive = center mark size, NEGATIVE = centerline size; for DIMRADIUS and DIMDIAMETER drawn only when the dimension line is outside the circle); Break Size; DIMARCSYM (preceding, above, none); DIMJOGANG (radius jog angle); linear jog height factor.
- Custom arrowheads: a block that already exists in the drawing, named in DIMBLK, DIMBLK1, DIMBLK2. Annotative blocks are NOT allowed. The block's insertion point matters; it is scaled by DIMASZ x overall scale. ([G:5D1F8D41](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5D1F8D41-86EC-481F-ACA0-B169F0B91D00), [G:E063AF30](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E063AF30-6F14-42D6-B0AB-0CF5C47B5897))
- Text: DIMTXSTY (text style), DIMCLRT, DIMTFILL and DIMTFILLCLR (fill), DIMTXT (height; works ONLY when the text style height is 0, a fixed style height wins), DIMTFAC (fraction height scale; Fractional format only), DIMGAP (text gap; NEGATIVE = frame around text; also the minimum dim line segment for text to fit inside), DIMTAD (vertical: Centered, Above, Outside, JIS, Below), DIMJUST (Centered, At Ext Line 1, At Ext Line 2, Over Ext Line 1, Over Ext Line 2), DIMTXTDIRECTION, DIMTIH and DIMTOH (alignment: Horizontal, Aligned with Dimension Line, ISO Standard). Default text is horizontal, even on vertical dims. ([G:863065EC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-863065EC-12D5-4F65-8E6F-2BE140CA68DF))
- Fit: DIMATFIT (Either Text or Arrows best fit, Arrows, Text, Both), DIMTIX (always keep text between extension lines), DIMSOXD (suppress arrows that do not fit), DIMTMOVE (text moved: beside dim line; over with leader; over without leader), DIMSCALE (overall scale, or 0 for scale to layout), DIMUPT (place text manually), DIMTOFL (draw dim line between extension lines even when arrows are outside).
- Primary Units: DIMLUNIT (format), DIMDEC (precision), DIMFRAC (fraction format; works ONLY when DIMLUNIT is 4 architectural or 5 fractional) ([G:AA5F50E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AA5F50E5-1376-4E5A-AEFB-55C9FB95E883)), DIMDSEP, DIMRND (round off; not angular), DIMPOST (prefix and suffix in one string; a prefix REPLACES the default diameter and R prefixes; also added to tolerances; `%%c` = diameter symbol), DIMLFAC, DIMZIN; angular: DIMAUNIT, DIMADEC, DIMAZIN.
- Alternate Units: DIMALT (on), DIMALTU, DIMALTD, DIMALTF (multiplier; 25.4 default for imperial), DIMALTRND, DIMAPOST, DIMALTZ. Shown in square brackets. Never on angular dims; DIMALTF is not applied to rounding or tolerance values. ([G:61A63A81](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-61A63A81-1248-4FEB-89B3-50F1D8AFF00D), [G:1B946C9E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B946C9E-0AB1-40E6-8675-80A51851BEA1))
- Tolerances: method by DIMTOL and DIMLIM (None 0/0; Symmetrical 1/0; Deviation 1/0; Limits 0/1; Basic = box, gap stored as a negative DIMGAP); DIMTDEC; DIMTP (upper); DIMTM (lower); DIMTFAC (height ratio); DIMTOLJ (Top 2, Middle 1, Bottom 0); DIMTZIN; DIMALTTD; DIMALTTZ. ([G:BE52ACEE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE52ACEE-A046-412D-AEC8-593B9DEB674D))
- Named elsewhere: DIMLAYER, DIMCONTINUEMODE, DIMASSOC, DIMSTYLE (current style name), DIMSAH and DIMTSZ (names only).
- Bit values of DIMZIN, DIMTAD, DIMATFIT and similar are NOT in these sources.

Feet-and-inches zero suppression (DIMZIN) ([G:AED5808A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AED5808A-1E95-4C73-84FB-3259CA3625ED))

| Option | 1/2 in | 6 in | 1 ft | 1 ft 3/4 in |
|---|---|---|---|---|
| none | 0'-0 1/2" | 0'-6" | 1'-0" | 1'-0 3/4" |
| 0 Inches | 0'-0 1/2" | 0'-6" | 1' | 1'-0 3/4" |
| 0 Feet | 1/2" | 6" | 1'-0" | 1'-0 3/4" |
| 0 Feet and 0 Inches | 1/2" | 6" | 1' | 1'-0 3/4" |

- With feet and a fractional inch, inches always show: 4'-3/4" displays as 4'-0 3/4". ([G:AED5808A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AED5808A-1E95-4C73-84FB-3259CA3625ED))
- [AUTO] DIMZIN (and DIMTZIN) also change the output of the AutoLISP functions rtos and angtos. Check LISP that formats feet-inches after changing zero suppression. ([G:2D1177AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D1177AB-3130-4522-A631-AA28493529DC), [G:BE52ACEE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE52ACEE-A046-412D-AEC8-593B9DEB674D))
- DIMRND rounds every value except angular; 0.25 rounds to the nearest 0.25; shown digits still follow precision. ([G:83E8F93F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-83E8F93F-A715-4066-95A1-9D1C49398507))

## 15.14 Dimension edits: breaks, jogs, text, center marks

DIMBREAK [AUTO letters] ([G:71020908](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-71020908-3FCB-4385-BE5E-06473B5AFD48), [G:8D5CBF92](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8D5CBF92-3851-4C79-B912-E22C36524154), [G:C6221B2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C6221B2C-701D-4428-AE06-DF8455CBF312), [G:4BEA92A7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4BEA92A7-B60A-420B-B54B-060C31F98478), [G:0BE818D3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0BE818D3-AB18-49FC-9E94-E80F9A2BA0CD), [G:3F163549](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3F163549-563F-4F69-8FD6-A296FE3945D3), [G:D04569C5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D04569C5-36A2-4DC1-A831-DF2D921FA8F5))
- One dimension: select it, then `a` (Auto) Enter; or `m` (Manual) and two points on the dim, extension or leader line; or pick the crossing object and Enter; or `r` (Remove).
- Several: at the first prompt `m` (Multiple), select dimensions, Enter, then `a` (Auto) or `r` (Remove). (The Auto and Remove task pages place the Enter differently; test the exact keystrokes once.)
- Remove takes off ALL breaks of the selected dimensions.
- Auto breaks and object-picked breaks update when things move. Manual (two-point) breaks never update and ignore dimension scale and annotation scale.
- Gap size: Symbols and Arrows tab Break Size, times dimension scale and the viewport's annotation scale.
- No breaks: dimensions inside xrefs or blocks (objects in them can still cut dims outside); at arrowheads or text (use a background mask); LEADER or QLEADER leaders; spline multileaders; trans-spatial auto breaks.

Other edits
- DIMJOGLINE: select a linear dimension, pick the jog point; `r` removes a jog. ([G:3A5F6C3F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3A5F6C3F-F137-48B2-A15A-064FA8FCDC7F))
- DIMEDIT Oblique: select a linear dim, type the obliquing angle. ([G:DEB94C8F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DEB94C8F-064F-4E44-AB7A-D157DA166581))
- DIMTEDIT: Left justify; text angle (select, type the angle). ([G:7872D5EC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7872D5EC-1B72-4DE7-8926-96B02E8361C9), [G:E7F401CB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E7F401CB-603F-45DF-9BA4-08D543546668))
- Text grip menu, Reset Text Position, Flip Arrow: hover and right-click menus [GUI]. ([G:C48417B4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C48417B4-5D9E-455D-96B2-C33A1AAAE690), [G:9346D623](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9346D623-CB66-46A3-8754-CBF89AF0E426))
- Moving text up or down keeps it aligned and adjusts dim and extension lines. ([G:C48417B4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C48417B4-5D9E-455D-96B2-C33A1AAAE690))

Center marks and centerlines [AUTO] ([G:33A38BD6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-33A38BD6-03D0-426C-B62E-A83DC3E1F51D), [G:5A37100E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5A37100E-179D-4436-A51A-AE552022611B), [G:91447C4B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-91447C4B-3F9E-4841-B111-5A8432EB0754), [G:62AF9BD4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-62AF9BD4-FE63-4BF1-AC64-7C69D227B4CE), [G:AA0F538F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AA0F538F-350E-4FA5-AFA2-80A1238992C3), [G:E641F03D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E641F03D-7784-44BB-8228-4BDEC7641E06), [G:C078E9E4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C078E9E4-FF38-4BA7-B72B-F2DAB92AFC99), [G:42EBBFF4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-42EBBFF4-ABA0-41A4-A2FB-C5216ADC6F21))
- CENTERMARK: select circles or arcs, Enter ends. CENTERLINE: select two lines. Both are associative.
- They are NOT annotative and do not use dimension styles; best for model-space plotting or paper-space annotation.
- CENTERLAYER = default layer for new marks and lines. CENTERMARKEXE 0 = mark only, 1 = with extension lines. CENTERCROSSSIZE and CENTERCROSSGAP take a relative value (`0.1x`), an absolute value, or ByLineType. Also CENTEREXE, CENTERLTYPE, CENTERLTSCALE, CENTERLTYPEFILE.
- These variables affect NEW objects only. CENTERRESET returns extensions to CENTEREXE. CENTERREASSOCIATE and CENTERDISASSOCIATE manage the ties. After a grip override a centerline becomes fixed length.
- Spellings: use CENTERCROSSSIZE and CENTERLTSCALE (list page [G:33A38BD6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-33A38BD6-03D0-426C-B62E-A83DC3E1F51D)); [G:4D96ECE3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4D96ECE3-3230-4DB8-A849-EE61EF547A71) tags misspell them.

Dialog-only dimension features [GUI]
- TOLERANCE opens the Geometric Tolerance dialog, then asks `Enter tolerance location:`. A feature control frame on a leader: `leader`, two points, Enter twice, `t` (Tolerance). ([G:2821B734](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2821B734-18B4-4A0E-A020-318D45DDDAE1), [G:F8A2C283](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F8A2C283-D902-4C5E-BB6E-714DD9C5AA0D))
- DIMINSPECT: Inspection Dimension dialog; Shape Round, Angular or None; label; rate 0 to 100. ([G:26EFD7AA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-26EFD7AA-A6A7-4034-82BD-A10F718598F2))

## 15.15 Blocks that feed sheets and takeoffs

Title blocks, symbols and takeoff tags are blocks. These rules decide their size, look and data.

Units and auto scaling [AUTO] ([G:6C46049D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6C46049D-8636-442D-8BAC-CF4FD515FDC0), [G:410E4A05](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-410E4A05-F789-4416-9D63-3D24A46DD740))
- Four settings drive scaling on insert: Drawing Insertion Units (Drawing Units dialog > Insertion Scale), Block Insertion Scale Factor, Source Content Units (used when the inserted block or file is unitless), Target Drawing Units (used when the drawing is Unitless). Pages tag INSUNITS, INSUNITSDEFSOURCE, INSUNITSDEFTARGET (inference: the variables behind these settings).
- Results (content units into drawing units): inch block into inch drawing = 1; mm block into inch drawing = 0.0394; inch block into mm drawing = 25.4.
- -INSERT and the Insert dialog follow these rules. Drag-and-drop of a unitless block from a palette ignores the drawing units (factor only). Results can differ by insertion method.
- To stop all unit scaling, choose Unitless.
- (inference) For ezdxf-built files, set the drawing's insertion units and the block units to match, then check one inserted block's size.

Definitions and redefinition ([G:F81D7F1E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F81D7F1E-1F0A-45AD-AC7E-891A85A0033A), [G:BBD754F5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BBD754F5-D51F-4692-8194-49E5B130CE68), [G:9C9FF3BC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9C9FF3BC-7275-44E8-93D4-00A2F50BC96D), [G:09581E02](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-09581E02-567B-4D12-B72B-6CD8B5EF711D), [G:8F9E9A25](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8F9E9A25-A27B-4C09-9DA0-3EA0C1E0207B))
- A DWG inserted as a block: block name = file name; base point = the file's BASE point (default 0,0,0); its paper space objects are NOT included; all its block definitions come in too.
- SAME-NAME RULE: when an incoming block has the name of a block already in the drawing, the CURRENT drawing's definition is used and the incoming one is ignored. DesignCenter insert does not overwrite either.
- To update: WBLOCK the new block to its own DWG and insert that DWG (this overwrites), or redefine it in the Block Editor, or DesignCenter > Insert as Block > Redefine Block.
- A block edited in another drawing does not update here; xrefs do.
- Erasing every reference leaves the definition until PURGE.
- Nested blocks are allowed; self-referencing (circular) blocks are refused.
- Block descriptions are stripped by INSERT.
- Blocks tied to dimension and multileader styles (arrowheads) are made automatically and hidden from the Blocks palette and gallery. ([G:BC0FD3C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BC0FD3C1-3BFC-4C5D-AB9A-BF480D5084BE))

Look of objects inside blocks ([G:25E9F20C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25E9F20C-D146-426C-8815-37DF48D2D33F), [G:BC0FD3C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BC0FD3C1-3BFC-4C5D-AB9A-BF480D5084BE))
- Layer 0 with ByLayer: takes the insertion layer's properties.
- ByBlock (any layer): takes the reference's own properties first, then its layer.
- Anything else: keeps its own color, linetype, lineweight, transparency.
- A reference always goes on the current layer.

Commands
- BLOCK, WBLOCK, INSERT, BEDIT, PURGE open dialogs [GUI]. -INSERT is the command-line form (named in [G:6C46049D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6C46049D-8636-442D-8BAC-CF4FD515FDC0); prompts not in these sources). ([G:7625417C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7625417C-BFA4-4BEB-8A19-109778AA1E30), [G:B601CDBB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B601CDBB-357B-497E-9C41-3CDCA6A166CB), [G:2CF2A2C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2CF2A2C1-2353-4D9E-B16A-4BFD48D364CB))
- BLOCKEDITLOCK = 1 stops BEDIT from opening. [AUTO] ([G:B69D58AD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B69D58AD-7920-4198-AB2A-0E24B944F6CD))
- EXPLODE breaks a reference into parts; the definition stays. Insert/Blocks palette Explode option explodes on insert. ([G:66154AB6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66154AB6-AD55-4287-9754-44C7AF1D7FB1), [G:2EE5B254](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2EE5B254-D9A4-4FB2-8847-4A8731C0ECBD))
- Allow Exploding and Scale Uniformly are block definition properties (Block Editor > Properties > Block). ([G:ED407915](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-ED407915-A83E-4165-ABE6-C96A3663B307), [G:AF1F77D4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AF1F77D4-42BA-4B13-8E4E-9CF939EF81DD))

## 15.16 Data extraction for takeoffs

DATAEXTRACTION wizard [GUI] ([G:0D4D2F90](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0D4D2F90-8885-44B0-B78E-8EA1D7BB78D1), [G:50BEF344](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-50BEF344-C735-45C1-A0D1-D0F901BAEBB9), [G:8D59F5C3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8D59F5C3-6571-4D34-A35B-3C1BC71F7FF3), [G:B0D32260](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B0D32260-45E3-4643-B574-7F6C31579B68))
- Ribbon: Insert tab > Linking & Extraction > Extract Data (some pages say Annotate tab > Tables > Extract Data). No command-line form appears in these sources.
- Save the drawing first. Pages: Begin (Create a New Data Extraction, or Use Previous Extraction as a Template: BLK, DXE or DXEX) > Save Data Extraction As (DXEX) > Define Data Source (drawings, folders, sheet sets) > Select Objects > Select Properties > Refine Data > Choose Output > Table Style > Finish > pick insertion point.
- The DXEX file holds sources, objects, properties, output and table style. Reuse it as a template; every table that references it, even in other drawings, picks up changes when updated.
- BLK and DXE files made in AutoCAD 2024 and earlier cannot be edited, only used to seed a new DXEX.

What gets extracted: traps ([G:B57E9DB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B57E9DB5-A4CE-47B7-911F-B607B7564299), [G:BDC14AAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDC14AAD-FABB-4EC3-BDAA-51A178790A98))
- Choosing a drawing extracts ALL objects in it, even invisible ones. Preselect objects to limit it.
- Default sources: model space AND paper space, including objects inside blocks and xrefs. Change in Data Extraction - Additional Settings.
- Values are always in the WCS.
- Blocks inserted with NON-UNIFORM scale are NOT extracted; a dialog says they were skipped.
- Attribute values are TEXT even when they look numeric. This matters for formula and total columns.
- Several source drawings with different units: the CURRENT drawing's units are used for conversion, even when it is not a source.
- Annotative objects report data at the current annotation scale.
- Property categories: 3D Visualization, Attribute, Drawing, Dynamic Block, General, Geometry, Misc, Pattern, Table, Text. Display Name renames a column.
- Folder sources accept wildcards (example `*Pipe*.dwg`). A new matching drawing does not trigger the update notice; edit the extraction to add it. Clearing "Automatically Include New Drawings Added In This Folder" makes the folder monitored. ([G:B57E9DB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B57E9DB5-A4CE-47B7-911F-B607B7564299), [G:384963CC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-384963CC-4C0F-4F2C-BBF5-A517901C90CC))

Refine and output ([G:8F587A78](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8F587A78-1D60-47F6-8254-A534D68439FF), [G:39165928](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-39165928-A505-464B-8536-5817BA9DEC27), [G:DA254FE6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DA254FE6-AC9D-4F38-B848-AF48B1ABA928), [G:858B6B28](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-858B6B28-F97C-424C-BFC2-B978B943194A), [G:5064889C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5064889C-613B-4B49-B883-BCF1F1FD15EB), [G:F185C718](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F185C718-4F2A-4F04-B097-56F82B828547))
- Combine Identical Rows adds a Count column; identical numeric rows show their SUM. Combine Record Mode > Sum Values. Filters, sorts, totals footer (Sum, Max, Min, Average), formula columns (+ - * / and CAL/QUICKCALC functions). Only VISIBLE columns are output.
- Output: a table in the drawing and/or an external file: XLSX, MDB, CSV, or TXT (tab separated, no formatting).
- Writing a period, comma or pound sign into an Excel or Access file replaces it with its Unicode representation.
- Extraction table cells are LOCKED by default (formatting is not). Extracted data sits inside a bold border; add rows or columns only outside it. Formatting and added rows survive updates.
- TABLEEXPORT writes a table to CSV (select the table, right-click Export, file dialog) [GUI]. ([G:85E4E4E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-85E4E4E5-3AB7-483F-99A1-B02843A2DBF0))
- Old attribute extraction tables must be converted (right-click > Convert to Data Extraction Table) before they can update; column sizes are lost. ([G:EFC150A0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EFC150A0-3824-4838-B98B-6F5460F1489F), [G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E))
- Detach a DXEX from a table: right-click inside a cell > Data Extraction > Detach Data Link. From the drawing: External References palette, Missing toggle off, "Data Extraction - [name.dxex]" > Detach. ([G:7312FC9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7312FC9D-4FB7-47B3-B16B-A4734A413D8D))

Updates and DXEVAL [AUTO] ([G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E), [G:B57E9DB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B57E9DB5-A4CE-47B7-911F-B607B7564299))
- DXEVAL sets when the "Data Extraction - Outdated Table" dialog shows (OPEN, SAVE, PLOT, PUBLISH, ETRANSMIT). Default: check, without auto-update, on PLOT and ETRANSMIT.
- Values stated: 1 = check when the drawing opens; 8 = update on publish. The full bit list is not in these sources.
- Auto-update can be set for SAVE, PLOT, PUBLISH, ETRANSMIT. With PLOT or ETRANSMIT the table is updated before output and the drawing is NOT saved.
- DXEVAL = 8 with BACKGROUNDPLOT = 2 or 3: published tables are NOT updated. Use BACKGROUNDPLOT 0 or 1.
- External files are never checked for currency. Attribute extraction tables give no notice.
- (inference) The Outdated Table dialog can stall an unattended -PLOT or accoreconsole run on a drawing that holds an extraction table. Test first.

Excel data links ([G:EC74C0C3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EC74C0C3-22EA-4159-B43C-479102E4639B), [G:C6324D6D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C6324D6D-0997-4C7B-99EC-4429C73DB81A), [G:C2F9F994](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C2F9F994-85D4-41DA-9B64-E12C3D66FE9E), [G:8B29525A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B29525A-5FBD-46D1-B927-8DBDC2847511))
- Link External Data on the Refine Data page (or DATALINK). Match one drawing column to one spreadsheet column; Check Match. Failures: "No match was found between any values in the drawing data and external data" (often numeric precision), or a column without unique values.
- Microsoft Excel must be installed on the same PC, and the XLS/XLSX saved locally, or no link can be made.
- DATALINKUPDATE syncs either way. Delete a data link only with DATALINK; the External References palette cannot delete it.

Headless takeoff (inference)
- The documented extraction route is a wizard. For unattended takeoffs, read block attributes and geometry directly (AutoLISP, COM, or ezdxf on a DXF) and apply the same traps on purpose: decide on paper space and xrefs, handle non-uniform blocks, convert attribute text to numbers, use WCS values, and watch units.

dbConnect (legacy external database links) ([G:F53A2A1A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F53A2A1A-48F9-42CE-9FBA-8C17A0200EE3), [G:05A3DDF8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-05A3DDF8-1928-4146-9DA0-F72747B41E39), [G:C7B08E1E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C7B08E1E-ED83-4089-BFE8-8FBA3D395CF3), [G:268ED65B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-268ED65B-919F-4DDD-BF65-AD05A2FBF0CF), [G:FE53CC5B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FE53CC5B-72DA-4FF9-AAB9-2225666D712B), [G:DA648AB6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DA648AB6-7A1E-4442-A4A8-392B67200582))
- DBCONNECT palette with Data View, link templates, label templates and queries (Quick, Range, Query Builder, SQL 92). Every step is a dialog or palette [GUI]; no command-line form, system variable or API member is documented. Files: .dbq query sets, .dbt template sets, asi.ini (legacy link mapping).
- Links do not print; labels (mtext) show linked data. Closing Data View, opening another table or exiting auto-commits edits.
- Export Links writes key fields plus each linked object's entity handle as native, comma- or space-delimited text.
- (inference) Not a practical headless takeoff path.

## 15.17 Xrefs: attach, overlay, paths, loading, logging

What an xref is ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667), [G:53030EDD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-53030EDD-1D1D-40C4-922E-9B964A048ED9), [G:0D7D1315](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0D7D1315-B58A-4BCD-9953-282FF578B144))
- A link to the MODEL SPACE of another DWG. It reloads every time the host opens, and adds little to file size. "External reference" covers DWG, image, PDF and other files; "xref" means a DWG.
- Uses: coordinate with other designers, build a master drawing from component drawings, keep their layer and style names apart from yours, bind at project end.
- Variable block attributes inside an xref are ignored.
- If another person is editing the referenced file, you get its last SAVED version.
- Xrefs nest without limit; each copy has its own position, scale and rotation. Parametric constraints can tie only to an xref's insertion point.

Attach [GUI dialog; command-line prompts not in these sources]
- XATTACH, or the External References palette (EXTERNALREFERENCES; Insert tab > Reference panel launcher), or DesignCenter right-drag > Attach as Xref. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667), [G:3E6FFC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3E6FFC2C-B509-47EA-88D7-5287347BA1E7))
- Attach External Reference dialog fields: Name; Browse; Reference Type = Attachment or Overlay; Locate using Geographic Data; Scale X, Y, Z (Uniform Scale); Insertion Point; Path Type = Full, Relative or No Path (default Relative; REFPATHTYPE changes the default) [AUTO]; Rotation; Block Unit (Unit = the INSUNITS of the inserted block, Factor); Show Details (Found In, Saved Path). Several DWGs can be attached in one go. ([G:53030EDD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-53030EDD-1D1D-40C4-922E-9B964A048ED9))
- [G:1F7D6EA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1F7D6EA1-9AA8-4D33-819F-09750C295D6B) names an "XREF Path option" for fixing paths (inference: the -XREF command line has a Path option; prompts not given).
- A URL attach must include https:// or ftp://; a site login prompt may appear [GUI]. ([G:D91CFD9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D91CFD9D-44EC-408D-8E60-8C826216EA61))

Attachment vs Overlay ([G:53030EDD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-53030EDD-1D1D-40C4-922E-9B964A048ED9), [G:0D7D1315](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0D7D1315-B58A-4BCD-9953-282FF578B144), [G:B6A3AD28](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B6A3AD28-F27C-414C-937E-68B6BC0E9126))
- Attachment: carried along when your drawing is itself attached somewhere (nests).
- Overlay: NOT carried along when your drawing is attached or overlaid into another drawing. Use it to see others' work without it showing up twice downstream.
- Switch type: palette Type cell (double-click) or right-click > Xref Type > Attach / Overlay [GUI]. Nested xrefs cannot change type.
- (inference) Overlay suits owner backgrounds placed in your sheets, so they do not ride into drawings that reference yours.

Paths [AUTO]
- Full path: drive letter, URL or server drive. Relative path: from the host drawing's folder or drive; not possible when the file is on another local drive or a network server. ([G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))
- Relative forms: `\` = root of the host's drive; `path` or `.\path` = from the host folder; `\path` = from the root; `..\path` = up one level; `..\..\path` = up two levels. Move the host and you must fix relative paths. ([G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))
- A nested xref's saved path is relative to its immediate host, not to the open drawing. ([G:0D7D1315](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0D7D1315-B58A-4BCD-9953-282FF578B144))
- Unsaved host: Saved Path shows a full path with an asterisk until the save; "Make Relative" works even on an unnamed host. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667), [G:EDBB7CA6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB7CA6-8505-4695-A828-77756E7B9D83))
- PROJECTNAME: type a name to set the current project, or "." to clear. Project names and their search paths live in the registry and can be edited only in Options > Files [GUI]. ([G:01B0493B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-01B0493B-944E-401F-A52D-82EFE874D16B), [G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))

Search order when a file is not at its saved path (the three pages differ; follow the one for the case)
- Top-level xref saved with No Path: host drawing folder, then support search paths, then project search paths (PROJECTNAME), then the Start In folder of the program shortcut. ([G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))
- Nested xref: original saved path, host drawing folder, project search paths, support search paths, Start In folder. ([G:1F7D6EA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1F7D6EA1-9AA8-4D33-819F-09750C295D6B))
- Underlay (PDF, DWF, DGN): saved path, folder of the current drawing, project search paths, support search paths, Start In folder. ([G:9C5FB777](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9C5FB777-337C-433A-9562-F395BF77186D))
- With a project name set, the path prefix is stripped and the project paths are searched, then the program search path again. ([G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))
- (inference) Keeping xrefs and underlays in the host drawing's folder makes them resolve in every case.

Fixing paths [GUI] ([G:F01B6AFD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F01B6AFD-5E4A-4663-A8B4-BC95BD199AF3), [G:EDBB7CA6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB7CA6-8505-4695-A828-77756E7B9D83), [G:1E07BA3C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1E07BA3C-8C5F-465F-B540-D5B4BB8CAB8B), [G:97F90017](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-97F90017-E17A-4209-A6BD-1E205BF892E1))
- External References palette: switch the Missing toggle OFF to list every reference (ON lists only missing ones).
- Details pane Saved Path (type or browse); right-click Select New Path (offers to apply the folder to other missing refs); Find and Replace (swaps one path for another in all selected refs, reports updated and failed counts); Change Path Type > Make Absolute, Make Relative, Remove Path.
- Reference Manager (separate app) lists and rewrites saved paths (xrefs, images, fonts, plot configs) in many drawings without opening them. No undo. ([G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))

Layers and display [AUTO]
- Xref-dependent names show as XREFNAME|NAME (example STAIR|STEEL). They are re-read from the file on every reload. You cannot make an xref layer current or insert an xref block. ([G:4E9487C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E9487C1-0821-47F9-8F1B-ECFFE3237FDE))
- VISRETAIN = 0: changes to xref layer properties last only for the session; lost on reload, detach or exit. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667))
- XREFLAYER: default layer for NEW xrefs. Freezing that layer hides the WHOLE xref regardless of its own layers. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667))
- XDWGFADECTL: fade percent for all xrefs (Insert tab > Reference > Xref Fading). ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667), [G:3E6FFC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3E6FFC2C-B509-47EA-88D7-5287347BA1E7))
- ERHIGHLIGHT: highlighting between palette and drawing; off is faster. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667))
- XCLIPFRAME: shows clip boundaries of clipped xrefs. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667))
- Xref dimension styles cannot be modified or made current ([G:135C8E5A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-135C8E5A-7756-433D-B9C8-ABF1EAE6224B)). Plot style tables and annotation scales arrive with xrefs ([G:5E926DA6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5E926DA6-8CEB-4270-9C9D-6F7F61E84C85), [G:11B58078](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-11B58078-C3D9-4E93-83B6-A330EC66064F)).
- Status bar xref icon appears when xrefs are attached; it shows an exclamation point when any are not found. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667))

Loading, locking, performance [AUTO] ([G:5A45465D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5A45465D-287F-460A-91B5-2CB8593FC7F1), [G:3DE106E0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3DE106E0-95E7-493C-9C03-8EA2BB6FA90C), [G:14520D04](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-14520D04-A872-497B-B892-6CB5784D3454), [G:D0C84B3B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D0C84B3B-9A88-41B0-A8B6-162E2842A8A3), [G:E4076F41](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4076F41-2F33-4E42-90D3-A1BA5AE64388))
- XLOADCTL: 1 = demand loading; the referenced file stays open and LOCKED (others can open it but not save). 2 = demand loading with copy: a temporary copy of the last saved version is opened, the original stays editable. The "Disabled" value is not stated (inference: 0). Dialog: Options > Open and Save > External References: Disabled / Enabled / Enabled With Copy.
- Demand loading pays off for clipped xrefs (needs a spatial index saved in the referenced drawing) and for many frozen xref layers (needs a layer index). Save indexes: SAVEAS > Tools > Options > Index Type: Layer, Spatial, Layer & Spatial [GUI]. INDEXCTL is the related variable (values not given). Pre-R14 files gain nothing.
- XLOADPATH: folder for demand-load copies; empty = the standard temp folder. Slow network: local XLOADPATH plus XLOADCTL 2. Users sharing one XLOADPATH share temp copies.
- Unload keeps the link, hides the xref and frees memory; with XLOADCTL 1 it also unlocks the file. Reload restores it. ([G:5A45465D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5A45465D-287F-460A-91B5-2CB8593FC7F1), [G:9D9A31DB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9D9A31DB-7256-4403-BD1C-4CD1FC314FAE))
- XREFNOTIFY sets change notification (default: a balloon by the xref icon). Check interval: `(setenv "XNOTIFYTIME" "n")`, n = 1 to 10080 minutes, default 5; type the name with exactly that capitalization. ([G:3DE106E0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3DE106E0-95E7-493C-9C03-8EA2BB6FA90C))
- All xrefs update when the drawing opens; the palette's Reload reloads only if the file changed. ([G:66F1B6BA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66F1B6BA-4964-4540-8EB8-88C71E6B2A63))

Logging for headless diagnosis [AUTO] ([G:1908D8C6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1908D8C6-5691-499B-8153-04D234D8B754), [G:C655520A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C655520A-9BE9-4F25-A890-49B981DD1349))
- XREFCTL = 1 turns logging on (default 0). Log = plain ASCII <drawing name>.xlg in the CURRENT folder, created if missing, appended each session.
- Each entry: drawing, date and time, operation (Attach Xref, Reload Xref, etc.), the nesting tree, each appended symbol (example `Appending symbol: STAIR|BOLT`), the search used ("Searching in ACAD search path"), and errors. Safe to delete when large.
- (inference) Turn XREFCTL on in scripted runs to see why an xref failed to load without a screen.

## 15.18 Xrefs: bind, XBIND, in-place edit, clip, missing and circular

Missing and circular references ([G:1F7D6EA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1F7D6EA1-9AA8-4D33-819F-09750C295D6B))
- The saved path is checked on OPEN, on PLOT and on Reload. If the file moved or was renamed, the xref does not load: an error shows the path and name, and text at each insertion shows the missing path.
- A task dialog may also appear, offering to ignore all missing xrefs or update their folder locations [GUI]. (inference: a stall point for unattended runs; resolve paths before the run.)
- Ship every referenced file with the drawings.
- Circular chain (A attaches B, B attaches C, C attaches A): on ATTACH a warning asks whether to continue [GUI] (Yes loads up to the loop point; No cancels). On LOAD the loop is broken for the session with the message `Breaking circular reference from C to current drawing.`
- Moved xref: on load a message at the xref site says it cannot load from the old path; give the new path and it reloads. ([G:164C2548](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-164C2548-91E6-476D-AFDF-6257340C2EE2))

Detach, unload, erase
- DETACH (palette right-click > Detach) removes the xref completely, including its layer definitions. Do not just erase it. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667), [G:3E6FFC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3E6FFC2C-B509-47EA-88D7-5287347BA1E7))
- A nested xref can be detached only from inside the drawing that holds it; the palette Tree View shows nesting. ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667), [G:EDBB7CA6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB7CA6-8505-4695-A828-77756E7B9D83))
- To detach several missing xrefs: Missing toggle ON, select them, Detach. ([G:3E6FFC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3E6FFC2C-B509-47EA-88D7-5287347BA1E7))

Bind ([G:E3039A04](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E3039A04-4524-462B-AA27-E5F7DE8C4E9E), [G:5BF89799](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5BF89799-D496-4AAD-8773-9D4BF9B9E8CD), [G:1BC15FC3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1BC15FC3-D900-4293-B210-BFC3B9C088BC), [G:4E9487C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E9487C1-0821-47F9-8F1B-ECFFE3237FDE))
- Palette > right-click a DWG reference > Bind > Bind Xrefs/DGN Underlays dialog [GUI]. Result: the xref becomes a block definition with a block reference in its place.
- Bind type "Bind": xref-dependent names change from XREF|NAME to XREF$n$NAME, n starting at 0 and rising when the name exists (FLOOR1|WALL becomes FLOOR1$0$WALL, then FLOOR1$1$WALL).
- Bind type "Insert": works like detach then insert; the xref name is stripped (FLOOR1|WALL becomes WALL). No renaming: if a local object has that name, the bound object takes the LOCAL object's properties.
- A nested xref can be bound only by also selecting its parent.
- Xrefs that contain proxy objects CANNOT be bound. Underlays can never be bound. ([G:1BC15FC3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1BC15FC3-D900-4293-B210-BFC3B9C088BC), [G:09D63C05](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-09D63C05-6647-4086-B7E3-86A019E4F93D))
- Why bind: freeze an archive copy so later edits to referenced files do not change it, or send reviewers one file. ([G:1BC15FC3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1BC15FC3-D900-4293-B210-BFC3B9C088BC))
- (inference) After a Bind-type bind the layer names change, so layer-keyed plot styles, layer filters, layer states or per-viewport freezes stop matching. Insert-type merges into same-name local layers.

XBIND and RENAME ([G:68D6DC25](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-68D6DC25-F67B-4B3E-94BF-1D7B6D897C6C), [G:4E9487C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E9487C1-0821-47F9-8F1B-ECFFE3237FDE), [G:D6330A0F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D6330A0F-E738-47B3-BAA3-6F5AB93600AC), [G:82D1A9CB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-82D1A9CB-A6D0-429B-857B-46B17D669A92))
- XBIND binds single xref-dependent named objects (blocks, dimension styles, layers, linetypes, text styles) [GUI dialog: expand the xref and type, select, Add to Definitions to Bind].
- `|` becomes `$n$`: STAIR|STEEL becomes STAIR$0$STEEL. Then RENAME it (RENAME dialog [GUI]). Layer 0 and linetype CONTINUOUS cannot be renamed.
- Binding a layer also binds its non-CONTINUOUS linetype. XBIND on a block binds everything its objects reference; a block holding an xref binds that xref and all its dependents.
- No command-line forms of XBIND or RENAME are given in these sources (inference: hyphen forms exist; verify on the command reference pages before scripting).

Edit in place: REFEDIT, REFSET, REFCLOSE ([G:CB42FBEC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CB42FBEC-212A-4050-A8DE-0774E6BF6928), [G:FBD079DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FBD079DA-935D-4836-858F-9754CC5BB15A), [G:B4C77039](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B4C77039-395A-4F5A-82D9-B6C7F69E4898), [G:EFA35F95](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EFA35F95-67B6-4B87-83A2-05928923CD2B), [G:1B2C1E8F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B2C1E8F-DFC5-44BA-8C43-03528AF08C0A), [G:6241A30A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6241A30A-97B7-424B-BCE7-9C2B65D866A9))
- REFEDIT (Insert > Reference > Edit Reference): pick the reference; if the pick hits nested references, the Reference Edit dialog lists them [GUI]. Only ONE reference can be edited at a time. OLE objects show but cannot be edited.
- You pick the working set; everything else is locked and faded. XFADECTL sets the fade (bigger = more faded); fading shows only in the 2D Wireframe visual style.
- The reference FILE is locked during the edit; you cannot edit in place if another user has it open.
- REFSET adds or removes objects (works only in the space where REFEDIT started; PICKFIRST = 1 allows preselecting). New objects you draw usually join the working set; objects made by editing objects OUTSIDE the set (a FILLET of two outside lines) do not.
- REFCLOSE saves back or discards. Saving a block redefines it and regenerates all instances. Discard does NOT restore objects outside the working set that you deleted (use UNDO). If a bad edit was already saved back, UNDO then REFCLOSE again to restore the xref file.
- Objects removed from the working set leave the reference and go to the host; objects added leave the host and go to the reference.
- BINDTYPE: 0 = properties pulled into the host get a $#$ prefix (xref layer SITE becomes $#$SITE); 1 = names unchanged (not in LT).
- Reference Edit Settings tab: "Create Unique Layer, Style, and Block Names" (on = $#$ prefixes); "Display Attribute Definitions for Editing" (changed attribute definitions affect only LATER insertions); "Lock Objects Not in Working Set". ([G:FD66291F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FD66291F-A997-4D0A-B84C-07C9B8EFB150))
- A saved-in-place xref loses its drawing preview until the xref file is opened and saved.

Edit in a separate window: XOPEN ([G:86BE8B4E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-86BE8B4E-B12D-46C9-BB50-699AD3DF342B), [G:C0857771](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C0857771-7619-4D14-A509-1AD5E493261F), [G:4E8FEAC4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E8FEAC4-D090-4DAB-A067-3A45E5139470))
- Palette right-click > Open, or XOPEN (nested xrefs via the Open Reference Files dialog [GUI]). The source opens in its own window; edit, save, close, then reload it in the host. Check what else references that file first.
- NCOPY copies selected objects nested in an xref, block or DGN underlay into the current drawing. ([G:CB42FBEC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CB42FBEC-212A-4050-A8DE-0774E6BF6928), [G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E))

Clip: XCLIP ([G:58C43BAA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58C43BAA-B13F-479F-BA00-932BB75AD2C6), [G:55ED3E89](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-55ED3E89-6903-4941-8AE5-8CDC7F021657), [G:22089B93](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-22089B93-5681-4ECF-A288-41099B7B124F))
- Clips xrefs and BLOCK references; DGNCLIP, DWFCLIP, PDFCLIP, IMAGECLIP clip the matching attachments.
- Boundary: polyline, rectangle or polygon. Clipping changes DISPLAY only; the objects are not altered. Answer yes to delete an existing boundary first. Invert Clip hides the inside instead.
- The boundary is ALWAYS applied planar to the current UCS; a picked polyline is applied in its own plane.
- Self-intersecting polygons are rejected and the old boundary returns.
- A clipped parent clips its nested xrefs. Images inside xrefs or blocks clip to rectangular extents only.
- Clipping OFF shows the whole reference (on and thawed layers).
- Show the boundary: XCLIPFRAME (xref), PDFFRAME, DWFFRAME, DGNFRAME, IMAGEFRAME set to 1 [AUTO]; then the midpoint grip of the first edge flips inside and outside.
- The XCLIP prompt list is not printed in these sources. The task page names the choices: pick a polyline, a rectangular boundary, a polygonal boundary, and Invert Clip ([G:55ED3E89](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-55ED3E89-6903-4941-8AE5-8CDC7F021657)). Test the keystrokes before scripting.

Index of xref names ([G:0FEDAC31](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0FEDAC31-0FE5-4799-9848-E84B2C00BF84), [G:954D94FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-954D94FF-B6DE-44E3-B7ED-58BC49FCF6E8), [G:2AA53D1F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2AA53D1F-FAB3-4D30-B32B-A091FC860DBD), [G:F454031F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F454031F-39F0-4484-850D-7FF90EC44A4D))
- Commands: ATTACH, XATTACH, XREF, EXTERNALREFERENCES, EXTERNALREFERENCESCLOSE, XBIND, XCLIP, REFEDIT, REFSET, REFCLOSE, XOPEN, NCOPY, RENAME, BASE, XCOMPARE (compare a loaded xref with its saved file or another DWG; XCOMPARECLOSE, XCOMPARERCNEXT, XCOMPARERCPREV).
- Variables named without values here: DEMANDLOAD, ERSTATE, FRAMESELECTION, INSBASE, TREEDEPTH, TREEMAX, TRAYICONS, TRAYNOTIFY, TRAYTIMEOUT, VISRETAINMODE, XEDIT, XREFOVERRIDE, XREFREGAPPCTL, XREFTYPE, XCOMPAREBAKPATH, XCOMPAREBAKSIZE, XCOMPARECOLORMODE, XCOMPAREENABLE, COMPARESHOWCONTEXT, CMFADECOLOR, CMFADEOPACITY.
- Coordination models (Navisworks NWD, NWC): COORDINATIONMODELATTACH dialog with the same Path Type, Insertion Point, Scale and Rotation fields. ([G:77A546A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-77A546A5-4D71-42DE-A67B-D67C36E51CC5))
- Point clouds: POINTCLOUDATTACH; POINTCLOUDLOCK stops move and rotate. ([G:8D698472](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8D698472-3435-4632-BEC8-301D417F760B))

## 15.19 Underlays for owner backgrounds (PDF, DWF, DGN)

Pick the background type
- Owner sent a DWG: attach it as an xref (15.17; inference: Overlay suits backgrounds). Xrefs can be bound, clipped and layer-controlled; underlays cannot be bound ([G:09D63C05](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-09D63C05-6647-4086-B7E3-86A019E4F93D)).
- Owner sent a PDF, DWF or DGN: attach it as an underlay. Underlays can be viewed, snapped to and clipped, but are linked files, not drawing objects. ([G:09D63C05](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-09D63C05-6647-4086-B7E3-86A019E4F93D), [G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E))

What an underlay is ([G:09D63C05](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-09D63C05-6647-4086-B7E3-86A019E4F93D), [G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E))
- 2D geometry from DWF, DWFx, PDF or DGN files, linked by path like a raster image. Not part of the DWG; keeps file size small.
- Underlays CANNOT be bound and CANNOT be edited. They are slightly less precise than DWG geometry.
- DGN: V7 and V8 only, 2D objects only; 3D content gives a warning and is not supported.
- A PDF is attached one PAGE at a time, a DWF one sheet, a DGN one model. The attach dialog allows Shift/Ctrl multi-select of pages or sheets. ([G:EE6787B6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EE6787B6-DD70-42D3-A719-01CAF51E5E9A), [G:EA5455B3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA5455B3-DDCF-4551-9008-5F44FF227D71)) (inference: each selected page becomes its own underlay.)
- The same file can be attached many times, like a block. Each instance has its own clip boundary, contrast, fade and monochrome.
- DWF and PDF underlays display ONLY in the 2D Wireframe visual style. DGN underlays display in any visual style.
- PDF hyperlinks are converted to text.
- Xrefs can carry their own underlays.
- Password-protected DWF, DWFx or PDF: the password (case sensitive) is asked on attach AND every time the drawing opens, once per protected file [GUI]. ([G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E))

Attach
- ATTACH (Insert tab > Reference > Attach), or PDFATTACH, DWFATTACH, DGNATTACH: Select Reference File dialog, then the Attach PDF/DWF/DGN Underlay dialog [GUI]. ([G:EE6787B6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EE6787B6-DD70-42D3-A719-01CAF51E5E9A), [G:EA5455B3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA5455B3-DDCF-4551-9008-5F44FF227D71), [G:8B74424C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B74424C-5370-4035-A42D-1A6EB2303241))
- Dialog fields: Name; Browse; page, sheet or model list; Path Type (Full, Relative, No Path; default Relative; REFPATHTYPE) [AUTO]; Insertion Point; Scale; Rotation; Show Details (Found In, Saved Path). DGN adds Conversion Units (Master or Sub Units). ([G:02FAF12D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02FAF12D-BA81-4124-86B5-8E381182C579), [G:D966C3EC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D966C3EC-0D69-4D3E-9471-048D9C99E250), [G:F742649E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F742649E-96E8-4784-AE63-6E9694D5516B))
- Defaults at attach: insertion point 0,0,0; scale 1; rotation 0. ([G:22CE2AD1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-22CE2AD1-593D-4E30-98B0-156FF2CDC755))
- With Specify On-Screen cleared you type the insertion point, scale and rotation. The PDF and DGN pages say at the command prompt; the DWF page says in the dialog. ([G:EE6787B6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EE6787B6-DD70-42D3-A719-01CAF51E5E9A), [G:8B74424C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B74424C-5370-4035-A42D-1A6EB2303241), [G:EA5455B3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EA5455B3-DDCF-4551-9008-5F44FF227D71))
- SCALE RULE [AUTO]: if INSUNITS is unitless, or the file has no resolution information, the scale factor BECOMES the underlay's width in drawing units. If INSUNITS is a real unit (mm, cm, inches, feet) and the file has resolution information, the factor is applied after the true width in drawing units is found. ([G:02FAF12D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02FAF12D-BA81-4124-86B5-8E381182C579), [G:D966C3EC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D966C3EC-0D69-4D3E-9471-048D9C99E250), [G:F742649E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F742649E-96E8-4784-AE63-6E9694D5516B)) Raster images (IMAGEATTACH) follow the same rule. ([G:ED93554F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-ED93554F-6006-4230-93FA-FBF6DCB00F28)) (inference: set INSUNITS before attaching an owner PDF, then measure one known dimension and correct with SCALE.)
- Hyphen forms: [G:5F10E306](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F10E306-BC6C-49C4-B9C4-5F05EEC72146) lists -ATTACH and -DGNBIND as the only hyphen underlay commands. It lists no -PDFATTACH and no PDFIMPORT. Prompts for -ATTACH are not in these sources.
- (field) accoreconsole has no PDFIMPORT command, and -PDFATTACH crashed it.
- (inference, untested) Routes to probe instead: -ATTACH in full AutoCAD driven over COM; writing the PDF underlay into a DXF with ezdxf (15.21); or asking the owner for DWG backgrounds and attaching them as xrefs.

Look: contrast, fade, monochrome, background ([G:E8C90EB7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E8C90EB7-A132-4AFE-B5F5-2E504920B931), [G:EF976213](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EF976213-D7DE-478C-8718-6E84436B45A6), [G:1D405507](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1D405507-C0F8-4641-8B71-1489A22D1552), [G:90C33CBF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-90C33CBF-48E1-44E7-B286-92D58F087A8E), [G:1E425683](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1E425683-5B58-4686-96A8-672CCBE27E67))
- Contrast, Fade, Monochrome and Adjust Colors for Background are set per instance. They never change the source file and never affect other instances. They DO change plotted output.
- Adjust Colors for Background: default Yes. AutoCAD compares the underlay background with the drawing background; when one is light and the other dark, the underlay colors are INVERTED so it stays visible. No keeps the original colors (the underlay may then disappear against the background).
- PDFADJUST (and ADJUST, DWFADJUST, DGNADJUST) [AUTO]: select the underlay; the "Enter PDF Underlay Options" menu offers Fade (enter a value), Contrast (enter a value), Monochrome (Yes or No). The display updates when the command ends. Value ranges, defaults and keyword letters are not printed in these sources.
- Properties palette: Contrast, Fade, Monochrome, Adjust Colors for Background; Geometry: Position X/Y/Z, Scale, Width, Height, Rotation; Misc: Show Clipped, Layer Display Override.
- MOVE, SCALE, ROTATE, MIRROR, ARRAY work on underlays. Grips act like block grips: one base grip at the lower-left corner, plus clip corner grips once clipped. ([G:22CE2AD1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-22CE2AD1-593D-4E30-98B0-156FF2CDC755), [G:AAD65B06](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AAD65B06-E480-49EA-B97D-57DDEA36783C))

Clip [AUTO] ([G:68628501](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-68628501-A570-452A-B914-87C4C7BFD941), [G:3536E877](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3536E877-F160-427F-A343-5DA828594B37), [G:095BAA52](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-095BAA52-1D04-4491-98DF-1B6BC5C61C6D), [G:FF7A6066](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FF7A6066-A726-4BA3-A5C6-5E926931CC3B), [G:63236225](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-63236225-06A7-4B8B-B085-04D4AC9C66D6))
- PDFCLIP, DWFCLIP, DGNCLIP (or select the underlay > contextual tab > Clipping > Create Clipping Boundary). At the prompt enter `s` (Select Polyline), `p` (Polygonal), `r` (Rectangular) or `i` (Invert Clip), then draw. Finish a polygon with Enter.
- If the underlay is already clipped, the command first asks to delete the old boundary: enter `y`.
- For `s`, draw the closed polyline over the underlay before running the command.
- ONE boundary per instance; vertices within the underlay's extents; clipping limits display AND plot. Delete the boundary to get the full underlay back. Show Clipped (Properties > Misc) shows or hides the clipped part.

Layers inside the underlay ([G:5EA58C29](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5EA58C29-9D73-4E4D-8020-6323E928ED79), [G:22962E58](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-22962E58-EC27-424C-A98F-7CE9DB5AF7BB))
- PDFLAYERS, DWFLAYERS, DGNLAYERS, ULAYERS (or right-click > Layers) open the Underlay Layers dialog [GUI]. All visible layers are on after attach. An empty list means the file has no layers.
- Properties > Misc > Layer Display Override reads None (all on) or Applied (some off), without opening the dialog.

Frames ([G:38CC9880](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-38CC9880-3D94-4560-8A9B-7975F9C40A9C), [G:095BAA52](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-095BAA52-1D04-4491-98DF-1B6BC5C61C6D))
- FRAME controls frame display AND whether frames plot, for ALL underlays of every type. Ribbon states: Hide Frames; Display And Plot Frames; Display But Don't Plot Frames. Numeric values are not printed in these sources. Per type: PDFFRAME, DWFFRAME, DGNFRAME, IMAGEFRAME, XCLIPFRAME.
- With frames hidden, a clipped underlay still shows only inside its clip.
- Underlays on a locked layer cannot be selected.

Snaps ([G:B8546EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B8546EA0-3B70-4971-8360-E0545B907A05), [G:F2AAFB51](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F2AAFB51-6E6C-46CC-9754-25427376A477))
- UOSNAP, PDFOSNAP, DWFOSNAP, DGNOSNAP switch underlay snapping separately from normal object snaps [AUTO]; values not given.
- A PDF made from SCANNED plans is a raster image: object snap does NOT work on it.
- PDFs from third-party programs can have nonstandard snap points (example: circles without a center point).
- (inference) Do not take measurements by snapping to a scanned owner plan, and expect dimensions snapped to an underlay to be non-associative ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA)).

Paths, status, memory ([G:9C5FB777](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9C5FB777-337C-433A-9562-F395BF77186D), [G:4F405E95](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F405E95-E2CA-454A-A1AC-968CE85D75BB), [G:E1CAF0EF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E1CAF0EF-32FF-4C04-9C3E-747F33F08BC6), [G:8D82D74D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8D82D74D-89F8-40A8-9453-049A92D2C5B1), [G:6EBD545E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6EBD545E-FC40-44F8-A041-3B7467F70A69))
- Search order: saved path, folder of the current drawing, project search paths (PROJECTNAME), support search paths, Start In folder.
- Status in the External References palette: Loaded, Unloaded, Not Found (Found At blank), Unreferenced (attached but no instances). List View shows one row per FILE, not per instance.
- Not Found or Unloaded underlays show only as a boundary box and do not plot.
- AutoCAD UNLOADS underlays by itself when memory is too low to hold several. (inference: check Status before a batch plot.)
- Detach removes ALL instances and the link. Erasing one instance keeps the link. Unload hides and keeps the position for reload.

Plot, publish, save down ([G:BF215599](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BF215599-C96C-4FFF-A2DB-21DEFFAC71C0))
- Plotting or publishing writes only VISIBLE underlay geometry. None of the underlay's own layer data goes into the output file.
- Save to an older DWG: PDF underlays need AutoCAD 2010 or later (unless a Bonus Pack is installed); DGN needs 2008 or later; DWF 2007 or later; DWFx 2008 or later. Earlier releases do not display them.
- eTransmit tracks PDF, DWF, DWFx and DGN underlays the same way as raster images.
- Reference Manager lists underlays with saved and found paths and can repoint them (separate app) [GUI]. ([G:E1CAF0EF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E1CAF0EF-32FF-4C04-9C3E-747F33F08BC6))

## 15.20 Import and export translators (DGN, IGES, STEP, STL, 3D DWF)

DGN import: DGNIMPORT [GUI dialog] ([G:2A82AA09](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2A82AA09-4C1A-4737-910A-064D872F12B5), [G:F022E27B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F022E27B-89CB-4012-ACB1-74555F7DF7D8))
- Import DGN Settings dialog. DGNIMPORTMODE holds the defaults for Import into Current Drawing, Prefix Dependent Definitions and Ignore Duplicate Names (values not given).
- Pick ONE design model (a DWG has one model space). Sheet models that reference it come in as layouts with viewports; other sheet models are skipped.
- External references: Translate References to Blocks or Xrefs (blocks when importing into the current drawing, xrefs when importing into a new one; names = design file + dash + model); Ignore All External References; Attach as DGN Underlay. DXF references are ignored.
- New DWG files made for references are NOT deleted automatically. If the DGN's folder is read-only, they go to the Documents folder.
- Overwrite choice for those files: Prompt to Overwrite (stalls a script, inference), Overwrite without Prompting, Do Not Overwrite.
- Conversion Units: Master Units (1 master unit = 1 DWG unit) or Sub Units.
- MicroStation .rsc resource files (line styles) must be on the Support File Search Path at import or attach time, or you get an error.
- Explode Text Node to Text Elements: one text object per line (keeps text along curves).
- Mapping setup (Standard by default) maps levels, line styles, lineweights and colors. Linetype remapping supports only acad.lin and acadiso.lin.

DGN export: DGNEXPORT [GUI dialog] ([G:E2FED62A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E2FED62A-14A5-4FC9-8485-5C2353282608), [G:4159EDDE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4159EDDE-E5A6-4C67-A3C3-262FA3AE0275), [G:F884EE2E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F884EE2E-1251-4ED9-843A-E5BD95AC9971))
- Export > DGN, type V8 DGN or V7 DGN. No accented or Asian characters in the DGN file name.
- DWG references: translate each to its own .dgn (Prompt to Overwrite / Overwrite without Prompting / Do Not Overwrite), bind all into ONE DGN (references become cells), or ignore them.
- "Export DGN Underlays as DGN References": checked = exported as references, cleared = dropped. Do not export V8 DGN underlays into a V7 file.
- Seed file sets working units. Imperial seeds: V8-Imperial-Seed2D/3D.dgn (Feet / Inches, 304800 per foot); V7-Imperial-Arch01 (Feet / Inches, 8000 POS) and Arch02 (1000 POS); Civil01 and Civil02 (Feet / Tenths). Then Master Units or Sub Units.
- DGNMAPPING: the Standard setup cannot be renamed, modified or deleted.
- MicroStation terms: levels = layers, cells = blocks, design model = model space, sheet model = layout, pen tables = plot styles, seed file = template; references with No Nesting translate as overlays. ([G:14C18189](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-14C18189-3124-4AA2-BCF7-0860460C7F58))

3D model import: IMPORT ([G:F5CEE149](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F5CEE149-E2CA-481A-97DE-EB85FE62697D), [G:0A48F69C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0A48F69C-E62A-44AC-A1E9-326E90C12A3B), [G:2CF5CE0F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2CF5CE0F-8049-459E-86C9-1826B41957F6), [G:F2BD58A8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F2BD58A8-CBE1-40B2-A8EB-AA16D0A112BA), [G:A6485DF3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A6485DF3-DAE5-480B-BB66-69EA2E2E3F58), [G:02A0FDF4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02A0FDF4-E1C3-45B1-8369-F901356EE7B7))
- Formats: IGES, STEP (AP214, AP203E2), Inventor (.ipt, .iam), SolidWorks (2003 to 2010, and 2019), Creo (.prt and .asm to 6.0), CATIA V4 and V5, JT (7.0 to 10.4), NX (3 to 7.5, 1847 Series), Parasolid (to version 23), Rhino (to 6.0). ([G:3AAB133D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3AAB133D-8A9F-43E3-89AD-D88DAE6982C0), [G:69622D22](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-69622D22-3E9E-4341-9E6C-5EF59B6FF15C), [G:870FBEA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-870FBEA3-E955-4A96-9628-8A7F2308C39A), [G:2A5B5616](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2A5B5616-15B6-4B72-876B-20501812054C), [G:7948584E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7948584E-B5D8-4C8B-BC5F-268839077AE9), [G:95A581CB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-95A581CB-1FB4-403A-A0CD-C3F250F65C13), [G:5142A3B9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5142A3B9-3491-4470-82E9-AB71937C49E2), [G:393FF535](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-393FF535-8AEA-4B37-B6BF-BC277E2E6540))
- Import runs as a BACKGROUND job. The documented way to put the result in the drawing is to click the file name in the notification bubble, or right-click the Import status bar icon > Insert [GUI]. IGES goes to the background only if translation takes over 5 seconds. (inference: no documented headless route.)
- Parts become blocks named after the part (bad characters become `_`), on layer 0, original wireframe colors kept as overrides. The top block's INSUNITS = the source units, or "No Units" if unknown.
- Inventor imports are NOT associative (use VIEWBASE for associative views). An .iam with assembly features does not import; export STEP or SAT from Inventor first.
- IGES: only fixed-length ASCII. Round trips change objects: a 2D polyline exports as entity 106:12 and comes back as a SPLINE; the IGES line (110) imports as a spline; IGES points (116) are not imported. ([G:0ECCAE5E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0ECCAE5E-8807-4F38-BDC7-627804012FDE), [G:C2ECA739](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C2ECA739-79F6-49C0-A57E-B3443674DBC6), [G:F61C578E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F61C578E-A246-417F-B826-6FB87BF03EF9))
- ACISIN imports SAT; ACISOUT exports trimmed NURBS surfaces, regions and solids only (lines and arcs are ignored). ([G:46B2F3E3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-46B2F3E3-F933-4411-94D7-DC4E11D3EC60))
- 3DSIN opens a dialog; up to 70 objects. ([G:64EFE542](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-64EFE542-CAE3-484B-A16D-6FFE7ACA29B3))

Exports
- STL (EXPORT or STLOUT): all selected solids must lie entirely in the positive X, Y, Z octant of the WCS. Only 3D solids and watertight meshes. FACETRES sets facet density; very high values only make bigger files. ([G:E40AB085](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E40AB085-5A19-4E3E-A74C-82F62DCD0DDB), [G:250152B2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-250152B2-7CA2-4F22-8A47-7F74FEBF6FAD), [G:4B5C0F42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4B5C0F42-2B82-49F0-946E-C1E22C8D7336))
- 3D DWF or DWFx (3DDWF, Export > 3D DWF): all model space objects by default. 3DDWFPREC 1 to 6 (higher = smoother, bigger, global). Only the diffuse map of materials publishes. Not carried: block attributes, layer information, hyperlinks, images, visual styles, named views and cameras, lights, XCLIP and section clipping, gradient hatch, hidden edges, many fonts. Put repeated objects in blocks to speed it up. ([G:792617AA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-792617AA-2DB3-4870-A739-C9225A5889DD), [G:62099908](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-62099908-E16E-4BD2-ABE0-C46FB64F4162))

## 15.21 ezdxf notes (inference)

None of these sources mention ezdxf, DXF group codes or any API. Everything here maps the AutoCAD rules above onto files built with ezdxf. ezdxf names are from memory and marked "verify": check them in the ezdxf docs before use.

Layouts and page setup
- Give every layout a real paper size, units, plot area and device; 0 x 0 paper leaves it uninitialized and PUBLISH will not take it ([G:725ED087](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-725ED087-F39F-429A-8D56-5E727112A53E)). (verify: the layout page setup call, `page_setup()`.)
- No spaces in layout names (field).
- Open the saved file once in AutoCAD or accoreconsole so each layout initializes and regens before -PLOT or -PUBLISH ([G:2C5C9DE4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C5C9DE4-0740-4D7F-A781-745A04F588B0), [G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA)).

Viewports
- Viewport scale = paper units / model units ([G:A576A246](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A576A246-5D21-45C8-8C12-F1FA2F9E373D)). With a viewport defined by paper size and model view height: scale = paper height / model view height. Example: 1/4" = 1'-0" (1:48) in a 10" tall viewport needs a 480" model view height. (verify: `add_viewport(center, size, view_center_point, view_height)`.)
- Put viewports on a layer that is off or set not to plot; lock them (Display Locked) so later zooms do not change the scale ([G:79D20005](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-79D20005-DFB3-4D27-9066-628D4B6A910C), [G:F9A37755](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F9A37755-68A8-489D-B508-253EDD88F356)).
- For model-space dimensions per viewport, freeze each dimension layer in the other viewports ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1)).
- Shade plot is a per-viewport property ([G:37708FB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-37708FB5-CF5E-4E55-8E77-F884687A4131)). PDF and DWF underlays show only in 2D Wireframe viewports ([G:7D42F81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D42F81C-1007-4D3C-83CE-88D2AF49918E)).

Dimensions
- Choose the scale method first (15.11): paper-space dims with DIMSCALE 1, or model-space dims with DIMSCALE = the scale factor (48 for 1/4" = 1'-0").
- Dimension graphics must be generated before saving or the dimension may show nothing (verify: the dimension `render()` step).
- Dimensions written outside AutoCAD carry no geometry association; use DIMREASSOCIATE in AutoCAD where it matters ([G:04334508](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-04334508-47C9-43E3-875C-DD5FEC9F9930)).
- DIMTXT takes effect only with a text style of height 0 ([G:38DAEEF0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-38DAEEF0-AB44-4C58-8D0E-955BFCFF71A7)). DIMFRAC needs DIMLUNIT 4 or 5 ([G:AA5F50E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AA5F50E5-1376-4E5A-AEFB-55C9FB95E883)). Definition points belong on layer Defpoints, which never plots ([G:BDD8C619](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BDD8C619-AB31-49D8-AE55-465EE6FAB61D)).

Blocks, xrefs, underlays
- Set the drawing's insertion units ($INSUNITS) and each block's units to match ([G:6C46049D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6C46049D-8636-442D-8BAC-CF4FD515FDC0)). A same-name block already in a target drawing wins on insert ([G:9C9FF3BC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9C9FF3BC-7275-44E8-93D4-00A2F50BC96D)).
- DXF has PDF, DWF and DGN underlay entities with underlay definitions, and xref block definitions (verify the ezdxf calls for underlay definitions, underlays and xref definitions). Set INSUNITS first because of the underlay scale rule ([G:02FAF12D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02FAF12D-BA81-4124-86B5-8E381182C579)). This is an untested way around the accoreconsole -PDFATTACH crash (field).
- Use relative paths or keep referenced files in the host drawing's folder so all three search orders find them (15.17).

## 15.22 System variable quick list

Only what these sources state. "Named only" = listed on an index page with no meaning or values given.

Plot and publish
- BACKGROUNDPLOT: the Plot dialog "Plot in Background" box ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE)). Only values stated: with DXEVAL = 8, values 2 or 3 leave published extraction tables stale; use 0 or 1 ([G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E)).
- DXEVAL: when the Outdated Table check runs; default checks on PLOT and ETRANSMIT without updating; 1 = check on open; 8 = update on publish ([G:A4B8BDF9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A4B8BDF9-5DDA-48F6-B535-B8801A66871E)).
- PLOTTRANSPARENCYOVERRIDE: overrides the Plot Transparency box; default honors the page setup and Plot dialog ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE), [G:D8BE8598](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8BE8598-D9F8-49C2-81BC-19786A390379)).
- PLOTROTMODE: also affects plot orientation ([G:264D3513](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-264D3513-0D22-4461-82D6-14F391BC5CDE)).
- PLOTOFFSET: listed with plot settings ([G:99AABBCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99AABBCD-5908-40AD-AF7B-0C3D5594B8F5)) (inference: printable-area vs paper-edge offset origin; verify).
- PUBLISHALLSHEETS: which sheets the Publish dialog lists ([G:25B7793D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25B7793D-F5E0-46D4-B58A-6CD715D61C0F)).
- Named only: BGCOREPUBLISH, PUBLISHCOLLATE, FULLPLOTPATH, PDFSHX, PLQUIET, PSTYLEMODE, PSTYLEPOLICY, CPLOTSTYLE, DEFPLSTYLE, PAPERUPDATE, RASTERDPI, RASTERPERCENT, RASTERTHRESHOLD, TEXTFILL, TEXTQLTY ([G:99AABBCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-99AABBCD-5908-40AD-AF7B-0C3D5594B8F5), [G:3482C5C7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3482C5C7-472D-40F6-8323-E0B177DAE5B8), [G:951D5EB1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-951D5EB1-A380-4C8C-BE58-A64318016C79), [G:929FE8EC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-929FE8EC-EFE3-43BB-A79F-4FF509A91D5A)).

Layouts and viewports
- LAYOUTTAB = 1 shows the Model and layout tabs ([G:C5BB2604](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C5BB2604-AD99-4F0C-BEFB-DA77C7D036A3)).
- TILEMODE: 1 = Model tab; MVSETUP's "Enable paper space" Yes sets it to 0 ([G:420F621B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-420F621B-9E49-4B81-8C52-3F024F4FA6E2)).
- VIEWPORTLAYER: default layer for new layout viewports ([G:93641503](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93641503-3EA3-4BC3-8E47-A33EAA6CD20A)).
- VPROTATEASSOC: 1 = rotating a viewport rotates its view; 0 = it does not ([G:D077CEA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D077CEA3-6EC1-4677-BD4B-372D7364D545)).
- PSLTSCALE: 0 can spoil linetype scale of xref and block objects in EXPORTLAYOUT ([G:3180E1FA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3180E1FA-3049-4F5E-B919-1BDC7E5EF7CA)).
- LTSCALE, CELTSCALE, HPSCALE, DIMSCALE: model-space plotting scale set ([G:58CEA276](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58CEA276-414D-4BE6-A878-C2AE054A399E)).
- Named only: CTAB, CLAYOUT, CVPORT, LAYOUTCREATEVIEWPORT, LAYOUTREGENCTL, LAYOUTSPATIALFILTERS, MAXACTVP, MVIEWPREVIEW, SPACESWITCH, PSVPSCALE, UCSVP, VIEWTWIST, VPCONTROL, VPMAXIMIZEDSTATE ([G:A361F313](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A361F313-E1EB-400C-81B2-6B9AA2C0DDB7), [G:5E01CAFB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5E01CAFB-326D-4541-ADD3-C90A931FBC5E), [G:C0465010](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C0465010-3499-4D9D-B330-B9571C58790D)).

Dimensions
- DIMASSOC: 2 associative, 1 non-associative, 0 exploded; read at creation ([G:8B7E8C96](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B7E8C96-C30D-409E-881E-7942871E80DA)).
- DIMSCALE: overall scale of sizes; 0 = from each viewport's ratio ([G:30D6D9C8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30D6D9C8-AB99-47D1-B420-3D4EB6C7B0D1), [G:17FAE4A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-17FAE4A5-34C7-4D87-BFC5-E3791C083E73)).
- DIMLFAC: multiplier on measured linear values; leave 1.0 ([G:2D1177AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D1177AB-3130-4522-A631-AA28493529DC)).
- DIMLAYER: layer for new dimensions ([G:9A8AB1F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A8AB1F2-4754-444C-B90D-CD3F2FC8A3E0)).
- DIMCONTINUEMODE: 0 = current style for continue and baseline; 1 = style of the continued dimension ([G:DE060D4E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DE060D4E-FA55-4740-B3D8-CE9952B45734)).
- DIMDLI: baseline spacing; changing it later does not move placed dims ([G:4701B99C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4701B99C-7895-4265-9CC3-47D3C42A463E)).
- DIMTXT works only when the text style height is 0 ([G:38DAEEF0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-38DAEEF0-AB44-4C58-8D0E-955BFCFF71A7)). DIMGAP negative = frame ([G:38DAEEF0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-38DAEEF0-AB44-4C58-8D0E-955BFCFF71A7)). DIMCEN 0 / + / - = none / mark / centerline ([G:E063AF30](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E063AF30-6F14-42D6-B0AB-0CF5C47B5897)). DIMFRAC needs DIMLUNIT 4 or 5 ([G:AA5F50E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AA5F50E5-1376-4E5A-AEFB-55C9FB95E883)). DIMTOLJ 2 / 1 / 0 = top / middle / bottom ([G:BE52ACEE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE52ACEE-A046-412D-AEC8-593B9DEB674D)). DIMZIN and DIMTZIN also change rtos and angtos ([G:2D1177AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D1177AB-3130-4522-A631-AA28493529DC), [G:BE52ACEE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE52ACEE-A046-412D-AEC8-593B9DEB674D)).
- ANNOMONITOR: annotation monitor (named; inference: on/off) ([G:42802E38](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-42802E38-FD91-4550-8160-33B30AFAA875)).
- CENTERLAYER, CENTERMARKEXE (0 mark only, 1 with extensions), CENTERCROSSSIZE, CENTERCROSSGAP (relative `0.1x`, absolute, or ByLineType), CENTEREXE, CENTERLTYPE, CENTERLTSCALE, CENTERLTYPEFILE: center marks and centerlines, new objects only ([G:33A38BD6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-33A38BD6-03D0-426C-B62E-A83DC3E1F51D), [G:62AF9BD4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-62AF9BD4-FE63-4BF1-AC64-7C69D227B4CE), [G:AA0F538F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AA0F538F-350E-4FA5-AFA2-80A1238992C3), [G:E641F03D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E641F03D-7784-44BB-8228-4BDEC7641E06)).

Blocks and units
- INSUNITS, INSUNITSDEFSOURCE, INSUNITSDEFTARGET: insertion units and unitless fallbacks ([G:6C46049D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6C46049D-8636-442D-8BAC-CF4FD515FDC0), [G:58CEA276](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58CEA276-414D-4BE6-A878-C2AE054A399E)). INSUNITS also drives the underlay and image attach scale rule ([G:02FAF12D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02FAF12D-BA81-4124-86B5-8E381182C579), [G:ED93554F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-ED93554F-6006-4230-93FA-FBF6DCB00F28)).
- BLOCKEDITLOCK = 1 stops BEDIT ([G:B69D58AD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B69D58AD-7920-4198-AB2A-0E24B944F6CD)).

Xrefs
- REFPATHTYPE: default path type for attaching (default Relative) ([G:53030EDD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-53030EDD-1D1D-40C4-922E-9B964A048ED9), [G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667)).
- PROJECTNAME: current project for path searches; "." clears ([G:01B0493B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-01B0493B-944E-401F-A52D-82EFE874D16B)).
- XLOADCTL: 1 demand load and lock; 2 demand load from a copy ([G:3DE106E0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3DE106E0-95E7-493C-9C03-8EA2BB6FA90C)).
- XLOADPATH: folder for demand-load copies; empty = temp folder ([G:D0C84B3B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D0C84B3B-9A88-41B0-A8B6-162E2842A8A3)).
- INDEXCTL: index type for demand loading (named; values not given) ([G:5A45465D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5A45465D-287F-460A-91B5-2CB8593FC7F1)).
- XREFCTL: 1 writes <drawing>.xlg logs; default 0 ([G:1908D8C6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1908D8C6-5691-499B-8153-04D234D8B754)).
- XREFNOTIFY: change notification; interval via `(setenv "XNOTIFYTIME" "n")`, 1 to 10080 minutes, default 5 ([G:3DE106E0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3DE106E0-95E7-493C-9C03-8EA2BB6FA90C)).
- XREFLAYER: layer for new xrefs; freezing it hides the whole xref ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667)).
- VISRETAIN: 0 = xref layer changes last one session ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667)).
- XDWGFADECTL: xref fade percent ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667)). XFADECTL: fade of objects outside a REFEDIT working set ([G:CB42FBEC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CB42FBEC-212A-4050-A8DE-0774E6BF6928)).
- BINDTYPE: 0 = $#$ prefix on properties bound during REFEDIT; 1 = names unchanged ([G:EFA35F95](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EFA35F95-67B6-4B87-83A2-05928923CD2B)).
- ERHIGHLIGHT: reference highlighting; off is faster ([G:A987D2FF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A987D2FF-45BD-474E-99C1-E6316A42F667)).
- XCLIPFRAME: clip boundary display for xrefs ([G:58C43BAA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58C43BAA-B13F-479F-BA00-932BB75AD2C6)).
- POINTCLOUDLOCK: locks an attached point cloud ([G:8D698472](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8D698472-3435-4632-BEC8-301D417F760B)).

Underlays
- FRAME: frame display and plotting for ALL underlays ([G:38CC9880](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-38CC9880-3D94-4560-8A9B-7975F9C40A9C)). PDFFRAME, DWFFRAME, DGNFRAME, IMAGEFRAME: per type ([G:095BAA52](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-095BAA52-1D04-4491-98DF-1B6BC5C61C6D), [G:58C43BAA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58C43BAA-B13F-479F-BA00-932BB75AD2C6)).
- UOSNAP, PDFOSNAP, DWFOSNAP, DGNOSNAP: underlay snapping on or off, separate from OSNAP ([G:B8546EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B8546EA0-3B70-4971-8360-E0545B907A05)).
- DGNIMPORTMODE: default DGN import settings ([G:2A82AA09](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2A82AA09-4C1A-4737-910A-064D872F12B5)). DGNIMPORTMAX, DGNMAPPINGPATH: named only ([G:319794A8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-319794A8-DFFA-4EA7-9673-72DE61EE8C16)).

3D output
- 3DDWFPREC: 1 to 6, 3D DWF smoothness and size ([G:792617AA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-792617AA-2DB3-4870-A739-C9225A5889DD)).
- FACETRES: STL facet density ([G:250152B2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-250152B2-7CA2-4F22-8A47-7F74FEBF6FAD), [G:4B5C0F42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4B5C0F42-2B82-49F0-946E-C1E22C8D7336)).
- SMOOTHMESHCONVERT: named only ([G:A989E491](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A989E491-9EB1-4A48-95BE-63FA0605AE97)).

## 15.23 Block Editor, dynamic blocks and wildcards (reference)

Block Editor (BEDIT) ([G:B69D58AD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B69D58AD-7920-4198-AB2A-0E24B944F6CD), [G:B6BF48AD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B6BF48AD-9408-4BE8-992D-4B7823F790F5), [G:A0477C1A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A0477C1A-493B-4CEC-8B42-171015D47EA4))
- BEDIT opens the Edit Block Definition dialog [GUI], then the Block Editor. Typing a new name starts a new definition; <Current Drawing> opens the whole drawing to save it as a dynamic block. Double-clicking a reference also opens it. BLOCKEDITLOCK = 1 stops the editor from opening [AUTO].
- Commands that work only inside the editor: BACTION, BACTIONBAR, BACTIONSET, BACTIONTOOL, BASSOCIATE, BATTORDER, BAUTHORPALETTE, BAUTHORPALETTECLOSE, BCLOSE, BCPARAMETER, BCYCLEORDER, BCONSTRUCTION, BGRIPSET, BLOOKUPTABLE, BPARAMETER, BSAVE, BSAVEAS, BTABLE, BTESTBLOCK, BVHIDE, BVSHOW, BVSTATE.
- The UCS command is disabled in the editor; the UCS icon origin is the block's base point.
- Parameters can be added to a 3D block but cannot be edited along Z. Solids in a dynamic block cannot be stretched or edited by actions.
- Save Block stores a definition even with no objects. BSAVEAS can also write the block to its own DWG ("Save Block Definition to Drawing File"). ([G:91EFB2C6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-91EFB2C6-FF31-4ECF-AB82-6E25537574D2), [G:3B30840F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3B30840F-739C-4B97-92CA-6BAA98FCDAE8))
- Block units of an existing block: BEDIT > Properties > Block > Units, then save. Scale Uniformly and Allow Exploding are set in the same place. ([G:B2136517](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B2136517-DF1F-4BD1-A8FD-C1F91D438AF9), [G:AF1F77D4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AF1F77D4-42BA-4B13-8E4E-9CF939EF81DD), [G:ED407915](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-ED407915-A83E-4165-ABE6-C96A3663B307))

Dynamic block parts ([G:B69D58AD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B69D58AD-7920-4198-AB2A-0E24B944F6CD))
- Parameters: Point, Linear, Polar, XY, Rotation, Alignment (whole block, no action), Flip, Visibility (whole block, no action), Lookup, Base Point (no action).
- Actions: Move, Scale, Stretch, Polar Stretch, Rotate, Flip, Array, Lookup.
- Parameter Sets add a parameter and its action(s) together; attach the selection with BACTIONSET.
- Constraints: geometric GC* constraints (GCCOINCIDENT, GCPERPENDICULAR, GCPARALLEL, GCHORIZONTAL, GCVERTICAL, GCEQUAL, GCFIX and others) and constraint parameters (Aligned, Horizontal, Vertical, Angular, Radial, Diameter). Not in AutoCAD LT.
- Visibility states: BVSTATE dialog; BVSHOW and BVHIDE set objects visible or hidden in the current or all states.

Wildcards (not every feature supports them) [AUTO] ([G:68373F99](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-68373F99-17F1-4AC4-8D37-184C49164705))
- `#` any digit; `@` any letter; `.` any non-alphanumeric character; `*` any string, anywhere; `?` any one character; `~` NOT the pattern (`~*AB*` = strings without AB); `[AB]` one of the listed; `[~AB]` none of the listed; `[A-G]` a range; reverse quote (backtick) reads the next character literally.
- Used, for example, by RENAME Old Name, DesignCenter search and data extraction folder filters. ([G:D6330A0F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D6330A0F-E738-47B3-BAA3-6F5AB93600AC), [G:95EE2918](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-95EE2918-9C4A-4FE7-A333-7A35A58AC90D), [G:B57E9DB5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B57E9DB5-A4CE-47B7-911F-B607B7564299))
