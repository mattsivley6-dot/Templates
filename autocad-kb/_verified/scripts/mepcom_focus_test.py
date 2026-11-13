"""Focus test (2026-10-18): can a COM-launched MEP open drawings and draw without ever taking the foreground?

The re-test (mepcom_comlaunch_retest.py) saw Documents.Open restore the minimized MEP window and make it the foreground
window. Here a sampler thread records the foreground window every 10 ms for the whole run, and every change of
IsWindowVisible / IsIconic of the MEP main window. One launch (launch(reg=None): no registry writes), then:
  mode "hidden":     Visible = False, then Documents.Open, Documents.Add, SendCommand, -AECBPIPEADD, Close
  mode "minimized":  only if "hidden" failed: WindowState 2 and Visible True, the same steps, re-minimized after each
The MEP instance is this test's own; nothing else is touched. No AutoCAD registry value is written.
usage: py -3.14 mepcom_focus_test.py <work_dir>        (refuses to run while any acad.exe runs)
"""
import json, os, shutil, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import pythoncom, win32con, win32gui, win32process

W = os.path.abspath(sys.argv[1])
os.makedirs(W, exist_ok=True)
SRC = r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg"
LOGP = os.path.join(W, "focus_test.log")
if os.path.exists(LOGP):
    os.remove(LOGP)
CHECKS, R, EV = [], {}, []


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    open(LOGP, "a", encoding="utf-8").write(s + "\n")


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    log("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + str(detail)) if detail != "" else ""))


class Sampler(threading.Thread):
    """Every 10 ms: foreground window's pid and title, and the MEP main window's visible/iconic state."""
    def __init__(self):
        super().__init__(daemon=True)
        self.stop, self.pid, self.hwnd, self.last = False, None, None, None

    def run(self):
        while not self.stop:
            h = win32gui.GetForegroundWindow()
            fp = win32process.GetWindowThreadProcessId(h)[1] if h else None
            st = (fp, win32gui.GetWindowText(h)[:50] if h else "",
                  bool(win32gui.IsWindowVisible(self.hwnd)) if self.hwnd else None,
                  bool(win32gui.IsIconic(self.hwnd)) if self.hwnd else None)
            if st != self.last:
                EV.append((round(time.time(), 3), STEP[0]) + st)
                self.last = st
            time.sleep(0.01)


STEP = ["start"]


def step(name):
    STEP[0] = name
    log("--", name)


def window(since):
    """Samples covering since..now: the state in force at <since> plus every change after it."""
    before = [e for e in EV if e[0] < since]
    return before[-1:] + [e for e in EV if e[0] >= since]


def stolen(since):
    """Samples in which our acad.exe owned the foreground window."""
    return [e for e in window(since) if e[2] == S.pid]


def shown(since, mode):
    """hidden: any sample with the window visible; minimized: any with it visible and NOT iconic (on screen)."""
    if mode == "hidden":
        return [e for e in window(since) if e[4] is True]
    return [e for e in window(since) if e[4] is True and e[5] is False]


def draw(doc, ms, y):
    n0 = m.get(ms, "Count")
    m.send('_-AECBPIPEADD\nR\nGlued\nSI\n4"\n_non\n0,%d,120\n_non\n240,%d,120\n\n' % (y, y))
    time.sleep(1)
    idle = m.wait_idle(90)
    out = []
    for i in range(n0, m.get(ms, "Count")):
        e = m.call(ms, "Item", i)
        if m.get(e, "ObjectName") == "AecbDbPipe":
            out.append(round(m.get(e, "Length"), 4))
    return idle, out


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


def run_mode(a, mode, y):
    """Open, Add, SendCommand and one pipe with the window in <mode>; True if AutoCAD never took the foreground."""
    t0 = time.time()
    hw = S.hwnd
    if mode == "hidden":
        m.put(a, "Visible", False)
    else:
        m.put(a, "WindowState", 2)                      # a fresh launch(): already minimized through COM
    time.sleep(0.5)
    log("%s: Visible %s, IsWindowVisible %s, IsIconic %s" % (mode, m.get(a, "Visible"), bool(win32gui.IsWindowVisible(hw)), bool(win32gui.IsIconic(hw))))
    work = os.path.join(W, "rp_%s.dwg" % mode)
    shutil.copyfile(SRC, work)
    docs = m.get(a, "Documents")
    step(mode + ": Documents.Open")
    t = time.time()
    doc = m.call(docs, "Open", work)
    m.wait_idle(120)
    R[mode + "_open"] = {"stolen": stolen(t), "shown": shown(t, mode)}   # fixed after an earlier run crashed here
    check("%s: Documents.Open did not take the foreground" % mode, not stolen(t), stolen(t)[:3])
    check("%s: Documents.Open did not show the window" % mode, not shown(t, mode), shown(t, mode)[:3])
    if mode != "hidden":
        m.put(a, "WindowState", 2)
    step(mode + ": Documents.Add")
    t = time.time()
    nd = m.call(docs, "Add")
    m.wait_idle(120)
    check("%s: Documents.Add did not take the foreground" % mode, not stolen(t), stolen(t)[:3])
    check("%s: Documents.Add did not show the window" % mode, not shown(t, mode), shown(t, mode)[:3])
    if mode != "hidden":
        m.put(a, "WindowState", 2)
    step(mode + ": Activate, SendCommand and -AECBPIPEADD")
    t = time.time()
    m.call(doc, "Activate")
    m.wait_idle(60)
    ping = users1(doc, '"PING"')
    check("%s: SendCommand runs" % mode, ping == "PING", ping)
    m.call(doc, "SetVariable", "TILEMODE", 1)
    idle, pipes = draw(doc, m.get(doc, "ModelSpace"), y)
    R[mode + "_pipe"] = {"idle": idle, "pipes": pipes}
    check("%s: -AECBPIPEADD drew one 240 in. pipe" % mode, idle and pipes == [240.0], pipes)
    check("%s: Activate and the command did not take the foreground" % mode, not stolen(t), stolen(t)[:3])
    check("%s: Activate and the command did not show the window" % mode, not shown(t, mode), shown(t, mode)[:3])
    step(mode + ": Close")
    t = time.time()
    m.call(nd, "Close", False)
    m.call(doc, "Close", False)
    m.wait_idle(60)
    check("%s: closing did not take the foreground" % mode, not stolen(t), stolen(t)[:3])
    ok = not stolen(t0)
    R[mode + "_never_foreground"] = ok
    return ok


running = m._acad_pids()
if running:
    raise SystemExit("acad.exe %s is running: wait until CAD is free" % sorted(running))
S = Sampler()
S.start()
pid = None
try:
    step("launch")
    t = time.time()
    a, pid = m.launch(reg=None)
    S.pid, S.hwnd = pid, m.get(a, "HWND")
    R["launch_s"] = round(time.time() - t, 1)
    R["profile"] = m.get(m.get(m.get(a, "Preferences"), "Profiles"), "ActiveProfile")
    log("launch(reg=None): pid %d in %.0f s, profile %r" % (pid, R["launch_s"], R["profile"]))
    check("launch(reg=None) gave MEP with no registry writes", "MEP" in R["profile"], R["profile"])
    check("the launch itself did not take the foreground", not stolen(t), stolen(t)[:3])
    guard = m.DialogGuard(cancel=True, pid=pid)
    guard.start()
    hidden_ok = run_mode(a, "hidden", 0)
    guard.stop = True
    R["dialogs"] = [(t_, x) for h, t_, x in guard.seen]
    if not hidden_ok:                                   # second launch: minimized, re-minimized after each Open/Add
        log("hidden mode let AutoCAD take the foreground; second launch for minimized mode")
        a = None
        log("quit_unsaved:", m.quit_unsaved(pid, 90))
        step("launch 2")
        a, pid = m.launch(reg=None)
        S.pid, S.hwnd = pid, m.get(a, "HWND")
        guard = m.DialogGuard(cancel=True, pid=pid)
        guard.start()
        run_mode(a, "minimized", 120)
        guard.stop = True
        R["dialogs_2"] = [(t_, x) for h, t_, x in guard.seen]
finally:
    STEP[0] = "quit"
    if pid:
        a = None
        log("quit_unsaved:", m.quit_unsaved(pid, 90))
    time.sleep(1)
    S.stop = True
    R["events"] = EV
    check("no acad.exe and no locator left", not m._acad_pids() and not m._held_pids(), (sorted(m._acad_pids()), m._held_pids()))
    R["checks"] = CHECKS
    json.dump(R, open(os.path.join(W, "focus_results.json"), "w"), indent=1, default=str)
    log("foreground and window changes:")
    for e in EV:
        log("   %.3f %-34s fg pid %s %r | visible %s iconic %s" % e)
    log("RESULT: %d of %d checks passed" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
