# 14 - AutoCAD Output I: Sheet Sets, Transmittals, Drawing Compare, Text, Leaders, Tables, Blocks and Attributes

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

This section covers the annotation and packaging side of a construction drawing set in AutoCAD 2027, the platform under AutoCAD MEP 2027: text, text styles and fonts, MTEXT format codes, annotation scale, multileaders, tables, fields, blocks and attributes, attribute extraction, sheet sets, publishing, eTransmit and Archive, DWG Compare, hyperlinks, signatures and load security.
For each command it says what a script can drive (command line, .scr, AutoLISP, COM) and what opens a dialog or palette that stalls an unattended run.
Most source pages document dialogs only. Where no command-line form is documented, this section says so. Test those before scripting them.
Legend: (G:...) links open the AutoCAD 2027 help page cited. [AUTO] = can be driven from the command line, a script, AutoLISP or COM; [GUI] = needs a dialog or palette; (inference) = not stated by Autodesk.

## Contents
- 14.1 Automation cheat sheet
- 14.2 Single-line text (TEXT), control codes, symbols
- 14.3 Multiline text (MTEXT)
- 14.4 MTEXT inline format codes and the alternate editor
- 14.5 Text styles and fonts
- 14.6 Finding, checking and rescaling text
- 14.7 Annotation scale and annotative objects
- 14.8 Leaders and multileaders
- 14.9 Tables
- 14.10 Fields
- 14.11 Blocks and attributes
- 14.12 Attribute extraction (ATTEXT, DATAEXTRACTION)
- 14.13 Sheet sets
- 14.14 Publishing a drawing set
- 14.15 eTransmit and Archive
- 14.16 Drawing compare
- 14.17 Hyperlinks, digital signatures, load security, passwords
- 14.18 Notes for DXF writers (ezdxf)
- 14.19 Conflicts between source pages

## 14.1 Automation cheat sheet

### Command-line routes the sources document
- [AUTO] TEXT: insertion point (ENTER = place just below the last text), height (skipped when the current style has a fixed height), rotation angle, then text lines. ENTER on a blank line ends ([G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5)).
- [AUTO] MLEADER option keys: `o` `l` `s` = straight leader ([G:CD496790](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CD496790-85A6-46CA-83F3-B113A6BF4F3D)); `o` `l` `t` `p` = spline leader ([G:4F382D40](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F382D40-A4C8-4C3E-B416-E7D53C92558E)); `c` `m` = turn an existing mtext into a leader ([G:9E772A74](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9E772A74-598C-4419-8B88-B8B7BFE697E8)). The straight and spline pages disagree on the steps; probe the live prompts first.
- [AUTO] MLEADERALIGN: select, ENTER, start point, optional `s` then Distribute / Use Current / Make Parallel, end point ([G:D4DDF671](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D4DDF671-9569-4891-A326-56A95DA683D3)).
- [AUTO] MLEADERCOLLECT: select in the order wanted, the LAST one keeps its landing, ENTER ([G:89691A32](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-89691A32-F357-42DC-A537-EEEFCA38F01F)).
- [AUTO] SCALETEXT: select, ENTER, justification option or ENTER to keep, `s`, scale factor ([G:05CC8143](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-05CC8143-FDA8-483D-927E-2469314EFFF7)).
- [AUTO] 'SPACETRANS: transparent at any distance prompt while working on a layout (not on the Model tab, not in a perspective view); turns a paper distance into model units ([G:C0A07C95](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C0A07C95-F2DA-46DE-BEBF-4E7407D708BC)).
- [AUTO] ATTSYNC: `name` then the block name; or `?` to list blocks; or ENTER and pick a block ([G:889213DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-889213DA-A3AF-4020-89F0-1E5049AD26EC)).
- [AUTO] UPDATEFIELD: select objects, ENTER; every field in them updates ([G:41B09208](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-41B09208-E652-460A-B6EA-9B9A5FAAEB68)).
- [AUTO] STYLE font answer: `font,bigfont`, `font,`, `,bigfont`, or `font` ([G:CBC3F683](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CBC3F683-06F3-4B9C-8747-D01F3C262956)).
- [AUTO] Variables set by typing the name: FONTALT ([G:C0898D69](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C0898D69-A0DB-4C3E-992A-B06A8961E878)), MTEXTED ([G:9083A065](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9083A065-0CED-4BBC-A998-E031E7A57726)), DCTMAIN and DCTCUST ([G:C717CC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C717CC2C-C0D5-411A-B607-CFDE4C1DC9FD)), ANNOMONITOR `-2` ([G:DE2691C0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DE2691C0-9E3D-4D6F-8FB5-1709AE4969FD)), SSMOPENMODE `1` ([G:E6B489F6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E6B489F6-C969-4EC8-8961-51DB5BDBD89C)).
- [AUTO] Hyphen forms that exist but whose prompts these pages do not give: -COMPARE ([G:A03EE801](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A03EE801-F912-4D89-8532-454FD6571A08)), -FIND ([G:03A48719](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-03A48719-9C75-4BBB-BFE9-4692BE5A591F)), -ATTEDIT ([G:520405D3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-520405D3-C7BB-4E20-A15B-CFD665483868)).
- [AUTO] ACTIVITYINSIGHTSOPEN opens the version history palette ([G:8F5A2620](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8F5A2620-D59B-42B4-AA20-E0DD6701FB91)).

### Dialog or palette only in these sources
TABLE, TABLESTYLE, TINSERT, DATALINK, MLEADERSTYLE, QLEADER Settings, the MTEXT editor, STYLE, FIELD, ATTDEF, BLOCK / BMAKE, BATTMAN, BATTORDER, EATTEDIT, ATTEDIT, ATTEXT, DATAEXTRACTION, SPELL, FIND, OBJECTSCALE, SHEETSET and all Sheet Set Manager dialogs, NEWSHEETSET, OPENSHEETSET, PUBLISH, ETRANSMIT, ARCHIVE, COMPARE (file dialog), XCOMPARE, HYPERLINK, DIGITALSIGN, SECURITYOPTIONS.
(inference) Drive these through COM or AutoLISP object properties, a template DWT that already holds the styles and blocks, or a tested hyphen form.

### Prompts and dialogs that can appear mid-run
- Missing SHX font: after the font mapping table, the style's font and FONTALT all fail, AutoCAD prompts for a new font. Missing .pfb: prompt after the mapping table and FONTALT ([G:928DF015](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-928DF015-1E04-4CC2-AF1B-0037548DFBAE)).
- Out-of-date data extraction table: Outdated Table dialog (Update, Update All, Skip Update, Skip All Updates) ([G:E2D6EA1D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E2D6EA1D-13D1-4CDA-81BE-6BB57D31B11D)).
- DIGITALSIGN with no valid certificate: Digital Signatures dialog ([G:0497EF29](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0497EF29-5E9D-465A-9732-BDFED9911AF2)). A digital ID obtained at Medium or High security shows a message on EVERY file signed ([G:5F3F9549](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F3F9549-C425-4B77-BA3C-B9B95D6C6F39)).
- SECURELOAD = 1: warning when an executable loads from outside TRUSTEDPATHS ([G:C108E81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C108E81C-7A06-477C-A5F8-10AA2FDEB050)).
- Transmittal or archive file name set to "Prompt for a File Name": file dialog ([G:9A2F96E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A2F96E5-34D1-4504-A5F3-54BCD410041D), [G:5DBC2E1E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5DBC2E1E-532E-48F5-B921-26DAC8362D85)).
- Sheet set DST over 6.3 MB: modal warning and it will not open ([G:E6B489F6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E6B489F6-C969-4EC8-8961-51DB5BDBD89C)). Same files reached through different drive letters: prompt to resave the sheet set ([G:577D8EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-577D8EA0-85F2-4829-B4F9-8CAD6F7AAACC)).
- Sheet added to a subset: prompt to update the sheet list table ([G:AF75182F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AF75182F-F6B0-4AEC-BBC1-5B82483160CA)).
- Block with attributes inserted in a table cell: Edit Attributes dialog opens ([G:5205DFAF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5205DFAF-7C96-4566-B7CD-AA77C48E0160)).
- Placing a callout block or a view on a sheet needs the current layer UNLOCKED ([G:87F36464](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-87F36464-0801-44B9-BF33-7430E75B4C74)).

### Settings to fix before a scripted run
- ATTDIA = 0 puts attribute prompts on the command line. Preset mode only works then ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38)).
- AFLAGS = default modes for NEW attribute definitions only ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38)).
- TEXTSIZE = mtext height when the style height is 0 ([G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3)). TEXTSTYLE = current text style ([G:32BE8580](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-32BE8580-3F05-42C2-B746-6175CA3863AF)). TEXTLAYER = default layer for new text and mtext ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).
- MLEADERSCALE = scale of non-annotative multileaders ([G:A1DA7F82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1DA7F82-690A-496E-AE70-E4B03B2FC679)).
- FIELDDISPLAY = gray non-plotting field background ([G:B9ADAE6A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B9ADAE6A-2DD1-4C44-B126-CF3FF92EBC68)).
- HYPERLINKBASE = base for relative hyperlinks; empty = current drawing path ([G:DD13DBA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DD13DBA3-8221-4485-A9E6-DF7C94DF240E)).
- SECURELOAD and TRUSTEDPATHS = executable load security ([G:C108E81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C108E81C-7A06-477C-A5F8-10AA2FDEB050)).
- Background publishing OFF for scripts that wait on output: OPTIONS > Plot and Publish tab > Publish Controls > clear Background Publishing ([G:1484D4DE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1484D4DE-BE0C-4FF6-BDA1-6F020DA3A177)).
- Named in index pages with no meaning given (look up before relying on them): CMLEADERSTYLE, MLEADERLAYER, CMDDIA ([G:6BB997D6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6BB997D6-662D-44D9-AFF8-094162DA2B84)); CTABLESTYLE, TABLELAYER ([G:CA9995D8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA9995D8-98B2-4BFB-972F-FEB0934A1E33)); CANNOSCALE, CANNOSCALEVALUE ([G:B4FDF0A4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B4FDF0A4-7936-4D64-B356-D8C2A25D78BD)); ATTREQ, ATTMODE, ATTMULTI ([G:61A6871E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-61A6871E-E74F-4959-8281-934C77D1EBF4)); FIELDEVAL ([G:2776142F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2776142F-A289-4ABE-96ED-ABC3518B82A9)).

## 14.2 Single-line text (TEXT), control codes, symbols

### TEXT
- [AUTO] Each line is its own object; it can be moved and reformatted alone ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).
- [AUTO] Prompt order: insertion point; height; rotation angle; text. ENTER inside the command starts another line below. ENTER on a blank line ends the command ([G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5)).
- [AUTO] The height prompt is skipped when the current text style has a fixed (non-zero) height ([G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5), [G:7BC6132F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7BC6132F-BF07-4A49-B8A8-4FCB524EB736)). (inference) A script must know the style height, or its height value is read as the rotation angle.
- New text goes on the current layer, or on the layer in TEXTLAYER. The Annotate tab text panel also has a layer override drop-down (Windows only) ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).
- Shortcut menu while editing TEXT: Opaque Background, Insert Field (not in LT), Find and Replace, Select All, Change Case ([G:BF4593C2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BF4593C2-A91A-47DB-B835-3796ABFCD575)).
- Rotated view: run UCS > View first. Text, leader landings and dimension parts take their horizontal and vertical from the UCS at creation ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).
- Edit: double-click (TEXTEDIT). With TEXTED = 1 the Edit Text dialog edits TEXT objects ([G:FC4CD78B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FC4CD78B-37B1-410A-A713-433E14968AD2)). Grips sit at the lower-left of the baseline and at the alignment point ([G:33014AC3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-33014AC3-6691-4B14-B443-A9422AF2AD21)).
- TEXTALLCAPS: fixes accidental Caps Lock typing in MTEXT and TEXT/DTEXT ("sURVEY" becomes "Survey") ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).

### %% control codes [AUTO] ([G:968CBC1D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-968CBC1D-BA99-4519-ABDD-88419EB2BF92))
Work in single-line text with SHX and PostScript fonts. NOT all work in mtext.
- `%%c` diameter. `%%d` degree. `%%p` plus/minus. `%%%` one percent sign.
- `%%u` underscore toggle. `%%o` overscore toggle. `%%k` strikethrough toggle. Under and over can be on together; both end at the end of the string.
- `%%nnn` = the character whose decimal Unicode value is nnn.
- Euro sign: SHX fonts and their TrueType twins from AutoCAD 2000 on; Alt+0128 on the keypad.

### Unicode symbols [AUTO] ([G:518E1A9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-518E1A9D-398C-4A8A-AC32-2D85590CDBE1))
Type `\U+xxxx` in the text (backslash first).
- Degree U+00B0. Plus/minus U+00B1. Diameter U+2205. Delta U+0394. Squared U+00B2. Cubed U+00B3.
- Not equal U+2260. Almost equal U+2248. Identity U+2261. Angle U+2220. Ohm U+2126. Omega U+03A9. Electrical phase U+0278. Subscript 2 U+2082.
- Centerline U+2104. Plate/property line U+214A. Boundary line U+E100. Flow line U+E101. Monument line U+E102. Initial length U+E200.
- Fonts that carry them: Simplex, Romans, gdt, amgdt, Isocp, Isocp2, Isocp3, Isoct, Isoct2, Isoct3, and TrueType-only Isocpeur, Isocpeur italic, Isocteur, Isocteur italic. Initial Length exists only in Simplex, Romans, gdt, amgdt and Isocpeur.

## 14.3 Multiline text (MTEXT)

### What mtext is
- One object that supports word wrap, per-character formatting, columns, stacked text, bullet and numbered lists, tabs and indents ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).
- Text inside dimensions and tolerances is made by the dimension commands. Leaders can carry mtext ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).
- Text style holds font, size, oblique angle, orientation. New text uses the CURRENT style. "Standard" exists in every drawing. Build a standard style set and save it in a .dwt ([G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).

### Create
- [AUTO] MTEXT: pick two opposite corners of the bounding box; the box sets the width ([G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5)).
- The editor then opens: the Text Editor contextual ribbon tab when the ribbon is on, the Text Formatting toolbar when it is off. MTEXTTOOLBAR controls the toolbar ([G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5), [G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119)).
- Save and exit: Close Text Editor, OK, click outside, or Ctrl+Enter. Esc exits and DISCARDS ([G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5), [G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).
- (inference) The in-place editor is interactive, and an MTEXTED editor (14.4) also waits for a person to close it. For unattended work, create mtext through COM or AutoLISP with the inline codes in 14.4, and test how MTEXT behaves inside a .scr before relying on it.
- Height: the style height if fixed; if the style height is 0, the TEXTSIZE value. One mtext can mix heights ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC), [G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3)).
- A height override applied to all text in the editor scales the whole object, width included ([G:7BC6132F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7BC6132F-BF07-4A49-B8A8-4FCB524EB736)).

### Text Editor ribbon tab ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC))
- Style panel: Style (Standard default), Annotative, Text Height, Background Mask.
- Formatting panel: Match Text Formatting, Bold and Italic (TrueType only), Strikethrough, Underline, Overline, Stack, Superscript, Subscript, Change Case, Font, Color, Clear Formatting, Oblique Angle (-85 to 85, positive leans right), Tracking (1.0 normal; above widens, below narrows), Width Factor (1.0 normal, 2 doubles, 0.5 halves).
- Paragraph panel: Justification (nine options, Top Left default), Bullets and Numbering (not in table cells), Line Spacing (1.0x, 1.5x, 2.0x, 2.5x, More = Paragraph dialog, Clear Paragraph Spacing), Left, Center, Right, Justified, Distributed.
- Insert panel: Columns, Symbol (also non-breaking space; Other = Character Map; symbols do not work in vertical text), Field.
- Spell Check panel: as-you-type toggle, Edit Dictionaries. Tools panel: Find and Replace, Import Text, AllCAPS (TEXTALLCAPS). Options panel: More, Ruler, Undo, Redo.
- Font list: TrueType by family name, SHX by file name. Custom and third-party fonts show as Autodesk proxy fonts in the editor.
- Trailing spaces at a line end count as text and shift that line's justification ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC), [G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119)).

### Text Formatting toolbar ([G:32BE8580](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-32BE8580-3F05-42C2-B746-6175CA3863AF))
- Show it: right-click in the editor > Editor Settings > Show Toolbar.
- Style control = TEXTSTYLE [AUTO].
- Applying a new style to existing mtext overrides font, height, bold and italic. Stacking, underline and color stay. Styles with Backwards or Upside Down effects are not applied.
- Color: BYLAYER, BYBLOCK, a listed color, or Other (Select Color dialog).

### Editor settings (right-click > Editor Settings) ([G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119))
- [AUTO] Always Display As WYSIWYG: checked sets MTEXTFIXED = 0; cleared sets MTEXTFIXED = 2 (very small, very large or rotated text shown legible and horizontal while editing).
- [AUTO] Show Toolbar sets MTEXTTOOLBAR. Show Options expands the toolbar.
- Show Ruler; ruler right-click Set Mtext Width and Set Mtext Height apply to all columns.
- Check Spelling toggles as-you-type checking; Check Spelling Settings; Dictionaries; Text Highlight Color.

### Shortcut menu items ([G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119))
- Paste Special strips character, paragraph or all formatting. Text pasted from Word keeps most of its formatting.
- Insert Field (Field dialog). Symbol. Import Text. Find and Replace.
- Paragraph Alignment: left, center, right, justify, center each line.
- Change Case: Uppercase, Lowercase, Superscript, Subscript. All CAPS converts only NEW and imported text; use Change Case for existing text.
- Character Set: code page for selected text. Combine Paragraphs: each paragraph return becomes a space. Remove Formatting: character, paragraph, or all.
- Not available for single-line text: Paste Special, Symbol, Import Text, Paragraph Alignment, Paragraph, Bullets and Lists, Columns, Character Set, Combine Paragraphs, Remove Formatting, Background Mask, Stack. Not available in table cells: Bullets and Lists, Background Mask, Show Ruler.

### Width, justification, frame, character format
- Justification sets the flow from the insertion point (middle, top or bottom of the object); left and right are relative to the box width. One word longer than the width sticks out past the box ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)).
- Change width: drag the right frame edge or the right end of the ruler, or ruler right-click > Set Mtext Width and type a width in drawing units ([G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).
- Properties palette Text Frame = Yes draws a frame with the text's color, linetype, transparency and layer ([G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).
- Character formats: Font, Height, Bold, Italic, Underline, Overline, Strikethrough (SHX fonts cannot do bold or italic), Color, Oblique angle -85 to 85, letter Spacing, Character width ([G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).

### Line and paragraph spacing
- Properties palette Line Space Style: "At Least" (default; grows to fit the tallest character in each line) or "Exactly" (equal spacing whatever the font or height) ([G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).
- Line Space Factor = multiple of single spacing; single spacing = 1.66 x text character height. Line Space Distance valid range 0.0833 to 1.3333 drawing units. Changing one updates the other when you leave the palette ([G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).
- Paragraph dialog line spacing ([G:90F5A530](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-90F5A530-BB66-4264-86F0-D5F670EC8519)): Exact = fixed value, text height changes do not change it; Multiple = times text height, the tallest text in a line sets it; At least = your value, or the text height when that is larger.
- Gap between two paragraphs = after-spacing of the upper + before-spacing of the lower ([G:90F5A530](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-90F5A530-BB66-4264-86F0-D5F670EC8519)).
- Line spacing applies to whole current or selected paragraphs, not to selected lines ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)).
- Not every paragraph and line spacing option is supported in AutoCAD 2007 and earlier releases ([G:90F5A530](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-90F5A530-BB66-4264-86F0-D5F670EC8519), [G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).
- The pages define line spacing two different ways; see 14.19.

### Tabs and indents ([G:90F5A530](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-90F5A530-BB66-4264-86F0-D5F670EC8519), [G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916), [G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F))
- Ruler: top slider = first line of each paragraph; bottom slider = the other lines (hanging indent). Long ticks = default tab stops.
- Tab types: left, center, right, decimal. Click the ruler to add, drag to move, drag off the ruler to delete. The Paragraph dialog also sets tabs.
- Decimal Style: period, comma or space from the user locale; saved with the drawing even if the locale changes later.
- Right Indent applies to the whole paragraph.

### Background mask ([G:3448A24E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3448A24E-E18B-4C8C-B8AB-84F4CD4EBC81))
- Right-click in the editor > Background Mask > Use Background Mask: opaque fill behind the text.
- Border Offset Factor: 1.0 = fill fits the mtext exactly; 1.5 = fill extends 0.5 x text height past it.
- Fill Color: Use Background Drawing Color, or a set color.
- With columns, only the column areas are masked; gutters stay clear.
- Not available for single-line text or table cells ([G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119), [G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).

### Lists ([G:FB9F3708](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FB9F3708-0A8C-4F77-B6EC-908B8B9BF7F5), [G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916), [G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119))
- Needs both "Allow Bullets and Lists" and "Allow Auto Bullets and Numbering" checked (right-click > Bullets and Lists).
- Typed list: letter or number, punctuation, TAB, item text. ENTER = next item; SHIFT+ENTER = plain paragraph without a number; ENTER twice ends. Numbering continues by itself.
- Punctuation allowed after the letter or number (cannot be used as bullets): period, close parenthesis, close angle bracket, close square bracket, close curly bracket, plus colon ([G:FB9F3708](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FB9F3708-0A8C-4F77-B6EC-908B8B9BF7F5), [G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)) or comma ([G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119), [G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)). The pages differ; see 14.19.
- Bullet: type U+2022, or Paragraph panel > Bullets and Numbering > Bulleted.
- TAB at the start of an item nests it one level; SHIFT+TAB moves it up. Lettered lists continue with double letters after Z.
- Start restarts the sequence at the selection (unselected items below join the new list). Continue joins the list above.
- Auto-detect (on by default): a line that starts with letters, numbers or a symbol, then punctuation, then Tab or Space, then text ended by Enter or Shift+Enter becomes a list item. Clearing Allow Bullets and Lists turns every list in that mtext into plain text and blocks new lists ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916), [G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119)).

### Stacked text (fractions, tolerances)
- `/` = vertical stack with a horizontal bar; `#` = diagonal bar; `^` = tolerance stack, no line. Text left of the character goes on top ([G:DC5BF02C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DC5BF02C-32A7-4C3B-92BC-DFC5415313E8), [G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).
- Select the text and click Stack. Digits before and after / # ^ stack by themselves when followed by a space or one of: ~ ` ! @ # $ % ^ & * ( ) _ = { } [ ] | \ : ; " ' < > ? , ([G:DC5BF02C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DC5BF02C-32A7-4C3B-92BC-DFC5415313E8)).
- AutoStack Properties ([G:60C5A608](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60C5A608-2B76-4793-9FA9-011942E69ABE)): Enable AutoStacking; Remove Leading Blank; `/` becomes Diagonal or Horizontal fraction by setting; `#` is always diagonal and `^` always tolerance. AutoStack acts only on numeric characters right before and after the character ([G:9E737D61](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9E737D61-58ED-4FB0-8E54-1B692D925637)). For tolerance stacking, +, - and . also stack ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)).
- Stack Properties ([G:9E737D61](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9E737D61-58ED-4FB0-8E54-1B692D925637)): Upper and Lower text; Style = Fraction (Horizontal), Fraction (Diagonal), Tolerance, Decimal (aligns decimal points); Position = Top, Center (default), Bottom, one alignment per object; Text Size 25 to 125 percent of the style size; Defaults.
- Stacking variables (names only): MTEXTAUTOSTACK, TSTACKALIGN, TSTACKSIZE ([G:DF61C99C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DF61C99C-850E-452D-9C09-0FE97A9ACE28)).

### Columns
- Text Editor tab > Insert panel > Columns: No Columns; Dynamic Columns (text flow adds or removes columns; Auto Height or Manual Height); Static Columns (set total width, total height and number of columns; all columns the same height, aligned on both sides) ([G:6DF5368A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6DF5368A-5F2F-44BE-8B80-F35FFEF80204), [G:3723E9F3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3723E9F3-6E0B-4BC2-9C73-996BB0ACC88F)).
- All columns have equal width and equal gutters. A multi-column object always starts as one column ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916), [G:6DF5368A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6DF5368A-5F2F-44BE-8B80-F35FFEF80204)).
- Height stays fixed unless too much text is added or the grip is moved; extra text flows to the next column. A column break assumes that column's current height is fixed ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)).
- Column break: Alt+Enter, or Columns > Insert Column Break ([G:3723E9F3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3723E9F3-6E0B-4BC2-9C73-996BB0ACC88F)).
- Column Settings dialog ([G:ADF140B5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-ADF140B5-627E-4D36-B8D5-DD46691F3564)): Column Type; Column Number (Static only); Height; Width and Gutter. Default gutter = 5 x the default text height. Shows total width.
- The ruler arrows at upper right change only the gutter. Dragging the first column's width sets all columns. Grip edits apply when the mouse button is released ([G:3723E9F3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3723E9F3-6E0B-4BC2-9C73-996BB0ACC88F), [G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F)).
- Variable named: MTEXTCOLUMN ([G:DF61C99C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DF61C99C-850E-452D-9C09-0FE97A9ACE28)).

### Import text into mtext
- [GUI] MTEXT > corners > right-click > Import Text > Select File > Open ([G:A72A6B7A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A72A6B7A-3175-4C98-AC74-642B9262B1F6)). Or drag a .txt or .rtf icon from File Explorer onto the drawing; Explorer must not fill the screen ([G:60085C64](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60085C64-1D36-4313-B128-E6E75BC8ABEA)).
- .txt or .rtf only. Size limit 256 KB per [G:66848B18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66848B18-9590-4E68-839E-A4DFD28301D2) and [G:A72A6B7A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A72A6B7A-3175-4C98-AC74-642B9262B1F6), but 32 KB per the Text Editor tab page ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)). (inference) Keep import files under 32 KB.
- TXT takes the current text style. RTF takes the current style NAME but keeps its own fonts and formatting ([G:66848B18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66848B18-9590-4E68-839E-A4DFD28301D2)).
- Import can replace the selection, replace all, or append. Color is set BYLAYER. Black text on a black background turns white or the current color ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).
- Dragged TXT becomes mtext in the current style, width set by its line breaks. Dragged RTF becomes an OLE object ([G:60085C64](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60085C64-1D36-4313-B128-E6E75BC8ABEA), [G:66848B18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66848B18-9590-4E68-839E-A4DFD28301D2)).
- Clipboard: text from another application becomes an OLE object; text from another drawing comes in as a block reference that keeps its original style ([G:66848B18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66848B18-9590-4E68-839E-A4DFD28301D2)).
- An Excel sheet pasted as OLE is cut off at 72 rows unless it was made in Office 2002 with SP2; the same cut happens when it is opened on a machine with an older Office ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).
- Use: keep standard general notes in a text file and import them ([G:66848B18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66848B18-9590-4E68-839E-A4DFD28301D2)).

## 14.4 MTEXT inline format codes and the alternate editor

### Inline format codes [AUTO] ([G:7D8BB40F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D8BB40F-5C4E-4AE5-BD75-9ED7112E5967))
The codes typed when an alternate editor is in use. (inference) The same codes make up the MTEXT contents string, so they are what AutoLISP, COM and DXF writers put in an mtext object's text.
- `\P` end paragraph (capital P) ([G:9083A065](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9083A065-0CED-4BBC-A998-E031E7A57726)).
- `\L...\l` underline on/off. `\O...\o` overline on/off (the table header prints `\0` with a zero, but the example is `\OAutoCAD\o`). `\K...\k` strikethrough on/off.
- `\~` non-breaking space. `\\` literal backslash. `\{` `\}` literal braces.
- `\C2;` color number. `\Ftxt.shx;` SHX font file (not for TrueType). `\fCourier New;` TrueType font name (not for SHX).
- `\H2;` height in drawing units. `\H3x;` height as a multiple of the current height.
- `\S...^...;` stack at the /, # or ^ character. Example `1.000\S+0.010^-0.000;`.
- `\T2;` character spacing, valid .75 to 4 times the original. `\Q20;` oblique angle. `\W2;` width factor.
- `\A0;` `\A1;` `\A2;` alignment bottom, center, top. Example `\A1;1\S1/2` (this example has no closing semicolon after the stack; the [G:6F59DA4A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F59DA4A-A790-4316-A79C-2CCE723A30CA) examples do close it: `\S1/2;`).
- `{ }` limit codes to the enclosed text. Braces nest up to eight levels.
- Value codes end with a semicolon.

### Worked lines from Autodesk ([G:6F59DA4A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F59DA4A-A790-4316-A79C-2CCE723A30CA))
```
{{\H1.5x; Big text} \A2; over text\A1;/\A0; under text}\P
{\A0;Baseline: 1 \S1/2;}\P
{\A1;Center: 1 \S1/2;}\P
{\A2;Topline: 1 \S1/2;}\P
{Tolerances: \A1;1.000\H.75x;\S+0.010^-0.000;}\P
{Architectural: 9-{\H.666x;\A2;11\A1;/\A0;16}\A2;"}\P
```
(inference) The last line builds a 9-11/16" dimension string with a small raised fraction.

### MTEXTED alternate editor [AUTO] ([G:9083A065](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9083A065-0CED-4BBC-A998-E031E7A57726), [G:AC1ADE24](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AC1ADE24-BE53-4701-B089-80B7FF031921))
- At the Command prompt: `MTEXTED`, then the full path of an ASCII editor executable (Notepad works), or `Internal` to restore the built-in editor. The About page calls MTEXTED a system variable.
- With an alternate editor, MTEXT asks for the box corners at the command line first, then opens the editor. On close, the text is inserted within the width limit.
- All formatting must be typed as codes. Edit later in the same editor to keep the codes.

## 14.5 Text styles and fonts

### Style rules
- A text style is a named set of text settings (font, line spacing, justification, color). New text uses the current style. Editing a style updates all text that uses it. Object properties can override it ([G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3)).
- Styles apply to notes, leaders, dimensions, tables and block attributes ([G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3)).
- STANDARD exists in every drawing and cannot be deleted. Keep a standard style set in a .dwt ([G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3)).
- Several styles can use one font, for example with different oblique angles ([G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3)).
- [AUTO] Height rule: a non-zero style height is used by TEXT and MTEXT, and TEXT skips its height prompt. Height 0: TEXT prompts for height every time; MTEXT uses TEXTSIZE ([G:B1B38199](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B1B38199-5329-4FF8-A4CE-1403B53A63F3), [G:7BC6132F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7BC6132F-BF07-4A49-B8A8-4FCB524EB736)). The dialog page adds: height 0.0 defaults to the last height used or the template value ([G:1ED81E98](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1ED81E98-6463-4574-875F-183C8280C4AC)).
- Annotative style: the height box becomes Paper Text Height ([G:1ED81E98](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1ED81E98-6463-4574-875F-183C8280C4AC)).
- Changing the orientation or font file of a style changes all text in that style at the next regeneration ([G:1ED81E98](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1ED81E98-6463-4574-875F-183C8280C4AC)).

### STYLE (Text Style dialog) [GUI] ([G:1ED81E98](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1ED81E98-6463-4574-875F-183C8280C4AC), [G:F9970584](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F9970584-DF6D-4946-8EC8-D415AD4A519D))
- Home tab > Annotation panel > Text Style. Current Text Style; Styles list (annotative styles show an icon); filter all styles or styles in use; Preview.
- Font Name: registered TrueType family names and all SHX fonts in the Fonts folder. Font Style: italic, bold, regular. With Use Big Font it becomes Big Font Name (Asian SHX files only).
- Size: Annotative; Match Text Orientation to Layout (only with Annotative); Height or Paper Text Height.
- Effects: Upside Down; Backwards; Vertical (only fonts with dual orientation, never TrueType); Width Factor (below 1.0 condenses, above expands); Oblique Angle -85 to 85.
- Buttons: Set Current; New (name up to 255 characters of letters, numbers, $, _ and -); Delete (unused styles only); Apply (updates the style and its text).
- TrueType can look smaller than SHX at the same height. TrueType with effects can look bold on screen; the plot follows the applied formatting.
- [AUTO] TEXTSTYLE holds the current style ([G:32BE8580](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-32BE8580-3F05-42C2-B746-6175CA3863AF)).
- Text style and field names listed together on one index page (no meanings): FIELD, UPDATEFIELD, PROPERTIES, TEXT, STYLE, TABLE, QTEXT, TABLEEXPORT, TABLESTYLE; variables CTABLESTYLE, QTEXTMODE, FIELDDISPLAY, FIELDEVAL, FONTMAP, TEXTSIZE, TEXTSTYLE, TEXTFILL, TEXTQLTY (the page metadata also prints "FONALT") ([G:2776142F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2776142F-A289-4ABE-96ED-ABC3518B82A9)).
- Set current from the Annotate tab > Text panel > Text Style list. Typing `textstyle` (no Enter) adds a text style category to the command-line suggestion list ([G:834CA7BC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-834CA7BC-B8FC-4768-AAEA-45501F70A68F)).
- (inference) The dialog blocks a script, and the full command-line prompt list for STYLE is not in these pages. Put styles in the template, or probe the command-line form live before scripting it.

### Font answers at the STYLE font prompt [AUTO] ([G:CBC3F683](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CBC3F683-06F3-4B9C-8747-D01F3C262956))
- `font,bigfont` sets both. `font,` sets only the normal font (Big Font unchanged). `,bigfont` sets only the Big Font. `font` alone sets the normal font and REMOVES any Big Font. Enter = no change.
- A font file name that contains a comma is not accepted; the comma is read as the separator.

### Height and font facts
- Text height is in drawing units ([G:7BC6132F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7BC6132F-BF07-4A49-B8A8-4FCB524EB736)).
- TrueType: the height covers a capital letter plus an ascent area for accents; the split is set by the font designer, so it differs by font. Descenders (y, j, p, g, q) hang below the stated height ([G:7BC6132F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7BC6132F-BF07-4A49-B8A8-4FCB524EB736)).
- SHX fonts cannot be bold or italic ([G:3740EC59](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3740EC59-FB75-47FD-B042-03D6AC095D4F), [G:8739509C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8739509C-15A7-4582-BF7C-3D83ED2A23B5)).

### Big Fonts and vertical text ([G:CBC3F683](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CBC3F683-06F3-4B9C-8747-D01F3C262956), [G:32786109](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-32786109-F454-47DD-AA4C-FB8C37F4430D))
- A Big Font is an SHX shape file for Asian alphabets with thousands of characters. A style can use a normal font and a Big Font together.
- Shipped Big Fonts: @extfont2.shx, bigfont.shx, chineset.shx, extfont.shx, extfont2.shx, gbcbig.shx, spec_bar.shx, spec_sl.shx, special.shx, whgdtxt.shx, whgtxt.shx, whtgtxt.shx, whtmtxt.shx.
- Vertical SHX text: SHX font + Use Big Font + Vertical. Vertical TrueType: fonts whose names start with @ (for their Asian language only).

### Missing fonts and substitution ([G:928DF015](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-928DF015-1E04-4CC2-AF1B-0037548DFBAE))
- [AUTO] FONTALT = font used when a named font file is missing. Default simplex.shx. For styles that use a Big Font, FONTALT also maps the pair; default pair txt.shx and bigfont.shx. Set it by typing `fontalt` and the font file name ([G:C0898D69](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C0898D69-A0DB-4C3E-992A-B06A8961E878)).
- Search order when a font file cannot be found at drawing open:
  - .ttf: 1 font mapping table, 2 font defined in the text style, 3 Windows substitutes a similar font.
  - .shx: 1 font mapping table, 2 font defined in the text style, 3 FONTALT, 4 PROMPT for a new font.
  - .pfb: 1 font mapping table, 2 FONTALT, 3 PROMPT for a new font.
- (inference) That prompt can stall an unattended run or eat script lines. Ship the fonts or map them in the .fmp before running headless.
- PostScript fonts can no longer be displayed; Autodesk supplies TrueType equivalents mapped in a font mapping file. If a TrueType font is missing, name a similar TrueType font to avoid text length and wrap changes.
- Proxy fonts: custom or third-party SHX fonts with no TrueType twin show as a TrueType proxy in the in-place editor (they look different on purpose). To apply such a font to characters, first make a text style that uses it.
- If the default font lacks a typed character, an alternate font is substituted. CIF and MIF codes typed in the editor convert to real characters.

### Font mapping file (.fmp) ([G:928DF015](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-928DF015-1E04-4CC2-AF1B-0037548DFBAE), [G:BE7A48CE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE7A48CE-E927-438E-B235-19220018A4DE))
- Plain ASCII, extension .fmp. One line per font: font file name with no path or extension, a semicolon, then the substitute file name with extension. Example: `timesnr;times.ttf`.
- [GUI] Set the file: Options > Files tab > Text Editor, Dictionary, and Font File Names > Font Mapping File > double-click > Select a File > Open > OK.
- [AUTO] Then run REGEN to convert existing text with the new mapping.
- eTransmit adds the .fmp to a package automatically; .shx and .ttf files are listed as not added automatically ([G:C32FA153](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C32FA153-88D6-41D9-B868-0DFF59509CD2)). (inference) They go in only with the Include Fonts setup option (14.15).

## 14.6 Finding, checking and rescaling text

### Command and variable names (index pages; no meanings given)
- Text: MTEXT, QTEXT, SPELL, STYLE, TEXT, TEXTALIGN, TEXTEDIT. Variables: FONTALT, MTEXTAUTOSTACK, MTEXTCOLUMN, MTEXTDETECTSPACE, TEXTALIGNMODE, TEXTALIGNSPACING, TEXTALLCAPS, TEXTAUTOCORRECTCAPS, TEXTED, TEXTEDITMODE, TEXTLAYER, TEXTSIZE, TEXTSTYLE, TSPACEFAC, TSPACETYPE, TSTACKALIGN, TSTACKSIZE ([G:DF61C99C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DF61C99C-850E-452D-9C09-0FE97A9ACE28)).
- Changing text: -FIND, FIND, FINDINCLUDE, FINDMATCH, JUSTIFYTEXT, MTEDIT, MTEXT, PROPERTIES, SCALETEXT, SPACETRANS, SPELL, STYLE, TEXT, TEXTEDIT, TXT2MTXT. Variables: CENTERMT, DCTCUST, DCTMAIN, DWGCODEPAGE, MIRRTEXT, MTEXTED, MTEXTEDENCODING, MTEXTFIXED, MTEXTTOOLBAR, MTJIGSTRING, OSNAPNODELEGACY, TEXTED, TEXTEDITMODE, TEXTFILL, TEXTGAPSELECTION, TEXTJUSTIFY, TEXTLAYER, TEXTQLTY ([G:6F907E64](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F907E64-D4A1-424E-8F79-6559DEF136FC)).

### FIND (Find and Replace) [GUI] ([G:03A48719](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-03A48719-9C75-4BBB-BFE9-4692BE5A591F), [G:3104FBDE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3104FBDE-7145-4AD9-9B05-CC2C002ED587), [G:BAFB39BD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BAFB39BD-01E2-48A6-8167-61A66487442C))
- Annotate tab > Text panel > Find: type the search text, Enter, the dialog opens. -FIND is the command-line form; its prompts are not in these pages.
- Find What (wildcards allowed; six most recent strings). Replace With.
- Find Where: Entire Drawing, Current Layout, Selected Objects. Default = Selected Objects if something is selected, else Entire Drawing.
- Find / Find Next (zooms to each hit), Replace, Replace All, Select Objects (dialog hides; Enter returns). List Results table (double-click a row to zoom). Create Selection Set (Highlighted) or (All): all hits must be in model space or in one layout.
- Search Options: Match Case; Find Whole Words Only; Use Wildcards; Search XRefs; Search Blocks; Ignore Hidden Items (text on frozen or off layers, invisible attributes, text in dynamic block visibility states); Match Diacritics; Match Half or Full Width Forms.
- Text Types (all on by default): Block Attribute Value; Dimension or Leader Text; Single-Line or Multiline Text; Table Text; Hyperlink Description; Hyperlink (URL).
- Replace changes text content only; character formatting and properties stay.
- In a 3D view the viewport switches to 2D during the search.
- Page example: Find What `4384K6?`, Replace With `4384K61`.
- Inside one mtext: double-click > Text Editor tab > Tools > Find & Replace (Find Next, Replace, Replace All; Match Case, Match Whole Word Only, Use Wildcards, Match Diacritics, Match Half/Full Width Forms) ([G:39B391F5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-39B391F5-F74D-4D6F-988D-61B24DEFEE52)).
- Windows Search finds drawings by their text, but not text in tables, fields or xrefs ([G:BAFB39BD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BAFB39BD-01E2-48A6-8167-61A66487442C)).

### Wildcards for FIND ([G:03A48719](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-03A48719-9C75-4BBB-BFE9-4692BE5A591F), [G:BAFB39BD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BAFB39BD-01E2-48A6-8167-61A66487442C))
- `#` any digit. `@` any letter. `.` any non-alphanumeric character. `*` any string, anywhere in the pattern. `?` any one character (`?BC` matches ABC, 3BC).
- `~` anything but the pattern (`~*AB*` = strings that do not contain AB).
- `[AB]` one of the listed characters. `[~AB]` any character not listed. `[A-G]` one character in a range.
- `` ` `` (reverse quote) reads the next character literally (`` `~AB `` matches ~AB).

### SPELL [GUI] ([G:6F12A83B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F12A83B-D3E9-4DCF-A0F4-15CC98FA9B61), [G:CC9D702D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CC9D702D-79B6-4527-9527-57A717F26118), [G:EE5131AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EE5131AB-1533-40BC-A374-E500758B5DB7), [G:C717CC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C717CC2C-C0D5-411A-B607-CFDE4C1DC9FD), [G:D5D0CA61](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D5D0CA61-FC33-4F64-945C-85AC77C02484), [G:2C7516F8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C7516F8-CB75-4148-9D93-DFC01BE5B840))
- Annotate tab > Text panel > Check Spelling. Checks single-line text, mtext, multileader text, dimension text, attribute values (only the values) and xref text. Text inside a block definition is checked only when its reference was selected.
- Settings: include Dimension Text, Block Attributes, External References; ignore capitalized words, mixed case, uppercase, words with numbers, words with punctuation.
- Buttons: Start, Change, Change All, Ignore, Ignore All, Add to Dictionary, Undo, Dictionaries, Settings.
- [AUTO] DCTMAIN = main dictionary; DCTCUST = custom dictionary. Set by typing the variable and the dictionary name ([G:C717CC2C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C717CC2C-C0D5-411A-B607-CFDE4C1DC9FD)).
- Custom dictionaries use .cus. Words up to 63 characters. Import adds words from a plain-text list. A custom dictionary file name must use only characters of the current code page; use ASCII for shared ones ([G:2C7516F8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2C7516F8-CB75-4148-9D93-DFC01BE5B840)).
- Check as you type is on by default in the in-place editor; turn off under Editor Settings ([G:EE5131AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EE5131AB-1533-40BC-A374-E500758B5DB7)).

### SCALETEXT, JUSTIFYTEXT, SPACETRANS [AUTO] ([G:C0A07C95](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C0A07C95-F2DA-46DE-BEBF-4E7407D708BC), [G:05CC8143](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-05CC8143-FDA8-483D-927E-2469314EFFF7))
- SCALETEXT scales text, mtext and attributes in place, keeping each insertion point. One factor for all picked objects. Choices: relative scale factor, absolute height, or match an existing text height.
- SCALETEXT steps: select, ENTER; a justification option or ENTER to keep the existing ones; `s` and the scale factor ([G:05CC8143](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-05CC8143-FDA8-483D-927E-2469314EFFF7)).
- JUSTIFYTEXT changes the justification point without moving the text (example: right-justify schedule text so new entries line up).
- SPACETRANS converts lengths between model and paper space. Use it transparently (`'spacetrans`) at any distance prompt. Page example: TEXT at start point 1,3; at `Specify height <0.375>:` enter `'spacetrans`; at `>>Specify paper space distance <1.000>:` enter 3/8; TEXT resumes with height 1.173, which plots 3/8" in that viewport. Not available on the Model tab or in a perspective view.

## 14.7 Annotation scale and annotative objects

### Annotation objects ([G:F8E4E984](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F8E4E984-71C5-4812-B1A0-3BD0A6BB0BDF))
- Annotation types: text and mtext (notes, labels); tables (tabular data); dimensions and geometric tolerances; hatches, gradients and fills; leaders and multileaders (notes that point at things); blocks and attribute definitions (title blocks).
- Two ways to size them: non-annotative objects get a fixed size worked out from the plot scale; annotative objects resize themselves to show at the same size at any view scale.

### The arithmetic for non-annotative work [AUTO] ([G:D8A24528](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8A24528-80F9-4B57-8802-CFA1608B9AEE), [G:4DE922FB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4DE922FB-79FC-44E0-AC05-313DB3CCE333))
- Plotting from model space: scale annotation by the inverse of the plot scale.
- DIMSCALE = inverse of the drawing scale. 1" = 4' (1:48) gives DIMSCALE 48.
- Text height = desired plotted height x scale factor. 1/4" text at 1:48 = 12".
- Fixed height recipe: scale factor = drawing units / paper units; 1/4" = 1'-0" gives 12 / 0.25 = 48. Plotted 3/16" (0.1875) x 48 = 9. Model-space text height is 9.
- LTSCALE depends on the linetype definition and the scale. Page example: 1:48 with 1/8" plotted dashes = LTSCALE 12.
- Hatch scale is set per pattern; AR patterns commonly use the drawing scale factor.
- Attributes and tables scale like text. Blocks are normally drawn 1:1; blocks that hold text or attributes may need scaling by the text method.
- Text placed directly on a layout is drawn full size, because layouts usually plot 1:1. Example: 1/8" paper-space text plots 1/8" ([G:4F448A62](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F448A62-A99E-4AB5-AE50-9EAAC0485283)).

### Annotative objects: how they behave ([G:590DE319](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-590DE319-FD23-45FE-8430-D3EF4AB989D2), [G:6D4A620B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6D4A620B-30AB-4593-B168-F9FF084017C6), [G:2BD75FA2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2BD75FA2-4FB2-4FFC-973A-DB972F3870E3))
- One annotative object is defined by a paper height or scale plus the annotation scales it carries. Each scale representation can be moved on its own ([G:6D4A620B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6D4A620B-30AB-4593-B168-F9FF084017C6)).
- It shows in a viewport or in model space only if that annotation scale is assigned. If not assigned, the object is not displayed ([G:6D4A620B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6D4A620B-30AB-4593-B168-F9FF084017C6)); [G:590DE319](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-590DE319-FD23-45FE-8430-D3EF4AB989D2) adds "or the text appears unchanged".
- Can be annotative: single-line and multiline text and text styles; blocks and attribute definitions; hatches; dimensions and dimension styles; geometric tolerances; multileaders and multileader styles ([G:6D4A620B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6D4A620B-30AB-4593-B168-F9FF084017C6)).
- Each layout viewport has its own annotation scale, often equal to its viewport scale. Model space uses the status bar Annotation Scale. Wrong-size display: select the viewport and click Viewport Scale Sync so Viewport Scale and Annotation Scale match ([G:2BD75FA2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2BD75FA2-4FB2-4FFC-973A-DB972F3870E3)).
- Legacy method that works everywhere: one layer per scale (example Notes1-4 and Notes3-16 for 1/4" and 3/16" viewports), one copy of the note on each, then VP Freeze / VP Thaw per viewport ([G:9CF59346](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9CF59346-CF6A-4E82-AFF5-7D2300A9D771)).

### Making things annotative
- Existing object: Properties palette > Misc > Annotative = Yes. New objects: use a style with Annotative on ([G:41E7A58B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-41E7A58B-8454-4510-857E-B829D153B35E)).
- Text style: STYLE > Size > Annotative; Match Text Orientation to Layout then becomes available ([G:8C282358](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C282358-F303-40F0-8708-FBC57701B442), [G:A23799DB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A23799DB-69A5-437D-BEF1-3B18F79DFB54)).
- Dimension style: DIMSTYLE > Modify > Fit tab > Scale for Dimension Features > Annotative ([G:8C282358](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C282358-F303-40F0-8708-FBC57701B442)).
- Multileader style: MLEADERSTYLE > Modify > Leader Structure tab > Scale > Annotative ([G:8C282358](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C282358-F303-40F0-8708-FBC57701B442)).
- [AUTO] Turning a style annotative or non-annotative does NOT update existing objects that use it. Run ANNOUPDATE to bring them in line ([G:8C282358](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C282358-F303-40F0-8708-FBC57701B442)).
- Block: BLOCK dialog > Behavior > Annotative; optional Match Block Orientation to Layout; OK > Redefine Block ([G:4859E66D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4859E66D-EF09-46ED-A4D5-989E494EC6DB), [G:BF73BDB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BF73BDB8-D403-408B-9026-ABD011B45087)). Only the dialog route is given.
- [AUTO] ANNORESET resets the positions of all scale representations of an object (right-click > Annotative Object Scale > Synchronize Multiple-scale Positions) ([G:93D033D2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-93D033D2-7F90-4E0D-81F3-3F01532702C2)).

### Adding scales to objects (OBJECTSCALE) [GUI] ([G:1E3DCBD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1E3DCBD5-C0F1-4598-9408-B330636E31E8), [G:85450EAE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-85450EAE-8B5B-47BD-AA45-3DB5B733FD64), [G:535F7895](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-535F7895-8686-49E7-9451-605F782F5D27))
- Select an annotative object > right-click > Annotative Object Scale > Add/Delete Scales opens the Annotative Object Scale dialog.
- Object Scale List; "List all scales for selected objects" or "List scales common to all selected objects only"; Add; Delete.
- Delete cannot remove the current scale or scales referenced by objects or views.
- Add opens Add Scales to Object (Shift or Ctrl for several). Custom scales go into the list with SCALELISTEDIT.
- Status bar "Automatically Add Scales to Annotative Objects When the Annotation Scale Changes" adds a scale on every change. It can grow the file; add scales only where needed ([G:535F7895](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-535F7895-8686-49E7-9451-605F782F5D27)).
- Annotation Visibility status bar button (ANNOALLVISIBLE) shows or hides non-current scale representations ([G:E33D02FA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E33D02FA-F3BB-425A-AE5E-24ED534AB1F7)).

### Workflows ([G:6932F056](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6932F056-E9ED-45CA-AECF-F2C4E4B3A98D), [G:579D4643](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-579D4643-A17E-41E4-9ED4-ABBBD107EA99))
- Annotative: 1 create or modify the annotation style; 2 set it current; 3 set the current annotation scale; 4 create the object; 5 optionally add scales; 6 reposition the new representations; 7 create or set a layout current; 8 create a viewport and set its scale.
- Non-annotative: create or modify the style; set it current; create the object; create or set a layout; create a viewport and set its scale. Objects do not resize with the viewport scale; use the arithmetic above.

### Commands and variables (names only) ([G:B4FDF0A4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B4FDF0A4-7936-4D64-B356-D8C2A25D78BD))
- Commands: ANNORESET, ANNOUPDATE, OBJECTSCALE.
- Variables: ANNOALLVISIBLE, ANNOAUTOSCALE, ANNOSCALEZOOM, ANNOTATIVEDWG, CANNOSCALE, CANNOSCALEVALUE, DIMANNO, HPANNOTATIVE, MSOLESCALE, SAVEFIDELITY, SELECTIONANNODISPLAY.
- Set the current annotation scale (GUI): QVDRAWING > Model thumbnail > status bar Annotation Scale list. Layout viewport: QVDRAWING > layout thumbnail > select viewport > Properties > Annotative Scale ([G:65D18FDC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-65D18FDC-B1C7-4760-8CF6-B8380B68D3B4)). (inference) CANNOSCALE is the variable to set from a script; its value format is not in these pages.

## 14.8 Leaders and multileaders

### What a multileader is ([G:8E2FF7CD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8E2FF7CD-1DF9-49F8-AA10-A614C7E63F68), [G:426C9A50](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-426C9A50-9B41-4D38-96BD-BC275D48598A), [G:AD3AE78E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AD3AE78E-FB34-47A9-9BAD-C11196C26228))
- A multileader = leader line(s) + content (mtext or a block). Made arrowhead first, tail first or content first, or from a style.
- One multileader can carry several leader lines, each with one or more segments, so one note can point at several objects. Add or remove lines with MLEADEREDIT or grip menus.
- Leader lines are straight segments or splines. The landing is the short horizontal line joining content to the leader line. Moving the landing or content moves the leader line with it.
- A leader object is not the leader line that a dimension draws by itself.
- Default style STANDARD ("Standard" in the manager): straight leader line, closed filled arrowhead, multiline text content ([G:AD3AE78E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AD3AE78E-FB34-47A9-9BAD-C11196C26228)).
- Annotative blocks cannot be multileader content or arrowheads ([G:A1DA7F82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1DA7F82-690A-496E-AE70-E4B03B2FC679), [G:AD3AE78E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AD3AE78E-FB34-47A9-9BAD-C11196C26228)).
- Associativity: with associative dimensioning on, the arrowhead can be tied to an object point by object snap. If the object moves, the arrowhead stays on it and the line stretches; the text stays where it was ([G:8E2FF7CD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8E2FF7CD-1DF9-49F8-AA10-A614C7E63F68)).
- Associativity is lost, for example, when a block is redefined so the attached point moves, or when a model documentation view update removes the point ([G:426C9A50](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-426C9A50-9B41-4D38-96BD-BC275D48598A)).
- Rotated view: run UCS > View before creating leaders ([G:426C9A50](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-426C9A50-9B41-4D38-96BD-BC275D48598A), [G:7B194BD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B194BD5-421E-4BC5-94A4-A805134003F4)).

### Content options ([G:A1DA7F82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1DA7F82-690A-496E-AE70-E4B03B2FC679))
- Text content: style, color, height and alignment can be set in the leader. Landing Gap in the style sets the text offset from the landing.
- Text attachment, nine choices: Top of top line; Middle of top line; Bottom of top line; Underline top line; Middle of text; Middle of bottom line; Bottom of bottom line; Underline bottom line; Underline all text.
- Block content: the style must reference a block already in the drawing. The landing attaches to a chosen insertion point of the block or to its center.
- [AUTO] Non-annotative multileaders scale with MLEADERSCALE.
- Annotative with text: text scales per representation; width, justification, attachment and rotation can differ per scale; the text content cannot.
- Annotative with a block: the block scales per representation; attributes inside it do not.
- Annotative with several segments: head points, landing size, arrowhead size and landing gap can differ per scale. Landing look, straight vs spline, and segment count stay the same in every scale ([G:8E2FF7CD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8E2FF7CD-1DF9-49F8-AA10-A614C7E63F68)).

### MLEADER [AUTO]
- Straight leader ([G:CD496790](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CD496790-85A6-46CA-83F3-B113A6BF4F3D)): MLEADER; `o` (options); `l` (leaders); `s` (straight); pick head start point; pick end point; type the mtext; OK.
- Spline leader ([G:4F382D40](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F382D40-A4C8-4C3E-B416-E7D53C92558E)): MLEADER; `o`; `l`; `t` (leader type); `p` (spline); pick start point; pick end point; type the mtext; OK.
- The two pages differ: the spline page has a `t` step the straight page lacks. (inference) One page skips a step. Probe the live option list before scripting.
- Existing mtext to leader ([G:9E772A74](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9E772A74-598C-4419-8B88-B8B7BFE697E8)): MLEADER; `c` (select content); `m` (select an existing multiline text object); specify the arrowhead location.
- The text is typed in the mtext editor and closed with OK ([G:CD496790](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CD496790-85A6-46CA-83F3-B113A6BF4F3D)). (inference) That editor needs a person. For unattended work build multileaders through COM or AutoLISP, and test MLEADER inside a .scr before relying on it.
- New multileaders use the current style. (inference) CMLEADERSTYLE holds it; the index page only lists the name ([G:6BB997D6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6BB997D6-662D-44D9-AFF8-094162DA2B84)). MLEADERLAYER is also listed there without a meaning.

### Editing multileaders
- [AUTO] MLEADERALIGN ([G:D4DDF671](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D4DDF671-9569-4891-A326-56A95DA683D3)): select the multileaders, ENTER; pick a start point (where the landing head goes); optional `s` and a spacing method: Distribute (even spacing between two picked points), Use Current (keep spacing), Make Parallel (last segments made parallel); click to end.
- [AUTO] MLEADERCOLLECT ([G:89691A32](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-89691A32-F357-42DC-A537-EEEFCA38F01F)): select multileaders in the order to collect; the LAST one keeps its landing; ENTER. Gathers block-content multileaders on one landing, horizontally, vertically, or within an area ([G:8E2FF7CD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8E2FF7CD-1DF9-49F8-AA10-A614C7E63F68)).
- Add a leader line (MLEADEREDIT) ([G:9AC1268F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9AC1268F-C36F-43C0-B3F4-32EEDE86DE2A)): select the multileader; hover the landing grip > Add Leader, or Annotate tab > Leaders panel > Add Leader; pick the new endpoint.
- Remove a leader line ([G:85E42888](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-85E42888-D615-49E3-836B-065C17DBFCD9)): hover an endpoint grip > Remove Leader, or the Remove Leader tool, select the leaders, ENTER.
- Grip menus ([G:23160F88](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-23160F88-FF56-4BA8-BC92-59C7D5D34872)): endpoint grip = Stretch, Add Vertex, Remove Leader. Vertex grip at the landing end = Stretch, Lengthen Landing, Add Leader. Other vertex grips = Stretch, Add Vertex, Remove Vertex. The landing grip lengthens or shortens the landing.
- Edit the text: double-click. Ribbon on = MTEXT contextual tab; ribbon off = In-Place Text Editor ([G:88BDAF8F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-88BDAF8F-2DE3-4BF2-BED5-0A2F4191D0BA)).
- Apply a style to an existing multileader: select it, pick the style in Annotate tab > Multileaders panel ([G:4F6E373E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F6E373E-F540-4A00-BCB7-C069FFDAA29A)).
- Segment properties are in the Properties palette ([G:8E2FF7CD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8E2FF7CD-1DF9-49F8-AA10-A614C7E63F68)).

### Annotation monitor ([G:DE2691C0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DE2691C0-9E3D-4D6F-8FB5-1709AE4969FD), [G:426C9A50](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-426C9A50-9B41-4D38-96BD-BC275D48598A))
- Flags annotations that lost associativity with a badge; the badge menu offers DIMREASSOCIATE and ERASE. Example: erase a circle and its dimension gets a badge.
- Toggle with the status bar button.
- [AUTO] Model documentation events only: type `ANNOMONITOR`, then `-2`. The monitor turns itself on (ANNOMONITOR = 2) at the first model documentation edit or update. The value for "all events" is not on the page.

### Leader command and variable names ([G:6BB997D6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6BB997D6-662D-44D9-AFF8-094162DA2B84))
- Commands: LEADER, MLEADER, MLEADERALIGN, MLEADERCOLLECT, MLEADEREDIT, MLEADERSTYLE, PROPERTIES, QLEADER.
- Variables (names only): CMDDIA, CMLEADERSTYLE, DIMASSOC, DIMASZ, DIMCLRD, DIMGAP, DIMLDRBLK, DIMSCALE, DIMTAD, DIMTXTDIRECTION, EXTNAMES, GALLERYVIEW, MLEADERLAYER, MLEADERSCALE.

### MLEADERSTYLE (Multileader Style Manager) [GUI] ([G:C4202790](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C4202790-AA18-4516-862D-110FE6A5E43B))
- Styles cover landing lines, leader lines, arrowheads and content.
- Current Multileader Style (default Standard). Styles list. List filter: All Styles or Styles In Use. Preview Of. Set Current (all new multileaders use it). New. Modify. Delete (a style in use cannot be deleted).
- Create New Multileader Style ([G:5965F3A2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5965F3A2-6145-4386-BDCB-6B9CDB665017)): New Style Name; Start With (existing style used as defaults); Annotative; Continue.
- Modify Multileader Style has three tabs: Leader Format, Leader Structure, Content ([G:9A26BE7C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A26BE7C-34BC-4E84-AD0B-67C320C9DD77)).
- (inference) The manager is dialog only. Build multileader styles in the template DWT.

### Leader Format tab ([G:628D9925](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-628D9925-4537-4F12-86BC-7EC880C64922))
- General: Type (straight, spline or none); Color; Linetype; Lineweight.
- Arrowhead: Symbol; Size.
- Leader Break: Break Size = the gap DIMBREAK uses on a multileader.

### Leader Structure tab ([G:E42AB914](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E42AB914-B055-4D67-9A97-88D708006105))
- Constraints: Maximum leader points; First segment angle; Second segment angle.
- Landing settings: Automatically include landing (horizontal landing on the content); Set landing distance (fixed landing length). The task page names the first one "Landing - Keep Horizontal" ([G:BBF1A961](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BBF1A961-C7CA-4949-A4E4-9D4B03F6E60F)).
- Scale: Annotative; Scale multileaders to layout (factor from model and paper space viewport scaling); Specify scale. The last two exist ONLY when the style is not annotative.

### Content tab ([G:16C41557](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-16C41557-2036-4912-9FE8-7DDE6A8AC5AE), [G:BBF1A961](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BBF1A961-C7CA-4949-A4E4-9D4B03F6E60F))
- Multileader Type: MText or Block; the choice changes the other options.
- MText: Default Text ([...] opens the mtext editor; a field can go here); Text Style (loaded styles only) plus Text Style button; Text Angle; Text Color; Text Height (the task page calls it "Paper Height", the height shown in paper space); Always Left Justify; Frame Text (gap = Landing Gap).
- Horizontal attachment (leader left or right of the text, with a landing): Left Attachment (used when text is right of the leader); Right Attachment (text left of the leader); Landing Gap; Extend Leader to Text (landing ends at the edge of the attached text line, sized by the longest line, not the mtext box).
- Vertical attachment (leader at top or bottom center, NO landing): Top Attachment (drop-down adds an overline); Bottom Attachment (adds an underline); Landing Gap.
- Block: Source block; Attachment (insertion point or center point; task pages also name block extents and Center Extents); Color (takes effect only when the block's objects are ByBlock; ByBlock is the default); Scale (a 1" square block at 0.5 inserts 1/2" square).

### Style recipes
- New style ([G:BBF1A961](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BBF1A961-C7CA-4949-A4E4-9D4B03F6E60F)): Home tab > Annotation > Multileader Style > New > name > Modify > set the three tabs.
- Landing with several segments ([G:D76929A9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D76929A9-867D-4006-A6BF-69C7947CDEE8)): Leader Structure > Constraints > check Maximum Leader Points, enter the count; OK; Set Current.
- Leader to block content at an angle ([G:CD91C9B6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CD91C9B6-8793-41D6-B6EE-1F3BC1DF68F2)): new style; Leader Structure > clear Automatically Include Landing; Content > Multileader Type = Block; Attachment = Center Extents (leader goes to the block's center extent) or Insertion Point (attaches from any point you pick); OK; Close; then create or apply.

### QLEADER and the Leader Settings dialog ([G:3351DB2D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3351DB2D-FDD5-42AD-981F-782862C524BD))
- The Settings option at QLEADER's first prompt opens Leader Settings (tabs Annotation, Leader Line and Arrow, Attachment). (inference) That option opens a dialog; a script should not pick it.
- Annotation Type (sets the annotation prompt): MText (prompts for mtext); Copy an Object (copies an mtext, text, tolerance or block reference and ties it to the leader end; move the copy and the leader end follows); Tolerance (opens the Tolerance dialog); Block Reference (prompts to insert a block, offset from and associated with the leader end, no hook line); None.
- MText Options (MText type only): Prompt for Width; Always Left Justify; Frame Text. Annotation Reuse: None; Reuse Next; Reuse Current.
- Leader Line: Straight or Spline. Arrowhead: the dimension arrowheads; "User Arrow" lists blocks in the drawing.
- [AUTO] Number of Points = how many leader points QLEADER asks for before the annotation prompt. Set it one more than the segments wanted (3 gives the annotation prompt after 2 points). No Limit asks until Enter. Angle Constraints: First Segment, Second Segment.
- Attachment tab (MText only): Top of Top Line; Middle of Top Line; Middle of Multiline Text; Middle of Bottom Line; Bottom of Bottom Line; Underline Bottom Line.
- [AUTO] Prompt order: leader points (count per Number of Points), then the prompt for the annotation type. Exact prompt wording is not on the page.

## 14.9 Tables

### What a table is ([G:831E41E7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-831E41E7-04EB-44DE-BEC8-F6A3A992DA61), [G:825B0E42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-825B0E42-C627-4053-95A7-57B67B0632AE))
- One compound object of rows and columns. Use it for schedules, parts lists, bills of materials, price lists. Cells hold text, blocks or numbers, computed from other cells or from external data.
- Made by TABLE (rows and columns) or by referencing an Excel spreadsheet.
- Table style = defaults for the table plus any number of cell styles. A cell style holds General (fill color, alignment, format, margins), Text (text style, height, color) and Borders (lineweight, linetype, color, display).
- Default table style Standard. Cell styles Title, Header and Data are ALWAYS in every table style and cannot be renamed or deleted ([G:8C5C592E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C5C592E-C0CC-456C-86A6-E34B67A026C7), [G:918CE7B7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-918CE7B7-9D4E-4F22-9A2B-CD89D49B4BAE)). Title and Header are Label type; Data is Data type. Best practice: leave those three unchanged and base new cell styles on them ([G:825B0E42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-825B0E42-C627-4053-95A7-57B67B0632AE)).
- Table styles live in the DWG or DWT like text and dimension styles; import them from other drawings with DesignCenter ([G:825B0E42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-825B0E42-C627-4053-95A7-57B67B0632AE), [G:831E41E7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-831E41E7-04EB-44DE-BEC8-F6A3A992DA61)).
- A data link connects a table to a Microsoft Excel file or a data extraction (.dxex) file; one-way or two-way, and you pick where computing happens ([G:831E41E7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-831E41E7-04EB-44DE-BEC8-F6A3A992DA61)).

### TABLE (Insert Table dialog) [GUI] ([G:135907BC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-135907BC-6148-4DC7-93A9-65233D882919))
- TABLE opens this dialog and makes an empty table. No dialog-free prompt list for TABLE is in these pages.
- Table Style list; the button beside it makes a new style.
- Insert Options: Start from Empty Table; Start from Data Link (external spreadsheet); Start from Data Extraction (wizard; not in LT).
- Preview: clear it to speed up large tables.
- Insertion Behavior: Specify Insertion Point = UPPER-left corner (LOWER-left when the style reads bottom-up), picked or typed at the Command prompt; Specify Window = size and place by window, and column and row counts or sizes follow the window.
- Column & Row Settings: Columns; Column Width (minimum one character); Data Rows; Row Height in LINES (one line = text height + cell margin from the style). With a starting table, columns and data rows are ADDITIONAL ones. A style with a title and a header row has at least 3 rows. Minimum row height one line.
- Set Cell Styles (style without a starting table): First Row = Title, Second Row = Header, All Other Rows = Data (defaults).
- Table Options (style with a starting table): keep Label Cell Text, Data Cell Text, Blocks, Retain Cell Style Overrides, Data Links, Fields, Formulas.

### TABLESTYLE [GUI] ([G:DDF3DE7B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DDF3DE7B-1C5D-41E2-A668-B07293405FCF), [G:4DCAAF7A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4DCAAF7A-27BF-40A8-B363-41C2ED4E4ABE), [G:C4F0C32E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C4F0C32E-F87B-41A3-B8F3-BAEFB90F8EF0), [G:2DA5D845](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2DA5D845-E556-4BDC-B6B6-C925DF445556), [G:8C5C592E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C5C592E-C0CC-456C-86A6-E34B67A026C7))
- Table Style dialog: Current Table Style; Styles list; List filter; Preview; Set Current (new tables use it); New; Modify; Delete (a style in use cannot be deleted).
- Create New Table Style: New Style Name; Start With; Continue.
- New / Modify Table Style: Starting Table (pick a table in the drawing as the model, then choose what to copy; Remove Table icon un-assigns it).
- General > Table Direction: Down = title and column heads at the top, Insert Rows > Below adds below. Up = title and heads at the bottom, Insert Rows > Below adds ABOVE.
- Cell Styles area: Cell Style menu; Create Cell Styles button (Create New Cell Style: New Style Name, Start With, Continue); Manage Cell Styles (New, Rename, Delete; Title, Header, Data cannot be renamed).
- Cell style General tab: Fill Color (default None); Alignment (top/middle/bottom and left/center/right); Format (Table Cell Format dialog); Type (label or data); Margins Horizontal and Vertical, default 0.06 imperial or 1.5 metric, applied to all cells; "Merge cells on row/column creation" (used to build a title row).
- Text tab: Text Style; Text Height default 0.1800 for data and column heads, 0.25 for the title; Text Color; Text Angle default 0, range -359 to +359.
- Borders tab: Lineweight (heavy weights may need bigger margins); Linetype (Other loads one); Color; Double Line; Spacing (default 0.1800); buttons All, Outside, Inside, Bottom, Left, Top, Right, No Border.
- (inference) Every table style screen is a dialog. Keep schedule table styles in the template DWT.

### Cell data formats ([G:DA292CE6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DA292CE6-B6A7-4F5F-8307-C92B6C130B96), [G:C8237C1D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C8237C1D-FEBF-4D4D-9092-F2F1B552383D))
- Table Cell Format: Data Type (types named on the pages: Angle, Currency, Date, Decimal Number, General, Percentage, Point, Text, Whole Number); Format (for Angle: Decimal Degrees, Grads, Radians and others); Precision (Angle, Decimal Number, Point); List Separator (Point: comma, semicolon, colon); Symbol and Negative Numbers (Currency); Append Symbol (Currency, Percentage); X/Y/Z filter (Point); Examples (Date).
- Additional Format (Angle, Decimal Number, Point, Whole Number): Current Value in base drawing units; Conversion Factor (default 1 = none); Additional Text (prefix or suffix); Decimal separator period, comma or space; Thousands comma; Zero Suppression: Leading (0.5000 shows .5000), Trailing (12.5000 shows 12.5; 30.0000 shows 30), 0 Feet (0'-6 1/2" shows 6 1/2"), 0 Inches (1'-0" shows 1').

### Editing tables ([G:CE2CC84F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CE2CC84F-944A-4EE6-B824-9B81692F5B7B), [G:BE0B1AFA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BE0B1AFA-6BCE-49E9-AE84-7F85D17B77D1))
- Click a gridline to select the table, then use grips or the Properties palette. A row or column grip changes only the neighbor; the table keeps its overall size. Hold Ctrl while dragging a column grip to resize the table in proportion.
- Click inside a cell to select it; drag or Shift+click for a block of cells. Ribbon on = Table Cell contextual tab; ribbon off = Table toolbar.
- On creation the first cell is ready for text. Typing in a selected cell replaces its content; double-click to edit. Tab or arrow keys move to the next cell. Row height grows to fit the text.
- Ctrl+Y repeats the last action on selected cells, but only actions from the shortcut menu, Table Cell tab or Table toolbar.
- [AUTO] TABLEINDICATOR turns the column letters and row numbers in the In-Place Text Editor on or off (shown by default). Their background: right-click > Table Indicator Color; text color, size, style and line color come from the column head settings of the current table style.
- Table breaks: Properties palette > Table Breaks splits a long table into a primary and secondary parts placed right, left or below, with set maximum height and spacing. Manual Positions = Yes allows grip moves of the parts.
- Cell properties ([G:8C7D2C85](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C7D2C85-ACC8-49E8-807F-0D69E429937A)): select cells, edit in Properties. Right-click > Remove Property Overrides restores the style.
- Rows and columns ([G:5019ECC2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5019ECC2-1C1E-4A54-8B66-B3F7E46911CC)): right-click > Rows > Insert Above / Insert Below; Columns > Insert Left / Insert Right; or right-click a row or column label.
- Another table style ([G:0772146E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0772146E-36E7-4F25-86F0-CD7EE4D426C3)): select the table > Annotate tab > Table panel > Table Style list. If the old style had a title row and the new one does not, the title text goes into the first cell and the rest of row 1 is blank.
- Save as style: cell right-click > Cell Style > Save as New Cell Style ([G:1DD4D1B3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1DD4D1B3-8EFE-4D58-AD4B-C13CD4C31872)); table right-click > Table Style > Save as New Table Style ([G:F1D99768](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F1D99768-F76B-4731-B347-95B59C66B50F)).
- Tool palette: right-drag the table onto a palette; all formatting and properties are saved in the tool ([G:27204BF3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-27204BF3-475E-44A8-A9C5-18ED04B72F6F)).
- AutoFill ([G:82675AEA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-82675AEA-30E2-4957-9C53-D4904C3229FD), [G:505EF5BB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-505EF5BB-5347-43DA-91A6-03141A9134C8)): drag a cell's lower-right grip. One number fills in steps of 1; one date in steps of 1 day; two dates a week apart continue in 1-week steps.

### Table Cell contextual tab ([G:918CE7B7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-918CE7B7-9D4E-4F22-9A2B-CD89D49B4BAE))
- Rows: Insert Above, Insert Below, Delete Row(s). Columns: Insert Left, Insert Right, Delete Column(s).
- Merge: Merge All, Merge By Row, Merge By Column; Unmerge Cells.
- Cell Styles: Match Cell, Alignment, cell style list, Background Color, Cell Borders.
- Cell Format: Cell Locking (content, format or both); Data Format with the same controls as Table Cell Format.
- Insert: Block, Field (not LT), Formula (not LT), Manage Cell Contents.
- Data: Link Cell; Download from Source (pulls changed data through an existing link).

### Cell borders ([G:FFA80DE7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FFA80DE7-A343-43D3-9084-3EE5EF7F2C50), [G:1F4E5427](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1F4E5427-32E1-4D1A-B815-A2B92C27D666))
- Select cells > right-click > Borders: Lineweight, Linetype, Color, Double Line (spacing default .1800). Apply to: All, Outside, Inside, No Borders, Top, Inside Horizontal, Bottom, Left, Inside Vertical, Right. Choose BYBLOCK so borders follow the table style. The preview does not show linetypes.

### Formulas [AUTO] ([G:505EF5BB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-505EF5BB-5347-43DA-91A6-03141A9134C8), [G:15E0C775](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-15E0C775-6E60-456D-B5C7-4726E0C586B7), [G:D87DA035](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D87DA035-5B52-4F58-85CF-5E2ED9E4FDFB), [G:89588DD2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-89588DD2-C1C5-4AA1-83DB-7375389FE891))
- A formula starts with `=`. Address = column letter + row number; top-left cell is A1. A merged cell uses its top-left address. Range `A5:C10` = rows 5 to 10 of columns A to C. Colon = range; comma = single cells.
- Operators: + - * / ^ and parentheses. Page examples: `=sum(a1:a25,b1)`; `=average(a100:d100)`; `=count(a1:m500)` (the page text says "rows 1 through 100", which does not match the range); `=(a6+d6)/e1`.
- Sum, average and count skip empty and non-numeric cells. Any other formula shows `#` when a referenced cell is empty or non-numeric.
- Copying a formula shifts its references (A10 summing A1:A9, copied to B10, sums B1:B9). `$A10` keeps the column; `$A$10` freezes both.
- The Cell option can pick a cell in another table in the same drawing.
- Field route: Table Cell tab > Field > Field Category Objects > Field Names Formula > Average, Sum or Count (pick first and last cell) or Cell (pick a cell); OK. Enter `q` (Quit) to save and leave the editor ([G:D87DA035](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D87DA035-5B52-4F58-85CF-5E2ED9E4FDFB)).
- Type route: Table Cell tab > Formula > Equation, type, click outside to save ([G:15E0C775](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-15E0C775-6E60-456D-B5C7-4726E0C586B7)).
- (inference) Formula text is plain cell text, so a script or COM call can write it into a cell.

### Fields, blocks and mixed content in cells
- Field in a cell ([G:CA280E03](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA280E03-4CA5-4033-885A-39B2220D0571), [G:B24A017B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B24A017B-66CA-4F24-AC50-7CAEAC737B7A)): double-click the cell, right-click > Insert Field (Ctrl+F), pick field and format, OK. The value shows after you move to the next cell.
- Block in a cell, TINSERT [GUI] ([G:3A3FBF20](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3A3FBF20-559F-4A39-8196-6200BC46B5AA), [G:5205DFAF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5205DFAF-7C96-4566-B7CD-AA77C48E0160)): Name, or Browse to insert a DWG as a block; Scale value or AutoFit (scale the block to the cell, or size the cell to the block); Rotation Angle; Overall Cell Alignment. A block with attributes opens the Edit Attributes dialog. No command-line prompts are given.
- A cell can hold several blocks plus text. Manage Cell Content ([G:1CBD3316](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1CBD3316-A352-49A0-847E-B5E8EF123BA3)): list in order ("Table Cell Text", "Block <name>"); Move Up, Move Down, Delete; Layout Flow, Stacked Horizontal or Stacked Vertical; Content Spacing.

### Data links to Excel or CSV ([G:3A038CCF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3A038CCF-A659-4E8A-AE6E-1D88D00D3A23), [G:A9C8C253](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A9C8C253-C947-4C17-BDE8-911FD3360FF5), [G:4E678DBE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E678DBE-1698-41C6-AFE2-8E2759D4070F), [G:F3E99252](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F3E99252-D893-4939-AEC2-52794C65263A))
- Source: CSV, XLS or XLSX; whole sheet, a row, a column, a cell or a range. Microsoft Excel must be installed to use Excel data links.
- [GUI] DATALINK opens the Data Link Manager: Excel Links tree (chain icon = valid, broken chain = broken); Create a New Excel Data Link asks a name, then opens New Excel Data Link.
- New Excel Data Link: File; Path Type Full Path, Relative Path (drawing must be saved first) or No Path; Select the Excel Sheet; Link Entire Sheet; Link to a Named Range; Link to Range (A1:D10, A:A, A:D).
- Cell Contents: Keep Data Formats and Formulas; Keep Data Formats, Solve Formulas in Excel; Convert Data Formats to Text, Solve Formulas in Excel; Allow Writing to Source File.
- Cell Formatting: Use Excel Formatting (off = table style applies); Keep Table Updated to Excel Formatting; Start With Excel Formatting, Do Not Update.
- [AUTO] DATALINKUPDATE refreshes the table after the spreadsheet changes, and writes table edits back to the file ([G:3A038CCF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3A038CCF-A659-4E8A-AE6E-1D88D00D3A23)); writing back needs Allow Writing to Source File ([G:A9C8C253](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A9C8C253-C947-4C17-BDE8-911FD3360FF5)).
- Linked cells are locked against editing by default. Lock content, format or both; unlock with Locking on the Table Cell tab. Hover shows the link info ([G:3A038CCF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3A038CCF-A659-4E8A-AE6E-1D88D00D3A23)).
- Link cells ([G:4E678DBE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E678DBE-1698-41C6-AFE2-8E2759D4070F)): select cells > Table Cell tab > Data > Link Cell > Create a New Excel Data Link > name > browse > options > OK.
- Open the source: right-click > Data Links > Open Data Link File ([G:05AE7D62](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-05AE7D62-C1C7-4E34-8668-DF65DD0A8B82)). Remove: right-click > Data Links > Detach Data Link ([G:430F062F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-430F062F-B5B1-4ADB-8697-901772676BC7)).
- Named range: in Excel select cells, type a name in the Name Box, Enter, save ([G:280B8BC6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-280B8BC6-C997-4EB5-9634-14516A5C1192)).

### Table names (index page, names only) ([G:CA9995D8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA9995D8-98B2-4BFB-972F-FEB0934A1E33))
- Commands: DATALINK, DATALINKUPDATE, FIELD, TABLE, TABLEDIT, TABLEEXPORT, TABLESTYLE, TINSERT, UPDATEFIELD.
- Variables: CTABLESTYLE, DATALINKNOTIFY, EXTNAMES, FIELDDISPLAY, GALLERYVIEW, TABLEINDICATOR, TABLELAYER, TABLETOOLBAR.

## 14.10 Fields

### What a field is ([G:B9ADAE6A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B9ADAE6A-2DD1-4C44-B126-CF3FF92EBC68))
- An instruction to show data that changes over the drawing's life (example: FileName). Updating shows the latest data.
- Fields go in mtext, single-line text, table cells, attributes and attribute definitions; not in tolerances. Insert Field is on the shortcut menu whenever a text command is active (Ctrl+F in the editor).
- No value available shows `----` (example: a blank Author property). An invalid field shows `####` (the page's example: CurrentSheetName, valid only in paper space, placed in model space).
- Field text uses the text style of the object that holds it. [AUTO] FIELDDISPLAY controls the light gray background, which does not plot.

### Updating fields
- [AUTO] By default, normal fields refresh on save or REGEN ([G:1B6DD22B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327)). FIELDEVAL is listed ([G:2776142F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2776142F-A289-4ABE-96ED-ABC3518B82A9)) but not explained in these pages.
- [AUTO] UPDATEFIELD (Insert tab > Data panel > Update Fields): select objects, ENTER; every field in them updates ([G:41B09208](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-41B09208-E652-460A-B6EA-9B9A5FAAEB68)). One field: double-click the text, right-click the field > Update Field.
- Sheet set fields keep their last stored value; when the source cannot be reached they show `####`. Refresh them with UPDATEFIELD ([G:1B6DD22B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327)).

### Contextual fields and title blocks [AUTO] ([G:D32A29E7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D32A29E7-7B98-4ADB-BF32-5CC24DBCC8C3))
- Contextual fields change with the space or layout they sit in: CurrentSheetCustom, CurrentSheetDescription, CurrentSheetNumber, CurrentSheetNumberAndTitle, CurrentSheetSet, CurrentSheetSetCustom, CurrentSheetSetDescription, CurrentSheetSubSet, CurrentSheetTitle, DeviceName, PaperSize, PlotDate, PlotOrientation, PlotScale, PageSetupName, PlotStyleTable.
- RULE: inside blocks and xrefs, contextual fields are NOT recalculated on insert; they keep the last cached value. To use one in a title block, put it in an ATTRIBUTE. Example: CurrentSheetNumber in an attribute shows the number of the sheet the title block sits on.
- Non-contextual fields update inside blocks and xrefs without an attribute. Fields in xrefs update from the host file, not the source file.
- A SheetSet field showing a chosen sheet's SheetNumber stays right when its block lands in another drawing; it turns `####` if that sheet leaves the sheet set.

### FIELD dialog [GUI] ([G:1B6DD22B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327))
- Field Category (All, or one category such as Date & Time, Document, Objects, SheetSet); Field Names; Field Value (labelled Property for object fields); Format list (dates with or without weekday; text uppercase, lowercase, first capital, title case); Field Expression (read-only view of the underlying expression).
- Date fields show the format (example M/d/yyyy) and an Examples list ([G:7F254BA7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7F254BA7-5C83-451B-A586-A78EE5D22C64)).
- Objects category: NamedObject lists named object types (layer, text style and others) and their names (example 0, STANDARD). Object + Select Object (dialog closes while you pick) lists the picked object's properties; for a block with attributes the attribute names appear.
- Display Value for Block Reference: object-property fields inside a block reference evaluate nested objects by the reference's size and orientation in the drawing, not by the block definition.
- Formula: Average, Sum, Count and Cell buttons close the dialog while you pick cells. Precision ("Current Precision" uses LUPREC). Additional Format. Evaluate refreshes the preview after hand edits.
- Sheet Set and Sheet View fields: Sheet Set name; Sheet Navigation Tree; Property; Associate Hyperlink (Ctrl+click jumps to the sheet or view; not for ViewportScale). For a sheet that is already in a sheet set, use a sheet set property field, not a placeholder.
- BlockPlaceholder: insertable only in the Attribute Definition dialog while the Block Editor is open. Block Name, Temporary Value, Block Reference Properties.
- SheetSetPlaceholder: Placeholder Type, Temporary Value. Example: SheetSet Placeholder + SheetTitle + Uppercase shows SHEETTITLE until the drawing is placed in a sheet set, then the sheet title.
- Edit a field: double-click the text, double-click the shaded field, change it, OK, close the editor ([G:2B4B98F9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2B4B98F9-2CDD-4B58-BBB6-2717C99D000A)).

### Field tasks ([G:7F254BA7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7F254BA7-5C83-451B-A586-A78EE5D22C64), [G:F613CBDA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F613CBDA-5899-4419-9C23-2E0F6C76BB99))
- In text: double-click the text, place the cursor, right-click > Insert Field (or Ctrl+F), pick Category, Field Names, format, OK.
- Object property (example: a circle's radius): Category All, Field Names Object, Select Object, pick the Property and format, OK.

### Field value format ([G:D1EA1BF5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1EA1BF5-6442-47EF-82F5-D6849A07906E))
- The Field Format button opens Additional Format: Conversion factor (multiplies the value); text before or after (example "mm"); decimal separator; thousands grouping None or Comma; zero suppression Leading, Trailing, 0 Feet, 0 Inches.
- The page says "to convert inches to millimeters, enter 0.03937". (inference) 0.03937 is 1/25.4, the mm-to-inch factor; inches to mm would be 25.4. Test before relying on it.

### Hyperlinks on fields ([G:14933ABC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-14933ABC-8574-430C-8CBE-467BB6B3CCB8))
- Ctrl+click follows a field's hyperlink: URL, file, saved view or layout. Kept while the field is unchanged. Hyperlinks made in Windows AutoCAD do not open in AutoCAD for Mac.
- The Hyperlink field stores an ABSOLUTE file path. The HYPERLINK command can store a relative one.
- Sheet and view title and number fields keep working after changes in Sheet Set Manager. In multi-sheet DWF publishing, DWG links in fields become DWF links.

### Sheet set placeholder inside a title or callout block [GUI] ([G:DA868354](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DA868354-801C-43E1-AA31-9C14B51F6D9C))
- Home tab > Block panel > Define Attributes (ATTDEF): Mode Preset; a Tag; Insert Field button beside Value; Category SheetSet; Field Names SheetSetPlaceholder; Placeholder Type; Format (capitalization on later updates); optional Associate Hyperlink (not for ViewportScale); OK; OK; pick the location; then make a block of the attribute plus the geometry.
- It shows its own name (example SheetNumber) until the block is inserted from a Sheet Set Manager shortcut menu (the page says the Views List tab), then it shows that sheet's value.
- Set all attribute definitions in label and callout blocks to Preset so placing them does not prompt ([G:87F36464](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-87F36464-0801-44B9-BF33-7430E75B4C74)).

## 14.11 Blocks and attributes

### Attribute basics ([G:67A2DDAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-67A2DDAD-2217-412F-8AEF-D4495192F45B))
- An attribute attaches data (part numbers, prices, comments, owner names) to a block. A block can hold several attributes, each with its own tag.
- A definition has a unique tag, a prompt shown at insertion, and a default value used when nothing is typed.
- Tags must be unique. Duplicates give unpredictable results and break data extraction and dynamic blocks; they show red in BATTMAN (Emphasize Duplicate Tags) and in the Enhanced Attribute Editor ([G:F351FDBB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F351FDBB-2731-40C1-A186-1B1F47779E32), [G:414DC467](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-414DC467-291B-4A52-A70D-1165CDEA8B39)).
- Single-line attribute value: max 255 characters. Multiline attributes allow richer formatting; saved to 2007 or earlier format they split into several single-line attributes, and are restored when reopened in a later release.
- Invisible: not displayed or plotted, but stored and extractable. Constant: fixed value, no prompt. Variable: prompts on every insert.
- Stand-alone attributes (no block) are allowed. Insert that drawing into another and you are prompted for the values.
- Keep a list of tags if you will extract data; the template needs them.

### Attaching attributes and prompt order ([G:67A2DDAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-67A2DDAD-2217-412F-8AEF-D4495192F45B), [G:4B47412C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4B47412C-108C-4F69-BB0D-60DDDB713169))
- Attach by including the attribute definitions in the selection when you define or redefine the block with BLOCK.
- Prompt order = the order the attributes were SELECTED. With a crossing or window selection, the order is the REVERSE of the order they were created. Fix it with BATTMAN Move Up / Move Down or BATTORDER in the Block Editor.
- (inference) For a block written outside AutoCAD (DXF), the order of the attribute definitions inside the block is the likely prompt order. Check with BATTMAN.

### BLOCK / BMAKE (Block Definition dialog) [GUI] ([G:03B61417](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-03B61417-F040-4EB0-AFEA-B229AD303D91))
- No command-line form is given on this page.
- Name: up to 255 characters; letters, numbers, spaces and any special character not reserved by the OS or program. Saved in the current drawing.
- Base Point: default 0,0,0; Specify On-Screen, Pick Insertion Base Point, or type X, Y, Z.
- Objects: Specify On-Screen, Select Objects (dialog hides; Enter returns), Quick Select; then Retain, Convert to Block, or Delete.
- Behavior: Annotative; Match Block Orientation to Layout (only with Annotative); Scale Uniformly; Allow Exploding.
- Settings: Block Unit (insertion units); Hyperlink. Description. Open in Block Editor.

### ATTDEF (Attribute Definition dialog) [GUI] ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38), [G:4B47412C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4B47412C-108C-4F69-BB0D-60DDDB713169))
- Home tab > Block panel > Define Attributes. Only the dialog route is given in these pages; the definition is then included in a block with BLOCK.
- Mode (behavior at insertion):
  - [AUTO] Defaults come from AFLAGS. Changing AFLAGS affects NEW definitions only, never existing ones.
  - Invisible: value not shown or plotted. [AUTO] ATTDISP overrides Invisible.
  - Constant: fixed value; the Prompt box is unavailable.
  - Verify: asks to confirm the value at insertion.
  - [AUTO] Preset: default used with no prompt. Works ONLY when attribute prompts are on the command line (ATTDIA = 0).
  - Lock Position: fixed inside the reference. Unlocked = grip-movable, and multiline attributes can be resized.
  - Multiple Lines: enables Boundary Width and the multiline editor button.
- Attribute: Tag (any characters except spaces; lowercase is converted to uppercase); Prompt (blank = the tag is used); Default; Insert Field button; Multiline Editor button ([AUTO] ATTIPE picks the abbreviated or full Text Formatting toolbar).
- Insertion Point: Specify On-screen (dialog closes, Start Point prompt) or type X, Y, Z.
- Text Settings: Justification; Text Style (loaded styles only); Annotative (matches block orientation if the block is annotative); Text Height (not available if the style has a fixed height or Justification is Align); Rotation (not with Align or Fit); Boundary Width (multiline only; 0.000 = no limit).
- Align Below Previous Attribute Definition: places the tag right below the last one defined.
- Edit a definition before it is in a block: double-click it (TEXTEDIT) > Edit Attribute Definition dialog: Tag (may contain exclamation marks), Prompt, Default ([G:8B059251](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8B059251-CDB9-41CC-AC61-FAA4E8416852), [G:BF34ECF7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BF34ECF7-74C1-415C-88CF-B61F7591B691)).

### Attribute command and variable names ([G:61A6871E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-61A6871E-E74F-4959-8281-934C77D1EBF4))
- Commands: ATTDEF, ATTDISP, ATTEDIT, ATTEXT, ATTIPEDIT, ATTREDEF, ATTSYNC, BATTMAN, BATTORDER, DATAEXTRACTION, EATTEDIT, EATTEXT, PROPERTIES, TEXTEDIT.
- Variables: AFLAGS, ATTDIA, ATTIPE, ATTMODE, ATTMULTI, ATTREQ, DXEVAL, TEXTEDITMODE. Of these, only AFLAGS, ATTDIA and ATTIPE are explained in these pages ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38)).

### Scripted insertion of attributed blocks (inference, test first)
- Only variable, non-preset attributes should prompt, in prompt order. Constant attributes never prompt ([G:67A2DDAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-67A2DDAD-2217-412F-8AEF-D4495192F45B)). Preset takes the default when ATTDIA = 0 ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38)). Verify adds a confirm step ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38)).
- After redefining a block, run ATTSYNC on it so old references get the new definition; their stored values stay ([G:889213DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-889213DA-A3AF-4020-89F0-1E5049AD26EC)).
- The INSERT and -INSERT prompt lists are not in these pages.

### BATTMAN (Block Attribute Manager) [GUI] ([G:4920952B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4920952B-6809-49E7-956E-C6A94BEA6FA1), [G:CC083B3D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CC083B3D-C9D6-4419-8156-900965670326), [G:889213DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-889213DA-A3AF-4020-89F0-1E5049AD26EC))
- Insert tab > Block Definition panel > Manage Attributes. Edits attribute definitions of blocks in the current drawing: edit, remove, reorder prompts. Dialog only.
- Block drop-down: every block definition that has attributes. Select Block: the dialog hides until you pick a block or press ESC; unsaved edits prompt a save first.
- List columns by default: Tag, Prompt, Default, Mode, Annotative (Settings picks columns). Mode letters: I Invisible, C Constant, V Verify, P Preset, L Lock Location, M Multiple Lines.
- Counts shown: Blocks Found in Drawing; Blocks Found in Current Space.
- Sync: pushes the current attribute properties to ALL references of the block. It never changes values already stored in references.
- Move Up / Move Down: list order = prompt order. Not available for constant attributes (Mode C).
- Edit or double-click: Edit Attribute dialog. Apply saves and keeps the dialog open.
- Remove: deletes the attribute from the definition, and from all references if Apply Changes to Existing References is on. Unavailable when the block has only one attribute; at least one must stay. To drop all, redefine the block ([G:F351FDBB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F351FDBB-2731-40C1-A186-1B1F47779E32)).

### Block Attribute Settings (BATTMAN > Settings) ([G:87154B11](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-87154B11-45B7-4B7A-A75E-BAF827D06E6A), [G:889213DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-889213DA-A3AF-4020-89F0-1E5049AD26EC))
- Display in List: pick columns (Tag always on); Select All; Clear All.
- Emphasize Duplicate Tags: duplicates show red; double-click to rename.
- Apply Changes to Existing References: ON (the default) = edits update every existing reference; OFF = only new insertions. Sync applies at once and temporarily overrides this option.

### Edit Attribute dialog (BATTMAN > Edit) ([G:16555B43](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-16555B43-D4FA-4C8E-BDF5-4256E9166A6F))
- Shows Block Name. Tabs: Attribute (Mode: Invisible, Constant, Verify, Preset, Lock Location, Multiple Lines; Data: Tag, Prompt, Default); Text Options (Text Style, Justification, Height, Rotation, Annotative, Backwards, Upside Down, Width Factor, Oblique Angle, Boundary Width); Properties (Layer, Linetype, Color, Lineweight, Plot Style).
- Auto Preview Changes: redraws at once; clearing it is slightly faster; unavailable when Apply Changes to Existing References is off.
- Lineweight changes do not show if LWDISPLAY is off. The Plot Style list is unavailable when the drawing uses color-dependent plot styles.

### Changing definitions: effect on references ([G:F351FDBB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F351FDBB-2731-40C1-A186-1B1F47779E32), [G:889213DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-889213DA-A3AF-4020-89F0-1E5049AD26EC))
- Changing a tag, prompt or default never changes values already entered in references (renaming tag Cost to Unit Cost leaves a stored 19.99 alone).
- Also changeable: modes (visibility, constant or variable, multiline, verify, position lock); text display (alignment, style, height, rotation, multiline width, annotative); layer, color, lineweight, linetype; prompt order.
- Apply scope: all existing references in the current drawing (default) or new insertions only. If not applied now, sync later with Sync or ATTSYNC.
- Run REGEN to see a removed attribute vanish from references, and to refresh constant attributes and nested attributed blocks.
- The Block Editor Properties palette can change a selected attribute definition, but not the prompt order or the apply scope.
- [AUTO] ATTSYNC (Home tab > Block panel > Synchronize Attributes): at the prompt enter `name` then the block name; or `?` to list blocks, then `name`; or press ENTER and pick a block. Error if the block does not exist or has no attributes. Also use it after a block is redefined ([G:889213DA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-889213DA-A3AF-4020-89F0-1E5049AD26EC)).

### BATTORDER (Attribute Order dialog) [GUI] ([G:9226D2B0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9226D2B0-C30A-4E10-A497-71444EAB7B40), [G:CC083B3D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CC083B3D-C9D6-4419-8156-900965670326))
- In the Block Editor: right-click an attribute > Attribute Order. Lists the definitions in the current block; select one, Move Up or Move Down, repeat.

### Editing values in block references
- [GUI] EATTEDIT, Enhanced Attribute Editor ([G:414DC467](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-414DC467-291B-4A52-A70D-1165CDEA8B39), [G:ECF7FC17](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-ECF7FC17-BCD7-437F-A7FE-796C61E767BF)): Home tab > Block panel > Edit Single Attribute, or double-click the block ([G:C054DDB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C054DDB8-1A63-47F7-8BDC-01EE6880792D)). Edits one reference, not the definition. Fields: Block, Tag, Select Block (dialog hides while you pick), Apply (writes and stays open; changes applied before a later Cancel are kept), OK.
  - Attribute tab: tag, prompt, value per attribute; only the VALUE can change. Multiline values: the ellipsis button opens the in-place editor (ATTIPE sets the toolbar). Right-click > Insert Field.
  - Text Options tab: Text Style, Justification, Height, Rotation, Annotative, Backwards, Upside Down, Width Factor, Oblique Angle, Boundary Width. Backwards, Upside Down and Oblique Angle are not available for multiline attributes; Boundary Width is multiline only.
  - Properties tab: Layer, Linetype, Color, Lineweight, Plot Style.
- [GUI] ATTEDIT, Edit Attributes dialog ([G:520405D3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-520405D3-C7BB-4E20-A15B-CFD665483868), [G:30770160](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-30770160-5E57-4ACC-B7AB-D00AF3D8D9D0)): values of one block only. Lists only the FIRST 15 attributes; Previous and Next page by eight. Values on locked layers cannot be edited. Multiline values open the in-place editor; right-click > Insert Field.
- [AUTO] -ATTEDIT is the command-line form for position, height, style and other properties; its prompts are not on the page ([G:520405D3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-520405D3-C7BB-4E20-A15B-CFD665483868)).
- Other ways ([G:C054DDB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C054DDB8-1A63-47F7-8BDC-01EE6880792D)): Ctrl + double-click an attribute edits it in place (if it carries a hyperlink, this opens the web page instead); the Properties palette edits values. Grips move attributes; on multiline attributes grips resize the width.

## 14.12 Attribute extraction (ATTEXT, DATAEXTRACTION)

### Choosing a route ([G:BA68DD22](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BA68DD22-A3CD-4538-90A9-6101C33BC963), [G:A1103600](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1103600-54CB-4FF8-8A62-EF237C890A09))
- ATTEXT writes attribute data to a text file (CDF, SDF) or a DXF subset (DXX) for a database or parts list. Extraction does not change the drawing.
- The Data Extraction wizard (DATAEXTRACTION) picks drawings, blocks and properties, and writes an AutoCAD table, an external file, or both. Its settings save to a .dxex file for reuse.
- Both are dialog driven in these pages. (inference) For unattended schedules, reading attributes through COM or AutoLISP avoids both dialogs.

### ATTEXT [GUI] ([G:07C3A8A9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-07C3A8A9-3D8C-4CAF-AF4E-624E5776FC0C), [G:05716CD3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-05716CD3-053D-4BBC-9E7C-B57EC920247B))
- Type `attext`: the Attribute Extraction dialog opens. A dialog-free form is not described in these pages; test before scripting.
- File format: Comma Delimited File (CDF), Space Delimited File (SDF), or DXF Format Extract File (DXX).
- Select Objects (dialog closes; Number Found shows the count). Template File (CDF and SDF only; default extension .txt). Output File (.txt appended for CDF and SDF, .dxx for DXF).
- CDF: one record per block reference that has at least one tag matching the template; commas between fields; character fields in single quotes. Example: `'DESK', 120.0, 49.5, 'ACME INDUST.', '51-793W', 379.95` ([G:A1103600](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1103600-54CB-4FF8-8A62-EF237C890A09)).
- SDF: same records, fixed-width fields, no separators or string delimiters.
- DXX: a DXF subset with only block reference, attribute and end-of-sequence objects. Needs no template.

### ATTEXT template file ([G:A1103600](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1103600-54CB-4FF8-8A62-EF237C890A09), [G:919FB556](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-919FB556-8988-4239-8490-88D3BA6E7574))
- Plain ASCII (Notepad works), saved with a .txt extension. One line per output field; output follows template order.
- Line = FIELDNAME, one SPACE (never Tab), then a code: `Cwww000` for character or `Nwwwddd` for numeric; www = 3-digit total width, ddd = 3-digit decimal places. Character fields ignore the last three digits.
- Numeric width includes the decimal point: 249.95 needs `N006002`.
- BL: fields: BL:NAME (C, block name); BL:LEVEL (N, nesting level); BL:X, BL:Y, BL:Z (N, insertion point); BL:NUMBER (N, block counter, same for MINSERT); BL:HANDLE (C); BL:LAYER (C, insertion layer); BL:ORIENT (N, rotation); BL:XSCALE, BL:YSCALE, BL:ZSCALE (N); BL:XEXTRUDE, BL:YEXTRUDE, BL:ZEXTRUDE (N, extrusion direction).
- At least ONE attribute tag line is required (`TAG Nwwwddd` or `TAG Cwww000`). The tag lines decide which blocks are written. A block missing a listed tag gets blanks (character) or zeros (numeric).
- No comments. Each field only once. Press Enter at the end of every line, the last one too. The output file name must differ from the template name.
- Delimiter overrides: `C:QUOTE c` (string delimiter) and `C:DELIM c` (field delimiter); the first non-blank character after the name is used, example `C:QUOTE "`. The quote character must not occur in character fields; the field delimiter must not occur in numeric fields.
- Sample template:
```
BL:NAME C008000
BL:X N007001
BL:Y N007001
SUPPLIER C016000
MODEL C009000
PRICE N009002
```
- Nesting: a block inserted in the drawing is BL:LEVEL 1; one nested inside it is 2. Nested coordinates, scales, extrusion and rotation are reported in world coordinates. A nested reference that cannot be described by two scale factors and one rotation (for example rotated in 3D) reports zero scale and rotation.
- Too narrow a field truncates the data and prints `** Field overflow in record <record number>`.
- The wizard page calls a .BLK file an "attribute extraction template" ([G:D1433C93](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1433C93-0E7F-46D0-8D05-78DF3626B146)); the template page says .txt ([G:919FB556](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-919FB556-8988-4239-8490-88D3BA6E7574)). Whether these are the same is not stated.

### DATAEXTRACTION wizard [GUI] ([G:D1433C93](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1433C93-0E7F-46D0-8D05-78DF3626B146))
Pages in order: Begin, Define Data Source, Select Objects, Select Properties, Refine Data, Choose Output, Table Style, Finish. No command-line or script switches are given; every option is a dialog control.
- Begin: Create a New Data Extraction (saves a .dxex; can start from a BLK, DXE or DXEX file); Use a Previous Extraction as a Template (DXE, DXEX or BLK; pages are pre-filled); Edit an Existing Data Extraction (DXEX only; DXE and BLK cannot be edited, only used to seed a new DXEX).
- Define Data Source: Drawings/Sheet Set (Add Folder, Add Drawings); Include Current Drawing; Select Objects in the Current Drawing (Select Objects button hides the wizard). Checked list items are extracted. Folder right-click (Add Folder folders only): Edit Folder Settings, Remove, Check All, Uncheck All, Invert Selection.
- Additional Settings (Settings button) ([G:8DA270FB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8DA270FB-7914-4FB5-B017-14826CEFF5D3)): Extract Objects from Blocks (nested); Extract Objects from Xrefs; Include Xrefs in Block Counts; Extract From = Objects in Model Space, or All Objects in Drawing (model, paper and drawing info; ON by default).
- Add Folder Options ([G:CA5F5FFF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA5F5FFF-546A-497F-9814-4BAB9F12C87B)): folder path; "Automatically include new drawings added to the folder" (on = live folder, shows the New Drawings Found dialog, [G:3CDBEFE2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3CDBEFE2-4360-48D1-8218-2DEB087C2C42); off = static); Include Subfolders; wild-card filter on drawing names (* and ?; the page reads "Valid characters are * ? ." so a period may also be meant).
- Select Objects: Object, Display Name (right-click > Edit Display Name), Type, Preview. Display: All Object Types (default), Blocks Only, Non-Blocks Only, Blocks with Attributes Only (dynamic blocks listed if they have actions or parameters), Objects Currently In-Use Only.
- Select Properties: Property, Display Name, Category. Category filter: 3D Visualization, Attribute (user attributes), Drawing, Dynamic Block, General (color, layer and so on), Geometry, Misc, Pattern, Table, Text.
- Refine Data: Count and Name columns show by default. Combine Identical Rows (Count = sum of merged objects); Show Count Column; Show Name Column; Link External Data; Sort Columns Options; Full Preview. Column right-click: Sort Ascending / Descending, Rename, Hide, Show Hidden Columns, Set Column Data Format, Insert Formula Column (placed right of the selected column), Edit / Remove Formula Column, Combine Record Mode (numeric, needs Combine Identical Rows), Insert Totals Footer (Sum, Max, Min, Average; numeric only), Filter Options, Reset Filter, Reset All Filters, Copy to Clipboard.
- Choose Output: Insert Data Extraction Table into Drawing (insertion point asked at Finish) and/or Output Data to External File: XLSX, CSV, MDB or TXT (tab-separated). Max 255 columns to XLSX and MDB.
- Table Style (only with table output): Use Table in Table Style for Label Rows (needs a style with a template table; data goes between top label rows and bottom rows); or Manually Setup Table: title (not overwritten on update; needs a title row, STANDARD has one), Title / Header / Data cell styles, Use Property Names as Additional Column Headers.
- Finish writes the output; a table asks for its insertion point.

### Wizard sub-dialogs (all from Refine Data)
- Insert / Edit Formula Column ([G:5DED24ED](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5DED24ED-6611-45CC-B4AB-CF5C975A3610), [G:E38072AB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E38072AB-2B08-4B3A-9049-077F90AD0EEA)): unique Column Name; Formula with QUICKCALC and CAL functions and + - * /; must pass Validate before insertion; existing formula columns are not listed and cannot be inputs.
- Filter ([G:7B660C5C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B660C5C-18E4-4B41-A7DB-568675DD8BA8)): over 50 variants by data type. Numeric: Greater than, Equal To, Between and others. Text: Equal To, Not Equal To, Contains, Begins With.
- Link External Data ([G:A2AA87E9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A2AA87E9-95E2-4C85-920A-96E8A06EB47F)): pick an Excel data link (or open the Data Link Manager); match a Drawing Data Column to an External Data Column; Check Match passes when the key is unique in the sheet and at least one drawing value matches; Case Sensitive; Ignore Prefix and Suffix White Space; pick the external columns to add; Use Top Row of External Data as Column Names (else Column 1, Column 2 ...).
- Set Cell Format ([G:4114DCA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4114DCA3-F9F0-4CE4-899E-B3043822E7CA)): same fields as Table Cell Format. Additional Format ([G:F38368FC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F38368FC-B7EB-47DD-9D2C-7D7D6E03A56D)): Conversion Factor (default 1), Additional Text, separators, zero suppression.
- Sort Columns ([G:882C3E46](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-882C3E46-34EF-47CF-A919-6E3472900F1E)): sort order list; Add, Remove, Move Up, Move Down.
- Outdated Table ([G:E2D6EA1D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E2D6EA1D-13D1-4CDA-81BE-6BB57D31B11D)): Update, Update All, Skip Update, Skip All Updates. (inference) Can stall an unattended run.

### Extraction output rules ([G:BA68DD22](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BA68DD22-A3CD-4538-90A9-6101C33BC963))
- A table output lands in the CURRENT space (model or paper) on the CURRENT layer. Updating re-extracts and replaces the data rows; title and header rows stay.
- Right-click menus for editing and updating tables need Options > User Preferences > Shortcut Menus in Drawing Area.
- Period, comma and pound sign (#) written to an Excel or Access file are replaced by their Unicode representation.

## 14.13 Sheet sets

### Concepts ([G:34D889BC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-34D889BC-19AD-4CD1-ADB1-F359D9B515FB), [G:577D8EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-577D8EA0-85F2-4829-B4F9-8CAD6F7AAACC))
- Sheet = one layout of a drawing file, imported into a sheet set as a numbered sheet. Sheet set = a named, ordered collection of sheets from several drawings; managed, published, transmitted and archived as a unit.
- The sheet set data file is a .dst. Each time it opens, the current DST is copied to a backup with the same name and extension .DS$ in the same folder.
- The first sheet set you create makes the default folder "AutoCAD Sheet Sets" under My Documents ([G:577D8EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-577D8EA0-85F2-4829-B4F9-8CAD6F7AAACC)).
- Sheet List tab: sheets grouped into subsets (nestable; often by discipline or status). Sheet Views tab: views grouped into view categories. Model Views tab: resource folders, their drawings and named model-space views.
- Always change sheets through the open sheet set in Sheet Set Manager so all sheet set data update ([G:34D889BC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-34D889BC-19AD-4CD1-ADB1-F359D9B515FB), [G:CE884F9A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CE884F9A-F8A7-403A-9427-4F39D552CA6F)).
- Each drawing caches the DST data it uses (custom properties and so on). After the DST changes, open and save each sheet, or use Resave All Sheets; other users must close the set's drawings first ([G:577D8EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-577D8EA0-85F2-4829-B4F9-8CAD6F7AAACC)).

### Commands and variables ([G:970CBE0D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-970CBE0D-9232-4900-82F7-F32A4A1273AE), [G:9751A902](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9751A902-27DC-4BCD-8D3D-585478B213DD))
- [AUTO] Command names: SHEETSET (opens the Sheet Set Manager palette), NEWSHEETSET (Create Sheet Set wizard), OPENSHEETSET (Open Sheet Set file dialog), SHEETSETHIDE, ARCHIVE. All lead to palettes or dialogs.
- Variables listed with no meanings: SSFOUND, SSLOCATE, SSMAUTOOPEN, SSMOPENMODE, SSMPOLLTIME, SSMSHEETSTATUS, SSMSTATE, STARTMODE, UPDATETHUMBNAIL.
- Sheet Set Manager is not fully functional while a command is active, when no drawing is open, or when the set is locked by another user (lock icon; hover shows who) ([G:9751A902](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9751A902-27DC-4BCD-8D3D-585478B213DD)). (inference) Sheet set work needs an open drawing; these pages give no command-line route into the manager.

### Prepare a sheet set ([G:1CF98963](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1CF98963-5C9E-4D61-9F6D-5B7CC7D013D4), [G:F39C5BFC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F39C5BFC-07F4-4798-A59A-58D2CCD9AE5D))
1. Consolidate the drawing files in a few folders.
2. Use ONE named layout per drawing (recommended). Several users can then work at once; a drawing that holds several sheets can be edited by only one user at a time.
3. Layout names must NOT contain a `#` character (stated as required when importing existing drawings).
4. Make a sheet creation template (DWT) for new sheets; name it in Sheet Set Properties or Subset Properties.
5. Make a page setup overrides file (DWT) with the plot page setups. It can apply one page setup to every sheet, overriding each drawing's own.

### Create and open [GUI]
- NEWSHEETSET (Application menu > New > Sheet Set) runs the Create Sheet Set wizard ([G:F39C5BFC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F39C5BFC-07F4-4798-A59A-58D2CCD9AE5D)): An Example Sheet Set (structure and defaults from a listed or browsed set; option to create folders from the subset storage paths) or Existing Drawings (pick folders; subsets can copy the folder structure; layouts can be imported automatically). Then the DST location, name, description, Finish. New cloud sheet sets and sheets are stored on Forma Data Management.
- OPENSHEETSET ([G:4E657527](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E657527-3A9C-4581-B47D-D1D9039221A4)): Open Sheet Set dialog > select the DST > Open. Cloud: Start tab > Autodesk Projects > hub > synchronized project > DST.
- The palette: View tab > Palettes panel > Sheet Set Manager. Its sheet set control lists open sets, Recent, New Sheet Set and Open ([G:9751A902](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9751A902-27DC-4BCD-8D3D-585478B213DD)).

### New sheets ([G:13B4B8C1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-13B4B8C1-F57B-4EA7-8F7A-385436775D6C), [G:27A63B35](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-27A63B35-9CE6-4CC9-A185-6D036AC8F7B3))
- Sheet List tab > right-click the set, a subset or a sheet > New Sheet. Creates a new DWG with a layout of the same name.
- Fields: Number (Autodesk recommends leaving it blank at creation); Sheet Title (matches the layout tab name); File Name (default number + title); Folder Path (default from Subset or Sheet Set Properties); Sheet Template (same defaults); Open in Drawing Editor.
- By default the drawing name and layout name = number + title. You can drop the number from the file name, but it stays in the layout name.
- Views later placed on the sheet attach their source drawings as xrefs to the sheet drawing.

### Import existing layouts as sheets [GUI] ([G:AD4F3361](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AD4F3361-BB2B-4905-8E02-527E5FAA3576), [G:C5C75E82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C5C75E82-96FC-49FA-A680-69C433BEEB20))
- Right-click the set, a subset or a sheet > Import Layout As Sheet > Browse for Drawings (Shift or Ctrl for several) > check layouts > Import Checked. Option: Prefix Sheet Titles with File Name.
- RULE: a layout that already belongs to a sheet set cannot be imported; copy its drawing first ([G:C5C75E82](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C5C75E82-96FC-49FA-A680-69C433BEEB20)).
- Shortcut from the open drawing: right-click a layout tab > Import Layout As Sheet, or drag the tab onto the Sheet List tab.
- Then right-click the new sheet > Rename & Renumber to set its number and title.

### Subsets ([G:10BEBF33](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-10BEBF33-017B-4AD2-AFD2-03313DC43F5F), [G:DD4C1645](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DD4C1645-044E-464D-A927-608C724FCE4F))
- Right-click the set or a subset > New Subset > Subset Properties > Subset Name > OK. Drag subsets anywhere, even under other subsets.
- Subset Properties: Subset Name (also its folder name when "Create Folders Relative to Parent Subset Storage Location" is selected); Create Folder Hierarchy (folders come from New Sheet Location, not from the name); Publish Sheets in Subset; New Sheet Location; Sheet Creation Template (printed syntax `layoutname [folderpath]filename.dwt`; the page does not say if the brackets are literal); Prompt for Template.
- Remove a subset: first remove or move its sheets, then right-click > Remove Subset. Same rule for view categories ([G:02901896](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02901896-9749-48B0-A366-7F4BF9A82478)).

### Sheet Set Properties ([G:19C80CB1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-19C80CB1-EC22-4EBF-9483-5CB78253DA62), [G:657F4DCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-657F4DCD-2388-437F-9612-00565F8F4489))
- Right-click the top node > Properties. Click a field to see its description.
- Name; Sheet Set Data File (DST path); Description.
- Model View: folders holding the set's drawings.
- Label Block for Views; Callout Blocks: the DWT or DWG that holds them.
- Page Setup Overrides File: DWT with the override page setups.
- Project Control: Project Number, Project Name, Project Phase, Project Milestone.
- Sheet Custom Properties; Sheet Set Custom Properties; Edit Custom Properties button.
- Sheet Storage Location: folder for new sheets. Sheet Creation Template: DWG or DWT for new sheets. Prompt for Template: ask each time or not.
- Select Layout as Sheet Template dialog ([G:A29A0F18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A29A0F18-630D-4235-BC6A-3694F9C98B54)): Drawing Template File Name, then pick the layout used for new sheets. (inference from its related link) It is the picker behind Sheet Creation Template.

### Custom properties ([G:683DA7B0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-683DA7B0-5FE6-4EFB-AE8A-C80B0D3D0EBC), [G:D04D740D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D04D740D-72FC-4C68-97AA-B208E69300FE), [G:B5F63864](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B5F63864-9B80-469E-B6B9-AA8EC117AD46))
- Right-click the set > Properties > Edit Custom Properties > Add: Name, Default Value, Owner = Sheet Set or Sheet. Delete removes one.
- Sheet set properties are per project (contract number, release date); sheet properties are per sheet (designer name).
- (inference) Title blocks show them through CurrentSheetCustom and CurrentSheetSetCustom fields placed in attributes (14.10).

### Sheet properties ([G:3B0D3681](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3B0D3681-07BB-4B51-98CE-EB3C996771EB), [G:DD52C358](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DD52C358-1852-4A1A-9D1D-77FEB489A105), [G:657F4DCD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-657F4DCD-2388-437F-9612-00565F8F4489))
- Right-click a sheet > Properties: sheet title, number, include for publish, custom properties; editable.
- Expected Layout = where the sheet was saved. Found Layout = where it was found. If they differ, edit Expected Layout to re-associate the sheet.
- Several sheets: Ctrl-click > right-click > Selected Sheets Properties. Only shared properties are shown, and only those with matching values are editable (description, include for publish, revision number, custom properties).

### Rename and renumber [GUI] ([G:A85CD2A2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A85CD2A2-BE10-4334-8A16-E1167941C135), [G:C913F771](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C913F771-5ADF-4184-A4AA-4C724FC4F6F0))
- Sheet: Number, Sheet Title, Layout Name, File Name, Folder Path. Checkboxes: Rename Layout to match Sheet Title, Prefix with Sheet Number; Rename Drawing File to match Sheet Title, Prefix with Sheet Number. Next and Previous walk through a series.
- View (Sheet Views tab): Number, View Title, Previous, Next.

### Sheet List tab ([G:5FF4D109](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5FF4D109-B454-4695-97FE-4F644F424E4D))
- Toolbar: Publish to DWF; Publish to DWFx; Publish to PDF; Publish to Plotter (selected sheets to the DEFAULT plotter, no questions); Publish Using Page Setup Override; Publish menu; Sheet Selections; Details and Preview panes.
- Shortcut menu (varies by set, subset or sheet): Archive; Close Sheet Set; eTransmit; Edit Subset and Sheet Publish Settings (Publish Sheets dialog, [G:4AB6E25C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4AB6E25C-163C-472B-B21D-A2F58D11FE59)); Import Layout as Sheet; Include Plot Stamp; Include for Publish; Insert Sheet List Table; Manage Page Setups; New Sheet; New Subset; Open; Open Read-Only; Plot Stamp Settings; Properties; Publish; Publish in Reverse Order; Publish Sheets in Subset ("Do Not Publish Sheets" suspends the whole subset); Publish to DWF; Publish to Plotter; Remove Subset; Rename & Renumber; Remove Sheet; Save Sheet Selection; Sheet Set Publish Options; Transmittal Setups; Resave All Sheets.
- Resave All Sheets opens and saves every DWG in the set and updates the DST. Drawings in an older DWG format keep that format. On a network, close any set drawings other users have open first.

### Remove, open, reassociate, recover
- Remove Sheet only disassociates the sheet; the DWG file and layout are NOT deleted ([G:20E629A4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-20E629A4-D8F5-4C6D-8B2E-758AB967295F)).
- Open: double-click, or select and Open; Open Read-Only cannot save under the original name ([G:CE884F9A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CE884F9A-F8A7-403A-9427-4F39D552CA6F), [G:5FF4D109](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5FF4D109-B454-4695-97FE-4F644F424E4D)).
- Moved sheet drawing ([G:006210FA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-006210FA-8B05-4CA0-89CD-5CFF957DC019)): Sheet Properties > click the Expected Layout path > browse to the new location. The Details area shows Expected Location and Found Location. Alternative: open the sheet, Remove Sheet, save, then Import Layout As Sheet again.
- Model Views tab Refresh re-reads the DST, all resource folders and expanded drawings ([G:216C475D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-216C475D-7CC7-4B13-BBCA-AAC91BC34B22)).
- Recover a DST ([G:A1E60616](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A1E60616-BEA6-436D-9329-BB8207638728)): make sure nobody on the network is using the set; copy the DST to another name (recommended); rename the .DS$ backup to .DST. [AUTO] Plain file operations do this. Back up DST files like drawings.

### Sheet views and model views ([G:BFC36AD5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BFC36AD5-2136-45C0-BFA5-81328C2BBDC3), [G:D1FC29EA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1FC29EA-CEFD-4248-A750-73C0B104F24D), [G:216C475D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-216C475D-7CC7-4B13-BBCA-AAC91BC34B22))
- A sheet view = three coincident things: an xref or geometry in model space, a layout viewport on the sheet, and a named view in paper space.
- A model-space view from another drawing is attached as an xref with a RELATIVE path (make it absolute in the External References palette). Its layers show only in that sheet view.
- When a sheet view is placed, ALL layers of the current drawing, layer 0 included, are frozen in the new viewport (VP Freeze column of the Layer Properties Manager). [AUTO] Gotcha: the sheet's own geometry disappears inside that viewport.
- Remove a sheet view: delete the viewport; for a full cleanup also detach the xref and delete the named paper space view. Right after placing, UNDO is easiest.
- Add a view [GUI] ([G:D1FC29EA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1FC29EA-CEFD-4248-A750-73C0B104F24D)): open the sheet; Model Views tab > + beside a folder > + beside a drawing; right-click a named model space view (or a whole drawing) > Place On Sheet, or drag it onto the sheet; right-click to choose the scale; pick the insertion point.
- Place on Sheet does these steps by itself: prompts to place the view (right-click first to change the scale); attaches the model as an xref; makes a layout viewport; makes a sheet view matching it ([G:216C475D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-216C475D-7CC7-4B13-BBCA-AAC91BC34B22)).
- RULE: SAVE the drawing after creating a named model-space view, or it will not show on the Model Views tab; then click Refresh ([G:216C475D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-216C475D-7CC7-4B13-BBCA-AAC91BC34B22), [G:D1FC29EA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1FC29EA-CEFD-4248-A750-73C0B104F24D)).
- If a view label block is set in Sheet Set Properties, a view label with the view's data is placed automatically ([G:D1FC29EA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1FC29EA-CEFD-4248-A750-73C0B104F24D)).
- Model Views tab shortcut menu: Add New Location; Remove Location; eTransmit; Open; Open Read-Only; Place on Sheet; See Model Space Views; Tooltip Style; Preview/Details Pane; Expand; Collapse; Close ([G:216C475D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-216C475D-7CC7-4B13-BBCA-AAC91BC34B22)). Resource Drawing Locations dialog: Add and Delete folders ([G:7B3B9A08](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7B3B9A08-6616-4E6C-A081-9C407A95A823)).
- Sheet Views tab ([G:AD5F5927](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AD5F5927-8A3D-4D42-9D3C-32ECC89BB36F)): lists only views created in AutoCAD 2005 or later. Buttons: New View Category, View by Category, View by Sheet. Shortcut menu: Display (opens the drawing if needed), New View Category, Place Callout Block, Place View Label, Properties, Rename, Rename & Renumber, Set Category.
- View categories ([G:02901896](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-02901896-9749-48B0-A366-7F4BF9A82478), [G:10B2AC81](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-10B2AC81-03D8-462F-A4C2-B0A831D03E5D)): Sheet Views tab > View by Category > right-click the set > New View Category: Category Name; tick the callout blocks for this category; Add Blocks opens List of Blocks. Drag views between categories, or use Set Category.

### Label and callout blocks ([G:87F36464](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-87F36464-0801-44B9-BF33-7430E75B4C74), [G:9F18EC18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9F18EC18-8A20-4ACA-9725-1DE0DB98E7F7), [G:A3C50C44](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A3C50C44-E6DB-49C8-9661-FD76C9FEE4DB), [G:4A7BBC28](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4A7BBC28-E68B-4F9A-8801-969ABAE4C1EB), [G:F8117B11](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F8117B11-85CA-48EF-92B2-45E90A030820), [G:6957BD90](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6957BD90-830C-4339-9FEC-C7E2AF9A41B8))
- Label blocks label views as they are placed. Callout blocks point to other sheets (reference tags, detail keys, detail markers, building section keys). Both carry data from the referenced view or sheet.
- A custom label or callout block must live in a DWG or DWT named in Sheet Set Properties. It is placed later from the Sheet Views tab shortcut menu.
- To show view title, sheet number and the like, the placeholder FIELD must sit inside a block ATTRIBUTE, not in plain text. Build: attribute definition, placeholder field as its value, Preset on, a tag (14.10).
- Set ALL attribute definitions in your label and callout blocks to Preset, so placing them does not prompt.
- GOTCHA: the current layer must be UNLOCKED when you place a callout block with fields, or a view.
- Default label block: Sheet Views tab > right-click the set > Sheet Set Properties > Label Block For Views > [...] > Select Block dialog.
- Callout block list: Sheet Set Properties > Callout Blocks > [...] > List of Blocks: Add (opens Select Block), Delete, Preview.
- Select Block dialog: Enter the Drawing File Name (a DWG or DWT); "Select the Drawing File as a Block" (whole file becomes the block) or "Choose Blocks in the Drawing File"; Preview.
- Place: Sheet Views tab > right-click the view > Place Callout Block > pick the insertion point. The block fills in the view data by itself.

### Sheet list table ([G:AF75182F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-AF75182F-F6B0-4AEC-BBC1-5B82483160CA), [G:73C378CD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-73C378CD-72A2-454C-8263-DE18E1B8B24A), [G:D86D0B53](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D86D0B53-A79F-4847-8226-7A801D308C6C), [G:B3A89FC1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B3A89FC1-6649-4D6A-9454-8B84B44D911A), [G:1B3204E2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B3204E2-A259-4200-BAAD-41A845766044))
- Right-click the set name, a subset, or several names > Insert Sheet List Table. Unavailable when the Model tab is active or the current layout is not a sheet of the current set. Usually placed on the title sheet.
- Settings: Table Style Name (Browse opens the Table Style dialog); preview; Include Subsets as Headers in Output (subset names split the table into sections).
- Table Data tab: Title Text; column list (top to bottom = left to right); Data Type per column; Heading Text; Add (adds a Sheet Number column); Remove; Move Up; Move Down. A column removed by mistake: Add one and change its data type.
- Subsets and Sheets tab: pick what is listed; "Populate From Sheet Selection" sets the checks from a saved selection.
- Later: right-click a table cell > Edit Sheet List Table Settings (same settings).
- When a sheet is later added to a subset, you are prompted to update the table automatically.

### Sheet selections ([G:82BA4F2A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-82BA4F2A-C749-414D-961C-ED023494FE4A), [G:FAD9BFE6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FAD9BFE6-EBEF-4542-9F22-322E4DEB8746), [G:A005A660](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A005A660-7FAD-4569-945B-224E375083FD), [G:19448B6F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-19448B6F-56E7-4C5C-BE41-E36D89459CC6), [G:6F5ACF66](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F5ACF66-2DC4-4DAB-B36D-1B544955557A), [G:D127F66A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D127F66A-2798-4CB3-8618-E9639DC3724C), [G:695C8C79](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-695C8C79-5C89-4F87-B4A4-3A374C91CA1A))
- A named group of sheets, so repeat publish, transmit or archive runs use exactly the same sheets.
- Create: select sheets and subsets (Ctrl or Shift) > Sheet Selections button > Create > name. Or right-click > Save Sheet Selection.
- Restore: Sheet Selections button > click the name; it becomes active for publishing and transmitting.
- Rename or Delete: Sheet Selections > Manage.
- RULE: a selection cannot be edited in place. Restore it, Ctrl-click to add or remove items, delete the old name under Manage, then Create it again.

### Networked and cloud sheet sets ([G:577D8EA0](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-577D8EA0-85F2-4829-B4F9-8CAD6F7AAACC))
- Every team member needs access to the DST and to the DWT files tied to the set. Shared DWTs keep page setups standard.
- If users reach the same files through different drive letters, each is prompted to resave the set with their own letters. Map the same drives for everyone.
- Status icon beside the set name while the DST is open: green dot = your session has the DST locked; red dot = another member's session has it; yellow dot = a special state such as Read-Only. A multi-user icon = several people working.
- Sheet status seen by all: available for editing; locked; missing or found in an unexpected location.
- After a network fault or a crash, a FALSE lock icon can show. Click the sheet for details; click Refresh on the Sheet List or Model Views tab.

### Connected Sheet Set Manager (AutoCAD 2026.1.1 and later) ([G:E6B489F6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E6B489F6-C969-4EC8-8961-51DB5BDBD89C))
- Sheet Set Manager for Web was REMOVED in AutoCAD 2026 Update 1.1 and later. The Connected Sheet Set Manager handles local, network and cloud sets in the normal palette with all its features. The Classic Sheet Set Manager is AutoCAD and Civil 3D 2026.1 and earlier.
- It opens a cloud DST directly from Forma Data Management, not from Desktop Connector synced folders, and supports multi-user co-editing of a cloud DST.
- Publishing: all classic publish features using local plot services; cloud files are downloaded and PDFs uploaded through Desktop Connector; output to local or network drives and physical devices works.
- It supports sheet and model views with callout blocks. It has no automatic sheet numbering (Web SSM had it).
- A co-edit icon beside the set name shows who is editing (hover). Users can join from the Connected SSM, Web SSM, the desktop or the web app.
- Opening locks the DST for that user; others can still join the session. After the first user leaves, the DST can still show as locked by that user until ALL users close it.
- Open errors: "Locked for Edit by <user>" = view-only; even a lock you placed yourself blocks editing, so unlock before opening. "No Editing Permission for This Sheet Set" = view-only; ask a project admin. File Size Exceeded = a DST over 6.3 MB will NOT open; [AUTO] set SSMOPENMODE to 1 to open it locally, with no co-editing.
- Save and unlock: right-click > Close Sheet Set as the last user saves and unlocks at once. Quitting AutoCAD saves and unlocks within 1 to 15 minutes. Closing only the palette does NOT close, save or unlock. After 60 to 90 minutes with no edits the session auto-closes, saves and unlocks; the DST goes view-only with a Reload button.

### Project-aware support files ([G:E6B489F6](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E6B489F6-C969-4EC8-8961-51DB5BDBD89C), [G:EB31E0D9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EB31E0D9-8F63-4556-9086-C30389CD9AA1))
- The Support File Location property was removed. From AutoCAD 2026.1.1 it is replaced by AutoCAD Connected Support Files. Without them, the Connected SSM uses the support files of the current AutoCAD user profile.
- Only Project Administrators in Forma Data Management can set them up: open a drawing from the Autodesk project > Options > Files tab > Set Up (no Set Up button = already configured) > Project Settings > Support Files Search Paths: add the folders holding the DWTs named in the "Sheet creation template" and "Page setup overrides file" properties. Template Settings node holds other template settings.

## 14.14 Publishing a drawing set

### Page setups, sheet creation template, overrides ([G:FBE7EA6E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FBE7EA6E-4E78-4FDB-B758-45D5F6A395F2))
- Page setups hold the plot and publish settings. The sheet creation template is the DWT whose page setups are used for all new sheets of a set.
- The page setup overrides file is a second DWT whose page setups can override each sheet's own. It is named in Sheet Set Properties.
- Publish choices for a set: each drawing's own page setups; the overrides for all drawings; or DWF/DWFx.
- [AUTO] PUBLISHCOLLATE: with page setup overrides, controls whether plotting a sheet set can be interrupted by other plot jobs. Values are not given here.

### PUBLISH dialog [GUI] ([G:55DEBF19](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-55DEBF19-ABC4-461F-9C48-956D7FFF703B), [G:0CA2EE37](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0CA2EE37-8E8E-486F-8527-187A5C1F403D))
- Output tab > Publish panel > Publish. Assembles sheets for paper, or for single- or multi-sheet DWF, DWFx or PDF. The list saves as a DSD (Drawing Set Descriptions) file (Save List).
- RULE: a layout must be INITIALIZED to publish, meaning its page setup paper size is anything but 0 x 0. Click each layout tab you want in the set ([G:0CA2EE37](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0CA2EE37-8E8E-486F-8527-187A5C1F403D)). (inference) In a scripted drawing, a layout never made current may not be initialized; make each layout current once before publishing.
- An uninitialized model sheet shows "Uninitialized" in the Status column. It can still plot if you pick an override page setup in its Page Setups drop-down.
- Right-click options: Include Layouts When Adding Sheets; Include Model When Adding Sheets.
- Add Sheets (or drag drawings in from the desktop): every layout of a chosen drawing becomes its own sheet. Remove Sheets; Remove All. Remove unwanted sheets yourself.
- Move Sheet Up / Move Sheet Down: sheets are viewed and plotted in list order. Rename Sheet.
- Page setup per sheet from the Page Setup list, or select sheets > Change Page Setup. "Import" pulls page setups from another drawing or template. Model space page setups apply only to model sheets; paper space page setups only to layouts.
- Copy Selected Sheets names the copy "<name>-Copy(n)" (example Plumbing-Copy(1)), so one sheet can publish with several page setups.

### Publishing from Sheet Set Manager [GUI] ([G:1484D4DE](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1484D4DE-BE0C-4FF6-BDA1-6F020DA3A177), [G:1D4AE986](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1D4AE986-169F-4783-A6B2-18F2C924A1B9), [G:5FF4D109](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5FF4D109-B454-4695-97FE-4F644F424E4D))
- Autodesk calls this more efficient than the Publish dialog. Select the set, a subset or sheets > Publish button (upper right) > Publish to DWF, DWFx, PDF or Plotter.
- Publish to Plotter sends the selected sheets to the DEFAULT plotter with no further questions. Publish Using Page Setup Override uses one chosen override for all sheets instead of each drawing's page setup.
- Per sheet or subset: Include for Publish; Publish Sheets in Subset; Publish in Reverse Order.
- Background publishing shows an animated plotter icon at the right of the status bar; right-click it for the job. [AUTO] For speed, turn it OFF: OPTIONS > Plot and Publish tab > Publish Controls > clear Background Publishing. (inference) With it on, the publish runs in the background, so a script waiting for the output file must not assume the command has finished writing it.
- RULE: metadata (sheet and sheet set properties, block attributes, dynamic block properties, custom object properties) is included only when you PUBLISH to DWF/DWFx/PDF; it is NOT available when you PLOT to DWF/DWFx ([G:1D4AE986](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1D4AE986-169F-4783-A6B2-18F2C924A1B9)).
- DWF and DWFx publish options are saved with the sheet set and become the defaults for later publishes ([G:1D4AE986](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1D4AE986-169F-4783-A6B2-18F2C924A1B9)).

### Sheet Set DWF publish options ([G:68387C52](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-68387C52-31C5-4073-B903-6B46621C664C))
- Publish button > Sheet Set DWF Publish Options. Click an item to switch it to Include: Layer information; Sheet set information (description, custom properties); Sheet information (title, number, description, set, subset, sheet custom properties); Block information (then pick or create a Block Template file that says which blocks, properties and attributes go in).
- Always published whatever you set: sheet name, sheet size, author, creator, creation time, modification time.

### Sheet Set PDF publish options ([G:41A77B2E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-41A77B2E-0853-4706-8743-44CE60EFA9E0))
- Publish button > Sheet Set PDF Publish Options. OK saves the settings to the sheet set.
- Location (output folder). Multi-sheet File: checked = one multi-page PDF; cleared = one PDF per sheet.
- Quality: vector and raster resolution. For printing from a viewer, match the printer's resolution; for screen viewing, pick a value above 2400 dpi.
- Include Layer Information (layers can be toggled in the PDF). Include Hyperlinks (keeps hyperlinks; sheet set links become hyperlinks). Create Bookmarks for Sheets and Views.
- Font Handling: Capture Fonts Used in Drawing (embeds fonts) or Convert All Text to Geometry (best visual fidelity). With neither, the viewer substitutes fonts it does not support.

### AUTOPUBLISH and Auto Publish Settings [GUI] ([G:0A0DDEBA](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0A0DDEBA-5FF8-4ACF-A58F-589456535A53), [G:58713703](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-58713703-312C-4B12-A3A1-82DC2D19545B))
- OPTIONS > Plot and Publish tab > Automatic Publish Settings. Publishes DWF, DWFx or PDF on save or close, or when AUTOPUBLISH runs.
- Publish on: Save; Close; Prompt on Save; Prompt on Close. (inference) The Prompt choices open a prompt that would stall an unattended run.
- Location: Drawing folder; "DWF and PDF" (subfolder of the drawing folder); Previously selected location; [...] for a new one.
- Include: model, layouts, or both. File Format: DWF, DWFx or PDF. Type: single-sheet or multi-sheet.
- Layer Information (not published for 3D DWF). Merge Control: Overwrite (top line hides bottom) or Merge (colors blend). Password Protection.
- Block Information must be Include before a Block Template File (DXEX) can be set. BLK and DXE files from AutoCAD 2024 and earlier cannot be edited but can seed a new DXEX.
- Names only: commands PUBLISH, AUTOPUBLISH; variables AUTODWFPUBLISH, AUTOMATICPUB, PUBLISHHATCH.

## 14.15 eTransmit and Archive

### What a package holds ([G:C32FA153](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C32FA153-88D6-41D9-B868-0DFF59509CD2), [G:0C34FD41](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0C34FD41-C06A-4CEE-B5C6-D783A1774062))
- Added automatically: the root DWG and attached xrefs; raster images attached to the root or xrefs or used in materials; attached DGN, DWF, DWFx and PDF files; the .fmp font mapping file; .ctb and .stb plot style tables; .pc3 plotter configurations.
- NOT added automatically: .shx; .ttf; .pfa and .pfb; .pat hatch patterns; .lin linetype files; .pmp plotter model parameters; OLE objects linked to files.
- The same page's intro says packages include "font files". The setup page has Include Fonts (TTF and SHX) ([G:9A2F96E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A2F96E5-34D1-4504-A5F3-54BCD410041D)). (inference) Fonts go in only with Include Fonts on. Custom .pat and .lin files must be sent by hand.
- Files referenced by URL are never included ([G:A329E883](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A329E883-840A-4584-A59A-06468DEB6137), [G:BA3634A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BA3634A5-1C41-458F-80C3-347B7CF664F6)).
- Package type: folder or ZIP only. eTransmit no longer makes self-extracting EXE files and no longer puts passwords on ZIP files ([G:0C34FD41](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0C34FD41-C06A-4CEE-B5C6-D783A1774062)). Password a ZIP afterward with an external tool ([G:4E32143C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E32143C-AA81-4A4E-9191-B32C4AA259EE)).
- ZIP files from DWGCONVERT, ETRANSMIT and ARCHIVE are UTF-8 ZIPs; names with extended characters show wrong in tools without UTF-8 support; use 7-Zip ([G:9A2F96E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A2F96E5-34D1-4504-A5F3-54BCD410041D)).
- eTransmit can save to older DWG formats and can transmit sheet sets. Drawings with objects over the legacy large-object limits are listed in the "Conversion Error Encountered" dialog and are NOT converted ([G:0C34FD41](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0C34FD41-C06A-4CEE-B5C6-D783A1774062)).

### ETRANSMIT, Create Transmittal dialog [GUI] ([G:847CA0F2](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-847CA0F2-CFD9-48BB-B069-DFD628F0C8CE), [G:A329E883](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A329E883-840A-4584-A59A-06468DEB6137), [G:6F96DA08](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F96DA08-0E95-4472-8794-2AB6D7E4EDC2), [G:976114A1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-976114A1-9DBB-478B-9A45-DCAA17BC4EA0), [G:C628034E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C628034E-E124-48D8-B924-5912B5A7E5AB), [G:00266258](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-00266258-F8BF-4160-8A54-BC76D4534B22))
- Application menu > Publish > eTransmit. These pages document only the dialog.
- Tabs: Sheets (sheet set packages), Files Tree, Files Table. Checked = included; right-click the file area to check or clear all. Add File adds extras. On Files Tree, expand a drawing to see its dependent files.
- Files Tree groups: Sheet Drawings, Sheet Set Files, Current Drawing, User Added Files.
- A greyed-out sheet is an xref of another sheet in the package and is included automatically.
- Enter Notes: written into the report. [AUTO] Default notes come from etransmit.txt in a folder on the Support File Search Path.
- Select a Transmittal Setup (default STANDARD); Transmittal Setups button; View Report (your notes plus distribution notes, for example where the recipient must copy SHX fonts). OK builds the package.
- From a sheet set ([G:21C65B7B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-21C65B7B-6E50-46D6-B218-54FF88C17944)): right-click the set, a subset or a sheet > eTransmit. Sheets from the same DWG show indented and are checked together, because sending a sheet sends its ENTIRE drawing file, every layout in it.

### Transmittal setups ([G:6D4A2392](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6D4A2392-A115-4A13-A1FB-AB402E46C64E), [G:74663E53](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-74663E53-5F2F-4082-B193-D58806E9A53A), [G:BCAA967D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BCAA967D-127E-432E-BD45-30FB4C3D2834))
- Transmittal Setups dialog: New (New Transmittal Setup Name; Based On), Rename, Modify, Delete, Import. Import in a sheet set context asks for a DST, then the Import Transmittal Setups dialog: check setups, Overwrite with Current Storage Location, Import Checked.
- Save a reusable setup: Transmittal Setups > New > name and Based On > Continue > set options in Modify Transmittal Setup > Transmittal Setup Description > OK. Later runs just pick it ([G:74663E53](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-74663E53-5F2F-4082-B193-D58806E9A53A), [G:21C65B7B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-21C65B7B-6E50-46D6-B218-54FF88C17944)).
- (inference) Setups used from a sheet set are stored in the sheet set data, since they can be imported from a DST.

### Modify Transmittal Setup: the settings [GUI] ([G:9A2F96E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A2F96E5-34D1-4504-A5F3-54BCD410041D))
- Transmittal Package Type: Folder (uncompressed files in a new or existing folder) or Zip.
- File Format: every drawing in the package is saved to the chosen DWG format.
- Maintain Visual Fidelity for Annotative Objects: annotative objects are decomposed; each scale representation goes on its own layer named from the original layer plus a number.
- Transmittal File Folder: if unchanged, the package goes in the folder of the first drawing; for a sheet set, in the folder holding the DST.
- Transmittal File Name (not for Folder type): Prompt for a File Name (file dialog); Overwrite if Necessary; Increment File Name if Necessary. [AUTO] Use Overwrite or Increment for unattended runs.
- Path Options: Use Organized Folder Structure (copies the source folder structure under a root; makes Fonts, PlotCfgs and SheetSets folders as needed; the DST goes in the root; absolute paths outside the root tree become No Path); Source Root Folder (root for relative xref paths; also holds the DST); Place All Files in One Folder; Keep Files and Folders As Is (AutoCAD 2007 behavior; easiest to install elsewhere). Organized and Keep As Is are unavailable for Internet locations. Autodesk usually recommends the organized structure for sheet sets ([G:21C65B7B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-21C65B7B-6E50-46D6-B218-54FF88C17944)).
- Actions: Send E-mail with Transmittal (opens the default mail program); Set Default Plotter to 'None'; Bind External References (Bind, or Insert = like detach and insert); Purge Drawings (silent, no report of what was removed).
- Include: Include Fonts (TTF and SHX; TrueType fonts are proprietary, so clear it if the recipient may not own them; missing fonts become the FONTALT font); Include Textures from Materials; Include Files from Data Links; Include Photometric Web Files; Include Unloaded File References (unloaded xrefs, images, underlays).

### ARCHIVE [GUI] ([G:BA3634A5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BA3634A5-1C41-458F-80C3-347B7CF664F6), [G:5DBC2E1E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5DBC2E1E-532E-48F5-B921-26DAC8362D85), [G:1D4AE986](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1D4AE986-169F-4783-A6B2-18F2C924A1B9))
- Packages the current sheet set for storage. Same as a transmittal set, except you name a folder and nothing is sent ([G:1D4AE986](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1D4AE986-169F-4783-A6B2-18F2C924A1B9)).
- The sheet set must be open in Sheet Set Manager. Right-click the top node > Archive, or type ARCHIVE; the page documents only the dialog, so expect one.
- Tabs: Sheets, Files Tree, Files Table. Checked = included. Make sure the files are not open in any application. Add a File button. URL-referenced files are not included.
- Enter Notes: goes into the report. [AUTO] Default notes template archive.txt in a folder on the Support File Search Path. View Report; Save As saves an extra copy. A report file is ALWAYS included.
- Modify Archive Setup ([G:5DBC2E1E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5DBC2E1E-532E-48F5-B921-26DAC8362D85)): Archive Package Type Folder or Zip (UTF-8 ZIP); File Format; Archive File Folder (blank = the folder holding the DST); Archive File Name (Prompt for a File Name / Overwrite if Necessary / Increment File Name if Necessary; not for Folder type); Path Options as for transmittals.
- Archive Actions: only Set Default Plotter to 'None' and Purge Drawings (silent). No Send E-mail, no Bind External References, no annotative fidelity option, no description field.
- Archive Include: Include Fonts (this page says "TXT and SHX"; the transmittal page says "TTF and SHX"); Include Files from Data Links; Include Textures from Materials; Include Photometric Web Files; Include Unloaded File References; Include Sheet Set Data and Files (DST, label block DWGs, callout block DWGs, DWT files).

## 14.16 Drawing compare

### Which tool ([G:2D69E78D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D69E78D-5C82-464F-B864-CD29D5720EB9), [G:94951E33](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-94951E33-4FDB-460E-9732-9186CCFDA53F), [G:8F5A2620](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8F5A2620-D59B-42B4-AA20-E0DD6701FB91))
- Two SEPARATE drawings: DWG Compare (COMPARE).
- Two versions of the SAME drawing: Activity Insights version compare.
- An xref against its latest saved version, or against another file: Xref Compare (XCOMPARE).

### COMPARE (DWG Compare) ([G:2D69E78D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D69E78D-5C82-464F-B864-CD29D5720EB9), [G:744D8A49](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-744D8A49-D582-4C06-80B1-6B0313E92CA2), [G:87D8D56F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-87D8D56F-8CF4-421A-9421-480F028BFD6D))
- [GUI] View tab or Collaborate tab > Compare panel > DWG Compare; or Application menu > Drawing Utilities > DWG Compare. COMPARE opens the "Select a Drawing to Compare" file dialog. With no drawing open, the DWG Compare dialog takes a base and a reference drawing and shows the result in the base drawing.
- [AUTO] -COMPARE is listed as a command; its prompts are not in these pages ([G:A03EE801](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A03EE801-F912-4D89-8532-454FD6571A08)). (inference) It is the command-line form to probe for scripted compares.
- The result is drawn in the current drawing. Default colors: gray = in both; red = only in the comparison drawing; green = only in the current drawing. Colors are changeable in Settings.
- Differences are grouped by closeness into change sets, each ringed by a revision cloud. Arrow buttons zoom to each set.
- While a compare is active, edits to the current drawing are picked up live. Edits to the comparison drawing show only after it is saved.
- Layers that are off or frozen in the current drawing are NOT part of the result.
- Toolbar: Settings panel (bulbs "Not in Current Drawing", "Only in Current Drawing", "No Differences"; Draw Order, default current drawing on top; Revision Clouds bulb, Rectangular or Polygonal, Size slider = offset from the change set; cloud arc size is automatic from the drawing extents; Text and Hatch filter bulbs); On/Off; Previous / Next; Import Objects (COMPAREIMPORT); Export Snapshot (COMPAREEXPORT); Exit (COMPARECLOSE).
- COMPAREIMPORT: select objects in the comparison drawing, Enter. Only objects not already in the current drawing are selectable; imported objects turn gray.
- COMPAREEXPORT: "Export a Comparison Snapshot" dialog > Continue > save. Default name `Compare_<Drawing1> vs <Drawing2>.dwg`. The snapshot holds two blocks, one per drawing, and opens with a "DWG Compare Snapshot" toolbar.
- Commands ([G:A03EE801](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A03EE801-F912-4D89-8532-454FD6571A08)): COMPARE, -COMPARE, COMPARECLOSE, COMPAREEXPORT, COMPAREIMPORT, COMPAREINFO, XCOMPARE, XCOMPARECLOSE, XCOMPARERCNEXT, XCOMPARERCPREV.
- Variables (names only, no values given): COMPARECOLOR1, COMPARECOLOR2, COMPARECOLORCOMMON, COMPAREFRONT, COMPAREHATCH, COMPAREPROPS, COMPARERCMARGIN, COMPARERCSHAPE, COMPARESHOW1, COMPARESHOW2, COMPARESHOWCOMMON, COMPARESHOWRC, COMPARETEXT, COMPARETOLERANCE, XCOMPAREBAKPATH, XCOMPAREBAKSIZE, XCOMPARECOLORMODE, XCOMPAREENABLE.

### Compare limits ([G:2D69E78D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-2D69E78D-5C82-464F-B864-CD29D5720EB9), [G:3D918CC7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3D918CC7-4FB7-4951-8F04-C2434DFD04A2))
- Model space only. A drawing saved in a layout is switched to the Model tab.
- DWG files only. Not supported: OLE objects, cameras, geographic data, Map 3D GIS objects, non-DWG underlays, images, coordination models, point clouds.
- A comparison result cannot be compared with a third drawing.
- ByBlock or ByLayer property changes inside nested blocks are not detected.
- Compare graphics show only in the 2D Wireframe visual style. Revision clouds cannot enclose changes in a 3D isometric view.
- Import works like copy and paste, not like the toolsets, so toolset objects can lose custom behavior.
- AutoCAD MEP toolset: importing an MEP object that is attached to another MEP object also imports the attached object (example: a duct fitting brings in its duct) ([G:3D918CC7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3D918CC7-4FB7-4951-8F04-C2434DFD04A2)).
- Other toolsets on the same page: Architecture (a door or window brings in its wall); Electrical (wires lose color and size, wire numbers lose their links); Mechanical (a symbol brings its object; a standard part does not update the BOM unless its part reference is also selected).

### XCOMPARE (Xref Compare) ([G:84E4CED9](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-84E4CED9-A52E-4F36-8D30-EB660DDC1086), [G:94951E33](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-94951E33-4FDB-460E-9732-9186CCFDA53F))
- [GUI] External References palette > right-click a DWG reference > Compare > Recent Changes (against the latest saved version of the xref file) or Select File (pick another DWG).
- Toolbar mirrors DWG Compare: Settings, On/Off bulb, Previous / Next, Exit Compare (XCOMPARECLOSE). Default draw order: host drawing objects on top.
- XCOMPARERCNEXT and XCOMPARERCPREV are listed by name only. (inference) They are the next and previous revision-cloud steps.

### Activity Insights version compare ([G:8F5A2620](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8F5A2620-D59B-42B4-AA20-E0DD6701FB91))
- Needs a subscription AND an account with a supported cloud provider: Forma Data Management, Dropbox, Box, Google Drive or OneDrive.
- [AUTO] ACTIVITYINSIGHTSOPEN (View tab > History panel > Activity Insights). In the palette: filter, pick a version, Compare; the Version Compare toolbar opens.
- Colors: red = only in the previous version; green = only in the current drawing; gray = both. Off or frozen layers are excluded. Same toolbar functions and snapshot naming as DWG Compare.

## 14.17 Hyperlinks, digital signatures, load security, passwords

### HYPERLINK [GUI] ([G:DD13DBA3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-DD13DBA3-8221-4485-A9E6-DF7C94DF240E), [G:BAE1EAFC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BAE1EAFC-85D8-474D-BC21-C37252C3A062), [G:F94EDDB4](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F94EDDB4-F7A2-425B-85A3-797FF2A5EAF5))
- Attaches hyperlinks to graphical objects through the Insert Hyperlink dialog; Edit Hyperlink adds a Remove Link button.
- Text to Display = the link's description. Link To tabs:
  - Existing File or Web Page: file or URL (local, network, internet); Recent Files; Browsed Pages; Inserted Links; File; Web Page; Target = Select Place in Document (a named view or layout, restored when the link runs); Path.
  - View of This Drawing: tree of named views in the current drawing.
  - E-mail Address: address and subject; running the link opens a new message in the default mail program.
- [AUTO] Use Relative Path for Hyperlink: on = the path is stored relative to HYPERLINKBASE, or to the current drawing path when HYPERLINKBASE is empty; off = the full path is stored.
- Convert DWG Hyperlinks to DWF: DWG links become DWF links when the drawing is published or plotted to DWF.
- Field hyperlinks always store absolute paths ([G:14933ABC](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-14933ABC-8574-430C-8CBE-467BB6B3CCB8)).

### Load security: SECURITYOPTIONS [GUI] ([G:C108E81C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C108E81C-7A06-477C-A5F8-10AA2FDEB050), [G:EDBB6671](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB6671-94A9-4B0C-A6F2-BC3EFBBBCBC2))
- [AUTO] Security Level = SECURELOAD: 2 = High (load only from trusted locations; files elsewhere are ignored); 1 = Medium (trusted locations, plus a WARNING when a load comes from elsewhere); 0 = Off (no warning, legacy, not recommended).
- [AUTO] Trusted Locations = TRUSTEDPATHS: folders in the Support File Search Path allowed to load and run executables.
- [AUTO] LEGACYCODESEARCH: include or exclude the Start In folder and the current drawing folder when searching for executables.
- [AUTO] ACADLSPASDOC: acad.lsp loads into every drawing, or only the first drawing of a session.
- Options can be greyed out by a CAD manager lock; all are greyed out when AutoCAD starts with /safemode.
- Code-carrying file types: ARX, CRX, CUI, CUIx, DBX, DLL, DVB, EXE, FAS, HDI, JS, LSP, MNL, PGP, RX, SCR, VLX ([G:EDBB6671](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB6671-94A9-4B0C-A6F2-BC3EFBBBCBC2)).
- (inference) With SECURELOAD = 1, a script that loads LISP or other code from an untrusted folder can stop at a warning; with 2 the load is skipped without notice. Put script and LISP folders in TRUSTEDPATHS before unattended runs.
- CUI, CUIx, DVB, JS, PGP and SCR files can hold code but cannot be digitally signed yet; Autodesk recommends read-only folders controlled by an administrator ([G:EDBB6671](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB6671-94A9-4B0C-A6F2-BC3EFBBBCBC2)).
- AutoLISP signing: use the AcSignApply utility (CA-issued or self-signed certificate). To revise a signed LSP: edit it, delete the signature block at the END of the file, sign again ([G:EDBB6671](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-EDBB6671-94A9-4B0C-A6F2-BC3EFBBBCBC2)).

### Digital signatures ([G:3D3F2AB3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3D3F2AB3-E3B0-40D7-9A47-4BC77AAE451E), [G:5F3F9549](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F3F9549-C425-4B77-BA3C-B9B95D6C6F39), [G:60026975](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60026975-0A2F-4E7B-9F00-5FB6363F5AF4), [G:0497EF29](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0497EF29-5E9D-465A-9732-BDFED9911AF2), [G:959C0A42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-959C0A42-D07D-4909-9582-7DC424144DD7), [G:504C12C5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-504C12C5-F17B-4B02-AC9B-5F7560261997))
- Names: commands DIGITALSIGN, SECURITYOPTIONS, SIGVALIDATE, SAVEAS; variable SIGWARN ([G:504C12C5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-504C12C5-F17B-4B02-AC9B-5F7560261997)).
- A signature identifies the signer and shows whether the file changed after signing. It needs a certificate from a certificate authority, or a self-signed one made with a utility.
- Signable with DIGITALSIGN: DWG and DWT in AutoCAD 2000 and later formats; DWS (not in LT) ([G:3D3F2AB3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3D3F2AB3-E3B0-40D7-9A47-4BC77AAE451E)). The batch tool's search also finds EXE and ZIP files made by eTransmit ([G:959C0A42](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-959C0A42-D07D-4909-9582-7DC424144DD7)).
- A signature turns invalid when the file is modified after signing, is corrupted in transit or during signing, or the certificate is revoked. Renaming does NOT invalidate it.
- To change a signed drawing and sign again: WBLOCK the entire drawing, save it under a NEW file name, then sign that ([G:3D3F2AB3](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-3D3F2AB3-E3B0-40D7-9A47-4BC77AAE451E)).
- One drawing [GUI] ([G:5F3F9549](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F3F9549-C425-4B77-BA3C-B9B95D6C6F39)): Options > System tab > Security Options, or Save As > Tools > Digital Signatures; check "Attach Digital Signature After Saving Drawing"; optional time stamp and comment.
- Many drawings [GUI] ([G:60026975](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-60026975-0A2F-4E7B-9F00-5FB6363F5AF4), [G:5F3F9549](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F3F9549-C425-4B77-BA3C-B9B95D6C6F39)): Windows Start > Autodesk <product> > Attach Digital Signatures (a separate program, not an in-session command). Files to Be Signed (Add Files, Search Folders, Remove, Clear List); Select a Digital ID; Get Time Stamp From (default "No Time Stamp"); Comment; Sign Files. A read-only file asks Yes / No / Cancel, with "Use the Same Answer for All Read-only Files in This Batch". "Signing Complete" shows the count.
- A digital ID obtained with Medium or High security shows a message EVERY time a file is signed, which blocks unattended signing ([G:5F3F9549](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5F3F9549-C425-4B77-BA3C-B9B95D6C6F39)).
- DIGITALSIGN with no valid digital ID opens the Digital Signatures dialog telling you to get one ([G:0497EF29](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-0497EF29-5E9D-465A-9732-BDFED9911AF2)).
- [AUTO] SIGWARN = Options > Open and Save tab > Display Digital Signature Information: on = status shows when opening any validly signed file; off = only when the signature is invalid ([G:6723C3D7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6723C3D7-DABA-46CD-BA69-7D7EBC66CD69)).
- Time stamps ([G:F9623564](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-F9623564-396F-428C-BEC9-1CC782BFFA77), [G:C953AE46](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C953AE46-AA46-48AA-A022-043C3D721929)): the server list is timesrvr.txt in the program install folder, one line per server: `Description (server_name)`, example `National Institute of Standards and Technology (time.nist.gov)`. [AUTO] The ADSKSIGTIMESRVR ENVIRONMENT variable (not a system variable) points to another list file.
- Check a signature ([G:6723C3D7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6723C3D7-DABA-46CD-BA69-7D7EBC66CD69)): status bar Validate Digital Signatures icon > View Base Signature; for xrefs, View Xref Drawings > View Xref Signature. File Explorer: Properties > Digital Signatures tab.
- Root certificate: get it from the signer, then Internet Options > Content > Certificates > Import ([G:4DBE2E22](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4DBE2E22-A70F-4F85-9EC9-E93C5024E9C3)). A digital ID comes from a certificate vendor ([G:48C60161](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-48C60161-41F2-4670-B421-82F531888D5C)).

### Passwords and drawing properties ([G:4E32143C](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4E32143C-AA81-4A4E-9191-B32C4AA259EE), [G:A9BEAC48](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A9BEAC48-DE55-4FDB-9822-B493B42BD35D))
- Since AutoCAD 2016-based products, a password can NOT be added to a drawing file.
- Alternatives named by Autodesk: put a password on the PDF output; password a ZIP with a secure external utility; third-party encryption (AES 256-bit or equal); network or cloud provider permissions. Strength guidance: AES 256-bit; RSA 2048-bit minimum for general security, 4096-bit for internet transactions.
- Title, author, subject and keywords can be read in File Explorer > Properties, except where an old drawing password encrypted them ([G:A9BEAC48](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A9BEAC48-DE55-4FDB-9822-B493B42BD35D)).

## 14.18 Notes for DXF writers (ezdxf)
The source pages do not cover ezdxf or the DXF file format. Below are the facts from this section that a DXF or DWG writer has to respect. How a writer stores them is (inference); check the ezdxf documentation for the exact API before writing code.
- MTEXT content: use the inline codes in 14.4 (`\P` paragraph, `\H..;` height, `\S..^..;` stack, `{ }` grouping up to 8 deep) and `\U+xxxx` symbols ([G:7D8BB40F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D8BB40F-5C4E-4AE5-BD75-9ED7112E5967), [G:518E1A9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-518E1A9D-398C-4A8A-AC32-2D85590CDBE1)). (inference) These are stored as-is in the mtext string.
- TEXT content: `%%c`, `%%d`, `%%p`, `%%%`, `%%u`, `%%o`, `%%k` work in single-line text with SHX fonts ([G:968CBC1D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-968CBC1D-BA99-4519-ABDD-88419EB2BF92)). Not all work in mtext; use `\U+xxxx` there.
- Height to write: for non-annotative text, model-space height = plotted height x scale factor (1/4" text at 1/4" = 1'-0" is 12; 3/16" is 9) ([G:D8A24528](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D8A24528-80F9-4B57-8802-CFA1608B9AEE), [G:4DE922FB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4DE922FB-79FC-44E0-AC05-313DB3CCE333)). Paper-space text is full size ([G:4F448A62](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F448A62-A99E-4AB5-AE50-9EAAC0485283)).
- Fonts: a missing SHX font can stop AutoCAD at a font prompt when the file opens ([G:928DF015](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-928DF015-1E04-4CC2-AF1B-0037548DFBAE)). (inference) Use fonts the pages name as defaults (simplex.shx, txt.shx) or ship the font with the file.
- Attribute tags: no spaces, and AutoCAD uppercases them ([G:92A7CE9D](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-92A7CE9D-2E1C-415E-A1BF-5CB35D5E2D38)). Keep tags unique ([G:67A2DDAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-67A2DDAD-2217-412F-8AEF-D4495192F45B)). Single-line values max 255 characters ([G:67A2DDAD](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-67A2DDAD-2217-412F-8AEF-D4495192F45B)). (inference) The order of attribute definitions inside the block is the likely prompt order; check with BATTMAN.
- Title block sheet data: contextual fields work in a block only inside an attribute ([G:D32A29E7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D32A29E7-7B98-4ADB-BF32-5CC24DBCC8C3)). (inference) A DXF writer does not evaluate fields; AutoCAD refreshes them on save or REGEN ([G:1B6DD22B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327)). If AutoCAD will not touch the file, write the literal text.
- Table formulas are plain text starting with `=` ([G:505EF5BB](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-505EF5BB-5347-43DA-91A6-03141A9134C8)). Cell styles Title, Header and Data exist in every table style ([G:8C5C592E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-8C5C592E-C0CC-456C-86A6-E34B67A026C7)).
- Layouts: a layout needs a non-zero paper size in its page setup before it can be published ([G:55DEBF19](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-55DEBF19-ABC4-461F-9C48-956D7FFF703B)). Layout names must not contain `#` for sheet sets, and one layout per drawing is recommended ([G:1CF98963](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1CF98963-5C9E-4D61-9F6D-5B7CC7D013D4)).
- Packaging: eTransmit does not add .shx, .ttf, .pat or .lin files automatically ([G:C32FA153](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C32FA153-88D6-41D9-B868-0DFF59509CD2)). Ship custom ones with the drawings.

## 14.19 Conflicts between source pages
Items 1 to 9 and 14 to 16 were re-checked against the source pages; both statements are really there. The rest were noted on a first reading and not re-checked.
1. Imported text size limit: 256 KB ([G:66848B18](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-66848B18-9590-4E68-839E-A4DFD28301D2), [G:A72A6B7A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-A72A6B7A-3175-4C98-AC74-642B9262B1F6)) vs 32 KB ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)). Staying under 32 KB satisfies both.
2. MLEADER option keys: straight = `o` `l` `s` ([G:CD496790](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CD496790-85A6-46CA-83F3-B113A6BF4F3D)); spline = `o` `l` `t` `p` ([G:4F382D40](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-4F382D40-A4C8-4C3E-B416-E7D53C92558E)). One page likely skips a step. Probe the live prompts.
3. List punctuation after a number or letter: colon allowed ([G:FB9F3708](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-FB9F3708-0A8C-4F77-B6EC-908B8B9BF7F5), [G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)) vs comma allowed ([G:25708CA1](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-25708CA1-3985-411C-9CD4-20C294B13119), [G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)). Period, close parenthesis, >, ] and } are on every list.
4. Mtext line spacing: "baseline of one line to the baseline of the next" ([G:E4DC3A14](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E4DC3A14-3F0A-46AE-9503-6BBEE8DAF916)) vs "bottom of the upper line to the top of the lower line" ([G:5B8A1DB8](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5B8A1DB8-8AF0-44EC-BA48-A8E06118D3DC)).
5. Fonts in eTransmit: the page intro says packages include font files, but its table lists .shx and .ttf as not added automatically ([G:C32FA153](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-C32FA153-88D6-41D9-B868-0DFF59509CD2)). The setup has an Include Fonts option ([G:9A2F96E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A2F96E5-34D1-4504-A5F3-54BCD410041D)).
6. Include Fonts types: "TTF and SHX" (transmittal, [G:9A2F96E5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-9A2F96E5-34D1-4504-A5F3-54BCD410041D)) vs "TXT and SHX" (archive, [G:5DBC2E1E](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-5DBC2E1E-532E-48F5-B921-26DAC8362D85)). (inference) TXT is likely a typo for TTF.
7. Invalid field display: the Field dialog says an invalid value shows `----` ([G:1B6DD22B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327)); the fields page says `----` = no value and `####` = invalid ([G:B9ADAE6A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B9ADAE6A-2DD1-4C44-B126-CF3FF92EBC68)). Unreachable sheet set fields show `####` ([G:1B6DD22B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-1B6DD22B-10D1-44ED-BAA2-E6D79FE52327)).
8. The invalid-field example names CurrentSheetName ([G:B9ADAE6A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-B9ADAE6A-2DD1-4C44-B126-CF3FF92EBC68)); the contextual field list has CurrentSheetTitle, not CurrentSheetName ([G:D32A29E7](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D32A29E7-7B98-4ADB-BF32-5CC24DBCC8C3)).
9. Field conversion example: "inches to millimeters, enter 0.03937" ([G:D1EA1BF5](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1EA1BF5-6442-47EF-82F5-D6849A07906E)). Arithmetic says that factor converts mm to inches.
10. Multileader text height: "Text Height" ([G:16C41557](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-16C41557-2036-4912-9FE8-7DDE6A8AC5AE)) vs "Paper Height", the height shown in paper space ([G:BBF1A961](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BBF1A961-C7CA-4949-A4E4-9D4B03F6E60F)).
11. Landing option name: "Automatically include landing" ([G:E42AB914](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-E42AB914-B055-4D67-9A97-88D708006105)) vs "Landing - Keep Horizontal" ([G:BBF1A961](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-BBF1A961-C7CA-4949-A4E4-9D4B03F6E60F)).
12. Table formula example `=count(a1:m500)` is described as "rows 1 through 100" ([G:15E0C775](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-15E0C775-6E60-456D-B5C7-4726E0C586B7)).
13. ATTEXT template extension: .txt ([G:919FB556](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-919FB556-8988-4239-8490-88D3BA6E7574)) vs a .BLK "attribute extraction template" in the Data Extraction wizard ([G:D1433C93](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-D1433C93-0E7F-46D0-8D05-78DF3626B146)).
14. Overline code: the table prints `\0` (zero) but the example uses `\O` (letter) ([G:7D8BB40F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D8BB40F-5C4E-4AE5-BD75-9ED7112E5967)).
15. `\A1;1\S1/2` has no closing semicolon after the stack ([G:7D8BB40F](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-7D8BB40F-5C4E-4AE5-BD75-9ED7112E5967)); the worked examples close it, `\S1/2;` ([G:6F59DA4A](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6F59DA4A-A790-4316-A79C-2CCE723A30CA)).
16. Annotative object without the current scale: "not displayed" ([G:6D4A620B](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-6D4A620B-30AB-4593-B168-F9FF084017C6)) vs "not displayed, or the text appears unchanged" ([G:590DE319](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-590DE319-FD23-45FE-8430-D3EF4AB989D2)).
17. Data extraction folder filter: "Valid characters are * ? ." ([G:CA5F5FFF](https://help.autodesk.com/view/ACD/2027/ENU/?guid=GUID-CA5F5FFF-546A-497F-9814-4BAB9F12C87B)); unclear whether the period is a wildcard.
