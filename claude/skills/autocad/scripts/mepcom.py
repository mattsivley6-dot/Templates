"""Raw-IDispatch helpers for AutoCAD MEP 2027 (pywin32 name lookup fails on its objects).
Two acad.exe at once: bind(pid) ties every helper here to one instance. Nothing bound = plain GetActiveObject.
launch() starts a NEW AutoCAD by COM that app(pid) reaches from any later script, even while another runs.
Run it as a script (py -3.14 mepcom.py) to print the PID-to-instance map (read only)."""
import win32com.client, pythoncom, pywintypes, win32process, time, sys
G, M, P = pythoncom.DISPATCH_PROPERTYGET, pythoncom.DISPATCH_METHOD, pythoncom.DISPATCH_PROPERTYPUT
PROGID = "AutoCAD.Application"
PID = None                              # set by bind()
MK_E_UNAVAILABLE = -2147221021          # "Operation unavailable": what GetActiveObject raises when no AutoCAD is registered
CLSID = "{E76F49EB-7DAE-4682-ADE6-6C12ECA76DD7}"  # AutoCAD.Application(.26); LocalServer32 = "acad.exe /Automation"
HELD = "mepcom.acad."                   # ROT item !mepcom.acad.<pid>: the locator a launch() holder keeps for its acad.exe
def bind(pid):
    """Tie app, doc, var, send, aec, wait_idle, dialogs and DialogGuard to one acad.exe, e.g. bind(proc.pid). bind(None) undoes it."""
    global PID
    PID = pid
def app(pid=None):
    """The AutoCAD Application. No pid and nothing bound: GetActiveObject, exactly as before.
    With a pid: that acad.exe or a com_error (busy, or MK_E_UNAVAILABLE), never another instance."""
    pid = PID if pid is None else pid
    if pid is None:
        return win32com.client.GetActiveObject(PROGID)._oleobj_
    a = _held(pid)                                      # started by launch(): reached through its holder's locator
    if a is not None:
        return a
    found = _rot()
    for p, a in found:
        if p == pid:
            return a
    for p, a in found:
        if a is None:
            raise p                                     # busy: callers retry as they do today
    raise pythoncom.com_error(MK_E_UNAVAILABLE, "acad.exe %s is not the AutoCAD that COM reaches (it reaches %s); "
                              "only the first one registered is reachable" % (pid, sorted({p for p, a in found}) or "none"), None, None)
def _rot():
    """[(pid, application)] for each AutoCAD entry in the Running Object Table, (com_error, None) for one too busy to give
    its HWND. Every entry, like GetActiveObject, gives the FIRST AutoCAD registered: while it runs, a second acad.exe
    cannot be reached by COM at all (Autodesk help on GetObject; tested with two stand-in objects under one !{CLSID} name)."""
    rot, ctx, out = pythoncom.GetRunningObjectTable(), pythoncom.CreateBindCtx(0), []
    want = ("!" + str(pywintypes.IID(PROGID))).upper()
    for mk in rot.EnumRunning():
        try:
            if mk.GetDisplayName(ctx, None).upper() != want:
                continue
        except pythoncom.com_error:
            continue
        try:
            a = rot.GetObject(mk).QueryInterface(pythoncom.IID_IDispatch)
            tid, pid = win32process.GetWindowThreadProcessId(get(a, "HWND"))
        except pythoncom.com_error as e:                # call rejected (busy), or it just quit
            out.append((e, None)); continue
        if tid:                                         # HWND 0 (starting up) gives thread 0 and a junk pid
            out.append((pid, a))
    return out
def _held(pid):
    """Application of acad.exe <pid> through the ROT locator of its launch() holder, or None (no holder for it)."""
    try:
        loc = pythoncom.GetRunningObjectTable().GetObject(pythoncom.CreateItemMoniker("!", HELD + str(pid)))
        return get(loc.QueryInterface(pythoncom.IID_IDispatch), "App")
    except pythoncom.com_error:
        return None
def _held_pids():
    """pids of the acad.exe that have a launch() holder locator in the ROT."""
    rot, ctx, out = pythoncom.GetRunningObjectTable(), pythoncom.CreateBindCtx(0), []
    for mk in rot.EnumRunning():
        try:
            n = mk.GetDisplayName(ctx, None)
        except pythoncom.com_error:
            continue
        if n.startswith("!" + HELD) and n[len(HELD) + 1:].isdigit():
            out.append(int(n[len(HELD) + 1:]))
    return out
def instances():
    """{pid: Application} for the acad.exe COM can reach (the first one registered, plus every launch() instance).
    `py -3.14 mepcom.py` prints the whole PID map."""
    out = {p: a for p, a in _rot() if a is not None}
    for p in _held_pids():
        a = _held(p)
        if a is not None:
            out[p] = a
    return out
def get(o, name, *args):
    return o.Invoke(o.GetIDsOfNames(name), 0, G, True, *args)
def call(o, name, *args):
    for i in range(60):
        try:
            return o.Invoke(o.GetIDsOfNames(name), 0, M, True, *args)
        except pythoncom.com_error as e:
            if e.hresult in (-2147418111, -2147417846):   # call rejected / busy
                time.sleep(1); continue
            raise
    raise RuntimeError("busy too long")
def doc():
    return get(app(), "ActiveDocument")
def var(name):
    return call(doc(), "GetVariable", name)
def send(cmd):
    call(doc(), "SendCommand", cmd)
PUT = pythoncom.DISPATCH_PROPERTYPUT
def put(o, name, val):
    """Set a property over raw IDispatch (e.g. put(pipe, "Layer", "M-CHWS"))."""
    return o.Invoke(o.GetIDsOfNames(name), 0, PUT, False, val)
def pt(x, y, z):
    """Point for MEP COM writes (StartPoint, EndPoint, Break): a typed double array. A plain tuple fails E_INVALIDARG (verified)."""
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (float(x), float(y), float(z)))
def aec(progid, d=None):
    """AEC/MEP database object bound to a drawing: aec("AecX.AecbPipeDatabase.8.9") -> PipeSystemDefs, PipeStyles...;
    aec("AecX.AecbDatabase.8.9") -> Graphs. Version 8.9 = AutoCAD 2027 (verified)."""
    o = call(app(), "GetInterfaceObject", progid)
    call(o, "Init", get(d or doc(), "Database"))
    return o
def names(coll, attr="Name"):
    """Names of every item in an AEC collection (Count + Item(i))."""
    return [get(call(coll, "Item", i), attr) for i in range(get(coll, "Count"))]
def connected(ent):
    """[(connector index, location, [(ObjectName, Handle) ...])] for an MEP object. Connectors.Count over-reports by one: stop at the first bad Item."""
    out, cons = [], get(ent, "Connectors")
    for i in range(get(cons, "Count")):
        try:
            c = call(cons, "Item", i)
            loc = get(c, "Location")
        except pythoncom.com_error:
            break
        mem = get(c, "ConnectedMembers") or ()
        out.append((i, loc, [(get(x, "ObjectName"), get(x, "Handle")) for x in mem]))
    return out
def wait_idle(timeout=600):
    t = time.time()
    while time.time() - t < timeout:
        try:
            st = get(app(), "GetAcadState")
        except Exception:
            st = None
        try:
            if st is None:
                st = call(app(), "GetAcadState")
            if get(st, "IsQuiescent"):
                return True
        except pythoncom.com_error:
            pass
        time.sleep(0.5)
    return False

# ---- dialog guard: report and cancel any modal dialog MEP raises, without touching mouse or keyboard
import threading, win32gui, win32process, win32con
def _acad_pids():
    import subprocess
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq acad.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    return {int(l.split('","')[1]) for l in out.splitlines() if l.startswith('"acad')}
def dialogs(pids=None):
    """[(hwnd, title, texts)] for visible dialogs of the given acad.exe pid or pids. Default: the bound pid, else every acad.exe (as before)."""
    if pids is None:
        pids = _acad_pids() if PID is None else {PID}
    else:
        pids = {pids} if isinstance(pids, int) else set(pids)
    found = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h) and win32gui.GetClassName(h) == "#32770":
            if win32process.GetWindowThreadProcessId(h)[1] in pids:
                texts = []
                def cc(c, _):
                    t = win32gui.GetWindowText(c)
                    if t: texts.append(t)
                    return True
                try: win32gui.EnumChildWindows(h, cc, None)
                except Exception: pass
                found.append((h, win32gui.GetWindowText(h), texts[:12]))
        return True
    win32gui.EnumWindows(cb, None)
    return found
class DialogGuard(threading.Thread):
    """Poll for MEP dialogs; log each one and press its Cancel (IDCANCEL) by message.
    pid: only that acad.exe's dialogs. Default: the bound pid, else every acad.exe (as before)."""
    def __init__(self, cancel=True, period=0.5, pid=None):
        super().__init__(daemon=True); self.cancel, self.period, self.seen, self.stop = cancel, period, [], False
        pid = PID if pid is None else pid
        self.pids = None if pid is None else {pid}
    def run(self):
        while not self.stop:
            for h, title, texts in dialogs(self.pids):
                if h not in [s[0] for s in self.seen]:
                    self.seen.append((h, title, texts))
                if self.cancel:
                    win32gui.PostMessage(h, win32con.WM_COMMAND, win32con.IDCANCEL, 0)
            time.sleep(self.period)

# ---- launch(): a NEW AutoCAD for this session over COM, reachable by pid from any later script
REG = r"Software\Autodesk\AutoCAD\R26.0"
MEPREG = {REG: {"CurVer": "ACAD-A106:409", "LastLaunchedProduct": "MEP"},
          REG + r"\ACAD-A106:409\Profiles": {"": "AutoCAD MEP (US Imperial)"}}
def launch(reg=None, timeout=420, bind_it=True, require="MEP"):
    """Start a NEW acad.exe by COM and return (Application, pid); binds pid unless bind_it=False. require: text the
    active profile must contain ("MEP"), else that acad.exe is quit and RuntimeError raised; None skips the check.
    A holder process (py mepcom.py --hold) sets the HKCU values in reg, if any (default none: write no AutoCAD registry
    values unless asked; old values go back after it exits), calls CoCreateInstance
    (Autodesk documents that CreateObject tries to start a new instance) and puts a locator for the new instance in
    the ROT as !mepcom.acad.<pid>: its own small object whose App property hands back AutoCAD (the ROT refuses a proxy,
    E_INVALIDARG). app(pid) uses it, so this works while another AutoCAD holds the shared !{CLSID} entry. When that
    acad.exe exits, the holder removes the locator and puts the old registry values back.
    Live test: a new MEP every time (also while another acad.exe ran), 42 s, "acad.exe /Automation -Embedding"
    under svchost, MEP profile and modules with no /ld /p /product. Its window opens NORMAL (no focus taken); the holder
    minimizes it through COM. Documents.Open and Documents.Add restore the window, also from Visible False, and Open
    made it the FOREGROUND window once (keys the user types then land in AutoCAD). No fix is proven: set
    WindowState 2 again after each, and know that a minimized window can stay the active one. It does NOT exit when released:
    end it with quit_unsaved(pid) while the holder runs, or it is left running where no COM call can reach it (only a
    kill by pid ends it)."""
    import json, os, subprocess, sys, tempfile
    d = tempfile.mkdtemp(prefix="mepcom_hold_")
    state = os.path.join(d, "holder.jsonl")
    with open(state + ".cfg", "w", encoding="utf-8") as f:
        json.dump({"reg": reg or {}}, f)
    before, t0 = _acad_pids(), time.time()
    h = subprocess.Popen([sys.executable, os.path.abspath(__file__), "--hold", state],
                         creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=open(state + ".err", "w"), close_fds=True)
    ev = {}
    while time.time() - t0 < timeout:
        evs = _events(state)
        ev = evs[-1] if evs else {}
        if ev.get("event") in ("ready", "error") or h.poll() is not None:
            break
        time.sleep(0.5)
    if ev.get("event") == "ready":
        a = _held(ev["pid"])
        while a is not None and time.time() - t0 < timeout:
            try:                                        # right after start AutoCAD rejects calls for a few seconds
                get(get(a, "Documents"), "Count")
                prof = get(get(get(a, "Preferences"), "Profiles"), "ActiveProfile")
            except pythoncom.com_error as e:
                if e.hresult not in (-2147418111, -2147417846):
                    raise
                time.sleep(1)
                continue
            if require and require not in prof:         # e.g. CurVer now points at plain AutoCAD: do not hand it out
                a = None
                end = quit_unsaved(ev["pid"], 60)
                raise RuntimeError("launch() got AutoCAD with profile " + repr(prof) + ", not " + require + " (" + end +
                                   " it). Start MEP once by hand, or pass reg=MEPREG to set CurVer, LastLaunchedProduct"
                                   " and the MEP profile for the launch")
            if bind_it:
                bind(ev["pid"])
            return a, ev["pid"]
    try:                                                # failed: stop our holder; kill only an acad.exe this launch started
        h.kill()
    except Exception:
        pass
    killed = []
    for p in sorted(_acad_pids() - before):
        if "/automation" in _cmdline(p).lower():
            subprocess.run(["taskkill", "/PID", str(p), "/F"], capture_output=True)
            killed.append(p)
    raise RuntimeError("launch() failed after %.0f s: last holder event %s; killed our acad.exe %s; holder log %s"
                       % (time.time() - t0, ev or "none", killed, state))
def quit_unsaved(pid=None, timeout=120):
    """End acad.exe <pid> (default: the bound one): close every drawing WITHOUT saving (save first), Quit, wait, and
    kill that pid only if it is still running. Returns "quit", "killed" or "not running"."""
    import subprocess, win32api, win32event
    pid = PID if pid is None else pid
    if pid is None:
        raise ValueError("quit_unsaved() needs a pid (or bind() first)")
    try:
        hp = win32api.OpenProcess(0x00100000, False, pid)          # SYNCHRONIZE
    except pywintypes.error:
        return "not running"
    sent = False
    try:
        a = app(pid)
    except Exception:
        a = None                                        # COM cannot reach it: no Quit can be sent, so kill at once
    if a is not None:
        try:
            ds = get(a, "Documents")
            for i in range(get(ds, "Count") - 1, -1, -1):
                try:
                    call(call(ds, "Item", i), "Close", False)
                except Exception:
                    pass
        except Exception:
            pass
        sent = True
        try:
            call(a, "Quit")
        except Exception:
            pass
    a = ds = None
    if win32event.WaitForSingleObject(hp, int((timeout if sent else 2) * 1000)) == win32event.WAIT_OBJECT_0:
        return "quit"
    subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
    return "killed"
def _events(state):
    import json, os
    if not os.path.exists(state):
        return []
    return [json.loads(l) for l in open(state, encoding="utf-8") if l.strip()]
def _cmdline(pid):
    import subprocess
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Process -Filter 'ProcessId=%d').CommandLine" % pid],
                       capture_output=True, text=True)
    return r.stdout.strip()
def _reg_set(reg):
    """Set HKCU string values {subkey: {name: value}}; return [[subkey, name, old value or None], ...]."""
    import winreg
    old = []
    for sub, vals in reg.items():
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, sub, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as k:
            for n, v in vals.items():
                try:
                    o = winreg.QueryValueEx(k, n)[0]
                except OSError:
                    o = None
                old.append([sub, n, o])
                winreg.SetValueEx(k, n, 0, winreg.REG_SZ, v)
    return old
def _reg_put_back(old):
    import winreg
    for sub, n, o in old:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub, 0, winreg.KEY_SET_VALUE) as k:
            if o is None:
                try:
                    winreg.DeleteValue(k, n)
                except OSError:
                    pass
            else:
                winreg.SetValueEx(k, n, 0, winreg.REG_SZ, o)
def _event(state, **k):
    import json, os
    k["t"], k["holder"] = round(time.time(), 2), os.getpid()
    with open(state, "a", encoding="utf-8") as f:
        f.write(json.dumps(k) + "\n")
def _hold(state):
    """The launch() holder: py mepcom.py --hold <state.jsonl>. Logs registry/created/ready/error/exit events there."""
    import json
    old = _reg_set(json.load(open(state + ".cfg", encoding="utf-8"))["reg"])
    _event(state, event="registry", old=old)
    t0 = time.time()
    try:
        a = pythoncom.CoCreateInstance(CLSID, None, pythoncom.CLSCTX_LOCAL_SERVER, pythoncom.IID_IDispatch)
    except pythoncom.com_error as e:
        _event(state, event="error", step="CoCreateInstance", hresult=e.hresult, msg=e.strerror, secs=round(time.time() - t0, 1))
        _reg_put_back(old)
        return
    _event(state, event="created", secs=round(time.time() - t0, 1))
    tid = pid = 0
    while time.time() - t0 < 600 and not tid:
        try:
            tid, pid = win32process.GetWindowThreadProcessId(get(a, "HWND"))   # HWND 0 while starting: thread 0
        except pythoncom.com_error:
            pass
        if not tid:
            time.sleep(0.5)
    if not tid:
        _event(state, event="error", step="HWND", secs=round(time.time() - t0, 1))
        _reg_put_back(old)
        return
    for i in range(120):                                # a COM launch opens a NORMAL window (no focus): minimize it
        try:                                            # through AutoCAD, which then keeps it minimized
            put(a, "WindowState", 2)
            break
        except pythoncom.com_error:
            time.sleep(0.5)
    _event(state, event="minimized", tries=i + 1, secs=round(time.time() - t0, 1))
    _serve(a, pid, state, old, t0)
def _serve(a, pid, state, old=(), t0=None):
    """Keep Application <a> of process <pid> reachable from any process: a locator in the ROT as !mepcom.acad.<pid>
    (this process's own object; its App property hands back <a>) until <pid> exits or <state>.stop appears. Then remove
    it, and once <pid> has exited put the registry values in <old> back (after a stop file, wait up to 120 s for that)."""
    import os, win32api, win32event
    import win32com.server.util

    class Locator:
        _public_methods_ = []
        _public_attrs_ = _readonly_attrs_ = ["App", "Pid", "Holder"]
        App, Pid, Holder = a, pid, os.getpid()

    rot = pythoncom.GetRunningObjectTable()
    cookie = rot.Register(1, win32com.server.util.wrap(Locator()), pythoncom.CreateItemMoniker("!", HELD + str(pid)))
    _event(state, event="ready", pid=pid, secs=round(time.time() - t0, 1) if t0 else None)
    hp = win32api.OpenProcess(0x00100000, False, pid)              # SYNCHRONIZE
    why = None
    while why is None:
        if win32event.MsgWaitForMultipleObjects([hp], False, 1000, win32event.QS_ALLINPUT) == win32event.WAIT_OBJECT_0:
            why = "acad.exe exited"
        else:
            pythoncom.PumpWaitingMessages()
            if os.path.exists(state + ".stop"):
                why = "stop file"
    rot.Revoke(cookie)
    Locator.App = a = None
    exited = win32event.WaitForSingleObject(hp, 120000 if old else 0) == win32event.WAIT_OBJECT_0
    if exited:
        _reg_put_back(old)
    _event(state, event="exit", why=why, acad_exited=exited,
           registry="nothing set" if not old else ("put back" if exited else "left as set: acad.exe still running"))

if __name__ == "__main__" and sys.argv[1:2] == ["--hold"]:
    _hold(sys.argv[2])
elif __name__ == "__main__":                            # py -3.14 mepcom.py: print the PID-to-instance map (read only)
    found, running = _rot(), _acad_pids()
    reach = {p: a for p, a in found if a is not None}
    held = {p: _held(p) for p in _held_pids()}
    print("acad.exe running:", sorted(running), "| AutoCAD entries in the ROT:", len(found))
    for p in sorted(running | set(reach) | set(held)):
        if p in reach or held.get(p) is not None:
            o = reach.get(p) or held[p]
            try:
                info = "HWND %s | %s" % (get(o, "HWND"), get(o, "Caption"))
            except pythoncom.com_error as e:
                info = "busy (%s)" % e.hresult
            print("  pid %d: COM reaches it%s | %s" % (p, " through its launch() holder" if p in held else "", info))
        else:
            print("  pid %d: running, NOT reachable by COM (only the first AutoCAD in the ROT is)" % p)
    for p, a in found:
        if a is None:
            print("  ROT entry busy:", p)
    try:
        print("  unbound app() (GetActiveObject) gives pid", win32process.GetWindowThreadProcessId(get(app(), "HWND"))[1])
    except pythoncom.com_error as e:
        print("  unbound app() (GetActiveObject):", e)
