---
name: fusion
description: "Drive Autodesk Fusion (formerly Fusion 360) on the user's Windows PC with no mouse or keyboard input: Python jobs through the ClaudeJobRunner add-in or Fusion's built-in MCP server, native piping models (Pipe feature, temporary B-Rep bodies merged one body per layer), renders and named views, cloud saves and versions, automatic drawings with PDF and DWG export, STEP and F3D import/export, plus measured notes from live tests. Use it for ANY Fusion task or question: 'do it in Fusion', 'build the model', 'Fusion API', 'script', 'add-in', 'job runner', 'render', 'named view', 'drawing from the model', 'share link', 'Fusion MCP', toolpaths, flat patterns, even when Fusion is only one part of a bigger CAD job (then also load the autocad skill). Read it BEFORE the first Fusion command."
---

# Autodesk Fusion, driven by an agent

Living skill. Every line is a point-in-time fact from tests on Fusion build 2705.1.30 (October 2026), and Fusion ships monthly: probe before trusting one. Live test evidence: `references/hands-on-2026-10-17.md`. Add each new finding the same day, with the date. Script paths below are relative to this skill's folder (for example `scripts/fjob.py`).

This skill is independent and not affiliated with or endorsed by Autodesk. Autodesk, Fusion and AutoCAD are trademarks of Autodesk, Inc., named here only to identify the product.

## Setup (once)
1. Install Fusion (per-user install under `%LOCALAPPDATA%\Autodesk\webdeploy\production\<hash>\`).
2. Install the job runner add-in: make the folder `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\ClaudeJobRunner\`, copy `scripts/ClaudeJobRunner.py` into it, and add `ClaudeJobRunner.manifest` beside it:
   ```json
   {
       "autodeskProduct": "Fusion",
       "type": "addin",
       "id": "<a new GUID>",
       "author": "<your name>",
       "description": {"": "Runs job scripts from a folder. Safe to disable."},
       "version": "1.0.0",
       "runOnStartup": true,
       "supportedOS": "windows",
       "editEnabled": true
   }
   ```
   Restart Fusion. The add-in writes `runner_started.txt` in the jobs folder when it loads.
3. Jobs folder: `FUSION_JOBS_DIR` if set, else `%TEMP%\claude-fusion\jobs`. The add-in, `fjob.py` and `fusion_up.ps1` all use this rule; if you set `FUSION_JOBS_DIR`, set it as a user environment variable so Fusion sees it at start.
4. Python 3 on the PC for the helper scripts (any recent version; Fusion's own embedded Python runs the jobs).
5. Optional: the Fusion MCP server (see below).

## Rules
1. **Check API names in the installed stubs, not in memory or the web.** `python scripts/fapi.py <regex>`, `-c <Class>`, `-m <Class.member>`, `-d <regex in docs>`, `--preview drawing`. The online API help can describe members the installed build does not have yet (in October 2026: drawing `Views.add`, `Sheet.titleBlock`, manual drawing dimensions).
2. **No mouse, no keyboard.** Drive Fusion only with jobs (runner) or MCP Execute. `scripts/fusion_up.ps1` starts Fusion minimized. Screenshots to check are fine.
3. **Leave the user's open work alone.** Before the first job, read `app.documents`, the window title (`*` means unsaved changes), and check whether another agent session is already driving Fusion. Test in a new scratch document and close it with `close(False)`. Never open, save or close the user's files unless that is the task.
4. **End stray commands before closing a document:** `if ui.activeCommand not in ("SelectCommand", ""): ui.terminateActiveCommand()`. A drawing starts `FusionDrawingAutoDimensionEditCommand` by itself 1 to 2 s after a PDF export, and closing while it runs hangs Fusion at 100% of a core until it is killed.
5. **Nothing that waits for a human:** no `close(True)`, `ui.messageBox`, `inputBox`, `selectEntity` or file dialogs in a job. They freeze the main thread and every later job.
6. **Model-changing jobs get `# runner: txn`.** The runner wraps them in `PTransaction.Start`/`Commit` and rolls back with `Abort` on any exception, so a failed job leaves nothing half-built, and the user can undo a whole job with one Ctrl+Z. Documents cannot be created, opened, saved or closed inside a transaction (stub: `Documents.add`, `Document.close`): put those in their own job without txn, then build in a txn job. `# runner: txn` starts the transaction on whatever document is active before the job runs: a job that activates its own document must start `PTransaction` itself after `doc.activate()`.
7. **Units:** the API works in cm and radians. Keep the model in inches in your own code and convert in one place (`IN = 2.54`). Use `ValueInput.createByString("4.5 in")` or parameter names for anything the user will read in Fusion (`createByReal` shows up as "114.30 mm").
8. **Y up:** new documents are Y up by default (`defaultModelingOrientation` = 0). Model Z up anyway (it matches AutoCAD and the op list) and always set the camera `upVector` to (0, 0, 1). Drawing view names follow the document frame, so a Z-up model's "Front" view is its plan. Changing the preference is the user's call (it is persistent and affects their new designs).
9. **Big models: merge each layer into one body before adding it.** 3,000 pipe pieces in 30 layer components: 14 s direct, 35 s parametric, against 91 to 214 s one body at a time and 36 s by STEP import.
10. **`TemporaryBRepManager.createTorus` ignores its center** (2705.1.30): build elbows at the origin, then `tbm.transform(body, matrix)`. The boolean still returns True on an empty result, so check `faces.count` or volume.
11. **A save is not done when `saveAs` returns.** Wait until `doc.dataFile.isComplete` is True (about 6 to 8 s; until then `dataFile.id` is a local cache path). A new version of a shared model changes what its public link shows: ask the user before saving their models.
12. **Check `design.designIntent` before adding components to a design the user made** (`DesignIntentTypes`: Part 0, Assembly 1, Hybrid 2; preview API). Since January 2026 a Part design holds bodies only and an Assembly design cannot model; `Documents.add` always makes a Hybrid design, which is what the recipes here need.
13. **`itemByName` can raise or return None** depending on the collection (`namedViews.itemByName` raises, `dataFolders.itemByName` returns None). Wrap in try and test for None. `findFileById` on a deleted file RAISES ("3 : file not found"); it does not return None.
14. **Status from artifacts:** the job's .queued/.started/.done/.err files, Fusion's log (`%LOCALAPPDATA%\Autodesk\Autodesk Fusion 360\<user id>\logs\AppLogFile*.log`), CPU over 3 s (about 3 s = one core pinned, hung), file mtimes, and a look at every PNG or PDF you make.
    - **Job queued, never started, Fusion idle (CPU near 0) and MCP calls time out = a modal dialog is open** (a Share dialog left open blocks the runner and MCP alike). Find it without touching the mouse: `win32gui.EnumWindows` over the Fusion360 process's visible windows (Qt dialogs show a Qt window class and are titled just "Fusion360"), then capture each with `PrintWindow(hwnd, hdc, 2)` to see what it is. A Share or other info dialog closes with `PostMessage(hwnd, WM_CLOSE)` and the queued job runs at once; tell the user in one line. Never close a dialog that is mid-edit (a command dialog with inputs): ask.
    - **The Data panel can be stale.** It can still list deleted files and folders an hour after `deleteMe`; `app.data` (dataProjects, rootFolder.dataFiles) shows the truth. Answer "what is in the cloud" from the API.
15. **No em or en dashes** in anything you write for the user, including title blocks and notes.
16. **`Documents.open(dataFile, False)` returns the tab that is already open** if that file is open (visible, in 0.2 s), so closing "your" copy closes the user's tab. Before opening, look for an open document whose `dataFile.id` matches; close only documents your job opened itself.
17. **Never leave an unsaved copy open in Fusion.** With save on close ON, closing Fusion turns every unsaved copy into a NEW cloud file (same name, or "Untitled") and Fusion may give it its own public link. Keep build-to-close in one uninterrupted run, close copies with `close(False)` when done, and after a session check the folder for same-name or Untitled files (`dataFiles` names, `latestVersionNumber`, `sharedLink.linkURL`).

## What a working install looks like (checked on 2705.1.30)
- Version strings are `AAAA.B.C` (`app.version`), no longer `2.0.xxxxx`.
- Per-user install: `%LOCALAPPDATA%\Autodesk\webdeploy\production\<hash>\` (the hash changes each update; `fapi.py --build` prints it). `FusionLauncher.exe` in that folder is the Start menu target; `fusion_up.ps1` finds the newest one, or pass `-Launcher`.
- Embedded Python 3.14, no pip: vendor any package beside the script. Stubs: `<build>\API\Python\packages\adsk\defs\adsk\{core,fusion,drawing,cam,electron,sim,volume}.py`. TypeScript typings for desktop and for the cloud Automation API: `<build>\API\TypeScript\@adsk\fusion\` and `...\automation\`.
- **ClaudeJobRunner v2** add-in: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\ClaudeJobRunner\` (source of truth `scripts/ClaudeJobRunner.py`).
- Preferences that matter: Y up, inches, new designs parametric (`defaultDesignType` 2), "save on close" ON by default (`isAutomaticSaveOnCloseEnabled`), auto versioning off, API debugging port 9000. "Allow 3D sketching" off only limits the GUI: API sketch lines may leave the sketch plane.
- Fusion starts into Home with NO document (`app.activeDocument` and `app.activeProduct` are None, `ui.activeCommand` is ""): a job must open or create a document before it touches a design.
- Job models live in their own projects and folders: look them up with `app.data`, do not assume "Default Project". Test files go in a new scratch folder and get removed when done.
- **Deleting cloud files:** the Data panel's Move to Trash goes to the project's Trash, restorable in the web client (see Autodesk's help on deleting designs). `DataFile.deleteMe()` / `DataFolder.deleteMe()` work (True, and the file is gone from `findFileById`) but Autodesk does not document whether they go to Trash. So back up first: `documents.open(dataFile, False)` (invisible open works), export .f3d (drawings: PDF and DWG), close, then delete. Only when the user asks.

## Drive Fusion

### Job runner (default path)
1. `pwsh -NoProfile -File scripts/fusion_up.ps1` starts Fusion if needed, minimizes it, and waits for the runner (48 to 113 s cold). If Fusion is already open it returns at once and touches nothing.
2. Write the job to a .py in your scratch folder, then `python scripts/fjob.py <job.py> [timeout_s]`. It drops the file in atomically and prints RESULT plus everything the job printed. Exit 0 done, 1 job raised (traceback), 2 timeout (with a CPU check), 3 runner not live.
3. The job runs on Fusion's main thread with `app`, `adsk`, `JOBS` and `RESULT` in scope. Fusion is frozen until it returns: keep each job to a few minutes and split bigger work. Windows hang detection (`generalPreferences.isHangDetectionEnabled`) can raise a modal dialog during a long compute; none appeared in a 3.5 minute test job.
4. Flags in the first 5 lines: `# runner: txn` (one undo step, rollback on error), `# runner: force` (run even if a command is active), `# runner: readonly` (same, for jobs that only read). Without force a job is REFUSED while `ui.activeCommand` is not "SelectCommand" or "" (the user may be inside a dialog). After a drawing export, a forced job may end the stray command.
5. For long steps, append progress lines to a file in `JOBS` from inside the job (open, append one timestamped line, close, for each step), so a hang shows where it stopped. `ops_to_fusion.py` writes its jobs this way.
6. Runner files: `.queued` (seen), `.started` (main thread began; first line is the active command), `.done`, `.err`. Queued but not started means the main thread is busy or blocked.
7. Add-ins load only at startup. To reload after an edit: with no document open, post WM_CLOSE to Fusion's main window (closes in 8 to 46 s), then `fusion_up.ps1`. With documents open, ask the user.
8. Write jobs MCP-style when they may also run through MCP: define `def run(_context: str)` and print the results. Runner v2 calls it.

### Fusion MCP server
- **Turn it on:** text commands `Options.Set MCPServerEnabled ON` then `Options.Save` (writes `%APPDATA%\Autodesk\Neutron Platform\Options\NMachineSpecificOptions.xml`; same setting as Preferences > General > API > "Fusion MCP Server"). Port option `MCPServerPort` (default 27182). It survives a Fusion restart. Turn it off with `Options.Set MCPServerEnabled OFF` + `Options.Save`, or the checkbox. Turning it on is the user's call.
- **Endpoint:** `http://127.0.0.1:<port>/mcp`, Streamable HTTP, loopback only, no authentication, gone whenever Fusion is closed. Server "MCP Server Adapter 1.0.0", protocol 2025-06-18. Check with text command `MCP.Server` ("MCP server is running at ...") or `Get-NetTCPConnection -State Listen -LocalPort <port>`.
- **Claude Code:** back up your Claude Code user config, then `claude mcp add --scope user --transport http autodesk-fusion http://127.0.0.1:27182/mcp`. `claude mcp list` shows "autodesk-fusion ... Connected" while Fusion runs. Sessions pick the tools up at START, so a session that began while Fusion was closed has no Fusion tools: start Fusion (`fusion_up.ps1`) and reconnect the server, or fall back to the runner or `scripts/mcp_probe.py`.
- **Tools (outside clients, 2705.1.30):** `fusion_mcp_execute`, `fusion_mcp_read`, `fusion_mcp_update`, `fusion_mcp_electronics_read` (in a session they appear as `mcp__autodesk-fusion__fusion_mcp_execute` and so on). Create and Delete are not offered.
- **Execute a script:** arguments `{"featureType": "script", "object": {"script": "<python>", "readOnly": true}}`. The script defines `def run(_context: str)`, prints its output (returned as `message` with `success`), and should let exceptions surface. Verified: a read-only script ran with NO document open, and a normal script created a scratch document, added a body (31.416 in3, exact) and closed it. The text command `MCP.ExecuteScript` reports "Execute script tool is disabled", which only concerns Fusion's own Assistant; external script calls work anyway. Same main thread as the runner: one at a time, Fusion frozen while it runs, a normal script is refused while a command dialog is open (`readOnly: true` is allowed then).
- **Raw client for tests and fallback:** `python scripts/mcp_probe.py` (handshake and tool list), `--script "<python>"` (read-only script), `--call <tool> '<json args>'`. Set `MCP_URL` if you changed the port.
- **MCP or runner?** Use the MCP tools for interactive work (instant output, screenshots from `fusion_mcp_read`, API documentation search). Use the runner for long or batch jobs (MCP execute times out on multi-minute scripts that still finish), for `# runner: txn` rollback, and when the session has no Fusion tools. Both need Fusion running.
- Full tool list and schemas: run `mcp_probe.py` (tools/list) or the text command `MCP.List`.

### Text commands
`app.executeTextCommand(cmd)` reaches Fusion's internal commands (Autodesk documents the call, not the commands). `TextCommands.List` lists them for your build. Proven on 2705.1.30: `Options.Get <id>`, `Options.Set <id> <value>`, `Options.Save`, `Options.List /full` (find option ids); `PTransaction.Start "name"`, `PTransaction.Commit`, `.Abort`, `.Undo`, `.Redo` (each returns '1'); `MCP.Server`, `MCP.ServerURL`, `MCP.Port`, `MCP.List`; `Application.StartupTime`; `Paths.UserDirectory`. Never use `TextCommands.LoadDll`, test hooks (`AASimulator.*`, `NTestGen*`) or commands that open dialogs.

### Cloud Automation API (APS)
Runs Fusion TypeScript scripts in the cloud, generally available, billed in Autodesk Flex tokens per compute hour, no viewport images. It costs money: ask the user before using it.

## Recipes (verified on 2705.1.30 unless marked)

### Scratch document and cleanup
```python
doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)   # always visible, becomes active
des = adsk.fusion.Design.cast(app.activeProduct)
des.designType = adsk.fusion.DesignTypes.DirectDesignType   # only for bulk solids with no timeline
root = des.rootComponent
# ... work ...
ui = app.userInterface
if ui.activeCommand not in ("SelectCommand", ""):
    ui.terminateActiveCommand()
doc.close(False)   # no prompt for an unsaved scratch document
```
`Documents.add(..., visible=False)` is not allowed (stub). `Documents.open(dataFile, False)` opens invisibly (2.6 to 4.4 s for a cloud file). Opening a drawing also loads its design; closing the drawing closes both.

### Pipe run with bends: Fusion's Pipe feature (parametric, editable)
```python
# runner: txn
IN = 2.54
P = lambda x, y, z: adsk.core.Point3D.create(x * IN, y * IN, z * IN)
des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
des.userParameters.add("CHW_OD", adsk.core.ValueInput.createByString("4.5 in"), "in", "4 in Sch 40 OD")
des.userParameters.add("CHW_WALL", adsk.core.ValueInput.createByString("0.237 in"), "in", "4 in Sch 40 wall")
occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); c = occ.component; c.name = "CHWS 4in"
sk = c.sketches.add(c.xYConstructionPlane)
L = sk.sketchCurves.sketchLines
pts = [P(0, 0, 120), P(240, 0, 120), P(240, 0, 30)]           # any number of corners; 3D lines are fine
segs = []
for a, b in zip(pts[:-1], pts[1:]):
    segs.append(L.addByTwoPoints(segs[-1].endSketchPoint if segs else a, b))   # share the end point so the path chains
for s1, s2 in zip(segs[:-1], segs[1:]):
    sk.sketchCurves.sketchArcs.addFillet(s1, s1.endSketchPoint.geometry, s2, s2.startSketchPoint.geometry, 6 * IN)
pin = c.features.pipeFeatures.createInput(c.features.createPath(segs[0], True), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
pin.sectionType = adsk.fusion.PipeSectionTypes.CircularPipeSectionType
pin.sectionSize = adsk.core.ValueInput.createByString("CHW_OD")       # OUTSIDE DIAMETER (measured)
pin.sectionThickness = adsk.core.ValueInput.createByString("CHW_WALL")  # wall; also sets isHollow
pf = c.features.pipeFeatures.add(pin)
```
- One feature per run, about 0.6 s; volume matched hand math exactly. Bend radius = the sketch fillet radius (1.5 x NPS for long radius elbows).
- Use it for runs the user may edit in Fusion. For thousands of pieces use the bulk recipe.
- OD by NPS: 1/2 0.840, 3/4 1.050, 1 1.315, 1-1/2 1.900, 2 2.375, 3 3.500, 4 4.500 in. Sch 40 walls (ASME B36.10): 1/2 0.109, 3/4 0.113, 1 0.133, 1-1/2 0.145, 2 0.154, 3 0.216, 4 0.237 in. Confirm against ASME B36.10 or the job spec before relying on them.

### Bulk solids: temporary bodies, one body per layer (fastest)
```python
tbm = adsk.fusion.TemporaryBRepManager.get()
U, D = adsk.fusion.BooleanTypes.UnionBooleanType, adsk.fusion.BooleanTypes.DifferenceBooleanType
def hollow(p0, p1, od, wall):            # points in cm
    o = tbm.createCylinderOrCone(p0, od / 2, p1, od / 2)
    n = tbm.createCylinderOrCone(p0, od / 2 - wall, p1, od / 2 - wall)   # extend the bore past the ends if faces must be clean
    tbm.booleanOperation(o, n, D); return o
for layer, pieces in layers.items():          # pieces: temp bodies for that layer
    acc = pieces[0]
    for b in pieces[1:]:
        tbm.booleanOperation(acc, b, U)       # disjoint pieces become one body with many lumps: accepted
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); occ.component.name = layer
    if des.designType == adsk.fusion.DesignTypes.DirectDesignType:
        occ.component.bRepBodies.add(acc)
    else:
        bf = occ.component.features.baseFeatures.add(); bf.startEdit()
        occ.component.bRepBodies.add(acc, bf); bf.finishEdit()
```
- Pieces: straight = hollow cylinder; reducer = `createCylinderOrCone(p0, r0, p1, r1)` outer minus inner; tee = union of run and branch, then subtract both bores; elbow = torus at the ORIGIN intersected with a box (or minus boxes), then `tbm.transform(elbow, m)` with `m.setToAlignCoordinateSystems(...)` or `m.translation`; valves and equipment = boxes and cylinders (`createBox(OrientedBoundingBox3D.create(center, lengthDir, widthDir, L, W, H))` honors its center).
- Keep the op list as the single source of truth for counts and calcs (the merged bodies no longer carry per-piece names).
- **Whole op list in one step:** `python scripts/ops_to_fusion.py ops.json job.py --png out.png [--parametric] [--view SWISO]`, then `python scripts/fjob.py job.py 900`. Input is an op list (`[layer, kind, args]` in inches: cyl, cone, sph, box, torus, elb, strut, wall, cstrap) plus layer colors. A building piping model of about 5,000 pieces in about 50 layers built in 42 s with zero failures. `scripts/dump_ops.py` dumps the op list from a Python model folder.
- Timings and the torus bug: `references/hands-on-2026-10-17.md`.

### Colors
```python
lib = app.materialLibraries.itemByName("Fusion Appearance Library")      # 172 appearances
ap = des.appearances.addByCopy(lib.appearances.itemByName("Paint - Enamel Glossy (Green)"), "CHWS green")
for i in range(ap.appearanceProperties.count):
    pr = ap.appearanceProperties.item(i)
    if pr.objectType.endswith("ColorProperty"):
        adsk.core.ColorProperty.cast(pr).value = adsk.core.Color.create(40, 160, 70, 255); break
occ.appearance = ap
```
Copy each appearance into the design once and reuse it. Any paint works as the base because the color is overwritten (the library has no orange; recolor the red). A readable palette: supply greens, return oranges, one color per system and size.

### Views and renders
- Orthographic camera, Z up, eye along the AutoCAD iso direction (SWISO (-1,-1,1), SEISO (1,-1,1), NEISO (1,1,1)), `target` at the box center, `upVector` (0,0,1), `isSmoothTransition = False`, then `vp.camera = cam`. Either `isFitView = True` (Fusion frames everything) or `isFitView = False` plus `cam.setExtents(width_cm, height_cm)` (orthographic only; Fusion keeps whichever extent matches the viewport aspect). About 0.95 x the box's largest side frames one area; 0.60 to 0.62 for a whole building. `cam.viewExtents` is a retired member missing from the stubs: it still worked in tests, but use `setExtents`/`getExtents` in new code.
- `isFitView = True` can leave an L-shaped run small and off center, and a target at the box center can crop it. Frame tightly by projecting the 8 bounding box corners onto the camera axes (verified):
```python
def frame(vp, bb, d=(-1.0, -1.0, 1.0), up=(0.0, 0.0, 1.0), margin=1.08, aspect=1.6):   # bb in cm, d points from target to eye
    unit = lambda v: [x / math.sqrt(sum(y * y for y in v)) for x in v]
    cross = lambda a, b: [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    d = unit(d); vd = [-x for x in d]; right = unit(cross(vd, up)); upv = cross(right, vd)
    mn, mx = bb.minPoint.asArray(), bb.maxPoint.asArray()
    cs = [(x, y, z) for x in (mn[0], mx[0]) for y in (mn[1], mx[1]) for z in (mn[2], mx[2])]
    us = [dot(c, right) for c in cs]; vs = [dot(c, upv) for c in cs]; bc = [(mn[k] + mx[k]) / 2 for k in range(3)]
    du = (min(us) + max(us)) / 2 - dot(bc, right); dv = (min(vs) + max(vs)) / 2 - dot(bc, upv)
    t = [bc[k] + right[k] * du + upv[k] * dv for k in range(3)]
    w, h = (max(us) - min(us)) * margin, (max(vs) - min(vs)) * margin
    w, h = (h * aspect, h) if w / h < aspect else (w, w / aspect)
    L = math.sqrt(sum((mx[k] - mn[k]) ** 2 for k in range(3)))
    cam = vp.camera; cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.target = adsk.core.Point3D.create(*t); cam.eye = adsk.core.Point3D.create(*[t[k] + d[k] * 2 * L for k in range(3)])
    cam.upVector = adsk.core.Vector3D.create(*up); cam.isFitView = False; cam.isSmoothTransition = False
    cam.setExtents(w, h); vp.camera = cam
```
- Image: `o = adsk.core.SaveImageFileOptions.create(path)`; `o.width, o.height`; `o.isAntiAliased = True`; `o.isBackgroundTransparent = True` when it goes on a sheet; `vp.saveAsImageFileWithOptions(o)`. Works with Fusion minimized. Render at the aspect of the sheet box it fills.
- Named views: `des.namedViews.add(vp.camera, name)` after setting the camera; saved in the .f3d; they store only the camera (not visibility). `namedViews.itemByName` raises when missing.
- Toggling `occ.isLightBulbOn` for a render marks a cloud document modified even after you restore it: on the user's clean documents, move the camera only.
- Camera-only renders are safe on a clean, saved cloud design (verified over MCP execute): save `vp.camera`, set a named view's camera or a `frame()` camera, `saveAsImageFileWithOptions`, put the saved camera back. `doc.isModified` stays False. To frame one detail (one equipment drop), take the union bounding box of the bodies named for it; if neighbors get cut at the edge of the frame, turn the view so they line up across the frame (side-on with about 40 degrees of elevation) instead of in front of it.
- For renders, set the ground shadow option (`GroundShadowEnabledId`) OFF: tall walls otherwise draw as a hard gray band on the ground in some views. Restore it after (no `Options.Save`).
- A job that just imported can frame the first view badly: re-render that view in a second job.
- `NamedView.camera` is read/write: turn a view by setting a new eye on its own camera (keep target and `getExtents`). The browser lists named views in creation order: delete and re-add them sorted to sort it.

### Polish an imported model (no geometry change)
Write one job that does these steps, and reuse it for any STEP or op-list model:
- Display units: `des.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.InchDistanceUnits` (STEP imports come in as mm).
- Group layer components: make group components inside the import wrapper, then `layerOcc.moveToComponent(groupOcc)` (both from `wrapper.component.occurrences`, same context). Worked on about 50 STEP-import occurrences in a parametric design. Keep the layer code in `component.partNumber` and match on it, so later scripts survive the renames.
- Body names are unique inside a component: setting a name another body still holds gives "name (1)". On a rename pass, set changed bodies to temporary names first, then the final names.
- Name bodies by matching each body's box center (and `faces.item(i).pointOnFace` samples for pipes) to the op list's tagged points and run polylines.
- **Check that every piece made it.** A CadQuery per-layer fuse on the STEP route can silently drop a short run with no error, and comparing bounding boxes cannot catch a piece lost inside the layer's extents. Test one point inside every op-list piece with `body.pointContainment` (0 inside, 1 on, 2 outside; prefilter by body box): about 5,000 pieces in 8 min. On one-body-per-layer builds, `BRepLump.pointContainment` with lump boxes as the prefilter checks about 7,000 points in about 1 s. Add a negative control (points lifted off each piece must test outside) to prove the check is not blind. Add missing pieces back natively (temporary bodies unioned, one base-feature body).
- `Component.opacity` (0 to 1) makes context see-through: building walls at 0.25 to 0.35 let the piping read through them in every view. It shows in Fusion and its renders only: the web share viewer draws those walls solid. The share viewer does show renamed groups in its model browser.
- Physical materials: Fusion Material Library has "PVC-Piping", "Steel, Galvanized", "Stainless Steel"; it has no concrete. Body appearance overrides from the STEP stay on top of the material, so set appearances yourself.
- Speed: a first pass (about 50 moves plus appearances on about 1,200 bodies) took about 3.5 min on an unsaved copy and 9 min on a cloud design with a second document open (give the runner a 900 s timeout); a rerun that skips unchanged values took 10 s. The Fusion MCP execute call timed out on the long pass while Fusion finished and committed it anyway: run anything over about a minute through the runner (`fjob.py`), which waits and prints the result.

### Save to the cloud
```python
rf = app.data.activeProject.rootFolder               # or find the right project: app.data.dataProjects
folder = rf.dataFolders.itemByName("zz Claude API tests") or rf.dataFolders.add("zz Claude API tests")
doc.saveAs("Name", folder, "description", "")       # returns at once
# next job(s): poll until app.activeDocument.dataFile.isComplete is True, then use the DataFile
```
- New version of an open cloud design: `doc.save("description")` returned in 3 to 10 s, with `isComplete` True and the new `versionNumber` a few seconds later. Read the share link without the dialog: `dataFile.sharedLink.linkURL` / `.isShared` / `.isDownloadAllowed` (read-only job; confirms the public link is the file you saved). The share link stays the same across versions and the web viewer shows the newest one.
- Replace a shared cloud model with a local .f3d and keep its link: `documents.open(df, True)`, delete the named views, `designType = DirectDesignType` (drops the whole timeline, no prompt), delete the root occurrences, `importToTarget2(createFusionArchiveImportOptions(f3d), root)` (about 9 s; one wrapper occurrence named after the file, not referenced; bodies, appearances and component opacity come through identical body by body), then re-add the named views: the .f3d's named views do NOT come with the import. Compare body by body against the .f3d opened by `importToNewDocument` (close it with `close(False)` in the same job; it opens as "Untitled", not the file name) before `doc.save`. Ask the user before saving: the public link will show the new version.

### Automatic drawing from a saved design
```python
inp = adsk.drawing.DrawingManager.get().createDrawingInput(dataFile, adsk.drawing.DrawingCreationModes.AutomaticDrawingCreationMode)
inp.standard = adsk.drawing.DrawingStandardTypes.ASMEDrawingStandardType
inp.units = adsk.drawing.DrawingUnitTypes.InchDrawingUnitType
inp.sheetSize = adsk.drawing.SheetSizes.DASMESheetSize                  # or customSize for 36 x 24
inp.sheetCreationType = adsk.drawing.SheetCreationTypes.FirstLevelOnlySheetCreationType
g = inp.automationPreferences.globalPreferences
g.omitComponentsWithKeywords = ""          # default "Bolt,Screw,Nut,Washer" drops any part NAMED like that
g.isComponentSheetGenerated = True         # one dimensioned sheet per first-level component
dwg = adsk.drawing.DrawingManager.get().createDrawing(inp)   # synchronous (84 s for 3 parts); returns a SAVED .f2d DataFile
# separate job:
ddoc = app.documents.open(dwg, True); drw = adsk.drawing.Drawing.cast(app.activeProduct)
o = drw.exportManager.createPDFExportOptions(pdf_path); o.openPDF = False; o.useLineWeights = True
drw.exportManager.execute(o)
drw.exportManager.execute(drw.exportManager.createDWGExportOptions(dwg_path))
# then: terminateActiveCommand if needed, ddoc.close(False)
```
- You get: an isometric sheet with balloons and a parts list, an orthographic sheet with overall dimensions, and one sheet per component with views, center lines and auto dimensions (a good pipe spool sheet). The title block fills itself (project, design name, Autodesk user name, date, scale, sheet n of N).
- Before creating: set `component.partNumber` and description (they default to creation timestamps) and the physical material (defaults to Steel). Name parts so they do not contain Bolt, Screw, Nut or Washer, or clear the omit list.
- Cannot by API in this build: place, move or scale views; sections, details; text, notes, leaders, manual dimensions; fill custom table cells (`setCellData` returns False); edit title block text; CSV export; print. Can: add sheets (inserted after the active sheet), sketch lines, rectangles, circles, arcs; insert images; create empty custom tables; document settings; PDF, DWG, DXF export.
- Gotchas: open the drawing, then cast `app.activeProduct` (`products.itemByProductType` raises); `Sheet.width/height` read in mm even on inch sheets while sketch points and image positions are in drawing units; `BendTables` has no `count`; PDF and DWG export need every sheet up to date; keep a drawing under about 30 sheets.
- The DWG export is a real AutoCAD file: one layout per sheet, real DIMENSION entities, MULTILEADER balloons, the parts list as an AutoCAD table, layers Visible, Hidden, Section Lines, FD_Dimensions, Notes and more. Tags and notes could be added with accoreconsole (autocad skill); that hybrid is not built yet.
- The October 2026 online API docs add `Views.add(BaseViewInput)`, manual dimensions, title blocks, hole and revision tables. Recheck `fapi.py --preview drawing` after each update: that is the day Fusion drawings can become full construction sets by API.

### STEP route (for models that already live in CadQuery)
CadQuery op list > STEP (the autocad skill's `scripts/fusion_step.py`: mm scaled x 25.4, one colored assembly part per layer, FUSE each layer first or Fusion drops pieces) > `importManager.importToTarget` > views > sheets. About 3,200 solids imported in 36 s. For new models the native per-layer recipe is faster and skips CadQuery; keep STEP for models that already live in CadQuery.
- Change a shared cloud model without losing its link or named views: dump named views to JSON first, delete the root occurrences, `importToTarget(stepOpts, root)` (adds one wrapper occurrence; named views survive; 136 s first import, 45 s after). Saving it changes what the public link shows: ask the user.
- Two sessions, one model: before building sheets, prove the model source matches what Fusion shows (bounding box of a part that moved), split ownership by folder, and tell the other session.

## Which path for which deliverable
| Need | Path |
|---|---|
| Piping model the user will edit in Fusion | Pipe feature per run, parameters for OD and wall, components per system |
| Large model (thousands of parts) | op list > `scripts/ops_to_fusion.py` > job: temporary bodies merged per layer, direct design (about 5,000 pieces: 42 s) |
| Renders, 3D views for sheets | camera job + `saveAsImageFileWithOptions`; named views saved in the .f3d |
| Spool, support, pad or equipment sheets with dimensions and a BOM | automatic drawing by API, PDF and DWG export |
| Full construction set (plans with tags, schedules, details) | autocad skill 2D pipeline from the op list (Fusion drawings cannot place views or text by API yet) |
| Controlled Fusion drawing layout | a template with view and parts-list placeholders built once in the GUI (needs a person at the GUI), then `baseDocumentType = FromTemplateBaseDocumentType` (untested) |
| Plasma or laser cut files | sheet metal flat pattern DXF from the design API; CAM jet operations for toolpaths |

## Staying current (after every Fusion update)
- `fapi.py --build` (new hash?) and `fapi.py --preview drawing` (look for Views, BaseViewInput, DrawingDimensions, TitleBlocks).
- Re-run `TextCommands.List` and `MCP.List`; diff with your saved copies from the last build.
- Re-test the torus center bug, `CustomTable.setCellData`, and the AutoDimensionEdit close hang; update rules 4 and 10 and the drawing notes.
- Read the Fusion release notes on Autodesk's help site.

## Files
- `references/hands-on-2026-10-17.md`: every live test with numbers.
- `scripts/fapi.py`: stub lookup.
- `scripts/fjob.py`: run a job through the runner.
- `scripts/fusion_up.ps1`: start Fusion minimized and wait for the runner.
- `scripts/ClaudeJobRunner.py`: the add-in source.
- `scripts/mcp_probe.py`: raw MCP client.
- `scripts/ops_to_fusion.py` and `scripts/dump_ops.py`: op list to a native build.
