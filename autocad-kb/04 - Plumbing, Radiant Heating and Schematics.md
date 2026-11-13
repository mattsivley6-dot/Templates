# 04 - Plumbing, Radiant Heating and Schematic Diagrams

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

AutoCAD MEP 2027 (US Imperial) handles plumbing-type work with three object families: 3D Pipe objects laid out from routing preferences (pressure and gravity/sloped), 2D style-based plumbing lines and fittings sized from fixture-unit and code tables, and 2D schematic lines and symbols for not-to-scale flow and riser diagrams.
This section covers all three, plus system definitions (Design Rules, system groups, the Waste rule), fixtures and fixture unit tables, sanitary and supply sizing with the math behind them, radiant heating (radiator MvParts, BDH and XML import, parallel pipes, valves, Connect Multiple Parts), and the UI facts these tasks depend on.
Almost every documented procedure is palette, dialog or grip based. The few documented command-line prompts are collected in 4.2 and marked [AUTO].
Legend: [G:xxxxxxxx] links go to the Autodesk AutoCAD MEP 2027 help page; [AUTO] marks a command-line or scripting note; [GUI] marks a step that needs a dialog, palette or grip.

## Contents
- 4.1 Pick the object family: Pipe, plumbing line or schematic line
- 4.2 Command and prompt index [AUTO]
- 4.3 System definitions (all domains) and plumbing system definitions
- 4.4 Pipe for gravity work: routing preferences, slope, deflection, elevation lock
- 4.5 Auto layout, routing solutions and connecting to equipment
- 4.6 Pipe connections, joints, engagement length and cut length
- 4.7 Pipe grips and associative movement
- 4.8 Pipe display: 1-line, 2-line, graphical 1-line, placeholder parts
- 4.9 Plumbing line and fitting styles (2D)
- 4.10 Drawing plumbing runs
- 4.11 Modifying plumbing runs and plumbing grips
- 4.12 Fixtures, fixture unit tables and sizing tables
- 4.13 Sanitary sizing
- 4.14 Supply sizing and its math
- 4.15 Radiant heating: radiators, BDH and XML import, parallel pipes
- 4.16 Radiator valves, alignment grips and Connect Multiple Parts
- 4.17 Schematic diagrams: concepts, modes, symbol kinds
- 4.18 Schematic styles and schematic system definitions
- 4.19 Drawing and converting schematic lines
- 4.20 Modifying, moving, rotating and resizing schematic objects
- 4.21 Chilled-water flow diagrams with the schematic tools (mostly inference)
- 4.22 Toolset UI facts these tasks depend on

## 4.1 Pick the object family: Pipe, plumbing line or schematic line

| Need | Use | Key limit |
|---|---|---|
| 3D layout with real sizes, elevations, sections, interference; chilled water, hydronic, steam; sloped drain/waste/vent in 3D | Pipe objects (Piping workspace, PIPEADD, routing preferences) | Sizing tools for plumbing do not run on Pipe (inference from [G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41) and [G:A7121902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7121902-5331-43FC-B965-024C8CF95E7A), which select plumbing runs) |
| Code-table sizing of domestic water or sanitary by fixture units | Plumbing lines and plumbing fittings (Plumbing workspace, PLUMBINGLINE) | 2D only; size, slope and elevation are "for calculation only" ([G:EFC3EA56](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EFC3EA56-822C-4184-AECD-D2BAA2CB2A4D), [G:673678A6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-673678A6-7871-4846-A8D9-261A8B9FA9A6), [G:B999730B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B999730B-1CBF-4A96-B108-2B8499715BB2)) |
| Not-to-scale flow diagram, riser diagram, 1-line concept | Schematic lines and symbols (Schematic workspace, SLINEADD) | No elevations or sections from it; no duct sizing or plumbing sizing tools ([G:24AA4038](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24AA4038-A82E-4224-9385-96495590CD4B)) |

- Pipe parts, plumbing equipment and plumbing fixtures are catalog-based (3D part definitions plus part models in part catalogs; equipment is called multi-view parts, MvParts). Plumbing lines, plumbing fittings and schematic objects are style-based 2D (property sets plus view blocks) ([G:07F8CEF9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F8CEF9-6BA9-4E1E-A2E3-71682E03DA85), [G:A9DC5DF8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A9DC5DF8-B9F0-4E8B-89BB-B2DA3CC9F5EE), [G:4272858B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4272858B-2EB7-4EE0-95F9-953B979A63E8)). Pipe is one of the part catalogs ([G:18346E9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-18346E9D-8EC7-45E2-B97D-35239E7F0973), [G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7)).
- Style-based content is made in Style Manager. Catalog parts (parametric or block-based) are made with Content Builder ([G:07F8CEF9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F8CEF9-6BA9-4E1E-A2E3-71682E03DA85)).
- Plumbing lines are 2D, system-based and style-based. Define systems, line styles and fitting styles BEFORE adding lines ([G:595EF736](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595EF736-646D-4717-AE17-BDCB5986A8BB)).
- The plumbing workflow combines families: step 9 draws a 1-line plumbing isometric with the schematic tools for code officers ([G:73E66BE7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73E66BE7-F5E4-4A56-94D8-546B75CE410A)). The general MEP workflow puts schematic flow and 1-line diagrams before detailed design with catalog parts ([G:0F5DF631](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0F5DF631-417C-416B-B4A9-FAC00947ADBD)).
- (inference) The sources describe no conversion between plumbing lines and Pipe objects, or from schematic lines to either.
- Pipe has its own gravity routing preferences and Gravity Pipe tab tools (drain, process drain, sanitary, sanitary vent, storm) ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8), [G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)). So sloped DWV can be modeled as Pipe; code sizing still needs plumbing lines (inference).

## 4.2 Command and prompt index [AUTO]

General rules for scripting these commands:
- [AUTO] No hyphen (dialog-free) form is documented in these sources for any pipe, plumbing or schematic command. Most names below come only from page metadata, with no prompts documented. Probe each one before relying on it.
- [AUTO] Application-menu command search finds MEP commands by name only with the Aecb prefix (aecbPipeAdd, not PipeAdd). The page does not say whether the command line needs the prefix ([G:C4C54B64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C4C54B64-5775-4AA1-862B-3541F57EE6B4)).
- [AUTO] Grip dimension input fields need BOTH Dynamic Input (status bar) and the Dimension Input drafting setting (default on). If either is off, pick a point or type coordinates at the command line ([G:1C6430E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C6430E8-E2C6-40EA-B3DC-9534821188F9), [G:8AFBE73A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AFBE73A-7535-4B74-98BA-2D0DAB749668), [G:D98C496C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D98C496C-DF52-4F33-A234-D0412EF24465), [G:9ADD3D9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9ADD3D9D-4496-4A73-90A3-4B102E13174F)).
- [AUTO] Grip connectivity choice (location, elevation grips): no key = keep connection, adjust only fittings and segments, parts stay; Ctrl once = adjust all objects including MvParts; Ctrl twice = break connectivity ([G:8AFBE73A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AFBE73A-7535-4B74-98BA-2D0DAB749668), [G:1C6430E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C6430E8-E2C6-40EA-B3DC-9534821188F9), [G:9ADD3D9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9ADD3D9D-4496-4A73-90A3-4B102E13174F)).

Pipe:
- [AUTO] PIPEADD: add a pipe run. The Placement elevation lock is OFF every time PIPEADD starts and resets to unlocked when it ends ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C)). Cannot lock elevation on a sloped segment ([G:5BE180D2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5BE180D2-1261-4ECA-AC43-01665B174D44)).
- [AUTO] PIPE: named on About Pipe Systems; no prompts given ([G:91CB307A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-91CB307A-2C8D-4476-B883-41C444B30ED4)).
- [AUTO] Routing solution prompt (when a pipe connects to an object that needs a solution): `n` Enter = next, `p` Enter = previous, `a` Enter = accept the one previewed, or type the solution number then `Accept` ([G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926)).
- [AUTO] PIPESLOPEDISPLAY: turns off the slope readout on segments. Enter PIPESLOPEDISPLAY, then `n` at the next prompt ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- [AUTO] AECBBASICCONNECTOREDIT: Pipe Connection Point Editor. Edits Pipe Units (Metric or Imperial), Pipe Size, End Type ([G:494AB729](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-494AB729-410F-481D-BF84-8FFF50B7D396)).
- [AUTO] PARALLELROUTING: adds parallel pipes (radiant heating). A conflict dialog can open mid-route and blocks a script ([G:EA1558DB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA1558DB-9E56-4CA1-8697-9D53387C8DCF)).

Plumbing (2D lines):
- [AUTO] PLUMBINGLINE: add plumbing lines; also Home tab > Build panel > Plumbing Line ([G:595EF736](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595EF736-646D-4717-AE17-BDCB5986A8BB), [G:135AAC3A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-135AAC3A-7689-429D-90AE-DAEC991F5DD1)).
- [AUTO] PLUMBINGLINECONVERT: right-click "Convert to Plumbing Line" on a selected LINE or PLINE (path may mix both). Prompt: Enter or `n` = keep the layout geometry, `y` = erase it. Then set style, size, system on the Properties palette Design tab; Esc saves and exits ([G:47B8FFDA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-47B8FFDA-3D93-4611-82F5-DBA0F3DDC59E)).
- [AUTO] Add Expansion Loop (ribbon only, no command tag): prompts in order: start point, second point, distance from the run, side of the run ([G:367A7BF0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-367A7BF0-FA2B-44EE-8A35-9BDF4D023012)).
- [AUTO] PLUMBINGLINESIZE with PLUMBINGLINESIZESANITARY or PLUMBINGLINESIZESUPPLY: open the Size Sanitary / Size Supply Plumbing Line dialogs. Calculator without resizing: Analyze tab > Plumbing panel > Size Plumbing, then press Enter at the command prompt; no option keywords documented ([G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41), [G:A7121902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7121902-5331-43FC-B965-024C8CF95E7A)).
- [AUTO] Metadata only, no prompts: PLUMBINGLINEMODIFY, PLUMBINGFITTINGMODIFY ([G:9D7DFD3D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D7DFD3D-42A5-4C26-8D41-6C6DEBC034BF), [G:863E7E92](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-863E7E92-E270-4034-888B-B5AD1F6188C0)); PLUMBINGFITTING ([G:5F1FAEF7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5F1FAEF7-C76B-48BD-86E0-B9B430A63CBD)); PLUMBINGLINEINVERTELEVATION ([G:673678A6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-673678A6-7871-4846-A8D9-261A8B9FA9A6)); PLUMBINGLINEREVERSEFLOW ([G:84894822](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-84894822-2D93-4079-B683-64AF89132735)); SHOWOBJECTSLIMITINGRUN ([G:5027E609](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5027E609-F871-4138-B1F6-50255E849E43)); PLUMBINGLINESTYLE, PLUMBINGLINESTYLEEDIT ([G:FC170703](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FC170703-22AE-4A72-BD23-049C40542588)); PLUMBINGFITTINGSTYLE, PLUMBINGFITTINGSTYLEEDIT ([G:A1E9478A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1E9478A-FF15-44BA-AE0D-F6446AD722B8)); PLUMBINGSYSTEMDEF, PLUMBINGSYSTEMDEFEDIT ([G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F)); FIXTUREUNITTABLESTYLE ([G:3EDC2C43](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3EDC2C43-52FA-4C85-9C87-1D8CF495A248)); SUPPLYPIPESIZINGTABLEDEF, SANPIPESIZINGTABLEDEF ([G:8416BAB1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8416BAB1-1AB2-4DD5-8086-732B40F58668), [G:E5900776](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5900776-DE47-43DC-93D3-EFF7F5126545)). The style and table pages describe only Style Manager (dialog) steps.
- (inference, unverified) SHOWOBJECTSLIMITINGRUN may be the command behind the Plumbing Line tab button Show Objects for Sizing ([G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9)).

Schematic:
- [AUTO] SLINEADD: add schematic lines. Typing `slineadd` works ([G:A831C7DA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A831C7DA-A282-4FC5-B145-E0DF4D68A194)). Style, System, Orientation, Isoplane, ID are set on the Properties palette; no command-line options documented. Pick points; Enter ends.
- [AUTO] Convert to Schematic Line (right-click on a LINE, ARC or PLINE; the page names no command): Enter or `n` = keep layout geometry, `y` = erase. The Modify Schematic Lines dialog opens (System, Style, Designation ID). The same can be given at the command line: `sy` system, `st` style, `i` designation ID, `m` match (pick an existing schematic line, choose properties, Enter) ([G:EDD12C73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EDD12C73-9857-457E-B925-12B3E6100C3C)).
- [AUTO] Grip move of schematic lines or symbols: click the Location grip (ortho) or Move Isoplane grip (isometric), then drag and click, or enter `b`, pick a base point, pick the second point ([G:203B4B72](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-203B4B72-579C-4F83-A871-1BD66B4BE908), [G:EB6B3C0C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB6B3C0C-3450-496F-BC0C-D6BB75140522)).
- [AUTO] SCALE resizes schematic symbols: select, base point, factor; or `R` for reference ([G:595AEF3F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595AEF3F-0D40-4D4C-83E3-0C527E4D2059), [G:3EEE6E29](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3EEE6E29-5AE6-4C6F-81B8-458053959471)). FILLET joins schematic lines by extend or trim ([G:A831C7DA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A831C7DA-A282-4FC5-B145-E0DF4D68A194)).
- [AUTO] Metadata only, no prompts: SLINE, SLINEADDSELECTED, SYMBOL, SYMBOLADD, SYMBOLADDSELECTED ([G:A614B788](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A614B788-0A64-4F7C-8C1F-6C4701C8AC73)); SLINESTYLE, SLINESTYLEEDIT ([G:8556E17E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8556E17E-8BDB-4384-8A3C-A63E65F91C42)); SSYSTEMDEF, SSYSTEMDEFEDIT ([G:2F7F184E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F7F184E-0CD2-4E41-9DEF-8D3858924B92)); SYMBOLPROPS ([G:73A0404A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73A0404A-5896-4FDC-B96F-2E46EC1E89A2)).

## 4.3 System definitions (all domains) and plumbing system definitions

What a system definition is:
- A style that holds properties shared by every object assigned to it: design rules, rise and drop style, display properties, layer key, attached notes and files ([G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370), [G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549)). Systems are assigned to catalog-based content ([G:07F8CEF9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F8CEF9-6BA9-4E1E-A2E3-71682E03DA85)).
- Stored in the drawing; can differ per drawing; can be copied between drawings. Default templates ship several (pipe: chilled water, heating hot water, steam and more) ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549), [G:2F7F184E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F7F184E-0CD2-4E41-9DEF-8D3858924B92)).
- A layer key style on the definition sets layer, color and linetype ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549), [G:DC9E8C4A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC9E8C4A-E447-4A8A-BD77-FABCA5C8F9B3), [G:2F7F184E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F7F184E-0CD2-4E41-9DEF-8D3858924B92)).
- A pipe system definition can show pipes 1-line or 2-line by size ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549)).

Open, create, copy [GUI]:
- Domain workspace > Manage tab > Style & Display panel > Style Manager drop-down > HVAC / Piping / Electrical / Plumbing / Schematic System Definitions ([G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370), [G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252)).
- New: in the left pane right-click the System Definitions node > New, type a name, Enter ([G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370)).
- Copy: right-click an existing definition > Copy; right-click the category node > Paste; right-click the copy > Rename; type; Enter ([G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F), [G:2F7F184E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F7F184E-0CD2-4E41-9DEF-8D3858924B92)). The general page words the paste step as "right-click the copy > Paste" ([G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370)).
- Then set the general properties (design rules, rise and drop style, display properties, notes and files), then the discipline tabs (duct, pipe, plumbing, electrical, schematic) ([G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370)).

Design Rules tab fields ([G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252)):
- Abbreviation: short system name, typically 2 or 3 characters; used in labels and schedules.
- System Group: select or type a name (new names join the list). Blank = may connect to any system group.
- System Type: only on Electrical and Plumbing definitions; list is NOT customizable. Every electrical system MUST have one. Plumbing examples: Hot Water, Waste; a plumbing system does not need one, except for the Waste rule below.
- Layer Key: list depends on the layer key style set for the drawing. Override: click [...] beside the Layer field, pick override values, OK.

Rules that cost runs:
- WASTE RULE: a sanitary system carrying gray or black water must have System Type = Waste (Design Rules tab). Otherwise the sizing command does not see it as sanitary and the run cannot be sized ([G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252), [G:E9F4BD73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9F4BD73-B3D2-4B2F-A067-929463A1A370), [G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F), [G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41)).
- Only Waste can be sanitary-sized; Storm Drain cannot be sized ([G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41)). Only Hot Water or Cold Water can be supply-sized ([G:A7121902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7121902-5331-43FC-B965-024C8CF95E7A)).
- Runs on different system definitions cannot connect unless you change the connecting run's system, EXCEPT when both definitions share one System Group. Then they connect and each keeps its own settings. Example group: Heating Hot Water - Supply plus Heating Hot Water - Recirculation ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549), [G:DC9E8C4A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC9E8C4A-E447-4A8A-BD77-FABCA5C8F9B3), [G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252)).
- Changing the system of one plumbing segment or fitting changes ALL components with valid connections to it ([G:26A610D4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-26A610D4-F534-42C4-BC69-1840C0D1086F)).

Display Properties tab ([G:912CD3A2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-912CD3A2-4B03-4480-BB84-8F1B609FFCDD)) [GUI]:
- Definitions use the display properties of the display representations and can override them. Select the system, Display Properties tab, pick the representation under Display Representations, check Style Override, edit components in the Display Properties dialog, OK twice.

Plumbing system definitions ([G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F), [G:DC9E8C4A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC9E8C4A-E447-4A8A-BD77-FABCA5C8F9B3), [G:B8EEA949](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8EEA949-6231-4313-8095-4C5EC4A148F4), [G:A77D3E44](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A77D3E44-2EAC-4EE9-9083-6E0217E307B7)):
- Commands tagged: PLUMBINGSYSTEMDEF, PLUMBINGSYSTEMDEFEDIT; page steps are Style Manager only [GUI].
- Related tasks named on the overview page: create a definition, set default fittings, set label and flow-arrow preferences, set annotation for a line style ([G:A77D3E44](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A77D3E44-2EAC-4EE9-9083-6E0217E307B7)).
- Named for what they serve (domestic hot water, sanitary sewer). The system sets system type (Cold Water, Waste, Fire Protection), the fittings inserted, and display ([G:DC9E8C4A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC9E8C4A-E447-4A8A-BD77-FABCA5C8F9B3), [G:595EF736](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595EF736-646D-4717-AE17-BDCB5986A8BB)).
- Tabs: General (name, description); Defaults (default fittings); Design Rules (System Type); others, then OK ([G:C05BEF63](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C05BEF63-974A-49F8-B158-3704F2CC8E7F)).
- Defaults tab entries: Elbow Tip, Tee, Tee Up, Tee Down, Cross, Transition. Set defaults for EVERY system used in a project. A default can be a base tee instead of a straight tee ([G:B8EEA949](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8EEA949-6231-4313-8095-4C5EC4A148F4)).
- Elbows are drawn dynamically from run direction. Elbow style name = elbow type + angle used (example: 60 Degree Standard Radiused Elbow). Those styles are stored in the drawing and reusable. There is no Import button for elbows ([G:B8EEA949](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8EEA949-6231-4313-8095-4C5EC4A148F4), [G:5F1FAEF7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5F1FAEF7-C76B-48BD-86E0-B9B430A63CBD)).
- Other default lists: if empty or missing a fitting, click Import, pick a fitting, OK ([G:B8EEA949](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8EEA949-6231-4313-8095-4C5EC4A148F4)).
- Second route to the Defaults tab: select a fitting > Plumbing Fitting tab > General panel > Edit Style drop-down > Edit System Style ([G:B8EEA949](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8EEA949-6231-4313-8095-4C5EC4A148F4)).
- Tee Up / Tee Down are used when a run connects at a point on a line at another elevation (see 4.10) ([G:30DCAD62](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-30DCAD62-36B4-4EBE-9197-B365C10EAFD9)).

Schematic system definitions: see 4.18.

## 4.4 Pipe for gravity work: routing preferences, slope, deflection, elevation lock

Routing preferences ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)):
- Tell auto layout which pipe and fittings to insert. Hold one or more SIZE RANGES (by nominal diameter) of pipe and fittings (elbows, tees, laterals, transitions). Couplings go in at the proper pipe length and at break points.
- Chilled-water example from the page: commercial steel threaded for 3" and smaller; commercial steel 150 class weld neck flanged for 3 1/2" and larger.
- Find or apply [GUI]: Styles Browser palette > Object Type > Piping Objects > Pipe Part Routing Preferences; or select a pipe > Properties palette > Basic > Dimensions > Routing Preference > button in the field.
- US Imperial pressure samples: Butt welded; Grooved and threaded; Slip on flanged - 150 lb. and threaded; Threaded 2000 lb.
- US Imperial gravity samples: Cast Iron soil pipe (bell and spigot); Cast Iron soil pipe (no hub); Ductile iron mechanical joint; HDPE; Sanitary drain, waste, vent.
- Size range rules: parts in a range must share nominal sizes. The lower limit is set to the smallest size common to all parts. The Size Upper Limit list offers only common sizes. Example: pipe 1/8" to 60" with elbow 1" to 24" gives 1" up to 24". Entering a value below the previous range's upper limit swaps the two ranges.
- Version gotcha: routing preferences from Autodesk Building Systems 2007 drawings were never validated for common sizes. Opening them in 2027 validates them, which can reset upper limits and set some parts to *NONE*.

Change routing preference or size on an existing run ([G:0E26F347](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0E26F347-F8B2-48CB-9048-4DFA1C6456E3)):
- Select a segment > Properties palette > Dimensions > routing preference, then Nominal size. The size list holds only sizes common to all pipes and fittings in that preference, grouped by size range. Missing size = choose another preference or edit its size ranges.
- Whole run [GUI]: Pipe tab > Modify panel > Modify Run > Modify Pipe Run dialog.
- Changing preference can change connection type (flanged to grooved) or pipe type (commercial to iron pipe).

Draw sloped piping ([G:68D9D62C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68D9D62C-1FC7-4960-B636-79C8CA5C9F9B), [G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)):
1. Start a pipe run. 2. Properties > General: pick a GRAVITY routing preference. 3. Nominal size.
4. Routing > Slope format (example Rise/Run with Fractional Rise = 1/4" per foot). Slope format is also on the General tab of Pipe Layout Preferences.
5. Slope: value in the current format. Negative pitches down from the main or branch in iso (-1/4" = down 1/4" per foot).
6. Advanced > Routing Options > Use fitting tolerance = Yes (default). Turns on angle of deflection (AoD) where the fitting supports it; ignored for female fittings without deflection (a flange).
7. Joint direction (male-female preferences only): with the flow = Male into Female (default); against the flow = Female out to Male.
8. Branch fitting: example "Tee or Wye (Lateral)" tries a tee, else a wye.
9. General > Routing: branch angle from catalog content; "Values from catalog selection" uses all angles in the preference. Outside angle plus tolerance opens the Choose a Part dialog [GUI].
10. Pick points; slope shows on the segment.
- Coupling or elbow follows the fitting tolerance: tolerance 10 degrees, a 5 degree layout angle gets a coupling, more gets an elbow ([G:68D9D62C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68D9D62C-1FC7-4960-B636-79C8CA5C9F9B)).
- Slope applies in the Z direction of the CURRENT UCS ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- Auto layout solves sloped runs only if the routing preference supports AoD ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- Gravity Pipe tab tools (drain, process drain, sanitary, sanitary vent, storm) support 1/8", 1/4", 1/2" per foot ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- Reducers: eccentric (different centerlines) or concentric (same centerline). Branch to main uses wyes (laterals) or angled tees ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)).
- Tip for PRESSURE piping (faster, more directed solutions): Use fitting tolerance = No, set Bend angle, set Branch fitting ([G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)). (inference) This applies to chilled water.

Angle of deflection ([G:4F5FA490](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4F5FA490-0E26-4041-A211-DD62B6088794), [G:AFC86914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AFC86914-6495-41E7-9307-766EC241D3B5), [G:D69BAA6F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D69BAA6F-F571-47B7-AB6E-7A39EF894F87)):
- Stored in catalog content; exists only on female fittings the maker's spec supports.
- Split equally among a fitting's female connectors (slope 10 degrees, 2 female connectors = 5 each), never above the AoD stored on the part.

Elevation lock ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C), [G:5BE180D2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5BE180D2-1261-4ECA-AC43-01665B174D44)):
- Properties palette > Placement: set elevation, start the run, then lock. A locked horizontal run will not snap to objects at other elevations.
- Use: tie a horizontal run into a riser along its length at the run's elevation. In top view only the riser end connector shows and its solutions miss the elevation; lock first, then pick the pipe snap on the riser.
- Can lock part of a run and unlock for the rest. Resets to unlocked when the pipe-add session ends. Cannot lock a sloped segment.
- (inference) A script must set the lock again in each PIPEADD session.

## 4.5 Auto layout, routing solutions and connecting to equipment

Pipe design workflow, in order ([G:3F1F7003](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3F1F7003-4B05-4D96-BD57-0035AA20C770)):
1. Set up the project, open the drawing, set pipe system standards, xref the architectural floor plan.
2. Preliminary 1-line conceptual design (for code officers and senior engineers).
3. Specify the pipes and fittings used while drawing (piping design specs = routing preferences).
4. Specify system definitions (chilled water, steam), size ranges, display properties.
5. Add boilers, chillers, pumps, heat exchangers and other equipment.
6. Connect equipment and lay out the runs, sloped or not (pipe settings, Pipe Layout Preferences, routing solutions).
7. Modify the layout. 8. Generate construction documents (annotate while placing objects).

Auto layout ([G:AFC86914](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AFC86914-6495-41E7-9307-766EC241D3B5)):
- In a new run you pick points; pipes, fittings and transitions come from the CURRENT routing preference.
- Works with compass angle entry, tracking lines and object snaps. The angles stored in the elbow content set the angles auto layout can use.
- Gravity systems: builds sloped solutions from picked points and decides whether to insert a transition.

Constrained layout ([G:D69BAA6F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D69BAA6F-F571-47B7-AB6E-7A39EF894F87), [G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)):
- Connects one pipe object to another, sloped (gravity) or not (pressure), even at different elevations. Horizontal routing solutions are supported between objects at different elevations.
- New vertical segments stay vertical to the current UCS.
- Slope readout shows in constrained layouts (pipe between 2 existing pipe objects) and unconstrained ones (object to a point in space). A segment may take a slope other than the palette value from the chosen solution.

Routing solutions ([G:0AC20AE4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC20AE4-5F17-403D-A5B4-A3A4ACC7F11D), [G:19940180](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-19940180-3350-44C8-9FFB-9174B0509926)):
- Generated when you connect objects at different elevations or slopes, or with misaligned centerlines. Each solution is a different fitting/joint combo from the current routing preference; angles come from the allowable angles of the selected elbow.
- Tip: preview in 2 viewports (plan + isometric); 3D Orbit works while previewing. If none fit, take the closest and fix with grips.
- Steps: start a segment from the first object; move straight to the second object until a pipe end connector or pipe curve connector shows; click it (a size or preference mismatch may ask you to choose a part).
- [AUTO] Prompt: `n` Enter next, `p` Enter previous, `a` Enter accept the one previewed, or the solution number then `Accept`. The run updates.
- Example: chiller connection at another elevation and not in line: select the last segment, click the Add grip on its open end, move to the chiller connection, click the pipe end connector; 2 solutions appear.

Connect a pipe run to an MvPart ([G:FDC6BB50](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FDC6BB50-907D-476B-81F8-32FBC72C1348)):
1. Start the run. 2. Near the MvPart (example chiller) turn on Object Snap Tracking on the status bar to line up with the connection. 3. Hover the MvPart connection until the pipe end connector shows; click it. You may be asked to accept or undo.
- Centerlines not aligned: routing solutions are offered.
- Pipe size differs from the connection: a transition is inserted automatically; accept it. If the routing preference has no transition, the Choose a Part dialog asks for one [GUI].
- Connection type differs: Choose a Part dialog asks for the fittings [GUI].
- Fitting in the catalog but not in the preference: set it on the Properties palette and insert it at the end of the run (Overriding a Default Part); you may need to move it to reach the MvPart.
- Horizontal into a vertical pipe: hover the vertical segment until a pipe curve connector shows, click it; use a side or iso view if it fails ([G:B4028733](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4028733-EBF6-418B-8CDB-B5739846D07C)).

Pipe parts catalog ([G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7), [G:18346E9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-18346E9D-8EC7-45E2-B97D-35239E7F0973)):
- Part types: Connector, Coupling, Cross, Elbow, Endcap, Offset wye (lateral), P-Trap, Takeoff, Tee, Transition, Wye, Undefined.
- US Imperial and US Metric profiles: organized by material (Cast iron, Copper, Ductile iron, Plastic, Steel); fittings grouped by connection type (for example threaded).
- Global profile: organized by type and outside diameter: Commercial pipe (steel, also plastic such as PVC), Ductile iron, a copper-tubing entry (heading missing in the source text), Placeholder. Fittings classified by part type, connection type and pressure rating (example: class 3000 socket weld coupling).
- Pipe MvParts catalog sits under the Mechanical chapter.
- Part catalogs (imperial and metric): Cable Tray, Conduit, Duct, MvParts (all disciplines), Pipe. Style-based extras: electrical devices and panels, plumbing fittings and valves, schematic symbols.

## 4.6 Pipe connections, joints, engagement length and cut length

What gets added at a joint, by connection type ([G:1EBC5DC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1EBC5DC2-D2AE-4D5F-97A2-D8A84888577A)):

| Connection type | Fitting to pipe | Pipe to pipe | Fitting to fitting |
|---|---|---|---|
| Flanged (all) | fitting has its flange; a separate flange is added to the pipe | a separate flange on each pipe end | direct, no extra flanges |
| Threaded, Socket weld, Glued, Brazed | pipe (inherent male end) goes into the female fitting | a female coupling is inserted | direct |
| Grooved | coupling added | coupling added | coupling added |
| Butt weld | nothing added | nothing added | nothing added |

- Connection types are assigned in the Connector Properties dialog when building fittings in Content Builder, then appear on the Connection Assignments tab of Pipe Layout Preferences ([G:1EBC5DC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1EBC5DC2-D2AE-4D5F-97A2-D8A84888577A)). Open Pipe Layout Preferences with the Preferences button during a run ([G:68D9D62C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-68D9D62C-1FC7-4960-B636-79C8CA5C9F9B)).
- Same Connection type: on a pipe object attached to a hub, connector 1 inherits the connection type of connector 2 of that hub ([G:1EBC5DC2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1EBC5DC2-D2AE-4D5F-97A2-D8A84888577A)).

Connectors and inheritance ([G:8837917F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8837917F-72AD-4718-B51C-0ADF5072994A), [G:69B70DE1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-69B70DE1-7A26-4D04-B910-8D850B1D40A3)):
- Connectors sit at each end of segments and fittings. Exception: grooved couplings keep their connectors INSIDE the coupling at CEL depth, so cut length with grooved joints is reported differently.
- MvPart and fitting connectors carry a connection type (base-mounted pump = flange; threaded coupling = threaded).
- Pipe SEGMENTS have no connection type; each end inherits it from the connected fitting (a socket weld coupling makes that end socket weld). Example: segment and a male elbow both inherit grooved from a female grooved coupling, as the preference specifies.

Joints ([G:D9B8A7EA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D9B8A7EA-D140-4F65-BCA9-1F9F231708F7), [G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7), [G:3709FC34](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3709FC34-7650-42CE-BCBD-5AFA4C534181)):
- Joints are separate objects. A flanged segment = 3 objects (1 pipe + 2 flanges). All connectors and joints can be counted and scheduled.
- Added while drawing per the Routing Options on the Pipe Properties palette. You can change a joint's connection type or move it along the run.
- In the catalog, joints are fittings in the couplings directory and the asymmetric connectors directory (socket weld flange: socket side for pipe, flange face for the neighbor).

Connector engagement length, CEL ([G:287DD32A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-287DD32A-C717-48D9-8245-536B73021BAE), [G:7CCE5361](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CCE5361-D654-4301-837D-909B31B7AF0C)):
- Every catalog fitting has CELn values = length of pipe that goes into the connection, per industry standards. The drawing shows pipe meeting the fitting end; CEL corrects length and joint location for the real insertion.
- Content Builder custom parts: set CEL to the real connector depth and AoD to the maker's tolerance.

Joint direction ([G:7CCE5361](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7CCE5361-D654-4301-837D-909B31B7AF0C), [G:97BD674B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97BD674B-B0D1-4020-A65D-27EC5D371C92)):
- Pipe Properties palette > Joint direction. Male into female = male drawn first, female after the joint. The software can reverse the orientation on a run when needed.

Pipe length vs cut length ([G:40FA7E16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-40FA7E16-3EB6-42B0-8405-CAE981F8F4DC)):
- Cut length = real pipe length including engagement depth = distance between the connectors inside the segment, based on CEL. It differs from pipe length.
- Adding a flange joint: overall pipe+joint length unchanged; pipe end moves to the flange connector; pipe length drops by the flange width; flange CEL is added to get cut length.
- Adding a coupling: coupling midpoint sits at the old pipe end; pipe end moves to the coupling face.
- Adding an elbow: pipe end stays; pipe length unchanged; cut length grows by the elbow CEL.
- Hub flange couplings: overall length includes the coupling.
- GOTCHA: lengthen grips and dynamic length dimensions do NOT include CEL. With fixed stock length, adding or changing a fitting can change a segment's cut length ([G:40FA7E16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-40FA7E16-3EB6-42B0-8405-CAE981F8F4DC), [G:78F05619](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78F05619-64FA-4D21-B218-0FAD9CB438C6)).

Cut length setting ([G:369D2D94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-369D2D94-DBD9-4ABF-BC94-1CBA5CD22678)):
- Properties palette > Dimensions > Cut length = Yes, then enter the length. With 10 ft stock, straight runs break into 10 ft pieces as drawn, a coupling at each break, still one system.
- GOTCHA: the value applies to ALL pipe system definitions. For different stock per system, change it before drawing each system. Segments can also be broken or merged later.

Other connection tools:
- [AUTO] AECBBASICCONNECTOREDIT: Pipe Connection Point Editor: Pipe Units (Metric or Imperial), Pipe Size, End Type. Related task: To Override a Fitting ([G:494AB729](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-494AB729-410F-481D-BF84-8FFF50B7D396)).
- Pipe snaps: pipe end connector (connect at a segment end); pipe curve connector (connect anywhere along a segment) ([G:C14F32A4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C14F32A4-9493-42A1-908B-7520C27394A8)).

## 4.7 Pipe grips and associative movement

- Grips add or modify pipe objects and MvParts directly. Every grip that applies shows when the object is selected. Kinds: Add, Location, Elevation, Flip and Rotate, Lengthen ([G:8BF13D8A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8BF13D8A-F40E-4D24-AB9A-8DB977ED2F07), [G:86A1419D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-86A1419D-6839-4F0D-A939-4412D16B5F60), [G:928EC9ED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-928EC9ED-6C78-4602-AEEC-25565CB284E4)).
- [AUTO] Grips are interactive. A script cannot click a grip; use these facts to predict what grip edits do, or to choose a non-grip route (Properties palette, MOVE) (inference).

Add grips ([G:928EC9ED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-928EC9ED-6C78-4602-AEEC-25565CB284E4)):
- On segments, fittings and MvParts. They add pipe while keeping the run connected (example: pipe straight off a pump in iso).
- An add grip on an elbow turns the elbow into a tee automatically as you draw the branch; existing branches stay connected.

Location grips ([G:548847B7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-548847B7-C1E5-4AB8-AB6B-5C1CDA02278D), [G:8AFBE73A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AFBE73A-7535-4B74-98BA-2D0DAB749668), [G:FCF459BE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FCF459BE-6FA2-4D5E-9855-2012EF242509), [G:98A0F223](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-98A0F223-B56E-4E63-8E14-2CF2B93D6AEF)):
- Move MvParts, fittings or segments in the CURRENT XY plane while keeping the run connected (associative movement). Grips sit on insertion and connector points.
- Moving an MvPart (example pump): attached pipes and fittings follow; everything else stays.
- Moving a segment: attached fittings follow; elbows move and the pipes beyond them change length; the rest stays; the system stays connected.
- Steps: select; click a location grip; if connected choose: no key = keep connection, adjust only fittings and segments, MvParts stay; Ctrl once = adjust all objects including MvParts; Ctrl twice = break connectivity.
- New location: relative = move toward the spot, type X, Enter; Tab to Y, type, Enter. Or drag and click with object snaps, toolset snaps, tracking.
- [AUTO] Dimension fields need Dynamic Input AND Dimension Input on (default); else drag and click or type coordinates.

Elevation grips ([G:774CA8F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-774CA8F1-DE69-4097-90E3-9679B9DA7460), [G:9ADD3D9D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9ADD3D9D-4496-4A73-90A3-4B102E13174F)):
- Change elevation relative to top, centerline or bottom of a segment, in model view.
- NOT available on flexible or sloped segments. Flexible pipe: change the start point elevation on the Properties palette. Sloped pipe: change the elevations of the connected fittings.
- Steps: go to a side or iso view; select; pick the elevation grip; same Ctrl choice as location grips; then Tab to the right field and type the overall elevation (relative to a point on the part such as the centerline), or drag, Tab to the relative-dimension field and type it; Enter.
- Example use: raise a segment to free valve hand wheels; connected objects adjust and stay connected.

Flip and rotate grips ([G:AD9FB96F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AD9FB96F-12B3-49D6-992B-1F5A840E3467)):
- Arrow flip grips turn in-line parts, fittings and takeoffs 180 or 90 degrees in the arrow direction (3-way valve 90 degrees in plan). Shown only on parts with connectors on opposite ends.
- In iso views, diamond rotate grips turn the object about its centerline to any angle.
- To protect connectivity the software limits options or hides grips (a wye with a connected branch cannot rotate). Connected objects adjust (small length changes); if they cannot, they disconnect.

Lengthen grips ([G:78F05619](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-78F05619-64FA-4D21-B218-0FAD9CB438C6)):
- Change length at the current angle. On a connected end you choose whether connectivity is kept.
- An UNCONNECTED segment: Start grip and End grip move the start or end XYZ, so length and angle both change. Good for tying a new segment into an existing run.
- The dynamic dimension shows pipe length, which may not equal cut length.

Flexible pipe location grip ([G:2CCFA1A7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2CCFA1A7-189D-4953-B9FE-E0BAF037ED13)):
- Any segment mode (line, arc, spline). Drag the location grip to move control points. After clicking it: Ctrl once = keep the MvPart connection; Ctrl twice = break it.

## 4.8 Pipe display: 1-line, 2-line, graphical 1-line, placeholder parts

Core idea ([G:62483160](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-62483160-700B-401D-ABA4-8DA3BD4E3723)):
- You do NOT declare a system 1-line or 2-line. Draw it once with real parts; parts keep type, size and connection type in every display.
- Displays: 1-line, graphical 1-line, 2-line, single line graphic. All map back to the true 3D location.
- Control = display configuration + system definition. Switch the drawing's display configuration for all 1-line or all 2-line. For a mix by nominal size, use the system definition with the matching display configuration.
- One drawing can mix graphical 1-line, 1-line and 2-line.
- Plot guidance from the page: large diameter = scaled 2-line; medium = scaled 1-line; small = graphical 1-line.
- 1-line is NOT a schematic display: it still shows true geometry and location and keeps size and system. 1-line and 2-line both work in iso views.
- Related help topics: To Configure System Definitions for 1-Line, 2-Line, or Single Line Graphics; To Configure Graphics for Single Line Pipe Display.

Display configurations ([G:D422E350](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D422E350-208A-4887-8F96-DC4FEC2E0D15)):
- Display representations set how an object looks per view; a display configuration groups them for a task (1-line vs 2-line; discipline views that color mechanical systems and screen the rest).
- Change: click the current display configuration name on the status bar and pick one. The Aecb Model template lists its default configurations. Example configuration named: Mechanical - Pipe by Size (Top view) ([G:1BC9DCA0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1BC9DCA0-A661-4107-A0BA-95710F46F7D8)).

The three looks:
- 1-line ([G:8D92AE3D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D92AE3D-750D-4D65-A91F-6748652291E5)): for construction documents. Fittings draw at actual envelope size (tees, elbows, reducers); in-line and anchored components (valves) draw scaled 1-line; MvParts (pump) draw scaled 2-line.
- 2-line ([G:F8B86C88](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F8B86C88-EAB4-4B6E-8856-FC738A9E9141)): scaled 2D (3D in iso); fittings and equipment follow real contours. Typical for large lines, space reservation, interference checks.
- Graphical 1-line ([G:1B4DDD6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B4DDD6A-DCF8-4375-B562-E14CBB872A54)): generalized routing with NON-scaled components; equipment as schematic symbols; symbol size relates to model location, not real dimensions. Symbols plot at a specified size, so small fittings stay readable on large plots. Components are unchanged and can switch to scaled 1-line or 2-line.
- CONFLICT on the same page ([G:1B4DDD6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B4DDD6A-DCF8-4375-B562-E14CBB872A54)): one sentence says graphical 1-line "does not show a fitting or joint type"; the example says connection types (threaded gas, soldered hot water) "are indicated on the fittings". Both sentences are on the page.

Placeholder parts ([G:D6FEC85D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D6FEC85D-75AC-4326-8CE9-73122BF53D60), [G:EF2DDD53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EF2DDD53-8BE1-4533-9912-252EE0174CC7)):
- 1-line, dimensionless parts for preliminary runs. Inserted like any pipe type; convert later (commercial steel, copper tubing) by changing the part subtype (To Modify the Routing Preference and Nominal Size; To Modify a Pipe Fitting).
- Needs a routing preference that uses the placeholder parts. The default Aecb Model template already has one.

Straight centerline display of elbows ([G:9D5D60B5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D5D60B5-148A-4489-83B3-7BF1BCD1969E)):
- Shows where an elbow's centerlines intersect (fabrication and process piping practice). Default follows the curve, in all orthographic and model views, based on connectors 1 and 2.
- Can be set and stored in a drawing in the Piping, Electrical or HVAC domain. Task page To Configure the Straight Centerline Display of Elbows is not in these inputs.

## 4.9 Plumbing line and fitting styles (2D)

Plumbing design workflow, in order ([G:73E66BE7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73E66BE7-F5E4-4A56-94D8-546B75CE410A); the Plumbing Systems Overview page [G:2B6F87F4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2B6F87F4-A2AB-4CB0-AC8D-2C5243F7060C) is only an index):
1. Configure system settings (drawing preferences, plumbing system settings). 2. Set up a project (templates, tool catalogs, Drawing Management Projects). 3. Set up pipe sizing: fixture unit table plus plumbing line sizing table. 4. Open a drawing; xref the architectural plan with Project Navigator. 5. Add pumps, water heaters, drains, showers, sinks, other equipment. 6. Connect with plumbing lines. 7. Size the lines (supply or sanitary). 8. Modify, recalculate as needed. 9. Draw a 1-line plumbing isometric with the schematic tools for code officers. 10. Label the system (annotation drives schedules and documents).

Line styles ([G:FC170703](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FC170703-22AE-4A72-BD23-049C40542588), [G:595EF736](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595EF736-646D-4717-AE17-BDCB5986A8BB)):
- Commands tagged: PLUMBINGLINESTYLE, PLUMBINGLINESTYLEEDIT.
- A line style sets: crossing display in plan, the nominal sizes offered, display properties. Built on material size/type/gauge (examples: Schedule 40 Carbon Steel, Copper Tube).
- GOTCHA: the plumbing module cannot tell horizontal branches from main runs, or horizontal offsets from horizontal branches. Make separate line styles for horizontal branches and for horizontal offsets (example name: Black Pipe - Horizontal Offset) and pick them when adding lines ([G:FC170703](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FC170703-22AE-4A72-BD23-049C40542588), [G:07F74802](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F74802-F400-44BA-BC80-02453E055FCD)).
- Open [GUI]: Plumbing workspace > Manage tab > Style & Display panel > Style Manager drop-down > Plumbing Line Styles. Or select a line > Plumbing Line tab > General panel > Edit System Style drop-down > Edit Plumbing Line Style ([G:F7B32454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7B32454-C651-4A0F-B627-37B110DD955E), [G:A6C2E76A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6C2E76A-D4C1-4195-BDDE-5D0463365E16)).

Crossing annotation (Annotation tab > Crossings) ([G:F7B32454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7B32454-C651-4A0F-B627-37B110DD955E)):
- Choices: as is, overlap, break. For overlap or break enter the PAPER width of the gap or overlap.
- Different elevations: the HIGHER line's crossing style wins. Same elevation: the line drawn SECOND decides.
- Equal priority: overlap + overlap = line drawn second shows the overlap; break + break = line drawn first shows the break; mixed = the line drawn second decides (overlap: it shows the overlap; break: the first line shows the break).
- Change draw order: Home tab > Modify panel > Draworder drop-down > Send To Back.

Standard sizes tab ([G:A6C2E76A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6C2E76A-D4C1-4195-BDDE-5D0463365E16)):
- The nominal sizes offered on the Properties palette come from this tab. New Size button, type, Enter; double-click a size to edit; select and Remove Size to delete.

Fitting styles ([G:A1E9478A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1E9478A-FF15-44BA-AE0D-F6446AD722B8), [G:5F1FAEF7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5F1FAEF7-C76B-48BD-86E0-B9B430A63CBD), [G:C72C7E0C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C72C7E0C-ECBD-45BF-B998-0F272D92EFDC)):
- Commands tagged: PLUMBINGFITTINGSTYLE, PLUMBINGFITTINGSTYLEEDIT.
- Built from type (tee, cross, trap, check valve) plus subtype (45-degree mitered, 90 degree long-radiused, 3-way). Shipped styles include Cross and Sanitary Tee.
- Set type and subtype [GUI]: Style Manager drop-down > Plumbing Fitting Styles (or select a fitting > Plumbing Fitting tab > General panel > Edit Style drop-down > Edit Style) > Details tab > type, then subtype, OK.

Fitting style connectors ([G:D6901742](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D6901742-2E8E-4DA2-836B-31E59CCB34AF), [G:119B4C46](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-119B4C46-0D93-46A1-B962-52F4DEF0F0C0)):
- Connectors live in the STYLE; editing them hits every instance in the drawing and can break connectivity.
- Connectors tab: Description (example Cold_Water_Supply), Domain (set to pipe), connection point X/Y/Z, connection direction X/Y/Z; add and remove buttons; OK.
- Do not usually use view-block center points as connectors.
- Connectors must be defined in a set order. Connection point value = segment length; direction = +1 or -1 by orientation from 0,0.
- Example, all segments 0.5 long (the source table heads both columns "connection direction"; (inference) the 0.5 set is the point and the 1 set is the direction):
  - Elbow: C1 0,0.5,0 dir 0,1,0; C2 -0.5,0,0 dir -1,0,0.
  - Tee: C1 -0.5,0,0 dir -1,0,0; C2 0.5,0,0 dir 1,0,0; C3 0,0.5,0 dir 0,1,0.
  - Cross: as tee plus C4 0,-0.5,0 dir 0,-1,0.

## 4.10 Drawing plumbing runs

Entry page ([G:88716A09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-88716A09-E138-4617-9C83-09348350001F)) lists the parts of building a plumbing system: adding lines, connecting at different elevations, adding equipment and fixtures, overriding default fittings for a run, adding fittings by hand, expansion loops (plus a video, Creating Plumbing Systems).

Terms ([G:595EF736](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595EF736-646D-4717-AE17-BDCB5986A8BB)): a run = individually drawn plumbing lines carrying gas or fluid between points. A network = all interconnected runs of one system (example: waste from fixtures to the main drain). Set the System on the Properties palette before drawing.

Draw a run ([G:135AAC3A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-135AAC3A-7689-429D-90AE-DAEC991F5DD1), [G:73ADB2A8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73ADB2A8-F095-45AD-8335-0E4FBDAE7241), [G:F54C18B0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F54C18B0-7869-4C96-8C52-50FE6906002A)):
- Start: Plumbing tool palette > Plumbing Line tab tool; or Home tab > Build panel > Plumbing Line; or an add grip on an existing line; or the Styles Browser palette (search, import, add).
- Properties palette Design tab, in order: Style (General), System, Elevation, Nominal Size, Offset (optional distance from the run to other objects), Rise and Run.
- System: pick from the list, or its button opens the Styles Browser to search, import and apply definitions.
- Slope: enter Rise and Run and slope is computed; or enter slope percent and rise and run are computed. Drainage needs a minimum slope everywhere. A slope glyph shows direction and up/down when a slope % is set.
- Start point: the Pipe Connector snap hits a line end or any point on a line. Pick more points; fittings insert automatically; change elevation between points as needed; Enter ends.
- Settings persist until changed. After each segment the palette shows the elevation of the last-drawn segment.
- In plan, an elevation change inserts an elbow-down drop symbol. An elbow-up fitting can be added by hand at a line end ([G:73ADB2A8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73ADB2A8-F095-45AD-8335-0E4FBDAE7241)).
- If a required fitting cannot fit, plumbing lines are inserted in its place ([G:5F1FAEF7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5F1FAEF7-C76B-48BD-86E0-B9B430A63CBD)).

Start from an add grip ([G:0C0D88BB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0C0D88BB-DC04-4032-8973-C798B4027C16), [G:B748C2BE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B748C2BE-42AC-42F8-9878-509EB9818612)):
- End of a segment: click the add grip at that end.
- Midpoint of a segment: click the midpoint add grip; a tee or takeoff goes in per plumbing layout preferences.
- MvPart: click the add grip on its connection. You MUST pick a system type; from a line or fitting the new run inherits the system.
- Fitting (elbow, tee): hold Ctrl and click the add grip pointing the new direction. An elbow becomes a tee; existing branches stay on the other 2 tee connections.
- Changing nominal size BEFORE the first point inserts a transition automatically.
- Lock Nominal Size prevents accidental size changes while modifying.

Start from equipment or a fixture ([G:2B17ED99](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2B17ED99-B455-4B9F-BE93-A83B6CD49877)):
- Run ends snap to the nearest connection point. A utility sink has 1; tanks and lavatories have several, some in different systems (supply and drain).
- With the Pipe Connector snap on, pick a connector. More than one available = Select Connector dialog [GUI].
- The connector sets the elevation and the default run direction (normally perpendicular to the part).

Connecting at a different elevation ([G:30DCAD62](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-30DCAD62-36B4-4EBE-9197-B365C10EAFD9)). You are prompted to pick one:
- Add a riser to the connecting plumbing line: at an end connector a drop symbol goes in; at a point on the curve the system's Tee Up or Tee Down goes in (chosen by the two elevations).
- Add a riser to the fixture: when connecting from a fixture (MvPart), the riser goes on the fixture.
- Adjust the slope: the line you are drawing takes a slope that absorbs the difference (elbow at an end, tee on a curve).
- Adjust the connecting plumbing line elevation: your line takes the other line's elevation (elbow at an end, tee on a curve).
- Do Not Make a Connection.
- (inference) The page does not give option keywords; treat this prompt as interactive.

Override default fittings for one run ([G:EFA0C51E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EFA0C51E-27C2-4862-82E5-91E221F55C7B)):
- Start a line tool (or Home tab > Build panel > Plumbing Line), then Properties > Design tab > Default Fitting Overrides > click the fitting type; in the Select a Style dialog pick Tee, Tee Up, Tee Down, Cross or Transition (no elbow entry), then the style. Draw, Enter.
- When the command ends the system definition defaults return. For one unique fitting, add it by hand instead.

Expansion loop ([G:367A7BF0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-367A7BF0-FA2B-44EE-8A35-9BDF4D023012)):
- For long hot water runs. Select a segment > Plumbing Line tab > Modify panel > Add Expansion Loop.
- [AUTO] Prompts in order: start point of the loop; second point; distance away from the run; side of the run.
- Added after sizing = resize the run.

## 4.11 Modifying plumbing runs and plumbing grips

Overview ([G:9D7DFD3D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9D7DFD3D-42A5-4C26-8D41-6C6DEBC034BF), [G:C131F93E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C131F93E-141C-4AAC-9C34-47EE990CE40D), [G:0AC2E1D9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC2E1D9-B25E-43B4-927D-C469C75EA86D), [G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9)):
- Commands tagged: PLUMBINGLINEMODIFY, PLUMBINGFITTINGMODIFY (Properties palette edits). Tools: grips and the slope tool.
- Plumbing Line contextual tab: Insert Fitting, Modify Plumbing Line, Add Expansion Loop, Merge Plumbing Line, Size Plumbing Line, Show Objects for Sizing, Reverse Flow. Plumbing Fitting tab: Show Connected Objects.
- Custom Display (OBJECTGRAPHICSEDIT) does NOT work on plumbing lines and fittings ([G:2A688CDE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2A688CDE-FB9A-4DB1-814C-9FBB9CDDB464)).

Change style ([G:A1E9478A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1E9478A-FF15-44BA-AE0D-F6446AD722B8)):
- Select, Home tab > Build panel > Tools drop-down > Properties > Design tab > Style.
- Line: pick from the drop-down, or Plumbing Line tab > Modify panel > Modify Plumbing Line.
- Fitting: click the Style image; the Styles Browser palette opens (search, import, apply). The Styles Browser appears only for fitting styles, not line styles.

Change system ([G:26A610D4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-26A610D4-F534-42C4-BC69-1840C0D1086F)):
- Properties > Design tab > System (Styles Browser), or Modify Plumbing Lines dialog. Changes ALL components validly connected to the selected segment or fitting.

Slope tool ([G:B999730B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B999730B-1CBF-4A96-B108-2B8499715BB2)):
- Select the segment > Analyze tab > Plumbing panel > Slope Plumbing. Green dot = start, red dot = end.
- Plumbing Line Slope dialog [GUI]: Select Start Point of Run / Select End Point of Run buttons redefine the ends. Calculation list: Start Elevation (enter end elevation and slope), End Elevation (enter start elevation and slope), Slope (enter both elevations). Press Tab to calculate, then OK.
- The page says enter at least one value; its table shows each solve needs the other two.
- Does NOT change the slope or elevation of connected branch lines or MvParts; they stay connected.

Elevation ([G:673678A6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-673678A6-7871-4846-A8D9-261A8B9FA9A6)):
- Command tagged: PLUMBINGLINEINVERTELEVATION. Properties > Design tab > Placement > Elevation; under Slope set Rise, Run, Slope (%). Or the Modify Plumbing Line dialog.
- RISK: can break connections and can change the elevation of connected objects on the same level. Check with View tab > MEP View panel > Solution Tips. Repair by adding connecting segments, changing elevations, or moving or lengthening parts.

Location by coordinates ([G:8BE9EBF0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8BE9EBF0-12E2-42D9-AD18-4E6E39DEA930)):
- Location grips are preferred. Palette route: Design tab > Placement > Elevation > Additional Information button > Location dialog: Insertion Point X/Y/Z; Normal = 1 on the normal axis, 0 on the others.
- GOTCHA: editing coordinates this way DISCONNECTS the line from its runs.

Nominal size ([G:EFC3EA56](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EFC3EA56-822C-4184-AECD-D2BAA2CB2A4D)):
- Properties > Design tab > Dimensions > Nominal Size, or Modify Plumbing Line. The line style sets the list.
- Nominal Size lock: list inactive; length and elevation can still change. Unlock on the palette.
- GOTCHA: lines are 2D, size is for calculation only, and changing size does NOT insert the needed fitting.

Move ([G:1C6430E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C6430E8-E2C6-40EA-B3DC-9534821188F9), [G:BFBBDB01](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BFBBDB01-2C6D-481A-8670-8037F4C5D864), [G:DF41AF89](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF41AF89-2338-41E2-8E69-A0752DEAE0C4), [G:D2EA6C1C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D2EA6C1C-8A58-43E4-BE6F-5165EA0963CD)):
- Select, click the Location grip, choose: no key = adjust only fittings and segments (MvParts stay); Ctrl once = adjust all including MvParts; Ctrl twice = break.
- New location: type X offset, Tab, type Y offset; or click a point (object snaps, toolset snaps, tracking).
- Segment move: connected fittings follow, adjacent elbows move and the lines on them change length, the rest stays. MvPart move (example a toilet): its lines and fittings follow; the rest stays.

Reverse flow ([G:84894822](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-84894822-2D93-4079-B683-64AF89132735)):
- Command tagged: PLUMBINGLINEREVERSEFLOW. Select a segment > Plumbing Line tab > Calculation panel > Reverse Flow.
- Invisible unless flow arrows are applied; the sweep on sanitary tees shows it. Does NOT propagate to connected objects. Done after sizing = resize.

Plumbing grips ([G:A10F5A78](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A10F5A78-73ED-49C3-87E9-0793C0FA74C0), [G:863E7E92](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-863E7E92-E270-4034-888B-B5AD1F6188C0), [G:B748C2BE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B748C2BE-42AC-42F8-9878-509EB9818612), [G:D85C0777](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D85C0777-FF55-48DA-935C-46D546151071), [G:82FA2F31](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-82FA2F31-001B-45BD-A81C-1D3C46F18EA4), [G:E5F553FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5F553FC-9A34-4268-A7F4-BA8DC986E7CA)):
- Kinds: add, location, lengthen, rotate (rotate and flip). Applicable grips show on selection.
- Add grips: on segments, fittings and MvParts (example a sink). See 4.10.
- Lengthen: keeps the current angle; a connected end asks whether to keep connectivity (example: vent lengthened to miss a duct).
- Location: moves in the current XY plane; grips at insertion and connector points. Unconnected segment: Start and End grips change length and angle. Connected: you choose connectivity.
- Rotate: turns in-line parts, fittings and takeoffs 180 or 90 degrees in the grip direction; shown only with connectors on opposite ends; may be limited or hidden to protect connectivity; connected objects adjust or disconnect. The same page also says "the rotate grip turns a part 180 degrees" and "the flip grip orients a part (in-line or anchored MvParts, fittings, or takeoffs) for flow direction" ([G:E5F553FC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5F553FC-9A34-4268-A7F4-BA8DC986E7CA)).

## 4.12 Fixtures, fixture unit tables and sizing tables

Fixtures and equipment are catalog MvParts ([G:07F8CEF9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F8CEF9-6BA9-4E1E-A2E3-71682E03DA85)):
- Added through the Add Multi-view Parts dialog [GUI]; for a fixture you choose the fixture unit table and fixture type there ([G:3EDC2C43](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3EDC2C43-52FA-4C85-9C87-1D8CF495A248)). Ribbon route shown on the radiator page: Home tab > Build panel > Equipment drop-down > Equipment ([G:B16A4B0F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B16A4B0F-DB9C-4D52-A282-EBA45B8F26DF)).

Fixture unit tables ([G:3EDC2C43](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3EDC2C43-52FA-4C85-9C87-1D8CF495A248), [G:B01A0433](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B01A0433-E985-42CD-82B9-2599730CED77)):
- Command tagged: FIXTUREUNITTABLESTYLE. Built in Style Manager on the Table tab.
- Give fixture units by fixture type and occupancy type, for cold water, hot water and sanitary waste.
- On add or modify, the toolset puts a default fixture unit value on each fixture CONNECTOR, from the connector's system type and the table values. Values are editable.
- Copy to another drawing [GUI]: open both, Plumbing workspace > Manage > Style & Display > Style Manager; right-click the table under the source drawing > Copy; under the target select "Fixture Unit Table Definitions" > right-click > Paste.

Default fixture unit matching ([G:AA5D861C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA5D861C-2B58-4774-9975-2EB42C1A3053)):
1. Rows matching the fixture TYPE. 2. Within those, the row matching the fixture SUBTYPE. 3. No exact row: the row matching keywords in the subtype name.
- No match = NO default values are assigned. Build tables that match your fixtures.
- A sample table based on industry standards ships. Make your own per local code (example named: Uniform Plumbing Code). Pick and check tables BEFORE sizing.

Fixture properties dialog ([G:F18C2F09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F18C2F09-2DDB-4DB9-99DE-CC0C3E5C8FFB), [G:0F6EB09C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0F6EB09C-9E99-46AC-8B07-B02D19E38EA8)) [GUI]:
- Select a fixture > Equipment tab > Modify panel > Equipment Properties > Multi-view Part Properties dialog.
- Calculations tab (read-only, filled only after the connected line is sized): per connector, flow rate and pressure, each with a minimum (needed) and calculated (actual) value; connector system type.
- Fixture Units tab: fixture unit table, fixture type, occupancy type (public or private), connector info.

Sizing tables ([G:8416BAB1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8416BAB1-1AB2-4DD5-8086-732B40F58668), [G:E5900776](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5900776-DE47-43DC-93D3-EFF7F5126545)):
- Commands tagged: SUPPLYPIPESIZINGTABLEDEF, SANPIPESIZINGTABLEDEF.
- SUPPLY tables: equivalent plumbing line lengths for fittings and valves. SANITARY tables: maximum permissible fixture unit loads for stacks, branches and offsets.
- Sample tables ship; build your own from code. Sizing accuracy depends on the table; verify BEFORE sizing.
- Create [GUI]: Style Manager > Plumbing Objects > the sizing table kind; right-click "Standard" > Copy; right-click the matching "Sizing Table Definitions" item (Supply Pipe or Sanitary Pipe) > Paste; rename "Standard (2)".
- General tab: name, description, Notes button.
- Supply table: Equivalent Plumbing Line Lengths tab (New Row, Remove Row, New Column, Modify Column, Remove Column).
- Sanitary table: Stacks, Branches, Offsets tabs (New, Remove).

## 4.13 Sanitary sizing

Before you start ([G:77966834](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-77966834-AC37-43E0-8CE0-45DF0C6AE4DC), [G:07F74802](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F74802-F400-44BA-BC80-02453E055FCD), [G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41)):
- Finish a draft of the system. Verify the fixture unit table. Create or verify a sanitary sizing table built from the governing code (example: Uniform Plumbing Code).
- ONLY System Type = Waste can be sized. Gray water and black water definitions must be set to Waste. Storm Drain cannot be sized.
- "Danger" on the page: ANY change to the sanitary system after sizing means the lines must be resized.
- Commands tagged: PLUMBINGLINESIZE, PLUMBINGLINESIZESANITARY.

Steps ([G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41)):
1. Finish the draft.
2. Select a run whose system type is Waste. Every line, fitting and fixture connected to and downstream of it highlights.
3. [GUI] Plumbing Line tab > Calculation panel > Size Plumbing Line. The Size Sanitary Plumbing Line dialog opens.
   - [AUTO] Calculator only, no resize: Analyze tab > Plumbing panel > Size Plumbing, then press Enter at the command prompt. No option keywords are documented.
4. Design Values: pick the plumbing line sizing table definition made from your code. The Plumbing Line Sizing Table icon opens it for checking.
5. Base Sizing On: pick the run type (below). Results show in the non-editable lower sections.
6. OK resizes the system.

Run types and the table tab each reads ([G:07F74802](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F74802-F400-44BA-BC80-02453E055FCD), [G:F3D97C48](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F3D97C48-A836-4546-A9E2-A14403A49EA0), [G:16176569](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16176569-B85C-42CD-B1B9-5C76F471363C), [G:67E1ED32](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-67E1ED32-CAE2-4FFA-9739-EEF48FA5F100)):

| Base Sizing On | Reads table tab |
|---|---|
| Branch | Branches |
| Offset/Home Drains | Offsets |
| Stack Spanning 3 Stories or Less | Stacks |
| Stack Spanning More than 3 Stories | Stacks |

- The software does NOT tell a horizontal offset from a horizontal branch. Use a separate line style for horizontal offsets (example: Black Pipe - Horizontal Offset) and pick it when adding the line.

Reading the results ([G:B0BCDAB2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B0BCDAB2-7F45-4975-BAFF-A137E930E19D)):
- Branch: "Fixture Units Upstream" = all connected fixtures, ASSUMING they are all in the current drawing. Then "Size of Branch".
- Offset/home drain: "Fixture Units from Upstream Stack" = connected fixtures in this drawing. Type the floor-above total into "Fixture Units from Branches Connecting Outside of this Drawing". Then "Size of Plumbing Line" is calculated and "Slope of Plumbing Line" is shown.
- Stack: "Fixture Units from Branches Connecting in this Drawing" = connected fixtures in this drawing. Multi-story: size floor by floor going DOWN; on each floor type the floor above's "Fixture Units from Branches Connecting in this Drawing" into "Fixture Units from Branches Connecting Outside of this Drawing".
- Save each floor of the sanitary system as its OWN drawing and calculate it separately.

Three-story example ([G:CA8B0E95](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA8B0E95-36D0-40F4-BDDF-377F67453282), [G:16176569](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-16176569-B85C-42CD-B1B9-5C76F471363C)). Size highest floor first, carry numbers down:
1. Third-floor drawing: select the line closest to the second-floor riser; Base Sizing On = Branch; write down "Fixture Units Upstream".
2. Second-floor drawing: select the line closest to the first-floor riser; Base Sizing On = Offset/Home Drains; type the third-floor "Fixture Units Upstream" into "Fixture Units from Branches Connecting Outside of this Drawing" (Size of Plumbing Line updates); write down "Fixture Units from Upstream Stack".
3. First-floor drawing: select the line nearest the end of the main leaving the building; Base Sizing On = Offset/Home Drains; type third-floor "Fixture Units Upstream" PLUS second-floor "Fixture Units from Upstream Stack" into "Fixture Units from Branches Connecting Outside of this Drawing".
- The example never uses a Stack option; Stack has its own carry-down rule above.

## 4.14 Supply sizing and its math

Before you start ([G:854EE092](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-854EE092-C4BD-49AE-B800-9CD5AB3BB6BB), [G:A7121902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7121902-5331-43FC-B965-024C8CF95E7A)):
- Finish a draft; verify the fixture unit table; create or verify a supply sizing table from the governing code (example: Uniform Plumbing Code).
- ONLY System Type = Hot Water or Cold Water can be sized.
- "Danger": any change after sizing means resize.
- Commands tagged: PLUMBINGLINESIZE, PLUMBINGLINESIZESUPPLY.

Steps ([G:A7121902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7121902-5331-43FC-B965-024C8CF95E7A)):
1. Finish the draft.
2. Select a Hot Water or Cold Water run. The pick also sets the point where flow rate, velocity and diameter are reported (example: pick the line nearest the booster pump for source flow) ([G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)).
3. [GUI] Plumbing Line tab > Calculation panel > Size Plumbing Line. Connected and downstream objects highlight; the Size Supply Plumbing Line dialog opens.
   - [AUTO] Calculator only: Analyze tab > Plumbing panel > Size Plumbing, then Enter at the command prompt. No option keywords documented.
4. Design Values:
   - Equivalent Plumbing Line Length for the Valves and Fittings: pick the Plumbing Line Sizing Table made from your code; verify it with the Plumbing Line Sizing Table icon.
   - Appropriate Plumbing Line Size: tick Restrict Velocity and enter the maximum velocity (guards against water hammer).
   - Amount of Water Pressure Coming into the Building: Pressure at Source (example: a booster pump).
   - Minimum Amount of Pressure: Pressure-Highest Fixture (example: a third-floor toilet at 80 ft may need 15 psi to flush).
5. OK resizes. Results sit in the non-editable sections.

The dialog's final results are two sections: Calculations for the Longest Run and Calculations at Selected Component ([G:C8BEE120](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C8BEE120-49A3-4DC7-B6E8-7D6DCAD00FAC)).

Results: Calculations for the Longest Run ([G:5027E609](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5027E609-F871-4138-B1F6-50255E849E43)):
- Command tagged: SHOWOBJECTSLIMITINGRUN (no prompts given).
- The software walks every connected fixture's run, adds equivalent lengths of fittings and valves from the chosen supply table, and takes the HIGHEST as the limiting (longest) run, typically booster pump to the highest fixture.
- Developed Length: longest run including fitting equivalent lengths.
- Elevation Difference: highest minus lowest elevation in the run (example: fixture at 2'-0", main entering at 6", difference 1'-6").
- Pressure Drop = Head Loss + Friction Drop. Head Loss = elevation difference. Friction Drop = Hazen-Williams friction of the limiting run.
- Downstream Fixture Units: sum of required fixture units of all connected fixtures on the selected run.

Results: Calculations at Selected Component ([G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)):
- Flow Rate: estimated with Hunter's Curve (mixed), a probability method. The line is NOT sized on the sum of all fixture flows.
- Actual Velocity: V = Q/A (A from the inside diameter).
- Plumbing Line Diameter: each line is first estimated at 8 ft/s.

The math ([G:D62F7367](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D62F7367-E86A-40B1-AD4D-3F4BD7675F59), [G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)):
- Hazen-Williams terms (formula image not in text): F = friction drop of the longest run per 100 ft (or 100 m); C = inside roughness / friction coefficient, DEFAULT 100; q = total downstream flow, gpm (or L/s); d = inside diameter.
- Total Pressure Drop = Friction Loss + Elevation Change.
- CONFLICT: [G:D62F7367](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D62F7367-E86A-40B1-AD4D-3F4BD7675F59) words the elevation change as "Pressure at Source minus the Highest Fixture value"; [G:5027E609](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5027E609-F871-4138-B1F6-50255E849E43) defines Elevation Difference as highest minus lowest elevation in the run.
- Pressure available for friction is built from Pressure at Source, Pressure at the Highest Fixture, Pressure Drop and Friction Loss-Water Meter. Both pages word the subtraction loosely; the exact sign order is NOT verified ([G:D62F7367](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D62F7367-E86A-40B1-AD4D-3F4BD7675F59), [G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)).
- Too little available pressure: EVERY component in the run goes up ONE line size and the drop is recalculated. The pages do not say how many passes run.
- Restrict Velocity on and actual velocity over the limit: up one size, recalculate ([G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)).
- After sizing, the nominal size is looked up from the calculated inside diameter, rounded UP to the next standard size.

Standard ID table used for ALL supply sizing (Schedule 40 steel), nominal in > ID in ([G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)):
0.125 > 0.269; 0.25 > 0.364; 0.375 > 0.493; 0.5 > 0.622; 0.75 > 0.824; 1 > 1.049; 1.25 > 1.380; 1.5 > 1.610; 2 > 2.067; 2.5 > 2.469; 3 > 3.068; 3.5 > 3.548; 4 > 4.026; 5 > 5.047; 6 > 6.065; 8 > 7.981; 10 > 10.02; 12 > 12.000; 14 > 13.250; 16 > 15.250; 18 > 17.250; 20 > 19.250; 22 > 21.250; 24 > 23.250; 26 > 25.250; 28 > 27.250; 30 > 29.250; 32 > 31.250; 34 > 33.250; 36 > 35.250.
- GOTCHA: the page says all sized lines are assumed to have Sch 40 steel inside diameters ([G:85782791](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-85782791-3D5A-41E6-B2BF-BFF5EC405C8B)). (inference) That would apply to copper line styles too.

## 4.15 Radiant heating: radiators, BDH and XML import, parallel pipes

Radiant heating uses Pipe objects (parallel supply and return pipes, branch pipes) and radiator MvParts with valve MvParts ([G:EDEE52B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EDEE52B1-2897-4FC5-A936-95E071B66053), [G:E6243F05](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6243F05-2C4E-4FEC-9169-10FFFA8210D3), [G:E14E1541](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E14E1541-68AC-40C9-9F25-32E7C57166A3)).

Workflow, in order ([G:EDEE52B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EDEE52B1-2897-4FC5-A936-95E071B66053)):
1. Set up the project (tool catalogs, project info). 2. Import radiator data files (BDH). 3. Place radiators using windows and walls. 4. Run parallel supply and return pipes. 5. Add radiator valves and branch pipes. 6. Copy valves and branches to other radiators (Connect Multiple Parts). 7. Modify radiators as the design changes. 8. Add labels and annotations.
- Radiators can go into selected spaces, at windows, or at picked locations. After connection you can change type, size, elevation and location and keep the connections ([G:83325035](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-83325035-89A0-4C4D-AFF9-39A962393F23)).

Add a radiator MvPart by hand ([G:B16A4B0F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B16A4B0F-DB9C-4D52-A282-EBA45B8F26DF)) [GUI]:
- Piping workspace > Home tab > Build panel > Equipment drop-down > Equipment opens Add Multi-view Parts. Tree: Plumbing - Radiators.
- Part Size Name: pick one, or let the Layout tab calculate the size. Elevation: pick a value. "Display/Hide additional parameters" checkbox. Details button lists sizes of the current radiator.
- Layout tab > Layout Method: Spaces (a radiator at every window of the selected spaces); Windows (at selected windows); Two points (2 points per radiator); Insert point ([AUTO] the command line asks for insertion points).
- Positioning: Justification Center, or Left/Right plus Offset distance; Distance from wall.
- Sizing: Use Width from Window makes the software size the radiator; Subtract Window Width by shrinks it. Height and depth come from the part size.
- Picks: Spaces = pick spaces (drawing or xref); each radiator gets the closest part size smaller than window width minus the Subtract value. Windows = pick windows (drawing or xref), then a point inside the building. Two points = left and right points; size comes from their distance, not the window. Insert point = pick the point. The dialog stays open for more.

Import radiators from a calculation program ([G:B463C0BC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B463C0BC-1CF4-4471-87AE-509EEEE8B0F6)) [GUI]:
- Piping workspace > Insert tab > Import panel > Radiator > Import Radiators dialog. Select file = XML from a heating calc program (example: SOLAR COMPUTER Desktop; the page lists it under commands, but it is the third-party program (inference)).
- The XML holds space IDs, each followed by that space's radiator list. Spaces in the file are matched to spaces in the drawing. If the drawing holds several copies of one xref, only the FIRST copy is used.
- Layout Automatic (Spaces): a radiator under each window, radiator length matched to window width; extra radiators make the software zoom to the space and ask for 2 points each. Manual (Two points): it zooms to each space and asks 2 points per radiator.
- Positioning as above, plus Elevation.
- Missing Radiator Parts dialog (XML names a size that does not exist): Create Custom Parts = parts added to THIS drawing only, not to the MvParts catalog, schedulable, limited editing; "Always create custom parts" suppresses the dialog. Cancel = stop, build the parts in the catalog first, run again.

Calculation-program round trip ([G:EA6554A4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA6554A4-D604-4C41-8786-9736246D21F6)):
1. MEP: export gbXML for the spaces. 2. Calc program: import gbXML. 3. Calc program: import BDH. 4. Calc program: compute type, size and count per space. 5. Calc program: export radiator XML. 6. MEP: import BDH to create part types and sizes (needed only if you will modify radiators later). 7. MEP: import the XML to place radiators.

gbXML export ([G:895CF2B9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-895CF2B9-CD82-4FAA-92A7-08D5CFBA0D7A), [G:A7B0C678](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7B0C678-8890-4F80-9B4C-F47772F76504), [G:93FFE346](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-93FFE346-6B7F-480E-BA6E-67954AE0075A)):
- Spaces model room interiors and are grouped into zones; zones export to Green Building XML.
- gbXML Export dialog [GUI]: File Name; Select Objects (zones); building type and zip code; Start; View Event Log on error. The ribbon location is not given on that page. The application menu export list includes gbXML; the Analyze tab HVAC panel imports DuctXML and gbXML.

Radiator parts from BDH files ([G:175E808C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-175E808C-553D-49CE-A3D0-D4FA95D44E4E)):
- BDH (.dat) data comes from radiator makers, heating-load apps and D A CH market design software: length, width, height, company name, part name.
- REQUIREMENT: the D A CH profile must be chosen on the Profiles tab of the Options dialog.
- [GUI] Open BDH Radiator Content (ribbon location not stated) > Import BDH File: Part Catalog (target MvParts catalog), Select BDH File (.dat). Chapter Name fills with the maker name and the count of parts to create or update. OK.
- Parts land in the MvParts (DEU).apc catalog, Plumbing > Radiator folder, under that chapter name, sorted by the BDH subchapters. Existing radiators are updated.
- Default radiator template (sets the graphic look; editable): `<ProgramData>\Autodesk\MEP <version>\enu\MEPContent\Global\MvParts\Plumbing\Radiators\Radiator Template_gbm.xml`.

Parallel supply and return pipes ([G:EA1558DB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA1558DB-9E56-4CA1-8697-9D53387C8DCF), [G:E6243F05](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E6243F05-2C4E-4FEC-9169-10FFFA8210D3)):
- [AUTO] PARALLELROUTING adds parallel pipes.
- A conflict appears with a small turn or an elevation change while routing pipes of different diameters. A dialog opens [GUI]: Undo (restart from the last segment and give a non-conflicting point or property) or accept the proposed new spacing, which is kept for the rest of the routing. A script blocks here.
- Pipe runs for placed radiators: 1. Add parallel supply and return. 2. Add valves to one typical radiator. 3. Add branch pipes from the valves to supply and return (Connecting to Existing Pipe; Connecting a Pipe Run to an MvPart, see 4.5). 4. Copy to similar radiators with Connect Multiple Parts.

Modify a radiator ([G:5DDF84BF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DDF84BF-B659-414F-AE4A-D314C3CE96D7)):
- Connections to valves and pipes are kept if possible. Branches to the parallel pipes adjust; if they cannot, they disconnect from the main run and move with the radiator.
- Type, size, elevation [GUI]: select radiator(s) > Equipment tab > Modify panel > Modify Equipment > Multi-view Part Modify dialog. Elevation is also on the Properties palette.
- Move: Location grip. Move and connect an unconnected radiator: Alignment grip to a connector.

## 4.16 Radiator valves, alignment grips and Connect Multiple Parts

Valves ([G:E14E1541](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E14E1541-68AC-40C9-9F25-32E7C57166A3), [G:196E169B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-196E169B-37CD-47A1-89CE-D468E25BBB01), [G:BE55F984](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BE55F984-8389-46D1-8F79-2A1287BBBC1F), [G:3CF31AB8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3CF31AB8-91FB-45EC-A7DA-67979472D8E6)):
- Radiator valves are MvParts, mostly handled with grips.
- Add [GUI]: select the radiator; click the Add grip on a radiator connector; in Add Multi-view Parts use the Part and Part Filter tabs for type and size; ENTER adds the valve to the connector; ENTER ends.
- Change type: select the valve > Equipment tab > Modify panel > Modify Equipment (connections kept if possible).
- Arrow Rotate grip = 180 or 90 degrees. Diamond Rotate grip in an iso view = any angle about its centerline.
- Move to another connector on the SAME radiator: pipe connections kept if possible. To a DIFFERENT radiator: pipe connections NOT kept.
- Location grip shows when the valve is connected to the main run (moves it and keeps that connection). Alignment grip shows when it is NOT connected (moves it and aligns it to another connector).

Alignment grip ([G:D3D3D127](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D3D3D127-9181-4686-8391-E2C88BF5DE5D)):
- Connects an MvPart to another object by lining up connectors and setting orientation (example: move a valve to the other side of the radiator).
- Shows on an MvPart connector only when the part can move without disturbing other connections; otherwise use that connector's Location grip.
- Steps: select the valve; click its alignment grip; click another radiator connector.

Connect Multiple Parts ([G:A3C086B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A3C086B1-092D-4B48-A986-30786F684DAF)):
1. Finish valves and branch pipes on the source radiator. 2. Select it. 3. Right-click > Connect Multiple Parts. 4. Select target radiators; Enter.
- If the branch routing preference names no fitting for a connection, the Choose a Part dialog asks [GUI].
- Moved a valve on one radiator? Run Connect Multiple Parts again to update the others.
- Rules: existing valves and branches on each TARGET are REMOVED first; source valves are copied; branches are built with the source branch routing preferences; targets join the same parallel pipes, or the nearest parallel set within a reasonable distance; connectors map lower-left to lower-left, best match if no one-to-one match (some may stay unconnected); system sides are kept (Hot Water Return on the right stays on the right); spacing adjusts to the target distance.

Connection failures ([G:29AE8B67](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-29AE8B67-D330-4FFB-991B-C7C36217B6A5)):
- Valves and branches are copied even when the target cannot connect; connect those by hand. Solution Tips explain failures.
- Causes: radiator not parallel to the mains; too close to the main (no room for branch fittings); on the wrong side or rotated 180 degrees; different type or orientation (single-panel target, two-panel source); no match for all source connectors.

## 4.17 Schematic diagrams: concepts, modes, symbol kinds

What a schematic is ([G:24AA4038](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24AA4038-A82E-4224-9385-96495590CD4B), [G:0F5DF631](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0F5DF631-417C-416B-B4A9-FAC00947ADBD)):
- A 2D, NOT-to-scale flow diagram of a building system's logic and operation: how air, power, hot and cold water move, and how equipment relates. A mechanical schematic can name equipment types and show the connecting duct or pipe. Little data about individual parts.
- Used as the base for the full layout, or for plumbing riser diagrams and details. Usually an early design step (flow and 1-line diagrams before detailed catalog-part design).
- Orthographic (plan) is the common form; isometric is for complex layouts that need more detail.
- Do NOT use a schematic when you need elevations or sections from the drawing, or the duct or plumbing sizing tools. Use real ducts, pipes or plumbing lines for those ([G:24AA4038](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24AA4038-A82E-4224-9385-96495590CD4B)).

How a diagram is built ([G:A614B788](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A614B788-0A64-4F7C-8C1F-6C4701C8AC73), [G:CFEAE09A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFEAE09A-E0CF-4F8F-9908-0F6AFDC46EEF)):
- Symbols connected by schematic lines. Lines draw like AutoCAD lines with MEP snaps and tooltips; symbols insert like AutoCAD entities (insertion point plus rotation angle).
- Unlike plain lines, schematic lines recognize the connection points built into each symbol, so the diagram is connected.
- Two orders both work: place freestanding or end-of-line symbols first and connect later (a pump, then supply and return), or draw lines first and drop in-line symbols into them (a duct heater breaking into a hot air run).
- Systems can be assigned to lines and symbols. New lines and symbols inherit the current system's defaults (layer, color, etc.). Examples: mechanical air supply, electrical power supply, cold water supply ([G:CFEAE09A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFEAE09A-E0CF-4F8F-9908-0F6AFDC46EEF)).
- Contextual tabs: Schematic Line tab has Insert Symbol; Schematic Symbol tab has Show Connected Objects ([G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9)).

Content ([G:EA92ECFA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA92ECFA-AE0E-43A8-8642-7BBFAE8D851C), [G:07F8CEF9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-07F8CEF9-6BA9-4E1E-A2E3-71682E03DA85), [G:C0476A8C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0476A8C-8734-4154-8E59-8C8E4A598FA1)):
- Schematic lines and symbols are style-based: styles are property sets; symbol styles also carry view blocks for the geometry. Make styles by hand in Style Manager.
- Batch routes: decompose the shipped symbol styles into components (settings plus view blocks), edit, convert back; or convert a batch of AutoCAD blocks from your own block library into symbol styles. The Manage tab > MEP Content panel (expanded) batch converts and decomposes drawing components.

Symbol kinds ([G:E5FB9492](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5FB9492-C86B-43FD-8BC7-687D95BE9A6A), [G:1C278882](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C278882-C0B1-4E0E-B510-6FE7E8AD9386), [G:5CF87BE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5CF87BE6-E2B4-48E0-88A8-4F309B060438)):

| | In-line symbols | End-of-line symbols |
|---|---|---|
| Examples | fittings, valves, gauges, controls (switches, signals, devices) | equipment: diffusers, pumps, fans, tanks |
| Placement | anchored anywhere along a schematic line (curve anchor) | usually at a line start or end; place the symbol FIRST, then connect the line |
| Line moves | symbol moves with it | symbol moves with it |
| Symbol moves | slides along the line | the line stretches |
| Line erased | symbol is ERASED too | symbol is NOT erased (erase separately) |

- Symbols sit in categories by type; categories can be added, deleted, renamed. Custom symbols and libraries can match company standards. Style properties set behavior, such as how connecting lines are trimmed ([G:E5FB9492](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5FB9492-C86B-43FD-8BC7-687D95BE9A6A)).

Orthographic vs isometric mode ([G:A16A98A0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A16A98A0-69BD-46F6-97EA-9BDA755A9643), [G:45ABD873](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45ABD873-5492-46AF-9225-D6F23F149E22), [G:BBECF38E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BBECF38E-1B06-44A0-A10E-F745E88E720C), [G:B4573F12](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B4573F12-C01F-4A75-BF84-72970D7CE211)):
- Orthographic: lines and symbols go in the WCS (X horizontal, Y vertical, Z perpendicular). Aids: compass, AutoCAD Ortho (follows the current snap angle or grid and snap settings), grid, snaps; toggle any time.
- Isometric: simulated 3D in 2D. Lines lie on isoplanes; symbols tilt along the iso axes. Isoplane (Properties palette): Left = 90 and 150 degree axes; Top = 30 and 150; Right = 30 and 90. Picking a plane aligns Ortho and the crosshairs; you can switch planes mid-run (top run, left riser, right to finish).
- Isometric is STILL 2D: no 3D distances, nothing shown in other viewports, no automatic hidden-line removal.
- Good for riser diagrams (the page names electrical risers). End-of-line and in-line symbols both work across planes.

Other facts:
- Associative movement: with certain grips, moving a symbol makes attached segments move, shrink or stretch; a segment can move without moving symbols or other segments ([G:7B342F79](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7B342F79-4BFA-4124-878A-4019406CEF3A)).
- Custom Display (OBJECTGRAPHICSEDIT) is NOT available for schematic objects and symbols ([G:2A688CDE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2A688CDE-FB9A-4DB1-814C-9FBB9CDDB464)).
- The Home tab Inquiry panel (distance, area, LIST) shows only in the Schematic and Architecture workspaces ([G:B0E324F0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B0E324F0-FEC2-488E-A109-9BE5BD621961)).

## 4.18 Schematic styles and schematic system definitions

Settings source ([G:B68B1050](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B68B1050-2188-4A10-8F93-F68B943912B1)):
- Schematic settings live in the Style Drawing. Import them into the current drawing, or open the content drawings. Configure before drawing.

Schematic line styles ([G:8556E17E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8556E17E-8BDB-4384-8A3C-A63E65F91C42), [G:2E85994E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2E85994E-D9EE-486A-BC63-A5B61F69AC7D)):
- Commands tagged: SLINESTYLE, SLINESTYLEEDIT (no prompts documented).
- A line style sets crossing display, the connection point symbol, the designation IDs offered, and display. Make separate line styles to tell system types apart.
- Open [GUI] ([G:EE34EB0D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE34EB0D-372D-4969-8B0B-FE04CEAD6560), [G:98B43F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-98B43F6A-5018-4AD2-8D36-B8F38B80E21C)): open the drawing holding the style; Schematic workspace > Manage tab > Style & Display panel > Style Manager drop-down > Schematic Line Styles, pick the style; or select a line using it > Schematic Line tab > General panel > Edit System Style drop-down > Edit Schematic Line Style.

Designations tab ([G:EE34EB0D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE34EB0D-372D-4969-8B0B-FE04CEAD6560)):
- A designation is the text ID on the Properties palette (Advanced > ID). The style supplies the list; users can pick or type another.
- Add: add icon, click the Designation field, type, Enter. Edit: click, edit, Enter. Delete: select row, delete icon.

Annotation tab ([G:98B43F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-98B43F6A-5018-4AD2-8D36-B8F38B80E21C), [G:5478CEC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5478CEC9-2B5C-485D-A293-61821F3C9FD1)):
- Crossings: as is, overlap or break. Overlap or break needs Break/Overlap Paper Width and Break/Overlap Priority (a number).
- Connections: connection node symbol and size for junctions. Start & End Settings: symbol and size for line start and line end.
- Priorities differ: priority decides which line shows the overlap or break.
- Same priority, CONFLICT on the source page ([G:5478CEC9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5478CEC9-2B5C-485D-A293-61821F3C9FD1)): one sentence says the line with the LOWER Z-axis value shows the overlap or break; the table on the same page keys it on draw order: overlap + overlap = line drawn second shows the overlap; break + break = line drawn first shows the break; mixed = the line drawn second decides (overlap: it shows the overlap; break: the first line shows the break). The page does not reconcile them. (inference) Test both on a sample drawing before relying on either.
- Change draw order: right-click the line > Display Order > a command (for example Send to Back).

Schematic system definitions ([G:2F7F184E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F7F184E-0CD2-4E41-9DEF-8D3858924B92), [G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252)):
- Commands tagged: SSYSTEMDEF, SSYSTEMDEFEDIT; the page procedure is Style Manager only [GUI].
- Named for the system (return air, lighting, domestic cold water). Settings drive display; the layer key sets layer, color and linetype. Stored in the drawing; copy between drawings. Default templates ship several to copy or edit.
- Create: Schematic workspace > Manage tab > Style & Display panel > Style Manager drop-down > Schematic System Definitions. New: right-click Schematic System Definitions > New, name, Enter. Copy: right-click a definition > Copy; right-click Schematic System Definitions > Paste; right-click the copy > Rename; Enter. General tab: description. Then the properties common to all disciplines.
- Design Rules tab gives Abbreviation, System Group and Layer Key; System Type exists only on Electrical and Plumbing definitions ([G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252)).

## 4.19 Drawing and converting schematic lines

Add schematic lines with SLINEADD ([G:A831C7DA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A831C7DA-A282-4FC5-B145-E0DF4D68A194), [G:1C2D6A1E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C2D6A1E-6E8E-4325-8EB0-1C9696D2A071)):
- [AUTO] Start in the Schematic workspace: a line tool on a schematic tool palette (scroll if needed), or Home tab > Build panel > Schematic Line, or type `slineadd`.
- Tools carry preset properties, so some properties may be fixed or hidden. A marker on the Properties palette flags properties that exist only while adding, not when modifying.
- Properties palette, in order:
  - Basic > Description: button, type text, OK.
  - Style: styles in the current drawing.
  - System: systems in the current drawing. Tip: tools can reference styles and systems in content library DWGs.
  - Orientation: Ortho or Isometric.
  - Isoplane (Isometric only): Left, Top or Right.
  - Advanced > ID: the style supplies the list; pick one or type another.
- Draw: pick the start point, or use the toolset's schematic snaps to attach to a symbol or another line; keep picking points. To change planes mid-run, change Isoplane on the palette (UCS icon and crosshairs follow). Properties can change between lines. Enter ends.
- [AUTO] No command-line options for Style, System, Orientation or Isoplane are documented; they are palette settings. (inference) For scripting, put the settings in a tool palette tool, or set them by converting AutoCAD geometry (below), which documents command-line options.
- [AUTO] AutoCAD FILLET extends or trims existing schematic lines to join them.

Add grips ([G:BFC5913F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BFC5913F-4658-4B79-8B94-A7ECF646D351)):
- Select a schematic line or symbol, click the add grip (+), pick more points, Enter. Works in ortho or isometric.

Convert an AutoCAD LINE, ARC or PLINE ([G:EDD12C73](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EDD12C73-9857-457E-B925-12B3E6100C3C)):
1. Draw the AutoCAD object.
2. Right-click it > Convert to Schematic Line.
3. [AUTO] Enter or `n` = keep the layout geometry; `y` = erase it.
4. The Modify Schematic Lines dialog opens: System, Style, Designation ID [GUI].
- [AUTO] Same settings at the command line: `sy` (system), `st` (style), `i` (designation ID). `m` (match): select an existing schematic line, choose the properties to match, Enter.
- The page names no command for the convert action. (inference) Find the underlying command name before scripting it, and test whether the dialog blocks under a script.

Symbols:
- Insert symbols at an insertion point plus rotation angle, like AutoCAD entities ([G:CFEAE09A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFEAE09A-E0CF-4F8F-9908-0F6AFDC46EEF)). The Schematic Line contextual tab has Insert Symbol ([G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9)). SYMBOL, SYMBOLADD, SYMBOLADDSELECTED are tagged, with no prompts documented ([G:A614B788](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A614B788-0A64-4F7C-8C1F-6C4701C8AC73)).
- End-of-line symbols (pumps, tanks, equipment) go in FIRST; then draw lines to them. In-line symbols (valves, gauges) go onto existing lines ([G:E5FB9492](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5FB9492-C86B-43FD-8BC7-687D95BE9A6A), [G:A614B788](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A614B788-0A64-4F7C-8C1F-6C4701C8AC73)).

## 4.20 Modifying, moving, rotating and resizing schematic objects

After placing lines and symbols you can edit their properties, move them, or assign them to another system ([G:15DCC7FF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-15DCC7FF-D22B-4BC3-A65B-413908BBD75C)).

Line properties ([G:DDB8B401](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DDB8B401-81BE-4DCF-B291-28F15A36870B)) [GUI]:
- Select the lines. System: Properties > Basic > General > System opens the Styles Browser with Object Type = Schematic System Definitions; pick from the gallery and click to apply.
- Styles Browser sources (same for symbols, [G:73A0404A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73A0404A-5896-4FDC-B96F-2E46EC1E89A2)):
  - Current drawing: Drawing File = Current Drawing.
  - All open drawings: Drawing Source = Currently Open Drawings, Drawing File = All Drawings.
  - Open drawings except this one: Drawing Source = Currently Open Drawings, Drawing File = All Without Current Drawing.
  - A content library file: Drawing Source = Content Library Drawings, pick the file in Drawing File.
  - Add a library location: Drawing Source = Content Library Drawings, Drawing File = Manage Content Library; in the Content Drawings Library dialog add a folder or drawing.
- Other properties: Description (button, edit, OK); Layer (current drawing layers); Style (current drawing styles); Location (Additional information > Location worksheet insertion point, OK; grips or MOVE also work); ID (Advanced > Design Data > ID). Esc when done.

Symbol properties ([G:73A0404A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73A0404A-5896-4FDC-B96F-2E46EC1E89A2)) [GUI]:
- Command tagged: SYMBOLPROPS (no prompts). Select symbols. Style: Basic > General > Style, click the image, Styles Browser, pick, click to apply.
- Description; Layer; System (expand System; current drawing definitions); Orientation (expand Drawing Mode; Ortho or Isometric); Isoplane (isometric symbols only; Left, Top, Right; grips can also rotate it around the 3 isoplanes); Rotation (ORTHO END-OF-LINE symbols only; under Location; degrees); Location (end-of-line only; Location worksheet; Location grips move both kinds); ID (Advanced > Design Data > ID). Esc.

Move schematic lines ([G:203B4B72](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-203B4B72-579C-4F83-A871-1BD66B4BE908)):
- Three ways: grip drag; AutoCAD MOVE; new insertion point on the Properties palette (which can also change the normal and rotation). In-line symbols anchored to the line move along with it.
- [AUTO] Ortho: select, click the Location grip; drag and click (grip = base point), or enter `b`, pick a base point, pick the second point.
- Start grip and End grip (ORTHO mode only) on an UNCONNECTED segment change length and angle (start or end XYZ). Handy for hooking a new segment to a run.
- [AUTO] Isometric: the Move Isoplane grip moves the line perpendicular to its plane; same drag or `b` choices.
- By coordinates: Properties > Basic > Location > Additional information > Location worksheet. Insertion Point = new coordinates. Normal for the XY plane: X 0, Y 0, Z 1. YZ plane: X 1, Y 0, Z 0. XZ plane: X 0, Y 1, Z 0. Rotation > Angle = rotation on its plane. OK, then Esc.

Move schematic symbols ([G:EB6B3C0C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB6B3C0C-3450-496F-BC0C-D6BB75140522)):
- Grips move ortho and iso symbols along lines and across the drawing. Use AutoCAD MOVE for symbols not anchored to lines.
- [AUTO] Ortho: select, Location grip, drag and click or `b` + base point + second point; Esc. Isometric: Move Isoplane grip, same choices; Esc.
- End-of-line symbols can also take a new insertion point on the Location worksheet.

Lengthen a schematic segment ([G:D98C496C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D98C496C-DF52-4F33-A234-D0412EF24465)):
- Lengthen grips hold the current angle. On a connected end you choose: no key = keep connectivity, adjust only schematic fittings and segments, parts stay; "press Ctrl" = adjust all objects including parts; "press Ctrl" = break connectivity. The page gives the same text for both Ctrl rows and no count. (inference) By analogy with the location grip page ([G:8AFBE73A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8AFBE73A-7535-4B74-98BA-2D0DAB749668)), once = adjust all, twice = break.
- Length entry: Tab to the resulting-dimension field and type the new total; or drag and type the change in the default field; or drag the grip and click a new end point.
- [AUTO] Needs Dynamic Input AND Dimension Input on (default); else move to a stretch point or type coordinates in the command window.

Rotate symbols ([G:AB971A50](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AB971A50-F397-479F-8C05-F00D841EE6C1), [G:5CF87BE6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5CF87BE6-E2B4-48E0-88A8-4F309B060438), [G:1C278882](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C278882-C0B1-4E0E-B510-6FE7E8AD9386), [G:43699DFE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-43699DFE-F823-459B-8509-BEA08143B93B)):
- Ortho: the Rotate (Flip) grip turns the symbol 180 degrees in the grip direction. Connected objects adjust (small length changes) or disconnect if they cannot.
- An in-line ortho symbol takes its rotation from its line. Rotate it by rotating its curve anchor (right-click > Curve Anchor commands).
- Palette route: release the anchor first (breaks the symbol-to-line link), select the symbol, Properties > Basic > Location > Rotation, type degrees, ESC. Reattach with a curve anchor afterward.
- Isometric symbols have 2 grip types: Rotate grips (90-degree steps in the current isoplane about the base point, one click per step) and Isometric plane grips (cycle left, top, right isoplanes, one click per step). Esc when done.

Resize symbols ([G:EA7AF85F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA7AF85F-5DA1-4AA6-A7A0-D5F184D6708B), [G:595AEF3F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-595AEF3F-0D40-4D4C-83E3-0C527E4D2059), [G:3EEE6E29](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3EEE6E29-5AE6-4C6F-81B8-458053959471), [G:12805FA9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-12805FA9-F623-4CF8-84DB-51C912F0B069)):
- A symbol's scale factor is relative to the annotation and drawing scale. Resize with AutoCAD SCALE (Home tab > Modify panel > Scale).
- [AUTO] By factor: SCALE, select symbol, base point, type factor (example .5), Enter. Aspect ratio kept; above 1 enlarges, below 1 shrinks. A typed length at that prompt is used as the factor in current units.
- [AUTO] By reference: SCALE, select, base point, `R`; pick two reference points, or type the current length (second point skipped); then pick or type the new length (example: reference 2.5, new length 3.5).
- By grips [GUI]: first convert the symbol to a block (BLOCK, or Copy then Paste as Block). Click its single insertion grip (turns red, base point), enter `sc` or press Spacebar/Enter to cycle to Scale, move, click.

## 4.21 Chilled-water flow diagrams with the schematic tools (mostly inference)

Documented facts that shape a chilled-water flow diagram:
- Schematics are 2D and not to scale; no sizing tools and no elevations or sections come from them ([G:24AA4038](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24AA4038-A82E-4224-9385-96495590CD4B)).
- Pumps, chillers (equipment), tanks: end-of-line symbols, placed FIRST, then connected. Valves, gauges, controls: in-line symbols placed on existing lines, erased with the line ([G:E5FB9492](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E5FB9492-C86B-43FD-8BC7-687D95BE9A6A), [G:A614B788](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A614B788-0A64-4F7C-8C1F-6C4701C8AC73)).
- One schematic system definition per system; the layer key sets layer, color and linetype; Abbreviation (2 or 3 characters) feeds labels and schedules ([G:2F7F184E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F7F184E-0CD2-4E41-9DEF-8D3858924B92), [G:B8BFD4FD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B8BFD4FD-3E01-490F-8693-1328A0671252)).
- Line styles tell systems apart and set crossing breaks, junction nodes, start and end symbols, and designation IDs ([G:2E85994E](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2E85994E-D9EE-486A-BC63-A5B61F69AC7D), [G:98B43F6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-98B43F6A-5018-4AD2-8D36-B8F38B80E21C), [G:EE34EB0D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE34EB0D-372D-4969-8B0B-FE04CEAD6560)).
- Orthographic for flow diagrams; isometric for riser-style diagrams on Left/Top/Right isoplanes ([G:24AA4038](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-24AA4038-A82E-4224-9385-96495590CD4B), [G:45ABD873](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45ABD873-5492-46AF-9225-D6F23F149E22)).
- Show Connected Objects on the Schematic Symbol tab checks connectivity ([G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9), [G:EA5D1830](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA5D1830-AD93-4C72-9BA6-C3F9D9D97441)).
- If a 3D Pipe model already exists: graphical 1-line display shows a generalized routing of that model with non-scaled components and equipment as schematic symbols, without changing the parts ([G:1B4DDD6A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1B4DDD6A-DCF8-4375-B562-E14CBB872A54), [G:62483160](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-62483160-700B-401D-ABA4-8DA3BD4E3723)). That is a display of the model, not a schematic diagram.

Suggested setup (inference, not a documented procedure; test on a copy):
1. Schematic workspace. Copy a shipped schematic system definition twice and name them for chilled water supply and return (example names CHWS, CHWR as Abbreviation). Set a layer key for each.
2. Put both in one System Group on the Design Rules tab. The "different systems cannot connect" rule is documented for pipe and plumbing ([G:A98BA454](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A98BA454-FC91-4834-9E89-F1830D814549), [G:DC9E8C4A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC9E8C4A-E447-4A8A-BD77-FABCA5C8F9B3)); whether it binds schematic lines is not stated, so the group is a safe default where supply meets return (bypass, 3-way valve).
3. Make one schematic line style per system with Crossings = break or overlap and a priority, so crossings read cleanly. Remember the unresolved same-priority rule (4.18).
4. Place chillers, pumps, tanks and coils first, then draw supply and return lines from their connection points with schematic snaps, then add valves and gauges onto the lines.
5. Check with Show Connected Objects.

Scripting notes (inference):
- The documented scriptable surface is thin: `slineadd` can be typed, but Style, System and Isoplane are palette settings; Convert to Schematic Line has command-line options (`sy`, `st`, `i`, `m`) but no documented command name; no symbol-insert prompts are documented (4.2).
- A scripted route to probe first: draw LINE or PLINE geometry by script, then convert it and answer the `sy`/`st`/`i` options. Confirm the convert command name and whether the Modify Schematic Lines dialog blocks under a script before building on it.
- Fallback when no live connectivity is needed: plain AutoCAD blocks and polylines on system layers are fully scriptable, but lose schematic connectivity, system-driven layer keys and Show Connected Objects.

## 4.22 Toolset UI facts these tasks depend on

Workspaces ([G:EB8AABD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EB8AABD5-EA71-430A-A5F5-15FBE416B46C), [G:135E632B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-135E632B-9F53-4D22-9C04-784286193D05), [G:EA0D9CD5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA0D9CD5-AE7A-4D2E-B0BF-AAE3E7FF8433), [G:C763CBED](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C763CBED-E373-4686-900F-B30C6FC0B540)):
- Six defaults: HVAC, Piping, Electrical, Plumbing, Schematic, Architecture. HVAC is the default after first install. Each fills the ribbon with its discipline tools and shows its tool palette group.
- A workspace sets which ribbon panels show and whether Tool Palettes and Command Line float or dock. Save your own [GUI]: click the workspace name on the status bar > Save Current As, name, Save. CAD managers can share read-only workspaces.
- Manage tab > Preferences panel exists only in HVAC, Piping, Electrical and Plumbing workspaces ([G:C0476A8C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0476A8C-8734-4154-8E59-8C8E4A598FA1)).

Ribbon and menus:
- Static tabs (always shown) and contextual tabs (follow the selection and mirror its right-click menu). Every contextual tab has a General panel (Select System, Object Viewer, Isolate Objects, ...) ([G:84FF7DF4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-84FF7DF4-CF53-40FD-9FEA-34FE9E1FFCFA), [G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9)).
- Default HVAC workspace static tabs: Home, floating View panel, Insert, Annotate, Analyze, View, Manage ([G:97B998B2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-97B998B2-CCFA-45A0-BA77-DF79757A9FDC)). The floating View panel (views, visual styles, Zoom, Pan) is undocked by default and can be docked to the Home tab ([G:8F537E11](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8F537E11-7176-4218-8EDE-113F5AB03A90)).
- A selected object's commands show on its contextual tab and vanish when it is deselected; the tab follows the object's context menu (example: Add Selected is on the duct context menu and the Duct tab General panel). The "Where is my Command?" help file (Help menu) maps old menu locations to the ribbon ([G:2B196266](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2B196266-0587-425D-A4DF-4DDE74DAB4DC)).
- [AUTO] `ribbon` at the command line shows a missing ribbon. The button right of the tab names cycles Minimize to Panel Titles, Minimize to Tabs, Show Full Ribbon ([G:AD94F7CC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AD94F7CC-94AC-4D86-B46D-0D1D5A01F808)).
- Mixed selection: the context menu shows only shared commands; the ribbon shows a "Multiple Objects" tab. Nothing selected: general menu ([G:0501B252](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0501B252-8BE0-4590-803B-F558A3072120)).
- Command line window: View tab > Windows panel > Command Line. A floating one can auto-hide to its title bar ([G:35284F3B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-35284F3B-21BA-46C3-8AF2-D028D8783C4B)).

Contextual tab commands that matter here ([G:B74ECD4C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B74ECD4C-69FF-4EB5-9ABE-9B8ED41398C9)):
- Pipe: Insert Equipment, Pipe Properties, Modify Run, Pipe Length, Set Flow Direction, Show Flow. Pipe Fitting: Insert Equipment, Set Flow Direction, Show Flow. Pipe Custom Fitting: Insert Equipment, Custom Fitting Properties, Set Flow Direction, Show Flow.
- Plumbing Line: Insert Fitting, Modify Plumbing Line, Add Expansion Loop, Merge Plumbing Line, Size Plumbing Line, Show Objects for Sizing, Reverse Flow. Plumbing Fitting: Show Connected Objects.
- Equipment: Modify Equipment, Equipment Properties, Convert to Device, Update Flow.
- Schematic Line: Insert Symbol. Schematic Symbol: Show Connected Objects.

Application menu ([G:A7B0C678](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7B0C678-8890-4F80-9B4C-F47772F76504), [G:C4C54B64](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C4C54B64-5775-4AA1-862B-3541F57EE6B4), [G:3CBA06B7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3CBA06B7-0D1C-4A88-B23E-EBCE4AFCBD90)):
- [GUI] Icon at the upper left; stays open while the cursor is inside it; closes on a command or a click outside.
- Opens drawings, project files, DGN, IFC. Saves to current format, AutoCAD 2007 format, DWT, DWS. Exports DGN, DWF, PDF, IFC, gbXML, DuctXML and earlier AutoCAD versions. Plot, publish, eTransmit.
- [AUTO] Command search covers the application menu, static ribbon tabs, any contextual tab on display and the Quick Access toolbar. It matches display names ("Style Manager"), partial names, command names ("aecstylemanager", "dist"), tooltip text and CUI search tags. MEP command names need the Aecb prefix here (aecbPipeAdd).

## 4.22 Toolset UI facts these tasks depend on (continued)

Model, Work and sheet tabs ([G:6E679147](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6E679147-77D9-4112-91A6-89ADF5702456)):
- [AUTO] The tabs below the drawing area are OFF by default. Enter LAYOUTTAB to turn them on.
- Model tab: works only with TILEMODE 1 (tiled viewports). All tiled viewports share ONE display configuration; no floating viewports; cannot freeze different layers per tiled viewport.
- Work tab (model templates): 2 viewports with default display configurations: Top (plan) for schematic, single-line, double-line or reflected ceiling plans, and an isometric view. It can be copied or deleted. (inference) It suits the 2-viewport plan plus iso preview recommended for routing solutions ([G:0AC20AE4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0AC20AE4-5F17-403D-A5B4-A3A4ACC7F11D)).
- Sheet (layout) tabs (sheet templates): plot layouts with border and title block.
- Work on non-Model tabs to get per-viewport display configurations, per-viewport frozen layers and floating viewports.

Palettes and project tools ([G:1F5F5F0B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1F5F5F0B-9C30-4BB1-A140-3E95FD40F1B0), [G:72B1B740](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-72B1B740-E1F2-435B-8A73-11D5C8276ED1), [G:7969FBD7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7969FBD7-1308-42AF-B834-3F1D13F5D61C), [G:7A77C054](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7A77C054-C071-4049-9B84-2A77CC9B0594)):
- Project Browser: create projects; set project number, name, tool palette and content library locations.
- Project Navigator: levels and divisions, drawings, plot sheets; the central place for project files. The plumbing and pipe workflows xref the architectural plan through it ([G:73E66BE7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-73E66BE7-F5E4-4A56-94D8-546B75CE410A), [G:3F1F7003](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3F1F7003-4B05-4D96-BD57-0035AA20C770)).
- Properties palette: properties of an object about to be drawn or already selected; Extended Data tab holds classifications, notes, reference documents, hyperlinks, property set data. Nearly every plumbing, pipe and schematic setting in this section lives here.
- Tool palettes: the main way to get object tools with preset styles and properties; grouped in tool palette groups in a tool palettes set; build your own or copy from the Content Browser.
- Quick Access toolbar: right-click a ribbon command > Add to Quick Access Toolbar; other commands via the toolbar's down arrow > More Commands > CUI editor ([G:6A122827](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6A122827-D169-4EB6-9C4C-603A2A3DFE96)).

Ribbon tab panels used in this section:
- Home: Build (ducts, fittings, equipment; tool palettes, Properties palette, Content Browser); Modify (Move, Rotate, Erase, Offset, Mirror, Scale, Array, Explode, Join; convert AEC objects to mass elements and mass elements to 3D solids); Inquiry (Schematic and Architecture workspaces only) ([G:B0E324F0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B0E324F0-FEC2-488E-A109-9BE5BD621961)).
- Insert: Reference (xrefs, DWF/DWFx, DGN underlays, images); Block; Attributes; Import (Radiator, WMF, ACIS, 3D Studio Max, DGN, LandXML); Content (Content Browser, DesignCenter, Autodesk Inventor) ([G:F809E349](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F809E349-1C0C-4E90-88A0-806242A56E1C)).
- Annotate: Tools (Document tool palettes set); Text; Dimensions; Scheduling (schedule tables, schedule tags, property set data renumbering); Callouts; Label (attach MEP labels and leaders); Keynoting; Markup; Annotation Scaling. The source text has gaps where linked command names were stripped, so this list is incomplete ([G:8163D900](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8163D900-1C7A-48A0-8FB4-2CED5393D583)).
- Analyze: tools differ by workspace. Inquiry (interference check between MEP objects and mass elements, distance and area, QuickCalc); HVAC (duct size calculation, import DuctXML and gbXML); Space and Zone ([G:93FFE346](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-93FFE346-6B7F-480E-BA6E-67954AE0075A)). The Plumbing panel holds Size Plumbing and Slope Plumbing ([G:961D7F60](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-961D7F60-F746-45C3-AAD7-FC7E9554EF41), [G:B999730B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B999730B-1CBF-4A96-B108-2B8499715BB2)).
- View > MEP View: show flow direction of ducts and pipes; display broken connections (solution tips); compass settings; expanded panel hides the compass bar and sets solution tip size ([G:13C3C20C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13C3C20C-6627-43D4-8E5F-6B49E16F1653)).
- Manage: Action Recorder; CAD Standards (incl. Layer Translator); Project Standards; Style and Display (Style Manager, Display Manager, AEC Dimension Style Wizard, profiles); Preferences; MEP Content (Content Builder, Catalog Editor; expanded: change, test, migrate catalog data, batch convert and decompose components); Applications ([AUTO] load ARX, LSP and VB apps, run user scripts and VBA macros, VBA Manager, Visual Basic and Visual LISP editors); Customization (CUI, tool palettes) ([G:C0476A8C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0476A8C-8734-4154-8E59-8C8E4A598FA1)).

Connectivity checks and solution tips ([G:EA5D1830](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EA5D1830-AD93-4C72-9BA6-C3F9D9D97441), [G:2EB67D54](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2EB67D54-D331-4BEC-A0FA-AFF6683DE82B), [G:13C3C20C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-13C3C20C-6627-43D4-8E5F-6B49E16F1653)):
- Show Connected Run: checks a duct, pipe, plumbing line, conduit, cable tray or wired run. Show Connected Objects: lists what is connected to one object and checks continuity through the run and branches.
- Solution tips flag bad placements; hover for the message and fixes; F1 opens the topic. Tips are suggestions, not guaranteed fixes.
- [GUI] Default: shown while drafting, hidden when plotting or publishing. Change: Options > AEC Editor tab > Solution Tip panel > Drafting and Plotting/Publishing checkboxes.

Custom Display, OBJECTGRAPHICSEDIT ([G:2A688CDE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2A688CDE-FB9A-4DB1-814C-9FBB9CDDB464), [G:B9A9143F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B9A9143F-8446-47B2-914A-86EDF0AA8650), [G:BCDDB402](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BCDDB402-61D0-4181-9381-21E650F21987)):
- In-place edit of an MEP object's plan graphics (vanes, hangers, pipe breaks in a rack to show several elevations, hidden lines for an equipment pad or access space such as a chiller or base-mounted pump).
- Works on duct, pipe, cable tray, conduit, MvParts, wires, devices, panels. NOT on plumbing lines and fittings, NOT on schematic objects and symbols.
- [AUTO] Start: select the object > contextual tab Updates panel > Object Graphics Edit, or type OBJECTGRAPHICSEDIT and select. End: Edit In Place > Edits panel > Finish (save) or Cancel (discard), ribbon only as documented [GUI].
- Other objects dim while editing; strength set in Options > Display tab > Fade Control > "In-place edit and annotative representations". Xref objects can be edited; the change lives in the host and holds only while the xref stays attached to that host. Earlier versions can see and remove, not edit.

Intelligent objects and analysis ([G:B5A862C6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B5A862C6-9CE5-4C27-9D3B-49AE9C7C3D88), [G:81D983B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-81D983B1-A719-4007-8A22-E26BE5A9C891), [G:6526DCB8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6526DCB8-DEBA-4C44-872B-8BFB91624FA9)):
- The toolset holds catalogs of objects that model real parts and connect, discipline tools such as system sizing analysis, common tools (projects, design preferences), and standards-based templates.
- Objects (duct, pipe, cable tray and plumbing line segments; fittings; MvParts) are built from standard AutoCAD geometry plus data. Connectors pass shape, size and system: drawing from a connector reads its size and shape, correctly sized fittings go in as you lay out, and a transition goes in when size changes. Connectivity is kept on modify.
- Analysis: before design, spaces and zones give loads, exported as gbXML with results imported back; while drawing, instant duct or wire sizing; after design, analyze HVAC, electrical or plumbing systems to check loads and resize.

AutoCAD MEP vs plain AutoCAD ([G:A011A47B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A011A47B-FCD3-4CC4-9BD2-A7ECF63FE291), [G:A7FB1011](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7FB1011-486A-4413-ABDA-C4B41BF39039), [G:513A9161](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-513A9161-4C30-4214-A991-61E2167E4383), [G:EC826177](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EC826177-64B1-407B-BE2D-BCE9A5838B22)):
- MEP only: gbXML import/export; MEP workspaces with object grips and snaps; layer keying; location grips with associative movement in X, Y, Z; auto layout, interference detection, connectivity checks; tagging and annotation for documents; automatic rise/drop and hidden-line symbols and display by elevation.
- Each domain workspace has preferences (default parts, labels, connection behavior, display) and system definitions (design rules, display, rise/drop) on its ribbon.

Help and tooltips ([G:DFE8CE62](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DFE8CE62-B2B9-4AE8-A56D-9FBB28DA48D9), [G:10D21526](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-10D21526-AAFD-4E4B-87C6-DB6F09268F91), [G:6B1127E6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6B1127E6-BAFD-4351-9EE2-C325467FE4F7), [G:DC80BF27](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC80BF27-63E5-403B-B352-B5E7B99FFA1D), [G:31E78B2A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-31E78B2A-DF37-4BB7-B9EC-387C67829159), [G:9A3BDCAC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A3BDCAC-F063-41F2-9712-35C2B17214AB), [G:DEDE0084](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DEDE0084-1FBF-4163-9CDA-6AB0BE010A1B), [G:AC82C517](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AC82C517-107E-48E4-B96C-C69E2F11F256)):
- F1 with a command active, a dialog open, or a ribbon tooltip showing gives context help; or the dialog's Help button.
- Every object grip has a tooltip naming its function, with extra info during the grip edit. Useful for identifying pipe, plumbing and schematic grips.
- The rollover tooltip on an MEP object shows standardized basic info and, unlike AutoCAD object rollovers, cannot be changed. Properties palette entries show a tooltip on hover. Command tooltips show on ribbon and Quick Access items, extended ones after a delay.
- Tooltip settings: Options > Display tab > Window Elements > Show Tooltips, "Number of seconds to delay", "Show extended Tooltips". Tooltip families: command, dialog and palette, object rollover, property palette, thumbnail, object grip, plus solution tips.
- Project Navigator file tooltips [GUI]: Constructs, Views or Sheets tab > right-click the toolbar area at the bottom > Tooltip style: Name; Preview (Small, Medium, Large); Details (location, size, last-saved date, last editor); Preview & Details. Right-click > Preview/Details Pane shows it below the file tree.

InfoCenter and resources ([G:5DD9FC7A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DD9FC7A-0A50-48AF-9A72-F16893F63C44), [G:5EF78743](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5EF78743-F192-43C9-A03C-20A5F5B10E1F), [G:4B34FF53](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4B34FF53-4887-4F1A-A29F-338D30907172), [G:CFF39839](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CFF39839-5E0E-41A1-ABC4-335A209917F4), [G:C0E6EE56](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C0E6EE56-BD6D-4EC9-9460-AB1F1748EBC3), [G:A7ADA7B6](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A7ADA7B6-5E31-425C-A988-246DFE9997E4), [G:FC8B3EB7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FC8B3EB7-0EFB-4B4F-9864-F9319C4044ED), [G:090077B2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-090077B2-AD33-4783-9BAB-621BA4A9826A)):
- InfoCenter (top right) searches Help plus files set in InfoCenter Settings, and opens the Communication Center (updates, service packs, RSS, "Did You Know" tips; check daily, weekly, monthly or on demand) and Favorites. The Help menu lives there (Help, knowledge base, developer resources, Subscription support, UI Tour Movie).
- Training: http://www.autodesk.com/autocadmep-training. Community: http://www.autodesk.com/autocadmep-community.
