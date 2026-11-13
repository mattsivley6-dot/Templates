# COM launch: each session its own AutoCAD MEP 2027 (mepcom.launch), 2026-10-18

Question: can two sessions each drive their own AutoCAD MEP 2027 over COM at the same time? This follows
`2026-10-18-mepcom-two-instances.md`, which found that the shared ROT entry reaches only the first acad.exe registered.
Module: `mepcom.py` in the autocad skill (`../../claude/skills/autocad/scripts/mepcom.py`).

**Answer: yes, with `mepcom.launch()`.** A COM launch (CoCreateInstance) started a NEW acad.exe every time, including
while another one ran. Each came up as full MEP with no `/ld /p /product` switches, and COM handed back that
instance's own object, outside the ROT. A holder process keeps the object and registers a locator in the ROT, so
`app(pid)` reaches that instance from any later script. **Open problem before running MEP sessions in parallel:**
`Documents.Open` restored the minimized window and made AutoCAD the foreground window, so anything typed at that moment
goes into AutoCAD.

Scripts (in `scripts/`): `mepcom_comlaunch_test.py` (2 launches, 27 checks), `mepcom_comlaunch_retest.py` (1 launch,
8 checks), `mepcom_pid_test.py` (stand-ins, 29 checks, with `mepcom_standin.py --handoff` and
`mepcom_holder_standin.py`). The no-AutoCAD holder prototype (`holder_proto.py`, log `holder_proto_h.jsonl`), the
factory probe log (`factory_probe.jsonl`) and the desktop probe (`desk_probe.py`) are in `scripts/2026-10-18-com-launch/`.

## What a COM launch starts (registry, read only)
- `HKCR\CLSID\{E76F49EB-7DAE-4682-ADE6-6C12ECA76DD7}\LocalServer32` = `C:\Program Files\Autodesk\AutoCAD 2027\acad.exe /Automation`. The same value is in HKLM and in a per-user HKCU copy. The registered ProgIDs are `AutoCAD.Application` and `AutoCAD.Application.26`; there is no `.26.0` here, though Autodesk's pages use `.26.0`.
- `HKCU\Software\Autodesk\AutoCAD\R26.0`: CurVer `ACAD-A106:409` (MEP), LastLaunchedLanguage `en-US`. LastLaunchedProduct read MEP, then ACAD after a Core Console run. The MEP default profile (`ACAD-A106:409\Profiles` default) is `AutoCAD MEP (US Imperial)`.
- Autodesk's help: CreateObject with "AutoCAD.Application.26.0" tries to start a new AutoCAD 2027 instance (G:BFFF308E). GetObject returns the first instance in the ROT (G:0225808C).

## Live results (no other AutoCAD running)
| | Round A | Round B | Re-test |
|---|---|---|---|
| acad.exe running before | none | A (16880) | none |
| Registry the holder set | LastLaunchedProduct ACAD | MEPREG | MEPREG |
| New pid, seconds to the object | 16880, 42.4 | 16860, 42.1 | 26916, 42 |
| Process | `acad.exe /Automation -Embedding`, parent svchost.exe (DCOM) | same | same |
| HWND of the object in that pid | yes | yes | yes |
| Product | MEP: CPROFILE `AutoCAD MEP (US Imperial)`, 52 aec* modules, `-AECBPIPEADD` defined, PipeSystemDefs 1 | same | same |
| SendCommand | runs | runs | runs |
| `-AECBPIPEADD` Glued 4 in. x 240 in. | 1 pipe, 240.0 | no pipe (see below) | 3 of 3, 240.0 each |
| How it ended | quit_unsaved: quit | killed (lifetime test) | quit_unsaved: quit |

- **Both `!{CLSID}` entries gave 16880 while both ran, and GetActiveObject gave 16880.** The stand-in finding holds for two real AutoCADs.
- **A separate process reached both at once** through the locators: `app(16860)` and `app(16880)` answered in 0.1 s and 0.0 s.
- Right after a launch, calls can be refused ("Call was rejected by callee") for a few seconds. Both rounds' child-script checks failed this way. `launch()` now returns only once `Documents` answers.
- **Window:** a COM launch opens a NORMAL visible window, but it did not take the foreground in any of the 3 launches. `launch()` now sets WindowState 2 through COM as soon as the HWND exists. Re-test: minimized right after launch, and the foreground stayed on the user's app.
- **Focus (open problem):** after `Documents.Open`, the window was restored (WindowState 1) and AutoCAD was the foreground window (re-test). `Documents.Add` and the pipe command restored the window too (round B: an outside helper had to re-minimize it 7 times). Keys typed then go into AutoCAD. For now, put WindowState 2 again after each Open or Add. A real fix is not tested yet. A Popen'd MEP probably does the same; not checked.
- **Round B's draw left no pipe:** wait_idle was True, nothing new was in model space and no dialog came up. During that draw, an outside helper was minimizing the window by ShowWindow (twice mid-command) and another process read Caption and HWND. The re-test drew 3 of 3: alone, with 29 reads (17 refused) from another process, and with 24 ShowWindow minimizes. Not reproduced; cause unknown.
- **Lifetime:** with the holder stopped and every reference released, AutoCAD B did not exit in 45 s, and no COM path reached it because it was not first in the ROT. Only a kill by pid ended it. Keep the holder running until `quit_unsaved(pid)`.
- **The ROT refuses a proxy:** `IRunningObjectTable::Register` with another process's object fails E_INVALIDARG (-2147024809), with flags 1 and 0. So a holder cannot re-register AutoCAD itself. A locator works: the holder's own object, whose App property hands back AutoCAD. Callers get AutoCAD's object straight from AutoCAD, and it kept working after the holder exited (prototype 8 of 8, pid test part 3).
- **LastLaunchedProduct does not pick the product:** round A set it to ACAD and still got MEP. CurVer was `ACAD-A106:409` in every launch; a launch with CurVer `ACAD-A101:409` was not tried. `launch()` sets MEPREG (CurVer, LastLaunchedProduct, MEP default profile) by default and puts the old values back after its AutoCAD exits.
- No dialogs in any instance. After the kill of B, the next launch showed no Drawing Recovery dialog.
- **Registry:** each holder put its values back after its AutoCAD exited. The startup values, plus FileDialog and CommandDialogs (the registry name of CMDDIA) under A101 and A106, ended as found. FILEDIA 1 and CMDDIA 1 read inside both MEP instances (uservars save and restore).
- **Tool shells see the real HKCU** (checked because a private copy was suspected). A throwaway `HKCU\Software\ClaudeRegProbe` value written from a tool shell was read by a WMI-started outside process (`Win32_Process.Create`), and the reverse. Back to back, inside and outside reads of the AutoCAD values agreed. Values do change between reads, though, while other processes open and close MEP windows, so read them right before you rely on them.
- **Slip, fixed:** the re-test turned LOGFILEMODE on, and `uservars.restore()` failed because no drawing was active after Close ("Failed to get the Document object"). LOGFILEMODE is stored at `HKCU\...\R26.0\ACAD-A106:409\Profiles\AutoCAD MEP (US Imperial)\General\LogFileOpen`; it was set back to 0 by registry. Run `uservars.restore()` before closing the last drawing.
- The `-AECBPIPEADD` prompts in a COM-launched MEP match the 2026-10-17 list: `Start point or [Routing preference/SYstem/SIze/Lock size/Tolerance off/Elevation/Justification/Slope/Match/preFerences]`, `Routing Preference name, index number or [?] <Glued>`, `Nominal Size or [?] <4">`, `Next point or [... Compass/Plane/roTAte/Slope/Match/New run/preFerences/Undo]`.

## Focus fixes tried
A sampler read the foreground window every 10 ms, plus the MEP window's state. No registry value was written in this part.

- **launch(reg=None):** MEP in 50 s with no registry writes. launch() now defaults to it.
- **Hidden (Visible False):** IsWindowVisible went False. Then `Documents.Open` made the window visible and normal again. The foreground stayed on the user's app that time. Not a fix. (`mepcom_focus_test.py`; that run stopped on a script bug right after Open, since fixed.)
- **Minimized:** in the re-test, AutoCAD was already the foreground window when draw 3's outside helper minimized it with SW_SHOWMINNOACTIVE. It stayed the foreground window while minimized, so a minimized window can keep the keyboard.
- **Its own Windows desktop:** `win32service.CreateDesktop` plus `STARTUPINFO.lpDesktop`, then `acad.exe /Automation -Embedding /ld ... /p "AutoCAD MEP (US Imperial)" /product MEP` (`mepcom_desktop_test.py`).
  - MEP came up there in about 45 s with Drawing1. Nothing appeared on the user's desktop and the user's foreground never changed. A Python test window (`scripts/2026-10-18-com-launch/desk_probe.py`) showed the same, and PostMessage reaches dialogs on that desktop.
  - **But COM could not reach that instance:** the ROT listed no AutoCAD after 90 s. CoCreateInstance (`mepcom_factory_probe.py`) did not use its class factory; it started another acad.exe (31992) on the user's desktop in 30 s. That instance's window was visible but took no focus, and it was quit at once.
  - The desktop instance was closed by WM_CLOSE posted to its frame on that desktop.
- Inference, not tested here: Windows lets a background process take the foreground only when the user has been idle past the foreground lock timeout, which fits the steal seen in the re-test and none while the user was active.
- **Not tested:** running the holder itself on the second desktop, so that its CoCreateInstance starts AutoCAD there (if DCOM starts the server on the caller's desktop) and its locator serves it.

## mepcom.py now
```python
a, pid = mepcom.launch()        # new MEP by COM, bound, minimized, answering; about 45 s
...                             # every helper (doc, var, send, aec, wait_idle, DialogGuard) talks to this pid only
mepcom.quit_unsaved(pid)        # after saving: closes drawings unsaved, Quit, kills that pid only if it hangs
```
- `launch(reg=MEPREG, timeout=420, bind_it=True)` starts the holder (`py mepcom.py --hold <state>`, no window). The holder sets the registry values, calls CoCreateInstance, maps HWND to pid, minimizes the window, and registers the locator `!mepcom.acad.<pid>`. It then waits for that acad.exe to exit, removes the locator, and puts the registry back. If the launch fails, it kills only a new `/Automation` acad.exe and raises.
- `app(pid)` tries the locator first, then the shared-entry walk as before. `instances()` and `py mepcom.py` (PID map) include launch() instances. `_held_pids()` lists them.
- Unbound calls are unchanged (GetActiveObject; dialogs of every acad.exe). A bound pid with no locator works as before.

## Not tested
- Two sessions really working at once, each with its own `launch()`.
- A fix for the Open and Add focus steal: keep the app hidden (Visible False) while working, re-minimize after each Open, or open drawings another way.
- A launch with CurVer `ACAD-A101:409`.
- Why round B's draw made no pipe.
