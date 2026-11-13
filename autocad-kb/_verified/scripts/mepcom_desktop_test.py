"""Second-desktop test (2026-10-18): run MEP on its own Windows desktop so it can never show a window on the user's desktop
or take the user's foreground, and drive it by COM.

The focus test found Documents.Open restores a minimized MEP window and shows a hidden one (Visible False), and the
re-test saw it take the foreground. A process started on another desktop (CreateDesktop, STARTUPINFO.lpDesktop) keeps
all its windows there (probe with a Python window: none on the user's desktop, foreground unchanged, dialogs reachable
by PostMessage). Here: acad.exe /Automation -Embedding plus the MEP switches on desktop mepcom_<pid>; a 10 ms sampler
records the user's foreground window and any acad window on that desktop; Documents.Open, Add, Activate, SendCommand and
one -AECBPIPEADD run through the shared ROT entry (it is the only AutoCAD). Last, CoCreateInstance: does COM hand back
this already-running instance (its class factory) or start another one?
One MEP launch (plus one by COM only if the class factory is not used). No AutoCAD registry value is written.
usage: py -3.14 mepcom_desktop_test.py <work_dir>        (refuses to run while any acad.exe runs)
"""
import json, os, shutil, subprocess, sys, threading, time, winreg
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import pythoncom, win32api, win32con, win32event, win32gui, win32process, win32service

W = os.path.abspath(sys.argv[1])
os.makedirs(W, exist_ok=True)
ACAD = r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe"
AECBASE = r"C:\Program Files\Autodesk\AutoCAD 2027\AecBase.dbx"
SRC = r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg"
LOGP = os.path.join(W, "desktop_test.log")
if os.path.exists(LOGP):
    os.remove(LOGP)
CHECKS, R, EV = [], {}, []
STEP = ["start"]
PIDS = set()                                            # this test's acad.exe pids


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    open(LOGP, "a", encoding="utf-8").write(s + "\n")


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    log("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + str(detail)) if detail != "" else ""))


def on_user_desktop():
    """Visible top-level windows on the user's (this thread's) desktop owned by our acad.exe pids."""
    out = []

    def cb(h, _):
        if win32process.GetWindowThreadProcessId(h)[1] in PIDS and win32gui.IsWindowVisible(h):
            out.append((h, win32gui.GetWindowText(h)[:40]))
        return True
    win32gui.EnumWindows(cb, None)
    return out


class Sampler(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.stop, self.last, self.n = False, None, 0

    def run(self):
        while not self.stop:
            h = win32gui.GetForegroundWindow()
            fp = win32process.GetWindowThreadProcessId(h)[1] if h else None
            mine = len(on_user_desktop()) if self.n % 10 == 0 else (self.last[3] if self.last else 0)
            st = (fp, win32gui.GetWindowText(h)[:40] if h else "", mine)
            if self.last is None or st != self.last[1:]:
                EV.append((round(time.time(), 3), STEP[0]) + st)
                self.last = (time.time(),) + st
            self.n += 1
            time.sleep(0.01)


def bad_since(t):
    """Samples since t (with the state in force at t) where our acad owned the foreground or had a window on the user's desktop."""
    before = [e for e in EV if e[0] < t]
    return [e for e in before[-1:] + [e for e in EV if e[0] >= t] if e[2] in PIDS or e[4]]


class DeskGuard(threading.Thread):
    """Log and cancel dialogs of our acad.exe on the second desktop (EnumWindows cannot see that desktop)."""
    def __init__(self, hd):
        super().__init__(daemon=True)
        self.hd, self.stop, self.seen, self.first = hd, False, [], {}

    def run(self):
        while not self.stop:
            try:
                hs = self.hd.EnumDesktopWindows()
            except Exception:
                hs = []
            for h in hs:
                h = int(h)
                try:
                    if win32gui.GetClassName(h) != "#32770" or not win32gui.IsWindowVisible(h):
                        continue
                    if win32process.GetWindowThreadProcessId(h)[1] not in PIDS:
                        continue
                except Exception:
                    continue
                if h not in self.first:
                    self.first[h] = time.time()
                    texts = []
                    win32gui.EnumChildWindows(h, lambda c, _: texts.append(win32gui.GetWindowText(c)) or True, None)
                    self.seen.append((win32gui.GetWindowText(h), [x for x in texts if x][:8]))
                    log("DIALOG on the second desktop:", self.seen[-1])
                win32gui.PostMessage(h, win32con.WM_COMMAND, win32con.IDCANCEL, 0)
                if time.time() - self.first[h] > 3:
                    win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.5)


def step(name):
    STEP[0] = name
    log("--", name)


def users1(doc, expr, secs=20):
    m.call(doc, "SetVariable", "USERS1", "")
    m.call(doc, "SendCommand", '(setvar "USERS1" %s) (princ)\n' % expr)
    t = time.time()
    while time.time() - t < secs:
        try:
            v = m.call(doc, "GetVariable", "USERS1")
            if v:
                return v
        except pythoncom.com_error:
            pass
        time.sleep(0.5)
    return None


def alive(pid):
    try:
        h = win32api.OpenProcess(0x00100000, False, pid)
    except Exception:
        return False
    return win32event.WaitForSingleObject(h, 0) != win32event.WAIT_OBJECT_0


REGV = [(m.REG, "CurVer"), (m.REG, "LastLaunchedProduct"), (m.REG + r"\ACAD-A106:409\Profiles", "")]


def reg_read():
    out = {}
    for sub, n in REGV:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as k:
                out[sub + "|" + n] = winreg.QueryValueEx(k, n)[0]
        except OSError:
            out[sub + "|" + n] = None
    return out


running = m._acad_pids()
if running:
    raise SystemExit("acad.exe %s is running: wait until CAD is free" % sorted(running))
REG0 = reg_read()
NAME = "mepcom_%d" % os.getpid()
hd = win32service.CreateDesktop(NAME, 0, win32con.GENERIC_ALL, None)
S = Sampler()
S.start()
G = DeskGuard(hd)
G.start()
pid = pid2 = None
try:
    step("launch on desktop " + NAME)
    si = win32process.STARTUPINFO()
    si.lpDesktop = "WinSta0\\" + NAME
    cmd = '"%s" /Automation -Embedding /ld "%s" /p "AutoCAD MEP (US Imperial)" /product MEP /language en-US /nologo' % (ACAD, AECBASE)
    t0 = time.time()
    hp, ht, pid, tid = win32process.CreateProcess(None, cmd, None, None, False, 0, None, None, si)
    PIDS.add(pid)
    log("acad.exe pid %d on %s: %s" % (pid, si.lpDesktop, cmd))
    a = None
    while time.time() - t0 < 360 and a is None:
        if not alive(pid):
            raise SystemExit("acad.exe %d exited during start" % pid)
        try:
            x = m.app(pid)                              # the shared ROT entry: it is the only AutoCAD
            m.get(m.get(x, "Documents"), "Count")
            a = x
        except Exception:
            time.sleep(2)
    if a is None:
        raise SystemExit("acad.exe %d never answered COM in 360 s" % pid)
    m.bind(pid)
    R["answer_s"] = round(time.time() - t0, 1)
    R["profile"] = m.get(m.get(m.get(a, "Preferences"), "Profiles"), "ActiveProfile")
    R["window"] = {"Visible": m.get(a, "Visible"), "WindowState": m.get(a, "WindowState")}
    log("answered COM after %.0f s: profile %r, %s, caption %r" % (R["answer_s"], R["profile"], R["window"], m.get(a, "Caption")))
    check("MEP on the second desktop answers COM (profile MEP)", "MEP" in R["profile"], R["profile"])
    check("the start put nothing on the user's desktop and took no foreground", not bad_since(t0), bad_since(t0)[:3])

    docs = m.get(a, "Documents")
    work = os.path.join(W, "rp_desk.dwg")
    shutil.copyfile(SRC, work)
    step("Documents.Open")
    t = time.time()
    doc = m.call(docs, "Open", work)
    m.wait_idle(120)
    check("Documents.Open: nothing on the user's desktop, no foreground", not bad_since(t), bad_since(t)[:3])
    step("Documents.Add")
    t = time.time()
    nd = m.call(docs, "Add")
    m.wait_idle(120)
    check("Documents.Add: nothing on the user's desktop, no foreground", not bad_since(t), bad_since(t)[:3])
    step("Activate, SendCommand, -AECBPIPEADD")
    t = time.time()
    m.call(doc, "Activate")
    m.wait_idle(60)
    ping = users1(doc, '"PING"')
    check("SendCommand runs on the second desktop", ping == "PING", ping)
    m.call(doc, "SetVariable", "TILEMODE", 1)
    ms = m.get(doc, "ModelSpace")
    n0 = m.get(ms, "Count")
    m.send('_-AECBPIPEADD\nR\nGlued\nSI\n4"\n_non\n0,0,120\n_non\n240,0,120\n\n')
    time.sleep(1)
    idle = m.wait_idle(90)
    pipes = [round(m.get(e, "Length"), 4) for e in (m.call(ms, "Item", i) for i in range(n0, m.get(ms, "Count")))
             if m.get(e, "ObjectName") == "AecbDbPipe"]
    R["pipe"] = {"idle": idle, "pipes": pipes}
    check("-AECBPIPEADD drew one 240 in. pipe on the second desktop", idle and pipes == [240.0], R["pipe"])
    check("Activate and the command: nothing on the user's desktop, no foreground", not bad_since(t), bad_since(t)[:3])
    step("Close")
    t = time.time()
    m.call(nd, "Close", False)
    m.call(doc, "Close", False)
    m.wait_idle(60)
    check("Close: nothing on the user's desktop, no foreground", not bad_since(t), bad_since(t)[:3])
    doc = nd = ms = docs = None

    step("CoCreateInstance while it runs")
    before = m._acad_pids()
    t = time.time()
    o = pythoncom.CoCreateInstance(m.CLSID, None, pythoncom.CLSCTX_LOCAL_SERVER, pythoncom.IID_IDispatch)
    tid2, pid2 = win32process.GetWindowThreadProcessId(m.get(o, "HWND"))
    R["cocreate"] = {"secs": round(time.time() - t, 1), "pid": pid2, "new_pids": sorted(m._acad_pids() - before)}
    log("CoCreateInstance: %s" % R["cocreate"])
    if pid2 == pid:
        check("CoCreateInstance handed back the instance on the second desktop (its class factory)", True, R["cocreate"])
    else:
        PIDS.add(pid2)
        check("CoCreateInstance handed back the instance on the second desktop (its class factory)", False,
              "it started another acad.exe %d instead" % pid2)
        try:
            m.call(o, "Quit")
        except Exception:
            pass
    o = None
finally:
    STEP[0] = "quit"
    m.bind(None)
    a = None
    for p in sorted(PIDS):
        if alive(p):
            log("quit_unsaved %d: %s" % (p, m.quit_unsaved(p, 90)))
    time.sleep(1)
    S.stop = True
    G.stop = True
    time.sleep(1)
    R["dialogs"] = G.seen
    try:
        hd.CloseDesktop()
    except Exception as e:
        log("CloseDesktop:", e)
    R["registry_changes"] = {k: (REG0[k], v) for k, v in reg_read().items() if v != REG0[k]}
    log("registry changes seen (not touched):", R["registry_changes"] or "none")
    check("no acad.exe left", not m._acad_pids(), sorted(m._acad_pids()))
    R["events"] = EV
    R["checks"] = CHECKS
    json.dump(R, open(os.path.join(W, "desktop_results.json"), "w"), indent=1, default=str)
    log("The user's foreground and our windows on the user's desktop (changes):")
    for e in EV:
        log("   %.3f %-36s fg pid %s %r | our windows on the user's desktop %s" % e)
    log("RESULT: %d of %d checks passed" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
