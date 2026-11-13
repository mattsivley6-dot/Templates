# Two AutoCAD MEP instances and COM (mepcom.py PID binding), 2026-10-18

Update, later 2026-10-18: a COM launch gives each session its own MEP. `mepcom.launch()` starts a new acad.exe with
CoCreateInstance, and a holder's ROT locator lets `app(pid)` reach it. Facts 1 and 2 below held for two real AutoCADs.
Fact 3 holds only for an acad.exe started by Popen. See `2026-10-18-mepcom-com-launch.md`.

Module: `mepcom.py` in the autocad skill (`../../claude/skills/autocad/scripts/mepcom.py`). Test: `scripts/mepcom_pid_test.py <work_dir>` with `scripts/mepcom_standin.py`. Why: when two scripts each ran an MEP at the same time, `mepcom.app()` (GetActiveObject) could return either one, and `dialogs()` / `DialogGuard` cancelled dialogs in every acad.exe.

## Facts found live
1. AutoCAD registers ONE Running Object Table entry per instance, an item moniker named `!{E76F49EB-7DAE-4682-ADE6-6C12ECA76DD7}` (the CLSID of `AutoCAD.Application`). It registers no entries for drawings: with `probe4.dwg` open, the ROT held no .dwg names (Excel's open workbook was there).
2. Two instances means two entries with the same name. The ROT gives the FIRST one registered for both entries, and GetActiveObject gives the first one too. Autodesk's Application object page says the same: with several sessions running, GetObject returns the first instance in the ROT (G:0225808C). Tested with two stand-in objects (two Python processes, same `RegisterActiveObject` call, same name): the walk gave [A, A]; the second registration returns MK_S_MONIKERALREADYREGISTERED (a success code) and is stored, but no lookup can reach it.
3. So while the first AutoCAD runs, a second acad.exe cannot be driven by COM at all. Two sessions cannot each drive their own MEP over COM at the same time. Run one MEP over COM at a time; headless work (takeoffs, plots, PDF import) goes to the Core Console.
4. The Office route does not work: `WM_GETOBJECT` with `OBJID_NATIVEOM` to all 142 windows of the running MEP got one answer, from the command line `RICHEDIT50W`, and that object is the RichEdit text object, not AutoCAD.
5. Mapping an entry to its process: `GetWindowThreadProcessId(app.HWND)`. With HWND 0 pywin32 returns thread 0 and a junk pid, so the thread id is checked.
6. The running MEP answered HWND and Caption reads while it rejected `Documents` (call rejected, busy).

## What mepcom.py does now
- `bind(pid)` ties app, doc, var, send, aec, wait_idle, dialogs and DialogGuard to one acad.exe. `bind(None)` undoes it.
- `app(pid)` walks the ROT and returns that acad.exe, or raises com_error MK_E_UNAVAILABLE (-2147221021, the same error GetActiveObject raises when no AutoCAD runs, so existing retry loops treat it the same). If the reachable instance is busy, it raises the busy error. It never returns another instance.
- `instances()` gives `{pid: Application}` for what COM can reach. `py -3.14 mepcom.py` prints the PID map.
- `dialogs(pids)` and `DialogGuard(pid=...)` look only at those processes.
- Nothing bound and no pid: the old code paths, unchanged (GetActiveObject; every acad.exe for dialogs).

## Results (23 of 23 checks passed)
- Live MEP, read only (pid 27360, already running, on probe4.dwg): `instances()` = {27360}; unbound `app()`, `app(27360)` and `bind(27360)` all reach 27360; `app(4)` and `bind(4)` fail closed; `bind(None)` restores GetActiveObject; `dialogs(27360)` equals unbound `dialogs()`. No real dialog was cancelled.
- Two stand-ins under one name: both entries give A; `instances()` = {A}; `app(A)` = A; `app(B)` fails closed; unbound `app()` gives A (the old cross-talk); `dialogs(A)` and `dialogs({B})` list only their own dialog; `DialogGuard(pid=B)` cancelled B's dialog and left A's; bound `DialogGuard()` cancelled only A's; nothing left in the ROT after.
- The stand-in dialogs sat off screen, never activated, with no taskbar button.

PID map printed by `py -3.14 mepcom.py`:
```
acad.exe running: [27360] | AutoCAD entries in the ROT: 1
  pid 27360: COM reaches it | HWND 10489600 | AutoCAD MEP 2027 - [probe4.dwg]
  unbound app() (GetActiveObject) gives pid 27360
```

## mto_make_test_dwg.py
Binds and guards by its own Popen pid. It still refuses to start while any acad.exe runs (its instance would register second and be unreachable). If another AutoCAD registers first during its start, it stops at once and kills only its own pid.

## Not tested
- Two real acad.exe at once: not tried in this test, because an MEP was already running for other work. The stand-ins use the same ROT call and name, and Autodesk's page says the same, so expect the same result.
- `CreateObject` / `CoCreateInstance` of AutoCAD.Application may start a new instance and hand back its object directly, outside the ROT. That could let two sessions each drive their own MEP, but a COM launch cannot pass `/ld AecBase.dbx /p ... /product MEP`. Tested later on 2026-10-18: it starts a new full MEP every time, without those switches (`2026-10-18-mepcom-com-launch.md`).
