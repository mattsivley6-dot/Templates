# 06 - Parts, Catalogs, MvParts and Content Builder

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

Covers the content system of the AutoCAD MEP 2027 toolset (US Imperial). Catalog-based content (segments, fittings, MvPart equipment) lives in part catalogs (APC file plus XML, DWG and BMP per part family). Style-based content (devices, panels, plumbing fittings, schematic symbols) lives as styles in content drawings.
It covers where catalogs live on disk and how a drawing loads them, placing and modifying MvParts, the catalog commands (CATALOGREGEN, CATALOGTEST, CatalogMigrate, RedefineFromCatalog), Catalog Editor, Content Builder (block-based and parametric parts, connectors, sizes, custom parameters, testing) and the style-based conversion tools.
Almost all part authoring is dialog-only. Lines tagged [AUTO] matter for scripts; [GUI] means dialog, palette or grip only.
Legend: G:XXXXXXXX links to an AutoCAD MEP 2027 help page (first 8 characters of its GUID); KB:n links to an Autodesk support article; (inference) marks a conclusion the cited pages do not state; (test install) = seen on one AutoCAD MEP 2027 US install by a read-only folder listing, not from Autodesk docs.

Contents
- 6.1 Content types
- 6.2 Where content lives
- 6.3 Loading catalogs: Options > MEP Catalogs tab and profiles
- 6.4 MvParts (equipment) in drawings
- 6.5 Catalog maintenance commands [AUTO]
- 6.6 Catalog Editor
- 6.7 Content Builder: start-up, rules, choosing a method
- 6.8 Block-based MvParts
- 6.9 Parametric parts: model concepts
- 6.10 Parametric parts: workflow, connectors, sizes, behaviors, symbols, save
- 6.11 Custom parameters and size data
- 6.12 Testing parts
- 6.13 Style-based content customization
- 6.14 Content tools: tool palettes and Content Browser
- 6.15 Troubleshooting index
- 6.16 What a script can and cannot do here

## 6.1 Content types

### Catalog-based vs style-based
- Catalog-based: duct, pipe, cable tray and conduit segments and fittings, and MvParts. Stored in part catalogs (APC). Built in Content Builder, edited in Catalog Editor. ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0), [G:6324961B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6324961B-138E-480D-BF9A-E2CDF742525B))
- Style-based: devices, panels, plumbing fittings, schematic symbols. They are styles in content library drawings, edited in Style Manager and the batch conversion tools. ([G:624C7B6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-624C7B6B-2E56-4620-80DA-B3354F65902D), [G:8AE18F38](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AE18F38-D993-40B5-A15C-50DE616CC6DA))
- [G:DF3201A3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF3201A3-BC08-49CF-9228-23C3AF2D5999) also lists MvParts among style-based content and calls all of it MvBlocks with smart connectors. Other pages treat MvParts as catalog content. ([G:DF3201A3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF3201A3-BC08-49CF-9228-23C3AF2D5999), [G:6324961B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6324961B-138E-480D-BF9A-E2CDF742525B))

### Parametric vs block-based parts
- Parametric: one 3D model driven by size parameters (single value, list of values, or equation). One family can cover many sizes. Good for simple shapes in many sizes: air terminals, junction boxes, tanks, elbows, tees, crosses. ([G:E6A99ECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6A99ECD-2329-4E69-9B27-9D5537FB02F9))
- Block-based: an MvPart where each size has its own 3D model AutoCAD block, plus 2D view blocks and connector placement. Good for complex equipment in few sizes: AHUs, motor control centers, pumps. ([G:E6A99ECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6A99ECD-2329-4E69-9B27-9D5537FB02F9), [G:4CB9ED4F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4CB9ED4F-8D9C-467A-A330-9E96945D2F67))
- Help rule of thumb: parametric for simple design with many sizes; block-based for complex design with few sizes. ([G:E6A99ECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6A99ECD-2329-4E69-9B27-9D5537FB02F9))
- Fittings MUST be parametric. Simple MvParts (air terminals, fans) may be parametric. ([G:44EED615](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-44EED615-0D8C-4667-B6E2-D32E13EFCA2E), [G:E6A99ECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6A99ECD-2329-4E69-9B27-9D5537FB02F9))
- Both kinds change look with view direction. Parts can carry behaviors (auto cleanup at connections, default insertion) and components (centerline, insulation, lining). ([G:E63ED223](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E63ED223-BF7D-488A-8C6C-41FC0C055E30))

### Equipment = MvParts
- Equipment is placed as Multi-view Parts (MvParts). They model size and shape and carry connectors. Organized by type in part catalogs; which catalogs are available comes from Options (initialization preferences). ([G:002C08FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-002C08FC-9076-47B2-A3CA-86D3BCCB4729))
- An MvPart is not a block or dynamic block. Click the "+" on a connector to start a run at the right size and type. (KB:x-56PmvkbM)
- MvBlocks (for example in an architectural xref) look like MvParts but do not connect. Convert them to MvParts to add connectors (6.4). ([G:002C08FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-002C08FC-9076-47B2-A3CA-86D3BCCB4729), [G:AA3A85B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3A85B6-8F56-416A-9541-02DACF6F4472))
- HVAC catalog: hundreds of parts in thousands of sizes, rooftop units to grilles. Air terminals and VAV boxes take flow values used for duct sizing. ([G:2D45FAA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2D45FAA0-DE66-4E86-89D3-3377A7460788))
- Pipe MvParts: chillers, boilers, cooling towers, valves, sprinklers. An MvPart can switch type (ball valve to butterfly valve); types split into subtypes. ([G:7CEC8CE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CEC8CE1-F652-41AA-9F22-80DE105C5F2B))
- Electrical equipment MvParts connect only to conduit and cable tray, not to circuits. Junction box exists as a device (circuits, wires) and as an MvPart (connects to conduit by nominal size). ([G:031F9C4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-031F9C4D-0BC2-4D3D-918A-00B5F4F08452))
- No manufacturer libraries ship. Shipped content is generic; get manufacturer content from the manufacturer. ([KB:000427790](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Does-AutoCAD-Architecture-MEP-ship-with-manufacturer-specific-libraries.html))
- Valve actuators have no connectors by design; they sit on top of valves. ([KB:000654038](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/There-are-no-connectors-available-for-valve-actuators-in-AutoCAD-MEP.html))
- Sprinklers: Home tab > Build panel > Equipment > Mechanical > Fire Protection > Sprinklers. ([KB:000504275](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-add-Sprinklers-in-AutoCAD-MEP.html))

## 6.2 Where content lives

### Part catalog files
- A part catalog = an APC file plus chapter folders. Help pages call APC "Autodesk Part Catalog" ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0)) and "Autodesk product catalog" ([G:67D95B84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67D95B84-81D8-47FA-AB9E-806D280E354A)).
- Each part family = 3 definition files named after the family: XML, DWG, BMP. Deleting a family in Content Builder deletes all three. ([G:4178DA80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4178DA80-9688-4292-A100-8392202699D6), [G:6998640F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6998640F-44D9-44CB-856D-A8BAEB6EE253))
- The family Name typed in the New Part dialog names those files. The Description is the label users see when picking parts. ([G:0958907D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0958907D-AAF1-483B-9440-11A1511CE87C), [G:79CD8F4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-79CD8F4E-8DEE-4767-8753-F76F2180F1EC))
- (test install) Confirmed: MEPContent\USI\MvParts\Mechanical\Chillers\ holds Air-Cooled Chiller.xml, .dwg, .bmp, plus "Air-Cooled Chiller Template" files (inference: templates for the Parametric Part Wizard, which uses shipped part templates per [G:9F57B992](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F57B992-77E9-448B-BF3D-6C0732F474F5)).

### Default US Imperial part catalogs (test install) [AUTO]
Root: C:\ProgramData\Autodesk\MEP 2027\enu\MEPContent\USI\

| Domain | APC file(s) under the root |
|---|---|
| Cable Tray | Cable Tray\Cable Tray (US Imperial).apc |
| Conduit | Conduit\Conduit (US Imperial).apc |
| Duct | Duct\Duct (US Imperial).apc; also Duct (EN 1505)\Duct (EN 1505).apc |
| MvParts | MvParts\All Installed MvParts (US Imperial).apc; plus MvParts\Electrical\Electrical MvParts (US Imperial).apc, MvParts\Mechanical\Mechanical MvParts (US Imperial).apc, MvParts\Plumbing\Plumbing MvParts (US Imperial).apc |
| Pipe | one APC per material, no single pipe APC: Pipe\Cast Iron\Cast Iron Pipes.apc, Pipe\Copper\Copper Pipes.apc, Pipe\Ductile Iron\Ductile Iron Pipes.apc, Pipe\General\General Pipes.apc, Pipe\HDPE\HDPE Pipes.apc, Pipe\Plastic\Plastic Pipes.apc, Pipe\Steel\Steel Pipes.apc |

- Other packs seen on the test install: Global, USM (US Metric), UK, DAN, SVE. Name patterns differ per pack, e.g. "Duct (Global).apc", "Duct DAN.apc", "Pipework (UK).apc". (test install)
- [KB:000428447](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-content-file-specified-for-this-tool-cannot-be-found-for-MEP-content-in-AutoCAD-MEP.html) gives a generic pattern MEPContent\<yyy>\Pipe\Pipe <yyy>.apc and ...\MVParts\MVParts <yyy>.apc with <yyy> = Global, Imperial or Metric. That pattern does NOT match the USI pack on the test install (folder USI, file "All Installed MvParts (US Imperial).apc", pipe split by material). Use the real paths above.
- Steel pipe chapters (test install): Butt Welded, Flanged, Grooved, Pipes, Socket Welded, Threaded. Fitting names follow the help convention Connection Type - Schedule/Class - Part Type, e.g. "Threaded - Sch 40 - Basin Tee". ([G:44EED615](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-44EED615-0D8C-4667-B6E2-D32E13EFCA2E))
- USI MvParts\Mechanical chapters (test install) include Air Separators, Air Terminals, Boilers, Chillers, Coils, Cooling Towers, Dampers, Fans, Heat Exchangers, Heat Pumps, Modular Air Handling Units, Pumps, Roof Mounted AC Units, Split System Air Handlers, Strainers, Suction Diffusers, Tanks, VAV Units, Valves, Vertical Fan Coil Units. The help says pipe MvParts such as chillers come from the plumbing part catalog ([G:7CEC8CE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CEC8CE1-F652-41AA-9F22-80DE105C5F2B)); on the test install they sit in MvParts\Mechanical, while MvParts\Plumbing holds fixtures, pumps and water heaters.

### Doc conflict: "Tool Catalogs" vs "MEPContent"
- [G:4178DA80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4178DA80-9688-4292-A100-8392202699D6) says catalog part DWGs are in \ProgramData\Autodesk\MEP <version>\enu\Tool Catalogs, then gives an example under \enu\MEPContent\USI\MvParts\Mechanical\Roof Mounted AC Units. [G:67D95B84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67D95B84-81D8-47FA-AB9E-806D280E354A) says to open APC files from "\ProgramData\Autodesk\MEP <version>enu\Tool Catalogs" (backslash missing on the page). Support articles use MEPContent. ([KB:000428447](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-content-file-specified-for-this-tool-cannot-be-found-for-MEP-content-in-AutoCAD-MEP.html), [KB:000576793](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Create-a-cable-tray-catalog-in-Autocad-MEP.html), [KB:000600828](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-catalog-files-in-AutoCAD-MEP.html))
- (test install) \enu\Tool Catalogs holds TOOL catalogs (e.g. "MEP Documentation (US Imperial)", "Design - Imperial"). Part catalogs are under \enu\MEPContent\<pack>\. Trust MEPContent.

### Part names for scripting
- [AUTO] Each part family's XML file holds the part name as the catalog stores it (the name MVPARTADD and PIPEADD look up), its subtype, nominal size range and end style. Build your own inventory from those XML files and look up exact part names and size ranges there before scripting a placement.

### Shared content and config files
- Shared Content Path (Options > MEP Catalogs tab) = generic part templates, primitives and config files. Required whatever content pack (Global, US Metric...) is in use. ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0))
- Primitives: \ProgramData\Autodesk\MEP <version>\enu\Shared\Primitives, one DWG + BMP each. ([G:90661905](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90661905-C46C-4E0C-951B-8FB255104DBF)) (test install) present: Box, Cone, Cylinder, Dome, Brazed / Buttweld / Flanged / Glued Pipe Connector, Cable Tray Connector, Conduit Connector, and others.
- [AUTO] \Shared\AecbCatalogConfig.xml: if duct, pipe or conduit placement fails with a write error, check that AecbTableExpandMode is 1 (a value of -1 is the known cause) and that Shared Content Path points at a real folder. ([KB:000426613](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-write-to-file-check-write-permissions-is-received-when-adding-MEP-objects-in-AutoCAD-MEP.html))
- (test install) \Shared also holds AecbCatalogTemplate_<Domain>.xml, AecbPartWizardTemplates.xml, AecbRequiredParams.xml, AecbDomainConfig.xml. Their roles are not documented in these sources.

### Support file locations ([G:50705C4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-50705C4B-D737-4BE7-9ACF-44EED6C40871) unless noted)
<version> = product version folder (MEP 2027).
- Plotter configurations: \ProgramData\Autodesk\MEP <version>\enu\Plotters; plot styles in ...\Plotters\Plot Styles
- DesignCenter content: \ProgramData\Autodesk\MEP <version>\enu\AEC Content
- Layer standards drawing: \ProgramData\Autodesk\MEP <version>\enu\Layers. (test install) AecbLayerStd4.dwg is there, with AecbLayerStd, 2010, 2013, 3, 5, 7.
- Styles drawings: \ProgramData\Autodesk\MEP <version>\enu\Styles
- Drawing templates: the page says \enu\Templates. (test install) the folder is \enu\Template (singular) and holds "Aecb Model (US Imperial Ctb).dwt" and "Aecb Model (US Imperial Stb).dwt".
- Area Evaluation templates: \enu\Template\Evaluation Templates (needs the Architecture content packs installed).
- Workspace UI catalog: %APPDATA%\Autodesk\MEP <version>\enu\Support\WorkspaceCatalog AME (Global/USImperial/USMetric)
- Stock Tool Catalog: \Program Files\Autodesk\AutoCAD <version>\Catalogs\MEP Stock Tool Catalogs
- Structural Member Catalog: \Program Files\Autodesk\AutoCAD <version>\Catalogs\Structural
- Sample palette catalogs: \Program Files\Autodesk\AutoCAD <version>\Sample\MEP Sample Palette Catalog (Global/US Imperial/US Metric)
- Catalog Editor: \Program Files\Autodesk\AutoCAD <version>\MEP\AecbCatalogEditor.exe ([G:32547D08](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32547D08-37B2-46D1-A518-791B1D77D5D4)). (test install) present for 2027.
- Catalog validation and regen reports: <folder of the APC>\Validate\ ([G:7BAF2064](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7BAF2064-25FD-44EA-A018-30ADE8B2CFF9), [G:CC6F94C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CC6F94C5-9049-4703-9528-E53916E74387))
- Custom parameter group XLS files: default subfolder "MEP Parameter Groups" ([G:7269A48E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7269A48E-5794-4A34-B623-624CF1337344))
- (test install) Style-based content drawings for US Imperial: MEPContent\USI\Electrical\Devices, MEPContent\USI\Electrical\Panels, MEPContent\USI\Plumbing\Plumbing Fittings (US Imperial).dwg and Plumbing Valves (US Imperial).dwg, MEPContent\USI\Schematic\*.dwg (e.g. "Fire Alarm (US Imperial).dwg"). (inference) These are what the Style-Based Content Paths on the MEP Catalogs tab point to.

## 6.3 Loading catalogs: Options > MEP Catalogs tab and profiles

### MEP Catalogs tab [GUI] ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0))
- Options > MEP Catalogs tab. Under Catalogs expand a domain (e.g. Duct) and set the catalogs available during layout.
- Add: pick the category > Add > browse to the APC > Open. Remove: select > Remove. Replace: select > Browse > APC > Open. Reorder: Move Up / Move Down.
- List order = order shown in part selection during layout. Several catalogs per domain are allowed (shipped duct plus custom duct).
- RULE: if two parts in different catalogs share an ID or a name, only the part from the catalog HIGHER in the list shows in part selection (adding MvParts, picking pipe fittings for a routing preference definition).
- Style-Based Content Paths: per content type (electrical devices, electrical panels, plumbing fittings, schematic symbols) click the Path value, then the button beside it, pick the folder, Open.
- Shared Content Path: see 6.2. Local content uses local paths; shared content uses network paths.
- Content Builder lists the catalogs on this tab ([G:082E1B71](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-082E1B71-3EBD-45E6-8A1A-CA59F7784639)). CATALOGREGEN and CATALOGTEST act only on catalogs listed here ([G:7BAF2064](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7BAF2064-25FD-44EA-A018-30ADE8B2CFF9), [G:CC6F94C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CC6F94C5-9049-4703-9528-E53916E74387)). A new or modified catalog must be loaded here before its parts can be picked in a drawing. ([G:97EB715D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97EB715D-08A7-4AAC-9757-1759EDD010C2), [G:E996EBFA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E996EBFA-FD84-4532-B1FD-6C00E86EEAC6))
- Fitting choices in the Select a Part dialog (Properties palette) also come from the loaded catalogs and content locations. ([G:3C01D8C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3C01D8C8-551C-47B8-BD22-E06DEBD87246))
- Routing preferences pick catalog fittings during layout. If a part, angle or transition is not defined in the current routing preference, the toolset prompts for a part substitution. ([G:DC5B76BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC5B76BF-0503-4F30-9228-96DE1E78AB8D))

### Custom content rules
- Put ALL custom parts in your own custom catalogs. Never add them to the shipped catalogs. At upgrade, move the whole custom catalog into the new version's catalog folders and list it beside the new shipped catalogs. ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0), [G:E0912FC5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0912FC5-7AFA-49F1-8B87-DF8DF17174D2), [G:082E1B71](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-082E1B71-3EBD-45E6-8A1A-CA59F7784639))
- Back up the shipped catalogs (copy the folders in Explorer) before using Content Builder so you can revert. ([G:C0CC1782](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0CC1782-4848-4AA9-8104-4447FB14560C))
- Support recipe for a custom catalog: duplicate the shipped catalog folder, open the copy's APC in Catalog Editor, edit. ([KB:000576793](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Create-a-cable-tray-catalog-in-Autocad-MEP.html))
- An error saying the catalog or APC cannot be created means no write permission; save the catalog on a local writable drive. ([KB:000624685](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-Create-New-Catalog-or-Generate-APC-File-in-AutoCAD-MEP.html))
- Catalogs on a cloud drive misbehave: ACA/MEP need absolute local paths to catalogs and dependent files. Each user downloads catalogs and dependent content to a local folder. ([KB:000470301](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Shared-Custom-Catalogs-on-the-Cloud-for-AutoCAD-Architecture-and-MEP.html))

### The profile decides which content loads
- The launch profile sets every content path. "AutoCAD MEP (Global)" loads global catalogs only. Under the Global or US Metric profile, equipment inserts as metric in an imperial drawing. Fix: OPTIONS > Profiles tab > pick the US Imperial profile > Set Current > OK. ([KB:000440790](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-only-shows-global-catalog-content-although-other-content-is-needed.html), [KB:000343982](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Convert-equipment-from-metric-to-imperial-in-an-existing-imperial-drawing-in-AutoCAD-MEP.html))
- [AUTO] Desktop icons launch acad.exe with a profile switch. Article example (2025): "C:\Program Files\Autodesk\AutoCAD 2025\acad.exe" /ld "C:\Program Files\Autodesk\AutoCAD 2025\AecBase.dbx" /p "<profile>" /product "MEP" /language "en-US". Profiles include "AutoCAD MEP (US Imperial)", "AutoCAD MEP (Global)", "AutoCAD MEP (US Metric)", "AutoCAD MEP (UK)". ([KB:000601104](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Some-MEP-equipment-might-vary-in-scale-size-when-inserted-into-the-drawing-in-AutoCAD-MEP.html)) (inference) 2027 uses the same pattern under ...\AutoCAD 2027\; not verified here.
- Do not hand-edit the MEP Catalogs list to fix a units problem; start the right profile. Start drawings from a template that matches the profile ("Aecb Model (Global Ctb).dwt" is metric). The "+" drawing tab reuses the last template used. ([KB:000601104](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Some-MEP-equipment-might-vary-in-scale-size-when-inserted-into-the-drawing-in-AutoCAD-MEP.html))
- Imperial profile with a metric catalog (or the reverse) gives wrong part sizes and wrong Add-grip results. Missing catalogs give "place holder" pipes drawn single-line. ([KB:000482051](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-created-via-the-Add-grip-are-using-wrong-size-and-type-of-pipe-in-AutoCAD-MEP.html), [KB:000421543](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-always-display-as-single-line-even-in-a-isometric-view-in-AutoCAD-MEP.html))
- A wrong-size symbol keeps its size on re-insert because its block definition stays in the drawing. Delete all instances, PURGE, re-insert. [AUTO] ([KB:000601104](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Some-MEP-equipment-might-vary-in-scale-size-when-inserted-into-the-drawing-in-AutoCAD-MEP.html))
- Custom MvPart catalog missing from the Equipment tool: confirm it is in the Multi-view Part list on the MEP Catalogs tab, move it to first place, and add its folder to Support File Search Path (Options > Files). ([KB:000429805](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Custom-MVPart-catalog-not-available-in-AutoCAD-MEP.html))

## 6.4 MvParts (equipment) in drawings

### Add equipment: MVPARTADD [GUI dialog] ([G:B412560B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B412560B-4408-40A6-AF30-1E8BA6C5170E), [G:2DC6F9D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2DC6F9D1-14AA-4448-842B-99E5C81EDE70))
- Command MVPARTADD. Ribbon: Home tab > Build panel > Equipment drop-down > pick equipment; or the Equipment tool palette of the workspace palette group. Onto a conduit run: select the conduit > Conduit tab > General panel > Insert Equipment.
- Opens the Add Multi-view Parts dialog: tree of the current catalog, opened at the part type folder tied to the tool.
- Part tab: pick a subtype in the part type folder; Details shows the sizes; Part Filter tab narrows long lists (connection size or type); pick Part Size Name; set Elevation (a defined elevation or a typed value).
- Click an insertion point; the compass sets the rotation. Repeat to add more with the same settings. Enter ends the command.
- Plumbing fixtures only: Fixture Units tab (fixture unit table, fixture type, occupancy public or private). Each connector gets a default fixture unit value from its system type and the table; plumbing line sizing later uses the stored values. Check them. ([G:2DC6F9D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2DC6F9D1-14AA-4448-842B-99E5C81EDE70))
- Parts offered depend on the catalogs and content locations in Options. A missing part means building a custom part in Content Builder. ([G:B412560B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B412560B-4408-40A6-AF30-1E8BA6C5170E))
- [AUTO] No command-line (hyphen) form of MVPARTADD and no prompt sequence appear in these sources. (inference) A script that runs MVPARTADD will meet the dialog; scripted placement needs another route, which these sources do not cover.

### Insertion method of an MvPart ([G:A34FB751](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A34FB751-C54B-4AD0-9685-A1860D8D06CE), [G:5A3DAB85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5A3DAB85-94A1-456C-B1A0-EB134862EC9A))
- Anchor: the part anchors to the picked segment or object and moves with it (louver on a segment).
- Breaks into: the part splits the picked segment in two (valve). It stays its own component, slides along the run, and the neighbors trim or stretch. These are "in-line parts".
- Both set on the part: the software asks which one each time the part is added. Neither set: it inserts like a plain AutoCAD block.

### Modify equipment: MVPARTMODIFY [GUI dialog] ([G:D719C222](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D719C222-6F3C-4C7B-BCE5-CFE0B5F5900F), [G:5EBBE7D5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5EBBE7D5-7D6D-4A14-A1A1-88B4BF4A4085))
- Select the MvPart > Equipment tab > Modify panel > Modify Equipment. Multi-view Part Modify dialog > Part tab > All Installed MvParts: pick a part (expand subfolders).
- Part Size Name lists sizes in the range of the current part. Size missing: Part Filter tab > Connections > Nominal Connection, pick a size range (format like 4-72); Display: type a number inside the allowed range to limit how many sizes show. Two step buttons under the part image walk through size names.
- Changing Elevation of a connected MvPart keeps connected objects connected and moves them to the new elevation.
- Equipment changes can force circuit changes (electrical) or connected plumbing line changes. Fixtures: Fixture Units tab.
- Switching an MvPart to another type (ball valve to butterfly valve) is task "To Match an MvPart of One Type to Another", not in these sources. ([G:7CEC8CE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CEC8CE1-F652-41AA-9F22-80DE105C5F2B))
- Catalog edits reach only parts added AFTER the edit; parts already in drawings do not update ([G:90577BAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90577BAD-0F5D-4203-B44F-18CBD9C9CD5E), [G:9890237D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9890237D-00F2-4CD5-8A21-8763CE8C464C)). See RedefineFromCatalog (6.5) for updating legacy drawings.

### Convert blocks or MvBlocks to MvParts: MVPARTCONVERT [GUI] ([G:AA3A85B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3A85B6-8F56-416A-9541-02DACF6F4472))
- Command listed: MVPARTCONVERT. Converts AutoCAD solids, mass elements, blocks or MvBlocks to MvParts. Works on an MvBlock inside an xref. Same steps for every discipline.
1. Select the element or block > right-click > Convert to Multi-view Part.
2. Multi-view Part Convert - Behavior dialog: part name, Type, Subtype, layer key > Next.
3. Multi-view Part Convert - Connectors: right-click the MvPart name > pick the connector type > Part Family Connector Properties dialog > OK. Repeat per connection.
4. Select a connection > right-click > Edit Placement. "MvPartBuilder - Connector Editor" opens. Pick Position for Connector, then place it. Object snaps, 3D Orbit and Pan help.
5. Direction: pick a vector or type the Normal under Connector Geometry (pipe connector flowing out downward = 0,0,-1).
6. Pick the other connectors at the top of the Connector Editor; OK closes it.
7. Later: right-click a connector > Modify; placement, direction or size: Edit Placement. Finish.
- Result: a new MvPart at the same location; the original block stays. The MvPart exists only in the drawing, not in a catalog. Copy and paste for more. Edit: select > right-click > Edit MvPart Style. To put it in a catalog, build it in Content Builder. ([G:AA3A85B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3A85B6-8F56-416A-9541-02DACF6F4472))
- Conflict: [KB:000413610](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Mv-Part-with-connectors-from-3D-Geometry-Block-in-AutoCAD-MEP.html) says a converted MvPart cannot be changed afterward because it lives in no catalog; [G:AA3A85B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3A85B6-8F56-416A-9541-02DACF6F4472) says edit it with Edit MvPart Style. (inference) Style edits inside the drawing work; catalog editing does not.
- [KB:000413610](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Mv-Part-with-connectors-from-3D-Geometry-Block-in-AutoCAD-MEP.html) walks the same route with slightly different menu labels; the steps match the list above.
- Clean up the 3D data first. Give the block a unique, clear name: generic names cause trouble when copying between files because block definitions are not overwritten on copy. ([KB:000413610](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Mv-Part-with-connectors-from-3D-Geometry-Block-in-AutoCAD-MEP.html))

### Import Inventor content (.adsk) [GUI] ([G:110A4B25](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-110A4B25-DB3C-4C94-937A-E9D726D89842), [G:5105DF4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5105DF4E-0BD6-4911-B5C4-02B7C2B62272))
- Prepare in Inventor and save as a Building Component Autodesk Exchange file (*.adsk).
- Insert tab > Content panel > Content Browser drop-down > Building Component. Import Building Component dialog: pick the .adsk and choose MvPart, block or multi-view block. Import dialog: name, description, orientation at insertion (any axonometric view inserts the 3D part; ViewCube; Rotate buttons about X, Y, Z); pick a catalog chapter; Add.

### Standard vs custom part sizes ([G:258A9D37](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-258A9D37-933F-4F36-B3EB-C1C17F86A730), [G:F36E8B05](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F36E8B05-BFBC-4096-A969-934EAC8A29F1), [G:5A3DAB85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5A3DAB85-94A1-456C-B1A0-EB134862EC9A))
- Options > MEP Layout Rules tab > Part Selection: Use Catalog Parts Only | Prompt when Non-Standard Parts are Needed (accept = custom part made; decline = last segment drawn is removed) | Use Non-Standard Parts.
- Custom sizes made during layout (e.g. an elbow at an angle the catalog lacks) live only in the current drawing; they are not saved to catalogs. For routine custom sizes, build catalog content.
- On the part side, the Custom Sizing Flag (Content Builder Options dialog) allows custom sizes when the catalog lacks the needed size; Auto Layout or the Add dialog part filter and values can then insert them. ([G:5A3DAB85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5A3DAB85-94A1-456C-B1A0-EB134862EC9A))
- A custom-size prompt for a size the catalog really has (for example on cable tray) points to a corrupted profile or a bad settings migration; reset to defaults. A truly missing size needs a catalog edit. ([KB:000646581](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/This-part-is-not-available-in-the-size-needed-would-you-like-to-create-a-custom-size-error-when-inserting-MEP-parts-in-AutoCAD-MEP.html))

## 6.5 Catalog maintenance commands [AUTO]
All four sit on Manage tab > MEP Content panel and ask for a domain keyword on the command line.

| Ribbon button | Command | Prompt (exact page text) |
|---|---|---|
| Regenerate Catalog | CATALOGREGEN | Catalog Regen [Cabletray/cOnduit/Duct/Mvpart/Pipe/All] |
| Test Catalog | CATALOGTEST | Catalog Test [Cabletray/Conduit/Duct/Mvpart/Pipe/All] |
| Migrate Catalog | CatalogMigrate | Catalog Migrate [Cabletray/cOnduit/Duct/Mvpart/Pipe/All] |
| Redefine From Catalog | RedefineFromCatalog | Redefine the parts of the type [Cabletray/cOnduit/Duct/Mvpart/Pipe/Select] <Select>: |

([G:7BAF2064](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7BAF2064-25FD-44EA-A018-30ADE8B2CFF9), [G:CC6F94C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CC6F94C5-9049-4703-9528-E53916E74387), [G:B367AB9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B367AB9C-64E9-4CE6-BC0A-C6AB0DD98005), [G:B28E1DAC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B28E1DAC-5539-4A4B-9EE1-3753FE00956F))
- Pages give only a = All, d = Duct, p = Pipe, then Enter. (inference) Other letters follow the capitals: C Cabletray, O cOnduit, M Mvpart, S Select.
- CATALOGTEST prints "Conduit" with a capital C, the same letter as Cabletray (checked on the source page). No conduit letter is given. Test live before scripting conduit validation. ([G:CC6F94C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CC6F94C5-9049-4703-9528-E53916E74387))
- CATALOGREGEN and CATALOGTEST names come from page metadata; CatalogMigrate and RedefineFromCatalog are given as typed names.

### When to validate and regenerate ([G:368D03AB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-368D03AB-E5B6-4A2E-A992-E592AE92E00B))
- After any catalog change. Only regenerated catalogs can be used; only validated parts show in part selection.
- Content Builder and Catalog Editor validate and regenerate automatically on save. Run the commands by hand for catalogs received from others or migrated from older releases.

### CATALOGREGEN ([G:7BAF2064](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7BAF2064-25FD-44EA-A018-30ADE8B2CFF9))
- Precondition: the catalog is listed on Options > MEP Catalogs tab. Only listed catalogs load, so only they regenerate.
- Updates the APC to show new or deleted part sizes. Several catalogs on one domain regenerate in list order.
- Results dialog. Full log: <APC folder>\Validate\Catalog_Regen_Summary.txt; use it to confirm a part was added or removed.
- End: click OK, then press Enter. (inference) A script must clear that results dialog or it stalls.
- Sizes missing or not removed: fix in Catalog Editor and regenerate again.

### CATALOGTEST ([G:CC6F94C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CC6F94C5-9049-4703-9528-E53916E74387))
- Same precondition. Walks the catalog and checks each part size has its required data: AoD (angle of deflection) and CEL (connection engagement length) parameters. Conduit content without the nominal size property fails.
- Results dialog. Full log: <APC folder>\Validate\Catalog_Validation_Summary.htm. End: OK, then Enter.
- Fix errors in Catalog Editor: open the catalog, go to the part, edit its data.

### CatalogMigrate ([G:B367AB9C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B367AB9C-64E9-4CE6-BC0A-C6AB0DD98005))
- Upgrades the version and parameter data of existing catalogs for one domain or all: version number plus connector data such as CEL, AoD and nominal size.
- Progress bar (part number, total parts, catalog). Report: error count, affected parts, link to a results file. End: OK, then Enter.
- Page example wording slip: "to regenerate the catalogs specified for Pipe, type p".
- Then bring existing drawings up to date with RedefineFromCatalog.

### RedefineFromCatalog ([G:B28E1DAC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B28E1DAC-5539-4A4B-9EE1-3753FE00956F))
- Reviews pipe, cable tray, conduit, duct, fittings and MvParts in a legacy drawing and updates eligible parts and the styles of selected objects.
- RULE: a part is swapped only if it is already in the drawing AND a part in the loaded catalogs for that domain matches its part ID and other parameters. No match: left unchanged.
- Select is the default answer; the page does not describe what Select asks next.
- Progress bar; final report: parts reviewed, parts updated, link to a details file.
- Legacy conduit: nominal size updates automatically; run Redefine From Catalog to update bend radius and outside diameter.

## 6.6 Catalog Editor

### What it is ([G:40A09459](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-40A09459-DE28-40AB-B5C8-10E944072F6D), [G:F7637DDA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7637DDA-9AF2-4DF3-880D-2987710010FA))
- Standalone utility with an Explorer-like tree. Opens inside or outside AutoCAD MEP. Views and edits the default catalogs and builds new ones.
- Uses: new catalog from an existing one or from scratch; reorganize (rename chapters, move parts); browse parts; new part from an existing part; add part sizes; add custom properties; copy, paste or drag part data between catalogs; edit part data in Excel.
- Window: navigation pane (left, tree of the open catalog); details pane (right, table of the selected part's data in raw "uncompiled" form: one column per parameter, rows hold attribute descriptions or unique values, background colors separate data kinds, attributes such as type and units control how values define the part); preview image window (lower left, rendered 3D image with the defining parameters shown as dimensions).

### Open it ([G:32547D08](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32547D08-37B2-46D1-A518-791B1D77D5D4), [G:67D95B84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67D95B84-81D8-47FA-AB9E-806D280E354A), [G:C6333E4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C6333E4E-E0F5-4F2A-92C2-A75A58A104F8))
- Inside MEP: Manage tab > MEP Content panel > Catalog Editor. [GUI]
- Outside MEP: run \Program Files\Autodesk\AutoCAD <version>\MEP\AecbCatalogEditor.exe. [AUTO] (inference) Starting it is a plain process launch; all editing inside it is GUI. (test install) the 2027 exe is present.
- From Content Builder: Open Catalog Editor button on the Size Parameters dialog toolbar.
- Open a catalog: toolbar Open or File > Open, go to the catalog folder, double-click the APC. The page names \ProgramData\Autodesk\MEP <version>enu\Tool Catalogs; the real part catalogs are under \enu\MEPContent\<pack>\ (6.2).
- Close: File > Exit or the title bar X.

### Editing behavior ([G:60EA520A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-60EA520A-31DC-440B-923C-2FE1C7F9AF2C), [G:66340340](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-66340340-2D9F-4DA8-A085-B5A2B966F066), [G:CD7D9D40](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD7D9D40-7C34-41CB-A985-6B515CC9BF51))
- Spreadsheet-style editing in tree and table views. Edit > Undo restores the original data. Right-click menus on catalog, chapter and family (tree) and on rows, columns and cells (table). Ctrl+X, Ctrl+C, Ctrl+V.
- Drag and drop moves or copies a chapter or family between chapters or catalogs. Between catalogs, open several Catalog Editor sessions.
- Tree view, by node:
  - Catalog: insert chapter; rename the catalog description.
  - Chapter: insert, rename, cut, copy, paste, delete. Copying a chapter copies all its families; on paste rename or keep the default name.
  - Part family: cut, copy, paste, rename, delete.
  - Part type node: edit size values in the Content tab of the right pane (cut, copy, paste, edit, add, delete).
  - Storage type node (Basic Table, Constant Lists, Constants, Calculations): insert a custom data column; insert a value row for a component in a basic table.
- Table view, by storage type:
  - Basic Table: edit name, description, units, data type and visible cells of custom columns; copy, paste, edit value cells; copy, paste, delete and insert value rows; insert, cut, copy, delete custom columns.
  - Constant Lists: same column and cell edits; no row operations listed.
  - Constants: same; rows: copy the value row only.
  - Calculations: same as Constants. Formulas need correct syntax and existing parameters. They evaluate left to right in column order, so one result can feed a later formula.

### Excel round trip ([G:34645E64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-34645E64-E284-4A26-A3B6-0C2C88EA48AE))
- Right-click a cell > Cut or Copy, paste into Excel; works from Excel back to the Editor too. Editor to Excel: rows paste in order. Excel to Editor: values paste into cells by data type.
- DANGER: a value that does not paste cleanly becomes its type default: Integer 0, Double 0.00, Boolean False. The Editor may also convert a value (real to string). Check every cell after pasting.

### Create a catalog ([G:E0912FC5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0912FC5-7AFA-49F1-8B87-DF8DF17174D2))
- Best done by a CAD manager or an experienced user. Safest method: copy parts from an existing catalog into the new one, then edit.
1. Open Catalog Editor. 2. New Catalog button or File > New.
3. New Catalog dialog: Domain Name (domain type); Catalog Name (becomes the APC file name, the one you pick on the MEP Catalogs tab); Catalog Description; Catalog Root Directory (browse to the folder). 4. OK.
5. Tree view: right-click > Insert Chapter (type name, Enter); Copy/Paste chapters or families; Cut/Paste to move; Delete; Rename.
6. Save (toolbar or File > Save).
- On save the software validates ALL parts in the catalog, then regenerates the APC. RULE: a catalog is usable only after a successful regeneration.

### Create a part ([G:97EB715D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97EB715D-08A7-4AAC-9757-1759EDD010C2))
- RULE: Catalog Editor creates a part only by COPYING an existing part and changing its parameters. A part from scratch needs Content Builder.
- Steps: select a similar family > right-click Copy > select target chapter > Paste (or drag) > right-click the copy > Rename, giving a name AND a unique description > change size values or add custom data in the table view > Save (validates and regenerates). Load the catalog in the drawing to pick the part.

### Add part sizes ([G:E996EBFA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E996EBFA-FD84-4532-B1FD-6C00E86EEAC6))
- For duct, pipe, cable tray and conduit segments and other non-MvPart parts. ATTENTION: MvPart (equipment) sizes need the Parametric Part Wizard or Content Builder. Content Builder can also add fitting sizes.
- Expand the family to show its storage types > select the storage type of the parameter that gets the size > table view:
  - Basic table: right-click a value row > Insert Row (new row goes ABOVE the selection).
  - Constant lists: right-click a value cell > Insert Cell (new cell goes above).
  - Any value, formulas included: click the cell and type. Edit > Undo removes a size.
- Type the new value > Save (validates, regenerates). Load the modified catalog in the drawing to see the size.

### Add custom data ([G:83F397A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-83F397A9-2FAC-413E-9B37-3B3EA94B5332))
- Custom data = a user-defined parameter for schedules or engineering values. Choose the storage type first:
  - basic table: value varies with other size parameters (e.g. material)
  - constant lists: list of values for the part (e.g. size dimensions)
  - constants: one value for all sizes (e.g. manufacturer)
  - calculations: value computed for all sizes
- Steps: open the catalog > expand the family to its storage types > select the storage type > in the table view right-click a cell > Insert Column (new column goes LEFT of the selected cell; Edit > Undo removes it) > fill Name and Description; set Units, Data Type, Visible > enter values > Save (validates the part, regenerates the catalog).

### Catalog Editor problems
- Edits lost after Save: a third-party add-in can interfere; start MEP with no plug-ins loaded and edit again. ([KB:000518645](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Changes-made-to-custom-catalog-through-Catalog-Editor-are-not-saved-in-AutoCAD-MEP.html))
- A wrong-domain error when importing a custom APC means the APC is corrupt; recreate it. ([KB:000637179](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-file-belongs-to-another-domain-displayed-while-importing-the-custom-APC-file-in-AutoCAD-MEP.html))

## 6.7 Content Builder: start-up, rules, choosing a method

### What it is ([G:F78B8241](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F78B8241-AE9B-403B-A941-4499C6D0F297), [G:1C73A9C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C73A9C8-92DC-4E65-BDA8-333DB7C784F3), [G:71444560](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-71444560-2B5F-4268-BCDA-BDB5DF872599))
- Built-in 3D modeling and 2D drafting tool for content. One piece of content = a part family (air terminal, junction box, tank) holding part sizes. It creates and modifies families and single sizes.
- The old MvPart Builder is merged in as the "block-based building environment" (its dialog is still titled "MvPart Builder"). The other is the "parametric building environment".
- Parametric environment: part browser on the left (feature tree; folder order = creation order), modeling area on the right (standard view commands work). Toolbar: save part, save as new part, generate preview image, validate, part options. Status bar under the browser: validation text, traffic light (green valid, red invalid), Details button listing warnings and errors. Right-click a feature for its menu.
- Block-based environment: Wizard mode (new part or added sizes; pages for behavior, sizes, block per size, preview image, connectors, property set info) and Modify mode (same items as tabs, change any in any order).

### Start it [GUI] ([G:082E1B71](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-082E1B71-3EBD-45E6-8A1A-CA59F7784639), [G:B316759A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B316759A-9801-4E84-B1B5-B7CE9FE0A39D), [G:F9F10998](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F9F10998-2D98-4F40-9E3C-FB3A02558D28), [G:79CD8F4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-79CD8F4E-8DEE-4767-8753-F76F2180F1EC), [G:624C7B6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-624C7B6B-2E56-4620-80DA-B3354F65902D))
- Manage tab > MEP Content panel > Content Builder. Command CONTENTBUILDER is listed on [G:624C7B6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-624C7B6B-2E56-4620-80DA-B3354F65902D). [AUTO] It opens a dialog, so it blocks a script.
- Dialog "Getting Started - Catalog Screen": catalog browser plus icon bar. The Part Domain list (one page says Part Catalog) = catalogs loaded on Options > MEP Catalogs tab.
- The domain picks the catalog, and each catalog domain writes domain data into its parts. An MvPart belongs to one catalog, but each of its connectors can have a different domain.
- Icons by domain: MvPart catalog enables New Block Part and New Parametric Part; component catalogs (duct, pipe, cable tray, conduit) enable New Parametric Part only.
- With a chapter selected: new block-based MvPart, new parametric part, add chapter, add a size to an existing part, modify a size, delete a part (removes its XML, DWG and BMP).
- New Part dialog: Name (key for the part files) and Description (family label; defaults to Name).
- An MvPart with no model geometry is legacy content: it can only be modified, and Catalog Editor is recommended for that.
- From a drawing: shortcut menu "Edit in Content Builder" on catalog-based content. ([G:C0CC1782](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0CC1782-4848-4AA9-8104-4447FB14560C))
- Primitives: Part Domain = "Primitives and Re-usable Parts". ([G:90661905](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90661905-C46C-4E0C-951B-8FB255104DBF), [G:E8ACC36E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8ACC36E-080E-4276-9685-7FAD0902F56C))

### Rules and tips ([G:C0CC1782](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0CC1782-4848-4AA9-8104-4447FB14560C), [G:3A239FB5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3A239FB5-401A-476F-9D84-E17F6D038BE0), [G:1F733687](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1F733687-642E-49DC-A2B3-562609164FC6), [G:BB0F03C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BB0F03C9-8009-4486-AACB-7BEB4EB3E021))
- [AUTO] Never run EXPLODE on a part. It deletes the part definition from the catalog.
- MVIEW does not make associative views of parts; Content Builder generates the views.
- Avoid standard AutoCAD commands in Content Builder. AutoCAD dimensions are not parametric and cannot drive the part. AutoCAD geometry is not valid on work planes.
- The UCS command does not tie the current plane to the part; use work planes.
- Enlarge points with Point Style ([G:79CD8F4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-79CD8F4E-8DEE-4767-8753-F76F2180F1EC) lists command DDPTYPE); an absolute point size is recommended.
- Work in a 3D view. Plan feature dependencies first. Object snaps work for selecting.
- Layer key: only keys in the layer key style of the CURRENT drawing can be picked. Before starting: Home tab > Layers panel > Select Layer Standard > Drawing Setup dialog > Layering tab > "Layer Standards/Key File to Auto-Import": browse to \ProgramData\Autodesk\MEP <version>\enu\Layers\AecbLayerStd4.dwg (standard "MEP - AIA"); under Default Layer Standard pick layer key style "Mech - AIA 256-color" > OK. Example: key Air Handling Unit maps to layer M-HVAC-Eqpm. Layer keying works only when the drawing has a layer standard and key style. ([G:BB0F03C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BB0F03C9-8009-4486-AACB-7BEB4EB3E021), [G:A34FB751](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A34FB751-C54B-4AD0-9685-A1860D8D06CE))

### Which tool to use ([G:9F57B992](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F57B992-77E9-448B-BF3D-6C0732F474F5), [G:3229E6C1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3229E6C1-96C8-4847-8B16-75991EF9F192), [G:E6A99ECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6A99ECD-2329-4E69-9B27-9D5537FB02F9), [G:97EB715D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97EB715D-08A7-4AAC-9757-1759EDD010C2), [KB:000413610](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Mv-Part-with-connectors-from-3D-Geometry-Block-in-AutoCAD-MEP.html))
- Parametric Part Wizard: quick parametric part from a shipped template; basic model; one or a few sizes made while designing (6.10).
- Content Builder: from-scratch parts, complex models, block-based equipment, fittings. Puts the part in a catalog and allows later edits.
- Catalog Editor: copy an existing part, add sizes or custom data. No from-scratch parts.
- MVPARTCONVERT: quick drawing-only MvPart from a block (6.4).

## 6.8 Block-based MvParts (equipment from 3D blocks)

### Prep in plain AutoCAD first ([G:541516BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-541516BF-39D3-4191-84A2-2B31BAE4B919), [G:4AF72311](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AF72311-98CD-4B8A-BCC5-4E82F427D9BD), [G:AD10CC62](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AD10CC62-4978-420F-ACE2-763BA813CBE5), [G:3AC80843](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3AC80843-67E1-4E9A-BE55-5838E5FE7D8F), [G:18E0E509](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-18E0E509-6A58-48F1-B139-2727ED3699B4), [G:0958907D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0958907D-AAF1-483B-9440-11A1511CE87C))
This stage is ordinary AutoCAD work and can be scripted. [AUTO]
- One unique 3D model block per part size, plus one 2D schematic symbol block, all in the SAME drawing. One DWG can hold many model blocks.
- Do NOT save these working drawings in the catalog folders. Keep them in a separate or temp folder.
- Model with AutoCAD solids (needed for automatic view-block generation and for render, shade and hide). Make each size ONE solid body so hidden-line display is right.
- Model and symbol geometry: layer 0, color BYBLOCK, linetype BYBLOCK, lineweight BYLAYER.
- Build at 0,0,0 WCS in SW isometric so generated view blocks align: top and bottom on XY, front and back on XZ, left and right on YZ.
- Put AutoCAD POINT objects at the center of every connection. Pick them later with the Node snap when placing connectors.
- Set the UCS to World (View tab > Coordinates panel > World) before making the block.
- Make the block: Insert tab > Block panel > Create Block (Block Definition dialog: name, Select Objects, Retain / Convert to Block / Delete, Base Point > Pick Point, Description). (inference) -BLOCK is the no-dialog form; the sources do not say so.
- Base point = where the size lands when placed. The symbol block base point must equal the model block base point, because the placed MvPart is one object.
- Names: model block = family + size + "model", e.g. "AHU Commercial Roof 24x24 model". Sizes whose block name ends in "model" get view blocks generated and assigned by default ([G:7D9D3E77](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7D9D3E77-1383-4DF3-A32D-BFF96F8809AC)). A symbol block named exactly "symbol" is used by default as the 3D symbol source; otherwise name it like "AHU Commercial Roof 24x24 symbol".
- Symbol: plan view, base entities only (lines, polylines, circles). If AEC objects (walls, ducts) were used, EXPLODE them to base entities first (object enabler problems). Content Builder scales the symbol into the model's bounding box and centers it, so connection points stay right for schematic lines.
- One symbol is usually shared by the whole family. Changing it changes all sizes. ([G:7F7293C3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7F7293C3-7932-49B5-A748-5B4F8566A402))

### Workflow, in order ([G:8ADDC602](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8ADDC602-4A0A-48D7-9512-39D80D583EC2), [G:1C73A9C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C73A9C8-92DC-4E65-BDA8-333DB7C784F3), [G:B316759A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B316759A-9801-4E84-B1B5-B7CE9FE0A39D), [KB:000413610](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-Mv-Part-with-connectors-from-3D-Geometry-Block-in-AutoCAD-MEP.html)) [GUI]
1. Model blocks and symbol drawn (above); open that drawing.
2. Manage tab > MEP Content panel > Content Builder > Part Domain = Multi-view Part > pick a chapter > New Block Part > Name and Description > OK. "MvPart Builder" opens after a short delay.
3. Behavior page: Type, Subtype, Layer Key, insertion method (Breaks Into and/or Anchor) > Next.
4. Blocks & Names page: Add Part Size, pick the model block; optional 2D symbol; Generate Blocks; OK the Views prompt.
5. Preview image page > Next.
6. Connectors: right-click the family to add each connector type, then Edit Placement per size.
7. Properties page: Edit Properties (optional) > Finish. The part is saved into the catalog at the chosen chapter.
- Skipping or reordering phases can leave an unusable part.

### Part behavior: family level, shared by all sizes ([G:A34FB751](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A34FB751-C54B-4AD0-9685-A1860D8D06CE))
- Part type: predefined, cannot be modified; carries behaviors (HVAC sizes can take flow annotation). Pick the closest type.
- Part subtype: filter in the Add and Modify dialogs; a new name can be typed.
- Layer key: one per family; must exist in the current drawing's layer key style (6.7).
- Insertion method: anchor, breaks into, both, or none (6.4).

### Size names and view blocks ([G:7D9D3E77](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7D9D3E77-1383-4DF3-A32D-BFF96F8809AC), [G:C73720A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C73720A9-DF3F-45CC-B474-094FBA5C432B))
- Part size name: describe the real size (W x H) or total cfm. Used to pick the part in the MvPart Add dialog, stored in the catalog, shown as the object name in tooltips.
- Add a size: pick a 3D model block (list = blocks in the ACTIVE drawing) > add button. Pick a 2D symbol block, or None (a symbol is not required).
- Status colors: empty = not assigned; RED = name assigned but block missing; BLACK = assigned and present.
- Generate Blocks makes the missing (red) view blocks: the 6 standard views (top, bottom, left, right, front, back), named from the model block. Views dialog: pick the size, a view number (#), then Display Representation and View Direction to change an assignment. Generate for many sizes at once.
- One view block may serve several directions when the part is symmetric. View blocks can also be drawn by hand and attached.
- All view blocks share insertion point 0,0,0 WCS, the same point on the model block.
- Default assignments: Top, Bottom, Front, Back, Left, Right blocks go to "1 Line" and "2 Line", view direction = own name. Model block goes to "1 Line" and "2 Line" with direction 3D, and "Model" with All directions. Symbol block goes to "Schematic", All directions; in Isometric mode it shows as a 3D bounding box with the 2D symbology.
- The "Plan" display representation is standard but unused by the MEP toolset. Standard representations cannot be deleted.
- Delete a size: select its Part Size Name > delete button. Next stays shaded until every size has a name and every view block shows black.
- Model block changed = regenerate that size's view blocks or display will be wrong. ([G:7F7293C3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7F7293C3-7932-49B5-A748-5B4F8566A402))

### Preview image ([G:0918A159](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0918A159-ED17-47AA-AE90-A24938811CB4), [G:65BE8AD4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-65BE8AD4-DA07-470B-9545-DD6EC0F465ED))
- One image per FAMILY, shared by all sizes. Typical: shaded SW isometric of one size.
- "Select a previously drawn image": 256-color BMP, 200 x 200 pixels (good for showing dimensions, the UCS icon at the insertion point, flow arrows).
- Or "Generate an image based on a model block from the SW Isometric View": pick a block > Generate (shaded, no text or dimensions). Next is grayed out until an image is chosen.

### Connectors on a block-based MvPart ([G:E1317481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E1317481-C416-4CAB-A68A-C6516B0BCB1F), [G:17C5625E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17C5625E-7140-4378-847E-B39FBC2B3FBE), [G:7F7293C3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7F7293C3-7932-49B5-A748-5B4F8566A402), [G:8ADDC602](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8ADDC602-4A0A-48D7-9512-39D80D583EC2))
- Usually one or more connectors; a part may have none. The connector COUNT must be the same for every size. Adding or deleting a connector applies to all sizes.
- Each connector has a domain, set once per family. A connector connects only to the same domain. AHU example: supply and return = duct; power = conduit; hot/chilled water in and out and drain = pipe.
- Per size: type (list per domain, e.g. flange, slip-joint, glued), size (rectangular L x W, round diameter), location, and whether unsized connections are allowed.
- Conflict on shape: [G:7F7293C3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7F7293C3-7932-49B5-A748-5B4F8566A402) body text, [G:E1317481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E1317481-C416-4CAB-A68A-C6516B0BCB1F) and [G:8ADDC602](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8ADDC602-4A0A-48D7-9512-39D80D583EC2) say shape and domain come from the family connector; the Attention note in [G:7F7293C3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7F7293C3-7932-49B5-A748-5B4F8566A402) and [G:17C5625E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17C5625E-7140-4378-847E-B39FBC2B3FBE) say size AND shape may differ per size. (inference) Plan on one shape per connector for the whole family.
- Add: MvPart Builder tree > right-click the part family > pick the connector type > Part Family Connector Properties dialog: Name; Connection Shape (list depends on domain); extra properties such as Flow Direction; Unsized True/False (True accepts unsized segments). These apply to ALL sizes > OK. The domain comes from the connector type picked and cannot change here. Unsized cannot change once the connector exists.
- Place: right-click the connector > Edit Placement > a property palette opens. [AUTO] Command-line keywords: p = Position (pick a point; use the Node snap on your POINT objects); n = Normal (one point: drag the right way with Ortho on and pick; or two points). Palette also sets Connection Type, Rotation (degrees, usually 0) and Size. OK, then Next.
- Normals point AWAY from the part. Recommended vectors: +X 1,0,0; +Y 0,1,0; +Z 0,0,1; -X -1,0,0; -Y 0,-1,0; -Z 0,0,-1. Correct normals keep the Compass aligned when connecting. Faces off the main planes: snap to the face center and point away. ([G:E1317481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E1317481-C416-4CAB-A68A-C6516B0BCB1F))
- Flip and rotate grips are added automatically when the part is created; they cannot be set directly. Missing grips = recreate the part with correct connectors. ([KB:000662898](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Rotation-or-flip-grips-are-missing-in-custom-MVparts-in-AutoCAD-MEP.html))

### Property set information ([G:5FE8E727](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5FE8E727-B805-4D74-B1B8-BA80925F1CDC), [G:92446174](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-92446174-61BD-4136-B79D-5E423C2001B6))
- Optional; Finish works without it. MvPart Builder: select the family or one size > Edit Properties > Property Editor dialog.
- Under Block-Based Parameter Configuration, CEL (connection engagement length) and AoD (angle of deflection) appear ONLY for pipe connectors; their Data Storage and Visibility can be changed.
- Add custom data: toolbar list = Parameter Configuration > New > New Parameter dialog: pick a parameter, or "Custom Data 1" and name it > OK. It is added as the LAST column. Set data storage, data type, units, visibility, description per cell.
- Storage: List (toolbar Values; Edit Values dialog; Add each value); Constant (double-click the value cell, type); Calculation (toolbar Calculations; Calculation Assistant); Table (a unique value per size row).
- PrtSN (Part Size Name) defaults to Table. Set it to Calculation to build size names from other attributes (height, width).
- Adding a custom property adds it to EVERY size; values are per size. Predefined parameters by part type (material, gauge) also exist.
- RULE for schedules: the data parameter and the property set property must have the SAME NAME. ([G:92446174](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-92446174-61BD-4136-B79D-5E423C2001B6))

### Modify a block-based part ([G:4178DA80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4178DA80-9688-4292-A100-8392202699D6), [G:7F7293C3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7F7293C3-7932-49B5-A748-5B4F8566A402), [G:90577BAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90577BAD-0F5D-4203-B44F-18CBD9C9CD5E)) [GUI]
- Content Builder > select the block-based part in the tree, then:
  - Add part size: "MvPart Builder (Add Part Size)" wizard, same steps as a new part.
  - Modify: "MvPart Builder (Modify Part Size)" tabbed dialog; change only what you need, in any order.
  - Delete: removes the family and its XML, DWG and BMP.
- BEFORE starting: new or changed model blocks must already be in the part family DWG stored in the catalog, e.g. \ProgramData\Autodesk\MEP <version>\enu\MEPContent\USI\MvParts\Mechanical\Roof Mounted AC Units. Edit = change the block in that DWG. Replace = delete the old block and add the new one there. Then regenerate the view blocks.
- Per size you can change: model block, symbol (applies to all sizes), behavior (type, subtype, layer key, insertion method; avoid the Behavior tab or page unless the whole family should change), size name and view blocks, preview image (all sizes), connectors (size, type, location per size; add or delete hits all sizes), properties (a new property goes to all sizes).
- Edits write straight into the catalog source files and reach only sizes added to drawings AFTER the change. Prefer editing individual sizes. ([G:90577BAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90577BAD-0F5D-4203-B44F-18CBD9C9CD5E))

## 6.9 Parametric parts: model concepts (all [GUI], part browser)

### Part configuration ([G:B399A789](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B399A789-35DC-447D-86E2-6CCD536F52AB), [G:9CEA696C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9CEA696C-16A4-4D5A-A226-66A87E738FD3), [G:1934EBB2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1934EBB2-78C7-4F21-90C7-F4B3AF80EA58), [G:4D8B166A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4D8B166A-7226-4614-B56C-67FFA538E040), [G:FABFD4FB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FABFD4FB-5ED4-4878-A078-FBECF896784E))
- First folder in the part browser. REQUIRED to save the part; set it BEFORE modeling. Once per family.
- Part Description: editable (the part Name is not editable there). Part Domain: from the catalog picked in Getting Started (duct, pipe, cable tray, conduit, MvPart components); read-only. Part Type: predefined list by domain and loaded catalogs (elbow, tee, fan, damper, tank). Part Subtype: predefined list by type, or type a custom one.
- Edit type or subtype: right-click Undefined > Edit. Examples: Air Terminal / Diffuser; Junction Box / Square Outlet Box; Tank / Vertical Storage Tank; Tee; Transition Straight.
- Only ONE part can exist in a drawing in this environment.

### Model building blocks ([G:B8603118](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8603118-DCFF-4EFA-81C5-B1EACBFD5417), [G:FB801B8F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FB801B8F-110C-4BCB-B4A6-7DB0953CA2D2), [G:9CF2D096](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9CF2D096-454E-4448-83E5-DBBEF0ECC568))
- Chain: geometry > profile > modifier. Change one and the next updates.
- Work plane: infinite construction plane at any angle, drawn as a rectangle (display only). Holds geometry, dimensions, constraints and profiles; has its own coordinate system.
- Add: expand Modeling > right-click Work Planes > Add Work Plane > Create Work Plane dialog: Default (WCS ZX, YZ, XY), Custom (X and Y direction and origin in the current UCS), Offset, Reference, Top, Bottom, Front, Back, Left, Right.
- Offset plane = set distance from a source plane. Reference plane = on a face of a modifier's extents; moves and resizes with the modifier.
- Features move with their plane. DELETING a plane deletes its features. Use the fewest planes; keep one visible at a time (right-click > Visible). Set View matches the view to a plane. ([G:80DCFA96](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-80DCFA96-89CB-485C-BD67-A636D856AFB0), [G:D32427C4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D32427C4-1ED8-4B20-BD65-B2475D45BE1B))

### Geometry ([G:1F733687](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1F733687-642E-49DC-A2B3-562609164FC6))
- 2D, attached to a work plane, listed under that plane's Geometry folder. 9 types: Point, Line, Unbounded Line, Circle, Arc, Rectangle, Oval, Point Reference (copy of a point from another plane; follows or dies with its source), Project Geometry (fixed projection of a modifier onto a plane; adjusts with the modifier).
- DANGER: do not use AutoCAD geometry commands. AutoCAD geometry is not valid on work planes.

### Profiles ([G:9C6052BA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9C6052BA-EE5C-49F1-86F2-AFF2D9EF88DC), [G:FD7B9C9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FD7B9C9D-1518-41AC-9F2B-A957B48E4DC6))
- Closed 2D outlines on a work plane; modifiers act on them. 4 types: Circular (center plus diameter), Rectangular (4 lines, 4 points, 4 perpendicular constraints), Oval (2 lines, 2 arcs, 4 points, 4 tangent constraints), Custom (from existing geometry on one plane).
- A circular profile defines a fitting's diameter and its connectors.

### Modifiers ([G:C8A76A38](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C8A76A38-5E77-4EF7-8C3A-419A1AA62481))
- 6 types: extrusion, path, transition, cut plane, Boolean add, Boolean subtract. Extrusion is the usual base feature.
- Extrusion: Midplane (equal both sides), Plane (to a work plane; follows a reference plane), From-To (between 2 planes), Blind (set distance; Flip reverses).
- Path: sweep a profile along a line or arc; start and end profiles may differ; segment count sets gores (gored elbows).
- Transition: body between a start and an end profile on different planes.
- Cut Plane: cuts a feature and keeps one side (sloped end). RULE: not parametric; it shows exactly as modeled.
- Boolean Add merges two features. Boolean Subtract: the subtractor must intersect the base or nothing changes.

### Constraints and dimensions ([G:1171A54D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1171A54D-08EC-416F-973B-2EDE24FDFD25), [G:45656ADE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45656ADE-4C8A-4D63-A352-C2EB37BB13C3), [G:EBC684DE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EBC684DE-F7BC-4DF2-B647-39163852699B))
- Constraints remove degrees of freedom; the command line lists what remains. 10 types: Tangent, Parallel, Perpendicular, Concentric, Coincident, Equal Distance, Equal Radius, Midpoint, Symmetric, Normal (two lines cannot be Normal; use Perpendicular).
- "Unconstrained by N dimensions" is informational. Add the minimum constraints that define the shape.
- Each dimension adds a parameter. Types: Distance, Horizontal Distance, Vertical Distance, Parallel Distance, Perpendicular Distance (none can be negative), Diameter, Angle (degrees), Path Angle (PathA1, PathA2... in Size Parameters). The page says 7 types and lists 8.
- Parameter names = letters plus order added: LenA1, LenB1, D1, ND1, WPOf1, PathA1.

### Model vs size parameters ([G:066F2578](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-066F2578-CA8D-41AD-AF0D-6BF2DD579F01), [G:337E71B9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-337E71B9-DCB9-4DD5-AC3E-51408E952CA2))
- Model parameters = default size and placeholders. The Model Parameters dialog is the one place to view, create and edit them: Name (default D1, D2...; renameable, unique), Value, Equation (constants, other parameters, operators; Equation Assistant checks it), Description.
- A constant used in an equation must itself be a model parameter. Check that results are not zero.
- Adding a model parameter adds a matching size parameter. Size parameters = the real sizes (6.10).

### Best practices ([G:3A239FB5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3A239FB5-401A-476F-9D84-E17F6D038BE0), [G:F1857095](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F1857095-8B8E-4E0B-917D-CBC9098451A5), [G:8CC5982A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8CC5982A-E38B-4478-90AE-FE48198653B6))
- Shape before size: constraints first, then dimensions. Large features before small ones. Few points, reused. Mix constraints and dimensions; if one distorts the model, delete or undo it and try another.
- Calculated values used for model parameters are NOT available in the part Add Size filter.

### Primitives ([G:32257F22](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32257F22-76D2-44F6-98A4-C96356AC41D2), [G:FC0A98BC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FC0A98BC-1ACB-4529-A1B0-1AF55A2F53B5), [G:EB1F3428](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB1F3428-5942-4B17-B7D4-4EB49667121D), [G:29076876](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-29076876-6758-4500-B58F-42C54D7136B6), [G:90661905](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90661905-C46C-4E0C-951B-8FB255104DBF), [G:E8ACC36E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8ACC36E-080E-4276-9685-7FAD0902F56C), [G:584DCFED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-584DCFED-F935-4A4D-840E-82B0130C3D51))
- Reusable partial models (box, torus, flanged pipe connector, duct connector) with planes, geometry, constraints, dimensions, model parameters, profiles, modifiers; connection primitives also carry connections. No part type, size parameters or autolayout data. DWG plus BMP; cannot go in catalogs.
- Make: from scratch (Part Domain = Primitives and Re-usable Parts > chapter > New Parametric Part > New Primitive dialog; reduced feature set; needs at least one work plane with parametric geometry; validate, save; BMP optional, else SW iso on save); copy and edit (edit > Save Part Family As; or [AUTO] copy and rename the DWG files in \Shared\Primitives); or save a part as a primitive (Save Part Family As Primitive dialog).
- Insert: Insert Primitive button > dialog > Insert. Attach to a work plane (click) or a face (Enter, then click the face; a reference plane is made). Then pick which of the primitive's planes aligns (n + Enter = next plane). Keys: f flip, r rotate (pick, or type angle + Enter), m mirror copy; Enter finishes. Plane centers align. Units convert. Model parameter descriptions carry the primitive's name.

## 6.10 Parametric parts: workflow, connectors, sizes, behaviors, symbols, save

### Workflow, in order ([G:FABFD4FB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FABFD4FB-5ED4-4878-A078-FBECF896784E), [G:C8AE9452](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C8AE9452-8468-4D59-A575-5DE100817BE3), [G:E8F1B517](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8F1B517-19D5-4187-ADA5-A57C10DDF03E), [G:E5446279](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5446279-3A83-4BE5-898C-4E54B7DA0A53), [G:79CD8F4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-79CD8F4E-8DEE-4767-8753-F76F2180F1EC), [G:F9F10998](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F9F10998-2D98-4F40-9E3C-FB3A02558D28)) [GUI]
1. Open the parametric building environment: Content Builder > Part Domain (Duct for a duct fitting, Multi-view Part for an MvPart, and so on) > chapter > New Part > unique Name and Description > OK. Then View tab > Appearance panel > Point Style so points show clearly.
2. Part configuration (6.9).
3. 3D model: work planes, profiles, modifiers. 2D views are generated from it.
4. Connectors (their shape and size come from the feature they sit on).
5. Dimensions and part sizes: one model, many sizes.
6. Preview image.
7. Insertion behaviors: layer key, placement point, trim lengths (fittings).
8. Validate and save. Every error must be fixed before the part can be saved and used.
- Do the phases in order or the part may be unusable.
- Parametric fittings are NOT used in plumbing runs; they serve duct, pipe, cable tray and conduit. ([G:E8F1B517](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E8F1B517-19D5-4187-ADA5-A57C10DDF03E))

### Modify a parametric part ([G:6998640F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6998640F-44D9-44CB-856D-A8BAEB6EE253), [G:363A8614](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-363A8614-A7DD-43CC-83DC-AFF6C3637ECC), [G:10C8ED6C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10C8ED6C-A129-4F7C-9D65-D11943DF7523)) [GUI]
- Content Builder > select the parametric part > add a size or modify a size (both open the parametric environment), or delete the family (XML, DWG, BMP).
- Parts from the shipped catalogs: you can change part behavior, size parameters and connectors. Parts you built: also the model (geometry, profiles, modifiers, constraints, dimensions). Edit with the same procedures used to create.
- Keep the feature dependencies of the model or the part becomes unusable. Geometry you add, edit or remove must be APPENDED TO THE PROFILE so Content Builder updates the model and assigns new constraints. Learn the existing constraints first; re-check constraints and dimensions after.
- Connector shape follows its modifier; change the modifier to change the shape. Sizes: e.g. turn a constant into a list of values, or add custom parameters for scheduling.
- Also editable: preview image (new direction or attached image), insertion behaviors (layer key, trim lengths, placement point), schematic symbol (parametric MvParts only).
- Deleting unneeded parts keeps a custom catalog's definition files managed.

### Pipe fitting content rules ([G:44EED615](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-44EED615-0D8C-4667-B6E2-D32E13EFCA2E), [G:25380F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-25380F6A-6BC0-4A8C-A643-9B953B5E6DB3))
- Pipe parts are built in the Piping domain, in the Top plane. Fittings MUST be parametric.
- Content Builder checks that every pipe connector has CEL (connection engagement length), AoD (angle of deflection) and ND (nominal diameter). Missing ones are added and you are asked to accept.
- A new pipe connector on a pipe segment or MvPart auto-adds CELn and AoDn (n = connector number): Constant, Real, CEL in drawing length units (in or mm), AoD in degrees, default 0.000.
- Name convention: Connection Type - Schedule/Pressure Class - Part Type, e.g. "Flanged - Class 2500 - Raised Face Blind Flange".
- Female connection types: hub, bell, mechanical joint. The female connector is connector 2 on elbows and tees, connectors 2 and 4 on crosses. A male-female part has both genders.
- Per fitting type:
  - Crosses: C1 male (CEL 0); C2 and C3 male or female; C4 female; every female CEL > 0. PathA1 = 180 degrees; PathA2 and PathA3 90 degrees or less.
  - Elbows: C1 male. 2-connector elbow: C2 female. 3-connector elbow: C2 or C3 male or female. PathA1 any angle.
  - Tees and offset wyes (laterals): C1 male, CEL 0; C2 female, CEL > 0; C3 male or female. PathA1 = 180 degrees; PathA2 90 degrees or less.
  - Eccentric transitions: female on either connector; male types left undefined so they take the name of the matching female.
  - Grooved true wye: connectors run clockwise. Auto layout never inserts true wyes.
  - Mechanical joint (bell, hub): C1 male, CEL 0, constant; C2 female, CEL > 0 set by the manufacturer. Part type = coupling.

### Connector behavior rules ([G:94AB8CC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-94AB8CC9-1257-43C5-8A17-C1D4165C18F1), [G:5ACE727E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5ACE727E-6FB3-4D9B-861F-3AFB9B3C98B7))
- Default connection type = undefined. Undefined connects validly to every type.
- Male connectors: leave undefined; they then follow the Connection Assignments tab of the Pipe Layout Preferences dialog.
- Female connectors: set a real type. A female joined to an undefined connector shows, on Connection Assignments, the male type assigned to that female type name.
- Tick only ONE connection name per pipe connector in the Connection Type Selection dialog. With more ticked, the first one detected is used.
- Butt-welded connects only to butt-welded; no CEL; joined without a joint.
- Bell/hub: C1 = bell end, C2 = back end. Orientation follows Joint direction on the Pipe Properties palette. C2 reports the same type as C1 on Connection Assignments.
- "Same Connection" (Piping domain): on a connector or coupling attached to a hub, it inherits the type of the hub's connector 2, not connector 1.

### Adding connectors ([G:5ACE727E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5ACE727E-6FB3-4D9B-861F-3AFB9B3C98B7), [G:25380F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-25380F6A-6BC0-4A8C-A643-9B953B5E6DB3), [G:10C8ED6C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10C8ED6C-A129-4F7C-9D65-D11943DF7523), [G:4AD35479](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AD35479-827B-442E-8B5B-156EB6CCAE5B), [G:288087E9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-288087E9-0BEE-4871-8C35-FFF2B0973579), [G:C0C9B4F6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0C9B4F6-CD29-4275-A465-6ECC28CA3EAB)) [GUI]
- Part browser: right-click Connections > Add Connection. The cursor snaps to candidate spots (tee: both trunk ends and the branch end; diffuser: top and bottom faces and stub ends). Pick one, press Enter for the default number (numbers ascend in the order added), then pick a spot off the model for the diameter dimension (D1...).
- One profile defining several connectors is dimensioned once: the tee's second trunk end gets D2 = D1 automatically.
- ATTENTION: the FIRST connector's position defines the part's axes on insertion. A first connector whose vector points perpendicular into the part makes that direction the +X axis in the drawing.
- Order conflict: the tee procedure says add connectors in plan LEFT to RIGHT, then BOTTOM to TOP, and that this order is valid for all tees and other fittings ([G:5ACE727E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5ACE727E-6FB3-4D9B-861F-3AFB9B3C98B7)). The connector concept page says "left to right, then top to bottom" ([G:25380F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-25380F6A-6BC0-4A8C-A643-9B953B5E6DB3)). Both checked on the source pages. Trim lengths are also defined left to right, then bottom to top ([G:67822B55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67822B55-7478-4CB9-9D13-5F8A03916844), [G:176E5003](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-176E5003-20E0-455D-A66C-8B6F9D5C8ED1)). (inference) Use bottom to top, as the worked tee does.
- A usable tee needs at least 3 connectors. ([G:5ACE727E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5ACE727E-6FB3-4D9B-861F-3AFB9B3C98B7))
- Set type: Connections > right-click a connector > Edit > Connector Properties dialog (domain and shape are view-only) > Type value > browse button > Connection Types Selection dialog. Domains offered depend on the modifier shape; types depend on the domain. Picking the Pipe domain makes System Type available (e.g. Cold Water). Types can be picked regardless of gender.
- Connector shape = shape of the modifier it sits on. To change the shape, change the modifier. The domain sets the connection rules: a duct-domain air terminal cannot connect to a pipe. ([G:10C8ED6C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10C8ED6C-A129-4F7C-9D65-D11943DF7523), [G:25380F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-25380F6A-6BC0-4A8C-A643-9B953B5E6DB3))
- Worked examples: diffuser flex stub (circular profile on the Lip Offset plane, radius 3" (76 mm); Blind extrusion 4" (102 mm); connector at the top of the stub; Type Banded); junction box knockout (Domain Conduit, Type Glued); tank tap (Domain Pipe, Type Threaded, System Type Cold Water).
- If picking a spot off the model fails, turn object snaps off.

### Part sizes ([G:337E71B9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-337E71B9-DCB9-4DD5-AC3E-51408E952CA2), [G:9F57B992](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F57B992-77E9-448B-BF3D-6C0732F474F5), [G:9EC9A8A6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9EC9A8A6-4EFA-489D-ADC8-25CCBFC8358C), [G:3E7EDC6C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3E7EDC6C-DF95-4A84-9D1D-DDE3A9ACC9B0), [G:BC57E9B8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BC57E9B8-FCD1-46D3-8B76-CCD4CDB8EA68), [G:64540C23](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-64540C23-8659-44CF-8CF7-63D715A8B573), [G:87A65A73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-87A65A73-2653-4A00-8FA0-9F3AD2EE4DF1))
- Size Parameters dialog: right-click Size Parameters > Edit Configuration, Edit Values or Edit Calculations. Three modes, switched by a toolbar list: Parameter Configuration (description, storage type, data type, units, visibility), Values, Calculations.
- Storage types: list, table, constant, calculation. Table: every column holds the same count, one row = one size. List: values combine in every combination (a diffuser with 2 neck diameters = 2 sizes).
- Table sizes: set the parameter's storage to Table, click the first row, then the New (add) button per size; double-click a cell to type.
- Values calculated in the model CANNOT be edited in Size Parameters; edit them in the Model Parameters dialog.
- A parameter with no dimension placed is NOT shown during part size selection.
- Size name = PrtSN, built by a calculation in the Calculation Assistant (Precision, Insert Variable, Evaluate). It uses VBScript FormatNumber plus string substitution, so syntax must be exact; click Evaluate before OK. Example: Precision 0, insert LenA1, click the PrtSN value and type x, insert LenA2, then type inch Louver Face Ceiling Diffuser (the page does not show the exact spacing or quoting in the stored formula). Fitting example: clear PrtSN, insert D1, type inch Dia., insert PSTyp, insert PTyp (PSTyp and PTyp are not defined on the page; (inference) part subtype and part type).
- Pipe connector sizes: enter the nominal diameter. The software searches the active pipe catalog for connectors with the same connection type and ND (for a fitting, also the same subtype if set) and inserts the physical diameter of the first match. Editable. ([G:BFCA07A8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BFCA07A8-BAF3-4384-90C0-175EB4321D4F))
- Conduit size parameters now carry nominal diameter (ND1, ND2) and material (Mat); earlier releases had only actual diameter (D1, D2). ([G:337E71B9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-337E71B9-DCB9-4DD5-AC3E-51408E952CA2))
- Insert the connector sizes of default segments: Size Parameters > select the value (storage must be List or Table; a pipe connector must be Table) > Default Connector Values button (or right-click > Default). Pipe: Choose a Part dialog, pick a pipe FITTING (fittings carry connection types). Overwrites ALL values. Parametric parts only; the connector needs a domain and a connection type. If storage types differ: paste values only, paste storage type and values, or cancel. ([G:49D86316](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-49D86316-01C9-4619-8F7E-C1D7BBFFE795))
- Copy and paste sizes with Ctrl+C / Ctrl+V from another part in Content Builder, a part in Catalog Editor, or Excel. Copying values moves only values. Copying a heading also brings the storage type (works between equal types and between List and Table, with the same three-way prompt). ([G:C6333E4E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C6333E4E-E0F5-4F2A-92C2-A75A58A104F8))

### Insertion behaviors and the Options dialog ([G:5A3DAB85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5A3DAB85-94A1-456C-B1A0-EB134862EC9A), [G:176E5003](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-176E5003-20E0-455D-A66C-8B6F9D5C8ED1), [G:07CBA412](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07CBA412-E49E-4D63-A853-E8FF7F796D18), [G:67822B55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67822B55-7478-4CB9-9D13-5F8A03916844)) [GUI]
- Set after the model is final and the preview image exists. Part browser Options button opens the Options dialog:
  - Custom Sizing Flag: allows custom sizes when the catalog lacks one (inserted by Auto Layout, or via the Add dialog part filter and values).
  - Hide Part Flag: hides the part from part selection. ON by default; good for temporary parts or parts built over several sessions. After a passing validate and save you are asked whether to keep it hidden.
  - Anchor Part, Break Into Part, Layer Key, Display Symbol in Plan View: MvParts only. A fitting takes its layer from the objects it connects to.
  - AutoLayout Flag: fittings only; adds the Autolayout Data folder for trim lengths and the placement point. MvParts get Autolayout Data automatically.
- Fitting steps: turn off work planes (right-click > Visible); Options > tick Auto Layout Flag > OK; View tab > Coordinates panel > World; expand Autolayout Data > right-click Layout Data > Add Trim Length (pick start, then end).
- Trim length = distance from the fitting center (intersection point) to a connection end; used to trim joining segments. Define them LEFT to RIGHT, then BOTTOM to TOP, or parts trim wrong. Count: elbow 2, reducer 2, tee 3, cross 4. Tee: TL1 trunk center to left end; TL2 trunk center to right end; TL3 trunk center to branch end.
- Then right-click Layout Data > Select Placement Point: the point where the connecting segments would meet if extended (tee: trunk center). It is the fitting's insertion point during auto layout with the Add commands. The concept page adds that connection 1's position is the insertion position and can be toggled. ([G:67822B55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67822B55-7478-4CB9-9D13-5F8A03916844))
- MvPart: Options > set behaviors > OK; expand Autolayout Data > right-click Layout Data > Select Placement Point > pick the insertion point. No trim lengths.

### Preview image of a parametric part ([G:753874C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-753874C9-E3CA-4B9C-BC93-CB8181A2BBC5), [G:4C3BCDC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4C3BCDC9-47EC-4175-8177-D80598E837D0), [G:95C6FF61](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-95C6FF61-9F4C-45CD-9213-BD913BB7F96C)) [GUI]
- BMP, 200 x 200 pixels, 256 colors. Make one before building, or let Content Builder generate it once the model is final.
- Fitting: toolbar icon. MvPart: Generate Bitmap icon in the part browser. Both open the Bitmap Preview dialog. Generate View offers 10 directions: top, bottom, left, right, front, back, SW, SE, NE, NW isometric. Or Browse to a ready bitmap. MvPart: OK to finish.
- Saved with the part; identifies it during part selection.

### Schematic symbols ([G:9890237D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9890237D-00F2-4CD5-8A21-8763CE8C464C), [G:CE254859](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CE254859-56EA-4C85-9622-C9F506DA98C2), [G:9E5C4254](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E5C4254-ED52-4D3E-AFB0-2118833F32A8), [G:C7EEB82F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C7EEB82F-2E85-4DE0-A2E9-E29CA1DD3C4A), [G:8FBFFC85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8FBFFC85-5DCF-48DD-ACA1-CD169EA52AE7)) [GUI]
- Optional; normally made for schematic diagrams. A part with no symbol is invisible in schematic representations. With a symbol, the part can also show it in 1-line and 2-line Top (plan) views (e.g. to tell supply from return): Options button > Display Symbol In Plan View > OK.
- Only parts added AFTER the symbol exists use it. Inserted parts do not update.
- Symbol and Annotation Plane: horizontal plane made automatically with each new part, far above the WCS origin in Z (zoom out to see it). Move: right-click > Change Plane Position > type Z > Enter. Right-click also gives Visible, Set View (Top is its default), Isolate Plane Contents, Hide Plane Contents, End Object Isolation, Part Boundary.
- Two kinds: Parametric (scales proportionally; parametric geometry, dimensions, constraints) and Block-based (scales uniformly; AutoCAD lines, arcs, circles, drawn from scratch or taken from an existing MEP symbol or 2D block in a DWG).
- Parametric symbol: expand the plane > right-click Parametric Graphics > Add Geometry > Point Reference to bring model points onto the plane; draw the symbol; constrain its corners to the point references, or dimension it and set each dimension's value to the name of the matching model dimension. Part Boundary draws the model outline as a guide; turn it off afterward (it does not resize). Test by changing model parameters and watching both resize. Overlaps: Shift+Spacebar cycles objects; Ctrl+Spacebar cycles solid faces, edges, vertices.
- Block-based from scratch: draw with AutoCAD objects > right-click Design Blocks > Add Schematic Block. [AUTO] Prompts: pick the plane that orients the symbol (Enter = current; a side plane makes it show in sections and elevations); select geometry (parametric geometry is filtered out); Enter; erase source geometry? n + Enter keeps it, y or Enter erases it.
- Block-based from an existing block: right-click Design Blocks > Insert AutoCAD Block > Insert dialog: Browse to the DWG; Name = the block (if the drawing holds one block you may pick the drawing name and tick Explode); insertion point, scale, rotation or Specify On-screen. [AUTO] Prompts: y or Enter = use it as the schematic symbol; erase source geometry? n keeps, y or Enter erases. The block is exploded into a Design Block.
- The block always attaches to the Symbol and Annotation Plane. Usually one symbol and one Design Block per part. Finish with Save Part Family and close the browser.

### Annotation on a symbol ([G:CEAC9403](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CEAC9403-49D7-460B-830F-6827F61ACEA8)) [GUI]
- Expand Modeling > Symbol and Annotation Plane > right-click Annotation Text > Add Annotation Text > pick two corners (sets mtext width) > type in the In-Place Text Editor > click outside, OK, or Ctrl+Enter.
- The text becomes a text block tied to the symbol; it is inserted with the symbol and keeps its relative spot when the symbol resizes. Right-click > Keep Text Horizontal holds it level at any rotation. Delete: select it, press Delete.
- Tip: character height 1 drawing unit, so Annotation Plot Size (Drawing Setup > Scale tab) alone sets plotted size (inches drawing, plot size 3/32", height 1 plots at 3/32").

### Validate, save and preview ([G:496792F6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-496792F6-71A9-4A38-AD24-4FABCF502CDA), [G:3D4E2F1C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D4E2F1C-9E3F-40CE-AD2F-D7E7E8647248), [G:D9B8E9B7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D9B8E9B7-EBD2-4325-9419-754949D78E25)) [GUI]
- Validate button on the toolbar. Pass = green light in the part browser status bar. Fail = red light plus a dialog of errors; fix and validate again. Warnings in the Part Family Validation Results dialog do NOT make a part invalid.
- Save only after a pass. Prompt: Yes = part is visible in the catalog; No = stays hidden (this answer sets Hide Part in Options). Saved at the catalog location chosen for it.
- Preview: right-click Size Parameters > Edit Values > select a row (row 1 is the default size) > Parametric Object Viewer button. Supported only for parametric parts made in Content Builder. Pick other rows or values and the viewer updates; Up/Down arrows step table sizes; Ctrl+Up / Ctrl+Down open list sizes. Pick a view or 3D orbit (drag around the circle). Check every size for badly joined segments.
- Fitting close-out: close the viewer, OK the Size Parameters dialog, Save again, close the part browser.

### Parametric Part Wizard ([G:9F57B992](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9F57B992-77E9-448B-BF3D-6C0732F474F5)) [GUI]
- Home tab > Build panel > Tools drop-down > Parametric Part Wizard. No command-line form is given.
- A part template = a fully configured, fully dimensioned parametric part with a basic model and NO sizes. Imperial and metric catalogs ship templates for common MvParts (air terminals, pumps) and fittings.
- Fields in order: Part Domain (catalog per domain set in Options), Part Type, Part Template (lists show only choices that have templates), Name (the part's XML file name; shown in Content Builder and Catalog Editor), Description (shown in add and modify dialogs; used to build size names), Parameters grid (double-click to type; right-click Copy, Paste, Clear; Table = equal counts, one row per size; List = every combination).
- OK adds the part to the CURRENT catalog, in the chapter matching the part type, then opens Add Multi-view Parts to place it. Later edits or custom data: Catalog Editor or Content Builder (e.g. change the size-name formula).

### Worked model examples, compressed ([G:EBC684DE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EBC684DE-F7BC-4DF2-B647-39163852699B), [G:CA0A0697](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA0A0697-6AFC-4503-BD7B-7A82D1B6823A), [G:328FB8CB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-328FB8CB-29E2-496E-AAAF-BF02F0126DE6), [G:61AD6FD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-61AD6FD5-E05A-43A5-9457-421B156E4997), [G:FD7B9C9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FD7B9C9D-1518-41AC-9F2B-A957B48E4DC6), [G:87A65A73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-87A65A73-2653-4A00-8FA0-9F3AD2EE4DF1), [G:B3592BF6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B3592BF6-7F46-464C-AFA9-55D0917FA24E), [G:E4DAED76](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E4DAED76-9CB3-4B9B-A1F8-5243A2F8CF49), [G:ED63B8D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ED63B8D1-1CA3-41C5-A990-980BD0C3D112), [G:9EC9A8A6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9EC9A8A6-4EFA-489D-ADC8-25CCBFC8358C), [G:BC57E9B8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BC57E9B8-FCD1-46D3-8B76-CCD4CDB8EA68), [G:64540C23](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-64540C23-8659-44CF-8CF7-63D715A8B573), [G:3E7EDC6C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3E7EDC6C-DF95-4A84-9D1D-DDE3A9ACC9B0))
- Ceiling diffuser (MvPart): rectangular profile on XY (top face); Offset plane "Bottom Face" 12" (305 mm) below with a second rectangle; center point plus Equal Distance constraints, Point Reference on the bottom plane; Add Transition top to bottom; Offset plane "Lip Offset" 1" above; extrusion with Termination Type Plane, To = Lip Offset. Dimensions: LenA1, LenA2 top face; LenA3, LenA4 bottom face; LenB1 flex stub set constant 4"; WPOf2 lip 1". Sizes: LenA1 to LenA4 as Table; WPOf1 = -4".
- Junction box (MvPart): rectangle on XY, Blind 15" (381 mm), Flip; knockout point plus Equal Distance; circle r .5" Concentric to the point; Blind 2", Flip. Dimensions: LenB1 = 4"; width: XY Plane > Add Dimension Horizontal Distance, pick 2 corners, [AUTO] type 4" on the command line + Enter (LenA1); depth: Add Dimension Vertical Distance, 2" (LenA2). Size: LenA1 as Table; name formula: insert LenA1, then type "inch Outlet Box".
- Vertical tank (MvPart): circle r 15" on XY (center can be typed, e.g. 15,15), Blind 60" (1524 mm), Flip; Offset plane "Tap Offset" 2"; tap circle r 1"; extrusion Plane To XY Plane. Dimensions: LenB1 body height; WPOf1 tap length 2". Sizes: ND1 and LenB1 as Table; name formula: insert LenB1, then type "inch Vertical Storage Tank".
- Tee (fitting): trunk circle r 12" (305 mm) on YZ, MidPlane 20" (508 mm); hide YZ, show ZX; branch circle r 6" on ZX snapped to the trunk center, Blind 10" (254 mm); Modifiers > branch extrusion > Edit > Flip moves it to the other side. Rename modifiers for clarity (e.g. "Extruded Branch Modifier"). Dimensions in Top view: LenB1 (trunk) = D1 + ( D1 * 0.5); LenB2 (branch) = (0.75 * D1). Sizes: D3 branch list (Edit Values > list-edit button > Add).
- Observed parameter prefixes (not formally defined): LenA = plan dimensions; LenB = heights or extrusion lengths; D = diameters; ND = nominal diameter; WPOf = work plane offset; PrtSN = part size name.

## 6.11 Custom parameters and size data

### Where custom data can be added ([G:7269A48E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7269A48E-5794-4A34-B623-624CF1337344), [G:337E71B9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-337E71B9-DCB9-4DD5-AC3E-51408E952CA2), [G:83F397A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-83F397A9-2FAC-413E-9B37-3B3EA94B5332), [G:5FE8E727](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5FE8E727-B805-4D74-B1B8-BA80925F1CDC))
- Catalog Editor: Insert Column on a storage type (6.6).
- Content Builder, parametric: Size Parameters dialog, Parameter Configuration mode: add from a predefined optional list (e.g. Material, Part Source URL; offer depends on part type and existing parameters) or add custom parameters with all attributes.
- Content Builder, block-based: Property Editor (6.8).
- RULE for schedules: parameter name must equal the property set property name. ([G:92446174](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-92446174-61BD-4136-B79D-5E423C2001B6))

### Custom parameter groups (XLS) ([G:788ADFFB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-788ADFFB-A734-47C9-A6E8-A129223C8592), [G:7269A48E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7269A48E-5794-4A34-B623-624CF1337344), [G:459449F6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-459449F6-5115-4E22-924B-2911FB070973)) [GUI]
- Build a parameter set once, save it as a group in a Microsoft Excel XLS file, load it onto other parts.
- Save: parametric = right-click Size Parameters > Edit Configuration > Size Parameters dialog > Save Custom Parameter Group icon; block-based = MvPart Builder > Properties tab > Edit Properties > Property Editor > Save Custom Parameter Group icon. Dialog "Save a Custom Parameter Group": tick Save in Group per parameter (or Select All); Save Value(s) Yes keeps current values, No does not; File name defaults to a "MEP Parameter Groups" subfolder (any folder allowed). Naming an existing file OVERWRITES its parameters.
- Load: same dialogs > Insert Custom Parameter Group icon > pick the XLS > Open. Values come along. A parameter whose name already exists on the part is NOT added.
- [AUTO] The XLS can be written by hand or by script if it copies the format the feature writes. Only the FIRST worksheet is read.

## 6.12 Testing parts ([G:B03F18E3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B03F18E3-22EE-4EB5-A455-AD96EC69115B), [G:CBC3F108](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CBC3F108-8BD5-4830-8853-56A03E704304), [G:8338A3AC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8338A3AC-6797-4CC1-B032-B5A8A59CC01C), [G:EE478823](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE478823-DA70-4952-A799-5BCC2C77AA0B))
- Test EVERY part size before using it in drawings: insertion point, every display representation, every connector. Fix and retest any bad size.
- Connector position: snap to the connector and connect a segment. A valid connection must form and you must be able to keep drafting the run. Connectors floating in space are misplaced.
- Connector direction: connect a valid object to EVERY connector of every size and draft a run. The default Compass direction must lay the run out away from the part, the right way.
- Display representations: in a drawing from scratch, cycle the viewport's display configurations (Model tab; list at the bottom right under the drawing area). In a drawing from a template, cycle the layout tabs.
- View block orientation: generated view blocks: add the part to a drawing from the MEP 2027 template and cycle the layout tabs. Hand-made view blocks saved as AutoCAD blocks: SW Isometric, [AUTO] insert each at 0,0,0 WCS; top on the top XY face, bottom on the bottom XY face, front and back on XZ, left and right on YZ.
- (inference) Inserting at 0,0,0 and connecting test runs are drawing operations a script could repeat; the docs describe them as hand checks.

## 6.13 Style-based content customization

### Scope and editing rules ([G:624C7B6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-624C7B6B-2E56-4620-80DA-B3354F65902D), [G:8AE18F38](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AE18F38-D993-40B5-A15C-50DE616CC6DA), [G:1BEEE2FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BEEE2FD-894B-482C-8C18-E67AC5B1ECB4), [G:DC7A67B3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC7A67B3-E551-47C0-A960-349A743D66BA))
- New style-based content = create and configure a style. Devices, panels, plumbing fittings and schematic symbols also need view blocks (AutoCAD blocks or an MvBlock).
- Style edits made in a drawing are saved in that drawing only. To change it everywhere, edit the style in the content library drawing that holds it; drawings whose Options content location points at that library get the change.
- Style edit commands listed on [G:1BEEE2FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BEEE2FD-894B-482C-8C18-E67AC5B1ECB4), no syntax given: DUCTSTYLEEDIT, PIPESYTLEEDIT (as printed; (inference) typo for PIPESTYLEEDIT), CABLETRAYSTYLEEDIT, CABLETRAYFITTINGSTYLEEDIT, CONDUITSTYLEEDIT, CONDUITFITTINGSTYLEEDIT.
- Copy a style to another drawing: in Style Manager drag it onto the destination drawing. Its blocks come along.

### Blocks for styles ([G:144EEB2E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-144EEB2E-2849-440E-B924-95A09F56FFEB), [G:DF3201A3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF3201A3-BC08-49CF-9228-23C3AF2D5999))
- Each new symbol, device, panel or plumbing fitting needs at least one block assigned to a view of its style.
- Draw with line, trace, hatch or solid. Do NOT use polyline. (The MvPart symbol page allows polylines, [G:3AC80843](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3AC80843-67E1-4E9A-BE55-5838E5FE7D8F); this rule is for style blocks.)
- A simple 2D block looks the same in every direction; an MvBlock differs per view direction. Each is a "view block".
- Counts: schematic symbol: one 2D plan block (it can generate the 12 isometric view blocks). Device: 2D plan block, plus an MvBlock for the model view (Front, Left...) if sections and elevations must show true size. Plumbing fitting: maybe only a 2D plan block. Other content: 2D and 3D blocks for plan and model views.
- Layer 0; color, linetype AND lineweight each BYBLOCK; insertion point 0,0,0; a unique name per block. (MvPart blocks use lineweight BYLAYER instead, [G:AD10CC62](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AD10CC62-4978-420F-ACE2-763BA813CBE5).) Copy the approach of the shipped styles.

### Style views ([G:9E96BA07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E96BA07-5248-4FEF-B547-515A45CBB2D4), [G:CDFAEBCF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CDFAEBCF-FA70-423D-80AB-770721877184)) [GUI]
- Devices, panels, plumbing fittings: make the blocks in the drawing that will hold the style > create the style > Style Manager > style > Views tab > Add: View Name (e.g. Plan, Model), View Block (any block in the current drawing), Display Representation, View Directions.
- RULE, view selection: the active display representation (from the active display configuration) plus the active view direction must match a style view. One match: its block shows. Several: all show. None: the object is NOT displayed. So removing a view can make every object of that style vanish in that representation and direction.
- Insert as annotation block (Offset in X, Offset in Y): drawn with the object type's Annotation display component. Two views with the same representation and directions can show a symbol block and an annotation block together. Keep text horizontal when rotating works only with annotation blocks.
- Scaling: Use Annotation Scale = annotation plot size (Drawing Setup > Scale tab) times the current annotation scale; the style setting decides, not the block's Annotative property. Override Scale = X, Y, Z factors. Both = override first, then times annotation scale. Neither = no scaling. Plumbing fittings and schematic symbols are always scaled by the current annotation scale in model space.
- Schematic symbols: plan block > create style > Views tab > Generate Isometric Views > Generate Isometric Symbol Blocks dialog: In-line symbol (follows the line direction) or Vertical symbol (stays vertical); Plan block to be used; Use new blocks in the style definition (overwrites assignments; off = blocks made but not assigned) > OK. Then set scaling per view. Advanced Editor opens the Views dialog. OK twice.
- Each MvPart makes a unique view block from its style name and view direction, kept when inserted. ([G:9E96BA07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E96BA07-5248-4FEF-B547-515A45CBB2D4))

### Connectors, design rules, display, notes ([G:6324961B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6324961B-138E-480D-BF9A-E2CDF742525B), [G:732C683D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-732C683D-7C41-483F-81F4-250879003F9D), [G:6BF69459](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6BF69459-DB0A-43E8-B7BD-C8E17652E16D), [G:22761EDA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-22761EDA-9270-4716-B11C-67B2D5B4466F)) [GUI]
- Open a style: Manage tab > Style & Display panel > Style Manager, or select an object > contextual tab > General panel > Edit Style (or right-click > Edit Style).
- Connectors tab: Description (e.g. Air_Supply), Domain, connection point X, Y, Z, or "Add Center Points from View Blocks in Top View"; add and remove buttons. DANGER: changes apply to every instance of the style in the drawing and can break connectivity. Device and plumbing fitting styles have their own connector rules (pages not in these sources).
- Design Rules tab (schematic lines, wires, plumbing lines meeting symbols, devices, panels, plumbing fittings): None, Bounding Box, Inscribed Circle, Circumscribed Circle, Trace Geometry. Style Manager drop-down by workspace: Schematic Symbol Styles, Electrical Device Styles, Electrical Panel Styles, Plumbing Fitting Styles. Existing content updates automatically.
- Display Properties tab: select a representation > Style Override > edit component visibility, layer, color (click Style Override again to clear it). Edit Display Properties > Other tab holds style-specific settings in some representations. Affects all instances.
- General tab: Name (predefined; change with caution, avoid duplicates), Description. Notes button: Notes tab and Reference Docs tab (Add, Edit, Delete). Property Sets button opens Edit Property Set Data (the page's last step calls it Edit Schedule Data).

### Categories ([G:BE30E9DD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE30E9DD-FB27-481A-A27E-50F79BE351A0), [G:C0E4DEF8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0E4DEF8-4F58-49C4-BD55-A68B5059781B)) [GUI]
- Style Manager > expand the Objects node (e.g. Plumbing Objects) > right-click the category node (e.g. Plumbing Fitting Categories) > New > name > Enter > in the right pane, tab named for the type (e.g. Plumbing Fitting) > Add styles.
- Purge deletes a category and its style references; the styles stay. Same steps for device, panel and schematic symbol categories.

### Batch conversion tools [GUI] ([G:E382B42D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E382B42D-BEC3-4E4B-B6C3-081640251B4C), [G:5513128D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5513128D-A404-4109-AE13-993393D4EE57), [G:8ECFDECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8ECFDECD-5DA3-4E5D-B90F-DFB922B01F50), [G:7BA4D514](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7BA4D514-CE24-4516-9769-D67812E8A958), [G:F641206E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F641206E-5B1B-4B5D-870C-BA34530390EA), [G:BB7F5811](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BB7F5811-3620-4345-A3C4-224C307F1B2F), [G:DEE81524](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DEE81524-F545-4CB4-AEE1-2D1149DC04B5), [G:7EB76F97](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EB76F97-61E3-4E50-9890-F0F80A56B90E), [G:425BE254](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-425BE254-DB6B-43FE-B520-E8B9BEEA4590), [G:C47252B2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C47252B2-9187-4B33-9468-5ACC586E965E), [G:32EE25C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32EE25C9-8AD7-4AE9-AF30-D0C7E984B012))
| Command (page metadata) | Ribbon | What it does |
|---|---|---|
| CONVERTDEVICECONTENT | Manage > MEP Content > Batch Convert Devices | blocks to device styles via a CCF script |
| CONVERTSYMBOLCONTENT | Manage > MEP Content > Batch Convert Symbols | blocks to schematic symbol styles via a CCF |
| DECOMPOSEDEVICECONTENT | Manage > MEP Content > Decompose Devices | device styles to block DWGs plus a CCF |
| DECOMPOSESYMBOLCONTENT | Manage > MEP Content > Decompose Symbols | symbol styles to block DWGs plus a CCF |
| CONVERTTODEVICE | Equipment tab > Modify panel > Convert To Device | one block, MvBlock or MvPart to a device and device style |

- No command-line form is documented for any of them; each opens a dialog.
- CCF = Custom Content File: conversion script holding style settings and paths to the drawings with the source blocks. CCT = Custom Content Template: default values used to generate a CCF.
- Batch Convert: Conversion Script File Path (Create / Browse / Edit) > Device (or Symbol) File Browse = target DWG (overwrite: Save, then Yes) > Generate > Log (if errors) or Close. One script makes one drawing.
- Create a script: Convert = Drawing (blocks in one DWG) or Folder (all DWGs in it) > Conversion Template Path (a CCT; Create, or Browse then Edit in the Conversion Template dialog) > Conversion Script Browse (the CCF) > Generate > Close.
- Edit a script (Edit Device Script / Edit Symbol Script): rows for style, view, connector; add or delete each. View Source Block = block drawing path. Connector Placement: Specify (X, Y, Z), Center (view block center), Insert (view block insertion point), Node (a connector at each AutoCAD POINT in the view block).
- ATTENTION: rerunning a conversion OVERWRITES edits made in Style Manager. Change the script, then rerun.
- Decompose: File to Decompose (Current Drawing or a file) > Block Path folder > Script Path > Decompose. Output: one DWG per view block per style, each holding one block definition, plus a CCF. Originals unchanged. GOTCHA: the script sets Connector Placement of ALL connectors to Specify (a style stores positions, not how they were set); fix before reuse.
- Script to Style Manager names: Style Name = Name (General tab). Type, Layer Key, Masking on the Design Rules tab (Masking = Wire Cleanup for devices, Line Cleanup for symbols). Category is not in Style Manager; it groups styles in the Select Device or Select Schematic Symbol worksheet and is created if missing. Annotation View = Annotation Block; Connector Type = System Type; Create ISO Blocks = Generate Isometric Views.
- CONVERTTODEVICE: Device Convert - Behavior dialog: Name (unique), Type (lets a modify command such as LIGHTINGMODIFY act on one type), Layer Key (from the drawing's layer standard and key style), Delete the original object > Next > electrical connectors (Description e.g. Normal Power; System Type, where Power and Lighting adds voltage and load; Add Center Points from View Blocks in Top View; X, Y, Z) > Finish, or Next and tick "Convert all additional references to the selected block in the drawing". Source can be in an xref. Drag the result to a tool palette to make a tool.

### Rise and drop styles ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)) [GUI]
- Commands listed, no syntax given: DUCTRISEDROPSTYLE, PIPERISEDROPSTYLE, CABLETRAYRISEDROPSTYLE, CONDUITRISEDROPSTYLE. Documented route is Style Manager only.
- Sets the symbols for rise and drop conditions in 2-line and 1-line displays of segments and fittings (duct, pipe, cable tray, conduit, plumbing). Duct styles set symbols per shape and can show rise or drop under an MvPart or at a vertical duct endcap.
- Steps: make the symbol blocks > Manage tab > Style & Display panel > Style Manager > expand the objects folder (e.g. Piping Objects) > right-click Rise Drop Styles > New > name > Description, notes > Rise and Drop tab.
- ATTENTION: reconfigure the default symbols but never remove them; they are the minimum set and the style is invalid without them. Pipe: 2-line rise, 2-line drop, 1-line rise, 1-line drop, and 1-line drop for tees and takeoffs only. Plumbing: rise, drop.
- Per symbol: Name; Display Representation (2-line display = Plan or 2 Line rep; 1-line display = 1 Line rep); Block (in the current drawing); Center Line Block (optional); Shape (duct only).
- Options: Show Rise Under MvParts, Show Rise Under Endcaps, Show Drop Under Elbows (elbow with a downward connector), Show Drop Under Endcaps, Show Drop Under MvParts, Drop Tees/Takeoffs Only.
- Scaling: on insert the block is first scaled to 1-unit extents, then: neither option = actual diameter (2-line) or nominal diameter (1-line); Use Annotation Scale and Override Scale as for style views. Center Line Block Scale Factor: 1 = same size, 1.5 = 50% larger.
- Display: symbol follows the Rise Drop display component; center line block follows the Center Line component.

## 6.14 Content tools: tool palettes and Content Browser

### Tools and palettes ([G:5E5CFFD3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5E5CFFD3-055C-49BD-B61B-45F0A8CE31C6), [G:56AAE8B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-56AAE8B1-5180-4AB1-8DE7-9E88D01B7DB9), [G:4A46D471](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4A46D471-116E-4BF6-8622-A735A7C22EAF), [G:304103FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-304103FD-4C25-41AE-879A-1B5B7EBDDFA5), [G:0F5F4DE7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0F5F4DE7-1A24-4A94-8640-A72BAAB51F7C), [G:E1583896](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E1583896-1C31-4B8F-A0DF-A87754416627), [G:9FF82C9E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9FF82C9E-6793-47D9-8548-FF44DDF00ED9))
- Object tools insert an object with stored settings (layer key, layer key overrides, object style). Command tools stand in for a command (e.g. Duct System Size Calculator). Tool description = tooltip.
- Content Browser = library of tool catalogs (tools and palettes); catalogs can be published for network use. Open: Home tab > Build panel > Tools drop-down > Content Browser. Ships the Stock Tool Catalog and the Documentation Tool Catalog.
- Command names given by support: CONTENTBROWSER ([KB:000603500](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/I-can-t-find-symbols-for-electrical-building-systems-MEP-inside-AutoCAD-Electrical-symbols.html), [KB:000470301](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Shared-Custom-Catalogs-on-the-Cloud-for-AutoCAD-Architecture-and-MEP.html)) and AECCONTENTBROWSER ([KB:000572458](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-Browser-can-t-be-opened-in-AutoCAD-Architecture.html)). Not reconciled.
- Tool from DesignCenter AEC content: open the palette > Insert tab > Content panel > Design Center > AEC Content tab > drag the item onto the palette.
- Tool from a routing preference: Manage tab > Style & Display panel > Style Manager drop-down > Routing Preference Definitions > drag the preference onto the matching palette tab. Tool name = preference name; "Standard" gives "Pipe Tool" or "Conduit Tool". Other properties show "--" and then reuse the last values used with that preference.
- Delete a tool: right-click > Delete. Objects already placed with it stay.
- Palette look: right-click > View Options (image size; Icon only / Icon with text / List view; Apply to Current Palette or All Palettes). Rename the set: title bar menu > Rename Palette Set. Change the palettes in the set: Options > Files tab > Tool Palettes File Locations (ATC files), or Options > Profiles tab > Set Current.

### Moving and sharing palettes (support)
- Architecture and MEP have no XTP palette export or import. Bring plain AutoCAD palettes in through Content Browser by adding the ATC catalog, or through the tool palette paths on Options > Files. ([KB:000326211](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Adding-custom-AutoCAD-tool-palettes-to-AutoCAD-Architecture-or-AutoCAD-MEP.html), [KB:000508407](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Export-import-of-Tool-Palettes-not-available-for-AutoCAD-Architecture-or-MEP.html))
- To share a tool catalog, publish it from Content Browser to a shared location and let the publish step copy the tool's dependent files with it. ([KB:000455827](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-share-tool-palette-catalogs-with-other-users-in-AutoCAD-Architecture-or-MEP.html), [KB:000470301](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Shared-Custom-Catalogs-on-the-Cloud-for-AutoCAD-Architecture-and-MEP.html))
- Palettes are tied to the release that made them; move them to a new release with Migrate Custom Settings, not by copying ATC files. ([KB:000470301](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Shared-Custom-Catalogs-on-the-Cloud-for-AutoCAD-Architecture-and-MEP.html))
- Palettes from an older release can be opened as a library in Content Browser and dragged across. ([KB:000255740](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-copy-tool-palettes-from-one-machine-to-the-next-in-AutoCAD-Architecture.html))
- [AUTO] A tool that fails with an unknown-command error often has trailing spaces in its command string; keep tool command strings clean. ([KB:000614085](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Commands-such-as-ADD-CABLE-TRAY-not-working-from-Tool-Palette-in-AutoCAD-MEP.html))
- A greyed-out tool is usually a stale catalog link; the linked article covers clearing and re-setting the refresh source. ([KB:000291384](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Cannot-update-linked-tools-in-a-catalog-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- Adding a large palette at once can hang; add sub-palettes one at a time. ([KB:000258995](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/crash-when-doing-add-to-tool-palette-in-autocad-architecture-or-autocad-mep.html))

## 6.15 Troubleshooting index (support articles)
Short summaries in our own words. Follow the linked article for the exact steps.
- Catalog APC cannot be read, or Options says a catalog is not valid: usually folder permissions on the MEPContent folder; fix permissions, else reinstall. ([KB:000575488](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Catalog-apc-file-not-open-for-read-A-specified-MEP-Catalog-within-Options-is-not-valid-is-displayed-when-adding-any-AEC-object-from-the-ribbon-to-a-drawing-in-AutoCAD-MEP.html))
- A tool cannot find its content DWG: re-add the catalog APCs on the MEP Catalogs tab, repair the install if the content folders are empty, or reset to defaults ([KB:000428447](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-content-file-specified-for-this-tool-cannot-be-found-for-MEP-content-in-AutoCAD-MEP.html)). For older AEC content, install the Architecture content packs ([KB:000361256](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-The-content-file-specified-for-this-tool-cannot-be-found-in-AutoCAD-MEP.html)).
- APC paths missing from Options: browse to each APC again on the MEP Catalogs tab. ([KB:000600828](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-catalog-files-in-AutoCAD-MEP.html))
- Content folders missing or empty: re-install the content packs through Add or Remove Features. ([KB:000292151](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Some-content-folders-missing-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- No default Content Browser catalogs, or an empty Styles Browser: reset settings to default or re-enter the AEC Content paths. ([KB:000304895](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Missing-AEC-object-style-and-Content-Browser-catalogs-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- A tool cannot locate its style or definition: the content folder is missing or the tool's definition location is wrong; point the tool at the right file. ([KB:000264175](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-A-Style-or-Definition-could-not-be-located-for-this-tool-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- Content Browser cannot load a catalog: run one product version at a time; network libraries need the right Content Browser setup; some characters in the Windows user name break palette folders. ([KB:000403701](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-Browser-Catalog-gives-an-error-The-catalog-you-are-trying-to-access-C-users-username-Documents-ACA-or-MEP-cannot-be-loaded-or-is-not-the-correct-file-format-in-AutoCAD-Architecture-or-AutoCAD-MEP.html), [KB:000219733](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-Browser-does-not-work-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- US Imperial tools will not drag and drop under the Global profile: the linked article has a registry repair; back up the registry first. ([KB:000252680](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Cannot-drag-content-from-Content-Browser-to-Tool-Palettes-or-drawing-in-AutoCAD-MEP.html))
- MvPart shows no 3D geometry (often after a recover): compare with a fresh copy of the part from the catalog in a new drawing, then bring the damaged drawing in as an exploded insert; rebuild the part if that fails. ([KB:000347487](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MVPart-not-displaying-in-3D-views-in-AutoCAD-MEP.html))
- MvBlock or MvPart invisible in plan: check the display representation control for Multi-View Block definitions in the current display set. ([KB:000293733](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Multi-view-block-does-not-display-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- Metric part (example: a diffuser) inserts at the wrong size, off by the inch to millimeter factor: the part's source DWG has the wrong drawing units; back it up, fix its units without rescaling, save. ([KB:000659962](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MvPart-from-US-Metric-content-catalog-is-inserted-at-the-wrong-overall-size-in-AutoCAD-MEP.html))
- Rotating an MvPart hides its symbol: add the missing view directions on the style's Views tab, and save the fix into the template. ([KB:000552312](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Symbolic-representation-lost-after-using-the-Rotate-grip-of-MV-Parts-in-AutoCAD-MEP.html))
- Slow MvPart copy between drawings: duplicated classifications in the drawings. ([KB:000570297](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Slow-performance-copying-Multi-View-Parts-into-another-drawing-file-in-AutoCAD-MEP.html))
- Hangers show as squares or cannot be placed: check the hanger style, reset, or start from the default template. ([KB:000606246](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hangers-not-displayed-correctly-in-AutoCAD-MEP.html), [KB:000635940](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-use-or-place-hangers-in-AutoCAD-MEP.html))
- Custom style drawings not showing on other PCs: put the style drawings on a shared folder, add them to the content library as defaults, and point each PC's style paths at that folder. ([KB:000333517](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Custom-styles-don-t-populate-in-Styles-Browser-in-AutoCAD-Architecture-or-AutoCAD-MEP.html))
- MV Block text style changes after insert: the host drawing's text style wins; change it there. ([KB:000590034](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MV-Block-text-style-is-not-changing-the-style-in-the-block-definition-in-AutoCAD-Architecture-or-MEP.html))
- Detail component database cannot be opened: install updates in the right order, confirm the database file exists and is listed in Options, check folder permissions and prerequisites, then repair or reinstall. ([KB:000378520](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-Cannot-open-database-in-AutoCAD-Architecture-or-AutoCAD-MEP-detail-component-manager.html))
- Metric structural member styles: generate them from the Structural Member Catalog (MEMBERCATALOG). ([KB:000522846](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Adding-European-standards-for-Structural-Member-objects-in-AutoCAD-Architecture-or-MEP.html))

## 6.16 What a script can and cannot do here

### Command-line driven (keyword prompts) [AUTO]
- CATALOGREGEN, CATALOGTEST, CatalogMigrate, RedefineFromCatalog: type the command, answer the domain letter (a = all), Enter. Each ends with a results dialog or report that needs OK, then Enter. Only catalogs listed on Options > MEP Catalogs tab are processed. (6.5)
- Results are written to files a script can read: <APC folder>\Validate\Catalog_Regen_Summary.txt and Catalog_Validation_Summary.htm. ([G:7BAF2064](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7BAF2064-25FD-44EA-A018-30ADE8B2CFF9), [G:CC6F94C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CC6F94C5-9049-4703-9528-E53916E74387))
- Command-line prompts inside otherwise dialog-driven work: connector Edit Placement keywords p (position) and n (normal) ([G:17C5625E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17C5625E-7140-4378-847E-B39FBC2B3FBE)); Add Schematic Block plane, selection and erase prompts ([G:C7EEB82F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C7EEB82F-2E85-4DE0-A2E9-E29CA1DD3C4A)); Insert AutoCAD Block "use as symbol" y and "erase source" y/n ([G:8FBFFC85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8FBFFC85-5DCF-48DD-ACA1-CD169EA52AE7)); dimension values typed for Add Dimension Horizontal or Vertical Distance ([G:E4DAED76](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E4DAED76-9CB3-4B9B-A1F8-5243A2F8CF49)); primitive insertion keys n, f, r, m ([G:29076876](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-29076876-6758-4500-B58F-42C54D7136B6)).

### Dialog-only per these sources [GUI]
- MVPARTADD (Add Multi-view Parts), MVPARTMODIFY (Multi-view Part Modify), MVPARTCONVERT (Multi-view Part Convert), CONTENTBUILDER (Getting Started - Catalog Screen, MvPart Builder, part browser), Parametric Part Wizard, Catalog Editor, Import Building Component, Options > MEP Catalogs tab, Style Manager, CONVERTDEVICECONTENT, CONVERTSYMBOLCONTENT, DECOMPOSEDEVICECONTENT, DECOMPOSESYMBOLCONTENT, CONVERTTODEVICE.
- No hyphen (no-dialog) forms, LISP functions or COM members for building parts, editing catalogs or adding MvParts appear in these sources. (inference) Author custom parts once by hand; have scripts place finished catalog parts and run the catalog commands.

### File-level work a script can do [AUTO]
- Build the source drawing for a block-based MvPart: solids on layer 0, BYBLOCK color and linetype, BYLAYER lineweight, POINT objects at connector centers, UCS World, blocks with base point 0,0,0, names ending in "model", a symbol block named "symbol". Keep it OUT of the catalog folders. ([G:AD10CC62](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AD10CC62-4978-420F-ACE2-763BA813CBE5), [G:3AC80843](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3AC80843-67E1-4E9A-BE55-5838E5FE7D8F), [G:4AF72311](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4AF72311-98CD-4B8A-BCC5-4E82F427D9BD))
- Make a custom catalog by duplicating a shipped catalog folder (then edit and regenerate). Write to a local, writable folder. ([KB:000576793](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Create-a-cable-tray-catalog-in-Autocad-MEP.html), [KB:000624685](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-Create-New-Catalog-or-Generate-APC-File-in-AutoCAD-MEP.html))
- Copy and rename primitive DWG files in \ProgramData\Autodesk\MEP <version>\enu\Shared\Primitives. ([G:90661905](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90661905-C46C-4E0C-951B-8FB255104DBF))
- Write a custom parameter group XLS in the format the feature saves; only the first worksheet is read. ([G:7269A48E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7269A48E-5794-4A34-B623-624CF1337344))
- Launch Catalog Editor as a process: C:\Program Files\Autodesk\AutoCAD 2027\MEP\AecbCatalogEditor.exe (test install). Editing inside it is GUI. ([G:32547D08](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32547D08-37B2-46D1-A518-791B1D77D5D4))
- Read part names, subtypes and size ranges from the part XML files before scripting a placement.
- Check \ProgramData\Autodesk\MEP <version>\enu\Shared\AecbCatalogConfig.xml for AecbTableExpandMode = 1. ([KB:000426613](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Unable-to-write-to-file-check-write-permissions-is-received-when-adding-MEP-objects-in-AutoCAD-MEP.html))
- Start MEP with the right profile: acad.exe /ld "...\AecBase.dbx" /p "AutoCAD MEP (US Imperial)" /product "MEP" /language "en-US" (2025 example; 2027 path not verified). ([KB:000601104](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Some-MEP-equipment-might-vary-in-scale-size-when-inserted-into-the-drawing-in-AutoCAD-MEP.html))

### Gotchas that waste runs
- Never EXPLODE a catalog part: it deletes the part definition from the catalog. ([G:C0CC1782](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0CC1782-4848-4AA9-8104-4447FB14560C))
- Catalog edits do not reach parts already in drawings; RedefineFromCatalog updates only parts whose part ID and parameters match. ([G:90577BAD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90577BAD-0F5D-4203-B44F-18CBD9C9CD5E), [G:B28E1DAC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B28E1DAC-5539-4A4B-9EE1-3753FE00956F))
- If two loaded catalogs hold parts with the same ID or name, only the one from the catalog higher in the MEP Catalogs list is offered. ([G:3D87EBEC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D87EBEC-1999-47D3-A504-613F02980DB0))
- The wrong launch profile loads the wrong unit catalogs; equipment then inserts at metric size. ([KB:000343982](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Convert-equipment-from-metric-to-imperial-in-an-existing-imperial-drawing-in-AutoCAD-MEP.html), [KB:000601104](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Some-MEP-equipment-might-vary-in-scale-size-when-inserted-into-the-drawing-in-AutoCAD-MEP.html))
- Help pages point at \enu\Tool Catalogs for part catalogs; the real US Imperial part catalogs are under \enu\MEPContent\USI\, and pipe is split into one APC per material. ([G:67D95B84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67D95B84-81D8-47FA-AB9E-806D280E354A); test install)
- Layer keys offered in Content Builder come only from the current drawing's layer key style; set AecbLayerStd4.dwg and "Mech - AIA 256-color" first. ([G:BB0F03C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BB0F03C9-8009-4486-AACB-7BEB4EB3E021))
- Block-based family: connector count must be equal across sizes. ([G:E1317481](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E1317481-C416-4CAB-A68A-C6516B0BCB1F))
- Parametric part: the first connector placed sets the insertion axes; tee connectors and trim lengths go left to right, then bottom to top. ([G:5ACE727E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5ACE727E-6FB3-4D9B-861F-3AFB9B3C98B7), [G:67822B55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67822B55-7478-4CB9-9D13-5F8A03916844))
- New parts default to hidden (Hide Part Flag on); answer Yes at save or the part will not show in part selection. ([G:5A3DAB85](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5A3DAB85-94A1-456C-B1A0-EB134862EC9A), [G:496792F6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-496792F6-71A9-4A38-AD24-4FABCF502CDA))
- These sources do not say whether the catalog commands or MvPart commands run in the headless Core Console (accoreconsole.exe). Test before relying on it.
