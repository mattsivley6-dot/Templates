# 07 - Styles, the Display System and Layers

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

Citation legend: `G:` links go to Autodesk help pages; `KB:` links go to Autodesk support articles (linked and summarized, not copied); codes with no link have no public URL on file.

This section explains how AutoCAD MEP 2027 decides what an object looks like and which layer it lands on.
It covers the AEC display system (representations, sets, configurations, overrides, cut planes, display by elevation) and how pipes and ducts draw in 1-line, 2-line, plan, elevation and 3D, including hidden lines and rise/drop symbols.
It covers the Style Manager, the Styles Browser, style-based content, and how styles, system definitions and display settings move between drawings.
It covers layer standards, layer key styles, layer key overrides, layer states and viewport layer overrides.
Almost all of it is dialog work. The few command-line pieces are marked [AUTO]; dialog-only items are marked [GUI].

Contents
- 7.1 Automation quick reference (commands, variables, what blocks a script)
- 7.2 Display system structure
- 7.3 MEP display representations and shipped display configurations
- 7.4 Display control hierarchy and overrides
- 7.5 Pipes and ducts: 1-line vs 2-line, hidden lines, crossings
- 7.6 Rise/drop symbols and rise/drop styles
- 7.7 Cut plane and display by elevation
- 7.8 3D, isometric views, elevations and 2D sections
- 7.9 Display Manager tasks
- 7.10 Xrefs and display
- 7.11 Style Manager and Styles Browser
- 7.12 Moving styles, system definitions and settings between drawings
- 7.13 Style-based content
- 7.14 Layer standards, layer key styles and layer keying
- 7.15 Layer key overrides and remapping
- 7.16 Layer states, viewport overrides and other layer tools
- 7.17 Project standards sync for styles and display settings
- 7.18 Troubleshooting checklists
- 7.19 Gaps and conflicts in the sources

Source note: many pages are from the AutoCAD Architecture (ACA) 2027 help. MEP shares the AEC display, style and layer system. Where only an ACA page supports a rule for MEP objects, treat it as likely but not proven (inference).

## 7.1 Automation quick reference

### Commands that open a dialog or palette [GUI]
No command-line (hyphen) form is documented for any of these.
- `DISPLAYMANAGER`: opens Display Manager ([KB:000447005](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Referenced-walls-are-not-displayed-in-a-2D-Section-in-AutoCAD-Architecture-MEP.html), [KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html)). [KB:000468738](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/XCLIP-of-references-does-not-work-for-Top-view-in-AutoCAD-Architecture-MEP.html) prints `DISPLAYMANGER`, a typo.
- `STYLEMANAGER`: opens Style Manager ([KB:000517324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/2D-Section-Elevation-colors-are-different-from-the-model-data-in-AutoCAD-Architecture-MEP.html), [KB:000474189](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Assigning-MEP-object-sub-components-to-specific-layers-in-AutoCAD-MEP.html)). Do NOT use `STYLESMANAGER` for this: it opens the plot style folder ([KB:000218455](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-CTB-or-STB-file-in-AutoCAD-is-not-found-or-missing.html)). [KB:000538630](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Delay-when-multiple-objects-are-selected-in-AutoCAD-Architecture-or-MEP.html) wrongly uses STYLESMANAGER for Style Manager.
- `STYLESBROWSER`: opens the Styles Browser palette ([G:F8A1FAD4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8A1FAD4-FEF0-4848-8D91-D0C9DF74CED5)). [KB:000464059](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Electrical-devices-do-not-display-as-3D-in-AutoCAD-MEP.html) prints `STYLEBROWSER`; the help page spelling wins. `STYLESBROWSEROPEN` and `STYLESBROWSERCLOSE` are names only ([G:1BC76D66](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1BC76D66-BEFB-44EE-A976-87385EFE852A)).
- `DISPLAYMANAGERCONFIGSSELECTION`: same as the status bar display configuration button; a menu of configurations pops up to pick from ([KB:000314102](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-display-configuration-of-an-Architecture-or-MEP-drawing-in-AutoCAD.html); named in the metadata of [G:F2B1D798](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2B1D798-9D12-4A32-81CC-34CCD134072E)). A pop-up pick needs the mouse (inference).
- `AECLAYERORDER`: Define Display Order By Layer dialog ([G:52E7EC1F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52E7EC1F-4663-4D8D-994E-004279747678)).
- `AECPROJECTSTANDARDS`: Configure AEC Project Standards dialog ([G:A5915307](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A5915307-EF29-4865-8CA6-7197BDF44429)).
- `HANGERADD`: opens a form that needs OK ([G:217FD1C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-217FD1C8-B503-48DC-9842-A4F960E5DDE3)).
- Content conversion, all dialogs: `CONVERTTODEVICE`, `CONVERTDEVICECONTENT`, `CONVERTSYMBOLCONTENT`, `DECOMPOSEDEVICECONTENT`, `DECOMPOSESYMBOLCONTENT` ([G:425BE254](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-425BE254-DB6B-43FE-B520-E8B9BEEA4590), [G:E382B42D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E382B42D-BEC3-4E4B-B6C3-081640251B4C), [G:5513128D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5513128D-A404-4109-AE13-993393D4EE57), [G:DEE81524](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DEE81524-F545-4CB4-AEE1-2D1149DC04B5), [G:7EB76F97](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EB76F97-61E3-4E50-9890-F0F80A56B90E)).
- Named in page headers with no syntax: `DUCTSTYLEEDIT`, `PIPESYTLEEDIT` (spelled so on the page; probably PIPESTYLEEDIT, inference), `CABLETRAYSTYLEEDIT`, `CABLETRAYFITTINGSTYLEEDIT`, `CONDUITSTYLEEDIT`, `CONDUITFITTINGSTYLEEDIT` ([G:1BEEE2FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BEEE2FD-894B-482C-8C18-E67AC5B1ECB4)); `DUCTRISEDROPSTYLE`, `PIPERISEDROPSTYLE`, `CABLETRAYRISEDROPSTYLE`, `CONDUITRISEDROPSTYLE` ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)); `CONTENTBUILDER` ([G:624C7B6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-624C7B6B-2E56-4620-80DA-B3354F65902D)); `AECBLAYERSTD` ([G:EEE2228A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EEE2228A-8605-4040-8587-4BCA2CC4A4D3)); `HANGERSTYLE`, `HANGERSTYLEEDIT` ([G:C98DAE80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C98DAE80-7EDF-4D4C-ABE0-3437BC6EE6F8)). Test before scripting.
- Ribbon-only (no command name in sources): Layer Key Styles, Layer Key Overrides, Select Layer Standard, Remap Object Layers (its prompts are command-line, see below).

### Command-line forms with known prompts [AUTO]
- `REA` (Regenerate All): run after any display change ([G:840AF8C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-840AF8C9-0CB1-450B-A592-2294CA3797C6), [G:F2B1D798](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2B1D798-9D12-4A32-81CC-34CCD134072E)). After Gap Width changes [KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html) says REGEN and REGENALL.
- `OBJRELUPDATE`: regenerates AEC objects when a viewport does not refresh after a view direction change in a shade mode other than 2D wireframe. Select objects, or Enter for all ([G:CA060AC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CA060AC6-37FD-4B22-BC7E-82498BC679E3)).
- `DISPLAYDXFNAME`: answer `y`, then REA. Every object is labeled with its object name, even objects that do not display. Turn off: DISPLAYDXFNAME, `n` ([G:0EE48E90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0EE48E90-9F94-4CE9-84FE-7BC51E09DCD2)).
- `SETXREFCONFIG`: select the xref; `Y` to override its display configuration; F2 lists the xref's configurations; type the number ([KB:000314102](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-display-configuration-of-an-Architecture-or-MEP-drawing-in-AutoCAD.html)).
- `AECTOGGLELKEYOVERRIDESMNU`: toggles layer key overrides for the current layer key style ([G:3B46B590](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B46B590-E204-42A0-AFC0-9EE7489D787F)).
- `AECPURGELAYERSTYLES`: purges ALL layer standards and ALL layer key styles. No prompts documented ([G:0E8CFE23](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0E8CFE23-734E-43E9-A515-63439478BE89)).
- `AECLYIMPORT`: file name (or `?` to browse), then a name for the new layer key style, then a dialog to pick LY sections, OK ([G:104881DE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-104881DE-B5D9-4792-B6BE-A269F0EF1763)).
- Remap Object Layers (ribbon Home tab > Layers panel; command name not given): select objects, Enter, type a layer key name; `?` lists keys; `o` (byObject) restores each object's default key layer ([G:94D29AE1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94D29AE1-E92C-4626-9F29-B94AB1DFEA21), [G:C168FBC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C168FBC2-DC8B-4FF1-94B4-51EA95C7B83B)).
- `AECSHOWOBJECTDISPLAYOVERRIDES`: finds objects with object-level display overrides ([G:A5915307](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A5915307-EF29-4865-8CA6-7197BDF44429)).
- `AECSYNCHRONIZEPROJECTDRAWING`, `AECSYNCHRONIZEPROJECT`: no interaction only if the project sync option is Automatic ([G:A5915307](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A5915307-EF29-4865-8CA6-7197BDF44429)).
- `AECCHANGEDISPLAYTABSTATUS`: hides or shows the Display tab of the Properties palette ([G:6C92CA39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6C92CA39-53A5-4A22-9493-6E2033558CB6)).
- `2DSECTIONRESULTEDIT`, `2DSECTIONRESULTMERGE`: edit or merge 2D section linework ([KB:000367898](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-add-remove-or-modify-elements-in-a-2D-Section-in-AutoCAD-Architecture.html)).
- AutoLISP layer states: `layerstate-addlayers`, `layerstate-export`, `layerstate-getlayers`, `layerstate-import`, and a restore function the page prints as `layerstate-retore` (inference: `layerstate-restore`; verify) ([G:9599CE8D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9599CE8D-A8B0-48E6-850F-CB007668BA33)).

### System variables
- `TILEMODE`: the drawing default display configuration applies to new viewports and to model space when TILEMODE = 1 ([G:F2B1D798](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2B1D798-9D12-4A32-81CC-34CCD134072E)).
- `LTSCALE`: multiplies each AEC component linetype scale (component 1.0 x LTSCALE 48 = 48; component 2.0 gives 96) ([G:8EBE0D10](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8EBE0D10-AFF8-4D15-8174-ECB67894AA7D)).
- `VPLAYEROVERRIDES` (read: 1 = current viewport has layer overrides), `VPLAYEROVERRIDESMODE` (0 = overrides not shown or plotted, can still be set), `VISRETAIN` (0 = xref layer overrides not kept), `PSTYLEMODE` (1 = named plot styles, needed for VP Plot Style) ([G:8909084C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8909084C-770C-41A3-A782-CCABE9DC433A), [G:1175F5BC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1175F5BC-40DB-4EB9-8AAF-715C28F1B2F7)).
- `XREFOVERRIDE`: [KB:000257034](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Xref-layers-reset-upon-reopening-drawing.html) lists value 1 as both a cause and a fix of lost xref layer overrides. Test both values.
- `XLOADCTL` = 2 (default) is required for project standards ([G:B9479240](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B9479240-6946-4C2A-8E0F-A162E91FE084)).
- `FASTSHADEDMODE` = 0 fixes Realistic artifacts in 2027 and blank or vanishing shaded geometry ([KB:000639112](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-and-MEP-Feature-Incorrect-Rendering-Of-3D-Model-When-Switching-To-Realistic-Visual-Style.html), [KB:000498570](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Structural-members-disappear-or-do-not-display-correctly-with-shaded-fast-visual-styles-in-Advance-Steel.html), [KB:000564100](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/3DCLIP-viewer-blank-in-AutoCAD-2025.html)).
- `PROXYGRAPHICS` = 1 before saving AEC objects to an older DWG so they display (not edit) there ([KB:000266207](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-MEP-AEC-Objects-not-showing-in-previous-versions-of-AutoCAD.html), written for 2018).
- `AECCLASSIFICATIONMERGEBEHAVIOR` = 1 stops duplicate classifications on insert ([KB:000349514](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Classifications-get-silently-duplicated-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- `AECSTYLESBROWSERSTATE`: read-only, not saved, 0 = Styles Browser closed, 1 = open ([G:1BC76D66](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1BC76D66-BEFB-44EE-A976-87385EFE852A)).
- `ANNOMONITOR` 0 hides solution-tip triangles; `SOLUTIONTIPICONSIZE` sets their size ([KB:000545330](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-turn-off-warning-triangle-with-exclamation-point-in-AutoCAD-Architecture-and-MEP.html), [KB:000554513](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Warning-symbol-size-in-AutoCAD-Architecture-or-MEP.html)).

### What this means for scripts (inference from the sources)
- Display configurations, sets, reps, styles, system definitions, layer standards and key styles live in the drawing and are edited only in dialogs. Display settings are per drawing and belong in templates (KB:ts-5ibXLTjd, [G:CFD43F8A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFD43F8A-BCA7-46DF-98FF-1DC941C84F97), [KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html), [G:4DC38FB6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4DC38FB6-0C3F-4536-8C54-3F7AEC930AA2)).
- So build them once in a template DWT by hand. Start every scripted drawing from that template. At run time a script then needs only REA, SETXREFCONFIG, the layer key override toggle, Remap Object Layers and system variables.
- A drawing started from acad.dwt has only the Standard configuration, so MEP objects can draw wrong ([KB:000290064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-MEP-AEC-objects-not-visible-in-files-created-with-acad-dwt-template.html), [KB:000598575](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-turns-into-skeleton-when-attempting-to-hatch-in-AutoCAD-MEP.html)).

## 7.2 Display system structure

### The three levels
- Display representation ("rep"): how one object type draws in one kind of view. Holds per-component visibility, layer, color, linetype, lineweight, plus object-specific items. MEP calls it the first level of display control ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4), [G:A54D85B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A54D85B9-DA09-4EA2-8E2D-67F05E372633)).
- Display set: which reps are checked for each object type. Second level ([G:9B167879](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9B167879-BB74-4DA8-88FA-CE9BA40089FC)).
- Display configuration: one display set per view direction: Top, Bottom, Left, Right, Front, Back and Default. Final level ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)). It is assigned to a layout viewport, to model space or to a tiled viewport ([G:1C82E74B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1C82E74B-75A8-45F7-9035-BF2513544904), [G:840AF8C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-840AF8C9-0CB1-450B-A592-2294CA3797C6)).
- Each configuration holds sets; each set holds reps ([G:6CDB2182](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CDB2182-F5CE-48E1-8BF0-A4D56F3A4938)).

### How an object gets drawn (render chain)
1. The viewport has a view direction and a display configuration.
2. The configuration picks the set mapped to that view direction.
3. The set picks the checked rep(s) for the object type.
4. The object draws with that rep's display properties, unless a style or object override applies ([G:BA31AA3B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA31AA3B-5E14-410B-9AD8-661A9E4D47A8), [G:0E3128EA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0E3128EA-398E-4CD1-8A4D-412027A659BC)).

### Rules that cause most surprises
- Any view direction with no set assigned, and all four isometric views, use the set mapped to Default ([G:D3805A7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D3805A7C-58D9-4443-9A32-A30D8270C133), [G:BA31AA3B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA31AA3B-5E14-410B-9AD8-661A9E4D47A8)). When iso views look wrong, check the Default set.
- No rep checked for an object type in the active set: that object does NOT draw ([G:547A986E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-547A986E-B800-4B21-806A-9DB098F022C8), [G:89C368FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89C368FF-0781-439D-9E4A-283E062A80D8)).
- Two reps checked for one object: both draw ([G:547A986E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-547A986E-B800-4B21-806A-9DB098F022C8)). To switch reps, check the new one AND clear the old one.
- Reps and sets are not bound to a view direction. They are only designed with one in mind ([G:0E3128EA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0E3128EA-398E-4CD1-8A4D-412027A659BC)).
- Edits flow outward. A rep edit changes every set and configuration that uses it. A set edit changes every configuration that uses it. A configuration edit changes every viewport that uses it. To limit the effect, duplicate the item and assign the copy ([G:3BA802C3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3BA802C3-BBA9-4687-BCAF-37ADBBB81590), [G:A54D85B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A54D85B9-DA09-4EA2-8E2D-67F05E372633)).
- Example: the Duct Plan rep is checked in sets MEP Design, Mechanical Duct - 2 Line Plan, Mechanical Plan, MEP Design - Plan, MEP Section & Elevation, Plan and Reflected, so one edit to it hits all of them (KB:ts-5ibXLTjd).
- Display Manager edits change only the drawing DEFAULT. Style overrides and object overrides still win ([G:A54D85B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A54D85B9-DA09-4EA2-8E2D-67F05E372633), [G:3BA802C3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3BA802C3-BBA9-4687-BCAF-37ADBBB81590)).
- Component defaults: layer 0, color and linetype ByBlock, so components inherit from the parent object ([G:A54D85B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A54D85B9-DA09-4EA2-8E2D-67F05E372633)).
- In the Representations by Object grid, a checked box means visible and editable; unchecked means the object cannot be edited in that set (KB:ts-5ibXLTjd).
- Display settings are stored per drawing. Objects copied or dragged into another drawing use the destination drawing's configuration ([G:51D63433](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-51D63433-681B-44D0-A069-FA4C2429A778)).

### What every drawing has
- Default display sets in every drawing, even without a template: Elevation, Model, Model High Detail, Model Low Detail, Plan, Plan High Detail, Plan Low Detail, Reflected ([G:89C368FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-89C368FF-0781-439D-9E4A-283E062A80D8)).
- A drawing not made from an AEC template has only the Standard configuration (Plan and Model sets) ([G:BA31AA3B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA31AA3B-5E14-410B-9AD8-661A9E4D47A8)).
- Templates add the working configurations and assign them to layout viewports ([G:8512B736](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8512B736-FC8A-4559-BFF5-7F097517A1C2)).
- Per-drawing default configuration: Utilities > Drawing Setup > Display tab ([G:6CDB2182](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CDB2182-F5CE-48E1-8BF0-A4D56F3A4938), [G:F2B1D798](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2B1D798-9D12-4A32-81CC-34CCD134072E)).

## 7.3 MEP display representations and shipped display configurations

### Representations ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4), [G:6CDB2182](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CDB2182-F5CE-48E1-8BF0-A4D56F3A4938))
- Most MEP objects have 1 Line, 2 Line, Model and Plan. Label curves and schematic objects have only General.
- 1 Line: centerline of the object in 2D or 3D. Sometimes used for isometric drawings.
- 2 Line: 2D or 3D contour in plan and model. Fast display engine. For speed it does NOT show hidden lines or rise/drop symbols.
- Plan: 2D or 3D contour. Slower engine, higher quality, better for plotting. Shows hidden lines and rise/drop symbols.
- Model: full 3D wireframe.
- Plan Presentation: all objects screened, hatching shown (display themes, interference highlighting). Plan Screened: same with no hatching.
- Schematic: 2D symbol of 3D MvParts for schematic diagrams.
- General: objects that need no per-rep graphics (annotation, plumbing lines, plumbing fittings).
- Screened variants (1 Line Screened, 2 Line Screened, Model Screened, Schematic Screened, General Screened) equal the base rep but screen the object as background.
- Plan High Detail, Plan Low Detail, Reflected: ACA reps carried into MEP, unused by MEP.
- Preview any object in any rep and view direction: Floating Viewer button in Display Manager [GUI].
- Layers that hold screened and hidden-line graphics:
  - Screened background objects: `G-Bgrd-Std-Scrn`
  - Mechanical hidden lines: `M-Hidn-Std-High`, `M-Hidn-Std-Subd`
  - Electrical hidden lines: `E-Hidn-Std-High`, `E-Hidn-Std-Subd`
  - Plumbing hidden lines: `G-Hidn-Std-High`

### Configurations in the Aecb Model templates ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0))
Each maps one set to Top and one set to all other directions (Bottom, Left, Right, Front, Back, Default). The page labels the column "Display Representations by view direction", but the names match display set names used elsewhere (KB:ts-5ibXLTjd), so read them as set names (inference).
- Standard: Plan (Top), Model (others). Not recommended for building systems (non-building-systems objects draw in full color).
- Mechanical: Mechanical - Plan / Mechanical - Model. Combined duct and pipe. Piping and equipment 2-line, but system definitions can switch 2-line, 1-line or graphical 1-line by size. Hidden lines and rise/drop on. Plan rep for mechanical objects, Plan Screened for electrical and plumbing.
- Mechanical - Duct/Pipe - 1-Line: Mechanical - Duct/Pipe 1-Line Plan / Model. 1-line duct; pipe 1-line and screened. Rise/drop on, hidden lines off. Non-duct screened.
- Mechanical - Duct/Pipe - 2-Line: Mechanical - Duct/Pipe 2-Line Plan / Model. Duct, pipe and equipment 2-line; system definitions can pick 1-line or graphical 1-line by size; pipe by size and screened. Hidden lines and rise/drop on. Non-duct screened.
- Mechanical - Pipe by Size: Mechanical - Pipe By Size Plan / Model. Pipe 2-line, 1-line or graphical 1-line by size from the system definitions. Hidden lines and rise/drop on. Non-pipe screened (Plan for pipe, Plan Screened for other trades).
- Electrical, Electrical - Lighting, Electrical - Power: electrical drawings; non-electrical screened; hidden lines and rise/drop on.
- Plumbing: Plumbing - Plan / Model. Pipes 1-line, ducts 2-line. Hidden lines and rise/drop on. Non-plumbing screened.
- MEP Basic 2-Line: 2-line duct, pipe and cable tray, IGNORING system definition 1-line settings. No hidden lines, no rise/drop. Lower detail, faster engine. Suited to Model views.
- MEP Design: design and coordination; shows architecture, building systems and ceiling grid. Large pipe and equipment 2-line, small pipe 1-line per the "Pipe By Size" setting in system definitions. Parts and fittings scale for 2-line and 1-line, not for graphical 1-line. Hidden lines and rise/drop on.
- MEP Presentation: screens everything except display themes and interferences.
- MEP Schematic: shows 3D equipment and pipe as schematic symbol reps. Hidden lines and rise/drop on. Graphical 1-line unavailable.
- For chilled-water and HVAC piping plans, Mechanical - Pipe by Size, Mechanical and MEP Design give size-based 1-line/2-line piping with hidden lines and rise/drop (inference from the list above).
- In these shipped configurations, elevations (Front, Back, Left, Right) and isometric views get the Model set ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0), [G:D3805A7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D3805A7C-58D9-4443-9A32-A30D8270C133)).

### Templates
- Aecb Model: design of building systems. Aecb Sheet: plotting. They set units, scales, annotation size, layouts, display reps and plot setups ([G:E53C7990](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E53C7990-6DA7-4591-A91F-9AF825911854)).
- [KB:000290064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-MEP-AEC-objects-not-visible-in-files-created-with-acad-dwt-template.html) (written for 2013 to 2017) lists MEP templates, default marked *: Global *Aecb Model (Global Ctb).dwt, Aecb Model (Global Stb).dwt; Imperial *Aecb Model (Imperial Ctb).dwt, Aecb Model (Imperial Stb).dwt; Metric *Aecb Model (Metric Ctb).dwt, Aecb Model (Metric Stb).dwt. 2027 names not confirmed there.
- Template folder: ProgramData\Autodesk\MEP <version>\enu\Template ([G:3EA8420D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3EA8420D-73B4-4B06-A7A9-D1AE95CF7ABA)).
- acad.dwt has only the Standard configuration; AEC content and xrefs from it can display wrong. Set QNEW's default template: OPTIONS > Files tab > Template Settings > Default Template File Name for QNEW ([KB:000290064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-MEP-AEC-objects-not-visible-in-files-created-with-acad-dwt-template.html)).
- Ducts that draw as hatched outlines with no proper plan look: the drawing has only the Standard configuration. Move the content into a drawing started from an MEP template, or in the Standard configuration's plan set switch the duct objects from the 2 Line rep to the Plan rep ([KB:000598575](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Duct-turns-into-skeleton-when-attempting-to-hatch-in-AutoCAD-MEP.html)).

## 7.4 Display control hierarchy and overrides

### MEP order of control ([G:2AAC9199](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2AAC9199-ECCA-44FC-BFBB-7A7AC639CF2D))
- Object > Style > System Definition > Domain Drawing Default.
- If a level has no override, control falls to the next level down. Removing an override hands control to the next level.
- The Properties palette Display tab shows the active level in "Display controlled by". Values listed: Object, Style, System definition, Domain drawing default ([G:E45168F3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E45168F3-6999-41DB-A693-292AD1432D50); that page says "3 options" and lists four, so trust [G:2AAC9199](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2AAC9199-ECCA-44FC-BFBB-7A7AC639CF2D)).
- ACA pages describe three levels for AEC objects: drawing default, style override, object override. Components set to ByMaterial take their look from the material's display properties ([G:0E3128EA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0E3128EA-398E-4CD1-8A4D-412027A659BC), [G:6C92CA39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6C92CA39-53A5-4A22-9493-6E2033558CB6), [G:3BA802C3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3BA802C3-BBA9-4687-BCAF-37ADBBB81590)).

### Domain sync ([G:2AAC9199](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2AAC9199-ECCA-44FC-BFBB-7A7AC639CF2D))
- Display property changes sync across every object type in a domain.
- Pipe domain: pipe, pipe fitting, pipe custom fitting, pipe flex.
- Duct domain: duct, duct fitting, duct custom fitting, duct flex.
- Also cable tray + cable tray fitting; conduit + conduit fitting; plumbing line + plumbing fitting.
- Example: change duct segments controlled by Drawing Default and duct fittings, custom fittings and flex change too. Adding or removing a system override also syncs the domain.

### Where to change what
- Drawing default for duct, pipe, cable tray and conduit domains: Style Manager, on the system definition (one change hits the whole domain). All other object types: Display Manager ([G:4DC38FB6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4DC38FB6-0C3F-4536-8C54-3F7AEC930AA2)).
- System-level override: all objects on that system, for example an exhaust duct system. Style-level override: all objects of that style, for example a device style ([G:4DC38FB6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4DC38FB6-0C3F-4536-8C54-3F7AEC930AA2)).
- [GUI] System definition route: Manage tab > Style & Display panel > Style Manager > expand the object folder (for example HVAC Objects) > system definitions > pick a system > Display Properties tab > double-click a rep (for example Plan) > edit component properties ([G:8C1E9519](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C1E9519-DFA8-4EFA-9603-E8674E52C638)). If that system's override box is ticked for the rep, the double-click opens the system's own override instead of the drawing default ([KB:000467587](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MEP-component-not-matching-layer-color-in-AutoCAD-MEP.html)).
- [GUI] Display Manager route: Representations by Object > double-click the object > pick the rep > Layer/Color/Linetype tab ([G:8C1E9519](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C1E9519-DFA8-4EFA-9603-E8674E52C638)).
- Style Manager and Display Manager show the full unfiltered component list. The Properties palette Display tab shows only components of the selected object ([G:8C1E9519](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C1E9519-DFA8-4EFA-9603-E8674E52C638)).
- Tabs differ by object and rep. A device in Model shows only Layer/Color/Linetype; in Plan it also shows Hatching ([G:8C1E9519](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C1E9519-DFA8-4EFA-9603-E8674E52C638)).

### Properties palette Display tab [GUI] ([G:E45168F3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E45168F3-6999-41DB-A693-292AD1432D50), [G:6C92CA39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6C92CA39-53A5-4A22-9493-6E2033558CB6))
- Click Select Components, then click a component of an object in the drawing.
- Set color, layer, linetype, linetype scale, lineweight, visibility. Changes show at once.
- Scope: all objects of the type, all of the style, or only the selected object.
- A button on the General title bar (shown only when a component is selected) opens "Apply Display Component Properties to Other Display Representations". It lists only reps valid for that component and changes them at the same control level.
- `AECCHANGEDISPLAYTABSTATUS` [AUTO] toggles this tab on and off ([G:6C92CA39](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-6C92CA39-53A5-4A22-9493-6E2033558CB6)).

### Overrides on a pipe, duct or style [GUI]
- Drawing default for one object type: select a pipe or duct > right-click > Edit Object Display > double-click the rep shown in bold. If the Object Override box is on, this opens that one object's settings instead ([KB:000467587](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MEP-component-not-matching-layer-color-in-AutoCAD-MEP.html)).
- Style or system override: select an object > contextual ribbon Edit Style or Edit System Style > Display Properties tab > select the rep > tick Style Override > Edit Display Properties. Clear the box to fall back to the default ([G:6BF69459](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6BF69459-DB0A-43E8-B7BD-C8E17652E16D), [KB:000376064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-objects-do-not-change-color-although-the-display-configuration-was-adjusted-in-AutoCAD-Architecture-MEP.html)).
- The brush button at the bottom of the Display tab reaches the same place ([KB:000376064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-objects-do-not-change-color-although-the-display-configuration-was-adjusted-in-AutoCAD-Architecture-MEP.html)).
- `AECSHOWOBJECTDISPLAYOVERRIDES` [AUTO] finds objects that carry object-level overrides ([G:A5915307](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A5915307-EF29-4865-8CA6-7197BDF44429)).

### Common fixes
- Display Manager edit "does nothing": the wrong rep was edited, or the style has a Style Override. Trace it from the current (bold) configuration to the set mapped to this view direction, then to the rep that set uses for the object type, and edit that rep. Still unchanged: look for the style override ([KB:000376064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-objects-do-not-change-color-although-the-display-configuration-was-adjusted-in-AutoCAD-Architecture-MEP.html)).
- MEP object color does not match its layer: a component is set to a color instead of BYLAYER. Set Contour (and fittings, insulation and other components) to BYLAYER in the drawing default or in the style/system override. For 3D, switch to a 3D view first so the 3D rep is the bold one ([KB:000467587](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MEP-component-not-matching-layer-color-in-AutoCAD-MEP.html)).
- Put a sub-component such as insulation on its own layer: style override on the style or system definition, set that component's layer. The object itself still takes its layer from its layer key ([KB:000474189](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Assigning-MEP-object-sub-components-to-specific-layers-in-AutoCAD-MEP.html)).
- Same object, different color in a layout viewport and in model space: the two use different display configurations. Give both the same configuration ([KB:000528438](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Objects-are-displayed-with-different-color-in-a-viewport-compared-to-model-space-in-AutoCAD-Architecture-or-MEP.html)).

## 7.5 Pipes and ducts: 1-line vs 2-line, hidden lines, crossings

### What picks 1-line or 2-line
- One object can draw as 1-line or 2-line (or other views) without redrawing it ([G:FBC9F4D1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FBC9F4D1-E6B4-4217-BA62-E8E59FB86CBA)).
- The active set decides: 1 Line rep = centerline; 2 Line or Plan rep = contour ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4)).
- In the size-based configurations (Mechanical, Mechanical - Duct/Pipe - 2-Line, Mechanical - Pipe by Size, MEP Design) the system definition can switch each pipe to 2-line, 1-line or graphical 1-line by size, the "Pipe By Size" setting ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)).
- MEP Basic 2-Line forces 2-line and ignores the system definition settings ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)).
- MEP Design scales parts and fittings for 2-line and 1-line, not for graphical 1-line ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)).
- Where the Pipe By Size setting sits inside the system definition dialog is not described in these sources.

### Hidden lines
- Hidden lines (one object passing under another at a different elevation) draw only in Plan reps. 2 Line reps never show them ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4)).
- Configurations with hidden lines off: Mechanical - Duct/Pipe - 1-Line, MEP Basic 2-Line ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)).
- Mechanical hidden-line graphics use layers M-Hidn-Std-High and M-Hidn-Std-Subd ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4)).
- Hidden-line look, layers, linetypes and color of crossing objects in 2-line plan views can be configured ([G:830BDD0F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-830BDD0F-1287-4F27-8329-2A85C11570E9)). The procedure page "To Configure the Display of a Gap Between Crossing Objects" is not in these sources.

Hidden pipe or duct draws continuous instead of dashed ([KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html)): first confirm that the hidden components of the rep the active set uses carry a dashed linetype (Display Manager). If they do, the dashes are too fine to see: lower LTSCALE or the component's LT Scale [AUTO], or widen the gap width on the MEP Display Control tab of OPTIONS [GUI], then regenerate. A drawing started from plain acad.dwt has no MEP configurations to switch to; move its content into a drawing started from an MEP template.

Other display switches in OPTIONS > MEP Display Control [GUI]:
- "Hidden Line for multiview parts": enable it when MvPart colors are inconsistent in the MEP Design configuration ([KB:000600403](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Inconsistent-color-display-of-multi-view-blocks-in-MEP-design-display-configuration-in-AutoCAD-MEP.html)).
- [G:F9A8BE6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F9A8BE6B-BEF9-4754-B62C-C35A877B5798) links this tab to duct center line display, the crossing gap and display by elevation. Only the gap setting is confirmed on it ([KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html)); the others are inference.

### Hiding by classification
- A set's Display Options tab has a Classification Filter. Clear a classification to hide it in viewports that use that set. Objects stay in the drawing ([G:EC377F07](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EC377F07-7AAC-4791-955F-01C163762562), [G:7705802A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7705802A-B26E-4F5B-8637-FA54C4F2B3D3)).
- An MvPart or device type cleared there is hidden whatever its layers do (KB:ts-5ibXLTjd).
- Neighbours do not change: hide dampers and the connecting ducts end where the dampers sit ([G:7705802A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7705802A-B26E-4F5B-8637-FA54C4F2B3D3)).
- Classifications holding only plain AutoCAD objects are not listed ([G:EC377F07](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EC377F07-7AAC-4791-955F-01C163762562)). Devices ship with a Device Type classification used by many supplied sets ([G:A6203E1D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6203E1D-856F-41D7-941D-81663C6DEBA4)).

## 7.6 Rise/drop symbols and rise/drop styles

### When a symbol shows
- Rise condition: an unconnected end of a vertical segment or fitting is visible in the current view. Drop condition: the segment or fitting is vertical but has no visible unconnected end ([G:70D697C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-70D697C7-DA1C-4FEE-B101-85FC9792544C)).
- Used in the orthographic views: Top, Bottom, Left, Right, Front, Back ([G:70D697C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-70D697C7-DA1C-4FEE-B101-85FC9792544C)).
- Drawn by Plan reps, never by 2 Line reps ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4)). Configurations with rise/drop off: MEP Basic 2-Line ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)).
- The symbol block, and its visibility, follows the "Rise Drop" display component of the current rep. The center line block follows the "Center Line" component. So they can be styled separately ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)).
- Plan reps also have a "Rise Drop - Above" component for objects above the display range ([G:17BF13BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17BF13BF-C73F-403F-B695-47766CFB78D7)).
- Rise/drop symbols inherit the parent object's elevation-based display ([G:CFD43F8A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFD43F8A-BCA7-46DF-98FF-1DC941C84F97)).

### Rise/drop styles
- A rise/drop style sets the symbols and the 2-line and 1-line displays that use them. Types: duct, pipe, cable tray, conduit, plumbing ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23), [G:70D697C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-70D697C7-DA1C-4FEE-B101-85FC9792544C)).
- Duct styles hold separate symbols per shape (round, rectangular, oval). They can show a symbol where a duct or pipe runs under an MvPart or where a vertical duct has an endcap ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)).
- Use one rise/drop style per system, for example supply vs return, so systems look different ([G:70D697C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-70D697C7-DA1C-4FEE-B101-85FC9792544C)). (inference: the style is picked in the system definition; the sources do not show where.)
- Commands named with no syntax: `PIPERISEDROPSTYLE`, `DUCTRISEDROPSTYLE`, `CABLETRAYRISEDROPSTYLE`, `CONDUITRISEDROPSTYLE` ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)).

[GUI] Create a pipe rise/drop style ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)):
1. Make the symbol blocks in the current drawing (rules below).
2. Manage tab > Style & Display panel > Style Manager.
3. Expand Piping Objects > right-click Rise Drop Styles > New > type a name > Enter.
4. Select it; enter Description; optional notes and reference docs.
5. Rise and Drop tab. The top pane lists default symbols; the selected symbol's settings show below.

Required default symbols. Reconfigure them, never remove them, or the style is not valid ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)):
- Pipe: 2-line rise, 2-line drop, 1-line rise, 1-line drop, 1-line drop for tees and takeoffs only.
- Plumbing: rise, drop.

Per-symbol settings ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)):
- Name: say where it is used.
- Display Representation: 2-line display uses a Plan or 2 Line rep; 1-line display uses a 1 Line rep.
- Block: a block in the current drawing. Center Line Block: optional, also in the current drawing.
- Shape: duct and duct fitting styles only.
- Add button = extra graphic for a specific condition. Remove button = delete a symbol.

Options ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)):
- Show Rise Under MvParts; Show Rise Under Endcaps.
- Show Drop Under Elbows (elbow with a connector pointing down); Show Drop Under Endcaps; Show Drop Under MvParts.
- Drop Tees/Takeoffs Only: in 1-line displays the drop symbol is used only for tees and takeoffs (in 1-line displays without object contours it picks the tee/takeoff symbol for drop conditions).

Scaling ([G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23)):
- On insert the block is first scaled so its extents equal 1 unit (1 in or 1 mm), then rescaled by the option below.
- Neither box ticked: 2-line symbols scale to the actual diameter of the segment or fitting; 1-line symbols to the nominal diameter.
- Use Annotation Scale: annotation plot size (Drawing Setup > Scale tab) x current annotation scale. The style setting decides, not the block's Annotative property.
- Override Scale: X, Y, Z factors. Both ticked: your factors first, then the annotation scale.
- Center Line Block Scale Factor: relative to the symbol block (1 = same size, 1.5 = 50% larger).

### Rise/drop blocks ([G:70D697C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-70D697C7-DA1C-4FEE-B101-85FC9792544C))
- The style and its blocks must exist in the current drawing. Keep them in your templates, or build them in a content library DWG and copy them into templates.
- Rise block: set current color, linetype and lineweight to ByBlock before drawing it. On insert it takes the Rise Drop component's values.
- Drop block: draw with the real color, linetype and lineweight wanted. The Rise Drop component's values for these are ignored.
- Visibility of both is still controlled by the Rise Drop component.
- Any size; base point = center of the symbol. Draw oval blocks as flat ovals.
- Shipped 2-line blocks carry extra geometry on nested, non-plotting, frozen layers so their extents can be measured. Copy that approach.
- Content packs ship a style drawing with many system definitions, several rise/drop styles and their blocks; some are already in the templates. A new style's default symbols use these blocks.

## 7.7 Cut plane and display by elevation

### How MEP uses the cut plane ([G:17BF13BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17BF13BF-C73F-403F-B695-47766CFB78D7))
- In plan view MEP uses the cut plane of the CURRENT display configuration. The object's elevation picks which component draws it: Below, Low, High or Above.
- A sloped pipe uses its start point elevation.
- MEP objects use the global cut plane and display range differently from ACA objects.
- The cut plane is stored per display configuration ([KB:000331038](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Doors-and-windows-do-not-cut-openings-when-inserted-into-walls-in-AutoCAD-Architecture.html)).

### [GUI] Set it ([G:17BF13BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17BF13BF-C73F-403F-B695-47766CFB78D7))
1. Options dialog: tick "Enable Display by Elevation". (The tab is not named; [G:F9A8BE6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F9A8BE6B-BEF9-4754-B62C-C35A877B5798) links display by elevation to the MEP Display Control tab, inference.)
2. Current configuration: click the Cut Plane value on the status bar. Any configuration: Display Manager > pick a configuration that uses a Plan rep in Top view (or 1 Line, Duct domain only) > Cut Plane tab.
3. Cut Height: height where objects are cut for the plan rep.
4. Display Above Range: top of the floor plan range.
5. Display Below Range: bottom of the range.
- Above and Below ranges are ABSOLUTE heights from the WCS origin, not offsets from Cut Height. Display Above Range must be greater than Cut Height. Bad values give wrong results.
- Calculate button: only when a project is selected in Project Navigator and the drawing is multi-story; sets the cut height for a level.

### Which component draws the object ([G:17BF13BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17BF13BF-C73F-403F-B695-47766CFB78D7))
- Above Display Above Range: Above components (1-line: Single Line - Above; plan: Contour - Above, Insulation - Above, Rise Drop - Above).
- At or below Display Above Range, above Cut Height: High components.
- At or below Cut Height, above Display Below Range: Low components.
- At or below Display Below Range: Below components.
- KB:ts-5ibXLTjd says items above or below the display range are not visible when display by elevation is on. (inference: the Above and Below components are probably off by default; check their visibility.)

### Elevation-based display components ([G:CFD43F8A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFD43F8A-BCA7-46DF-98FF-1DC941C84F97))
- Components: Contour, Connector, Center Line, Hatch, Insulation, Lining, Rise Drop, Annotation.
- Objects: duct, flex duct, duct fitting, custom duct fitting, pipe, flex pipe, pipe fitting, custom pipe fitting, MvParts, cable tray and conduit with fittings.
- They work only when ALL are true: Display by Elevation enabled; current view is Top; current configuration uses 1-Line or Plan reps.
- Only Duct domain objects have 1 Line elevation-based components.
- A 2D section or elevation made with a set that uses 1-Line or Plan reps also shows them.
- Uses: one linetype below the slab, another above it; hide objects outside the range. Example: cut 2500 mm, above range 3500 mm, below range 0: a duct at -1000 mm is hidden.
- Set them in Style Manager, Display Manager, or per object on the Display tab (which shows the component matching that object's elevation).
- Stored in the drawing: enable and set them in the template. In a project, copy the display settings into every construct, view and sheet template.

### Workflow ([G:00BD3DF7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-00BD3DF7-2EFA-47BF-A61B-37B43D331F4D))
1. Enable Display by Elevation.
2. For each configuration using 1-Line or Plan reps in Top, enter Cut Height and the two ranges.
3. In the 1-Line and Plan reps, set component properties (linetype, color, visibility) per elevation range.
4. Add exceptions with cut plane overrides ("To Override the Cut Plane", not in these sources).
- Show only piping below Z = 0: enable display by elevation, then adjust the Cut Plane tab values ([KB:000638566](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-display-only-piping-that-is-below-the-0-level-on-the-z-axis-in-AutoCAD-MEP.html)).
- Cut plane changes are not versioned and are not overwritten by project standards sync ([G:C13693FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C13693FD-4D28-4929-88E7-C5CB59176411), [G:22719521](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22719521-E959-4DDC-8DEF-19175A2E5D17)).

### Cut plane problems on architectural xrefs (ACA objects)
- Door or window opening missing in plan: the global cut plane does not intersect the opening, or the wall style overrides the cut plane lower ("Override Display Configuration Cut Plane", style Display Properties > Edit Display Properties > Cut Plane tab) ([KB:000331038](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Doors-and-windows-do-not-cut-openings-when-inserted-into-walls-in-AutoCAD-Architecture.html)).
- Stair shows only a bounding box: stair elevation above the cut plane ([KB:000298890](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Stairs-do-not-display-correctly-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- Wall hatch missing in every configuration: wall Base height below the cut plane ([KB:000460331](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-Walls-are-missing-hatch-under-all-display-configurations-in-AutoCAD-Architecture-or-MEP.html)).

## 7.8 3D, isometric views, elevations and 2D sections

### 3D and isometric views
- The Model rep is full 3D wireframe ([G:F0E60B59](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F0E60B59-F7E4-49EC-8C99-7A26100ECEF4)). In the shipped MEP configurations every direction except Top uses the Model set ([G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0)).
- All four isometric views use the set mapped to Default ([G:D3805A7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D3805A7C-58D9-4443-9A32-A30D8270C133)).
- MvParts or other 3D elements missing in iso or other views: their visibility is off in one or more configurations. Display Manager > Representations by Object > the object type > tick the boxes under every rep it needs ([KB:000367434](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/3D-objects-are-not-displayed-in-some-views-in-AutoCAD-MEP-or-Architecture.html)).
- Electrical devices that stay 2D in 3D have no 3D rep in their style. Most, not all, shipped devices have one ([KB:000464059](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Electrical-devices-do-not-display-as-3D-in-AutoCAD-MEP.html)).
- Viewport cut with 3DCLIP top and bottom planes shows empty or partial: its configuration draws a 2D plan projection in Top, not the 3D model. Give the viewport a configuration whose Top direction uses a set with the objects' Model reps checked ([KB:000439389](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/3D-objects-are-not-displayed-when-using-viewports-and-3DCLIP-to-determine-top-and-bottom-cuts-in-AutoCAD-MEP.html)). (inference: for pipe and duct, check their Model reps in that set.)
- XCLIP with an elevation clips AEC objects in every view except Top, because the Top set draws 2D components at elevation 0. Workaround: duplicate the current configuration, map the Default direction's set to Top in the copy, and make the copy current for that viewport or model space ([KB:000468738](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/XCLIP-of-references-does-not-work-for-Top-view-in-AutoCAD-Architecture-MEP.html)).
- Cable tray rotation display needs the Cable Tray Model rep for both trays and fittings in the current configuration ([G:AA3BE944](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA3BE944-869C-486F-B3B0-4311AEF49EB8)).

### Visual styles and shading
- Hidden and Conceptual visual styles take only the object color from AEC/MEP settings and draw their own edges, ignoring Display Manager line settings. Thick prints from a Hidden viewport: VISUALSTYLES > select the style > Silhouette Edges > Width = 1 [GUI] ([KB:000503332](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-MEP-objects-are-printed-very-thick-when-the-visual-style-Hidden-is-applied-in-AutoCAD-based-products.html)).
- 2027: with FASTSHADEDMODE on, Realistic can render wrong. [AUTO] FASTSHADEDMODE 0 before switching to Realistic ([KB:000639112](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-and-MEP-Feature-Incorrect-Rendering-Of-3D-Model-When-Switching-To-Realistic-Visual-Style.html)).
- FASTSHADEDMODE 0 also fixed 3D solids vanishing or going dark in Shaded (Fast) and a blank 3DCLIP "Adjust Clipping Plane" viewer ([KB:000498570](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Structural-members-disappear-or-do-not-display-correctly-with-shaded-fast-visual-styles-in-Advance-Steel.html) lists 2023 and 2024, [KB:000564100](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/3DCLIP-viewer-blank-in-AutoCAD-2025.html) lists 2025). "(fast)" appears in style names only while FASTSHADEDMODE is on ([KB:000564100](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/3DCLIP-viewer-blank-in-AutoCAD-2025.html)).
- Fast visual styles need DirectX 12 feature level 12_0 ([KB:000643510](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/System-requirements-for-AutoCAD-2027-including-Specialized-Toolsets.html)).
- Render materials: AEC objects get render materials through a Material Definition in Style Manager (its display properties name the render material, which must already be saved in the drawing); the AEC style's Materials tab then maps components to that definition. Dragging from the Materials Browser does not work for them ([KB:000484390](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Material-dragged-onto-a-3D-element-will-not-display-or-render-in-AutoCAD-Architecture-MEP.html), [KB:000595012](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Animation-Motion-Path-are-rendered-grey-instead-of-visual-style-colors-in-AutoCAD-Architecture-or-MEP.html)).

### What exporters use
- 3D DWF/DWFx uses the configuration active at publish time and only its 3D set (usually a Model set). Objects with no rep in that set do not publish; tags, annotation and 2D plan symbols are usually missing. Publish 2D, or turn those reps on in the Model set ([G:A69262BA](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A69262BA-2882-49DE-9AB7-A1C1B881A7D5)).
- IFC export: the current display configuration defines geometry. Objects export only if their reps are active in it; objects that display there export even if their layers are off or frozen ([G:540EF8FE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-540EF8FE-733F-4A81-A03D-BFB6F5428763), [G:4E70F535](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-4E70F535-6258-49D8-BCBA-041CBE6C0134)).
- Navisworks uses the Standard configuration, not the current one. If the model looks sectioned, set the Standard configuration's cut plane and display range ([KB:000227693](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-model-is-displayed-sectioned-in-Navisworks.html)).

### Elevations and 2D Section/Elevation objects
- A 2D Section/Elevation is a snapshot generated through a display set. It is not live ([KB:000567269](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Layer-viewport-freeze-of-2D-sections-elevations-in-AutoCAD-Architecture-or-MEP.html)).
- [GUI] Colors wrong (often all one color): in the 2D Section/Elevation style's Design Rules tab, turn on the option that keeps layer, color and linetype from the display set used to generate it, then Refresh existing sections; new sections pick it up directly ([KB:000517324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/2D-Section-Elevation-colors-are-different-from-the-model-data-in-AutoCAD-Architecture-MEP.html)).
- Blank or missing parts: a plan-type set has no 3D data to cut. Regenerate the section with a display set that has 3D reps, such as `Section_Elev` ([KB:000318759](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Section-Elevation-views-missing-some-components-in-AutoCAD-MEP.html)).
- Nothing appears after the progress bar: the set for Top in the current configuration has no rep ticked on the "2D Section/Elevation" row. Tick one in that set's Display Representation Control tab. Or use the "Details"/"Dialog" command-line option during creation instead of clicking a point ([KB:000396273](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/2D-Section-Elevation-not-displayed-after-creation-in-AutoCAD-Architecture-MEP.html)).
- How a pipe looks inside a section: the Regenerate dialog shows which display set generated the section. In Display Manager edit the pipe rep that set uses (for example make Center Line visible), repeat for other object types, then regenerate the section ([KB:000525825](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/To-change-the-Layer-Color-Linetype-of-AEC-MEP-objects-inside-2D-Section-Elevation-in-AutoCAD-Architecture-or-MEP.html); the regenerate step is inference).
- How the section linework itself looks: the 2D Section/Elevation style's own rep in Display Manager > Representations by Object > 2D Section/Elevation. "Unknown Component" covers anything unassigned. "By Material" uses the sectioned objects' material display; Hidden and Erased cannot be By Material ([KB:000525825](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/To-change-the-Layer-Color-Linetype-of-AEC-MEP-objects-inside-2D-Section-Elevation-in-AutoCAD-Architecture-or-MEP.html)).
- Components with a shared material go missing: use different materials, or clear "Merge Common Materials" (Material Definition > Display Properties > Edit Display Properties > Other tab), then Refresh ([KB:000446541](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/2D-Section-Elevation-missing-components-with-material-style-in-AutoCAD-Architecture-MEP.html)).
- VP freeze leaves gaps or misses sub-components: sub-components can be on other layers. For clean linework, freeze the layers globally in model space, then Refresh the section ([KB:000567269](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Layer-viewport-freeze-of-2D-sections-elevations-in-AutoCAD-Architecture-or-MEP.html)).
- [AUTO] `2DSECTIONRESULTEDIT` (delete or modify linework) and `2DSECTIONRESULTMERGE` (add linework). Linework that represents AEC objects cannot be stretched or moved. Regenerating resets those edits and needs the 3D model present ([KB:000367898](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-add-remove-or-modify-elements-in-a-2D-Section-in-AutoCAD-Architecture.html)).
- Hidden lines wrong when the model is an xref (2017 to 2019): bind the xrefs, EXPLODE once, then generate ([KB:000340938](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-calculation-of-Generate-2D-section-shows-wrong-result-when-used-with-XREF-in-AutoCAD-Architecture-MEP.html)).
- Live section that cuts both AEC objects and AutoCAD solids (2013 to 2016 article): pair a Building Section line with live section on and a `SECTIONPLANE` drawn through the same two points, also set live ([KB:000276650](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-a-live-section-that-cuts-both-Solids-and-AEC-Objects-in-AutoCAD-MEP.html)).

### Live section settings on a display set [GUI] ([G:E97BD768](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E97BD768-DD6E-4DF1-A40F-C3B19F4EC6E7))
- Display Manager > Sets > the set > Display Options tab > Live Sections and Materials group.
- "Section AEC Objects by Display Range defined in Display Configuration" with sub-option "Show Materials where Display Range Intersects AEC Objects".
- "Hide Sectioned Body Component"; "Hide Surface Hatching".
- DANGER (page): clear this for PLAN sets or 2D sections inserted in Plan view will not display. The text is ambiguous about which box; clear both on Plan sets (inference).
- Live Section settings are not versioned and not overwritten by project sync ([G:C13693FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C13693FD-4D28-4929-88E7-C5CB59176411), [G:22719521](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22719521-E959-4DDC-8DEF-19175A2E5D17)).

## 7.9 Display Manager tasks [GUI]

### Open and read it
- `DISPLAYMANAGER`, or Manage tab > Style & Display panel > Display Manager ([KB:000447005](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Referenced-walls-are-not-displayed-in-a-2D-Section-in-AutoCAD-Architecture-MEP.html), [G:D83B5778](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D83B5778-A87B-441E-8D5D-8F1EBE9172C1)).
- Left pane: Configurations, Sets, Representations by Object. The current configuration is bold; the active set is highlighted ([G:BA31AA3B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA31AA3B-5E14-410B-9AD8-661A9E4D47A8), KB:ts-5ibXLTjd).
- Click the "Representations by Object" title: a table of the active reps per object type, with reps down the side and sets across the top; the highlighted column is the active set. Double-click an active icon to edit its layer properties ([KB:000525825](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/To-change-the-Layer-Color-Linetype-of-AEC-MEP-objects-inside-2D-Section-Elevation-in-AutoCAD-Architecture-or-MEP.html), KB:ts-5ibXLTjd).
- Representations by Object > object > rep: the right pane shows DEFAULT properties only. Style and object overrides are not shown there ([G:E77202DC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E77202DC-722B-45F4-90ED-CFE78AE82645)).
- Rep tabs: Layer/Color/Linetype (AutoCAD properties, component visibility, "By Material" control); Hatching, Other, Cut Plane and similar for object-specific items. Which tabs appear depends on object and rep ([G:A54D85B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A54D85B9-DA09-4EA2-8E2D-67F05E372633)).

### Create and wire up ([G:D001D9C0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D001D9C0-08F0-401F-AA80-740E3A178332), [G:1AD51BA0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1AD51BA0-FC97-4BC7-969E-90729A933801), [G:131C201B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-131C201B-5AA2-4D98-BB1E-A43DC0138B7F), [G:547A986E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-547A986E-B800-4B21-806A-9DB098F022C8), [G:D3805A7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D3805A7C-58D9-4443-9A32-A30D8270C133), [G:840AF8C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-840AF8C9-0CB1-450B-A592-2294CA3797C6))
1. Rep: Representations by Object > object > right-click an existing rep > Duplicate > name > Enter. Double-click to edit. Pick a source rep close to what you want. The new rep shows in the left tree only after Display Manager is closed and reopened.
2. Set: click Sets > New (empty, no reps) or select a set > New (copy) > name > Enter. Display Representation Control tab: tick reps per object. Right-click a rep name > Select All; right-click an object > Clear All (removes it from the set); right-click the Objects heading > Select All / Clear All Display Representations.
3. Configuration: click Configurations > New (empty, no sets) or select one > New (copy) > name > Enter. Configuration tab: under Display Representation Set pick a set for each view direction and for Default.
4. Assign the configuration: select the viewport, then the Display Configuration control in the drawing status area; or right-click the configuration > Set To Current Viewport.
5. Regenerate: [AUTO] REA.
- Start from a shipped configuration rather than from scratch ([G:3BA802C3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3BA802C3-BBA9-4687-BCAF-37ADBBB81590)).
- Compare Sets: Ctrl+click exactly two sets > right-click > Compare Sets; arrow buttons copy reps across ([G:EB161B10](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EB161B10-B153-4D05-9253-EB578F3622F9)).
- Standard Sets Adjustment: right-click Sets > choose which set acts as each standard set type ([G:46091C7C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-46091C7C-6385-47E1-ACDA-01F4CB291F28)).

### Drawing default configuration ([G:F2B1D798](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2B1D798-9D12-4A32-81CC-34CCD134072E))
- Utilities > Drawing Setup > Display tab > Drawing Default Display Configuration. Used by NEW viewports and by model space when TILEMODE = 1.
- Or right-click a configuration > Set as Drawing Default.
- Existing viewports with a configuration already assigned do not change.

### Copy display settings to another drawing ([G:3A05B84D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3A05B84D-97CA-432D-8E16-660102A5C004), [G:0D52332C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0D52332C-C354-412C-8590-DC093221CB59))
- In Display Manager use File Open (existing drawing) or File New to list the target drawing.
- Right-click one item > Copy, or right-click the whole Configurations, Sets or Representations folder > Copy. Right-click the target drawing > Paste. Drag and drop also works.
- Same name in the target opens "Import/Export - Duplicate Names Found": Leave Existing, Overwrite Existing, Rename to Unique (appends a number).
- Copying a configuration brings only the sets and reps missing in the target. Same-name sets or reps already there are NOT overwritten; rename the target item first to bring new data ([G:0D52332C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0D52332C-C354-412C-8590-DC093221CB59)).
- Fix a drawing that lacks configurations (built from a non-AEC template): open Display Manager once so the Standard configuration is created, or drag the three entries Configurations, Sets and Representations by Object from a drawing started on an AEC Model or Aecb Model template ([KB:000447005](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Referenced-walls-are-not-displayed-in-a-2D-Section-in-AutoCAD-Architecture-MEP.html)).
- Send: right-click the drawing > Send writes all display settings into a new drawing and attaches it to an email. Needs an email client ([G:5AB2D102](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5AB2D102-E2C5-40B1-AD3B-812F700376DB)).

### Limits on delete, purge, rename ([G:B4BA6DEB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B4BA6DEB-897D-4550-8DD4-D0A1B5DF71F7), [G:7A65B198](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7A65B198-2566-431F-A76C-B1838D2A34D2), [G:DF28622C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DF28622C-2FCC-4441-ADB8-0AF843216710), [G:F12E76F0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F12E76F0-6C09-4FA0-92CA-858F3A33EB5E), [G:63509D14](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-63509D14-23F1-41D6-A4BB-8A5A3D048282), [G:B45BC417](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B45BC417-B542-4941-A2D0-3B5F2135F691), [G:19872330](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-19872330-87B3-431A-A711-77F424868D68))
- Configuration: cannot delete the one on the current viewport, a predefined one (red check mark) or Standard. Cannot purge one assigned to a viewport or model space. Standard cannot be renamed.
- Set: cannot delete or purge one used by a configuration; predefined sets (Standard, Model, Plan) cannot be purged. Tip: click Configurations to see which sets are in use.
- Rep: delete only user-defined reps assigned to no set (right-click > Clear All first). Predefined reps (Model, General) cannot be purged, deleted or renamed.
- Deleting a configuration keeps its sets and reps; deleting a set keeps its reps.
- Purge buttons open Purge Display Configurations / Sets / Representations dialogs with everything purgeable pre-ticked.

### Other settings
- Notes and reference files on a configuration or set: General tab > Notes ([G:D8AB2577](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D8AB2577-FD01-4C6B-994C-B7275DC90AD5)).
- Classification Filter and Live Sections: set > Display Options tab ([G:EC377F07](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EC377F07-7AAC-4791-955F-01C163762562), [G:E97BD768](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E97BD768-DD6E-4DF1-A40F-C3B19F4EC6E7)).
- Project standards items: right-click > Synchronize with Project Standards, Update Standards from Drawing, Ignore During Synchronization (see 7.17).

## 7.10 Xrefs and display

### Which configuration an xref uses
- Default: objects in attached and overlaid xrefs use the HOST drawing's configurations ([G:5C7165F8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5C7165F8-B78F-41F7-9021-BED2172E8E44)).
- Override one xref [GUI]: select the xref > Properties palette Display tab > Edit Object Display (or right-click > Edit Object Display) > Xref Display tab > tick "Override the display configuration set in the host drawing" > pick one of the xref drawing's configurations. "Drawing Default" (ACA page) or "Domain Drawing Default" (MEP page) = the host's default configuration. Then Regenerate Drawing And Viewports or REA ([G:332E0EC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-332E0EC6-2AFC-4A48-99E3-DDC40BA524CC), [G:78166D6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78166D6B-1CDD-46E5-A1D1-1319E124E280)).
- [AUTO] Same by command line: `SETXREFCONFIG` > select the xref > `Y` > F2 to list the xref's configurations > type the number ([KB:000314102](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-display-configuration-of-an-Architecture-or-MEP-drawing-in-AutoCAD.html)).
- If the xref drawing has "When used as an Xref Overlay, use this drawing's default display configuration initially" ticked (its Utilities > Drawing Setup > Display tab), the Xref Display settings are greyed in the host and cannot be changed for that overlay ([G:5C7165F8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5C7165F8-B78F-41F7-9021-BED2172E8E44), [G:332E0EC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-332E0EC6-2AFC-4A48-99E3-DDC40BA524CC)). One page says "initially", the other "always".

### Editing styles and display through an xref
- Display settings and object styles cannot be changed while refediting an xref from the host. Display Manager and Style Manager let you edit, but nothing is saved. Open the xref drawing, change it, save, reload the xref ([G:8512B736](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8512B736-FC8A-4559-BFF5-7F097517A1C2), [G:BBEF10AC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BBEF10AC-3C40-4AEA-97C5-957DDA128E48)).

### Xref display problems
- Xref shows only boxes: its AEC/MEP objects are proxies. OPTIONS > Open and Save > ObjectARX Applications: "Demand load ObjectARX apps" = "Object detect and command invoke"; "Proxy images for custom objects" = "Show proxy graphics"; reopen. Preset these before a scripted open so the proxy dialog does not block it ([KB:000599534](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Content-of-some-XRefs-appear-only-as-bounding-boxes-in-AutoCAD-products.html); script point is inference).
- Objects in an xref missing though their layer is on: layer 0 is off or frozen (blocks and AEC objects keep internal geometry on layer 0), or the layer state is corrupt. Thaw and turn on layer 0 and all xref layers ([KB:000323063](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Objects-in-Xref-or-in-a-drawing-do-not-display-at-all-or-incorrectly-in-AutoCAD.html)).
- 2018/2019 only: AEC components set ByLayer took the color of the layer the xref sits on. Fixed in later updates ([KB:000304566](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-objects-set-to-display-BYLAYER-are-the-wrong-color-in-Xref-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- An overlaid xref is not shown when its host is itself referenced into another drawing ([G:45203A5A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45203A5A-EB2C-40CF-A685-65B8CAC73F07)).
- Xref layer property overrides lost on reopen: set VISRETAIN = 1 in the host; keep xref geometry off layer 0; test XREFOVERRIDE; in ACA/MEP project sheets set Project Properties > Drawing Settings > "Match Sheet View Layers to View" = No ([KB:000257034](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Xref-layers-reset-upon-reopening-drawing.html)).
- Pipes vanish or sink behind xrefs that came from non-Autodesk DWG writers: repair with RECOVERALL or paste into a clean native-template drawing (COPYBASE / PASTEORIG keep position) ([KB:000592774](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Pipes-and-MEP-objects-drawn-behind-XRefs-in-AutoCAD-MEP-or-Architecture.html)).
- Some MEP objects draw wrong in one configuration though Display Manager is right: the object's display definition is corrupt. Start a drawing from an MEP template, check a catalog part there, then bring the bad content in by copy or INSERT with Explode ticked ([KB:000361712](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Certain-MEP-objects-are-not-displaying-correctly-in-AutoCAD-Architecture-or-MEP.html)).

## 7.11 Style Manager and Styles Browser

### What a style is
- A style is a set of parameters that fixes how objects look and work. Every object is an instance of one style; editing the style changes ALL its instances in the drawing ([G:BBEF10AC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BBEF10AC-3C40-4AEA-97C5-957DDA128E48)).
- The tool that creates an object normally applies its style. Afterwards you can apply another style or edit the style ([G:BBEF10AC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BBEF10AC-3C40-4AEA-97C5-957DDA128E48)).
- Using a tool palette tool ADDS that tool's style to the drawing automatically ([G:BBEF10AC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BBEF10AC-3C40-4AEA-97C5-957DDA128E48)).
- MEP style-type objects include system definitions, rise/drop styles, connector styles, device, panel, wire, plumbing fitting, plumbing line, schematic symbol and schematic line styles, hanger styles ([G:8C1E9519](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C1E9519-DFA8-4EFA-9603-E8674E52C638), [G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23), [G:55201F4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-55201F4D-BDB3-4870-A35A-A7381224EB5D), [G:160FDE57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-160FDE57-8802-4AB7-ACD6-4C6D73BA873B), [G:C98DAE80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C98DAE80-7EDF-4D4C-ABE0-3437BC6EE6F8)).

### Style Manager [GUI]
- Open: `STYLEMANAGER` ([KB:000517324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/2D-Section-Elevation-colors-are-different-from-the-model-data-in-AutoCAD-Architecture-MEP.html)), Manage tab > Style & Display panel > Style Manager, or right-click a style-based tool on a palette > "<object type> Styles" ([G:AD74394E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD74394E-6979-4A3B-B89F-ABD6B6546224)).
- The Style Manager drop-down jumps straight to a style type by workspace: Electrical Device Styles, Electrical Panel Styles, Wire Styles (Electrical); Plumbing Fitting Styles, Plumbing Line Styles (Plumbing); Schematic Symbol Styles, Schematic Line Styles (Schematic) ([G:160FDE57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-160FDE57-8802-4AB7-ACD6-4C6D73BA873B), [G:732C683D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-732C683D-7C41-483F-81F4-250879003F9D)).
- Tree: every drawing and template open in the session. ACA pages name three categories: Architectural Objects, Documentation Objects, Multi-Purpose Objects ([G:AD74394E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD74394E-6979-4A3B-B89F-ABD6B6546224)). MEP pages name object folders such as HVAC Objects, Piping Objects, Plumbing Objects, Electrical Objects ([G:8C1E9519](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8C1E9519-DFA8-4EFA-9603-E8674E52C638), [G:0BE3EF4B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BE3EF4B-B1D0-49F9-957D-983A2124AD23), [G:BE30E9DD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE30E9DD-FB27-481A-A27E-50F79BE351A0), [G:1A1DBC84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1A1DBC84-1338-4488-8607-B49603D3B030)). For conduit, cable tray and custom duct or pipe fittings, click + on the domain type to reach the sub-domain styles ([G:160FDE57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-160FDE57-8802-4AB7-ACD6-4C6D73BA873B)).
- Multi-Purpose Objects holds Layer Key Styles, Connector Styles, Hanger Styles, Material Definitions and Classification Definitions ([G:FA684C28](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA684C28-B27F-4041-922F-A14A3933A564), [G:55201F4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-55201F4D-BDB3-4870-A35A-A7381224EB5D), [G:C98DAE80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C98DAE80-7EDF-4D4C-ABE0-3437BC6EE6F8), [KB:000484390](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Material-dragged-onto-a-3D-element-will-not-display-or-render-in-AutoCAD-Architecture-MEP.html), [KB:000538630](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Delay-when-multiple-objects-are-selected-in-AutoCAD-Architecture-or-MEP.html)).
- Sort by drawing (default) or by style type: View menu > Explore By Style, or the toolbar button. Status bar shows sort, drawing, type and style. A filter button shows one style type ([G:781DA7B9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-781DA7B9-3D1D-4356-9180-200470B3D434), [G:AD74394E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD74394E-6979-4A3B-B89F-ABD6B6546224)).
- Lock icon (read-only) when the file is read-only, from an older release, xref'd into an open drawing, open in another application, or locked on the network. Hover the status bar lock for the reason ([G:C8D542C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8D542C2-D2EE-41BD-AD85-3C0F6713DBF1)).
- Files opened, created (File > New Drawing, .dwg or .dwt) or dragged in from File Explorer inside Style Manager are open ONLY there. Leave Style Manager before opening them in the session. Close them with File > Close; a drawing open in the session cannot be closed from Style Manager ([G:C8D542C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8D542C2-D2EE-41BD-AD85-3C0F6713DBF1), [G:DA559DE6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-DA559DE6-4AD5-4F20-B4C6-5666CCEDE826), [G:7011E8B2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7011E8B2-6255-4D11-990E-E279D41B26A5), [G:E3BAD018](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E3BAD018-789C-475B-8862-DF5B82AD0445), [G:3DE3F132](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3DE3F132-F4F7-4029-90B8-9A5A1BFAB904)).
- Tip: keep styles in a read-only source drawing and copy them out as needed ([G:C8D542C2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C8D542C2-D2EE-41BD-AD85-3C0F6713DBF1)).

### Style Manager tasks [GUI]
- New style: right-click the style type > New. Copy: right-click a style > Copy, right-click the type > Paste, then Rename. Set name and description on the General tab ([G:50FCBF83](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-50FCBF83-22B2-4D91-9FC5-80533000A20F), [G:160FDE57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-160FDE57-8802-4AB7-ACD6-4C6D73BA873B)).
- New and renamed styles are NOT saved until the drawing is saved ([G:50FCBF83](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-50FCBF83-22B2-4D91-9FC5-80533000A20F), [G:C2F6775D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C2F6775D-A2CE-4A3F-B0EA-EE8A02765087)).
- Style from an object: select it > contextual tab > General panel > Copy Style. The copy is assigned to that object only ([G:E641D9AE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E641D9AE-4BAD-4AA5-A975-2EA5D8EABD19)).
- Edit an object's style: select it > contextual tab > General panel > Edit Style (some objects show an Edit System Style drop-down), or right-click > Edit Style ([G:22761EDA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-22761EDA-9270-4716-B11C-67B2D5B4466F), [G:6324961B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6324961B-138E-480D-BF9A-E2CDF742525B)).
- Purge: right-click a style or a style type > Purge, or press Delete. Removes only styles not used by any object or other style. Sub-definitions used by a purged style stay ([G:59B4853A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-59B4853A-D6B1-4116-8BD0-2D7327A9F62A)).
- Tool from a style: drag it from Style Manager onto a tool palette. The tool keeps a reference to the style's drawing. If that is another drawing, the style is copied in only when an object is added, and only if the current drawing has been saved ([G:42F73EB5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-42F73EB5-578B-46FC-95E4-C147DA6AB90C)).
- Send: right-click a style, type or drawing > Send emails a drawing holding just those styles. Needs an email client ([G:AD2551DB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AD2551DB-EB97-4454-9631-4F632946BF14)).
- Notes and reference files: General tab > Notes ([G:22761EDA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-22761EDA-9270-4716-B11C-67B2D5B4466F)).
- Connector Styles (Cable Tray, Conduit, Electric, HVAC, Pipe, Schematic) decide when connections are allowed. Keep the defaults; changes can make the software work wrongly. Check rules: Multi-Purpose Objects > Connector Styles > style > Rules tab ([G:55201F4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-55201F4D-BDB3-4870-A35A-A7381224EB5D), [G:ACBA8796](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ACBA8796-0F54-4B9E-A59B-DEB547A66D69)).

### Styles Browser [GUI] ([G:F8A1FAD4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8A1FAD4-FEF0-4848-8D91-D0C9DF74CED5), [G:BA5E6771](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA5E6771-DB18-43B5-A1A2-FDE8329852BC), [G:2787AFC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2787AFC6-50C8-4728-B654-40EC6E3B5D79))
- Open: `STYLESBROWSER` [AUTO], or Home tab > Tools drop-down > Styles Browser. Everything after that is palette mouse work.
- Object Type: every object type that has styles. The ACA list has no pipe, duct or fitting types. MEP pages use it with Object Type = Device, Panel and Electrical System Definitions ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD)).
- Drawing Source: Currently Open Drawings, Content Library Drawings, or a Project Standards drawing (needs an active project).
- Drawing File: All Drawings, Current Drawing, All Without Current Drawing, System Definitions, Manage Content Library.
- Search Style filters by name. Gallery shows matches; system definitions show no preview, only the name.
- Double-click a style: starts that object's add command with the style. Right-click: Add Object or Import Styles.
- Object types cleared in the project's Configure Standards dialog do not appear.

### Content Drawings Library ([G:E3A06655](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E3A06655-E1DC-4D4E-9BC0-F7A31F7B06C4), [G:04FE166D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-04FE166D-B74E-4A83-ACCA-D4B86129622E))
- A list of drawing files holding ACA styles or MEP system definitions. Adding a file or a folder makes its styles or system definitions available to the current drawing.
- Reach it from Styles Browser > Drawing File > Manage Content Library, or Properties palette > Basic > General > Search > Browse.
- Add files or folders; Remove (does not delete the file); Restore (last saved list); "Save as default" saves the list.
- Where the list is stored is not stated.

## 7.12 Moving styles, system definitions and settings between drawings

- Styles and system definitions: in Style Manager drag the style from one drawing's tree onto the other drawing ([G:E53C7990](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E53C7990-6DA7-4591-A91F-9AF825911854)). This also copies all blocks tied to the style ([G:DC7A67B3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC7A67B3-E551-47C0-A960-349A743D66BA)).
- Copy/Paste in Style Manager works too; a same-name item raises "Import/Export - Duplicate Names Found" (shown for property set definitions on [G:46F8C145](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-46F8C145-4E1F-454E-A789-8AFEBD837768)).
- Styles Browser > Import Styles copies a style from an open, content library or standards drawing ([G:F8A1FAD4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8A1FAD4-FEF0-4848-8D91-D0C9DF74CED5)).
- Palette tools pull their style in on use ([G:BBEF10AC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BBEF10AC-3C40-4AEA-97C5-957DDA128E48), [G:42F73EB5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-42F73EB5-578B-46FC-95E4-C147DA6AB90C)).
- Tools and palettes also travel through Content Browser tool catalogs. Copies dropped into the palette set stay linked to the catalog by default (Refresh from active in the tool's Properties); Stock Tool Catalog items always drop unlinked; Autodesk-supplied catalogs cannot be edited ([G:97DBF73D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-97DBF73D-9B60-47D3-B646-35B67B2FDF99), [G:17B6B359](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-17B6B359-1DE6-499D-8FE1-C63B2F2FFB93)).
- Content library drawings: change a style in the library drawing and it reaches every drawing whose Options content location points at that library. A Style Manager edit in a working drawing stays in that drawing only ([G:8AE18F38](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AE18F38-D993-40B5-A15C-50DE616CC6DA), [G:F28CE47C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F28CE47C-7E44-44F0-8A3E-9350855BE287)).
- Display configurations, sets, reps: Display Manager copy, paste or drag ([G:3A05B84D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3A05B84D-97CA-432D-8E16-660102A5C004)); see 7.9.
- Layer standards: Layer Properties Manager > Layer Standards > Import/Export ([G:E53C7990](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E53C7990-6DA7-4591-A91F-9AF825911854), [G:1DCBBB27](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1DCBBB27-A9DB-41D8-B3BD-D478F77FB28B)). Layer key styles: Style Manager.
- Layer states: export to LAS and import ([G:A12F4A88](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A12F4A88-9119-4BFA-BF1C-2DE02AE9507C), [G:9456C6C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9456C6C9-3D3B-4D49-8763-9D47D9620068)).
- Text styles, dimension styles, linetypes: Insert tab > Content panel > Design Center; double-click to add ([G:E53C7990](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E53C7990-6DA7-4591-A91F-9AF825911854)).
- Layouts: right-click a layout tab > From template ([G:E53C7990](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E53C7990-6DA7-4591-A91F-9AF825911854)).
- Projects: project standards sync (7.17).
- Routing preferences are not named in any source for this section. (inference: they are style-type objects in Style Manager under Piping Objects and should move the same way; verify in the piping sections, including whether the part sizes they reference come along.)
- Changes to a key style, style or system definition apply only to the open drawing. Make the same change in the template for future drawings ([KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html), [G:E53C7990](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E53C7990-6DA7-4591-A91F-9AF825911854)).
- No command-line or API route for copying styles appears in these sources. For scripts, put everything in the template (inference).

## 7.13 Style-based content

### What it is
- Devices, panels, plumbing fittings, schematic symbols and MvParts are style-based content: MvBlocks with smart connectors that join into systems. An MvBlock looks different per view direction. A view is defined by assigning a pre-drawn block to a named view in the style ([G:DF3201A3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF3201A3-BC08-49CF-9228-23C3AF2D5999)).
- Hangers are style-based content too ([G:0C408474](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0C408474-E353-4FF6-AB4A-4C9BB1F42E67)).
- A style made in Style Manager lives only in the drawing where it was made. For reuse, build it in a library DWG that sits in (or under) a folder set as a style-based content location ([G:F28CE47C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F28CE47C-7E44-44F0-8A3E-9350855BE287), [G:8AE18F38](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AE18F38-D993-40B5-A15C-50DE616CC6DA)).
- Shipped, customizable libraries: `\ProgramData\Autodesk\MEP <version>\enu\MEPContent` (no drive letter on the page). Copy originals before customizing ([G:F28CE47C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F28CE47C-7E44-44F0-8A3E-9350855BE287)).
- Name library files to show what they hold, for example "Project ABC Ortho Iso.dwg" ([G:F28CE47C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F28CE47C-7E44-44F0-8A3E-9350855BE287)).

### Workflow ([G:8D6A3E16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D6A3E16-A0D5-4002-8B68-80DBDBD9C110))
1. Create or open the content library DWG.
2. Draw at least one AutoCAD block for a style view (needed for schematic symbol, device, panel, plumbing fitting styles).
3. Create the style in Style Manager and assign blocks to its views. Batch tools exist for many device or symbol styles at once.
4. Add the content to categories.
5. Save and close the library drawing.

### Blocks for style views ([G:144EEB2E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-144EEB2E-2849-440E-B924-95A09F56FFEB))
- Draw with line, trace, hatch or solid. Do NOT use polylines.
- Build on layer 0; set color, linetype and lineweight individually to BYBLOCK; insertion point 0,0,0. Then inserted symbols follow the current layer standard.
- Give every block a unique name.
- 2D block = same in every view direction. MvBlock = different per view direction (for example isometric views).
- Counts: schematic symbol usually one 2D plan block (it can generate the 12 isometric view blocks). Other content needs 2D and 3D blocks for plan and model views. A plumbing fitting may need only a 2D plan block. A device needs a 2D plan block, plus an MvBlock for model, front, left and so on if sections and elevations must show true size.
- Block color will not follow the layer unless the block was made on Layer0; Vision Tools tab > Block Definition panel > To Layer 0 fixes it ([G:D56094F4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D56094F4-98FD-4962-8DB9-E818B1D0CBAB)).
- MV-Block color depends on its blocks' contents: set a color inside each block; or ByLayer contents with the inner layer colored; or ByBlock contents with the MV-Block's layer colored. Edit with `BEDIT` [AUTO] ([KB:000478290](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-color-of-Multi-View-Blocks-in-AutoCAD-Architecture-MEP.html)).

### Views tab (devices, panels, plumbing fittings) [GUI] ([G:9E96BA07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E96BA07-5248-4FEF-B547-515A45CBB2D4))
- Style Manager > select the style > Views tab > Add: View Name (for example Plan, Model), View Block (any block in the current drawing), Display Representation, View Directions (one or more).
- Matching rule: the software takes the active rep (from the active configuration) and the active view direction, then finds style views with the same pair. One match: its block is used. Several: all are used. NONE: the object is NOT displayed ([G:9E96BA07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E96BA07-5248-4FEF-B547-515A45CBB2D4), [G:CDFAEBCF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CDFAEBCF-FA70-423D-80AB-770721877184)).
- DANGER: removing a view with no replacement makes every object of that style vanish in that rep and direction.
- "Insert as annotation block" with Offset X/Y: the block draws with the object's Annotation display component (color, linetype, lineweight). Two views with the same rep and directions let one object show a symbol block plus an annotation block. "Keep text horizontal when rotating" works only with this option.
- Scaling: Use Annotation Scale = annotation plot size (Drawing Setup > Scale tab) x current annotation scale; the style setting, not the block's Annotative property, decides. Override Scale = X, Y, Z factors. Both: factors first, then annotation scale. Neither: no scaling. Plumbing fittings and schematic symbols always scale by the current annotation scale in model space ([G:9E96BA07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E96BA07-5248-4FEF-B547-515A45CBB2D4), [G:CDFAEBCF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CDFAEBCF-FA70-423D-80AB-770721877184)).
- Each MvPart builds a unique view block from the style name and view direction ([G:9E96BA07](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9E96BA07-5248-4FEF-B547-515A45CBB2D4)).
- Schematic symbols: Views tab > Generate Isometric Views: In-line symbol (follows the line direction) or Vertical symbol (stays vertical); pick the plan block; "Use new blocks in the style definition" overwrites existing view blocks. Advanced Editor edits views by hand ([G:CDFAEBCF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CDFAEBCF-FA70-423D-80AB-770721877184)).

### Other style tabs [GUI]
- Connectors tab: Description (for example Air_Supply), Domain, connection point X, Y, Z, or "Add Center Points from View Blocks in Top View"; add and remove buttons. DANGER: changes apply to every instance of the style and can break connectivity ([G:6324961B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6324961B-138E-480D-BF9A-E2CDF742525B), [G:1A1DBC84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1A1DBC84-1338-4488-8607-B49603D3B030)).
- Display Properties tab: select a rep > Style Override > edit components (visibility, layer, color). Clear Style Override to return to the drawing default. Style-specific settings: Edit Display Properties > Other tab ([G:6BF69459](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6BF69459-DB0A-43E8-B7BD-C8E17652E16D)).
- Design Rules tab (schematic symbols, devices, panels, plumbing fittings): line or wire cleanup None, Bounding Box, Inscribed Circle, Circumscribed Circle, Trace Geometry. Existing content updates automatically ([G:732C683D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-732C683D-7C41-483F-81F4-250879003F9D)).
- Device style Design Rules: Type (fixed built-in list; load totals group lighting, receptacles, other), Layer Key (from the drawing's layer standard and key style), Wire Cleanup ([G:57753CC7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-57753CC7-1D27-405C-AC58-BA35CE4DDFBC)).
- Device style Classifications tab: Device Type classification; keep it equal to the Type value. Display sets can show or hide devices by it ([G:A6203E1D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6203E1D-856F-41D7-941D-81663C6DEBA4)).
- Panel style Design Rules hold only wire cleanup. To move panels to another layer, remap layers ([G:8A1DF64B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8A1DF64B-004E-4554-980A-B8B70784EBC7)).
- Categories: Style Manager > object folder (for example Plumbing Objects) > right-click the category node (for example Plumbing Fitting Categories) > New > name > add styles on the right. Purge removes the category, not the styles ([G:BE30E9DD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE30E9DD-FB27-481A-A27E-50F79BE351A0)).

### Conversion tools (all dialogs) [GUI]
- `CONVERTTODEVICE`: Equipment tab > Modify panel > Convert To Device. Turns one block, MvBlock or MvPart (current drawing or xref) into a device and a device style. Device Convert - Behavior: Name, Type, Layer Key, "Delete the original object"; then electrical connectors; option "Convert all additional references to the selected block in the drawing" ([G:425BE254](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-425BE254-DB6B-43FE-B520-E8B9BEEA4590)).
- `CONVERTDEVICECONTENT` / `CONVERTSYMBOLCONTENT`: Manage tab > MEP Content panel > Batch Convert Devices / Batch Convert Symbols. Conversion Script File (CCF) + target DWG > Generate. One script makes one drawing of styles ([G:E382B42D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E382B42D-BEC3-4E4B-B6C3-081640251B4C), [G:5513128D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5513128D-A404-4109-AE13-993393D4EE57)).
- CCF = Custom Content File (style settings plus paths of the block drawings). CCT = Custom Content Template (default values used to build a CCF) ([G:E382B42D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E382B42D-BEC3-4E4B-B6C3-081640251B4C), [G:8ECFDECD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8ECFDECD-5DA3-4E5D-B90F-DFB922B01F50)).
- `DECOMPOSEDEVICECONTENT` / `DECOMPOSESYMBOLCONTENT`: Manage tab > MEP Content panel > Decompose Devices / Decompose Symbols. Writes one DWG per view block per style plus a CCF. Originals are not changed ([G:DEE81524](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DEE81524-F545-4CB4-AEE1-2D1149DC04B5), [G:7EB76F97](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EB76F97-61E3-4E50-9890-F0F80A56B90E)).
- GOTCHA: rerunning a batch conversion overwrites edits made in Style Manager. Edit the script, then rerun ([G:E382B42D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E382B42D-BEC3-4E4B-B6C3-081640251B4C), [G:5513128D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5513128D-A404-4109-AE13-993393D4EE57)).
- GOTCHA: decompose sets Connector Placement of ALL connectors to Specify. Fix each before reuse: Specify (X, Y, Z), Center, Insert, Node (one connector per AutoCAD point in the view block) ([G:DEE81524](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DEE81524-F545-4CB4-AEE1-2D1149DC04B5), [G:7EB76F97](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EB76F97-61E3-4E50-9890-F0F80A56B90E), [G:F641206E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F641206E-5B1B-4B5D-870C-BA34530390EA)).
- Edit Device Script / Edit Symbol Script: Category is not a Style Manager field; it groups content in the Select Device or Select Schematic Symbol worksheet and is created if missing ([G:F641206E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F641206E-5B1B-4B5D-870C-BA34530390EA), [G:BB7F5811](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BB7F5811-3620-4345-A3C4-224C307F1B2F)).

### Hanger styles ([G:C98DAE80](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C98DAE80-7EDF-4D4C-ABE0-3437BC6EE6F8), [G:217FD1C8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-217FD1C8-B503-48DC-9842-A4F960E5DDE3))
- A hanger style points to TWO structural member styles: one channel, one drop rod. Make them first: Architecture workspace > Manage tab > Style & Display panel > Structural Member Wizard.
- Naming rule: Channel Style lists member styles whose name or description contains both "hanger" and "channel"; Rod Style needs both "hanger" and "rod". Other names do not appear.
- Style Manager > Multi-Purpose Objects > Hanger Styles > Hangers tab: Channel Style, Rod Style, Rod Offset, Rod Overrun. If Hanger Styles is missing, run `HANGERADD` once.
- Hangers go on duct, pipe, cable tray and conduit segments, not on fittings. They move and delete with the host.

## 7.14 Layer standards, layer key styles and layer keying

### The core rule
- When an MEP or AEC object is added, it is drawn on the layer its layer key gives it in the CURRENT layer key style. This is "layer keying" ([G:CB5753AC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CB5753AC-5F31-42F0-9A11-3A8D74DCD699), [G:04A427DC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-04A427DC-85B3-4B90-AA84-6B0F5C017036)).
- The current layer does NOT decide where toolset objects go. Plain lines and polylines go on the current layer ([G:45D2635F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45D2635F-DBEB-4F03-AF88-C3A9A06FBEEA), KB:x-56PmvkbM). ([G:45D2635F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-45D2635F-DBEB-4F03-AF88-C3A9A06FBEEA) names only the Architecture toolset; the MEP pages say the same about layer keying.)
- Exception: Layer Key Overrides set to `<Current Layer>` sends new AEC objects to the current layer ([KB:000435576](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-AEC-objects-on-the-current-layer-instead-of-the-definition-from-Layer-Key-in-AutoCAD-Architecture-MEP.html); see 7.15).
- An MEP object takes its layer from the layer key tied to its system definition or style ([KB:000474189](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Assigning-MEP-object-sub-components-to-specific-layers-in-AutoCAD-MEP.html)). System definitions can override layer key settings for their object type ([KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html)). Device styles carry a Layer Key on the Design Rules tab ([G:57753CC7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-57753CC7-1D27-405C-AC58-BA35CE4DDFBC)).
- Every layer standard has a matching layer key style; a key style holds layer keys ([G:CB5753AC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CB5753AC-5F31-42F0-9A11-3A8D74DCD699)).
- A layer key maps an object type to a layer and sets that layer's default color, linetype, lineweight, plot style and plot setting ([G:FA684C28](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA684C28-B27F-4041-922F-A14A3933A564)).
- The toolset creates layers on demand under the current standard: adding the object creates its layers if missing ([G:D7350EC7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7350EC7-5626-4A22-B99F-AA5C1EE4E0C8)).

### Shipped standards and files
- MEP defaults include "MEP Object - Based on AIA" and "BS1192 - AUG Version 2". Example: under the MEP Object standard the duct layer is `M-Duct-Std` ([G:5B6BCE5E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5B6BCE5E-FE2B-4241-B4CD-8E131E4E0AEF)). [KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html) uses `M-HVAC-Duct` as its example. Real names depend on the key style in your template; read its Keys tab.
- ACA ships AIA 2nd Edition, BS1192 Descriptive, BS1192 - AUG Version 2, DIN 276, ISYBAU Long Format, ISYBAU Short Format, STLB ([G:08947990](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-08947990-83DE-48D9-9042-BAC426C65177)). AIA 2nd Edition example: A-WALL-FULL-ABOV-D.
- MEP file: `AecbLayerStd.dwg` in `ProgramData\Autodesk\MEP <version>\enu\Layers` or a subfolder. Older copies with a number appended (for example AecbLayerStd5.dwg) are kept for legacy drawings. Shipped templates auto-load a suitable AecbLayerStd ([G:EEE2228A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EEE2228A-8605-4040-8587-4BCA2CC4A4D3)).
- ACA file: `AecLayerStd.dwg` in `C:\ProgramData\Autodesk\ACA <version>\enu\Layers` ([G:FA684C28](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA684C28-B27F-4041-922F-A14A3933A564); [KB:000292194](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-Layer-Standard-in-AutoCAD-Architecture-or-AutoCAD-MEP.html) gives `ACA 20XX`).
- `AECBLAYERSTD` is named on the layer standards drawing page; no prompts given ([G:EEE2228A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EEE2228A-8605-4040-8587-4BCA2CC4A4D3)).

### Select the drawing's standard and key style [GUI] ([G:F2F25F13](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F2F25F13-C0F5-4BE1-A03D-A0852967C639))
1. Home tab > Layers panel > Select Layer Standard. Drawing Setup opens on the Layering tab.
2. "Layer Standards/Key File to Auto-Import": browse to the layer standards DWG or DWT (Content folder > Layers in the left pane of the Open dialog if it is in the default location).
3. "Default Layer Standard": pick the layer key style. Apply.
- "Save as Default" ticked: also applied to every new drawing started with no template or from a template without drawing setup data. Units and Scale tab settings are saved as defaults too.
- Cleared: current drawing only. If units changed, you are asked whether to scale existing objects.
- Layer key styles missing in a drawing: save the layer settings and apply them globally this way ([KB:000606420](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Certain-layer-key-styles-are-missing-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- Layers created in the wrong language: the template's standard and key style are in another language. Reset to defaults or switch the standard and key style ([KB:000431474](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Layers-appear-in-wrong-language-when-working-in-AutoCAD-Architecture-MEP.html)).

### Edit a layer key style [GUI] ([G:58CAE977](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-58CAE977-5A7E-446E-917F-1F33AB38147C), [G:B5E49507](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B5E49507-6E4A-49E5-BE5D-767F75150E4B), [G:BA9F9960](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA9F9960-F871-44BD-92D6-B8FC576495B3))
- Home tab > Layers panel > Layer Key Styles (or the icon in Layer Properties Manager). Style Manager opens: Multi-Purpose Objects > Layer Key Styles > style > Keys tab ([KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html)).
- Columns per key: Description, Layer ([...] opens layer field values), Color, Linetype, Lineweight, Plot (printer icon), Allow Overrides.
- Standard field: pick a layer standard, or Non Standard.
- Add keys (they get default values); Remove keys. DEFAULT keys cannot be removed. Ctrl-select keys to edit together.
- GOTCHA: a newly added key's layer name is not yet based on the standard, so its override options are inactive. Set the layer name with [...] first.
- New key defaults: layer = key name, description blank, color 7, linetype Continuous, lineweight Default, plot style Normal, Plot Yes ([G:0357AD90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0357AD90-862E-44B5-B165-BDD9B5238EC6)).
- New key style: right-click Layer Key Styles > New; or Copy then Paste, then Rename ([G:BA9F9960](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA9F9960-F871-44BD-92D6-B8FC576495B3)).
- From a legacy LY file (Architectural Desktop S8 or Release 1): [AUTO] `AECLYIMPORT` > file name or `?` > new style name > pick LY sections (dialog) > OK. Missing default keys are added and mapped by name (key ANNOBJ to layer ANNOBJ). The new style is not tied to a standard until you assign one ([G:104881DE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-104881DE-B5D9-4792-B6BE-A269F0EF1763)).
- Changes apply to the open drawing only. Repeat them in the template ([KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html)).
- Layers that styles or components point to cannot be deleted ([G:AA3CA86C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-AA3CA86C-D633-493D-B878-58FDD66F0FE1)).

### Default layer keys (ACA list)
- The ACA page lists 102 default keys; none are duct or pipe keys ([G:C2E1E1C5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C2E1E1C5-B7E1-479C-A548-EAED24F80307)). MEP keys are not documented in these sources; read them from the Keys tab of your key style.
- System and equipment keys on that list: COMMUN, CONTROL, DRAINAGE, ELEC, ELECNO, EQUIP, EQUIPNO, FIRE, LIGHTCLG, LIGHTW, PFIXT, POWER, SWITCH, UTIL. Drafting keys include HIDDEN, FINE, THIN, MED, WIDE, HATCH, DIMLINE, ANNOBJ.

### Layer standards: structure ([G:08947990](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-08947990-83DE-48D9-9042-BAC426C65177), [G:206A05AF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-206A05AF-088B-4C11-A74F-E1D33288AD2E))
- A standard = rules that build layer names from component fields joined by delimiters.
- Field settings:
  - Field Name.
  - Optional: Yes lets the field drop off the END of a name. An optional field cannot sit before a required one unless Match Description is Yes.
  - Max Width; Fixed Width (Yes = never shorter than Max Width).
  - Wildcard: AutoCAD wildcard the value must match.
  - Match Description: Yes = recognized only by exact match to a description; this allows omitting fields in the MIDDLE. GOTCHA: an omitted field must have Match Description = No, or the layer cannot be created.
  - Delimiter; Default value.
- AIA Long Format ([G:FE0C3A9D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE0C3A9D-838C-4584-9FDB-5195773ECFA6)), Optional / Width / Fixed / Wildcard / Match / Delimiter / Default:
  - Discipline Designator: No / 1 / Yes / `@` / No / None / A
  - Major: No / 4 / Yes / `@@@@` / No / `-` / Wall
  - Minor: Yes / 4 / No / `*` / No / `-` / blank
  - Status: Yes / 4 / No / `*` / No / `-` / blank
- BS1192 AUG v2 and Descriptive tables: [G:A2C40447](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A2C40447-41ED-47DB-AAF7-C8B0F860D961), [G:80C5FD0A](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-80C5FD0A-9824-42F5-A5E4-CCDD34C3ACE3).
- Edit a standard: Layer Properties Manager > Layer Standards icon > select > Edit > tabs Component Fields, Descriptive Fields, Edit Descriptions, Description Specification ([G:5D5BB167](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5D5BB167-2206-4C4F-AB17-B727D7D7D923), [G:A7E85B67](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A7E85B67-F02B-4965-8168-733E4EAA36A6), [G:617F11DD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-617F11DD-1FF5-4CFC-A93F-2977C796A1CE), [G:BA41DC0E](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA41DC0E-AE59-4F95-8DBD-BBDED67AD268)).
- New layer under a standard: new-layer button > pick the standard > fill fields ([...] or type) > name and description fill in. If the name equals an existing layer in the current key style, that layer's properties are used ([G:D7350EC7](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7350EC7-5626-4A22-B99F-AA5C1EE4E0C8)). "Non Standard" makes a free-named layer ([G:759BEE38](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-759BEE38-BD4A-4A79-928F-E50615CA3BA9)). Right-click a layer > Change Layer Standard (greyed = not valid for it) ([G:C9113394](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C9113394-30A7-4EF3-A0FB-6BE3683F7F9A)).

### Import, export, purge [GUI]
- Import: LAYER > Layer Standards icon > Import/Export > Open > pick a drawing (for example AecLayerStd.dwg) > select standards in the External File list > Import > Apply, OK ([KB:000292194](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-Layer-Standard-in-AutoCAD-Architecture-or-AutoCAD-MEP.html), [G:1DCBBB27](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1DCBBB27-A9DB-41D8-B3BD-D478F77FB28B)).
- Export: Import/Export > New or Open target > select > Export ([G:7CF0A481](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7CF0A481-602F-42CA-A468-FFEBC2EDFF6C)).
- Name clash: Yes overwrites, No cancels ([G:1DCBBB27](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1DCBBB27-A9DB-41D8-B3BD-D478F77FB28B)).
- Then make it current: Select Layer Standard > Layering tab > a key style based on it ([KB:000292194](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-Layer-Standard-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- Purge one: purge the key style based on it first (Layer Key Styles > right-click > Purge), then the standard (Layer Standards > Purge) ([KB:000292194](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-Layer-Standard-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- [AUTO] `AECPURGELAYERSTYLES` purges ALL standards and ALL key styles; use when building templates or before importing new ones ([G:0E8CFE23](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0E8CFE23-734E-43E9-A515-63439478BE89)).

## 7.15 Layer key overrides and remapping

### What overrides do ([G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5), [G:B7611619](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B7611619-E2B2-4CC6-97AA-B8B33BA42327))
- An override changes part of the layer name a key produces, for example the Status or a Minor field, so new objects go on a variant layer.
- Overrides can be allowed on all keys or on chosen keys (Allow Overrides column), and on all or chosen descriptive fields.
- HARD RULE: the key style must be based on a layer standard in the current drawing. A Non Standard style cannot have overrides, and the Overrides On/Off command is unavailable for it ([G:B7611619](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B7611619-E2B2-4CC6-97AA-B8B33BA42327), [G:FA684C28](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA684C28-B27F-4041-922F-A14A3933A564)).
- GOTCHA: the default "Standard" layer key style is NOT based on a layer standard, so it cannot take overrides ([G:FA684C28](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FA684C28-B27F-4041-922F-A14A3933A564)). A copied style supports overrides only if its source was based on a standard.
- The override value must fit the field's width and type. A 4-letter value in AIA Discipline Designator (width 1) fails. Change the standard to change the rules ([G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5)).
- Overrides do NOT change existing objects. Only objects created after the override is enabled ([G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5)).

### [GUI] Set overrides ([G:B7611619](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B7611619-E2B2-4CC6-97AA-B8B33BA42327))
1. Home tab > Layers panel > Layer Key Overrides (or the icon in Layer Properties Manager).
2. Current Layer Key Style: pick the style. "Based on Standard" shows its standard (read-only).
3. Per descriptive field type an Override value or use [...]. Fields depend on the standard; AIA 2nd Edition shows Discipline Designator, Major, Minor 1, Minor 2, Status.
4. Tick "Enable All Overrides" to use them now. OK.
- Not enabled at OK: new objects go on the plain standard layer until overrides are switched on.
- Enable All Overrides skips keys that do not allow overrides; with overrides on, only keys that allow them use the values.

### [AUTO] Toggle ([G:3B46B590](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B46B590-E204-42A0-AFC0-9EE7489D787F))
- `AECTOGGLELKEYOVERRIDESMNU`: toggles overrides for the current layer key style. Works only if the style is based on a standard AND overrides were specified. A check mark beside the menu item = on.
- On: new objects get the standard's layers plus the override values. Off: the page says the standard's layers only; [G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5) says layers "defined only by the layer keys". Same practical result (inference).

### Put new AEC objects on the current layer ([KB:000435576](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-AEC-objects-on-the-current-layer-instead-of-the-definition-from-Layer-Key-in-AutoCAD-Architecture-MEP.html))
- [GUI] Layer Properties Manager (or LAYER) > Layer Key Overrides > "Current Layer Key Style" drop-down > `<Current Layer>` > OK. New AEC objects are then created on the current layer.
- (inference) With this set, a script can choose the layer of new MEP objects with CLAYER before each add command. Test it on pipes and fittings before relying on it.

### [AUTO] Remap Object Layers ([G:94D29AE1](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94D29AE1-E92C-4626-9F29-B94AB1DFEA21), [G:C168FBC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C168FBC2-DC8B-4FF1-94B4-51EA95C7B83B))
- Ribbon: Home tab > Layers panel > Remap Object Layers. The command name is not given in the sources.
- Prompts: select objects, Enter, then enter a layer key name. `?` lists keys (F2 opens the text window; the page copies a key line with right-click > Paste To CmdLine). Typing the key name directly is implied (inference).
- Option `o` (byObject): puts each selected object back on the layer of its DEFAULT key, respecting current overrides.
- Result honors any overrides currently active. This is the documented way to bring existing objects in line after changing overrides (inference from [G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5) and [G:C168FBC2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C168FBC2-DC8B-4FF1-94B4-51EA95C7B83B)).
- Panel styles have no layer key in their design rules; the page says to move panels to another layer by remapping layers "with Layer Manager" ([G:8A1DF64B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8A1DF64B-004E-4554-980A-B8B70784EBC7)).

## 7.16 Layer states, viewport overrides and other layer tools

### Layer 0 and sub-component layers
- Keep layer 0 On and Thawed. With it off, AEC object osnap points are not shown or active ([G:40795C0B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-40795C0B-53A1-4696-88E0-5D3A078D6280)). Blocks and AEC objects keep internal geometry on layer 0, so a frozen or off layer 0 can hide them ([KB:000323063](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Objects-in-Xref-or-in-a-drawing-do-not-display-at-all-or-incorrectly-in-AutoCAD.html)).
- A key style can put an object on one layer and its components on others (example: wall on A-Wall, material components on A-Wall-Comp). Turning the main layer OFF hides the whole object unless an option in "To Specify a Layer Standard and a Layer Key Style" keeps sub-components visible. FREEZING the main layer always hides everything ([G:40795C0B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-40795C0B-53A1-4696-88E0-5D3A078D6280)).
- Objects still visible after their layer is turned off: content sits on other layers; freeze instead, or fix the style ([KB:000417185](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Objects-are-still-visible-even-after-the-layer-has-been-turned-off-in-AutoCAD.html)).
- VP freeze of AEC objects: also VP freeze the layers their sub-components use (check the style and rep) ([KB:000567269](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Layer-viewport-freeze-of-2D-sections-elevations-in-AutoCAD-Architecture-or-MEP.html)).
- Layer on/off and freeze/thaw states and properties: Off and Frozen layers never plot; Frozen layers regenerate when thawed, Off layers do not; Locked layers still allow osnaps; New VP Freeze affects only new layout viewports; you cannot VP-thaw a layer frozen or off globally ([G:40795C0B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-40795C0B-53A1-4696-88E0-5D3A078D6280)).

### Viewport layer overrides ([G:8909084C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8909084C-770C-41A3-A782-CCABE9DC433A), [G:02C58E45](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-02C58E45-05B7-469E-A511-FBDE1F379989), [G:1175F5BC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-1175F5BC-40DB-4EB9-8AAF-715C28F1B2F7))
- Per layout viewport: VP Color, VP Linetype, VP Lineweight, VP Plot Style columns appear when Layer Properties Manager is opened from a layout with a viewport active. VP Plot Style needs named plot styles (PSTYLEMODE = 1).
- They do not change global layer properties or ByLayer/ByBlock object settings.
- Overridden cells show a light blue background; a Viewport Overrides filter lists the layers.
- [AUTO] `VPLAYEROVERRIDES` = 1 means the current viewport has overrides. `VPLAYEROVERRIDESMODE` = 0 hides and stops plotting them. `VISRETAIN` = 0 drops overrides on xref layers.
- Remove: right-click a cell > Remove Viewport Overrides for > property > In Current Viewport only / In All Viewports; or for selected layers or all layers.
- Older releases do not show the overrides but keep them, unless the viewport is deleted there.

### Layer states ([G:0066FDF2](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0066FDF2-0380-4FA7-9F6C-5E082F3DF9BB), [G:94BB0911](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94BB0911-E604-4F56-969E-4275BC8D26E9), [G:E1241484](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E1241484-08A5-4CB9-84E2-E056E4B03368), [G:9456C6C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9456C6C9-3D3B-4D49-8763-9D47D9620068), [G:A12F4A88](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A12F4A88-9119-4BFA-BF1C-2DE02AE9507C))
- A layer state stores layer settings, not the layers. Home tab > Layers panel > Layer States drop-down > Manage Layer State, or the Layer Properties Manager icon.
- Saved from model space: global color, linetype, lineweight, plot style. Saved from a layout viewport: the viewport overrides.
- Restore: tick only the "Layer properties to restore" you want; others stay as they are. "Turn off layers not found in layer state" turns off layers added later. "Apply properties as viewport overrides" (layout viewport only).
- Restoring into a layout viewport cannot change On/Off or Freeze/Thaw (layers come in On and Thawed). Model space restores are always global. Layers off or frozen in a model state become VP Freeze in a viewport.
- The layer that was current at save becomes current again, if it still exists.
- DANGER: delete a layer after saving a state and it silently drops out of that state. Export the state to LAS first if you need it later ([G:94BB0911](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-94BB0911-E604-4F56-969E-4275BC8D26E9)).
- Import sources: DWG, DWS, DWT, LAS. From a drawing, missing layers, linetypes and plot styles come in too. From LAS, a linetype or plot style missing in the target cannot be restored ([G:9456C6C9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9456C6C9-3D3B-4D49-8763-9D47D9620068)).
- Xref states show in the host as `Xref Name__Layer State Name` (double underscore), restorable but not editable; after Bind: `Xref Name$0$Layer State Name` ([G:E1241484](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E1241484-08A5-4CB9-84E2-E056E4B03368)).
- Legacy Layer Snapshots (LAY) convert to layer states (LAS) the first time Layer States Manager opens, and the snapshots are deleted ([G:E1241484](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E1241484-08A5-4CB9-84E2-E056E4B03368), [G:9599CE8D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9599CE8D-A8B0-48E6-850F-CB007668BA33)).
- LISP: layerstate-* functions replace AecLayer*Snapshot functions ([G:9599CE8D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9599CE8D-A8B0-48E6-850F-CB007668BA33)).
- Same colors across many drawings: import a layer state with preset colors and restore it ([KB:000602805](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/EXPORTTOAUTOCAD-from-AutoCAD-MEP-or-Architecture-sets-ACE-and-MEP-colors-to-be-byobject-instead-of-bylayer.html)).

### Other layer tools
- New-layer notification: Layer Properties Manager > Settings > "Evaluate new layers added to the drawing" (xref layers only or all), "Notify when new layers are present" on Open, Attach/Reload Xrefs, Restore Layer state, Save, Insert; "Display alert for plot when new layers are present". Reconcile: Unreconciled Layers group > right-click > Reconcile Layer ([G:057F6FED](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-057F6FED-DC26-4B5E-8FCF-10036F1E5B14), [G:9656C5DE](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9656C5DE-192B-41FD-A802-48A8AE9C5AD8), [G:3749896B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3749896B-2D00-40F2-9329-1F813675F981)).
- Filters: group filter (static, add by hand), property filter (dynamic; criteria in one row are AND, extra rows are OR), layer standards filter (layers of chosen categories). "All" and "Xref" groups are automatic. A layer in several groups changes in all of them ([G:68BF04AD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-68BF04AD-9F26-4FAA-89E5-E9BD06A82849), [G:ACA0470C](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-ACA0470C-989F-4EB6-957F-E74797F1177B), [G:3A3AFB04](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3A3AFB04-59BF-4456-8386-8EC97FBD3052), [G:22F545A0](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22F545A0-4707-4144-A30E-8D18D6AD6B30)).
- Display order by layer: `AECLAYERORDER` or Vision Tools tab > Display Order panel > Display By Layer Order opens a dialog; top of the list draws on top ([G:52E7EC1F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52E7EC1F-4663-4D8D-994E-004279747678)). LAYERORDER crashed in ACA/MEP 2026 ([KB:000625987](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/FATAL-ERROR-Unhandled-when-using-the-LAYERORDER-command-in-AutoCAD-Architecture-or-MEP.html)); fixed in MEP 2027 ([KB:000646540](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-2027--Fixed-Issues.html)).
- Project sheets: Project Properties > Drawing Settings > "Match Sheet View Layers to View" = Yes makes sheet views use the view drawing's layer settings ([G:3050DAA9](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3050DAA9-87AC-45F5-9DDB-BDF766014A29)). Set No if xref layer overrides keep reverting ([KB:000257034](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Xref-layers-reset-upon-reopening-drawing.html)).
- EXPORTTOAUTOCAD gives exploded objects the layer color as a fixed color; run SETBYLAYER on the result ([KB:000602805](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/EXPORTTOAUTOCAD-from-AutoCAD-MEP-or-Architecture-sets-ACE-and-MEP-colors-to-be-byobject-instead-of-bylayer.html)).

## 7.17 Project standards sync for styles and display settings

All from ACA pages; the feature is shared with MEP (inference for MEP style types).

### Basics
- Works only for drawings inside a Drawing Management project. Standalone drawings can receive copied styles but never sync ([G:B9479240](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B9479240-6946-4C2A-8E0F-A162E91FE084)).
- Standards drawings (DWG, DWT, DWS) hold standard styles and display settings. Inside the project folder = project-specific; outside = company standards, only referenced ([G:732BFBCB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-732BFBCB-4DDE-49EC-88A0-8CB8C8E6EC6C)).
- Can be standard: object styles, property set definitions, property data formats, schedule table styles, classification definitions, display theme styles, layer key styles, mask block, material, multi-view block and profile definitions, display properties, display sets, display configurations ([G:732BFBCB](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-732BFBCB-4DDE-49EC-88A0-8CB8C8E6EC6C)).
- Only ONE standards drawing per project may hold display settings ([G:B9479240](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B9479240-6946-4C2A-8E0F-A162E91FE084)).
- AutoCAD standards (layers, text styles, linetypes, AutoCAD dimension styles) must be in DWS files. Their check is separate and always manual, via an auto-made CHX file and the batch standards checker ([G:B9479240](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B9479240-6946-4C2A-8E0F-A162E91FE084), [G:9AFF00CC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9AFF00CC-D934-4F3D-B1DA-7595EA3FFB24)).
- XLOADCTL must be 2 ([G:B9479240](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B9479240-6946-4C2A-8E0F-A162E91FE084)).
- A style type must be ticked for its standards drawing in the project configuration, or its styles show as "not standardized" (gray) ([G:FE9DDF08](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE9DDF08-B0D4-46D5-BEC5-5BE32307BF99), [G:7A6958FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7A6958FF-E53A-4473-9847-555CCD9A4F4C)).

### Versions decide everything ([G:22719521](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22719521-E959-4DDC-8DEF-19175A2E5D17), [G:9AFF00CC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9AFF00CC-D934-4F3D-B1DA-7595EA3FFB24), [G:C864EF6D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C864EF6D-263A-4BCC-B103-D1C47FDE5753))
- Each style and display setting has a version: GUID, date and time, Windows login name of the last editor, optional comment.
- Identical = same object type, same name, same version GUID. No property-by-property compare.
- Project drawings: a new version is made automatically on Apply or OK in Style Manager or Display Manager.
- Standards drawings: you must version by hand (Version History tab > Version, or [AUTO] `AECVERSIONMODIFIEDOBJECTS`). DANGER: saved but unversioned edits never reach project drawings.
- Not auto-versioned in standards drawings: display configuration cut plane, display set surface hatch on/off, display set Live Section on/off, wall graph toggle ([G:22719521](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22719521-E959-4DDC-8DEF-19175A2E5D17)). Cut plane and Live Section changes are not overwritten by sync ([G:C13693FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C13693FD-4D28-4929-88E7-C5CB59176411)).
- If several standards drawings hold the same style, the FIRST (leftmost in the configuration table) wins, even if a later one is newer. Keep dependent styles in one standards drawing.
- A standard with no version info still syncs and counts as latest.
- Rename is not a modification and cannot be synced; sync never deletes anything ([G:F06E006B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F06E006B-B29E-4478-BF3C-114E70D30023)).
- Version history cannot roll back ([G:22719521](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-22719521-E959-4DDC-8DEF-19175A2E5D17)).

### Sync modes (one setting for all project users) ([G:651E734B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-651E734B-06CD-4188-95E9-F66F461BE5A0))
- Automatic: compared at open; drifted items overwritten with no prompt; not standardized items ignored silently; edits in project drawings are not offered for upload.
- Semi-automatic: compared at open; dialog to overwrite or ignore; users prompted to upload changes.
- Manual: user starts sync; dialog to overwrite or ignore; no upload prompt.
- Automatic sync does NOT run during background plot or publish ([G:9AFF00CC](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9AFF00CC-D934-4F3D-B1DA-7595EA3FFB24)).
- Project-wide sync skips drawings open by another user or read-only (Synchronization Warning) ([G:865E3697](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-865E3697-8387-479C-A96D-6B879DBB6EB3)).

### Commands [AUTO] ([G:A5915307](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A5915307-EF29-4865-8CA6-7197BDF44429); no prompts given)
- `AECPROJECTSTANDARDS` (dialog), `AECSYNCHRONIZEPROJECTDRAWING`, `AECSYNCHRONIZEPROJECT` (no interaction only in Automatic mode), `AECAUDITPROJECTDRAWING`, `AECAUDITPROJECT`, `AECSHOWOBJECTDISPLAYOVERRIDES`, `AECVERSIONMODIFIEDOBJECTS` (standards drawings only), `AECPROJECTSTANDARDSSETUPREPORT`, `AECUPDATESTANDARDS`, `AECPURGEVERSION` and `AECCLEARVERSIONHISTORY` (standards drawings only), `AECSYNCHRONIZEWSTANDARDS` (spelled so on the page), `AECUPDATEPROJECTCADSTANDARDS`.

### Per-item actions [GUI] ([G:CC717E15](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CC717E15-BC70-4E32-8DE4-380FE89B5001), [G:7BF70575](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7BF70575-7015-4FC9-BAC6-EED636E48529), [G:D7490E5B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7490E5B-2315-4176-8B5C-F35689CA6CB1), [G:D1737F84](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D1737F84-95BB-40B4-AAE1-FA027847D87A), [G:8A968A6F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8A968A6F-A149-4E1C-9609-4BD0D41FD7D8), [G:FE9DDF08](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE9DDF08-B0D4-46D5-BEC5-5BE32307BF99), [G:9DDD1794](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9DDD1794-574B-4EA0-967A-B185E72B6383), [G:06AB94FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-06AB94FF-3050-4E4C-BD46-65BC4BE9EF68))
- Pull a standard into a project drawing: Style Manager or Display Manager > right-click the item, type or category > Synchronize with Project Standards > Action = Update from Standard > OK.
- Push a project drawing item up: right-click > Update Standards from Drawing. Existing standards (top panel): Update Project Standards / Do not Update Project Standards / Ignore. New items (lower panel): Add to Project Standards / Skip / Ignore. Then OK, Apply, and Yes to save the standards drawing. The change reaches ALL project drawings at the next sync.
- Exclude: right-click > Ignore During Synchronization (toggle). Shown again only if "Show objects set to ignore during project standards synchronization" is ticked.
- Add display settings from the standards drawing: in Display Manager drag the item from the standards node onto the project drawing node ([G:90142973](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-90142973-8DC6-4366-A799-856493D200D3)).
- Status icons: blue = standard, in sync; outdated (standards has newer GUID); nonstandard (newer) version; excluded; no version information; changed but not versioned (standards drawing only); gray or dark blue = not standardized ([G:7A6958FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7A6958FF-E53A-4473-9847-555CCD9A4F4C), [G:BD29B0D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD29B0D6-59B4-4ECC-AB5D-115D455656FB), [G:C13693FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C13693FD-4D28-4929-88E7-C5CB59176411)).
- Choices in these dialogs stop a script ([G:CC717E15](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-CC717E15-BC70-4E32-8DE4-380FE89B5001), [G:D7490E5B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-D7490E5B-2315-4176-8B5C-F35689CA6CB1)).

## 7.18 Troubleshooting checklists

### Object missing or wrong in a view ([G:0EE48E90](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-0EE48E90-9F94-4CE9-84FE-7BC51E09DCD2), [G:EAE0E000](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-EAE0E000-4273-46DE-8A8D-D9C9C595A27E), [G:08D04181](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-08D04181-4E4C-4A38-962F-1C1410E3216A), [KB:000314102](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-display-configuration-of-an-Architecture-or-MEP-drawing-in-AutoCAD.html), KB:ts-5ibXLTjd)
1. Status bar: which display configuration is current? Try the others.
2. Display Manager: the current configuration (bold) and the set mapped to this view direction. Iso views use the Default set.
3. That set's Display Representation Control tab: is a rep checked for the object type? None = not drawn. Wrong one = untick it.
4. Set Display Options tab: is its classification cleared?
5. The rep's components: visible? Correct layer? ByMaterial pointing at a material with display off?
6. Style override or object override hiding the change (7.4).
7. Layer on and thawed, layer 0 on and thawed, viewport layer freeze.
8. Cut plane and display range when display by elevation is on (7.7).
9. Xref: attachment type and xref display configuration (7.10).
10. [AUTO] `DISPLAYDXFNAME` y, REA: labels every object, so you can tell "hidden" from "absent".
11. [AUTO] REA; if a shaded view will not refresh, `OBJRELUPDATE`.
- Pipe or duct shows 1-line where 2-line was expected (or the reverse): wrong rep checked in the set, the configuration was edited, or it is a size-based configuration (7.5). If the configuration is corrupt, copy the content into a clean drawing from an MEP template ([KB:000314102](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-display-configuration-of-an-Architecture-or-MEP-drawing-in-AutoCAD.html)).
- Same part fine in a new drawing but wrong here: corrupt display definition ([KB:000361712](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Certain-MEP-objects-are-not-displaying-correctly-in-AutoCAD-Architecture-or-MEP.html)).

### Display edits not taking effect
- Edited the drawing default but a style or object override wins ([KB:000376064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-objects-do-not-change-color-although-the-display-configuration-was-adjusted-in-AutoCAD-Architecture-MEP.html), [G:3BA802C3](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3BA802C3-BBA9-4687-BCAF-37ADBBB81590)).
- Edited a rep that the active set does not use ([KB:000376064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-objects-do-not-change-color-although-the-display-configuration-was-adjusted-in-AutoCAD-Architecture-MEP.html)).
- New rep missing from the tree: close and reopen Display Manager ([G:131C201B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-131C201B-5AA2-4D98-BB1E-A43DC0138B7F)).
- Changed the drawing default configuration: existing viewports keep theirs ([G:F2B1D798](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F2B1D798-9D12-4A32-81CC-34CCD134072E)).
- Project drawing with Automatic sync: the change is overwritten from standards at next open ([G:651E734B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-651E734B-06CD-4188-95E9-F66F461BE5A0)).
- Edited through refedit of an xref: not saved ([G:8512B736](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8512B736-FC8A-4559-BFF5-7F097517A1C2)).

### Linetype and color problems
- Dashes look solid: AEC component linetype scale is multiplied by LTSCALE ([G:8EBE0D10](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-8EBE0D10-AFF8-4D15-8174-ECB67894AA7D)). Lower LTSCALE or the component LT Scale ([KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html)).
- Hidden line display: needs Plan reps and a configuration with hidden lines on (7.5).
- Object color not following layer: components set to a color, not BYLAYER ([KB:000467587](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/MEP-component-not-matching-layer-color-in-AutoCAD-MEP.html)).
- Thick prints in Hidden or Conceptual: Silhouette Edges width ([KB:000503332](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AEC-MEP-objects-are-printed-very-thick-when-the-visual-style-Hidden-is-applied-in-AutoCAD-based-products.html)).
- Plot colors wrong or gray: check the page setup plot style table and "Display plot styles" ([KB:000357516](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Colors-are-being-displayed-wrong-in-AutoCAD.html)). CTB pairs with color-dependent templates, STB with named ones ([KB:000218455](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-CTB-or-STB-file-in-AutoCAD-is-not-found-or-missing.html)).
- Hatch on AEC objects not shown: pattern too dense for HPMAXLINES; raise HPMAXLINES (max 10,000,000), raise hatch scale, or use a simpler pattern ([KB:000562572](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Custom-hatch-pattern-is-not-displayed-in-AutoCAD-2025.html)).

### Other fixes from support articles
- Grips and trigger grips missing on AEC objects: the plain AutoCAD profile is current. OPTIONS > Profiles > set the MEP profile current ([KB:000483276](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Grips-and-trigger-grips-are-missing-for-AEC-objects-in-drawings-in-AutoCAD-Architecture.html)).
- Selection hangs with the Properties palette open (2023, 2024): too many classification definitions. Close the palette, or purge Style Manager > Multi-Purpose Objects > Classification Definitions ([KB:000538630](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Delay-when-multiple-objects-are-selected-in-AutoCAD-Architecture-or-MEP.html)).
- Classifications duplicating with "(2)" suffixes after inserts: set AECCLASSIFICATIONMERGEBEHAVIOR = 1; in-use classifications cannot be purged ([KB:000349514](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Classifications-get-silently-duplicated-in-AutoCAD-Architecture-or-AutoCAD-MEP.html)).
- MEP 2026 update fixed Display Manager when classifications apply only to AutoCAD objects, and crashes in Display Manager ([KB:000604615](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Fixed-Issues-in-AutoCAD-MEP-2026.html)). MEP 2027 keeps exported IFC layers for all objects and fixes the LAYERORDER crash ([KB:000646540](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-2027--Fixed-Issues.html)).

## 7.19 Gaps and conflicts in the sources

### Conflicts (both sides cited)
- Display Manager command: `DISPLAYMANAGER` ([KB:000447005](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Referenced-walls-are-not-displayed-in-a-2D-Section-in-AutoCAD-Architecture-MEP.html), [KB:000375916](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Hidden-parts-of-ducts-or-pipes-do-not-show-as-dashed-in-AutoCAD-MEP.html)) vs `DISPLAYMANGER` ([KB:000468738](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/XCLIP-of-references-does-not-work-for-Top-view-in-AutoCAD-Architecture-MEP.html), a typo). No help page in these sources names the command.
- Style Manager command: `STYLEMANAGER` ([KB:000517324](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/2D-Section-Elevation-colors-are-different-from-the-model-data-in-AutoCAD-Architecture-MEP.html), [KB:000474189](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Assigning-MEP-object-sub-components-to-specific-layers-in-AutoCAD-MEP.html)) vs `STYLESMANAGER` ([KB:000538630](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Delay-when-multiple-objects-are-selected-in-AutoCAD-Architecture-or-MEP.html)). STYLESMANAGER opens the plot style folder ([KB:000218455](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Error-CTB-or-STB-file-in-AutoCAD-is-not-found-or-missing.html)), so use STYLEMANAGER. No help page in these sources names it.
- Styles Browser command: `STYLESBROWSER` ([G:F8A1FAD4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8A1FAD4-FEF0-4848-8D91-D0C9DF74CED5), [G:BA5E6771](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA5E6771-DB18-43B5-A1A2-FDE8329852BC)) vs `STYLEBROWSER` ([KB:000464059](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Electrical-devices-do-not-display-as-3D-in-AutoCAD-MEP.html)).
- Pipe style edit command printed `PIPESYTLEEDIT` ([G:1BEEE2FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BEEE2FD-894B-482C-8C18-E67AC5B1ECB4)). Probably PIPESTYLEEDIT (inference).
- Layer state restore LISP printed `layerstate-retore` ([G:9599CE8D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-9599CE8D-A8B0-48E6-850F-CB007668BA33)). Probably layerstate-restore (inference).
- "Display controlled by" options: [G:E45168F3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E45168F3-6999-41DB-A693-292AD1432D50) says three and lists four (Object, Style, System definition, Domain drawing default). [G:2AAC9199](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2AAC9199-ECCA-44FC-BFBB-7A7AC639CF2D) gives the clear order Object > Style > System Definition > Domain Drawing Default.
- Display by elevation, objects outside the range: drawn with Above/Below components ([G:17BF13BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-17BF13BF-C73F-403F-B695-47766CFB78D7)) vs "not visible" (KB:ts-5ibXLTjd).
- Xref overlay option: "use this drawing's default display configuration initially" ([G:5C7165F8](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-5C7165F8-B78F-41F7-9021-BED2172E8E44)) vs "always use its own" ([G:332E0EC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-332E0EC6-2AFC-4A48-99E3-DDC40BA524CC)). The host-side list entry is "Drawing Default" ([G:332E0EC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-332E0EC6-2AFC-4A48-99E3-DDC40BA524CC)) or "Domain Drawing Default" ([G:78166D6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78166D6B-1CDD-46E5-A1D1-1319E124E280)).
- Layer key overrides switched off: new objects go on layers "defined by the layer standard" ([G:3B46B590](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-3B46B590-E204-42A0-AFC0-9EE7489D787F)) vs "defined only by the layer keys" ([G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5)).
- AIA override fields: "Minor Code and Status" ([G:A074A216](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-A074A216-910E-44EE-9783-474FEE14D6D5)) vs Discipline Designator, Major, Minor 1, Minor 2, Status ([G:B7611619](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-B7611619-E2B2-4CC6-97AA-B8B33BA42327)). The AIA Long Format rules table shows one Minor row though the field list names Minor 1 and Minor 2 ([G:FE0C3A9D](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-FE0C3A9D-838C-4584-9FDB-5195773ECFA6)).
- Not-standardized icon: gray ([G:7A6958FF](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-7A6958FF-E53A-4473-9847-555CCD9A4F4C), [G:C13693FD](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C13693FD-4D28-4929-88E7-C5CB59176411)) vs dark blue ([G:BD29B0D6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BD29B0D6-59B4-4ECC-AB5D-115D455656FB)).
- XREFOVERRIDE = 1 is listed as both a cause and a fix of lost xref layer overrides ([KB:000257034](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Xref-layers-reset-upon-reopening-drawing.html)).
- Duct layer example: `M-Duct-Std` ([G:5B6BCE5E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5B6BCE5E-FE2B-4241-B4CD-8E131E4E0AEF)) vs `M-HVAC-Duct` ([KB:000247518](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Setting-the-default-layer-for-ducts-and-pipes.html)). Different key styles; read your template's Keys tab.
- Styles Browser Drawing Source: two choices ([G:BA5E6771](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-BA5E6771-DB18-43B5-A1A2-FDE8329852BC)) vs three including a Project Standards drawing ([G:F8A1FAD4](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-F8A1FAD4-FEF0-4848-8D91-D0C9DF74CED5), [G:2787AFC6](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-2787AFC6-50C8-4728-B654-40EC6E3B5D79)).
- [G:3D6A9A21](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3D6A9A21-7F19-4B71-98D9-CBEE6FB1DCF0) labels its per-direction column "Display Representations", but the entries (for example "MEP Design - Plan") are display set names (KB:ts-5ibXLTjd).
- Live sections Danger note: unclear whether it means the "Show Materials..." box or the whole "Section AEC Objects by Display Range..." group ([G:E97BD768](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-E97BD768-DD6E-4DF1-A40F-C3B19F4EC6E7)).
- Display order: help names `AECLAYERORDER` ([G:52E7EC1F](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-52E7EC1F-4663-4D8D-994E-004279747678)); support articles name `LAYERORDER` ([KB:000625987](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/FATAL-ERROR-Unhandled-when-using-the-LAYERORDER-command-in-AutoCAD-Architecture-or-MEP.html), [KB:000646540](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-MEP-2027--Fixed-Issues.html)). Same feature is likely (inference).
- Layer states table ([G:40795C0B](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-40795C0B-53A1-4696-88E0-5D3A078D6280)) prints the same "still hides other objects under HIDE" wording for Off and for Frozen. Verify against core AutoCAD help.
- Attach vs Overlay are described differently on [G:CD9F2073](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD9F2073-511E-404E-99BE-F2D7FE33BE29) and [G:45203A5A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45203A5A-EB2C-40CF-A685-65B8CAC73F07). Display rule that holds on both: an overlay is not shown when its host is referenced elsewhere ([G:45203A5A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45203A5A-EB2C-40CF-A685-65B8CAC73F07)).

### Gaps (not answered by these sources)
- Routing preferences: not named anywhere in these sources, including how they move between drawings.
- No command-line, LISP, COM or .NET way to create or edit display configurations, sets, reps, styles, system definitions, layer key styles or layer standards. Only layerstate-* LISP functions appear.
- No typed way to set a viewport's display configuration by name. DISPLAYMANAGERCONFIGSSELECTION is a pop-up menu ([KB:000314102](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-change-the-display-configuration-of-an-Architecture-or-MEP-drawing-in-AutoCAD.html)). For xrefs, SETXREFCONFIG is scriptable.
- No command names for Remap Object Layers, Layer Key Styles, Layer Key Overrides or Select Layer Standard.
- MEP layer key names (pipe, duct, fitting keys) are not listed; the ACA key list has none ([G:C2E1E1C5](https://help.autodesk.com/view/ARCHDESK/2027/ENU/?guid=GUID-C2E1E1C5-B7E1-479C-A548-EAED24F80307)).
- Where the "Pipe By Size" (2-line, 1-line, graphical 1-line) setting sits in the system definition dialog, and where a rise/drop style is assigned to a system.
- Which Options tab holds "Enable Display by Elevation" ([G:F9A8BE6B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F9A8BE6B-BEF9-4754-B62C-C35A877B5798) only links it to the MEP Display Control tab).
- Procedure pages referenced but not supplied: To Configure the Display of a Gap Between Crossing Objects; To Override the Cut Plane; To Enable the Elevation-Based Display Components; To Display Center Lines on Ducts; To Apply System-Level Overrides; To Apply Style-Level Overrides; About Pipe System Displays.
- Where the Content Drawings Library list is stored (per user or per profile).
- 2027 template file names: [KB:000290064](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/AutoCAD-Architecture-MEP-AEC-objects-not-visible-in-files-created-with-acad-dwt-template.html) lists names for 2013 to 2017 only.
- Whether display, style and layer key behavior works in the headless Core Console is not covered here; see the automation sections.
