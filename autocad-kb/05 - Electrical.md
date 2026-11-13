# 05 - Electrical

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

This section covers the electrical side of the AutoCAD MEP 2027 toolset: devices, panels, circuits, the electrical project database (.epd), wires and home runs, conduit and cable tray, checking tools, panel schedules, electrical styles and definitions, and annotation.
It gives exact command names, dialog and palette names, settings, rules, and the places where an unattended script will stop.
Extra care goes to how HVAC equipment gets power: device connectors, poles, voltage, phase loads, motor loads, circuits, and conduit to equipment.
Read 5.1 first. Almost every electrical task in the sources is a dialog, palette or Style Manager task. Only a handful of commands have documented prompts.

## Contents
- 5.1 Automation quick reference (commands, prompts, script blockers)
- 5.2 Powering HVAC equipment: what the sources support
- 5.3 How the electrical model works
- 5.4 Electrical Preferences and setup order
- 5.5 Electrical project database (.epd)
- 5.6 Circuits and the Circuit Manager
- 5.7 Devices and device connectors
- 5.8 Panels and panel links
- 5.9 Wires, home runs and wire sizing
- 5.10 Conduit and cable tray
- 5.11 Checking electrical systems
- 5.12 Panel schedules
- 5.13 Styles, definitions and annotation
- 5.14 Troubleshooting, source conflicts and gaps

Legend: G:XXXXXXXX links to an AutoCAD MEP 2027 help page (first 8 characters of its GUID); KB:n links to an Autodesk support article; (inference) marks a conclusion the cited pages do not state.

## 5.1 Automation quick reference

### What the sources give and do not give
- None of the help pages behind this section documents a hyphen (dash) command form, a system variable, a registry key, or a COM/AutoLISP member for electrical objects. Every setting below is reached through a dialog, worksheet, palette or Style Manager unless a prompt is listed.
- Documented command-line prompts exist only for: CIRCUITASSIGN and PANELASSIGN ([G:5D0A8DE9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D0A8DE9-813B-4978-944F-FA103CE8C4EA)), WIRECONVERT ([G:070A2ED0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-070A2ED0-1975-4CD6-AE03-6BA98CE79EBB)), the `g` option of WIREADD ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD)), the `w` option of DEVICEADD ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B)), and the `c` and `b` keywords after picking an Alignment grip ([G:1CFDC450](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1CFDC450-4314-4B6B-89AF-01E7AEE4CCC1), [G:E9453F0B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9453F0B-B866-41BD-BA74-CEAFA12C5132)).
- Command names come from the "commands:" tag on each help page. Concept pages tag DEVICE ([G:5DF43123](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DF43123-5D3A-4820-B263-FE5E0A0FCC80)), PANEL ([G:4BB2BA8F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BB2BA8F-9CBB-49F9-B2B7-B29F3D7F59A7)) and WIRE ([G:7208F408](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7208F408-8718-470F-BCF9-723E4F367AC8)). The task pages that say what to type tag DEVICEADD, PANELADD and WIREADD ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD), [G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD)). Type the ADD forms. (inference) The bare names may be page tags only; they are not confirmed as typed commands.

### Commands
Setup and project database
- [AUTO] ELECTRICALPREFERENCES: opens the Electrical Preferences dialog (tabs: Voltage Definitions, Circuiting, Electrical Project Database). Ribbon: Manage tab > Preferences panel > Electrical. Dialog, blocks a script. ([G:5872B9E9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5872B9E9-DF5D-41CD-8EFA-667A64C0FCF4), [G:50F2BD55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-50F2BD55-9D98-4DCF-8CA9-5F2CD2DB0ECD), [G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D))
- [AUTO] CIRCUITCONFIGPROJ: tagged on the Electrical Project Database tab page. That tab names the .epd file for the drawing. Dialog. ([G:E0EA3534](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0EA3534-013F-454F-81EF-6EE7CD082B24))
- [AUTO] CIRCUITRELOADPROJ: reloads the .epd into the current drawing. No prompts documented. If a linked drawing cannot be found, the Electrical Project Database Reload dialog opens. ([G:E3FF8266](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E3FF8266-648F-4603-B390-97FE82AE5F7F))
- [AUTO] CABLETRAYPREFERENCES, CONDUITPREFERENCES: open the Cable Tray Layout Preferences dialog and the Conduit Layout Preferences worksheet. Both block a script. ([G:BBC62D0F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BBC62D0F-E0F8-41AF-B50E-DD09DCC2CD72))

Placing objects
- [AUTO] DEVICEADD: adds devices. Settings come from the Properties palette or a tool palette tool. Prompts: `w` then pick a wire to drop the device into it (the wire splits into 2 wires); rotation by cursor or typed degrees, or Enter for the default rotation then click; Enter ends. DEVICEADDSELECTED is listed; no prompts given. ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B))
- [AUTO] PANELADD: adds panels. Settings on the Properties palette. Create circuits = Yes opens the Circuit Settings worksheet (dialog). Rotation typed or Enter for default; Enter ends. PANELADDSELECTED is listed; no prompts given. ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD))
- [AUTO] WIREADD: draws wires. `g` at the prompt generates wires for all devices on the circuit set in the wire properties. After the last device: Enter, then click toward the panel for the home run. Enter twice ends with no home run. WIREADDSELECTED is listed. ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD), [G:11F65058](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11F65058-40C4-4233-B7C6-C0A5CEE8193B))
- [AUTO] WIRECONVERT: turns a line, arc or polyline into a wire. Prompt: Enter or `n` keeps the source geometry, `y` erases it. Then the Modify Wires dialog opens (system, voltage): blocks a script. ([G:070A2ED0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-070A2ED0-1975-4CD6-AE03-6BA98CE79EBB))
- [AUTO] CABLETRAYADD, CONDUITADD, CABLETRAYFITTINGADD, CONDUITFITTINGADD, and the ...ADDSELECTED forms: draw runs and fittings. Cable tray settings live in the Add Cable Trays and Add Cable Tray Fittings dialogs; conduit settings on the Properties palette. Prompt sequences not documented. ([G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9), [G:2FE64946](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2FE64946-87EB-48E7-A15D-F034E341C05C), [G:7DD7AE49](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7DD7AE49-D39F-4D28-9BDC-CF626D1D61B6))

Circuits and checking
- [AUTO] CIRCUITMANAGER: opens the Circuit Manager (create, configure, delete and move circuits; link panels; calculate wire sizes; reports). GUI only. It can stay open while you work in the drawing. ([G:A1D8548D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1D8548D-9C3C-4868-AAFA-91816DDA3907), [G:6B936888](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6B936888-2E29-4508-B9EB-F83519D2BDCD))
- [AUTO] MULTIPLECIRCUITSCREATE: tagged on the Circuit Settings dialog page (used when creating circuits in Circuit Manager or while adding a panel). Dialog. ([G:2DFED135](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2DFED135-65D2-45A8-8F32-59D06AAB6969))
- [AUTO] CIRCUITASSIGN, PANELASSIGN: move selected devices to another circuit or panel at the command line. Need a linked .epd. Prompts below. ([G:5D0A8DE9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D0A8DE9-813B-4978-944F-FA103CE8C4EA))
- [AUTO] CIRCUITINFO: Circuit Info for a selected wire or device: voltage, load, length. ([G:2B682A94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2B682A94-F9CF-4045-8ACE-EF4ECE228F94))
- [AUTO] CIRCUITREPORT: circuit report (panel name, circuit name, voltage, load in VA, circuit length, number of devices) through the same Circuit Info ribbon item, with a Copy to Clipboard button. ([G:FEE46A09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEE46A09-D54D-46CC-9E53-299634C37372))
- [AUTO] SHOWCIRCUITS: highlights all devices in the current drawing on the same circuit. Enter clears it. ([G:90DB44C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90DB44C5-C1CD-46DC-A975-9ECC701F51BC))
- [AUTO] POWERTOTALS: select devices, Enter. Totals the load of the selection (lighting, receptacles, other). ([G:645B48DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-645B48DF-77C5-462E-B513-525178676F4D))

Modify
- [AUTO] CABLETRAYMODIFY ([G:5FF61976](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5FF61976-F619-4094-928D-D609A09850BF)), PANELMODIFY ([G:7EA95A2F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EA95A2F-1959-422A-B09A-634DB7D2D165)): listed; no prompts documented.
- [AUTO] CABLETRAYBREAK, CABLETRAYMERGE, CONDUITBREAK, CONDUITMERGE: the page documents only the Cable Tray Length / Conduit Length dialog. ([G:0BEE0234](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BEE0234-F957-45B7-A503-96C11E55D414))
- [AUTO] LIGHTINGMODIFY (example given): each device type has its own modify command. Select all (Ctrl+A), then enter the type's modify command; it filters the selection to devices of that type. ([G:57753CC7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-57753CC7-1D27-405C-AC58-BA35CE4DDFBC))

Styles and definitions (each opens Style Manager, GUI)
- [AUTO] DEVICESTYLE, DEVICESTYLEEDIT ([G:F6EE3716](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F6EE3716-AF0C-4FAC-AD36-B2D3B15DCC8C)); PANELSTYLE, PANELSTYLEEDIT ([G:C07BBE46](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C07BBE46-4F7A-4852-8A2C-401F6F9F1BB4)); WIRESTYLE, WIRESTYLEEDIT ([G:EBB66DBE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EBB66DBE-DB1C-430E-93EF-798B9FFA8D1D)); ELECSYSTEMDEF, ELECSYSTEMDEFEDIT ([G:A89CF529](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A89CF529-BA46-41CE-AC23-D5C7FACF182E)); LOADCATEGORYDEFINITIONS ([G:CF01E9D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CF01E9D8-1D16-419D-863F-261C10CDD6E6)).

Panel schedules
- [AUTO] REGEN (alias `re`): refreshes values in every panel schedule in the drawing after loads change. ([G:6CB9613C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CB9613C-69AD-41ED-A3B6-88042146BB18), [G:3554BAD0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3554BAD0-7719-4214-831E-1465023D9D08))
- Update Panel Schedule: right-click menu item on a selected schedule. No command name given. Needed when rows must be added or removed. ([G:3554BAD0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3554BAD0-7719-4214-831E-1465023D9D08))
- Export: right-click a schedule > Export > Export Data dialog > .csv file. ([G:5B68FCF5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5B68FCF5-0A15-418B-9EE6-F9B909FBE5EF))

### Documented prompt sequences
CIRCUITASSIGN ([G:5D0A8DE9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D0A8DE9-813B-4978-944F-FA103CE8C4EA))
1. The drawing must be associated with an Electrical Project Database (.epd) file.
2. Enter CIRCUITASSIGN, select the devices, press Enter.
3. Same panel: enter the circuit number.
4. Another panel: enter `p` to show all panels and their circuits. Specify the panel name to switch to that panel, then enter a circuit name under it.
5. If the circuit is overloaded, does not match the device type, or the circuit number is not in the new panel, the devices are NOT reassigned. No error text is documented. (inference) Verify with SHOWCIRCUITS or CIRCUITINFO after the run.
6. New panel: enter CIRCUITMANAGER, create the panel and its circuits in the left pane, then run CIRCUITASSIGN again.

PANELASSIGN ([G:5D0A8DE9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D0A8DE9-813B-4978-944F-FA103CE8C4EA))
1. .epd required. 2. Enter PANELASSIGN, select the devices, press Enter. 3. Enter the panel name, press Enter.
- Devices move only if the panel name is correct, a matching circuit exists in that panel, and the circuit matches the selected device types.

### What stops an unattended script
- Dialogs and worksheets: Electrical Preferences (all tabs); the Electrical Project Database prompt (Create a new EPD file / Open an existing EPD file) that appears when circuits are made with no .epd set ([G:DF533E20](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF533E20-D5AB-4854-831A-1D029DD42F58), [G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3)); Circuit Settings worksheet; Create Multiple Circuits; Circuit Manager; Electrical Properties worksheet; Modify Wires; Calculate Wire Sizes; Add Cable Trays; Add Cable Tray Fittings; Modify Cable Tray; Cable Tray Length / Conduit Length; Maintain Connection; Select a Part; part substitution prompt; Panel Schedule; Export Data; Panel to Panel connection dialogs; Styles Browser; Style Manager.
- The overload warning (once per drawing session) ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085)). (inference) The first one can stop a script.
- Saving a linked drawing while its .epd is open prompts you to close the .epd ([G:7E44D451](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E44D451-B319-4291-8F3B-5073D51E27DA)).
- Changing circuits used in other drawings prompts you to open and save those drawings ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430), [G:11C9A4AE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11C9A4AE-668A-45D2-8475-F49B07444FEA), [G:8DD4A3F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8DD4A3F1-4991-4A7A-966E-4EB392582974)).
- (inference) Plan unattended runs so the .epd exists and is linked, circuits exist, and styles, voltages and load categories are in the template before the script starts. The script then only places objects and runs CIRCUITASSIGN or PANELASSIGN.

## 5.2 Powering HVAC equipment: what the sources support

Read this before showing power to an AHU, RTU, fan coil, pump, chiller or condensing unit. It gathers every rule in the sources that touches equipment power, then gives a method built only from those rules. The method is labeled (inference) because no page walks through it end to end.

### Verified rules that apply to equipment
- Two electrical workflows. Lighting, power and telecom plans: add devices, connect them with wire runs, assign devices to circuits with the panel and circuit features, manage loads with circuit features. Equipment plans (switchboards, emergency generators): add MvParts to the floor plan and draw conduit or cable tray runs between them. ([G:1D53F1C9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1D53F1C9-8A82-41E5-8519-B1F3E05D7548))
- The project workflow adds electrical equipment (generators, transformers, switchboards) right after creating the .epd and before adding panels. ([G:5D10E08D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D10E08D-3AEE-4323-B0E5-83231C17A7AD))
- Wire Ways snaps connect to cable tray, conduit and electrical MvPart equipment. Electrical snaps connect wires to devices and panels. Each family has End Connector and Curve Connector snaps. ([G:46F44722](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-46F44722-79D5-409F-8B53-1670DC9B01CC))
- Conduit or cable tray can start at an MvPart: select an existing conduit or cable tray, click its Add grip, click the MvPart connection. Conduit from an MvPart: optionally set the system and routing preference under Dimensions on the Properties palette. Cable tray from an MvPart: you must pick a System type in Add Cable Trays. Starting from a segment or fitting, the run inherits the system. ([G:839A0F7B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-839A0F7B-3ABB-4D96-9551-C0ECB3DC2911))
- Fittings can be added by hand to customize the connection to an MvPart. ([G:2FE64946](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2FE64946-87EB-48E7-A15D-F034E341C05C))
- Show Connected Objects highlights MvParts connected to conduit or cable tray runs. ([G:5E77C1BA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5E77C1BA-6598-46C6-866E-20078EA41E7A))
- Circuit loads are totaled only for circuits of system type Power and Lighting. ([G:DD5DCB19](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DD5DCB19-62CC-46DA-8134-30893B1F48E7))
- Only a Power and Lighting connector has Voltage, Number of poles (1, 2, 3 or By Circuit), Load Phase 1/2/3 in VA, and Load Category. ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085), [G:FEEBC902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEEBC902-87A2-478E-A95B-4B8D4262C9CF))
- Load Sub-category: Motor can be selected on a connector. The pages do not say what it changes. ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085), [G:FEEBC902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEEBC902-87A2-478E-A95B-4B8D4262C9CF))
- Maximum Overcurrent Rating (amps) and Power Factor on a connector are "reserved for future use". There is no working connector field for nameplate MOCP or power factor. ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085), [G:FEEBC902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEEBC902-87A2-478E-A95B-4B8D4262C9CF))
- A load category demand factor can be "constant for all motors except the largest". ([G:CF01E9D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CF01E9D8-1D16-419D-863F-261C10CDD6E6))
- Device to circuit rule: device voltage and number of poles must be equal to or less than the circuit's. A higher device voltage, or more device poles than circuit poles, blocks the assignment. ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430))
- Panel Phases (1 or 3) can be chosen only BEFORE the panel is placed; it is read-only after insertion. Wires (3 or 4) applies to 3-phase panels. 3-pole circuits can be made at insert only if Phases = 3. ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD))
- Panels of different voltages link with the method "Panels are connected through a transformer". ([G:D7B332A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D7B332A9-3E01-4F70-83F0-56FB7CEC43F6), [G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD))
- Wire styles: the "Multi-pole" example style is for equipment and power distribution. ([G:7208F408](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7208F408-8718-470F-BCF9-723E4F367AC8))
- Instant wire sizing needs a Power and Lighting circuit and a wire style whose material was picked from the list. Sizes come from the circuit rating, the wire material and temperature rating, and the drawing ambient temperature, using NEC 2002 Handbook tables 310.16 and 250.122. ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD), [G:524859D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-524859D8-3899-46BB-900B-F0189C59CB41), [G:CA0971E0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA0971E0-0ED6-4975-8EC9-6BB09E2B7434))
- A device can have several connectors. A device on circuits from different panels needs one home run per panel; give each connector its own location in the device style. ([G:F7A65629](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7A65629-1D39-4FAB-86A5-2A254683703C), [G:FEEBC902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEEBC902-87A2-478E-A95B-4B8D4262C9CF))

### Not in the sources
- No page behind this section says an HVAC MvPart (air handler, rooftop unit, pump, fan, chiller) carries an electrical connector that can join a circuit, or that MvPart load reaches the Circuit Manager or a panel schedule. Treat that as unverified until tested in the drawing.
- No page gives fields for MCA, MOCP, FLA, RLA or disconnect size. The panel schedule circuit fields are Circuit Name, Description, Total Load, Rating, Voltage, Number of Poles, Phase, Load Category, System, System Type, Wires, Load Phase A/B/C and Amps; none holds MCA or MOCP ([G:FB5180B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FB5180B1-B103-4C84-9DFD-6D5AC729668D)). (inference) Put the unit tag in the circuit Description so it prints on the schedule.

### Method (inference, built only from the rules above)
1. Template setup: voltage definitions for the project voltages (keep the 2-pole and 3-pole lists the same, [G:50F2BD55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-50F2BD55-9D98-4DCF-8CA9-5F2CD2DB0ECD)); a load category for motor loads, for example with demand factor type "constant for all motors except the largest" ([G:CF01E9D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CF01E9D8-1D16-419D-863F-261C10CDD6E6)); an electrical system definition named for the real system, following the pattern "Device - Power - 277V" ([G:A89CF529](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A89CF529-BA46-41CE-AC23-D5C7FACF182E)).
2. Create and link the .epd (5.5) before making any circuit, so no database prompt appears.
3. Add the panel with the right Phases, Wires and voltages set before you place it. Create 3-pole circuits at the unit voltage, or 2-pole circuits for single-phase 208 or 230 V units.
4. Represent each unit's power connection with a device placed at the unit: a junction box device (junction boxes are in the device library, [G:5DF43123](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DF43123-5D3A-4820-B263-FE5E0A0FCC80)) or a custom device style. Its connector: system type Power and Lighting, Number of poles 3 (or 2), Voltage equal to the circuit voltage, Load Phase 1/2/3 in VA, Load Sub-category Motor, Load Category = the motor category.
5. Do not use a General connector where the unit's load must count. General connectors have no voltage, pole or load fields (those are Power and Lighting only), so they add no load.
6. Assign the device to the circuit in the Electrical Properties worksheet while adding it, or later with CIRCUITASSIGN.
7. Set the circuit Rating in Circuit Manager (Power and Lighting only). Rating is the input for wire sizing.
8. Keep nameplate data (MCA, MOCP, FLA, disconnect size) in a property set on the device and show it with a tag. Property set = user-defined group of properties; tag = symbol that shows property set data ([G:E7CCD48A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7CCD48A-8EEB-419E-A63F-E61EF8363FAD), [G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B)).
9. Draw conduit from the device or the MvPart with the Add grip and Wire Ways snaps.
10. Check with CIRCUITINFO and POWERTOTALS, look for red (overloaded) circuits in Circuit Manager, then REGEN or Update Panel Schedule (5.12).
- (inference) In power totals, equipment devices land in the "other" group, since totals group only lighting, receptacles and other ([G:57753CC7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-57753CC7-1D27-405C-AC58-BA35CE4DDFBC)).

### Load math (inference, standard electrical math, not from these pages)
- Not engineering advice. These notes are drafting aids only; circuit, conductor and overcurrent sizing must come from the engineer of record and the code edition adopted where the work is built.
- 3-phase balanced load: total VA = 1.732 x line-to-line volts x amps. Enter one third of the total in each of Load Phase 1, 2 and 3.
- Single-phase 2-pole load (208 or 230 V): total VA = volts x amps. Split it evenly across Load Phase 1 and Load Phase 2 (common panel schedule practice).
- NEC rules for HVAC equipment let the breaker (MOCP) be larger than the conductor ampacity (MCA basis). Auto sizing from the circuit rating can then give a bigger wire than the nameplate needs. Check auto sizes against the code edition in force; the 2027 page still cites NEC 2002 ([G:524859D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-524859D8-3899-46BB-900B-F0189C59CB41)).

## 5.3 How the electrical model works

### Objects
- Electrical objects are devices, panels and wires. Cable tray and conduit runs are drawn afterward to complete the network. ([G:45362B94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45362B94-760D-44EB-A9EF-FE945D676BE0))
- Device library: power receptacles, general lighting fixtures, fluorescent lighting fixtures, switches, communication devices, fire safety devices, junction boxes. ([G:5DF43123](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DF43123-5D3A-4820-B263-FE5E0A0FCC80))
- Panel library: recessed panels and surface door panels. ([G:4BB2BA8F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BB2BA8F-9CBB-49F9-B2B7-B29F3D7F59A7))
- Display: 3D views show real geometry; 2D plan shows one-line symbols ([G:5DF43123](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DF43123-5D3A-4820-B263-FE5E0A0FCC80), [G:4BB2BA8F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BB2BA8F-9CBB-49F9-B2B7-B29F3D7F59A7)). Receptacles, switches and telecom outlets are symbolic and NOT to scale in plan. Lights are symbolic but scaled to their real envelope in plan, so lighting density and interference checks work. ([G:45362B94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-45362B94-760D-44EB-A9EF-FE945D676BE0))
- Panels, wires and devices are style-based content: each object is an instance linked to its style, and editing the style updates the objects ([G:C07BBE46](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C07BBE46-4F7A-4852-8A2C-401F6F9F1BB4), [G:EBB66DBE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EBB66DBE-DB1C-430E-93EF-798B9FFA8D1D), [G:F6EE3716](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F6EE3716-AF0C-4FAC-AD36-B2D3B15DCC8C)). Exception: changing Number of Poles, Voltage or Load in a device style does NOT update instances already in the drawing ([G:FEEBC902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEEBC902-87A2-478E-A95B-4B8D4262C9CF)).

### Circuits
- A circuit is a non-graphical element stored in a database. It carries electrical system, rating, voltage and panel assignment; devices are assigned to it. ([G:4419EDDF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4419EDDF-DB88-4DE1-AC5B-90F082BF5C06))
- Circuit Manager is the only place to reach circuit objects and change them. Circuit changes show nothing in the drawing; read circuit info or a circuit report to see them. ([G:8DD4A3F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8DD4A3F1-4991-4A7A-966E-4EB392582974))
- Wires are not required to assign devices to circuits or to see loads. Wires without circuits are useful in early design. ([G:7208F408](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7208F408-8718-470F-BCF9-723E4F367AC8), [G:11F65058](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11F65058-40C4-4233-B7C6-C0A5CEE8193B))
- Wires are anchored to devices. Moving a device stretches its wires. ([G:7208F408](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7208F408-8718-470F-BCF9-723E4F367AC8))
- Circuits can exist with no panel; they follow the naming convention and show as "unassigned". ([G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D))

### System types (decide what can connect)
Set when the circuit is created ([G:C1B44143](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C1B44143-C730-4F69-A540-EA41DDC208DE)):
- Power and Lighting: devices connect only to circuits of the same type (receptacles, small appliances, light fixtures). Only this type tabulates loads, checks overloads and allows instant wire sizing. ([G:DD5DCB19](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DD5DCB19-62CC-46DA-8134-30893B1F48E7), [G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D), [G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD))
- General: devices connect to circuits of ALL system types. Example: switches and junction boxes set to General can go on General, Power and Lighting or Other circuits.
- Other: devices connect only to circuits of the same type (communication, fire safety).
- Rule: for Power and Lighting or Other, the device connector must use the same system type as the circuit. To allow any circuit, give the connector the General type. ([G:C1B44143](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C1B44143-C730-4F69-A540-EA41DDC208DE))
- Overload checks do not work for General or Other circuits (no current ratings or voltages). ([G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D))

### Device system vs connector system
- The device's own system (Advanced > System) sets only its display. The system on each electrical connector decides which connections it accepts. ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085))
- A connector with no system accepts a wire of any system. A connector with a system needs a wire of the same system, or the connector's system must change. Connection rules decide whether you are prompted, the change is silent, or the connection is refused. The device's display system does not change. ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD))
- Connector styles hold those rules (Cable Tray, Conduit, Electric, HVAC, Pipe, Schematic). Autodesk recommends keeping the defaults; edits can make the software work improperly. View them: Manage tab > Style & Display panel > Style Manager > Multi-Purpose Objects > Connector Styles > style > Rules tab. ([G:55201F4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-55201F4D-BDB3-4870-A35A-A7381224EB5D), [G:ACBA8796](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-ACBA8796-0F54-4B9E-A59B-DEB547A66D69))

### Snaps
- Electrical Snaps connect wires to devices and panels. Wire Ways Snaps connect to cable tray, conduit and electrical MvPart equipment. Each family has End Connector Snaps (endpoint) and Curve Connector Snaps (anywhere along the centerline). ([G:46F44722](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-46F44722-79D5-409F-8B53-1670DC9B01CC))
- If snapping is hard, zoom in or change the AutoSnap aperture size (Options dialog > Drafting tab). ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:E9453F0B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9453F0B-B866-41BD-BA74-CEAFA12C5132))

### Runs and networks (conduit, cable tray)
- Run = parts that enclose or support wires from one point (junction box, panel) to another (a junction with another run). Network = connected runs. ([G:FF460803](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FF460803-026B-4714-8518-D0D61D53FF4B))
- A branch can start anywhere along another run; a fitting goes in and the branch inherits part properties from the run it joins. Solution Tips test validity after connecting. ([G:FF460803](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FF460803-026B-4714-8518-D0D61D53FF4B), [G:C30CF331](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C30CF331-9793-49A0-8F0E-64AB0E89A06B))

## 5.4 Electrical Preferences and setup order

### Electrical Preferences dialog
- [AUTO] ELECTRICALPREFERENCES, or Manage tab > Preferences panel > Electrical. Dialog, blocks a script. ([G:5872B9E9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5872B9E9-DF5D-41CD-8EFA-667A64C0FCF4))
- Set before creating circuits: project voltages, circuiting features (naming, overload checks, wire sizing factors), and the .epd file. ([G:5872B9E9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5872B9E9-DF5D-41CD-8EFA-667A64C0FCF4))

Voltage Definitions tab ([G:50F2BD55](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-50F2BD55-9D98-4DCF-8CA9-5F2CD2DB0ECD))
- Valid voltages per number of poles. They are the defaults offered for devices and circuits.
- Each definition = voltage + minimum + maximum. Min and max set the valid range when a device is connected to a circuit.
- Keep the 2-pole and 3-pole settings the same, or some values may be missing in the Circuit Settings worksheet.
- Add: select a pole type > Add Voltage Definition > enter voltage, minimum, maximum. Delete: expand the pole, select the voltage > Remove Voltage Definition.
- Panel voltage lists (phase-to-neutral, phase-to-phase) come from these definitions. ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD))

Circuiting tab ([G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D))
- Require Unique Circuit Names per Drawing: each drawing uses its own names.
- Prefix: None; Panel Name; User defined (type it in the box).
- Numbering: Use Sequential Numbers (start 1, next pole 2); Group using Number of Poles (groups even and odd branch circuits; a 3-pole circuit with start 1 makes the next pole 3); Increase by Number of Poles (1-pole uses 1 number, 2-pole 2, 3-pole 3).
- Start Number: default 1. The serial number is appended to the end of the circuit name.
- Overload: Check Overload when circuiting; Display Overload in the Circuit Manager; a percentage of maximum circuit rating at which a prompt appears. Works only for Power and Lighting circuits.
- Wire Sizing: Ambient Temperature. Sets the ampacity correction factor used when wire sizes are calculated.

Electrical Project Database tab ([G:E0EA3534](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E0EA3534-013F-454F-81EF-6EE7CD082B24), [G:7E44D451](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E44D451-B319-4291-8F3B-5073D51E27DA), [G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3))
- Project Database (browse button, New, or `<None>`), Use Fixed Path / Use Relative Path, and the number of backup .epd files (up to 99). Details in 5.5.

### Setup order
Define system requirements first ([G:5CC1C499](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5CC1C499-DC67-4F17-9C4B-BB61E9546C28)):
1. Electrical system definitions. 2. Load category definitions. 3. Electrical Preferences (voltages, naming, wire sizing factors). 4. Wire style design specifications (hot, neutral, ground, isolated ground). 5. Device styles (wire cleanup method, drawing layer).
- Best practice: do these before creating circuits; it cuts the details you must enter when adding circuits. ([G:EE8C9967](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE8C9967-7534-4B3D-8BF8-B39DCC9C8D27))

Project steps ([G:5D10E08D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D10E08D-3AEE-4323-B0E5-83231C17A7AD)):
1. Preliminary 1-line design (schematics). 2. Create the .epd. 3. Add electrical equipment (generators, transformers, switchboards). 4. Add panels (can create circuits at the same time). 5. Spaces (for power totals, wire sizes, room take-off schedules). 6. Place fixtures and devices; copy devices and panels. 7. Create circuits in Circuit Manager. 8. Draw cable tray and conduit. 9. Add wires (drawn or generated). 10. Check (power totals, wire sizes) and modify. 11. Insert panel schedules. 12. Annotate (labels, tags, symbols). 13. Views and details for construction documents.
- Typical start: attach the architectural plan as an xref, then place devices and panels. ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD))
- The electrical features target the design development and construction document phases. ([G:03C2B241](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-03C2B241-897B-495B-BCB9-A35692ECD13C))

## 5.5 Electrical project database (.epd)

### What it is
- A file with extension .epd that holds the panels and circuits that devices and wires are assigned to. Device drawings are separate drawings linked to it. All linked drawings share current circuit data. ([G:821C23DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-821C23DC-6E17-4DDB-8782-8CC618B72670))
- Keeps loads and assignments right even when devices in several drawings sit on one circuit. ([G:F10CE01D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F10CE01D-757B-469E-90DF-A0FC64411823), [G:DD5DCB19](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DD5DCB19-62CC-46DA-8134-30893B1F48E7))
- Panel schedules for construction documents are built from the .epd; circuit data comes straight from it. ([G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3))
- One .epd per project is recommended ([G:DF533E20](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF533E20-D5AB-4854-831A-1D029DD42F58)). A drawing can link to ONLY ONE .epd at a time ([G:7E44D451](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E44D451-B319-4291-8F3B-5073D51E27DA)).

### Is it required? (pages differ)
- One page says every drawing with circuits needs an .epd. It can be set before or after circuits are created. If none is set when circuits are added, you are prompted for an .epd file name. ([G:821C23DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-821C23DC-6E17-4DDB-8782-8CC618B72670), [G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3))
- Another page says circuits can live in the same drawing as the panel they belong to. ([G:EE8C9967](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE8C9967-7534-4B3D-8BF8-B39DCC9C8D27))
- Circuit Manager and the Electrical Properties worksheet list circuits from the current drawing, or from the .epd when one is set. ([G:A1D8548D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1D8548D-9C3C-4868-AAFA-91816DDA3907), [G:744FDF65](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-744FDF65-26E9-4AA3-AE6D-E60E2B680511), [G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085))
- CIRCUITASSIGN and PANELASSIGN need an associated .epd. ([G:5D0A8DE9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D0A8DE9-813B-4978-944F-FA103CE8C4EA))
- (inference) Practical rule: create and link the .epd before PANELADD with Create circuits = Yes, and before any circuit is made in Circuit Manager. Otherwise the database prompt dialog stops a script.

### Create one
- Prompt route: when circuits are made with PANELADD or in Circuit Manager and no .epd is set, the Electrical Project Database dialog offers Create a new EPD file (enter a file name, OK) or Open an existing EPD file (browse to it, OK). ([G:DF533E20](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF533E20-D5AB-4854-831A-1D029DD42F58))
- Before any circuits: Manage tab > Preferences panel > Electrical > Electrical Project Database tab > New. Optionally reference the floor plan in the new drawing for panel placement. Add panels (Panel tool palette or PANELADD). Make circuits while adding panels or later in Circuit Manager. ([G:DF533E20](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF533E20-D5AB-4854-831A-1D029DD42F58))
- Usual pattern: create panels and circuits in one drawing and add them to the .epd; other drawings link to the .epd and use them. Any drawing can be linked. ([G:6B936888](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6B936888-2E29-4508-B9EB-F83519D2BDCD))

### Link a drawing ([G:7E44D451](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E44D451-B319-4291-8F3B-5073D51E27DA))
1. Open the drawing (new or existing).
2. Manage tab > Preferences panel > Electrical.
3. Electrical Project Database tab.
4. Project Database: click the browse button.
5. Pick the .epd file, Open. The file name shows under Project Database; "Used Database" shows the folder path.
6. Choose Use Fixed Path or Use Relative Path.
7. An Electrical Project Database status icon appears in the application status bar.
- Fixed path: moving the .epd, or the whole project, breaks the links. To move the .epd, open each linked drawing and re-point it to the new path.
- Relative path: the link holds while the .epd keeps the same position relative to the drawing; project folders can be moved or renamed. If Use Relative Path is greyed out, save the drawing first.
- (inference) For projects copied between folders or machines, use relative paths.
- After linking, devices can be assigned to .epd circuits as they are added or modified. With several drawings open, reload the .epd in the current drawing.

### Rules while working
- The .epd must be CLOSED while you work in linked drawings. If it is open, saving a linked drawing prompts you to close it. Nothing is written from linked drawings to the .epd unless the .epd is closed. ([G:7E44D451](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7E44D451-B319-4291-8F3B-5073D51E27DA))
- Panel properties changed inside the .epd: save and close the .epd before working in linked drawings. ([G:7EA95A2F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EA95A2F-1959-422A-B09A-634DB7D2D165))
- Circuits cannot be edited from a linked drawing. Open the .epd, edit in Circuit Manager, save and close it, then continue. Linked drawings affected by the edit prompt to be opened and saved so they take the latest data. ([G:8DD4A3F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8DD4A3F1-4991-4A7A-966E-4EB392582974)) Other pages word this differently; see 5.14.
- With 2 or more electrical drawings open, reload the .epd in each one to see the latest circuit info. Example: lighting devices were added to a circuit; a power drawing using circuits on the same panel must reload. ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:9A64EDEF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A64EDEF-8818-4DD4-A18E-DDDB7D73A49B))
- An xref that uses an older .epd than the one the current drawing references puts panel schedules out of date. Reloading an updated .epd does too. ([G:3554BAD0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3554BAD0-7719-4214-831E-1465023D9D08))

### Reload ([G:E3FF8266](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E3FF8266-648F-4603-B390-97FE82AE5F7F))
- [AUTO] CIRCUITRELOADPROJ reloads the .epd. No prompts documented.
- Needed when 2 or more people edit electrical drawings at once, or when 2 or more linked drawings are open and one was saved. Example: another drawing assigned devices to a circuit while yours was open; reload to see the new device count.
- The status bar icon shows an alert marker as soon as a linked drawing is saved. If the other drawing was not open when the change was made, no reload is needed; the .epd reloads every time a drawing opens.
- Automatic reload every 5 minutes. Always on, not configurable.
- Manual: click the Electrical Project Database Status icon once, or right-click it > Reload Electrical Project Database. The status then shows current.
- Missing linked drawing: the Electrical Project Database Reload dialog has a check box to remove that drawing's data from the .epd. Checked = remove (the drawing was deleted). Cleared = keep (the drawing is on a server that is offline for now).

### Unlink ([G:A9208957](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A9208957-B378-44A1-9E27-F14E32E6F0BD))
- Allowed only after ALL circuits in the drawing are removed. On the next save that drawing's data leaves the .epd automatically.
- Manage tab > Preferences panel > Electrical > Electrical Project Database tab > Project Database = `<None>` > save the drawing. Open linked drawings can then reload the .epd.

### Backups ([G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3))
- Backup .epd files are made by default. Use them if an .epd is corrupt or files were linked wrong. Set how many on the Electrical Preferences dialog, up to 99.

### Project tips ([G:BFBB8289](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BFBB8289-3F8B-4AC4-8D38-632F3810561B))
- Use an .epd for all drawings. Create circuits when adding a panel, or later in Circuit Manager.
- Configure circuit settings only in the drawing that contains the circuits. After one device is assigned, many settings lock.
- Set loads on device styles so the load is set when the device is placed.
- Assign devices to circuits at placement or afterward. Reload the .epd to keep several drawings current.
- Turn on overload notification for Power and Lighting circuits in Electrical Preferences.
- Check circuits by viewing a selected device's circuit info, and verify connectivity by showing the devices on the same circuit.
- Balance loads by moving circuits within a panel or dragging them to another panel. Panel schedules generate from circuit data.

## 5.6 Circuits and the Circuit Manager

### Open it
- [AUTO] CIRCUITMANAGER. GUI window; it may stay open while you work in the drawing. ([G:A1D8548D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1D8548D-9C3C-4868-AAFA-91816DDA3907), [G:6B936888](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6B936888-2E29-4508-B9EB-F83519D2BDCD))
- Ribbon routes: Analyze tab > Electrical panel > Circuit Manager ([G:BAB198CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BAB198CF-C790-4240-A296-21ABE0365675), [G:F54B931F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F54B931F-7A38-43EA-A9DA-35C79448470F)); select a device or wire > Device tab or Wire tab > Circuits panel > Circuit Manager drop-down > Circuit Manager ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430), [G:1140E66B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1140E66B-6A72-47EB-BADF-07FA1DE2800D)); select a panel > Panel tab > Circuits panel > Circuit Manager ([G:11C9A4AE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11C9A4AE-668A-45D2-8475-F49B07444FEA)).

### Layout ([G:A1D8548D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A1D8548D-9C3C-4868-AAFA-91816DDA3907), [G:744FDF65](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-744FDF65-26E9-4AA3-AE6D-E60E2B680511))
- Left pane: panels, then system types (for example Power and Lighting), then circuits. Type a panel name in the left pane to search. Right pane: details of the left selection.
- Header: panel properties and circuit settings: voltage, phases/wires, panel rating and type, main rating size, design capacity, AIC rating, mounting, enclosure.
- Footer: connected loads and demand factor, totals per load category, totals times demand factor, demand load total, available spare capacity, load distribution among phases.
- Overloaded Power and Lighting circuits show in red.
- With an .epd you see circuits from every linked drawing; without one, only the current drawing. With an .epd you can edit circuit settings only from the current drawing, not for other linked drawings.
- Editable: name, description. View-only: number of poles and phases for ANSI.
- Copy to Clipboard: Ctrl+C. ([G:FEE46A09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEE46A09-D54D-46CC-9E53-299634C37372))
- Tasks: view circuit and panel info, create, configure and delete circuits, link panels, calculate wire sizes, circuit reports. Power and Lighting circuits get wire sizes calculated from circuit rating, with optional auto-resize of undersized or oversized wires.

### Create circuits ([G:6B936888](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6B936888-2E29-4508-B9EB-F83519D2BDCD))
- Circuits can be made while adding panels, after, or BEFORE any panel exists. One at a time or many at once.
1. In a drawing that has (or will have) at least one panel, open Circuit Manager.
2. Left pane: pick the panel. With no panels yet, pick `<Unassigned>`. New panels land in `<Unassigned>`; drag circuits from `<Unassigned>` onto panels later.
3. One circuit: Create New Circuit button (its drop-down arrow picks a circuit type); or right-click the panel name > New <circuit type>; or right-click the system type under the panel > New Circuit.
4. Many circuits: Create Multiple Circuits button; or right-click the panel name > New Multiple Circuits.
5. Create Multiple Circuits dialog, common properties: Panel (greyed out if you picked a panel first; from `<Unassigned>` pick a panel or leave `<Unassigned>`), System Type, System.
6. Under "<System Type> Properties": number of 1-pole, 2-pole and 3-pole circuits and the voltage for each.
- After adding circuits, update the panel schedules.
- With no .epd set, making circuits brings up the database prompt (5.5). ([G:DF533E20](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF533E20-D5AB-4854-831A-1D029DD42F58))

### Circuit Settings worksheet (when adding a panel) ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD), [G:2DFED135](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2DFED135-65D2-45A8-8F32-59D06AAB6969))
- Properties palette > Circuits > Create circuits = Yes > Circuit Settings button. Dialog; no command-line way to fill it is documented.
- System Type: Power and Lighting, General, or Other. For Power and Lighting or Other, connectors must have the same system type to join the circuit; General lets any system type connect.
- System: the electrical system for the circuits.
- Power and Lighting: total slots on the panel; number of 1-pole, 2-pole and 3-pole circuits (3-pole only if Phases = 3); a voltage for each pole type from drawing voltages valid for that pole count. If the circuit counts are less than the slots, the remaining circuits are created with rating 0. (The page does not say if this compares each count or the sum.)
- General or Other: Number of circuits.
- Circuit Description: text for circuits with breakers and without breakers, shown in Circuit Manager when new circuits are made.

### Configure and modify circuits ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430), [G:F54B931F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F54B931F-7A38-43EA-A9DA-35C79448470F))
- Select the circuit in the left pane. For several: select the branch holding them (for example Power and Lighting), then Shift or Ctrl rows in the right pane. Double-click the property field in the right pane; type or pick a value.
- Editable by system type: Name (follows the naming convention), Description (usually device type and area served), System (electrical system definition), Rating (Power and Lighting only), Voltage (Power and Lighting only).
- Load Category is a style, edited in Style Manager (5.13). ([G:F54B931F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F54B931F-7A38-43EA-A9DA-35C79448470F))
- Calculated, not typed: number of devices, circuit length, and total load (Power and Lighting).
- Circuit length is calculated only when the panel and all devices on the circuit are in the same drawing. Devices normally point to .epd circuits, so length then shows `<Used in multiple drawings>`. ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430), [G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B))
- After devices are assigned, some properties lock. To change one: set the devices' circuit to `<Unassigned>` and edit the circuit; or make a new circuit, set it up, move the devices to it, then delete or reuse the old one. ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430))
- With an .epd, changing a circuit used by devices in other drawings prompts you to open and save those drawings. ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430))
- Rule: Power and Lighting device voltage and poles must be equal to or less than the circuit's, or the assignment is blocked. ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430))
- After any circuit property change, update existing panel schedules. ([G:F54B931F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F54B931F-7A38-43EA-A9DA-35C79448470F))

### Delete circuits ([G:BAB198CF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BAB198CF-C790-4240-A296-21ABE0365675))
- In Circuit Manager select one circuit in the left tree, or select the system type and Shift/Ctrl circuits in the right pane. Click the Delete circuit button.
- A circuit with no devices is deleted with no warning. A circuit with devices asks you to confirm.
- Then run Update Panel Schedule so schedules drop that circuit's data.

### Move circuits between panels ([G:11C9A4AE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11C9A4AE-668A-45D2-8475-F49B07444FEA))
- Use when a panel shows too much load. Select a panel > Panel tab > Circuits panel > Circuit Manager. In the expanded left tree, drag the circuit onto another panel.
- All circuit info and device connections move with the circuit. No drawing change is needed unless wires represent the circuit. Voltage and load figures update at once.
- With an .epd you are prompted to open and save affected linked drawings. Update panel schedules after.

### Reassign devices
- Command line: CIRCUITASSIGN and PANELASSIGN (prompts in 5.1). Need an .epd. ([G:5D0A8DE9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5D0A8DE9-813B-4978-944F-FA103CE8C4EA))
- Palette: the Circuit field of the Electrical Properties worksheet (5.7). Unassigned removes the assignment. ([G:9A64EDEF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A64EDEF-8818-4DD4-A18E-DDDB7D73A49B))

### Overload behavior
- Assigning a device, or wiring it onto a circuit, updates the circuit and checks overload from the connector load and load category. Circuiting preferences decide whether you are warned. After one overload warning you are not warned again in that drawing session. ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085), [G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD))
- Changing a connector's circuit, load or load category re-checks the affected circuits. Editing several devices on different circuits warns once, but you must use Circuit Manager to find which circuit is overloaded. ([G:9A64EDEF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A64EDEF-8818-4DD4-A18E-DDDB7D73A49B))
- Overload checks use total load and work only for Power and Lighting circuits. ([G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D))

## 5.7 Devices and device connectors

### Add devices: DEVICEADD ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B))
- [AUTO] DEVICEADD (DEVICEADDSELECTED is also listed; no prompts given). Ribbon: Home tab > Build panel > Device. Also: a device tool palette tool (tools carry preset properties, so some palette properties may be locked or unneeded), or Styles Browser palette with Object Type = Device (search, import, add).
- A device inserted onto a wire breaks the wire into 2 wires.
- A device can go on a circuit as it is added, or stay unassigned. Circuits can be created and connected at any time.
- Properties palette: an icon marks properties that exist only while adding, not while modifying.

Properties palette fields
- General: double-click the device display to open the style selector; Description button > text > OK.
- Location, Layout Method One by One: Align to objects = Yes snaps with object snaps and turns the device perpendicular to a wall, ceiling grid, space boundary, line, polyline, spline, arc or circle, in this drawing or an xref. = No aligns by hand.
- With Align to objects = Yes the device goes in by the block's insertion point and rotates to the object, so Justification (palette) and Rotation (command line) cannot be set. Layout methods Distance around space and Quantity around space force Align to objects = Yes.
- Justification: the block's insertion point or one of 9 other points (Top Left, Middle Center, and so on).
- Elevation: Preset Elevation (pick from a list) or Elevation (type it).
- Advanced > System: the device's system, which sets its display.
- Design Data > ID: optional number.
- Tag > Insert Tag: a tag anchored to the device. List = tags in the drawing plus the tag set in the selected tool. Tip: build device tools that add tags and property sets on insert. Property sets can also be attached by hand on the Extended Data tab.
- Advanced > Circuits > Electrical Properties button: opens the Electrical Properties worksheet (below).

3D placement rules ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B))
- Connector Z = 0 always. Device insertion point Z = 0. Any other height goes in the device Elevation property (3D offset from the current UCS, seen in 3D or iso views). Reason: devices have 2D views and often 3D views.
- Circuit length comes from elevation differences of devices, wires and panel, and only when the panel and every device on the circuit are in the current drawing.

Insert
- Quantity around space / Distance around space: move the cursor to the first spot (must be on a space boundary), check the preview, click.
- One by One + Align Yes: to drop into a wire enter `w` and pick the wire; otherwise snap to an object (for example a wall) and click; repeat.
- One by One + Align No: for a wire enter `w`, pick it, slide the device along it; click the insertion point; rotate by cursor or type degrees, click (or Enter for default rotation, then click); repeat.
- Change palette values and insert more, or Enter to end.
- With an .epd and 2 or more electrical drawings open, reload the .epd in each open drawing to get current circuit info.

### Electrical Properties worksheet ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085), [G:3359640C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3359640C-646B-449D-9C92-9EC256DAA3E6))
- Every device needs its connectors set here when added. Most devices have one electrical connector.
- Open: while adding, Properties palette > Advanced > Circuits > Electrical Properties. For an existing device: select it > Device tab > Circuits panel > Circuit Properties. Worksheet, blocks a script.
- Two ways: assign the connector to a circuit (pick it, or filter first), or set connector properties and leave it unassigned for later.
- The worksheet lists connectors with System Type and Description. Both come from the device style; change them in the style.
- Filter the Circuit list by: Show circuits from panel (a panel, or Unassigned), System, Number of Poles, Voltage (pick or type).
- Circuits offered: from the current drawing, or from the .epd if the drawing has one. They must match the connector values and have system type General or the connector's system type. Each shows its current load, summed over all drawings including the .epd.
- Once a circuit is picked, System locks. For Power and Lighting, Voltage and Number of poles lock too. Set Circuit to Unassigned to unlock them. ([G:14F2E610](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-14F2E610-A948-47A8-BD45-7755437DC085), [G:9A64EDEF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A64EDEF-8818-4DD4-A18E-DDDB7D73A49B))
- If the device style prevents override of a value, it stays read-only even with no circuit. Allow or prevent overrides is set in the device or panel style connector setup.

Connector fields
- System: General connector = any electrical system in the drawing; otherwise only systems of the same type (Power and Lighting, or Other).
- Load Phase 1/2/3 (VA): Power and Lighting only. Poles Undefined or 1: Phase 1 only. 2 poles: Phases 1 and 2. 3 poles or By Circuit: all three. Left blank, the style value is used and shown.
- Voltage: Power and Lighting only. Type it, pick a drawing voltage valid for the pole count, or By Circuit (taken from the circuit once assigned).
- Number of poles: 1, 2, 3 or By Circuit. Power and Lighting only.
- Load Category: Power and Lighting only; from the drawing's load categories.
- Load Sub-category: Motor is selectable.
- Maximum Overcurrent Rating (amps), Power Factor: reserved for future use.
- "Value Set By" column: Style Default (matches style), Style Override (differs from style), empty (style has no value), Circuit (By Circuit in the style or in the connector).

Editing several devices at once ([G:9A64EDEF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-9A64EDEF-8818-4DD4-A18E-DDDB7D73A49B))
- A property read-only on any selected device is read-only for all. Connectors are listed by number. A differing system type shows *VARIES* and only common properties show. Different values or different sources (style override vs By Circuit) show *VARIES*. By Circuit values also show *VARIES* when connectors are on different circuits.
- Circuit list: circuits matching the entered values with system type General, plus circuits of the shared type when all selected connectors share one; narrowed when types vary.
- Picking a circuit puts the selected connector of every selected device on it. Unassigned removes the assignments.

### Device style connectors ([G:FEEBC902](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEEBC902-87A2-478E-A95B-4B8D4262C9CF))
- Open: Manage tab > Style & Display panel > Style Manager > Electrical Objects > Device Styles > style; or select a device > Device tab > General panel > Edit Style drop-down > Edit Style. Then the Connectors tab.
- Fields: Description (for example Normal Power); System Type (Power and Lighting, Other, or General); Connection Point X, Y, Z, or the button "Add Center Points from View Blocks in Top View" for a centered connector.
- Power and Lighting extras: Number of poles (1, 2, 3, By Circuit, Undefined); Voltage (typed, drawing voltage, By Circuit, Undefined); Load Phase 1/2/3 in VA (added to the circuit for each device placed); Load Category; Load Sub-category (Motor); Maximum Overcurrent Rating and Power Factor (reserved for future use).
- Undefined poles or voltage, with no value given at placement, defaults to By Circuit.
- Changing Number of Poles, Voltage or Load in the style does NOT update devices already in the drawing.
- Prevent Override column: Yes = cannot be overridden when adding devices; No = can.
- Add and remove buttons. DANGER: removing a connector removes it from every instance of the style in the drawing and can break circuit connectivity.
- Several connectors (for example normal power plus emergency) need separate home runs. Give each connector its own location so each home run starts at its own connector. ([G:F7A65629](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7A65629-1D39-4FAB-86A5-2A254683703C))

### Device style design rules ([G:57753CC7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-57753CC7-1D27-405C-AC58-BA35CE4DDFBC))
- Open the device style (as above) > Design Rules tab. It sets device type, drawing layer and wire cleanup.
- Type: a fixed list built into the software; it cannot be customized. Power totals and Circuit Manager group devices by type into lighting, receptacles and other.
- [AUTO] Each device type has its own modify command. Ctrl+A, then a type's modify command (example given: LIGHTINGMODIFY) filters the selection to devices of that type.
- Layer Key: the layer key for devices of this style, from the layer standard and layer key style set for the drawing.
- Wire Cleanup: how wires look where they meet devices or panels (preview image).

### Device style classifications ([G:A6203E1D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6203E1D-856F-41D7-941D-81663C6DEBA4))
- A classification definition is a set of named classifications for object types (example: Construction Status with Existing, Demo, New).
- Uses: display sets that show or hide by classification (for example only lighting devices; many supplied display sets work this way); schedules that include only matching objects, use definitions as columns, or pull data from property sets attached to classifications.
- The software ships a Device Type classification definition holding the built-in device types. It is on the Classifications tab of each device style; most supplied styles already set it.
- Each device has one property per classification definition. View or override it on the Extended Data tab of the Properties palette.
- Set: device style > Classifications tab > button beside Device Type > Select Classification dialog > pick > OK.
- Keep the Device Type classification equal to the Type value on the Design Rules tab unless a custom classification fits better.

### Copy and move devices and panels with Alignment grips ([G:1CFDC450](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1CFDC450-4314-4B6B-89AF-01E7AEE4CCC1), [G:E9453F0B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E9453F0B-B866-41BD-BA74-CEAFA12C5132))
- Unlike COPY and MOVE, Alignment grips can turn the copy or the moved item perpendicular to the object snapped to (wall, ceiling grid).
- Default Alignment grips sit at the electrical connector points. The Show all insertion points grip adds grips at the justification points (Top Left, Bottom Center, Insertion Point and so on).
- Steps: select the device or panel; pick a grip (default = relative to the connector point; or Show all insertion points, then another grip). Alignment is on by default: it snaps and turns perpendicular to a wall, ceiling grid, space boundary, line, polyline, spline, arc or circle in this drawing or an xref. Hold Ctrl to turn alignment off and keep the current rotation (snapping still works).
- [AUTO] Copy: enter `c`, then give the second point (pick, or type coordinates + Enter); or enter `b`, give a base point, then the second point. Repeat for more copies. Esc ends.
- [AUTO] Move: give the second point, or enter `b` for a different base point, then the second point. Esc ends.
- Several at once: Shift-click the same Alignment grip on each object, then click that grip again on one object to make it the base grip. If the base item aligns to an object, the others take the same rotation and keep their position relative to the base.
- Copying a device raises the circuit load. REGEN updates the panel schedule for that circuit. If the new load passes the load category limit, the schedule needs a new row (Update Panel Schedule). A diagonal line through the schedule means it is out of date. ([G:1CFDC450](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1CFDC450-4314-4B6B-89AF-01E7AEE4CCC1))

## 5.8 Panels and panel links

### Add panels: PANELADD ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD))
- [AUTO] PANELADD (PANELADDSELECTED is also listed; no prompts given). Ribbon: Home tab > Build panel > Panel. Or a Panel tool palette tool (preset properties).
- To use a panel and its circuits in several drawings, create an .epd and link the drawings to it.
- Properties palette: an icon marks add-only properties.
- Style: Properties palette > Basic > General > Style > click the image. Styles Browser opens with Object Type = Panel. Search scope:
  - current drawing: Drawing File = Current Drawing
  - all open drawings: Drawing Source = Currently Open Drawings, Drawing File = All Drawings
  - open drawings except current: Drawing Source = Currently Open Drawings, Drawing File = All Without Current Drawing
  - content library: Drawing Source = Content Library Drawings, pick the file in Drawing File
  - default content location for panels, or a template: Drawing Source = Content Library Drawings, Drawing File = Manage Content Library, then add a folder or drawing in the Content Drawings Library dialog
- Location: Align to objects, Justification and Elevation work as for devices (5.7).
- Advanced > System: pick a system. The button beside it opens Styles Browser with Object Type = Electrical System Definitions.

Design Data fields
- Name (unique). Rating.
- Voltage phase-to-neutral and phase-to-phase: lists from Electrical Preferences > Voltage Definitions.
- Phases: 1 or 3. Selectable only BEFORE the panel is placed; read-only after insertion.
- Wires: 3 or 4 (3-phase panels only).
- Main type: Main lugs only (MLO) or Main circuit breaker (MCB). Main size (amps). Design capacity.
- Panel type: ANSI or ISO. Enclosure type (typed). Mounting: Surface, Recessed, Floor. AIC rating. Fed from. Notes.
- Circuits: Create circuits = Yes > Circuit Settings button (5.6).

Insert
- Align Yes: snap to an object (for example a wall), click. Align No: click the insertion point; rotate by cursor or typed degrees, click (or Enter for default rotation, then click). Repeat; change palette values for different panels; Enter ends.
- Panels can be located first and circuited later, or created with their circuits. ([G:D279670B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D279670B-DEC4-4402-9CB3-EE55D3ABBFB3))

### Link panels (feeders) ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD), [G:D7B332A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D7B332A9-3E01-4F70-83F0-56FB7CEC43F6))
- Route 1: select the panel > right-click > Connect To > pick the target panel, OK (valid connections show in bold) > pick the method, OK.
- Route 2: select the panel > Panel tab > Connections panel > Connect To Other Panel. First Panel to Panel connection dialog: the panel that will be fed by another panel. Second dialog: the method. OK.
- Methods: Circuit breaker in panel (sub-fed from an existing circuit in the linked panel); Feed-thru lugs; Subfeed lugs (written "Sub-feed lugs" on [G:D7B332A9](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D7B332A9-3E01-4F70-83F0-56FB7CEC43F6)); Subfeed breaker; Panels are connected through a transformer (for panels of different voltages).
- The sub-fed panel shows indented in the left-pane tree. (inference) This is the Circuit Manager tree.
- After linking, use Circuit Manager to move panel demand and connected load totals per load category from one panel to another.
- Limits: linking a panel back to the panel that feeds it shows a warning symbol (circular reference). A panel cannot be linked to more than one panel at a time. Each panel can be connected to only once through feed-thru lugs, subfeed lugs or subfeed breaker. The circuit breaker option works only while circuits are available.
- Any circuit add or delete means existing panel schedules need updating.
- Unlink: select the panel > Panel tab > Connections panel > Remove Connection To.

### Panel styles ([G:1A1DBC84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1A1DBC84-1338-4488-8607-B49603D3B030), [G:8A1DF64B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8A1DF64B-004E-4554-980A-B8B70784EBC7))
- Open: Manage tab > Style & Display panel > Style Manager > Electrical Objects > Panel Styles > style; or select a panel > Panel tab > General panel > Edit Style drop-down > Edit Style.
- Connectors tab: Description; Domain = Electrical; Connection Point X, Y, Z or "Add Center Points from View Blocks in Top View"; Add and Remove buttons. DANGER: removing a connector removes it from every instance of the style and can break circuit connectivity.
- Design Rules tab: only Wire Cleanup (how wires show at panels). To move panels to another layer, remap layers with Layer Manager.
- [AUTO] PANELMODIFY is listed for modifying devices and panels; no prompts documented. With an .epd, save and close it after changing panel properties inside it. ([G:7EA95A2F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7EA95A2F-1959-422A-B09A-634DB7D2D165))

## 5.9 Wires, home runs and wire sizing

### Basics ([G:7208F408](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7208F408-8718-470F-BCF9-723E4F367AC8), [G:11F65058](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11F65058-40C4-4233-B7C6-C0A5CEE8193B))
- Wires show circuits graphically. They are not needed to assign devices to circuits or to see loads.
- Wires are anchored to devices: moving a device stretches its wires. Endpoint grips cannot move a wire end off a device. ([G:2D38797D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2D38797D-A4D5-4106-B76E-3AE2CB2845CB))
- Wire styles separate wiring setups. Examples: 1-pole (general lighting, power distribution), Multi-pole (equipment, power distribution), Low voltage (security, fire alarm, communication). The style sets wire material, number of wires and annotation. Labels can show a run's wire style or circuit. Wire style settings are in 5.13.

### Add wires: WIREADD ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD))
Three ways: draw by hand (wire tool, or the + grip on a device); generate with a command (a circuit must be set in the wire properties); or Styles Browser (search Wire, import, add).
1. Start: Home tab > Build panel > Wire; the + grip on a device; a Wire tool palette tool (preset properties); [AUTO] type `wireadd`; or Styles Browser > Object Type = Wire > Gallery. An icon flags add-only properties.
2. Basic > General > Style: a wire style in the drawing. Do NOT use the supplied Standard style if you want instant sizing: by default it has no wire material, and sizing needs one.
3. Description: free text.
4. Location > Segment: Line; Arc (Height, Offset Left or Right); Snake (arcs on alternating sides; Height, Offset); Polyline (lines with filleted corners; Radius); Chamfer (plateaus; Height, Offset); Spline (curve through or near points; Height, Offset). For arc, snake and spline, picking a point between two devices overrides Height and Offset, to route around walls or equipment.
5. Elevation: Preset Elevation or typed Elevation. Elevation differences of devices, wires and panel give circuit length, computed only when the panel and all devices on the circuit are in the current drawing.
6. Advanced > System: opens Styles Browser with Object Type = Electrical System Definitions (same search scopes as for panels, 5.8).
7. Design Data > Circuit: Unassigned, or "Show circuits from panel" (panels in the drawing or .epd), then Circuit. Instant sizing needs a Power and Lighting circuit; Unassigned or other system types are not allowed. Devices go on the circuit unless already on one (then Circuit cannot change). Multi-branch circuits: change the circuit while adding wires, or wire two devices that are on different circuits.
8. Dimensions: the instant sizing button sizes from the wire style material and temperature rating, the Power and Lighting circuit rating, and the drawing ambient temperature (Circuiting tab). Or pick or type hot, neutral, ground and isolated ground sizes; which apply depends on the wire style specifications.
9. Insert by hand with electrical snaps (the palette shows Connected circuits and Connected load; multi-branch shows all). Or [AUTO] type `g` at the prompt to generate wires for all devices on the specified circuit.
10. Home run: press Enter and click toward the panel (its look comes from the wire style annotation). Press Enter twice to end with no home run; add it later.

+ grip behavior ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD))
- The wire takes the chosen connector's properties. System = the connector's system type; if undefined, the last system used in that drawing or session. The Systems list is filtered to the connector. The palette also shows Circuit (unless unassigned) and Panel (from the circuit).
- Default circuit for an unassigned connector: Power and Lighting = first circuit with no load, or with the least load; Other = first circuit of that type; General = first circuit. Panel list = last used panel, or All if Circuit is undefined.
- Wiring devices onto a circuit updates it and checks overload (warning once per drawing session).

### Home runs ([G:F7A65629](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F7A65629-1D39-4FAB-86A5-2A254683703C))
- A home run is a wire showing the circuit running to its distribution point, usually a panel. It need not touch the panel; draw it toward the panel. Its look comes from the wire style annotation.
- Add later: select an existing wire on the circuit > Wire tab > General panel > Add Selected; with electrical snaps pick a device on the circuit; Enter; click toward the panel. (inference) Add Selected runs WIREADDSELECTED, listed on [G:11F65058](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-11F65058-40C4-4233-B7C6-C0A5CEE8193B).
- A device on circuits from two panels (for example normal and emergency) needs one home run to each panel, so each can be tagged with its panel. Give the style's connectors different locations.

### Convert geometry: WIRECONVERT ([G:070A2ED0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-070A2ED0-1975-4CD6-AE03-6BA98CE79EBB))
- [AUTO] WIRECONVERT, or select a line, arc or polyline > right-click > Convert to Wire.
- Prompt: Enter or `n` (no) leaves the layout geometry in the drawing; `y` (yes) erases it.
- Then the Modify Wires dialog opens (system, voltage and other properties) > OK. Blocks a script.

### Modify wires
- Layout: select the wire, click a vertex Location grip, move it, click, Esc. ([G:2D38797D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2D38797D-A4D5-4106-B76E-3AE2CB2845CB))
- Properties palette ([G:CA0971E0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA0971E0-0ED6-4975-8EC9-6BB09E2B7434)). Basic: Description, Layer, Style (from styles in the drawing), Location > Preset elevation or Elevation. Advanced: System; Dimensions (instant sizing button, or hot, neutral, ground, isolated ground sizes).
- Flip tick marks: select the wire, click a Flip grip (ticks flip toward the arrow), Esc. ([G:A86D428F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A86D428F-5743-4FF5-9453-11346BA7B1E3))
- Move tick marks: select the wire, click the tick mark Location grip, slide it along the wire, click, Esc. ([G:91711A57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-91711A57-146F-4430-A865-115A01AB5116))
- Whether ticks show on segments and home runs is a wire style annotation setting. ([G:A86D428F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A86D428F-5743-4FF5-9453-11346BA7B1E3), [G:91711A57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-91711A57-146F-4430-A865-115A01AB5116))
- Draw order decides which crossing wire shows the break or overlap: Home tab > Modify panel > Bring to Front drop-down. ([G:71EA1D84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-71EA1D84-F3E3-4F43-A37F-16C643C84DE9))

### Wire sizing
- Two ways, for circuited wire runs: instant sizing while adding or modifying wire (from the circuit rating), or Circuit Manager for any wires on a circuit. Basis: NEC 2002 Handbook Table 310.16 (current-carrying conductors) and Table 250.122 (grounding conductors). ([G:524859D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-524859D8-3899-46BB-900B-F0189C59CB41))
- Instant sizing rules: ALL selected wires need an assigned circuit of system type Power and Lighting AND the same wire style. Result uses the wire style material and temperature rating, the circuit rating, and the drawing ambient temperature. ([G:CA0971E0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CA0971E0-0ED6-4975-8EC9-6BB09E2B7434))
- Prerequisites for any sizing: wire already added to the devices on the circuit; the wire style has a conductor material (copper or aluminium) picked from the list. Typing a material in does not work for sizing. ([G:1140E66B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1140E66B-6A72-47EB-BADF-07FA1DE2800D), [G:74BBFF4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-74BBFF4D-0DC1-4D2D-ACAB-0DBAB2852DC1))
- Circuit Manager route ([G:1140E66B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1140E66B-6A72-47EB-BADF-07FA1DE2800D)): select a wire > Wire tab > Circuits panel > Circuit Manager drop-down > Circuit Manager. In the right pane select the circuit(s) with Shift or Ctrl (picking a panel in the left pane selects only the first circuit in the list). Click Calculate Wires. Calculate Wire Sizes dialog:
  - Check only: compare, change nothing; opens the Calculate Wire Size - Results dialog.
  - Change Under dimensioned: resize undersized wires.
  - Change All: resize undersized and oversized wires.
  - Resized wires update in the right pane under Wires.
- Ambient temperature (Electrical Preferences > Circuiting tab) sets the ampacity correction factor. ([G:818FC278](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-818FC278-6D3E-4354-900B-B59030F8224D))
- The 2027 page still cites the NEC 2002 Handbook. (inference) Check auto sizes against the code edition in force before relying on them.

## 5.10 Conduit and cable tray

### Where settings live ([G:7DD7AE49](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7DD7AE49-D39F-4D28-9BDC-CF626D1D61B6), [G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9), [G:BBC62D0F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BBC62D0F-E0F8-41AF-B50E-DD09DCC2CD72))
- Conduit and conduit fittings: Properties palette. Cable tray: Add Cable Trays dialog. Cable tray fittings: Add Cable Tray Fittings dialog.
- Layout preferences are stored in the drawing. The sample templates carry default preferences so layout can start at once; custom templates can hold company or project preferences.
- [AUTO] CABLETRAYPREFERENCES: Cable Tray Layout Preferences dialog. Also from the button in the Add Cable Trays dialog, or Manage tab > Preferences panel > Cable Tray. Blocks a script.
- [AUTO] CONDUITPREFERENCES: Conduit Layout Preferences worksheet. Also the Preferences button on the conduit Properties palette, or Manage tab > Preferences panel > Conduit. Blocks a script. ([G:2376C681](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2376C681-C546-4984-ABCB-B325D95D6367))

### Cable Tray Layout Preferences dialog
Routing tab
- Cable Tray Layout Rise/Run: choose Angle or Fraction, enter Rise/Run in that format; for Angle also set the increment in degrees. Slope is in the Z direction of the current coordinate system. The value becomes the default in Add Cable Trays. ([G:AEF1F66D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AEF1F66D-5DE3-400E-B2AA-89EB782E0E13))
- Automatically create riser at new Elevation: default selected. ([G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9))
- During Layout > Cable Tray Length: cuts tray into set lengths while drawing. ([G:32700FD2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-32700FD2-B398-4548-A483-D79187119A8E))
- Offset group > Justification: default Center on Horizontal and Vertical with Offset A = 0 and Offset B = 0 (centerlines run through the picked points). Left or Right (horizontal) and/or Top or Bottom (vertical) put one or two sides on the picked points. Offset A and/or Offset B offset the tray from the picked points. Preview at right. ([G:B47F66BD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-B47F66BD-A1BC-4BE5-AA7A-CAEAE9CAB65F))

Annotations tab ([G:6F37F116](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6F37F116-CF8C-4745-914E-E9F461739497))
- Cable Tray Pattern: line pattern type (hatch, vertical or 45-degree lines) + Spacing.
- Labels and Flow Arrows: a style and a layout method; labels only, arrows only, or both.

Connections tab ([G:3AE08B50](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3AE08B50-8E72-436F-A7CD-19FFA153DB17))
- Connection Style: confirm Cable Tray Connector Style is set.
- Connect with Cable Tray > Use Fitting: checked = a fitting goes in where segments meet; cleared = direct connection.
- Connect with Elbow > Use Tee: checked = elbow replaced by a tee when a segment joins it.
- Connect with Tee > Use Cross: checked = tee replaced by a cross.

### Conduit Layout Preferences worksheet ([G:2376C681](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2376C681-C546-4984-ABCB-B325D95D6367))
- Slope format: Angle (degrees); Percentage where 100% = 45 degrees; Percentage where 100% = 90 degrees (the page lists two rows both named Percentage); Rise/Run (a fraction, for example 1/48).
- Drawing units for Rise and Run. Slope-format units come from the current profile and the Drawing Setup dialog.
- Ratio divider: slash (/) or colon (:).
- Automatically create riser at new Elevation: selected by default. A vertical rise is drawn when you enter a new elevation while routing. (inference) Cleared = no riser.
- Label style and flow arrow style (None skips the layout method). Layout method: By quantity (number per straight segment) or By distance (interval length; a segment shorter than the interval gets no automatic label).

### Draw a run ([G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9), [G:7DD7AE49](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7DD7AE49-D39F-4D28-9BDC-CF626D1D61B6))
- [AUTO] CABLETRAYADD (cable tray). [AUTO] CONDUITADD (conduit; listed on [G:2FE64946](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2FE64946-87EB-48E7-A15D-F034E341C05C)). Prompt sequences not documented.
- Ribbon: Home tab > Build panel > Cable Tray or Conduit. Also: Styles Browser (Object Type = Cable Tray or Conduit), a tool palette tool, the Add grip, or select an object > Cable Tray or Conduit tab > General panel > Add Selected.
- System: cable tray = Add Cable Trays > System; conduit = Properties palette > General > System > browse button (Styles Browser). Predefined systems exist, for example Power - 120V and Data. The run inherits system design parameters, display properties and rise/drop style.
- Conduit routing preference: Properties palette > General > Dimensions > Routing Preference.
- Size: cable tray = Width and Height in Add Cable Trays; conduit = Properties palette > Dimensions > Nominal size.
- Elevation and offset: enter the elevation, then justification and offset (cable tray: Add Cable Trays; conduit: Properties palette > Placement). Horizontal: Left, Right or Center + distance to the horizontal object. Vertical: Top, Center or Bottom + distance to the vertical object. The icon beside Elevation (a lock, inference) stops the elevation changing. To extend at the same elevation, use the Add grip; the new segment inherits elevation and other properties.
- Angle: cable tray = Add Cable Trays > Use Routing > Elbow Angle; conduit = Properties palette > Routing > Bend angle. Pick from the list, type a value, or pick a point on the compass. The lock beside Elbow Angle / Bend angle makes every following segment use that angle.
- Riser: with "Automatically create riser at new Elevation" set, enter the new elevation.
- Slope: cable tray = Add Cable Trays > Layout Method > Use Rise/Run (value in degrees per [G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9); [G:AEF1F66D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AEF1F66D-5DE3-400E-B2AA-89EB782E0E13) gives Angle or Fraction formats); conduit = Properties palette > Routing > Slope and Slope format.
- Conduit only: the Connection details button shows flow direction and connection type for connector #1.
- Keep clicking points; fittings go in automatically from the routing preference. Default fittings can be overridden for a run. Use MEP snaps to find valid connection points.

### Start from an existing run or equipment: Add grip ([G:839A0F7B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-839A0F7B-3ABB-4D96-9551-C0ECB3DC2911))
- Select a conduit or cable tray, click the Add grip. Start at: a segment end (click the end); a segment midpoint (conduit gets a tee or takeoff per the connection set in routing preferences); an MvPart (click its connection); a fitting (click in the direction of the new run).
- Conduit: set the layout method on the Properties palette under Routing Options. From an MvPart, optionally set system and routing preference under Dimensions. The new run inherits routing preference and system of the connected object.
- Changing nominal size (conduit) or a dimension (cable tray) before the first segment inserts a transition.
- A conduit part missing from the routing preference prompts for a part substitution at the needed angle. Blocks a script.
- Cable tray from an MvPart: you must pick a System type in Add Cable Trays. From a segment or fitting, the run inherits the system.

### Branches ([G:C30CF331](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C30CF331-9793-49A0-8F0E-64AB0E89A06B))
- A branch can start anywhere along another run, not only at an end; the software inserts a fitting.
- Turn on Wire Ways Curve or Wire Ways Connector snaps. Home tab > Build panel > Cable Tray or Conduit. With the snap, pick the first segment, then the second. Properties can be changed at the command line. Close or Enter ends.
- Rise and drop symbols are inserted as needed from the rise/drop style of the run's system. Check the result with Solution Tips.

### Conduit Properties palette, Design tab ([G:21BC26DE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-21BC26DE-1DC4-4235-94DA-673094FE8754), [G:AB9E53E3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AB9E53E3-1D3B-440C-9DEF-EDF77246E4A5), [G:F8682AA3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F8682AA3-4A8D-43F2-BF5F-67895A5AD3EA))
- Used to add and modify conduit segments and fittings. Basic and Advanced groups. Basic shows the default or last stored value. With several objects selected only some properties show. Page marks: * = several conduit segments; ** = several fittings; *** = several segments, or segments with fittings.
- General: Description*; Layer*; System*; Part (click the image for the Select a Part dialog); Current size (fitting size).
- Dimensions: Connections (nominal diameter of each connector); Path angle (fitting arc angle from catalog content: conduit bend 1 to 180; conduit elbow list such as 30, 45, 60, 90); Radius of curvature (industry standard radius from the catalog, varies with size); Part; Nominal size* (trade size; fitting: Modify only) plus a lock that prevents changing it; Routing preferences* (fitting: Modify only); Specify cut length (Yes = Cut length sets each segment's cut length).
- Placement: Elevation* plus a lock that stops a segment at one elevation snapping to a segment at another; Start elevation; End elevation; Move attached segments* (keeps connectivity when elevation changes); Additional information*** (opens the Location worksheet for connector 1; changes affect all connectors); Specify rotation on screen (No = type the fitting angle in Rotation**); Justify; Horizontal and Vertical offset.
- Routing Options: Parallel bends (Concentric or Fixed radius; only when drawing parallel runs); Slope format; Slope; Bend angle (from the catalog; formerly elbow angle; its lock prevents editing in auto layout); Bend radius (its lock prevents editing in auto layout).
- Not available for parallel conduit routing: system, routing preferences, slope, slope format.
- Advanced: Additional Information > Connection details (Connection Details worksheet) and Preferences (layout preferences). Labels and Flow Arrows > Style, then By quantity or By distance (segment must be longer than the interval). ([G:F8682AA3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F8682AA3-4A8D-43F2-BF5F-67895A5AD3EA))
- (inference) Rows listed twice by name (Elevation, Size, Bend angle, Bend radius) are lock toggles for the value above them. ([G:AB9E53E3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AB9E53E3-1D3B-440C-9DEF-EDF77246E4A5))

### Parallel conduit runs ([G:D09F0D58](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D09F0D58-79EF-4170-9749-6083E18D070E), [G:FBD636A7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FBD636A7-4EA0-4E1B-B77A-F03ABB23D7C7), [G:DBD4D201](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DBD4D201-BFBE-4A25-9B12-8A0CC61C3860))
- Concentric: the bend radius applies to the baseline conduit only. The software computes inside, middle and outside radii so all follow the standard values 16", 24", 32", 40" for each bend.
- Fixed radius: the radius you give is used for every bend in the run; elbows keep their predefined radii. The same page also says all bend radii are 16" for fixed radius routing; it does not reconcile the two statements.
- Editing while routing: properties that place the baseline conduit (Justification, Compass) apply only to it. Properties that change size (Size) apply to all segments in the run. A new Elevation moves all segments being routed, keeping spacing unless that causes a conflict.
- Conflicts while routing: distance conflicts (invalid turn, elevation change) and dimension conflicts (nominal size differences). Undo to go back to the last point, or accept the suggested action; settings then carry on between segments.

### Conduit routing preferences ([G:4C03A031](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4C03A031-A1A0-44FF-AEBE-EB98C18C42C0), [G:5E1446D4](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5E1446D4-07BA-48A3-86D0-1E861FF12037))
- They make auto layout accurate: when a preference matches an industry standard or spec, the right fittings go in automatically. Auto layout can offer several routing solutions.
- A conduit part routing preference holds one or more connection types (for example set screw) across the part sizes for conduits and fittings. Page examples: set screw; threaded IMC conduit to a junction box.
- Change it while adding segments, on the Properties palette. Nominal size reflects the current preference.
- Find or apply: Styles Browser > Object Type > Electrical Objects > Conduit Part Routing Preferences; or select the object > Properties palette > Basic > Dimensions > Routing Preference button.
- Create, copy, delete [GUI]: Manage tab > Style & Display panel > Style Manager drop-down > Routing Preference Definitions. New: right-click Conduit Routing Preferences > New. Copy: right-click a preference > Copy, then right-click Conduit Routing Preferences > Paste. General tab: name, description, notes. Delete: right-click > Purge.

### Add fittings by hand ([G:2FE64946](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2FE64946-87EB-48E7-A15D-F034E341C05C))
- [AUTO] CABLETRAYFITTINGADD, CONDUITFITTINGADD, CABLETRAYFITTINGADDSELECTED, CONDUITFITTINGADDSELECTED. Prompts not documented.
- Use: add to an existing segment or run, start a run from a fitting, or customize the connection to an MvPart.
1. Home tab > Build panel > Cable Tray Fitting or Conduit Fitting.
2. Part type: cable tray = Add Cable Tray Fitting dialog, Part tab, a part type folder then a subtype (Details expands the dialog); conduit = Properties palette, click the part image, Select a Part dialog. Display/Hide additional part parameters toggles extra parameters.
3. Filter: cable tray = Part Filter tab; conduit = Filter by Dimensions.
4. Pick the part size name (cable tray) or part size (conduit).
5. Elevation: cable tray = in the Add Cable Tray Fittings dialog; conduit = OK the Select a Part dialog, then Properties palette > Placement > Elevation.
6. Pick the insertion point; the compass sets rotation.

### Modify runs
- [AUTO] CABLETRAYMODIFY is listed for modifying runs; no prompts documented ([G:5FF61976](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5FF61976-F619-4094-928D-D609A09850BF)). Runs change often: tray sizes grow, conduits get added, wiring re-routes.
- Break or merge ([G:0BEE0234](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-0BEE0234-F957-45B7-A503-96C11E55D414)): select the run > Cable Tray tab > Modify panel > Cable Tray Length, or Conduit tab > Modify panel > Conduit Length. Dialog: Apply to Cable Tray Run / Apply to Conduit Run (whole run); Break (new segment length); Merge; Select Objects; Length (type it, pick from the 10 last-used lengths, or pick points). Break cuts pieces of that length; the last piece may be shorter. Merging cannot cross fittings. Useful for counting the pieces a manufacturer must supply. Commands: CABLETRAYBREAK, CABLETRAYMERGE, CONDUITBREAK, CONDUITMERGE.
- Elevation ([G:CD861873](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CD861873-D8BF-402A-B75D-CE5ABC423FE5)): cable tray = Cable Tray tab > Modify panel > Modify Cable Tray dialog; conduit = Properties palette > Placement. Conduit: Advanced > Connection details button opens the Connection Details worksheet (location, elevation and connection type for all connectors). Then check the run; you may need segments, transitions or bends to reconnect.
- System ([G:C6F3A669](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C6F3A669-E4CD-4124-A3C8-D81F87B99012)): cable tray = Modify Cable Tray dialog; conduit = Properties palette > General > System. The system can also be changed on single connection points.
- Size ([G:2798CDB8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2798CDB8-16C2-4BBC-912D-3C4E64761331)): cable tray = Modify Cable Tray, width and height; conduit = Properties palette > Dimensions > Nominal size (a size missing from the routing preference prompts a part substitution). Then the Maintain Connection dialog: "Modify to next junction/transition" (whole run matches the segment) or "Modify to maintain connection to next part" (transition inserted, rest unchanged). Resizing a whole run joined to another run replaces the junction fitting with a transition.
- Layout ([G:D06DB315](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D06DB315-2F1F-4D14-B24E-3D8468D0A530)): Home tab > Modify panel > Move (base point, second point), or the Location grip. Copy: Cable Tray or Conduit tab > General panel > Add Selected, then start point and second point.

### Rotate fittings ([G:AA465602](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AA465602-FBF9-4B99-A671-006043641A48))
- Arrow-shaped Rotate grips turn a fitting 180 degrees (click) or 90 degrees (Ctrl + click) in the arrow direction.
- In isometric views, diamond-shaped Rotate grips turn a conduit fitting about its centerline to any angle. Click the grip, then: type the new absolute angle in the dimension input field; or drag, press Tab, type the change; or drag the grip; or type Rotation on the Location tab of Fitting Properties; or [AUTO] type the value at the command line.
- Grips show only on fittings whose connectors are on opposite ends. To keep runs connected, rotation choices may be limited or the grips hidden.
- Connected objects adjust (small length changes) to stay connected, or are disconnected if they cannot.

### Rise and drop symbols on runs ([G:70D697C7](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-70D697C7-DA1C-4FEE-B101-85FC9792544C), [G:C30CF331](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C30CF331-9793-49A0-8F0E-64AB0E89A06B))
- They show vertical segments and fittings in Top, Bottom, Left, Right, Front and Back views. Rise = an unconnected end of a vertical segment or fitting is visible in the view. Drop = vertical with no visible unconnected end.
- A run takes its rise/drop style from its system ([G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9)). Use one style per system so systems look different.
- The style and its blocks must exist in the current drawing. Keep them in templates, or build them in a content library drawing and copy them into templates.
- Rise block: make it with color, linetype and lineweight set to ByBlock; the Rise Drop display component values then apply. Drop block: make it with the real color, linetype and lineweight; the display component values for these are ignored. Visibility of both follows the Rise Drop display component.
- Block base point = symbol center. Any size: on insert it is scaled so its extents = 1 unit (1 in), then by the style.

## 5.11 Checking electrical systems
- Circuit tools give circuit and panel assignment info for one circuit or all circuits, and power totals for selected devices. With an .epd the info stays accurate across drawings. ([G:74C735A0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-74C735A0-8DAF-4C9A-9C08-46D5CFF7AA87))
- Loads total automatically only for Power and Lighting circuits. Assigning a device adds its load. ([G:DD5DCB19](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DD5DCB19-62CC-46DA-8134-30893B1F48E7))
- [AUTO] CIRCUITINFO ([G:2B682A94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2B682A94-F9CF-4045-8ACE-EF4ECE228F94)): voltage, load and length of a circuit. Select a wire or device > Wire tab or Device tab > Circuits panel > Circuit Manager drop-down > Circuit Info. If the .epd was reloaded in the current drawing, the load is the total of ALL devices on the circuit, across drawings.
- [AUTO] CIRCUITREPORT ([G:FEE46A09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEE46A09-D54D-46CC-9E53-299634C37372)): panel name, circuit name, voltage, load (VA), circuit length and number of devices for one or more selected circuits. Same Circuit Info ribbon item; Copy to Clipboard button for pasting into a spreadsheet. Circuit Manager also copies with Ctrl+C.
- [AUTO] SHOWCIRCUITS ([G:90DB44C5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-90DB44C5-C1CD-46DC-A975-9ECC701F51BC)): highlights all devices in the current drawing on the same circuit. Routes: select a wire or device > Wire tab or Device tab > Circuits panel > Show Circuited Objects drop-down > Show Circuited Objects; or right-click a device > Connected Objects > Show Circuited Objects; or in Circuit Manager select a circuit with devices > Show Circuited Devices toolbar button. Enter exits and clears the highlight.
- Show Connected Objects ([G:5E77C1BA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5E77C1BA-6598-46C6-866E-20078EA41E7A)): highlights everything connected in a run or network (lighting: devices, wires, junction boxes, switches; equipment: MvParts to conduit or cable tray runs). Select the object > its contextual tab (for example Cable Tray Fitting tab) > Modify panel > Show Connected Objects drop-down > Show Connected Objects. Enter exits.
- [AUTO] POWERTOTALS ([G:645B48DF](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-645B48DF-77C5-462E-B513-525178676F4D)): total load of a selection, even before devices are connected; groups lighting, receptacles, and others (all other types totaled together). Analyze tab > Electrical panel > Power Totals, select devices, Enter. Or select a device > Device tab > Circuits panel > Power Totals.
- Overloads: with circuiting settings on, overloaded circuits show red in Circuit Manager, and a separate option warns while you assign devices. ([G:DD5DCB19](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DD5DCB19-62CC-46DA-8134-30893B1F48E7))
- Solution Tips test conduit and cable tray runs after connecting. ([G:FF460803](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FF460803-026B-4714-8518-D0D61D53FF4B), [G:C30CF331](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-C30CF331-9793-49A0-8F0E-64AB0E89A06B))

## 5.12 Panel schedules

### What they are ([G:2F354B01](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2F354B01-0E37-49B2-B247-60E6D8F7B7CF), [G:3554BAD0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3554BAD0-7719-4214-831E-1465023D9D08), [G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3))
- Default panel schedule table styles make 5 types: 1-phase branch circuit, 3-phase branch circuit, switchboard, distribution, standard.
- Normal practice: a panel schedule sheet with no panels on it. Small projects can put schedules in a drawing that holds panels.
- A schedule can cover one drawing or circuits spanning several drawings. Panel schedules for construction documents are built from the .epd.

### Insert ([G:8F96BBF5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8F96BBF5-4CBB-4A01-ADDF-6456AC87608C))
- Electrical tool palettes set > Tag and Schedule palette > a panel schedule tool. Or select a panel > Panel tab > Circuits panel > Panel Schedule.
- Panel Schedule dialog: Panel (the list shows panels in the .epd), a panel schedule table style, Show panels from = Electrical project database, OK. Dialog, blocks a script.
- Separate sheet: create and open a general view drawing; set Manage tab > Preferences panel > Electrical > Electrical Project Database tab > Project Database = the .epd (needed for a panel not in the current drawing); insert schedules; repeat for more on the same sheet.
- General view drawing ([G:1C875DAE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1C875DAE-3BEE-4DCA-B170-19F32937EAFE)): Quick Access Toolbar > Project Navigator > Views tab > right-click a subdirectory > New View Dwg General; name, category, template; Next; pick floors; Next; pick constructs (attached as references); OK. A reference attached as an overlay is NOT carried when the view goes on a sheet; select that reference drawing too. The view drawing is created but not opened.

### Updating ([G:6CB9613C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-6CB9613C-69AD-41ED-A3B6-88042146BB18), [G:3554BAD0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3554BAD0-7719-4214-831E-1465023D9D08))
- Schedules do NOT update by themselves.
- [AUTO] REGEN (`re`), or View tab > Appearance panel > Regenerate drop-down > Regenerate: refreshes values in all schedules in the drawing (loads up or down).
- Update Panel Schedule (select the schedule > right-click): needed when rows must be added or removed.
- Out-of-date triggers: add or delete circuits; delete a panel; link or unlink panels; attach or detach devices; change the number of load categories a panel uses; change a device phase load; change circuit properties (rating, description); change panel properties (name, rating, wires); reload an updated .epd; an xref using an older .epd than the current drawing.
- An invalid schedule shows a line drawn through it (a diagonal line). ([G:3554BAD0](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-3554BAD0-7719-4214-831E-1465023D9D08), [G:1CFDC450](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1CFDC450-4314-4B6B-89AF-01E7AEE4CCC1))

### Export ([G:5B68FCF5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5B68FCF5-0A15-418B-9EE6-F9B909FBE5EF))
- Select the schedule > right-click > Export > Export Data dialog > file name > Save. Output is a text file with a .csv extension (opens in Excel).
- Not linked: edits in the drawing or the file do not update the other.

### Panel schedule table styles and field codes ([G:FB5180B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FB5180B1-B103-4C84-9DFD-6D5AC729668D))
- Build a table matching the company schedule, then make the panel schedule table style from it. Put placeholder field codes where data should show; at generation they are replaced with values from Circuit Manager.
- The page lists field names only. It does not show the literal code text placed in a cell.
- Panel fields (34): Panel Name, Panel Rating, Panel Voltage Phase-to-Phase, Panel Voltage Phase-to-Neutral, Panel Phases, Panel Wires, Panel Main Type, Panel Main Size, Panel Design Capacity Amps, Panel Type, Panel Enclosure Type, Panel Mounting, Panel AIC Rating, Panel Fed From, Panel Connected Load Total Phase A / B / C, Panel Notes, Panel Load Category Name, Panel Load Category Connected Load, Panel Load Category Demand Factor, Panel Load Category Demand Load, Panel Connected Load Total KVA, Panel Connected Load Total Amps, Panel Demand Load Total KVA, Panel Demand Load Total Amps, Panel Design Capacity KVA, Panel Slots, Panel Spare Capacity KVA, Panel Spare Capacity Amps, Panel Spare Capacity Percent, Panel Phase Balance A to B / B to C / C to A.
- Circuit fields (15): Circuit Name, Circuit Description, Circuit Total Load, Circuit Rating, Circuit Voltage, Circuit Number of Poles, Circuit Phase, Circuit Load Category, Circuit System, Circuit System Type, Circuit Wires, Circuit Load Phase A / B / C, Circuit Amps.
- No field exists for MCA, MOCP or disconnect size. (inference) For HVAC units, put the unit tag in the circuit Description and keep nameplate data in a property set (5.2).

## 5.13 Styles, definitions and annotation

### Electrical system definitions ([G:A89CF529](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A89CF529-BA46-41CE-AC23-D5C7FACF182E))
- A system definition sets behavior and display for every object in a system. Name it for the real system, for example Device - Power - 277V, Device - Lighting - 120V, Conduit - Emergency. Default templates contain definitions to copy and edit.
- [AUTO] ELECSYSTEMDEF, ELECSYSTEMDEFEDIT (Style Manager, GUI).
- Manage tab > Style & Display panel > Style Manager drop-down > Electrical System Definitions. New: right-click Electrical System Definitions > New, type a name, Enter. Copy: right-click a definition > Copy; right-click Electrical System Definitions > Paste; right-click the copy > Rename. Configure on the right-pane tabs (same kind of properties as systems in other disciplines).
- Conduit and cable tray runs inherit design parameters, display properties and rise/drop style from their system. ([G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9))

### Load category definitions ([G:CF01E9D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-CF01E9D8-1D16-419D-863F-261C10CDD6E6))
- [AUTO] LOADCATEGORYDEFINITIONS (Style Manager, GUI).
- A demand factor turns connected load into estimated demand load, for a realistic demand estimate and to keep circuits from being overloaded.
- Demand factor types: constant value; constant for all motors except the largest; varies with the load total; varies with the quantity of objects. Each factor is a value multiplied by the load.
- Page examples: lighting, factor 1.00, 10 lights x 60 VA = 600 VA; a constant factor of 0.5 gives 300 VA; a quantity-based factor with a minimum of 0.72 (for example elevators) gives 432 VA. A 20,000 VA receptacle load might use a 15,000 VA demand depending on local code. Building codes guide the values.
- Load categories are assigned to device connectors. Estimated demand load shows in Circuit Manager and the panel schedule; the schedule also lists the load for each load category. Default templates contain load category styles to copy and edit.
- Manage tab > Style & Display panel > Style Manager drop-down > Load Category Definitions; right-click Load Category Definitions > New; type a name, Enter; select it; General tab = description; Demand Factor tab = pick the type, then enter the value(s).

### Wire styles
- [AUTO] WIRESTYLE, WIRESTYLEEDIT (Style Manager). Open: Manage tab > Style & Display panel > Style Manager > Electrical Objects > Wire Styles > style; or select a wire > Wire tab > General panel > Edit Style drop-down > Edit Style. ([G:EBB66DBE](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EBB66DBE-DB1C-430E-93EF-798B9FFA8D1D), [G:74BBFF4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-74BBFF4D-0DC1-4D2D-ACAB-0DBAB2852DC1))

Specifications tab ([G:74BBFF4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-74BBFF4D-0DC1-4D2D-ACAB-0DBAB2852DC1))
- Sections: Hot (conductors), Neutral, Ground, Isolated Ground. The page does not list the Hot or Ground fields.
- Neutral: Match hot (enter "Size of hot in %", the neutral size as a percent of conductor size) or Specify neutral (Material, Insulation, Temp. Rating).
- Instant sizing uses the material and temperature rating stored here. Pick the material from the list; a typed material does not work for sizing.
- The supplied Standard style has no material by default; do not use it for instant sizing. ([G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD))

Annotation tab ([G:71EA1D84](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-71EA1D84-F3E3-4F43-A37F-16C643C84DE9))
- Tick Marks: symbol type, size and angle for conductor, neutral and ground. Distance: spacing between conductor and neutral ticks, or neutral and ground ticks. Display on wire segment; Display on home run; paper distance between ticks of the same kind.
- Home Run Arrow: arrow style and size; Display one arrow for each circuit.
- Crossings: as is, overlap, or break. For overlap or break: Break/Overlap Paper Width and Break/Overlap Priority (a number). Draw order decides which wire shows the overlap or break.
- Connections: node symbol type and size at wire junctions.
- Tick marks always show in plan views unless turned off with Edit Display Properties on the Display Properties tab (Style Manager or Wire Style Properties dialog).

### Creating styles and content libraries
- Style Manager entry points ([G:160FDE57](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-160FDE57-8802-4AB7-ACD6-4C6D73BA873B)): Manage tab > Style & Display panel > Style Manager drop-down, then by workspace: Electrical Device Styles, Electrical Panel Styles, Wire Styles (Electrical). For conduit, cable tray and other content: Style Manager, then click + to open the domain type and reach the sub-domain styles.
- New blank style: right-click the category (for example Device Styles) > New > name > Enter. Copy: right-click the style > Copy; right-click the category > Paste; right-click the copy > Rename. General tab: description, Apply. Then Design Rules, Views, Connectors, Display Properties.
- A style made in Style Manager is saved only in the current drawing. To reuse it, build it in a library drawing (example name: Project ABC Ortho Iso.dwg; name it to show orthographic plus isometric, or orthographic only). The library is reachable while drawing if it sits in a folder set as a default location for style-based content, or in a subfolder. ([G:F28CE47C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F28CE47C-7E44-44F0-8A3E-9350855BE287))
- Supplied libraries: `\ProgramData\Autodesk\MEP <version>\enu\MEPContent` (the page shows no drive letter; (inference) normally on C:). Copy the originals before customizing. ([G:F28CE47C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F28CE47C-7E44-44F0-8A3E-9350855BE287))
- Workflow ([G:8D6A3E16](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8D6A3E16-A0D5-4002-8B68-80DBDBD9C110)): 1. Create or open the library drawing. 2. Make at least one AutoCAD block for a style view (needed for device, panel, schematic symbol and plumbing fitting styles). 3. Create the style in Style Manager and assign blocks to its views. 4. Add the content to categories. 5. Save and close.
- Block to device style tools (dialogs only; no command-line form given): Conversion Script dialog (a script holding style values and references to the block drawings) ([G:261E76DA](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-261E76DA-8478-4BEA-A9E0-8DDF9CD461AA)); Conversion Template dialog (default values for the script) ([G:EE923D23](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE923D23-85A7-4611-BEC4-275926E56AE0)); Edit Script dialog ([G:BD8AC8BD](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BD8AC8BD-7F8F-45BF-AEC1-BCBA70AE12A1)); Batch Convert dialog (converts a set of blocks to device styles or schematic symbol styles) ([G:2BA82EA2](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2BA82EA2-2CB0-48AD-8ABD-1E615B16671E)); Decompose dialog (turns device styles back into style settings plus blocks, for customizing existing styles) ([G:8E0806E8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8E0806E8-0F4D-4D1B-BC54-EBE95FC6D1F7)).
- Also see: device style Design Rules and Classifications (5.7), panel style connectors and design rules (5.8), connector styles (5.3).

### Annotation ([G:DC91ECC8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DC91ECC8-731E-46F1-A4C5-8B41AC0CE73B), [G:2A7CBA1B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2A7CBA1B-AFEF-4032-A1F6-6BE88380BD00), [G:E7CCD48A](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-E7CCD48A-8EEB-419E-A63F-E61EF8363FAD), [G:D279670B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D279670B-DEC4-4402-9CB3-EE55D3ABBFB3))
- Labels can be added by hand to wires, conduits and cable trays. Layout preferences can add labels automatically to cable tray and conduit as they are drawn (5.10).
- Devices: set property sets and tags in device tool properties so they attach as devices are added. Property set = user-defined group of related properties (part number, manufacturer). Tag = symbol that shows property set data on an object. Both can also be set by hand in the Properties palette when adding devices.
- Home run tags can be added to wire runs to show panel and circuit. ([G:D279670B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D279670B-DEC4-4402-9CB3-EE55D3ABBFB3))
- A schedule of tagged conduit and fitting parts can be added. Systems on cable tray and conduit give a shared look and behavior across layouts, for example one group of runs as a power and lighting system and another as a general system. ([G:FF460803](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FF460803-026B-4714-8518-D0D61D53FF4B))
- Panel schedules: 5.12.

## 5.14 Troubleshooting, source conflicts and gaps

### Electrical tab or tools missing from the ribbon ([KB:000252979](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Tabs-or-panels-are-missing-from-the-ribbon-in-AutoCAD.html))
- In short: a missing Electrical tab is usually a ribbon, workspace, profile or customization-file problem, not a missing feature. Check that the tab is switched on and in the current workspace, that the MEP profile (not a plain AutoCAD profile) is current and the MEP toolset is actually installed, then reload or reset the CUIx; reset to defaults or reinstall only as a last resort. The linked article has the full checklist.

### Where the pages disagree
- Command names: concept pages tag DEVICE, PANEL and WIRE ([G:5DF43123](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-5DF43123-5D3A-4820-B263-FE5E0A0FCC80), [G:4BB2BA8F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4BB2BA8F-9CBB-49F9-B2B7-B29F3D7F59A7), [G:7208F408](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-7208F408-8718-470F-BCF9-723E4F367AC8)); task pages tag DEVICEADD, PANELADD and WIREADD ([G:274579A5](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-274579A5-C3D2-44A8-83A4-D9D2194CC23B), [G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD), [G:377253D3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-377253D3-8DF5-4D4A-9093-F1D9BE05B2DD)). Use the ADD forms.
- CIRCUITREPORT ([G:FEE46A09](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FEE46A09-D54D-46CC-9E53-299634C37372)) and CIRCUITINFO ([G:2B682A94](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2B682A94-F9CF-4045-8ACE-EF4ECE228F94)) both point to the ribbon item Circuit Info.
- Is an .epd required? Needed for every drawing with circuits ([G:821C23DC](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-821C23DC-6E17-4DDB-8782-8CC618B72670), [G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3)) vs circuits can be stored in the same drawing as their panel ([G:EE8C9967](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-EE8C9967-7534-4B3D-8BF8-B39DCC9C8D27)). The prompt for an .epd when circuits are made ([G:DF533E20](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-DF533E20-D5AB-4854-831A-1D029DD42F58)) suggests it is required in practice.
- Where circuits are edited:
  - Circuit Manager can be opened from the panel drawing or any linked drawing to view and manage circuits ([G:606D5ABB](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-606D5ABB-97DC-453C-9BE4-0A54F8FCF3A3)).
  - Circuits cannot be edited from a linked drawing; open the .epd, edit, save and close it ([G:8DD4A3F1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-8DD4A3F1-4991-4A7A-966E-4EB392582974)).
  - Configure circuit settings only in the drawing that contains the circuits ([G:BFBB8289](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BFBB8289-3F8B-4AC4-8D38-632F3810561B)).
  - With an .epd you can edit circuit settings only from the current drawing, not for other linked drawings ([G:744FDF65](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-744FDF65-26E9-4AA3-AE6D-E60E2B680511)).
  - Configuring a circuit used by devices in other drawings prompts you to open and save them ([G:1514F07C](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-1514F07C-E841-4D37-B318-752A43D9A430)).
  - (inference) Safest: edit circuits only in the drawing that holds them, with the other linked drawings closed, then reload elsewhere.
- Locking: some circuit properties edit only while no devices are on the circuit ([G:F54B931F](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-F54B931F-7A38-43EA-A9DA-35C79448470F)); many settings lock after the first device is assigned ([G:BFBB8289](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-BFBB8289-3F8B-4AC4-8D38-632F3810561B)). Consistent in effect.
- Cable tray slope: "Use Rise/Run, value in degrees" ([G:06FB2F66](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-06FB2F66-D26F-4DE6-99AF-0ECCC97849C9)) vs a choice of Angle or Fraction format ([G:AEF1F66D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AEF1F66D-5DE3-400E-B2AA-89EB782E0E13)).
- Fixed radius parallel conduit: the radius you give is used for every bend, and also "all bend radii are 16 inches" (both [G:D09F0D58](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-D09F0D58-79EF-4170-9749-6083E18D070E)).
- Conduit Layout Preferences lists two slope formats both named Percentage (100% = 45 degrees and 100% = 90 degrees) ([G:2376C681](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-2376C681-C546-4984-ABCB-B325D95D6367)).
- Conduit palette wording: the bend radius lock is described as "bend angle", and elbow Path angle values are called radius values ([G:AB9E53E3](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-AB9E53E3-1D3B-440C-9DEF-EDF77246E4A5)). The routing preference page says "select a duct" for conduit ([G:4C03A031](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-4C03A031-A1A0-44FF-AEBE-EB98C18C42C0)).
- Circuit Settings: "less than the number of slots" does not say whether each count or the sum is compared ([G:A6F22F2B](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-A6F22F2B-5DDE-49EB-A684-53629EF643CD)).
- Wire sizing on the 2027 page still cites the NEC 2002 Handbook tables ([G:524859D8](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-524859D8-3899-46BB-900B-F0189C59CB41)).

### Gaps (not documented in these sources)
- Hyphen command forms, system variables, and COM, AutoLISP or .NET members for devices, panels, circuits, wires, conduit, cable tray or the .epd.
- Prompt sequences for DEVICEADD, PANELADD and WIREADD beyond the keywords in 5.1, and for CABLETRAYADD, CONDUITADD, the fitting commands, break and merge, CABLETRAYMODIFY, PANELMODIFY, CIRCUITRELOADPROJ and MULTIPLECIRCUITSCREATE.
- Whether an HVAC MvPart can be put on a circuit (5.2).
- What Load Sub-category Motor changes in the calculations.
- The literal syntax of panel schedule field codes ([G:FB5180B1](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-FB5180B1-B103-4C84-9DFD-6D5AC729668D)).
- The Hot and Ground fields of the wire style Specifications tab ([G:74BBFF4D](https://help.autodesk.com/view/BLDSYS/2027/ENU/?guid=GUID-74BBFF4D-0DC1-4D2D-ACAB-0DBAB2852DC1)).
- (inference) Before scripting any of these, probe in a scratch drawing and record the real prompts and results.
