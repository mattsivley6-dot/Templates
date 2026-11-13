# 13 - Automation II: Scripts, Customization, Plug-ins, .NET and the Core Console

Adapted from Autodesk AutoCAD 2027 help (help.autodesk.com), (c) Autodesk, Inc., under CC BY-NC-SA 3.0. Condensed, reorganized and annotated with test notes. See [LICENSE.md](LICENSE.md).

Legend: (G:...) links open the Autodesk AutoCAD 2027 developer help page cited. [AUTO] = can be driven from the command line, a script, AutoLISP, COM or .NET; [GUI] = needs a dialog or palette; (inference) = not stated by Autodesk.

Summary
- How to drive AutoCAD MEP 2027 from text: .scr scripts, startup switches, acad.pgp, startup LISP files, support and trusted paths, and the SECURELOAD rules that decide which code may load.
- How to package and load code: plug-in bundles (PackageContents.xml), digital signing, NETLOAD, demand-load registry keys.
- The AutoCAD .NET API for 2027 (.NET 10, project file, references, CommandMethod, transactions, document locking, plotting and publishing), changes by release, ObjectARX readme facts.
- PC3/PMP plotter configuration; what the official sources say (and do not say) about the Core Console; the AutoCAD MEP managed API help.

Contents
- 13.1 Command scripts (.scr) and startup switches
- 13.2 Command lookup, aliases, external commands (acad.pgp)
- 13.3 SECURELOAD, trusted paths, support paths, library search path
- 13.4 Startup code: acad.lsp, acaddoc.lsp, MNL, S::STARTUP, acad.rx, acad.dvb
- 13.5 Plug-in bundles and PackageContents.xml
- 13.6 Digital signing and loading signed files
- 13.7 Plotter configuration: PC3, PMP, paper sizes, ports, AutoSpool
- 13.8 .NET for AutoCAD 2027: framework, project file, references, compatibility
- 13.9 Loading .NET code: NETLOAD, demand loading, initialization attributes
- 13.10 .NET commands, transactions, document locking, command line, prompts, errors
- 13.11 Plotting and publishing from .NET; layouts, viewports, visual styles
- 13.12 Migration by release; ObjectARX readme facts (fiberless, acedCommand)
- 13.13 Core Console: what these sources cover
- 13.14 AutoCAD MEP managed API; AecbPipeBaseMgd classes
- 13.15 Other programming interfaces at a glance

## 13.1 Command scripts (.scr) and startup switches

### Script file rules
- Plain ASCII text, extension .scr, one command or script call per line. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- Every space counts as Enter or Spacebar. You must know each command's exact prompt sequence. Prompts change between releases: re-test scripts after an upgrade. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- A line starting with `;` is a comment. The LAST line of the script must be blank. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- File names with spaces need double quotes: `open "my house"`. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- A script can run any Command-prompt command EXCEPT one that shows a dialog box. Use the hyphen form instead: `-INSERT`, not `INSERT`. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E)) [AUTO]
- Never use command aliases (acad.pgp) in a script. Use full command names. ([G:FE9AE544](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE9AE544-F537-4D3B-8F75-B76484513787), [G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E)) [AUTO]
- Script input assumes PICKADD = 1 and PICKAUTO = 0. You do not need to set them. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- Undo: the whole script undoes with one U, but every command still writes undo data, which slows long scripts. Speed up with `UNDO Control None` at the start; restore with `UNDO Control All` at the end (option names as printed; the exact prompt sequence is not shown). ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E)) [AUTO]
- Plotting several jobs with `-PLOT` on Windows: set BACKGROUNDPLOT to 0 BEFORE the script runs. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E)) [AUTO] The .NET plot pages say the same (13.11).
- Inside a script LAYER runs as the command-line LAYER (same as `-layer`). Doc example, one per line: `grid on` / `ltscale 3.0` / `layer set 0 color red 0` / blank line. The blank line ends LAYER. ([G:9F648910](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9F648910-2D8C-4AED-B796-FD977D52872E))
- TEXTEVAL gotcha: `-TEXT` reads TEXTEVAL only when it runs inside a script or AutoLISP and every prompt is answered there. With TEXTEVAL = 1, text that starts with `(` or `!` is evaluated as AutoLISP. ([G:F469D307](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F469D307-86E6-4081-A33B-CD9AD94A4C20)) [AUTO]
- Blank line = Enter, so a stray blank line repeats the last command (inference from the null-response rule in 13.2).

### SCRIPT and SCRIPTCALL [AUTO]
- SCRIPT: runs a script in the current session. If a script is already running, starting SCRIPT stops the active one. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- SCRIPTCALL: runs nested scripts as well as commands. ([G:95BB6824](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-95BB6824-0700-4019-9672-E6B502659E9E))
- These pages do not give the prompt strings of SCRIPT or SCRIPTCALL or say whether SCRIPT opens a file dialog. Not stated here.

### Startup switches for acad.exe [AUTO]
- Run a script at startup: `<executable_path> <drawing_name> /b <script_name>`. `/b` and the script name must be the LAST parameter. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55), [G:8675B657](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8675B657-8C15-4594-BDFB-644B66BD02D7))
- New drawing from a template, then the script: `<executable_path> /t MyTemplate /b setup`. Omit `/t` to use the default template. You can no longer name a new drawing this way; name it when you save. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55))
- Open to a named view: `/v <view_name>`. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55), [G:8675B657](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8675B657-8C15-4594-BDFB-644B66BD02D7))
- Extensions `.exe`, `.dwg`, `.dwt`, `.scr` are optional. Names with spaces need double quotes. If the script is not found, the program reports that it cannot open the file. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55))
- When the script ends, the program sits at the Command prompt; the session stays open. ([G:8675B657](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8675B657-8C15-4594-BDFB-644B66BD02D7)) (inference: end the script with QUIT to close; the page does not say so.)
- `/s "path1;path2"` replaces ALL support file search paths for that launch. Doc example: `/s "c:\AcadJobs;c:\AcadJobs\Support"`. ([G:348D791E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-348D791E-D621-444F-B059-C0C6F97AD69F))
- `/c <file>` starts with an alternate configuration (CFG) file. ([G:A694AB72](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A694AB72-7EB7-4560-B473-B480C378E457))
- Launch works from the Windows Run box or a Command Prompt. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55))
- Warning: VBA and AutoLISP files loaded at startup should test whether the process is visible (Visible property of the ActiveX Application object). If not visible, do not run them: the process may be doing background plotting or publishing. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55)) [AUTO]
- None of these pages mention accoreconsole.exe. Whether the Core Console takes the same switches is not stated here. See 13.13.

### Job-folder launch ([G:29FCFD3B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-29FCFD3B-8B5B-4609-A626-F5BD0A108F91))
- A shortcut whose working directory is a job folder makes that folder current at startup ONLY if REMEMBERFOLDERS = 0. [AUTO]
- Doc batch launcher idea: a small `acad.bat` on the PATH, run as `acad jobname`, that creates `\AcadJobs\Jobs\<jobname>` if it is missing, changes to that folder, then starts `acad.exe` from the install folder. The full listing is on the linked page; if you copy it, use plain quotes on the start line (inference).
- Entering `support` (no path) in the Support File Search Path adds the `support` folder under the current folder. Layout idea: `/AcadJobs/Job1/Support` for job-only blocks and files.

## 13.2 Command lookup, aliases, external commands (acad.pgp)

### What happens when a name is entered ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B)) [AUTO]
Commands can come from the prompt, the UI, a script, AutoLISP, ObjectARX or .NET. Lookup order:
1. Null response (Space or Enter) repeats the last command; HELP if none.
2. Built-in commands. If the name matches and is NOT prefixed with a period, the UNDEFINE list is checked; an undefined command keeps searching. (inference: a leading period, as in `.LINE`, always reaches the built-in.)
3. Device-driver commands, then display-driver commands.
4. External commands in acad.pgp. A match runs and the search ends.
5. Commands defined by AutoLISP, ObjectARX and .NET apps. Autoloaded commands load at this step.
6. System variable names: a match runs SETVAR with that variable.
7. Alias, AutoCorrect or synonym: the expanded name restarts the search at step 2.
8. Otherwise an illegal-command warning.
- A LISP `c:NAME` with the same name as a built-in does not override it unless the built-in is UNDEFINEd (inference from the order).
- Aliases are step 7, yet the alias page says aliases cannot be used in scripts ([G:FE9AE544](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE9AE544-F537-4D3B-8F75-B76484513787)). The pages do not explain the difference. Treat scripts as full-name only.

### Command aliases ([G:7BFFBEE9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7BFFBEE9-63F8-4C2B-A352-A8DCE1E8B4FC), [G:FE9AE544](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE9AE544-F537-4D3B-8F75-B76484513787), [G:D4CACED6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D4CACED6-DFBA-43C3-BC42-8D980AB3AE75))
- Syntax: `abbreviation,*command`. The asterisk is required. `;` starts a comment line.
- Hyphen forms work as alias targets: `-LA, *-LAYER`, `-CH, *-CHANGE`.
- File: `<user folder>\AppData\Roaming\Autodesk\<product name>\<release>\<language>\Support\acad.pgp`. Edit with Manage tab > Customization panel > Edit Aliases, or `ai_editcustfile` then `acad.pgp` (opens a text editor; would stall a script, inference).
- To replace an alias, do not edit the shipped line. Add a new line under User Defined Command Aliases at the bottom. The last definition loaded wins.
- Reload after editing: REINIT (Re-initialization dialog, tick PGP file, OK) [GUI], the RE-INIT system variable (Windows), or restart. [AUTO]
- The product also loads AutoCorrectUserDB.pgp and acadSynonymsGlobalDB.pgp. Do not edit them directly. AutoCorrect needs Input Search AutoCorrect on (INPUTSEARCHOPTIONS). ([G:FE9AE544](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE9AE544-F537-4D3B-8F75-B76484513787))

### External commands in acad.pgp (Windows AutoCAD only) ([G:4CE44766](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4CE44766-E856-47D4-93E6-D45A3EC6749B))
- Syntax: `command,[executable],bit flag[,[*]prompt[,return_code]]`.
- Bit flags (add): 0 start and wait; 1 do not wait; 2 run minimized; 4 run hidden; 8 put the argument string in quotes. 2 and 4 together: 2 wins. 2 or 4 WITHOUT 1 locks AutoCAD until the app ends.
- An executable string without `start` or `cmd` also holds AutoCAD until its window closes. `start` = separate process; `cmd /c` = run and close; `cmd /k` = run and keep the window.
- Prompt: the typed reply is appended to the executable string. A leading `*` lets the reply contain spaces (ends with Enter).
- Return code: 1 = load `$cmd.dxb` then delete it; 2 = make a block from `$cmd.dxb` named by the reply (name must be new).
- Doc examples: `RUN, cmd /c,0,*Batch file to run: ,` and `LISTSET,cmd /k SET,0`. From [G:2090E4E8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2090E4E8-9AE0-4E01-B5EB-0843A30EB0E9): `RUNAPP1, start c:\vbapps\app1, 0`.
- AutoLISP `startapp` also launches an external program; LISP has no control over it afterwards. ([G:2090E4E8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2090E4E8-9AE0-4E01-B5EB-0843A30EB0E9))
- Not stated whether the Core Console honors PGP external commands. Do not assume. ([G:4CE44766](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4CE44766-E856-47D4-93E6-D45A3EC6749B))

## 13.3 SECURELOAD, trusted paths, support paths, library search path

### Secure mode
- Default SECURELOAD = 1. Autodesk tells developers to make apps work with the defaults SECURELOAD = 1 and LEGACYCODESEARCH = 0. ([G:C3E22BC9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C3E22BC9-5703-4F7A-AFFA-D9FE9B39E1BA))
- Since AutoCAD 2014, custom apps must work in secure mode (SECURELOAD = 1 or 2): the program loads and runs code only from trusted locations, set by the TRUSTEDPATHS system variable. Stated for plug-ins, NETLOAD, LISP, ARX and VBA. ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008), [G:D790D6DA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D790D6DA-4592-4C58-910F-42E4AA9EA982), [G:4E633A41](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E633A41-30EA-4C6B-ABC5-11F58970E1EE), [G:409E18E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-409E18E6-7164-41CB-A188-97E79E42BC5A), [G:30F06535](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30F06535-7FB5-4F03-A0EE-96973836E231), [G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A))
- The full value table for SECURELOAD (what 0, 1, 2 each do) and the TRUSTEDPATHS separator and default are NOT in these inputs. ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B) gives no values.)
- Code-bearing "trusted path" file types: `*.arx, *.crx, *.dbx, *.dll, *.dvb, *.fas, *.lsp, *.rx, *.scr, *.vlx`. Note .scr is in this list. ([G:83590A12](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83590A12-D545-49CE-B129-4C9D36952792)) (inference: a script outside a trusted folder may get the same check; test before a headless run.)
- Options > Files > Trusted File Search Path is the dialog list of these folders (inference that it is the TRUSTEDPATHS view; [G:83590A12](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83590A12-D545-49CE-B129-4C9D36952792) lists the node, does not name the variable).
- Signing benefit stated by Autodesk: signed files can load from outside a trusted location without the "File Loading - Security Concern" message box each time; once a publisher is trusted, all its signed files are trusted. By default, files in a bundle are not trusted. ([G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691)) (inference: that message box is modal and stalls a script or COM run.)

### Ways to load code without touching SECURELOAD
1. Put files in a folder already in TRUSTEDPATHS. Read it first: `(getvar "TRUSTEDPATHS")`. [AUTO]
2. Install a bundle under `%PROGRAMFILES%\Autodesk\ApplicationPlugins`. Plug-ins there are trusted and NOT checked for a signature. Other ApplicationPlugins folders must be trusted in the program's preferences and should be signed. ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008)) (inference: writing under Program Files needs admin rights.)
3. Sign the files and trust the publisher (13.6). ([G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691))
4. Adding a folder to TRUSTEDPATHS is a different variable from SECURELOAD, but it is still a security setting. Clear it with whoever owns CAD security for your machines before changing it (policy note, not from the docs).
- Conflict to keep in mind: [G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008) says bundles under Program Files are trusted; [G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691) says files in a bundle are not trusted by default. Read together (inference): only the Program Files plug-in folder is trusted automatically.

### LEGACYCODESEARCH ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B), [G:C3E22BC9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C3E22BC9-5703-4F7A-AFFA-D9FE9B39E1BA)) [AUTO]
- Controls whether the Start In folder and the drawing's folder are searched for EXECUTABLE files (LSP, ARX, DLL...). Autodesk recommends 0 (off): those folders are common malware targets. Default 0.
- Consequence (inference): with 0, code sitting only next to the DWG is not found. Load it by full path from a trusted folder, or put it on the support and trusted paths.

### Library search path (file name given without a full path) ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B))
1. Start In folder (STARTINFOLDER). 2. Current drawing folder (DWGPREFIX). 3. Project folder for xrefs, images, underlays (PROJECTNAME). 4. Support File Search Path (ACADPREFIX). 5. Program install folder.
- Steps 1 and 2 are searched for executable files only if LEGACYCODESEARCH is on.
- Outside the path, give a full or relative path. Doc example at a prompt: `-insert` then `/files2/olddwgs/part5`.
- acad<release>.lsp and acad<release>doc.lsp (acad2027.lsp, acad2027doc.lsp) load ONLY from the product's install folders (since 2013 SP1). A copy elsewhere is not used as a startup file. ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B), [G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520))

### Support paths and Options > Files (Windows; Options needs an open drawing) ([G:B8426D5A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B8426D5A-766F-42D6-9A45-70BD6B77E211), [G:83590A12](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83590A12-D545-49CE-B129-4C9D36952792))
- Support File Search Path: Options > Files > Add > Browse > OK. [GUI] ([G:348D791E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-348D791E-D621-444F-B059-C0C6F97AD69F)) Command-line override per launch: `/s` (13.1). From code: the COM `Preferences.Files` object (13.10).
- Nodes on the Files tab: Support File Search Path; Trusted File Search Path; Help and Miscellaneous File Names > Configuration File ([G:F9B57D49](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F9B57D49-87EB-49C5-BD53-372D3B81AFBC)); Customization Files > Main / Enterprise Customization File, Custom Icon Location; Text Editor, Dictionary, and Font File Names > Font Mapping File, Alternate Font File; Template Settings > Drawing Template File Location ([G:B8426D5A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B8426D5A-766F-42D6-9A45-70BD6B77E211)); Printer Support File Path > Printer Configuration Search Path (PC3, [G:F4D1D0EA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F4D1D0EA-15D0-4EA9-A3D6-31BC01D3C031)), Printer Description File Search Path (PMP, [G:517CE2BB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-517CE2BB-8266-4DD5-9019-2FC2BCC9A6DD)), Plot Style Table Search Path ([G:22A1CA9D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-22A1CA9D-9416-40CC-BE60-1E9CA9070A9B)); Print Support File Path > Print Spooler File Location ([G:40F523CD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-40F523CD-55E4-4C76-9F1A-5AE7F422BC0E)); Data Sources Location (restart needed, [G:94535264](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-94535264-9C9C-4BBC-9B58-FDF0EF12C021)); Texture Maps Search Path ([G:726D5E3B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-726D5E3B-32BD-403A-BBAC-0AD97D34DC82)).
- "Support path" file types: `*.dcl, *iso.lin, *iso.pat, *.lin, *.mnl, *.pat, *.pgp, *.psf, *.pss, *.shx, *.unt`. Others: `*.cfg`, `*.cuix`, icons `*.bmp`, help `*.chm/*.htm/*.html`, font map `*.fmp`, alternate font `simplex.shx`. ([G:83590A12](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83590A12-D545-49CE-B129-4C9D36952792))
- PROJECTAWARE (AutoCAD 2026 and later): 1 = support paths come from the Forma Data Management project the open drawing belongs to, not the user profile. Only an admin edits project paths. Stated on the template, trusted path and support path pages, not on the PC3 or plot style pages. ([G:B8426D5A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B8426D5A-766F-42D6-9A45-70BD6B77E211), [G:83590A12](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83590A12-D545-49CE-B129-4C9D36952792), [G:348D791E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-348D791E-D621-444F-B059-C0C6F97AD69F))
- LOCALROOTPREFIX and ROAMABLEROOTPREFIX give the local and roamable root folders of customizable files. Read with getvar. ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B)) [AUTO] The AppData product folder is hidden by default. ([G:D4A64920](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D4A64920-8520-4BCA-9D49-DCB3BCE2B6E8))
- Keep add-on code apart from the install folder, e.g. `/AcadApps` for programs and `/AcadJobs/<job>` for drawings. ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B))

## 13.4 Startup code: acad.lsp, acaddoc.lsp, MNL, S::STARTUP, acad.rx, acad.dvb

### Which files load, and when ([G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520))
- acad.lsp: loads ONCE at program start (ACADLSPASDOC = 0, the default). ACADLSPASDOC = 1 reloads it with every new or opened drawing. With 0, functions defined in acad.lsp exist only in the FIRST drawing. [AUTO]
- acaddoc.lsp: loads with EVERY drawing, always, whatever ACADLSPASDOC is. Searched on the library path, so a drawing folder can carry its own acaddoc.lsp. (Conflict: with LEGACYCODESEARCH = 0 the drawing folder is not searched for executable files, [G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B). Test before relying on a per-folder acaddoc.lsp.)
- Neither acad.lsp nor acaddoc.lsp ships with the product. You create them. Best practice: only `(load ...)` calls inside.
- Reserved files, do not edit: acad2027.lsp loads right before acad.lsp; acad2027doc.lsp loads right before acaddoc.lsp.
- MNL: when a CUIx loads, the same-name MNL loads (custom.cuix -> custom.mnl), AFTER acaddoc.lsp. If a menu is loaded with `(command "menu" "newmenu")`, its MNL loads only after the whole LISP routine ends.
- Order (inference from the "right before" and "after" statements): acad2027.lsp, acad.lsp, acad2027doc.lsp, acaddoc.lsp, MNL, then S::STARTUP after the drawing is initialized.
- Each open drawing has its own AutoLISP namespace; variables do not cross drawings. ([G:16DC15FC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-16DC15FC-5329-492E-B66A-401D49CF971F))
- No-file alternative: APPLOAD > Startup Suite [GUI].

### Rules that break startup files [AUTO]
- An AutoLISP error while a startup file loads makes AutoCAD skip the REST of that file. ([G:1C6334CF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1C6334CF-9FC8-4E94-B69C-0A001F625A5E))
- Guard each load: `(princ (load "build" "\nBUILD.LSP file not loaded."))`, end the file with `(princ)`. `load` returns the last expression's value, or the onfailure value. ([G:1C6334CF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1C6334CF-9FC8-4E94-B69C-0A001F625A5E))
- `command` is not guaranteed before the drawing is initialized. In acad.lsp, acaddoc.lsp and MNL files call `command` only inside a `defun`; put startup commands in S::STARTUP. ([G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520), [G:1C6334CF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1C6334CF-9FC8-4E94-B69C-0A001F625A5E))
- S::STARTUP must be defined with `defun-q` so it can be appended. Safe pattern: `(defun-q MYSTARTUP () ...)` then `(setq S::STARTUP (append S::STARTUP MYSTARTUP))`. ([G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520))
- Doc example of replacing a built-in: acaddoc.lsp defines `C:HATCH` (alert, then `(command "BHATCH")`) and `C:OLDHATCH` (`(command ".HATCH")`), and S::STARTUP runs `(command "undefine" "hatch")` after init. The period in `".HATCH"` reaches the original. ([G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520))
- Like-named LSP, FAS or VLX files: the newest Modified time wins unless you give the full name with extension. ([G:4E633A41](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E633A41-30EA-4C6B-ABC5-11F58970E1EE), [G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520))
- Paths in LISP strings use `/` or `\\`, never one backslash: `(load "d:/files/morelisp/newfile")`. ([G:4E633A41](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E633A41-30EA-4C6B-ABC5-11F58970E1EE)) Applies to every LISP path sent over COM or in a script.
- LSP source may be ASCII or Unicode from AutoCAD 2021-based products on. ([G:4E633A41](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E633A41-30EA-4C6B-ABC5-11F58970E1EE))
- Lazy loading: `(autoload "CMDS" '("CMD1" "CMD2"))` registers commands and loads cmds.lsp on first use; `autoarxload` does the same for ARX. ([G:FDB4038D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FDB4038D-1620-4A56-8824-D37729D42520))

### ObjectARX and VBA at startup
- acad.rx: plain text, one ARX app name per line, loaded at startup; searched in library-path order, else the default in the program folder. ([G:409E18E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-409E18E6-7164-41CB-A188-97E79E42BC5A))
- `(arxload "myapp" [onfailure])` returns the program name; loading an already loaded app is an error, check with `(arx)`; `(arxunload "myapp")` also removes its commands. `arxload` from an MNL loads an app with its menu. ([G:409E18E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-409E18E6-7164-41CB-A188-97E79E42BC5A)) [AUTO]
- VBA is not installed by default (download from autodesk.com/vba-download). ([G:2CD40631](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2CD40631-D67B-4DF0-A2C4-606E9B613252)) An `acad.dvb` on a support path with a macro `AcadStartup` loads and runs per drawing session. ([G:30F06535](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30F06535-7FB5-4F03-A0EE-96973836E231))
- From LISP: `(command "_-vbaload" "mytools.dvb")` or `(vl-vbaload "mytools.dvb")`; run with `-vbarun` then `project!module.macro`, or `(vl-vbarun "mytools.dvb!utilities.selectcircles")`. Loading a DVB shows an Enable Macros box [GUI]. ([G:30F06535](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30F06535-7FB5-4F03-A0EE-96973836E231), [G:E50E8491](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E50E8491-5BCB-4202-B3A9-BF6FD9CF68A3))

## 13.5 Plug-in bundles and PackageContents.xml

### What a bundle is and where it goes ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008), [G:40F5E92C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-40F5E92C-37D8-4D54-9497-CD9F0659F9BB))
- A bundle is a FOLDER whose name ends in `.bundle`, not a file. It holds `PackageContents.xml` plus the app files. One bundle can target several OSs and releases.
- Folders scanned at startup (Windows): `%PROGRAMFILES%\Autodesk\ApplicationPlugins` (general), `%ALLUSERSPROFILE%\Autodesk\ApplicationPlugins` (all users), `%APPDATA%\Autodesk\ApplicationPlugins` (current user). Found bundles are registered and loaded from their XML.
- Use the Program Files folder: bundles there are trusted and not signature-checked. The other two must be made trusted in the preferences and should be signed. ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008)) See 13.3.
- Install: MSI or copy the folder tree. Uninstall: delete the `.bundle` folder. ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008))
- [AUTO] APPAUTOLOAD (system variable) controls plug-in loading. By default, plug-ins installed during a session register automatically. APPAUTOLOAD = 0: no plug-ins load unless the APPAUTOLOADER command is run. Other values are not given here. ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008))
- AutoCAD LT for Windows: bundles for local deployment only. ([G:BC76355D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC76355D-682B-46ED-B9B7-66C95EEF2BD0))
- Organized subfolders (Contents, Resources, Help) can significantly speed up load times. ([G:CBDC037A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CBDC037A-9B84-4ED2-B0A6-6552ECF59540))
- Doc example gotcha: the OfficeSymbols XML points at `./Contents/LISP/OfficeSymbolsUtilities.lsp` but the printed tree has no LISP folder. ModuleName must match the real path. ([G:40F5E92C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-40F5E92C-37D8-4D54-9497-CD9F0659F9BB))

### Top level ([G:BC76355D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC76355D-682B-46ED-B9B7-66C95EEF2BD0), [G:EC442AA9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC442AA9-EA8C-4D69-A434-2F3DAFBB06AE))
- Three element groups: ApplicationPackage (exactly one, wraps the rest), CompanyDetails, Components.
- ApplicationPackage attributes:
  - SchemaVersion: always `1.0` for now. Required.
  - AppVersion: e.g. `1.0.0.0`; decides whether the installed copy is newest. Required.
  - ProductCode: unique GUID per plug-in; CHANGE it whenever AppVersion changes. Required.
  - UpgradeCode: GUID that must NEVER change (upgrades without uninstall). Optional for local deployment.
  - Author, Name, Description, Icon (32x32, 32-bit, BMP or ICO), HelpFile (TXT, HTML, PDF). Name, Description, Icon, HelpFile recommended for local deployment.
  - Icon and HelpFile paths use `/`, relative to the `.bundle` root.
- Child list on [G:EC442AA9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC442AA9-EA8C-4D69-A434-2F3DAFBB06AE) names `DependentBundles`; the format table and Dependencies page name the element `Dependencies` ([G:BC76355D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC76355D-682B-46ED-B9B7-66C95EEF2BD0), [G:35FAF023](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-35FAF023-9E18-44FB-B934-5031FC19EAF3)). Both as printed.
- CompanyDetails (Name, Phone, URL, Email) is optional for local deployment, required for App Store. ([G:8364E8F1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8364E8F1-3365-4A13-B1C4-C85E48D4D20C), [G:BC76355D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC76355D-682B-46ED-B9B7-66C95EEF2BD0))

### Components and ComponentEntry ([G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F))
- Several Components elements allowed. Each may hold RuntimeRequirements, many ComponentEntry, and at most ONE each of RegistryEntries, SystemVariables, EnvironmentVariables.
- ComponentEntry attributes:
  - AppName: REQUIRED for ObjectARX and .NET, optional for AutoLISP ([G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F)). The format table marks it Required for all ([G:BC76355D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC76355D-682B-46ED-B9B7-66C95EEF2BD0)). Always set it.
  - ModuleName: relative path inside the bundle, `/` separators. Type comes from the extension: `.dll` managed .NET; `.arx`; `.dbx`; `.lsp .fas .vlx`; `.cuix`; `.atc` tool palette; `.dvb`, `.js`, `.xaml` (2015-based and later).
  - AppType: overrides the extension. Values: `.Net`, `Arx`, `Atc`, `Bundle`, `Cui`, `CuiX`, `Dbx`, `Dependency` (resource DLL, NOT loaded), `JavaScript`, `Lisp`, `CompiledLisp`, `Mnu`, `VBA`, `Xaml`.
  - AppDescription; PerDocument (AutoLISP only; True = load once per document; default True); XamlType (only `ContextualTabRule`, required for XAML).
- Windows AutoCAD loads from bundles: LSP, FAS, VLX, ARX/CRX, DBX, XAML, CUI/CUIX, ATC, JS, managed or mixed .NET DLL, DVB.
- [AUTO] LOAD ORDER IS BOTTOM UP: ComponentEntry elements load in listed order from the bottom. A file others depend on goes LOWER in the list (an ARX that needs a DBX is listed above the DBX).
- DVB in a bundle: needs the VBA enabler; the user must click Enable Macros [GUI]; loads only when a drawing is open at startup (set STARTUP to 0 or 1).

### LoadReasons ([G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F))
- Defaults when LoadReasons is not given: LoadOnAutoCADStartup, LoadOnAppearance, LoadOnProxy = True; LoadOnCommandInvocation = False.
- LoadOnCommandInvocation: load when a listed command runs. Needs a Commands element. AutoLISP, ObjectARX, .NET only. Turning it on turns OFF LoadOnAutoCADStartup and LoadOnAppearance unless set True explicitly. Defining any Command element turns it on implicitly. Autodesk calls it very important for startup speed.
- LoadOnAutoCADStartup: overrides all others; VBA, ObjectARX, .NET only.
- LoadOnProxy: ObjectDBX only. LoadOnAppearance: load as soon as the bundle appears in an ApplicationPlugins folder, no restart.
- The page calls LoadReasons both an "attribute" and an "element" and shows no XML example of it (source checked). Prefer controlling load with a Commands block, or test the syntax first.

### Commands ([G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F))
- `<Commands GroupName="...">` holds `<Command Global="..." Local="..."/>`. Global and Local required; HelpTopic optional (needs HelpFile); StartupCommand = True runs the command at startup.
- Doc example: `<Commands GroupName="ADSKCMDS"><Command Global="HELLOWORLD" Local="ADSKHELLOWORLD"/><Command Global="DRAWLINE" Local="ADSKDRAWLINE"/></Commands>`.

### AssemblyMappings (.NET) ([G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F))
- Tells AutoCAD where to find assemblies that are NOT in the install folder. `AssemblyMapping` (Name = owning ComponentEntry, Path = assembly) and `AssemblyMappingFolder` (Path = folder; AutoCAD 2022-based and later).
- Example: `<AssemblyMappings><AssemblyMappingFolder Path="./Content/Assemblies" /></AssemblyMappings>`.

### RuntimeRequirements ([G:1591CA01](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1591CA01-EF87-48CD-952B-772FE26037F1))
- Attributes: OS (`Win32`, `Win64`, `Mac`, combine with `|`); Platform; SeriesMin; SeriesMax; SupportPath and ToolPalettePath (semicolon lists, relative to the bundle).
- Platform values: `AutoCAD`, `AutoCAD*` (all AutoCAD-based), `MEP` (AutoCAD MEP), `ACADE`, `ACADM`, `ACADLT`, `ADT`, `Civil`, `Civil3D`, `Map`, `Plant3D`, `PNID`, `AIP`, `AIPRS`, `AIPSIM`, `AIS`, `AOEM`, `LDT`.
- Not stated which Platform value AutoCAD 2027 with the MEP toolset reports. Omit Platform or use `AutoCAD*` (inference).
- SeriesMin / SeriesMax: major (`R24`) or specific (`R24.1`), from the registry or ACADVER. AutoCAD 2027 = release 26.0 ([G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A)) and registry R26.0 ([G:4DA730AB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4DA730AB-7A47-4663-838B-21E71438D6C8)), so `SeriesMin="R26.0"` (inference; confirm with ACADVER). Both absent = all releases.
- Required or not is inconsistent: "recommended/optional" ([G:1591CA01](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1591CA01-EF87-48CD-952B-772FE26037F1)); required if Components exists ([G:BC76355D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC76355D-682B-46ED-B9B7-66C95EEF2BD0)); required for AutoCAD LT ([G:EC442AA9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC442AA9-EA8C-4D69-A434-2F3DAFBB06AE)). Include it. If omitted, all products, releases and OSs are assumed OK.

### RegistryEntries, SystemVariables, EnvironmentVariables (2015-based and later) ([G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F)) [AUTO]
- RegistryEntry: Name, Value, Type (`REG_SZ`, `REG_EXPAND_SZ`, `REG_DWORD`, `REG_QWORD`), Flags. Written ONLY under `HKEY_CURRENT_USER\Software\Autodesk\AutoCAD\<release>\ACAD-<product>:<language>`.
- SystemVariable: Name, Value, PrimaryType (`Int16`, `Int32`, `Real`, `String`), StorageType (`Database`, `Profile`, `Session`, `User`), Owner, Flags.
- EnvironmentVariable: Name (case sensitive), Value (stored as string), Type, Flags.
- Flags: `Create` (default), `Open` (change on every load, only if it exists), `OpenOnce` (first load only). Open or OpenOnce is REQUIRED to modify an existing value. System variables also: `SpacesAllowed`, `DotIsEmpty`, `NoUndo`, `Chatty` (Create only).
- Value operator prefixes: `+` add or append, `-` subtract or remove text, `&` bitwise AND, `|` bitwise OR (numeric). Escape a literal leading character with `\`, e.g. `\+radius`.
- Doc examples: `Name="OSMODE" Value="|63" Flags="Open"` (always turns on END, MID, CEN, NOD, QUA, INT); `Name="CURSORSIZE" Value="100" Flags="OpenOnce"`.

### Dependencies (AutoCAD 2022-based and later) ([G:35FAF023](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-35FAF023-9E18-44FB-B934-5031FC19EAF3))
- `<Dependency UpgradeCode="..." Optional="False" VersionMin="2.0" VersionMax="5.0"><Component AppName="App1" /></Dependency>`. UpgradeCode must equal the other bundle's UpgradeCode.
- The Optional attribute is printed as True = "Bundle is required", which reads backwards. The text says Component uses `Name`, the example uses `AppName`. Test before relying on either.

### Locale codes ([G:90A822A0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-90A822A0-3595-401B-8DE6-22A9BC969660))
- Append to attribute names to localize: `Enu`, `Esp`, `Fra`, `Deu`, `Ita`, `Jpn`, `Kor`, `Chs`, `Cht`, `Csy`, `Hun`, `Plk`, `Ptb`, `Rus` (e.g. `DescriptionEsp`).

### Minimal .NET bundle skeleton (assembled from the documented attributes above; not a doc sample)
`MyTools.bundle\PackageContents.xml`:
```
<ApplicationPackage SchemaVersion="1.0" AppVersion="1.0.0.0"
  ProductCode="<new GUID>" UpgradeCode="<fixed GUID>" Name="<plug-in name>" Author="<author>">
  <CompanyDetails Name="<company>" />
  <Components>
    <RuntimeRequirements OS="Win64" Platform="AutoCAD*" SeriesMin="R26.0" SeriesMax="R26.0" />
    <ComponentEntry AppName="MyTools" ModuleName="./Contents/MyTools.dll">
      <Commands GroupName="MyTools"><Command Global="MYEXPORT" Local="MYEXPORT" /></Commands>
    </ComponentEntry>
  </Components>
</ApplicationPackage>
```
The Commands block makes the DLL load on first use of MYEXPORT. Remove it to load at startup (default LoadOnAutoCADStartup).

## 13.6 Digital signing and loading signed files

### What can be signed, with what ([G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691), [G:3DA95353](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3DA95353-9EF3-4E29-9671-6AEB7704EBE6), [G:A63E8C40](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A63E8C40-6870-4874-BF7E-FD75E87268AA))
- Signable: ARX, CRX (Console Runtime Extension: like ARX, no user interface), DBX, DLL (.NET assembly or menu resource), FAS, MNL, LSP, VLX. Also MSI installers that deploy custom programs. NOT signable: DVB (VBA) and JS.
- AcSignApply.exe signs AutoLISP (LSP, MNL, FAS, VLX) and can also sign a DWG. Installed with the product: Start > Autodesk > Attach Digital Signatures.
- SignTool.exe signs binaries (ARX, CRX, DBX, DLL, MSI). Part of the Windows SDK; NOT installed with AutoCAD.
- Since AutoCAD 2016-based products every loaded custom file is checked for a signature. ([G:5E50A846](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5E50A846-C80B-4FFD-8DD3-C20B22098008))
- Workflow: get a certificate (vendor such as Symantec or DigiCert for public release; self-made for testing and in-house), import it, sign, then load the file and confirm the signature is recognized. ([G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691), [G:26D7B31C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-26D7B31C-4165-410C-9FC4-2D556749D517))

### Command lines (shortened; full forms on the linked pages) [AUTO]
- Make a test certificate ([G:26D7B31C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-26D7B31C-4165-410C-9FC4-2D556749D517)): `MakeCert.exe -r -sv MyCert.pvk -n "CN=<publisher>" MyCert.cer -b <start date> -e <end date>`. MakeCert ships with the Windows SDK (`Windows Kits\10\bin\x64`). `-r` self-signed, `-sv` private key file, `-n` publisher, `-b`/`-e` validity dates. It opens password dialogs [GUI].
- Merge the key and certificate into a PFX with `pvk2pfx.exe` from the same SDK folder: `-pvk` key file and `-spc` certificate in, `-pfx` file out, `-pi` / `-po` for the key and PFX passwords ([G:DC1B25FE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DC1B25FE-E063-486C-B90C-565AB5E87BBC)).
- Sign a binary: `signtool.exe sign /f MyCert.pfx /p <pfx password> /t <timestamp server URL> <file>` ([G:3DA95353](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3DA95353-9EF3-4E29-9671-6AEB7704EBE6)). `/t` adds a time stamp. Signing fails if the file or its folder is read-only.
- Sign on every build: put the same signtool line in a Visual Studio post-build event with `"$(TargetDir)$(TargetFileName)"` as the file, run On Successful Build ([G:AA7BBBED](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-AA7BBBED-98D0-4003-8C80-D66173664DBA)). Special characters in the project name or path can break SignTool. Success prints `Successfully signed: <path>`.
- Import certificates with `certutil.exe` ([G:19D6716A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-19D6716A-0AD1-4A7A-82BA-A067E6D65F66)): `-addstore Root MyCert.cer` adds a CER to a store; `-importpfx MyCert.pfx` (with `-p <pfx password>`) imports a PFX, and adding `-user` targets the current user's Personal store. Store names: My, TrustedPublisher, AddressBook, AuthRoot, CertificateAuthority, Disallowed, TrustedPeople, Root. The page is inconsistent about whether `-addstore` targets Root or TrustedPublisher. GUI route: `certmgr.msc` > Personal > All Tasks > Import.

### Rules
- To SIGN AutoLISP the PFX must be in the Personal (My) store. To VALIDATE signed binaries the PFX or CER must be in the Trusted Root (Root) store; AutoCAD verifies a signature only when the certificate is in Trusted Root. ([G:19D6716A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-19D6716A-0AD1-4A7A-82BA-A067E6D65F66), [G:3DA95353](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3DA95353-9EF3-4E29-9671-6AEB7704EBE6))
- Any edit to a signed LISP file invalidates the signature. Re-sign and choose "Replace the Existing Signature" or "Replace All Existing Signatures". ([G:A63E8C40](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A63E8C40-6870-4874-BF7E-FD75E87268AA))
- A signed VLX cannot load in AutoCAD 2015-based and earlier products. Back up VLX files before signing. ([G:A63E8C40](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A63E8C40-6870-4874-BF7E-FD75E87268AA))
- LISP signing is a dialog: "Attach Digital Signatures" > Add Files or Search Folders > Select a Digital ID (Certificate) > Get Time Stamp From (or Time from This Computer) > Sign Files. [GUI] ([G:A63E8C40](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A63E8C40-6870-4874-BF7E-FD75E87268AA))
- .NET: do NOT strong-name sign. Error "'Acdbmgd' does not have a strong name" means project Properties > Signing > "Sign the assemblies" is on. Clear it and use Authenticode (SignTool) in a post-build event. ([G:0AFCAF6A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0AFCAF6A-07DA-44EB-835F-9CBD3253F3D6))
- AcSignApply error "File may be read-only or in use.": file locked, no write access, or corrupt certificate. ([G:79B5E715](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-79B5E715-33AC-43BC-BF22-BD50E816005B))

### What the user sees when a signed file loads ([G:5CE8D264](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5CE8D264-FB3B-4E66-A637-183EB999F210))
- Signed and unsigned files load with the same commands (APPLOAD, NETLOAD, ARX, APPAUTOLOADER, APPAUTOLOAD). A signed file shows a verification box: Load or Do not load. [GUI]
- Verified and unchanged: load; optionally trust the publisher so the box no longer shows for any file from that publisher.
- Cannot be verified: unsigned, badly signed, or certificate not in "Trusted Root Certification Authorities". Fix by installing the certificate there.
- Changed after signing: do not load.
- (inference) For unattended runs, trust the publisher once by hand so the box does not appear later.

## 13.7 Plotter configuration: PC3, PMP, paper sizes, ports, AutoSpool

### The editor ([G:907BB938](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-907BB938-AC02-4A64-BAEF-1E5F14B197AD), [G:814AB2AF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-814AB2AF-5D2E-4CB5-B8E0-8E1F98E835F4), [G:6B38619A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6B38619A-4ED5-4713-A163-0D3E0A3847B0))
- PLOTTERMANAGER (Application menu > Print > Manage Plotters) opens the plotter folder; double-click a PC3 to open the Plotter Configuration Editor. [GUI]
- Tabs: General, Ports, Device and Document Settings. Only settings the device supports appear in the tree.
- Whole branches can be dragged from one PC3 to another. The Custom item copies automatically from OS (system) drivers, only when selected for nonsystem drivers.
- Save under a new name: Device and Document Settings tab > Save As > name > Save. ([G:023C02F1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-023C02F1-1D67-4353-B528-97D0812E9464))
- No command-line or system-variable way to edit a PC3, PMP, media, pens or ports is given in these pages. Set it once by hand, save the PC3, reuse it (inference). [GUI]
- Search lists: Options > Files > Printer Support File Path > Printer Configuration Search Path (PC3), Printer Description File Search Path (PMP), Plot Style Table Search Path. No default folders given. ([G:F4D1D0EA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F4D1D0EA-15D0-4EA9-A3D6-31BC01D3C031), [G:517CE2BB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-517CE2BB-8266-4DD5-9019-2FC2BCC9A6DD), [G:22A1CA9D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-22A1CA9D-9416-40CC-BE60-1E9CA9070A9B))

### PMP files, calibration, custom paper sizes
- A PMP (plotter model parameter) file stores calibration and, for nonsystem plotters, custom paper sizes. A PMP made by calibration is auto-attached to the PC3 used for the test. ([G:E755A113](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E755A113-91B4-42BC-8F65-C7FAA2E02C4E))
- Calibrate only if drawings must plot exactly to scale (test: a 10-inch line at 1:1 must measure 10 in). Prefer the plotter maker's utility. Wizard: Calibrate Plotter > paper > Rectangle Size > Measured Plot > File name (PMP saved in the product's Drv folder) > Check Calibration > Finish. ([G:E755A113](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E755A113-91B4-42BC-8F65-C7FAA2E02C4E), [G:55BAF217](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-55BAF217-6E48-44AD-AB90-4EA1937B3AAD)) [GUI]
- Device and Document Settings > User-Defined Paper Sizes & Calibration: Attach / Detach / Save PMP. Detach is unavailable if no PMP is attached. ([G:96F4A7FB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-96F4A7FB-DD08-4167-A053-ABD09B737663), [G:D0BD3D7E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D0BD3D7E-E951-4D14-9DFD-120C1407F9AD), [G:3BB4832D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3BB4832D-F612-4D5A-BAAC-613D933B75EE))
- Custom Paper Sizes > Add > wizard: Start from Scratch or Use Existing > Media Bounds (Inches or Millimeters; Width, Length) > Printable Area > Paper Size Name > File Name (PMP) > Finish (Print Test Page optional). Raster outputs (BMP, TIFF) size in pixels. ([G:D55691E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D55691E6-3D29-4404-99D6-8B7185628EB8), [G:43248E5C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-43248E5C-A78B-4346-BF9E-23FEFE1FCEE9))
- System printers: custom sizes are made in the driver's own dialog (Custom Properties > Access Custom Dialog). The AutoCAD wizard can only fix the printable area of standard sizes (Modify Standard Paper Sizes). ([G:865FF364](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-865FF364-64B4-4A60-A616-22FA4BA6EDB7), [G:E755A113](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E755A113-91B4-42BC-8F65-C7FAA2E02C4E), [G:EBE15E06](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EBE15E06-23FB-4A8F-B4CA-48B53E789FB7))
- Filter Paper Sizes: checked sizes are the ones listed in the Plot and Page Setup dialogs. ([G:FD6FACBE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FD6FACBE-C349-4668-A515-D5E48D1F88E4))
- Media: Source and Size, Media Type, Duplex, Media Destination. System printers set media through Custom Properties. ([G:E7883389](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E7883389-689B-43FA-B733-E4179042E6E6))
- Custom Properties opens the driver maker's dialog; cannot be driven by a script (inference). ([G:5539170E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5539170E-5986-4B2E-8017-DC304D88D6C2))
- Graphics: Installed Memory, Vector Graphics (color depth, resolution, dithering), Raster Graphics, TrueType Text, Merge control. ([G:07E14A9B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-07E14A9B-DC24-42E8-80FD-5D9CEA6B94D3))
- Physical pens are never auto-detected. "AutoCAD PDF (General Documentation).pc3" and "DWF6 ePlot.pc3" have no physical pens: assign pens through plot style tables. ([G:4E4336D6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E4336D6-5CD6-4F8C-AFD7-B2471DA12C27)) "DWG To PDF.pc3" is not named on that page.
- Initialization strings: only for unsupported nonsystem plotters in emulation mode. ([G:B30BC745](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B30BC745-EC3A-4CB6-B1A6-C0A6169723B3))

### Ports, timeouts ([G:DD9C98E9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DD9C98E9-BC4A-4E54-837A-53CF80222A1B), [G:8028B340](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8028B340-AA7B-4DD1-832F-8270755DBA7D), [G:3E9066ED](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3E9066ED-9430-4EEA-9DBA-6156AAA0D5A5))
- Ports tab: Plot to the Following Port; Plot to File (file name set on the Options Files tab); AutoSpool; Show All Ports; Browse Network. Defaults: parallel LPT1, serial COM1.
- A Windows system printer on the same local port forces spooling through Windows; PC3 port settings are then ignored. Across a network the remote computer owns the port settings.
- Timeout default 30 seconds; raise it for complex drawings or slow pens. Local parallel: Transmission Retry (ms); serial: Input and Output Timeout (ms); system printers: Windows printer Properties > Ports > Configure Port (seconds). ([G:3E9066ED](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3E9066ED-9430-4EEA-9DBA-6156AAA0D5A5), [G:907A8502](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-907A8502-BFFF-4AA3-B340-6A490676BF7C), [G:4AA478D1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4AA478D1-716E-44E2-BC33-0D749B52C5BD))
- Serial flow control default XON/XOFF; Hardware enables Advanced (CTS, DSR, RLSD, RTS, DTR). ([G:FB699DA4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FB699DA4-1DF3-49DC-8CED-88E30D92DD81))

### AutoSpool ([G:CD9B5B2F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CD9B5B2F-74A0-4C69-9176-A8BE717B833F), [G:40F523CD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-40F523CD-55E4-4C76-9F1A-5AE7F422BC0E), [G:8FBE6A29](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8FBE6A29-EE60-4134-920A-091D747718EA))
- Writes each plot to a random file name in a chosen folder, then runs a program with your argument list. `%s` (spool file path) is required.
- Setup: PC3 Ports tab > AutoSpool; Options > Files > "Print file, Spooler, and Prolog Section Names" > Print Spool Executable, e.g. `myspool.exe %s`; Options > Files > Print Support File Path > Print Spooler File Location.
- Variables: `%s` spool file, `%d` drawing full path, `%c` device description (no spaces), `%m` model, `%n` plotter name, `%p` plotter number, `%w` / `%h` plot width / height, `%i` first letter of plot units, `%l` login name, `%u` user name, `%e` equal sign, `%%` percent.
- Device names in the batch file are case-sensitive. (inference: AutoSpool is a post-plot hook; not stated for PDF drivers; untested.)

### Device and media names used from code ([G:9B330DCF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9B330DCF-6A4E-4C58-B5C1-085E34912077), [G:946669A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-946669A9-E813-4D12-828A-44986E388AA2), [G:96E2EFD0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-96E2EFD0-B16B-4A3A-BA6A-A9277BBB3610), [G:B08B5173](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B08B5173-0C17-4663-BD1C-A40E4C8F3A75))
- PC3 device names are file names: `"DWG To PDF.pc3"`, `"DWF6 ePlot.pc3"`. The publish sample writes `"DWG to PDF.PC3"`.
- Canonical media names look like `ANSI_B_(11.00_x_17.00_Inches)`; list them with `PlotSettingsValidator.GetCanonicalMediaNameList`.
- A device name that matches no installed device silently falls back to the DEFAULT device. Check `GetPlotDeviceList()` first. [AUTO]

## 13.8 .NET for AutoCAD 2027: framework, project file, references, compatibility

### The basics
- The AutoCAD .NET API exposes AutoCAD objects through managed classes (wrappers over ObjectARX). Use it to create and modify objects in a drawing database or change customization files. Any .NET language works; C# is recommended, VB.NET supported. ([G:4E1AAFA9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E1AAFA9-740E-4097-800C-CAED09CDFF12), [G:3A5E2EE7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3A5E2EE7-9A06-4965-A614-AD97A49B849A), [G:8986A7BC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8986A7BC-7B76-4272-A159-3605DC8E977C))
- IN-PROCESS ONLY. A .NET DLL runs inside AutoCAD; it cannot run as a separate exe. To drive AutoCAD from an exe use COM, then load your DLL with SendCommand (13.9). ([G:C8C65D7A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8C65D7A-EC3A-42D8-BF02-4B13C2EA1A4B))
- AutoCAD has been 64-bit only since 2020. ([G:390A47DB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-390A47DB-77AF-433A-994C-2AFBBE9996AE), [G:7045F2A0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7045F2A0-DBC6-4616-8F5C-D31DE338B649))

### Target for 2027 [AUTO]
- AutoCAD 2027 and 2027-based programs (the MEP toolset is one): Microsoft .NET 10.0 and Visual Studio 2026 version 18.0. ([G:450FD531](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-450FD531-B6F6-4BAE-9A8C-8230AAC48CB4), [G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A)) The 2027 readme: managed libraries migrated from .NET 8 to .NET 10. ([G:83DA77DD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83DA77DD-6599-48B2-B965-43ABC3E285F0))
- Earlier: 2026 and 2025 = .NET 8.0 (VS 2022 17.10.4 / 17.8.0); 2024 to 2021 = .NET Framework 4.8; 2020 and 2019 = .NET Framework 4.7. ([G:450FD531](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-450FD531-B6F6-4BAE-9A8C-8230AAC48CB4), [G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A))
- Release notes: anything using .NET for 2027 must target 10.0; install the .NET 10.0 SDK before migrating .NET 8 projects. Visual Studio 2022 17.14 can build native ObjectARX for 2027 but CANNOT build managed .NET apps for it. ([G:4DA730AB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4DA730AB-7A47-4663-838B-21E71438D6C8))
- Build against the SAME or an EARLIER .NET version than the target AutoCAD uses. ([G:15D4DF8D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-15D4DF8D-8B13-47F8-A249-7427FA48D6F9))
- Visual Studio Community works with the API; the guide assumes Professional. Express has no debugger. ([G:450FD531](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-450FD531-B6F6-4BAE-9A8C-8230AAC48CB4), [G:4EB83A6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EB83A6B-9903-4BF7-9F19-767A4D419CE3))
- Test note: compiling does NOT need the .NET SDK. PowerShell 7 running on .NET 10 carries the C# compiler; `Add-Type -TypeDefinition $src -OutputType Library -OutputAssembly X.dll -ReferencedAssemblies accoremgd.dll, acdbmgd.dll, acmgd.dll, ACA\AecbPipeBaseMgd.dll ...` built a .NET 10 command DLL that references accoremgd 26.0, acdbmgd 26.0 and AecbPipeBaseMgd 8.9. Loading is the hard part: NETLOAD from an untrusted folder printed "Unable to load ... assembly" in the Core Console with SECURELOAD 1 and TRUSTEDPATHS empty. Put the DLL in a trusted folder (13.3). Test write-up: [_verified/2026-10-17-dotnet-plugin-build.md](_verified/2026-10-17-dotnet-plugin-build.md). (inference) The SDK-style project below should also build with `dotnet build` from the .NET 10 SDK; Autodesk does not document that route.

### Project file (per the 2027 guide, [G:23E33075](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-23E33075-3C36-48CA-B937-B85606B77F71))
```
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <FrameworkReference Include="Microsoft.WindowsDesktop.App"></FrameworkReference>
  </ItemGroup>
</Project>
```
- `net10.0` may be changed to `net10.0-windows` to target Windows and use Windows libraries; same as Project Properties > Application > General: Target Framework ".NET 10.0", Target OS "Windows". ([G:23E33075](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-23E33075-3C36-48CA-B937-B85606B77F71), [G:E4C5C858](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E4C5C858-787F-4D35-B7FC-1F2CBA3D4966))
- New Project in VS: C#, Windows, Library, template "Class Library", Framework ".NET 10.0 (Long Term Support)". For forms use "WPF Class Library" or "Windows Forms Class Library". NEVER "Class Library (.NET Framework)" or "Class Library (Universal Windows)". A plain library gains WPF or WinForms with `<UseWPF>true</UseWPF>` or `<UseWindowsForms>true</UseWindowsForms>` in the PropertyGroup. ([G:43564EB9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-43564EB9-F843-4771-823C-573495EE23E0))
- Projects never moved to .NET 8: change the version and add the `FrameworkReference Include="Microsoft.WindowsDesktop.App"` line inside the ItemGroup. ([G:4DA730AB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4DA730AB-7A47-4663-838B-21E71438D6C8))
- Optional AutoCAD .NET Wizard templates (C# only): autodesk.com/developautocad, `<release> .NET Wizards.zip` containing `<release> dotNET Wizards.msi`. [GUI] ([G:8657D153](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8657D153-0120-4881-A3C8-E00ED139E0D3), [G:43564EB9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-43564EB9-F843-4771-823C-573495EE23E0))

### References [AUTO]
- Core assemblies: `AcCoreMgd.dll` (editor, publishing and plotting, defining commands and LISP functions), `AcDbMgd.dll` (drawing database objects), `AcMgd.dll` (application and user interface), `AcCui.dll` (customization files). The first-project exercise references AcCoreMgd, AcDbMgd and AcMgd. ([G:8657D153](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8657D153-0120-4881-A3C8-E00ED139E0D3), [G:2363CE7C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2363CE7C-AC2B-4CAC-AE5D-F77B386132D7))
- Reference them from the ObjectARX SDK `inc` folder (recommended; simplified copies with no AutoCAD UI dependency) or from `<drive>:\Program Files\Autodesk\AutoCAD <release>`. SDK download: objectarx.com, license form. [GUI] ([G:2363CE7C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2363CE7C-AC2B-4CAC-AE5D-F77B386132D7), [G:8657D153](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8657D153-0120-4881-A3C8-E00ED139E0D3))
- Set Copy Local = No on every AutoCAD reference. Copies in the build output can cause unexpected results when AutoCAD loads the assembly. ([G:2363CE7C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2363CE7C-AC2B-4CAC-AE5D-F77B386132D7), [G:8657D153](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8657D153-0120-4881-A3C8-E00ED139E0D3)) (inference: in a hand-edited csproj this is `<Private>false</Private>` on each Reference; not in the docs.)
- Default install layout (test observation): `C:\Program Files\Autodesk\AutoCAD 2027\` holds `accoremgd.dll`, `acdbmgd.dll`, `acmgd.dll`, `AcCui.dll`, `Autodesk.AutoCAD.Interop.dll`, `Autodesk.AutoCAD.Interop.Common.dll`, `acad.exe`, `accoreconsole.exe`. AEC/MEP managed DLLs sit in `...\AutoCAD 2027\ACA\` (`AecBaseMgd.dll`, `AecbBldSrvMgd.dll`, `AecbPipeBaseMgd.dll`, `AecbHvacBaseMgd.dll`, `AecbPlumbingBaseMgd.dll`, `AecbElecBaseMgd.dll`, `AecCoreMgd.dll`, `AecPropDataMgd.dll` and others) and `...\AutoCAD 2027\MEP\` (`AecbPartBaseMgd.dll`, `AecbRuntimeCatalogMgd.dll`).
- Extra references named by samples: PresentationCore (System.Windows.Point/Size), WindowsBase, AdWindows.dll (namespace Autodesk.Windows; install folder or SDK). ([G:6C52F8BC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6C52F8BC-B107-4EE4-BA25-5B74900B271A), [G:CB7D7DC2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB7D7DC2-C8C1-4EF9-A638-C4C6184BFC85))

### Namespaces ([G:390A47DB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-390A47DB-77AF-433A-994C-2AFBBE9996AE), [G:F98FAC6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F98FAC6B-4DC4-489E-B65E-5D8C5E64E534))
- ObjectARX prefix to .NET namespace: AcAp = `Autodesk.AutoCAD.ApplicationServices`; AcDb = `.DatabaseServices`; AcGe = `.Geometry`; AcGi = `.GraphicsInterface`; AcPl = `.PlottingServices`; AcRx = `.Runtime`; AcCm = `.Colors`; AcBr = `.BoundaryRepresentation`; AcLy = `.LayerManager`; AcUt = DatabaseServices and ApplicationServices.
- Also used by samples: `.EditorInput` (Editor, prompts), `.Windows` (dialogs, palettes, Window.State), `.Interop` and `.Interop.Common` (COM).
- Full class map: "Mapping ObjectARX Classes to Managed Types" in the Managed Class Reference. ([G:390A47DB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-390A47DB-77AF-433A-994C-2AFBBE9996AE))

### Binary compatibility and release numbers
- Managed .NET table (release | number | SDK | .NET): 2027 | 26.0 | AutoCAD 2027 only | .NET 10.0. 2026 | 25.1 | 2026, 2025 | .NET 8.0. 2025 | 25.0 | 2025 | .NET 8.0. 2024 | 24.3 | 2024 to 2021 | 4.8. ([G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A))
- Binary compatibility table: AutoCAD 2027 is compatible with 2027 ONLY. Releases that broke compatibility (recompile required): 2025, 2021, 2019, 2018, 2017, 2015, 2013, 2010, 2007, 2004, 2000. ([G:73279C76](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-73279C76-12E2-468B-8687-6B07CE12C350))
- ObjectARX: 2027 breaks binary compatibility with 2025 and 2026; relink against the new `*26.lib` files and recompile. ([G:4DA730AB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4DA730AB-7A47-4663-838B-21E71438D6C8))
- Conflict: a note on [G:450FD531](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-450FD531-B6F6-4BAE-9A8C-8230AAC48CB4) says apps built with VS 2019 16.0 or later "should load" into 2027. The tables above say 2027 only. Rebuild for net10.0 (inference: safest).
- Change lists: "What's New and Migration Guide" in `<objectarx install folder>\docs\arxmgd.chm` (managed) and `arxref.chm` (native). ([G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A), [G:C21B8F00](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C21B8F00-C7DE-4E44-8006-D5DC99199F31))

### COM interop from .NET ([G:BFFF308E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BFFF308E-CC10-4C56-A81E-C15FB300EB70))
- Type libraries: `acax26enu.tlb` ("latest AutoCAD (or AutoCAD-based) Type Library") and `axdb26enu.tlb` (AutoCAD/ObjectDBX Common 26.0 Type Library), in `<drive>:\Program Files\Common Files\Autodesk Shared` (seen there in a test install). Interop assemblies: `Autodesk.AutoCAD.Interop.dll`, `Autodesk.AutoCAD.Interop.Common.dll`. The page says they are in the global assembly cache; in a test install they were in the AutoCAD 2027 folder.
- .NET to COM: `Application.AcadApplication`, `Database.AcadDatabase`, `Document.AcadDocument`. COM to .NET: static `FromAcadXxx`, e.g. `Database.FromAcadDatabase`.
- ProgIDs: `AutoCAD.Application.26.0` = 2027; `.25.1` = 2026; `.25.0` = 2025; `.25` = 2025 or 2026; `.24.3` = 2024. A full major.minor ProgID pins one release; that release must be installed. ([G:BFFF308E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BFFF308E-CC10-4C56-A81E-C15FB300EB70), [G:C8C65D7A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8C65D7A-EC3A-42D8-BF02-4B13C2EA1A4B))

### Wrapper rules ([G:DB165894](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DB165894-208B-490E-8382-6BEF5BCA2452), [G:4213EB7F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4213EB7F-C21F-4361-BF12-176F897F44C8))
- Wrappers wrap unmanaged memory: call Dispose (or `using`). Do not rely on garbage collection.
- Opening the same object twice gives two wrappers that compare equal (Equals and GetHashCode use the unmanaged pointer).
- ObjectARX error codes become exceptions. C++ get/set pairs become properties; reactors become events.
- Commands are declared with attributes (13.10), not registered at run time.
- Some features are reachable ONLY through COM objects (Preferences, MenuBar, MenuGroups, Utility). When mixing .NET and COM, return ObjectIds, not objects.
- Collections implement IEnumerable. If you call GetEnumerator yourself on a `dynamic` object, Dispose the enumerator yourself. ([G:DB165894](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DB165894-208B-490E-8382-6BEF5BCA2452))
- C++ interop: `UnmanagedObject` gives the native pointer of a wrapper; `DisposableWrapper.Create()` wraps a native object. A .NET app may include C++ parts to call ObjectARX functions that have no managed wrapper. ([G:FE481D64](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FE481D64-4239-448A-8711-6F6F98D1B092))
- No global functions in the wrappers: command-prompt functions live in a `CommandLinePrompt` class (name as printed), and `acdbTransactionManagerPtr()` became the `Database.TransactionManager` property. ([G:DB165894](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DB165894-208B-490E-8382-6BEF5BCA2452))

## 13.9 Loading .NET code: NETLOAD, demand loading, initialization attributes

### NETLOAD [AUTO]
- FILEDIA = 1 (or not 0): NETLOAD opens the "Choose .NET Assembly" file dialog [GUI], which blocks a script. ([G:D790D6DA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D790D6DA-4592-4C58-910F-42E4AA9EA982), [G:E0EA91B2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E0EA91B2-E833-477C-9F4F-B900E02891D5))
- FILEDIA = 0: NETLOAD prompts `Assembly file name:` at the command line. Type the path, Enter. ([G:0733B384](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0733B384-E920-4007-B364-80EC9A0FC620))
- Script form (assembled from [G:0733B384](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0733B384-E920-4007-B364-80EC9A0FC620) and the script rules in 13.1; inference): lines `FILEDIA 0`, `NETLOAD`, `C:/Tools/MyTools.dll`, then the command name, then a blank last line. Quote a path that has spaces. (inference) Set FILEDIA back to 1 at the end so interactive users get dialogs again.
- From AutoLISP: NETLOAD can be called from inside a LISP file. ([G:70D60274](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-70D60274-57E0-4B22-8D0C-3C7F212A7CAF)) Autodesk's COM sample sends `(command "NETLOAD" "c:/myapps/mycommands.dll")`. ([G:C8C65D7A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8C65D7A-EC3A-42D8-BF02-4B13C2EA1A4B))
- From an external exe over COM (Autodesk sample, C#): `acDocComObj.SendCommand("(command " + (char)34 + "NETLOAD" + (char)34 + " " + (char)34 + "c:/myapps/mycommands.dll" + (char)34 + ") ");` then `acDocComObj.SendCommand("MyCommand ");`. Forward slashes in the path; every sent string ends with a space (Enter). If the assembly is demand-loaded, just send the command. ([G:C8C65D7A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8C65D7A-EC3A-42D8-BF02-4B13C2EA1A4B))
- Getting the COM object in C#: `Marshal.GetActiveObject("AutoCAD.Application.26.0")`, else `Activator.CreateInstance(Type.GetTypeFromProgID(...), true)`; the sample then sets `Visible = true`. ([G:C8C65D7A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8C65D7A-EC3A-42D8-BF02-4B13C2EA1A4B)) (inference: `Marshal.GetActiveObject` exists in .NET Framework but not in .NET 5 and later, so an external driver built on .NET 10 needs another way to attach; verify in the current .NET docs. Python drivers use their own COM library.)
- Secure mode applies: with SECURELOAD 1 or 2 the DLL must be in a TRUSTEDPATHS location (13.3). ([G:D790D6DA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D790D6DA-4592-4C58-910F-42E4AA9EA982), [G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A))
- Managed apps CANNOT be unloaded. `Terminate()` runs only when AutoCAD closes. ([G:FA3B4125](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FA3B4125-F7BD-4E89-969F-9DCC90AC6977)) (inference: to load a rebuilt DLL, restart AutoCAD.)
- Network: by default .NET assemblies cannot be loaded from a network location; they load only if special permissions are granted (the page does not say how). Keep DLLs on a local drive. ([G:01354898](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-01354898-965C-4340-9A39-607B56DAB888)) [AUTO]
- Debug and Release builds both load. Release is for distribution. Default output `\bin\debug` or `\bin\release`; the VS Output pane shows the path. ([G:70D60274](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-70D60274-57E0-4B22-8D0C-3C7F212A7CAF), [G:4EB83A6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EB83A6B-9903-4BF7-9F19-767A4D419CE3))
- Debugging: project Properties > Debug > Start External Program = `acad.exe` in `C:\Program Files\Autodesk\<release>`; Debug > Start Debugging; NETLOAD the DEBUG build. [GUI] Opt out of the Customer Involvement Program so AutoCAD does not crash under the debugger. ([G:4EB83A6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4EB83A6B-9903-4BF7-9F19-767A4D419CE3), [G:01354898](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-01354898-965C-4340-9A39-607B56DAB888))

### Demand loading from the registry ([G:70D60274](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-70D60274-57E0-4B22-8D0C-3C7F212A7CAF)) [AUTO]
- One key per app under the Applications key of the specific AutoCAD release. Values:
  - DESCRIPTION (string, optional).
  - LOADCTRLS (DWORD): 1 load when a proxy object is found; 2 load at startup; 4 load at start of a command; 8 load on request of a user or another app; 16 do not load; 32 load transparently.
  - LOADER (string): the assembly file (full path in the sample).
  - MANAGED (DWORD): 1 = .NET assembly (otherwise ObjectARX).
- Sample RegisterMyApp: root = `HostApplicationServices.Current.RegistryProductRootKey`, opens `Registry.CurrentUser` > that key > `Applications`, creates `MyApp` with LOADCTRLS = 14 and LOADER = `Assembly.GetExecutingAssembly().Location`. So the key is `HKEY_CURRENT_USER\<product root key>\Applications\<AppName>`. AutoCAD loads the DLL at the next start. UnregisterMyApp deletes the subkey tree.
- Gotchas: the sample never updates an existing key (unregister first if the DLL moves); RegisterMyApp is itself a command, so NETLOAD once first (inference); 14 = 2 + 4 + 8 (inference; the page does not say values add); no null check on OpenSubKey.
- Each release has its own registry number (2027 = R26.0, was R25.1). The loader reads ONLY the host version's section: write demand-load entries for each version. Do not hard-code the key; read it at run time. ([G:4DA730AB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4DA730AB-7A47-4663-838B-21E71438D6C8), [G:01354898](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-01354898-965C-4340-9A39-607B56DAB888))
- Bundles (13.5) are the other autoload route.

### Initialization and load-time attributes ([G:FA3B4125](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FA3B4125-F7BD-4E89-969F-9DCC90AC6977), [G:B8F6FD9A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B8F6FD9A-8FC2-47DF-BE26-11073EAF49D5), [G:90D867AA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-90D867AA-6513-4F0C-A498-7453FEA4FEC3))
- `Autodesk.AutoCAD.Runtime.IExtensionApplication`: `Initialize()` at load, `Terminate()` at AutoCAD exit. Empty bodies are fine.
- `[assembly: ExtensionApplication(typeof(Ns.App))]`: put on ONE type, which must implement IExtensionApplication. Without it AutoCAD scans all exported types for an implementation; none = no initialization.
- `[assembly: CommandClass(typeof(Ns.Commands))]`: if ANY CommandClass attribute exists, AutoCAD searches ONLY the listed types for command methods. Declare one for EVERY class that holds commands, or the rest will not register. Without any, all exported types are scanned. The speed gain shows only in larger apps.
- `[assembly: PerDocumentClass(typeof(Ns.MyClass))]`: AutoCAD makes one instance per open document and per document opened later. The class needs a public constructor taking a Document OR a public static `Create(Document)` (Create wins if both exist). Sample keeps the instance in `acDoc.UserData` under a key.
- All three are declared at ASSEMBLY scope.
- First-project sample (2027 guide): `[assembly: CommandClass(typeof(MyFirstProject1.Class1))]`, `[CommandMethod("AdskGreeting")]`, adds an MText at (2,2,0) to Model space; run `netload`, then `adskgreeting`. ([G:90D867AA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-90D867AA-6513-4F0C-A498-7453FEA4FEC3), [G:E0EA91B2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E0EA91B2-E833-477C-9F4F-B900E02891D5))

## 13.10 .NET commands, transactions, document locking, command line, prompts, errors

### Defining commands ([G:6F28B00B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6F28B00B-36BE-4D32-998E-39B62A69E52F), [G:F77E8FE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F77E8FE0-8034-4704-93BD-F717608F8223)) [AUTO]
- Two attributes mark entry points: `CommandMethod` and `LispFunction`. A command method takes NO arguments. A LISP function method takes exactly ONE `ResultBuffer`.
- `[CommandMethod("Name")]` or `[CommandMethod("Name", CommandFlags.UsePickSet | CommandFlags.NoBlockEditor)]`. Optional values: Command Flags, Group Name, Local Name, Help Topic Name, Context Menu Type Flags, Help File Name.
- CommandFlags: `Modal` (not while another command is active); `Transparent`; `Session` (runs in application context, not the document context); `DocReadLock` / `DocExclusiveLock` (document locked when invoked); `NoInternalLock`; `UsePickSet` (pickfirst set cleared when read); `Redraw` (pickfirst and grips NOT cleared); `NoHistory`; `NoUndoMarker` (for commands that do not change the database); `NoPaperSpace`; `NoTileMode`; `NoPerspective`; `NoBlockEditor`; `NoMultiple`; `NoNewStack`; `NoOEM`; `NoInferConstraint`; `Interruptible`; `Undefined` (only by Global Name); `ActionMacro`; `NoActionRecording`; `TempShowDynDimension`; `Defun` (set ONLY by the Visual LISP engine; never set it yourself).
- Instance method: the class is created once PER OPEN DOCUMENT (per-document data). Static method: one copy for all documents. Instance + `Session` = application context with per-document data (like PROPERTIES).
- Samples that create or open drawings use `CommandFlags.Session`. ([G:330A8DCB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-330A8DCB-626F-4271-8B89-9773A7631D87))

### LISP-callable functions ([G:3B2760FE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3B2760FE-A0DC-4229-AEBE-5CC83290BA95)) [AUTO]
- `[LispFunction("DisplayFullName")] public static void DisplayFullName(ResultBuffer rbArgs)`. Read arguments with `foreach (TypedValue tv in rbArgs)`; `tv.TypeCode` vs `(int)LispDataType.Text`; `tv.Value`.
- Types: Boolean, Double, Integer, Null, ObjectId, Point2d, Point3d, ResultBuffer, SelectionSet, String, TypedValue.
- Call from LISP: `(displayfullname "First" "Last")`. So inline LISP sent over COM or a script can reach .NET code. The sample returns void; no return-value pattern is shown.
- The sample imports only Runtime and ApplicationServices; ResultBuffer and TypedValue may also need `Autodesk.AutoCAD.DatabaseServices` (inference).

### Transactions: the pattern every sample uses [AUTO]
```
Document acDoc = Application.DocumentManager.MdiActiveDocument;
Database acCurDb = acDoc.Database;
using (Transaction acTrans = acCurDb.TransactionManager.StartTransaction())
{
    BlockTable bt = acTrans.GetObject(acCurDb.BlockTableId, OpenMode.ForRead) as BlockTable;
    BlockTableRecord ms = acTrans.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite) as BlockTableRecord;
    ms.AppendEntity(ent);
    acTrans.AddNewlyCreatedDBObject(ent, true);
    acTrans.Commit();
}
```
([G:F98FAC6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F98FAC6B-4DC4-489E-B65E-5D8C5E64E534), [G:33058D80](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33058D80-EA6B-4A19-9F07-F20BC5EBC530), [G:A2CD7540](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A2CD7540-69C5-4085-BCE8-2A8ACE16BFDD), [G:90D867AA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-90D867AA-6513-4F0C-A498-7453FEA4FEC3))
- Open with `acTrans.GetObject(id, OpenMode.ForRead)`; to change an object open it again with `OpenMode.ForWrite` (upgrade). ([G:31193942](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31193942-2AEB-4BFF-A861-6279EE8394A2), [G:076B6391](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-076B6391-F375-454E-BFB2-533BDCA9E23D))
- No `Commit()` = nothing kept (inference: every writing sample commits; read-only samples call `Abort()` or just dispose). ([G:076B6391](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-076B6391-F375-454E-BFB2-533BDCA9E23D), [G:5FA86EF3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5FA86EF3-DEFD-4256-BB1C-56DAC32BD868))
- New entity: `AppendEntity` on a BlockTableRecord, then `AddNewlyCreatedDBObject(obj, true)`. New symbol table record: `table.Add(rec)` then AddNewlyCreatedDBObject. New dictionary entry: `dict.SetAt(key, obj)` then AddNewlyCreatedDBObject. ([G:1ECA7D76](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1ECA7D76-EF28-43E3-A22B-CC2906270A73), [G:31193942](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-31193942-2AEB-4BFF-A861-6279EE8394A2), [G:C6DA4EF7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C6DA4EF7-1DFE-4D7A-A55D-62EA06E44997))
- Paper space target: `bt[BlockTableRecord.PaperSpace]`. Walk a space: `foreach (ObjectId id in btr)`; `id.ObjectClass.DxfName` gives the DXF class name. ([G:034504F8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-034504F8-59F8-4D6D-8777-3EF8A9C251DF), [G:61C22902](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-61C22902-F63B-4204-86EC-FA37312D1B6E))
- A drawing has exactly NINE symbol tables; you cannot add a table. Dictionaries can be added to the named object dictionary (NOD) but cannot hold entities. ([G:7313ECA1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7313ECA1-4875-4946-82E3-C06A4074F807))
- `table.Has("Name")` tests existence; `table["Name"]` returns the ObjectId. Use the `Purge` method to test whether a layer, block or style can be erased; after `Erase()` do not use the object again. ([G:F98FAC6B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F98FAC6B-4DC4-489E-B65E-5D8C5E64E534), [G:A4927721](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A4927721-5F7E-4FC7-9A00-E6BD1609F7B8))
- An entity created in memory and never added to a database must be disposed (`using`). ([G:B931C746](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B931C746-6FCF-4E89-9C71-62C2C0C86A9A))
- Transactions can be nested; commit or abort each. ([G:A43A20B7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A43A20B7-A73A-4BBC-B871-B8E6B9D1006C))
- Attach an xref: `ObjectId id = db.AttachXref("c:/clients/Proj 123/grid.dwg", "grid");` (forward slashes; block name from `Path.GetFileNameWithoutExtension`). ([G:034504F8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-034504F8-59F8-4D6D-8777-3EF8A9C251DF))
- ObjectARX tip: remove the pickfirst set before aborting a transaction (transactions + UNDO + Object Property Toolbar can destabilize AutoCAD): `acedSSSetFirst(NULL, NULL);` then abort. ([G:01354898](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-01354898-965C-4340-9A39-607B56DAB888))

### Document locking ([G:A2CD7540](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A2CD7540-69C5-4085-BCE8-2A8ACE16BFDD)) [AUTO]
- You must lock a document before changing it when your code: (1) runs from a modeless dialog; (2) touches a loaded document that is NOT the current one; (3) runs as a COM server; (4) is a command registered with `CommandFlags.Session`. Without the lock: lock violation.
- A normal (non-Session) command changing the CURRENT document needs no lock.
- `using (DocumentLock l = doc.LockDocument()) { ... }`. Unlock = Dispose or end of the `using`. The text says the method is on the Database; the sample calls it on the Document.
- Sample LockDoc (`CommandFlags.Session`): `Application.DocumentManager.Add("acad.dwt")`, lock the new doc, add a Circle in its Model space, Commit, then after the lock block `DocumentManager.MdiActiveDocument = newDoc`.
- Fiberless rule (13.12): a document switch happens only after all commands and LISP in the old document end; code that asks for a switch must RETURN. ([G:7752BA67](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7752BA67-A0F3-4775-8BB8-632E6FC8558F))

### Sending commands from .NET ([G:F4A36181](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F4A36181-39FB-4923-A2AF-3333945DB289), [G:33058D80](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33058D80-EA6B-4A19-9F07-F20BC5EBC530), [G:A1309D38](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A1309D38-A432-487C-B890-6666B891C701)) [AUTO]
- `Document.SendStringToExecute(string, true, false, false)` sends ONE string: command plus answers in prompt order. A space or carriage return = Enter. End the string with a space.
- It is ASYNCHRONOUS: nothing runs until the current .NET command ends.
- Synchronous routes listed by Autodesk: COM `SendCommand` (via interop); P/Invoke `acedCommand` / `acedCmd` (native and ObjectARX/.NET commands); P/Invoke `acedInvoke` (commands defined in AutoLISP). In fiberless AutoCAD, legacy acedCommand fails; see 13.12.
- Doc samples: `acDoc.SendStringToExecute("._circle 2,2,0 4 ", true, false, false);` and `acDoc.SendStringToExecute("._zoom _all ", true, false, false);`. The three booleans are not explained on the page. A leading period reaches the built-in even if it was UNDEFINEd ([G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B)); the underscore is not explained in these pages.
- `acDoc.Editor.Command("_-RENDERPRESETS", "_custom", "mypreset");` appears in a 2027 sample, called after the transaction closed. Its sync behavior is not described here. ([G:A1309D38](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A1309D38-A432-487C-B890-6666B891C701))
- Calling `SendStringToExecute` with no argument is invalid. ([G:F4A36181](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F4A36181-39FB-4923-A2AF-3333945DB289))

### Prompting for input ([G:41E19C3B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-41E19C3B-B40A-41EC-88CB-347B1161B74A), [G:3D998905](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3D998905-0C24-4FF9-A9C7-7F361A591B80), [G:DF40DD82](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DF40DD82-FD27-43C5-B7D2-E75646B2E47E), [G:33058D80](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33058D80-EA6B-4A19-9F07-F20BC5EBC530), [G:203F2756](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-203F2756-1BA6-4226-A505-B776ED8AF0FB))
- The Editor's Get methods (GetPoint, GetString, GetInteger, GetDistance, GetKeywords, GetEntity...) show a prompt and WAIT. Each returns a result with `Status` and `Value`/`StringResult`. Prefix prompts with `\n`. (inference: in a driven session the answers must come from the command stream.)
- Test `Status` before reading `Value` (PromptStatus.Cancel, PromptStatus.Keyword, OK). One doc sample reads Value first; do not copy that. ([G:B931C746](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B931C746-6FCF-4E89-9C71-62C2C0C86A9A), [G:33058D80](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33058D80-EA6B-4A19-9F07-F20BC5EBC530))
- Keywords: `opts.Keywords.Add("Big")`. The underscore `_` cannot be a keyword or part of one. AllowNone = false forces a keyword; to accept Enter set `Keywords.Default` and `AllowNone = true`. ([G:DF40DD82](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DF40DD82-FD27-43C5-B7D2-E75646B2E47E), [G:3D998905](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3D998905-0C24-4FF9-A9C7-7F361A591B80))
- PromptIntegerOptions: AllowZero, AllowNegative. PromptStringOptions.AllowSpaces = true: Space types a space and only Enter ends input. PromptPointOptions: UseBasePoint, BasePoint (rubber band). ([G:3D998905](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3D998905-0C24-4FF9-A9C7-7F361A591B80), [G:203F2756](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-203F2756-1BA6-4226-A505-B776ED8AF0FB), [G:33058D80](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33058D80-EA6B-4A19-9F07-F20BC5EBC530))
- Snap and grid do NOT affect points passed through the API; they only affect points a user picks. Scripted coordinates are exact. ([G:A588F7CE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A588F7CE-C810-49CB-B88A-00B416B9956B))

### Things that block an unattended run
- Never call `Form.ShowDialog` in an AutoCAD extension. Use `Application.ShowModalDialog` or `ShowModelessDialog`. ([G:7AE1E920](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7AE1E920-2F7F-497B-A6C3-FB22987974B6))
- `Application.ShowAlertDialog(...)` and `System.Windows.Forms.MessageBox.Show(...)` are modal; many doc samples use them, often inside `catch`. Replace with `Editor.WriteMessage("\n...")` or a log file for headless use (inference). ([G:6C52F8BC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6C52F8BC-B107-4EE4-BA25-5B74900B271A), [G:CBB74093](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CBB74093-BB22-49CC-B54A-D33D7E92694C), [G:728723FC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-728723FC-E8A3-4001-83CF-D728E9DB419C), [G:CB7D7DC2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB7D7DC2-C8C1-4EF9-A638-C4C6184BFC85), [G:56BD3247](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-56BD3247-471C-4471-A238-FFDFDC3BD2E4))
- An unhandled .NET exception shows the default error message and ends the application. Try-Finally still shows that box and waits for Continue. Use Try-Catch(-Finally). ([G:06DF188F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-06DF188F-C832-4406-93E7-99F008B9F124), [G:A8D1137E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A8D1137E-9283-4F1D-9B3E-89B90E5AA5A6))
- `PlotProgressDialog` (13.11) is a GUI dialog.
- Every Get* prompt waits for input (above).
- NETLOAD with FILEDIA = 1 opens a file dialog (13.9).

### Settings and system variables from .NET [AUTO]
- System variables: `Application.SetSystemVariable("MAXSORT", 100);` and `System.Convert.ToInt32(Application.GetSystemVariable("MAXSORT"))` (the return value is loosely typed; convert it). ([G:F6B3122D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F6B3122D-A6F4-4112-A838-4662E0E1B30B))
- Options-dialog settings have NO .NET classes. Use COM: `AcadPreferences prefs = (AcadPreferences)Application.Preferences;` with sub-objects Display, Drafting, Files, OpenSave, Output, Profile, Selection, System, User (PreferencesDisplay ... PreferencesUser). Example: `prefs.Display.CursorSize = 100;`. ([G:7E1AC51A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7E1AC51A-CDD6-4CD5-8703-3D3A472BFFC5), [G:4213EB7F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4213EB7F-C21F-4361-BF12-176F897F44C8))
- Drawing-based options live in the DWG: use the Database property or Get/SetSystemVariable. ([G:8BFCB4E3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8BFCB4E3-E67E-4689-8F31-74C44C2D3A97))
- Ortho lives in the Database: `db.Orthomode = true`. Grid and snap live in the ACTIVE viewport: open `Editor.ActiveViewportId` ForWrite as ViewportTableRecord, set `GridEnabled`, `GridIncrements`, `SnapEnabled`, `SnapIncrements`, `SnapBase`, `SnapAngle` (radians), then `Editor.UpdateTiledViewportsFromDatabase()` and Commit. ([G:65FBB486](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-65FBB486-54C8-4746-8834-99524F9F23D3), [G:A588F7CE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A588F7CE-C810-49CB-B88A-00B416B9956B))
- The .NET API has no polar-point and no coordinate-system translation method. Use COM `Utility.PolarPoint` / `TranslateCoordinates`, or do the math (X + d cos a, Y + d sin a; radians). ([G:9825A799](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9825A799-D48C-4E72-A7EB-6200AE5F452E))
- Useful variables: DBMOD (0 = no unsaved changes), DWGTITLED (0 = still Drawing1 style name), CVPORT (current viewport number). ([G:A73E66C5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A73E66C5-AE7F-4142-9160-705C04552C4A), [G:CBB74093](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CBB74093-BB22-49CC-B54A-D33D7E92694C), [G:2CEED409](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2CEED409-0E15-4F48-9AA1-D12D246E27DB))
- Application object properties: DocumentManager, DocumentWindowCollection, MainWindow, MenuBar (COM), MenuGroups (COM, one group per loaded CUIx), Preferences (COM), Publisher, StatusBar, UserConfigurationManager (profiles), InfoCenter, AcadApplication. ([G:06F95957](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-06F95957-9A08-4036-BFB6-541C5B5F3A15))
- Hide or show AutoCAD while code runs: `Application.MainWindow.Visible = false;` / `true`; `Application.MainWindow.WindowState = Window.State.Minimized;` (Autodesk.AutoCAD.Windows). Position and size samples need a PresentationCore reference. ([G:6C52F8BC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6C52F8BC-B107-4EE4-BA25-5B74900B271A))
- Areas: the `Area` property works on Curve-derived entities (arc, circle, ellipse, polylines, region, hatch, closed planar spline). ([G:B931C746](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B931C746-6FCF-4E89-9C71-62C2C0C86A9A))

### Display and views
- The API does not redraw after each call. Refresh with `Application.UpdateScreen()`, `Editor.UpdateScreen()`, or `Editor.Regen()`. After changing tiled viewports or snap/grid call `Editor.UpdateTiledViewportsFromDatabase()`. ([G:4271D259](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4271D259-52E6-42B2-8F2B-7219186CE115), [G:A588F7CE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A588F7CE-C810-49CB-B88A-00B416B9956B))
- NO zoom or pan method exists. Get `Editor.GetCurrentView()` (a ViewTableRecord), set `CenterPoint`, `Height`, `Width` (DCS), `Target`, `ViewDirection` (WCS), `ViewTwist` (radians), then `Editor.SetCurrentView(view)`. Bounds come from `db.Extmin/Extmax` (Model), `Pextmin/Pextmax` (current layout), `Limmin/Limmax`. ([G:FAC1A5EB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FAC1A5EB-2D9E-497B-8FD9-E11D2FF87B93), [G:70B3140A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-70B3140A-14F1-4F54-AF5F-8DEDB444C3BA))
- Simpler for extents: `SendStringToExecute("._zoom _all ", ...)` as in [G:33058D80](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-33058D80-EA6B-4A19-9F07-F20BC5EBC530) (runs after the command ends).
- Doc Zoom helper `Zoom(Point3d pMin, Point3d pMax, Point3d pCenter, double dFactor)` treats an all-zero point as "not given" (inference: a center at 0,0,0 cannot be requested). ZoomExtents uses factor 1.01075. The ZoomScale text says 50% smaller but its code doubles the view size. ([G:FAC1A5EB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-FAC1A5EB-2D9E-497B-8FD9-E11D2FF87B93), [G:70B3140A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-70B3140A-14F1-4F54-AF5F-8DEDB444C3BA), [G:25131FDB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25131FDB-7C20-44C1-B3F2-BACD27F7C116))
- Named views: ViewTable `Add` + `Editor.SetCurrentView(rec)`; names up to 255 characters of letters, digits, `$`, `-`, `_`. ([G:076B6391](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-076B6391-F375-454E-BFB2-533BDCA9E23D))
- Tiled viewports: ViewportTable records; every displayed tiled viewport is named `*Active` (duplicate names allowed only here). Make one current: `Application.SetSystemVariable("CVPORT", rec.Number)`. Corners run (0,0) to (1,1). ([G:E066A548](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E066A548-6A42-4F23-ADD2-EE8DA239139A), [G:2CEED409](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2CEED409-0E15-4F48-9AA1-D12D246E27DB), [G:728723FC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-728723FC-E8A3-4001-83CF-D728E9DB419C))

### Drawings: new, open, save, close ([G:330A8DCB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-330A8DCB-626F-4271-8B89-9773A7631D87), [G:CBB74093](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CBB74093-BB22-49CC-B54A-D33D7E92694C), [G:A73E66C5](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A73E66C5-AE7F-4142-9160-705C04552C4A)) [AUTO]
- New: `Document d = Application.DocumentManager.Add("acad.dwt"); Application.DocumentManager.MdiActiveDocument = d;` If the template is missing, defaults are used. The new doc is not active until MdiActiveDocument is set. Sample command uses `CommandFlags.Session`.
- Open: `Application.DocumentManager.Open(path, false);` after `File.Exists(path)`. The second argument is not explained. Session flag again.
- Save: `doc.Database.SaveAs(path, true, DwgVersion.Current, doc.Database.SecurityParameters);` The bool `bBakAndRename` renames the database and the old file to a backup.
- Close: `Document.CloseAndDiscard`, `Document.CloseAndSave`, `DocumentCollectionExtension.CloseAll` (no signatures on the page).
- DWG files can no longer be saved with a password (2016 and later); password data passed to saveAs is ignored and returns an error. ([G:46A2AD05](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-46A2AD05-210A-4C5E-BA6F-71B542CC197A))
- Side database (no window): `using (Database db = new Database(false, true)) { db.ReadDwgFile(path, FileOpenMode.OpenForReadAndAllShare, true, ""); ... }`. Another sample uses `ReadDwgFile(path, System.IO.FileShare.None, false, "")`. A missing file throws eFileNotFound. Dispose the database when done. ([G:5FA86EF3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5FA86EF3-DEFD-4256-BB1C-56DAC32BD868), [G:A8D1137E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A8D1137E-9283-4F1D-9B3E-89B90E5AA5A6))
- Zero-document state: all drawings can be closed; there is then NO command line, so open or create a drawing first. `DocumentDestroyed` fires per close; `DocumentManager.Count` reads 1 inside the handler when the last one closes. ([G:CB7D7DC2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CB7D7DC2-C8C1-4EF9-A638-C4C6184BFC85))
- New Tab page (2015+): `Application.DocumentManager.MdiActiveDocument` is NULL while it is active. Null-check before touching the drawing. ([G:7438B913](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7438B913-0E2A-4BA6-A2B7-0AF66C1621DC))

### Errors, threads, security
- Catch `Autodesk.AutoCAD.Runtime.Exception` (every sample fully qualifies it). Members: `ErrorStatus` (enum `Autodesk.AutoCAD.Runtime.ErrorStatus`), `Message`, `Source`, `StackTrace`, `TargetSite`. ([G:D93FC79E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D93FC79E-B78B-4D41-A16B-C7BFFB59FD1F), [G:A8D1137E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A8D1137E-9283-4F1D-9B3E-89B90E5AA5A6))
- Add error handling around user input, file I/O and every database or object access; most doc samples omit it. ([G:06DF188F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-06DF188F-C832-4406-93E7-99F008B9F124), [G:577EDC34](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-577EDC34-0A10-4D63-BED4-ECA4570355A3))
- ObjectARX does NOT support multi-threaded programming: only one thread at a time may call into it. ([G:01354898](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-01354898-965C-4340-9A39-607B56DAB888)) The MEP managed API help class pages also say instance members are not guaranteed thread-safe. (AecbPipeBaseMgd help: Autodesk.Aec.Building.Piping.DatabaseServices.Pipe)
- Autodesk security checklist: compile with `/WARNASERROR`; digitally sign every executable (DLL, EXE, JS); validate all input; HTTPS for network calls; keep libraries current; check memory leaks; test with LEGACYCODESEARCH = 0 and SECURELOAD = 1. ([G:C3E22BC9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C3E22BC9-5703-4F7A-AFFA-D9FE9B39E1BA))

## 13.11 Plotting and publishing from .NET; layouts, viewports, visual styles

### Layouts ([G:5FA86EF3](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5FA86EF3-DEFD-4256-BB1C-56DAC32BD868), [G:BEF5FDEE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BEF5FDEE-925E-4E28-86E1-9B4A2CADD355), [G:0071C84E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0071C84E-1BC0-4AB0-848A-FE4CAF9472CB))
- Model space is the one layout named "Model"; it cannot be renamed and there cannot be a second. Paper space layouts: many, renamable.
- `*MODEL_SPACE` block record = Model geometry. `*PAPER_SPACE` = the LAST ACTIVE paper space layout.
- Each Layout has exactly one BlockTableRecord: `Layout.BlockTableRecordId` and `BlockTableRecord.LayoutId`; `BlockTableRecord.IsLayout`.
- Current drawing: `LayoutManager.Current` (`CreateLayout(name)` returns an ObjectId; `CurrentLayout` get/set; `GetLayoutId(name)`). Other drawings: the layout dictionary `db.LayoutDictionaryId`.
- Most output settings on a Layout are READ-ONLY. Change them through a PlotSettings copy and PlotSettingsValidator, then `layout.CopyFrom(ps)` with the layout open ForWrite.
- ImportLayout sample: read the other DWG into `new Database(false, true)`, make a `*Paper_Space<n>` block record, `WblockCloneObjects(..., DuplicateRecordCloning.Ignore, false)`, new `Layout` + `AddToLayoutDictionary`, `CopyFrom`; copy its named page setup; `Editor.Regen()` so the tab shows; abort the external transaction and Dispose the external database.

### Page setups and validator ([G:56BD3247](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-56BD3247-471C-4471-A238-FFDFDC3BD2E4), [G:9B330DCF](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9B330DCF-6A4E-4C58-B5C1-085E34912077), [G:946669A9](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-946669A9-E813-4D12-828A-44986E388AA2), [G:9F7F854D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9F7F854D-5172-4F42-A6C5-E7E54DF6E0B6), [G:96E2EFD0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-96E2EFD0-B16B-4A3A-BA6A-A9277BBB3610), [G:723C62A6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-723C62A6-04CD-4C25-865A-0A05B3B69903)) [AUTO]
- Layout derives from PlotSettings. A PlotSettings object in `db.PlotSettingsDictionaryId` = a named page setup.
- Change the current layout to PDF (doc sample): `using (PlotSettings ps = new PlotSettings(layout.ModelType)) { ps.CopyFrom(layout); PlotSettingsValidator v = PlotSettingsValidator.Current; v.SetPlotConfigurationName(ps, "DWG To PDF.pc3", "ANSI_B_(11.00_x_17.00_Inches)"); v.SetZoomToPaperOnUpdate(ps, true); layout open ForWrite; layout.CopyFrom(ps); }` then Commit and `Editor.Regen()`.
- Validator setters: SetPlotConfigurationName, SetPlotType, SetPlotWindowArea, SetPlotViewName, SetPlotOrigin, SetPlotCentered, SetUseStandardScale, SetStdScaleType (`StdScaleType.ScaleToFit`), SetPlotPaperUnits (`PlotPaperUnit.Inches`), SetPlotRotation (`PlotRotation.Degrees000`), SetCurrentStyleSheet, SetZoomToPaperOnUpdate.
- RULE: call `v.RefreshLists(ps)` BEFORE setting the plot style table.
- Direct properties: ScaleLineweights, ShowPlotStyles, PlotPlotStyles, PrintLineweights, PlotTransparency, DrawViewportsFirst, ShadePlot, ShadePlotResLevel, PlotHidden (named layouts only).
- Style sheet: sample uses `"acad.ctb"` when `db.PlotStyleMode` is true, else `"acad.stb"` (inference: true = color-dependent).
- PlotType: Display (not from Paper space), Extents, Limits, View (PlotViewName), Window (PlotWindowArea), Layout (not from Model space). New paper space layouts default to Layout.
- Lists: `GetPlotDeviceList()`, `GetCanonicalMediaNameList(ps)`, `GetLocaleMediaName(ps, i)`, `GetPlotStyleSheetList()`. Unknown device name = silent fallback to the default device. PlotPaperUnits: Inches, Millimeters, Pixels.

### Plotting with PlotEngine ([G:CE91C625](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CE91C625-A278-4445-8219-3A2D880E6C22), [G:6E0B1F7B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6E0B1F7B-7B0E-4E3E-B1FD-018E0A3673BE), [G:C8AF82C4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8AF82C4-FF10-42B9-A99F-79DC3D8CEF51)) [AUTO]
- Set BACKGROUNDPLOT = 0 for foreground plotting. ([G:CE91C625](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CE91C625-A278-4445-8219-3A2D880E6C22))
- Objects: PlotFactory, PlotEngine, PlotInfo, PlotSettings, PlotSettingsValidator, PlotInfoValidator, PlotPageInfo (namespace `Autodesk.AutoCAD.PlottingServices`). A PlotEngine can plot to a file, to a device, or show a preview.
- Model space defaults when nothing is set: system printer, current display, scaled to fit, rotation 0, offset 0,0.
- Flow: PlotSettings, validate, PlotInfo, PlotEngine. Doc sample PlotLayout (plots current layout extents to a DWF file):
  1. Open the current Layout ForRead (`LayoutManager.Current.GetLayoutId(LayoutManager.Current.CurrentLayout)`).
  2. `using (PlotInfo pi = new PlotInfo()) { pi.Layout = layout.ObjectId;`
  3. `using (PlotSettings ps = new PlotSettings(layout.ModelType)) { ps.CopyFrom(layout);` then validator: SetPlotType(Extents), SetUseStandardScale(true), SetStdScaleType(ScaleToFit), SetPlotCentered(true), SetPlotConfigurationName(ps, "DWF6 ePlot.pc3", "ANSI_A_(8.50_x_11.00_Inches)").
  4. `pi.OverrideSettings = ps;` (an override: NOT saved back to the layout).
  5. `PlotInfoValidator piv`; `piv.MediaMatchingPolicy = MatchingPolicy.MatchEnabled; piv.Validate(pi);`
  6. Guard: only if `PlotFactory.ProcessPlotState == ProcessPlotState.NotPlotting`.
  7. `using (PlotEngine pe = PlotFactory.CreatePublishEngine())` and `using (PlotProgressDialog dlg = new PlotProgressDialog(false, 1, true))` [GUI progress dialog].
  8. `pe.BeginPlot(dlg, null); pe.BeginDocument(pi, acDoc.Name, null, 1, true, "c:\\myplot");` (args not explained; inference: 1 copy, true = plot to file, last = output file).
  9. `pe.BeginPage(new PlotPageInfo(), pi, true, null); pe.BeginGenerateGraphics(null); pe.EndGenerateGraphics(null); pe.EndPage(null); pe.EndDocument(null); pe.EndPlot(null);` with dlg OnBegin/OnEnd calls around sheet and plot.
- Paper space layouts plot the same way, but the layout must be initialized and its viewports defined first. ([G:C8AF82C4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8AF82C4-FF10-42B9-A99F-79DC3D8CEF51))

### Publishing to one multi-sheet PDF ([G:B08B5173](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B08B5173-0C17-4663-BD1C-A40E4C8F3A75)) [AUTO]
- Build one `DsdEntry` per layout: `DwgName` (full path), `Layout`, `Title`, `Nps` (page setup override, "" = none), `NpsSourceDwg`. Add to a `DsdEntryCollection`.
- `DsdData`: `SetDsdEntryCollection(coll)`, `DestinationName` (output PDF), `ProjectPath` (folder), `SheetType = SheetType.MultiPdf`, `LogFilePath`. `WriteDsd(path)` writes a DSD usable by the PUBLISH command; `ReadDsd(path)` reads one.
- Publish: `PlotConfig cfg = PlotConfigManager.SetCurrentConfig("DWG to PDF.PC3"); Application.Publisher.PublishExecute(dsdData, cfg);` (device override for all layouts). `PublishDsd` uses each layout's own settings or the entry's page setup.
- Set BACKGROUNDPLOT = 0 before publishing a DSD with PublishDsd; the sample notes PublishExecute honors BACKGROUNDPLOT. All Dsd objects are IDisposable.

### Paper space viewports ([G:61C22902](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-61C22902-F63B-4204-86EC-FA37312D1B6E), [G:F0906774](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F0906774-90AD-4AD2-9894-E37ACEF8035A), [G:8036F643](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8036F643-0186-4075-B35C-5331956FBE07), [G:4A177301](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4A177301-1624-45F5-97E9-8832E484B0FB), [G:30161103](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30161103-5E6B-453D-B1F5-2DBBBB03BDF0)) [AUTO]
- Create: open `bt[BlockTableRecord.PaperSpace]` ForWrite; `Application.SetSystemVariable("TILEMODE", 0); acDoc.Editor.SwitchToPaperSpace();`; `using (Viewport vp = new Viewport())` (no constructor arguments): `CenterPoint`, `Width`, `Height`; `AppendEntity`; `AddNewlyCreatedDBObject`; then `ViewDirection`; `On = true`.
- RULE: to set view properties (ViewDirection, LensLength...) `On` must be FALSE; to make a viewport current `On` must be TRUE. At least one viewport must be On before switching to model space on a layout.
- Making a viewport current has no managed call in the docs; the sample P/Invokes `acedSetCurrentVPort` from `acad.exe` with a mangled EntryPoint `"?acedSetCurrentVPort@@YA?AW4ErrorStatus@Acad@@PBVAcDbViewport@@@Z"` after `Editor.SwitchToModelSpace()`. (inference: acad.exe exports are not available in the Core Console; and the name has `PBV` where the 64-bit mangling example on [G:19D96E61](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-19D96E61-64D1-4BB4-9BB3-B74BFC34A771) carries an `E`, so it may not resolve on 64-bit AutoCAD. Test before use.)
- View content: `ViewCenter`, `ViewDirection`, `ViewHeight`, `ViewTarget`. Other: `Layer`, `Linetype`, `LinetypeScale`, `Locked`, `GridOn`, `LensLength`.
- Clip to a shape: append a Circle (or other closed entity) to paper space, then `NonRectClipEntityId = circle.ObjectId; NonRectClipOn = true;`.
- Which space: TILEMODE 1 = Model tab. TILEMODE 0 and CVPORT 2 = inside a floating viewport. TILEMODE 0 and CVPORT not 2 = paper space. Switch with `Editor.SwitchToModelSpace()` / `SwitchToPaperSpace()`. (inference: with several viewports the active one may not be number 2; test.)
- SCALE CONFLICT: the scale page defines `CustomScale` as paper:model, so 1:4 = 0.25 (source checked). The viewport samples set `CustomScale = 48` for "1 in = 4 ft" and `96` for "1 in = 8 ft". By the definition, 1/4" = 1'-0" would be 1/48 = 0.0208333. Test on a real viewport before trusting either. `StandardScale` takes a `StandardScaleType` value. The four-viewport sample text claims 1:2 but sets no scale.
- PSLTSCALE keeps linetype scaling uniform across viewport scales; set with SetSystemVariable (values not listed). ([G:30161103](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30161103-5E6B-453D-B1F5-2DBBBB03BDF0))

### Shaded viewports, visual styles, render presets ([G:32466B8D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-32466B8D-60A0-4964-90D8-01C4B6A48FB8), [G:C6DA4EF7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C6DA4EF7-1DFE-4D7A-A55D-62EA06E44997), [G:A1309D38](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A1309D38-A432-487C-B890-6666B891C701))
- `vp.SetShadePlot(ShadePlotType.VisualStyle, visualStyleId)` or `(ShadePlotType.RenderPreset, presetId)`; `ShadePlot` property; `HiddenLinesRemoved` bool. `Layout.ShadePlot` overrides every viewport on that layout; `ShadePlotResLevel` sets quality.
- Visual styles: `db.VisualStyleDictionaryId`, `DBVisualStyle`. All styles can be customized, so a drawing may lack the template styles ("Sketchy" is used in a sample). Skip entries with `InternalUseOnly == true`. Change with `SetTrait(VisualStyleProperty.X, value, VisualStyleOperation.Set)`. The sample adds flag values with `+` (inference: use bitwise OR).
- Render presets (RapidRT since 2016): NOD key `ACAD_RENDER_RAPIDRT_SETTINGS` holds `RapidRTRenderSettings`; `ACAD_RENDER_PLOT_SETTINGS` holds copies assigned to viewports or PlotSettings. Standard presets (Low, Medium, High, Coffee-Break Quality, Lunch Quality, Overnight Quality) cannot be modified. Make one current by command: `acDoc.Editor.Command("_-RENDERPRESETS", "_custom", "mypreset");`. Legacy MentalRay (`ACAD_RENDER_SETTINGS`) kept for backward compatibility only.
- Sample order: set `Locked` and scale before AppendEntity, `ViewDirection` after, `On = true` last; finish with `db.TileMode = false` to show the last layout.

## 13.12 Migration by release; ObjectARX readme facts

### AutoCAD 2027 release notes ([G:4DA730AB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4DA730AB-7A47-4663-838B-21E71438D6C8), [G:83DA77DD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83DA77DD-6599-48B2-B965-43ABC3E285F0)) [AUTO]
- ObjectARX: 2027 BREAKS binary compatibility with 2025 and 2026. Native apps built for 2026 or earlier must be relinked against the new LIB files (`*26.lib`, e.g. `acui26.lib`) and recompiled. A 2026 .arx/.dbx cannot just be copied over.
- Managed .NET: target .NET 10.0 (was .NET 8.0 LTS for 2025 and 2026). Install the .NET 10.0 SDK before migrating. Projects never moved to .NET 8 also need `<FrameworkReference Include="Microsoft.WindowsDesktop.App"></FrameworkReference>` inside the CSPROJ/VBPROJ ItemGroup.
- Tools: Visual Studio 2026 version 18.0 with VC tools 14.44.35207 for ObjectARX. Anything .NET must target 10.0. VS 2022 17.14 can build ObjectARX for 2027 but CANNOT build managed .NET apps.
- Registry key changed from R25.1 to R26.0.
- Tool palettes: call `Clipboard.Clear()` before `ToolPaletteManager.Manager.LoadCatalogs()` (sample clears only if a clipboard format contains "ACTC"). (inference: Clipboard needs an STA thread.)
- 2027 API changes (Feature Completeness): new native functions (hatch swatch preview, path parsing, layout thumbnail check, substitute font file, underlay load check, highlight properties, last character of a string, Identity/origin for Geometry 2D/3D point, scale, vector). REMOVED: AcGiContext2 (merged into AcGiContext), deprecated color-class functions, the `*` operator on several Geometry classes, other deprecated members; some signatures now use standard data types. Managed: libraries moved from .NET 8 to .NET 10; new members to compare the runtime ID of two databases and get a database hash code; new classes to check whether the Revcloud and Viewport Layer controls are on the ribbon; removed the function that told whether the drawing is being regenerated for a PostScript file.
- Full per-member lists are not in these inputs: see "What's New and Migration Guide" in arxmgd.chm / arxref.chm (ObjectARX SDK docs folder). ([G:A6C680F2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A6C680F2-DE2E-418A-A182-E4884073338A), [G:C21B8F00](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C21B8F00-C7DE-4E44-8006-D5DC99199F31))

### Changes by release (ObjectARX Migration Guide)
- 2026+ (Windows): stop including `banned.h`; MSVC headers do that job now. ([G:5AB371AA](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5AB371AA-7CFC-4C53-9269-044092799DDD))
- 2025+: `AcString` can no longer be passed to printf-style variadic functions; pass `str.constPtr()`. clang message "cannot pass object of non-trivial type 'AcString' through variadic function, call will abort at runtime" means a real crash. ([G:BB220CEE](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BB220CEE-569D-4F3E-8AD5-56B595DF52E4))
- 2024+: `acgi.h` no longer includes `dbpl.h` or `dbmain.h`; add the includes yourself. `AcCmColor` moved to `AcCmColor.h` (dbmain.h still includes it). ([G:58156321](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-58156321-FFA1-4465-AC3E-7359B39A57D4), [G:BC89C009](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BC89C009-9650-49F0-8282-2105B626AA2D))
- 2023+: from `dbmain.h`, `acutAcStringToAChar()` and `acutGetAcStringConvertToAChar()` moved to `acutacstring.h`; `AcDbObject` and `acdbOpenObject()` moved to `dbObject.h`. ([G:80BC29E8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-80BC29E8-F5E8-4829-A561-610C18695036))
- 2022 Update 1 and 2: AcGiContext vtable shift (`forceUseFillTrait()`) can break apps built for 2022; install the latest 2022 update. Not an SDK binary-compatibility issue. ([G:5CC63E05](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5CC63E05-C462-405C-B040-7B55C5A5586C))
- 2021+: `AsdkHlrApi<version>.dbx` ships with the product; stop distributing it. 3D modeler classes (AcDbBody, AcDb3dSolid...) moved to `AcGeomentObj.dbx` (spelling as printed); RealDWG apps load it with `acrxLoadModule(L"AcGeomentObj.dbx", false);`. ([G:C696363D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C696363D-8E40-4F71-A646-4007624EBF92), [G:66193692](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-66193692-6F3E-4E25-8DAC-CDF1E158A4C6))
- 2019+: replace `dbid_ops.h` and `dbidapps.h` with `dbid.h`. ([G:ADD3FEE6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-ADD3FEE6-CD7F-49E2-A7F1-1DE015478EFD))
- 2017+: Windows `Adesk::Boolean` is now `bool`, `Adesk::Int32/UInt32` are `int/unsigned int` (as on Mac). DANGER: `writeItem()/readItem()` on `int`/`BOOL` variables now resolve to Int32 instead of Boolean filing, changing the DWG data with no compiler warning. Test that new builds read old DWGs and old builds read new ones. ([G:E44CD205](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E44CD205-84FF-429F-B132-EE2F51CD5339))
- 2017+: graphics system only through the GS manager; `AcDbDatabase::gsModel()/setGsModel()` obsolete, `AcGiDrawable::gsNode()/setGsNode()` removed; use AcGiDrawableReactor callbacks. ([G:B55BC9C2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B55BC9C2-B39F-4D36-AA65-FC3B52E176E4)) Bitmap icons with an RGB 192,192,192 background no longer supported; use transparent PNG. ([G:0553C079](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0553C079-799A-44BF-A2E9-8830FE8AC505))
- 2016+: DWG password saving removed (saveAs returns an error if password data is passed). Never use the compiler-generated copy constructor or assignment on AcDbObject-derived classes (double delete crash). ([G:46A2AD05](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-46A2AD05-210A-4C5E-BA6F-71B542CC197A), [G:2C5A51E7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2C5A51E7-E83D-47A2-A7B0-AE9479F1DA8C))
- 2015+: the New Tab page is a document with no database: C++ `curDoc()` and .NET `MdiActiveDocument` are null; hide drawing palettes then. ([G:7438B913](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7438B913-0E2A-4BA6-A2B7-0AF66C1621DC)) Visual LISP on 64-bit is fully compatible with 32-bit. ([G:8319439A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8319439A-C945-46ED-A14B-B7237F5FA17D))
- 2014: VBA 6.5 replaced by VBA 7.1 (32 and 64 bit). Autodesk warns VBA will be removed in a future version; port to VB.NET. ([G:C7B47A11](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C7B47A11-8042-4F5D-AC41-3007A001A2D9), [G:8319439A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8319439A-C945-46ED-A14B-B7237F5FA17D))

### 64-bit facts that still matter ([G:7045F2A0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7045F2A0-DBC6-4616-8F5C-D31DE338B649), [G:C7B47A11](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C7B47A11-8042-4F5D-AC41-3007A001A2D9), [G:EC6625F7](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-EC6625F7-4645-4F4F-901A-5D606AC20ED3), [G:1DADB41E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-1DADB41E-39B9-4601-9839-90DF405D12CE), [G:C2CF8478](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C2CF8478-D76A-4A8B-BF7C-E7E3507A4983))
- No 32-bit AutoCAD since 2020. One process cannot mix 32-bit and 64-bit modules; a non-portable piece must run out-of-process.
- .NET binaries are platform independent. LSP needs no change; FAS is platform independent.
- DWG limits unchanged: symbol table records per database limited to 32K; xdata limited to 16 KB per application.
- COM `ObjectID` (IAcadObject, id 0x406) returns through `LONG_PTR*`: treat object IDs as 64-bit in COM clients. [AUTO]
- Native porting rules (polymorphic types `Adesk::IntPtr`, `LongPtr`, `IntDbId`, `GsMarker`; `/Wp64`; no inline assembly on x64; LRESULT is LONG_PTR) only matter when rebuilding very old C++ code. ([G:D212CBF4](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-D212CBF4-CF10-4A76-B9CE-BD5039943C77), [G:B844AE68](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-B844AE68-F1C7-4BAC-8E22-64FA5CB71475), [G:2E138E7C](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2E138E7C-3E7F-4A62-A3BF-0ED76111CD4B), [G:82606BE1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-82606BE1-931E-485B-8A93-BE0681C303B7))

### Tips and Techniques ([G:01354898](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-01354898-965C-4340-9A39-607B56DAB888))
- ObjectARX does not support multi-threading: one thread at a time.
- New registry number per release (major number bumps on API breaks, minor on binary-compatible releases). The ObjectARX/DBX loader reads ONLY the host version's section; demand-load entries must be written for each version. Do not hard-code: use `getUserProductRegistryRootKey()`, `getMachineProductRegistryRootKey()`, `acrxProductKey()`, or `acrxObjectDBXRegistryKey()` (DBX).
- .NET assemblies on a network share do not load by default (special permissions needed).
- `acedCommand()` does not work while handling `AcRx::kLoadDwgMsg`; it works in `kInvkSubr`. To run commands at the start of every drawing, queue LISP with `ads_queueexpr()` inside kLoadDwgMsg only; it runs after S::STARTUP, after your handler returns, in call order. Never call ads_queueexpr anywhere else.
- `AcDbBlockReference::appendAttribute()` returns eIllegalEntityType on derived classes. Call `setOwnerId()` on custom objects. Free strings returned by methods like `getName(char*&)` with `acutDelString()`.
- Opt out of the Customer Involvement Program to avoid crashes under the debugger. LNK4099 warnings about missing PDBs are safe to ignore. Do not use the debug C++ runtime (`#undef _DEBUG` before standard headers). Do not `#define ACAD_OBJID_INLINE_INTERNAL`.
- MFC tabbed dialogs: `CAcUiTabMainDialog` / `CAcUiTabChildDialog` (acui26.lib), not CPropertySheet. Avoid `__declspec(dllimport)` on class definitions.
- Unwanted demand loading of a class's app: open the drawing, do a full save, reload.
- Dimension text and definition points you set may be moved to fit the dimension layout (e.g. DIMFIT = 3).
- Object enablers are no longer hosted by ADN; host them yourself.
- Doc set ([G:9789981B](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-9789981B-2351-4736-A9F1-7B54AAC6A703)): Native Developer's and Reference Guides, Managed (.NET) Developer's and Reference Guides (each reference has a migration section), Interoperability Guide, Migration Guide, Readme.
- Contacts ([G:6E389085](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-6E389085-904C-4CE7-A569-2A72E2D236FB)): ADN https://aps.autodesk.com/adn (members: https://adn.autodesk.io/); https://www.autodesk.com/developautocad; forums https://forums.autodesk.com/t5/autocad/ct-p/8.

### Fiberless AutoCAD: document switching and acedCommand ([G:5D2BF4CD](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5D2BF4CD-2B4D-44F0-A790-623AAB424B60), [G:7752BA67](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-7752BA67-A0F3-4775-8BB8-632E6FC8558F), [G:E4630516](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E4630516-6E06-4B6D-B219-F5BFE0D98A89))
- Old AutoCAD used fibers; current AutoCAD does not. There is one native stack on the main thread, so control transitions that fibers used to do now need code changes. Application context vs document context still exists, but you reach application context by RETURNING out of document-context code.
- `$FIBERWORLD`: 1 = fiber behavior, 0 = fiberless. Current AutoCAD runs fiberless by default.

Document switching (MDI) rules [AUTO]
- You can no longer switch the active document in the middle of a command or LISP expression and switch back to resume.
- A switch (close the active document, open or create one) happens only after ALL commands and LISP in the old document have ended. After asking for a switch your code must RETURN. Input is disabled until the switch completes. Some document-deletion reactor callbacks arrive at different times.
- `ACRX_CMD_SESSION` still means "run in application context", but such commands are delayed if LISP or another command is active. (inference: .NET `CommandFlags.Session` is the managed counterpart, [G:F77E8FE0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F77E8FE0-8034-4704-93BD-F717608F8223).)
- `AcApDocManager::sendStringToExecute(doc, str, bActivate = true, bWrapUpInactiveDoc = false, bEchoString = true)`: with bActivate, activation waits until all commands and LISP end; keyboard, mouse and script input are disabled meanwhile. `setCurDocument(..., activate = true)` and `activateDocument(...)` behave the same way.
- `appContextNewDocument`, `appContextOpenDocument`, `newDocument`, `openDocument`: the new document is not activated until its initialization is complete.
- `appContextCloseDocument` destroys the document at once and will likely crash AutoCAD if the active document is closed with command logic on the stack. Use `closeDocument()`, which queues the close. `executeInApplicationContext` is dangerous with it.
- (inference) .NET code that opens or creates drawings (13.10) follows the same rule: the new document becomes active only after your command returns.

acedCommand migration (native C++) [AUTO]
- Legacy `acedCommand` and `acedCmd` do NOT work in fiberless AutoCAD. The ObjectARX SDK provides replacements; take exact signatures from the SDK and the linked help pages:
  - `acedCommandS` / `acedCmdS`: synchronous, for a COMPLETE command whose tokens you supply in full (the first token starts the command, the last one finishes it). If the tokens run out while the command still waits for input, the command is cancelled and what it already did is not undone. Do not nest modal or transparent commands in it. Prefer this form.
  - `acedCommandC` / `acedCmdC`: coroutine form, for a command that must pause for the user. It queues the tokens, your function must RETURN, and AutoCAD calls your callback later. Keep the callback data alive until then and handle the cancel case (Esc at the pause also cancels your own command).
  - LISP-callable (`acedDefun`) functions that use the coroutine form must detect that they are being re-entered. Test the exact behavior on the target build.
- (inference) The .NET route from Autodesk (P/Invoke `acedCommand`/`acedCmd`, [G:F4A36181](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-F4A36181-39FB-4923-A2AF-3333945DB289)) is the legacy pair that fails fiberless; prefer COM SendCommand or `SendStringToExecute` in .NET.

## 13.13 Core Console: what these sources cover
The sources used for this section (the AutoCAD customization guide, the 2027 Managed .NET Developer's Guide, the ObjectARX Migration Guide and the Release Notes) have NO page about the AutoCAD Core Console. Its command-line switches, exit behavior, supported commands and limits must come from another section of this knowledge base or from a live test. Do not cite this section for them.

What these sources do say that bears on a headless run:
- In a default install (test observation), `accoreconsole.exe` sits in `C:\Program Files\Autodesk\AutoCAD 2027\` next to `acad.exe`, `accoremgd.dll`, `acdbmgd.dll` and `acmgd.dll`.
- CRX = "Console Runtime Extension": like an ARX module but with no user interface. CRX is a trusted-path file type, is signable with SignTool, and loads from bundles like ARX. ([G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691), [G:83590A12](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-83590A12-D545-49CE-B129-4C9D36952792), [G:3C25E517](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3C25E517-8660-4BB7-9447-2310462EF06F))
- `AcCoreMgd.dll` holds the editor, publishing and plotting, and command and LISP-function definitions; `AcMgd.dll` holds the application and user interface. ([G:8657D153](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8657D153-0120-4881-A3C8-E00ED139E0D3)) (inference: a plug-in for the Core Console should reference only AcCoreMgd and AcDbMgd and avoid AcMgd, Application.MainWindow, palettes, ribbon and dialogs. Not stated on these pages; test.)
- Code that P/Invokes `acad.exe` exports (the `acedSetCurrentVPort` sample) cannot resolve in a process that is not acad.exe (inference). ([G:61C22902](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-61C22902-F63B-4204-86EC-FA37312D1B6E))
- Startup LISP and VBA should check the Visible property and do nothing when the process is invisible, because it may be background plotting or publishing. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55))
- Startup switches `/b`, `/t`, `/v`, `/s`, `/c` are documented only for acad.exe. ([G:5510017F](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-5510017F-4656-478F-BD4C-AB6B1998BF55), [G:348D791E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-348D791E-D621-444F-B059-C0C6F97AD69F), [G:A694AB72](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-A694AB72-7EB7-4560-B473-B480C378E457))
- Secure loading still governs any code a headless session loads: SECURELOAD default 1, TRUSTEDPATHS, and `.scr` is a trusted-path type (13.3). (inference: a security prompt in a console session has no one to answer it; keep scripts and DLLs in trusted folders.)
- Every dialog listed in 13.10 ("Things that block an unattended run") must be absent from code meant for the Core Console (inference).
- PGP external commands: not stated whether the Core Console honors them. ([G:4CE44766](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4CE44766-E856-47D4-93E6-D45A3EC6749B))

## 13.14 AutoCAD MEP managed API; AecbPipeBaseMgd classes

### Where the help and the DLLs are
- The MEP managed API help is installed with the product as CHM files: `C:\Program Files\Autodesk\AutoCAD 2027\Help\<name>.chm`. MEP-relevant sets: AecBaseMgd, AecbBldSrvMgd, AecbPipeBaseMgd, AecbHvacBaseMgd, AecbPartBaseMgd, AecbPlumbingBaseMgd, AecbElecBaseMgd.
- GOTCHA: the pages carry a title and copyright header from the AutoCAD MEP 2011 era, although they ship with AutoCAD 2027. (inference: members may have changed since; confirm each member against the real DLL, e.g. in the Visual Studio Object Browser, before relying on it.)
- DLLs (default install, test observation): `C:\Program Files\Autodesk\AutoCAD 2027\ACA\` holds AecBaseMgd.dll, AecbBldSrvMgd.dll, AecbPipeBaseMgd.dll, AecbHvacBaseMgd.dll, AecbPlumbingBaseMgd.dll, AecbElecBaseMgd.dll (and other Aec*Mgd); `...\AutoCAD 2027\MEP\` holds AecbPartBaseMgd.dll and AecbRuntimeCatalogMgd.dll.
- Namespaces by help set (from page names): AecBaseMgd: `Autodesk.Aec`, `Autodesk.Aec.ApplicationServices`, `Autodesk.Aec.DatabaseServices`, `Autodesk.Aec.Geometry`, `Autodesk.Aec.Modeler`. AecbBldSrvMgd: `Autodesk.Aec.Building.ApplicationServices`, `Autodesk.Aec.Building.DatabaseServices`. AecbPartBaseMgd: `Autodesk.Aec.Building.ApplicationServices`. AecbHvacBaseMgd: `Autodesk.Aec.Building.Hvac.ApplicationServices`, `.Hvac.DatabaseServices`. AecbPlumbingBaseMgd: `Autodesk.Aec.Building.Plumbing.ApplicationServices`, `.Plumbing.DatabaseServices`. AecbElecBaseMgd: `Autodesk.Aec.Building.Elec`, `.Elec.ApplicationServices`, `.Elec.DatabaseServices`.
- Thread safety line on every class page: static members safe; instance members not guaranteed thread-safe. (AecbPipeBaseMgd help: Autodesk.Aec.Building.Piping.DatabaseServices.Pipe)
- (inference) A pipe plug-in would reference AecbPipeBaseMgd.dll, AecbBldSrvMgd.dll and AecBaseMgd.dll besides AcCoreMgd, AcDbMgd and AcMgd, all with Copy Local = No. These inputs do not state it.

### AecbPipeBaseMgd (assembly AecbPipeBaseMgd.dll): namespaces and classes
`Autodesk.Aec.Building.Piping.ApplicationServices` (AecbPipeBaseMgd help: Autodesk.Aec.Building.Piping.ApplicationServices)
- `PipeDBVariables` : BuildingCommonDBVariables. Drawing-level pipe settings; has a static `GetInstance`.

`Autodesk.Aec.Building.Piping.DatabaseServices` (AecbPipeBaseMgd help: Autodesk.Aec.Building.Piping.DatabaseServices)
- Entities: `Pipe` : Segment; `PipeFitting` : Fitting; `PipeCustomFitting` : MultiSegment; `PipeFlex` : MultiSegment.
- Styles and definitions: `PipeStyle` : SegmentStyle; `PipeFittingStyle` : FittingStyle; `PipeCustomFittingStyle` : MultiSegmentStyle; `PipeFlexStyle` : MultiSegmentStyle; `PipeRiseDropStyle` : MultiViewPartBaseDefinition; `PipeSystemDefinition` : SystemDefinition; `PipePartCatalogPreferenceStyle` : PartCatalogPreferenceDefinition; `PipePartRoutingPreferencesStyle` : PartRoutingPreferencesDefinition.
- Dictionary helpers (each : Autodesk.Aec.DatabaseServices.Dictionary): `DictionaryPipeStyle`, `DictionaryPipeFittingStyle`, `DictionaryPipeCustomFittingStyle`, `DictionaryPipeFlexStyle`, `DictionaryPipeRiseDropStyle`, `DictionaryPipePartCatalogPreferenceStyle`, `DictionaryPipePartRoutingPreferencesStyle` (each has `GetStandardStyle`), `DictionaryPipeSystemDefinition` (has `GetStandardDefinition`).
- Routing preferences: `PartRoutingPreferencesDefinition` : DictionaryRecord; `PartRoutingPreferenceItem` : ImpObject; `PartRoutingPreferenceItemCollection` (IList).
- Other: `PipeSlopeFormat` : ImpObject (its description is printed as "Represents a ?.").
- Inheritance of Pipe as printed: Object, MarshalByRefObject, DisposableWrapper, RXObject, Drawable, DBObject, Entity, Curve, (Aec) Entity, Geo, LayoutTool, Member, Segment, Pipe. So a Pipe is an AutoCAD Curve-derived entity and goes through the normal transaction pattern (13.10). Segment, Fitting, MultiSegment and Member are in `Autodesk.Aec.Building.DatabaseServices`. (AecbPipeBaseMgd help: Autodesk.Aec.Building.Piping.DatabaseServices.Pipe, AecbPipeBaseMgd help: Autodesk.Aec.Building.Piping.DatabaseServicesHierarchy)

## 13.15 Other programming interfaces at a glance

### What full AutoCAD on Windows supports ([G:E6429154](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E6429154-36DF-4D84-8ABC-9FCA15B66158))
- AutoLISP, Visual LISP, ObjectARX, Managed .NET, ActiveX Automation, VBA, JavaScript: all on Windows AutoCAD (and so on the MEP toolset). Commands: ARX, NETLOAD, VBAIDE, VLIDE, APPLOAD, WEBLOAD.
- LT: no ObjectARX, no .NET; ActiveX only through AutoLISP. Mac: no .NET, no ActiveX, no VBA. ([G:E6429154](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E6429154-36DF-4D84-8ABC-9FCA15B66158), [G:2090E4E8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2090E4E8-9AE0-4E01-B5EB-0843A30EB0E9), [G:25616676](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-25616676-EFF2-4060-A06F-19112622A78B))

### AutoLISP ([G:16DC15FC](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-16DC15FC-5329-492E-B66A-401D49CF971F), [G:4E633A41](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-4E633A41-30EA-4C6B-ABC5-11F58970E1EE))
- Built-in interpreter: type at the Command prompt or load files. Formats: `.lsp` (source), `.fas` (one compiled file), `.vlx` (compiled set of LSP/DCL; Windows only).
- Each open drawing has its own namespace. AutoLISP cannot open and close drawings across a session; VBA can. ([G:2CD40631](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2CD40631-D67B-4DF0-A2C4-606E9B613252))

### ActiveX / COM ([G:2090E4E8](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2090E4E8-9AE0-4E01-B5EB-0843A30EB0E9), [G:BFFF308E](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-BFFF308E-CC10-4C56-A81E-C15FB300EB70), [G:C8C65D7A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C8C65D7A-EC3A-42D8-BF02-4B13C2EA1A4B))
- Any Automation controller (stand-alone EXE, DLL, Office macro) can create and change drawing objects, prompt for input, make selection sets and read data. Works in or out of process; .NET works in-process only.
- ProgID for AutoCAD 2027: `AutoCAD.Application.26.0`. Type library `acax26enu.tlb`. Object IDs are 64-bit (LONG_PTR). ([G:C2CF8478](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-C2CF8478-D76A-4A8B-BF7C-E7E3507A4983))
- Launch an external app from a command: acad.pgp line such as `RUNAPP2, start c:\vbapps\app2, 0, *Parameters: ,`, or AutoLISP `startapp`.

### VBA ([G:2CD40631](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-2CD40631-D67B-4DF0-A2C4-606E9B613252), [G:30F06535](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-30F06535-7FB5-4F03-A0EE-96973836E231), [G:E50E8491](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-E50E8491-5BCB-4202-B3A9-BF6FD9CF68A3), [G:8319439A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8319439A-C945-46ED-A14B-B7237F5FA17D))
- Not installed by default; download from autodesk.com/vba-download. Runs in-process via ActiveX. Projects are `.dvb` files and must be loaded before their macros run.
- Run: `-vbarun` then `project!module.macro`, or `(vl-vbarun "mytools.dvb!utilities.selectcircles")`. Loading shows an Enable Macros box [GUI].
- Autodesk warns VBA will be removed in a future version. Not signable. ([G:8319439A](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-8319439A-C945-46ED-A14B-B7237F5FA17D), [G:0A93626D](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-0A93626D-8389-45FC-969B-B86A2F37D691))
- 64-bit VBA: `Set x = New AcXxx` fails because VBA cannot load the 64-bit COM DLLs; use `AcadApplication.GetInterfaceObject(progId)` for IDispatch-based objects. Sheet Set objects (IUnknown-based, e.g. AcSmSheetSet) have no 64-bit VBA route; port to VB.NET. The page is marked for 2014 and earlier. ([G:71350DE2](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-71350DE2-0D33-4833-AB52-94A335A46038))

### ObjectARX ([G:3FF72BD0](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-3FF72BD0-9863-4739-8A45-B14AF1B67B06), [G:409E18E6](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-409E18E6-7164-41CB-A188-97E79E42BC5A))
- Compiled C++ DLL with extension `.arx`, loaded into AutoCAD's address space with direct access to the database, graphics and geometry. Can define commands and LISP functions. Build with Visual Studio; ship a release build. CRX is the no-UI console variant (13.13).

### Customization pieces ([G:CDF5C4CB](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-CDF5C4CB-BE69-4ECE-B9EC-49BA422B878E))
- Templates (DWT), aliases (acad.pgp), AutoCorrect and synonym PGPs, linetypes (LIN), hatch (PAT), shapes and fonts (SHP/SHX), CUIx (CUI command), scripts (SCR via SCRIPT), tool palettes, status bar via DIESEL and MODEMACRO.
- Redefining commands (REDEFINE) is listed as a customization; doc example: redefine QUIT so it writes billing info to a log first. With UNDEFINE it is how a LISP command can replace a built-in (13.2, 13.4 S::STARTUP example). Not in LT. Action macros (ACTMX, ACTRECORD; not in LT): ACTM files from 2024 and earlier must be migrated to ACTMX before playback.

### License mode check ([G:DDF57ED1](https://help.autodesk.com/view/OARX/2027/ENU/?guid=GUID-DDF57ED1-AFD9-4256-B0AF-201D5DC30D87)) [AUTO]
- Read `_PKSER`, `ONLINEUSERID`, `ONLINEUSERNAME`. `_PKSER` not "000-00000000" = perpetual. `_PKSER` = "000-00000000" with both online values non-empty = subscription.
