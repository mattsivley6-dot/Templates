"""Re-test (2026-10-18) after mepcom_comlaunch_test.py round B drew no pipe: one launch(), three -AECBPIPEADD draws.

Round B's draw ran while (1) another process read Caption and HWND from it and (2) an outside helper minimized its
window with ShowWindow each time AutoCAD restored it (7 times, twice during the draw). launch() now minimizes through
COM (WindowState 2) as soon as the window exists. Here:
  draw 1: nothing else touches AutoCAD
  draw 2: another process reads Caption and HWND every 0.2 s during the draw
  draw 3: another process sends ShowWindow(SW_SHOWMINNOACTIVE) to the main window every 0.3 s during the draw
The window state is recorded after launch, after Open and after each draw. LOGFILEMODE is on for the run (uservars
save() and restore() put it back) so each draw's command-line text is kept.
usage: py -3.14 mepcom_comlaunch_retest.py <work_dir>        (refuses to run while any acad.exe runs)
"""
import json, os, shutil, subprocess, sys, time, winreg
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import uservars
import pythoncom, win32con, win32gui, win32process

W = os.path.abspath(sys.argv[1])
os.makedirs(W, exist_ok=True)
SRC = r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg"
LOGP = os.path.join(W, "retest.log")
if os.path.exists(LOGP):
    os.remove(LOGP)
GC = r"\FixedProfile\General Configuration"
REGVALS = [(m.REG, "CurVer"), (m.REG, "LastLaunchedProduct"), (m.REG, "LastLaunchedLanguage"),
           (m.REG + r"\ACAD-A106:409\Profiles", ""), (m.REG + r"\ACAD-A101:409\Profiles", "")] + \
          [(m.REG + "\\" + k + GC, n) for k in ("ACAD-A106:409", "ACAD-A101:409") for n in ("FileDialog", "CommandDialogs")]
CHECKS, R = [], {}


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    open(LOGP, "a", encoding="utf-8").write(s + "\n")


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    log("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + str(detail)) if detail != "" else ""))


def reg_read():
    out = {}
    for sub, n in REGVALS:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as k:
                out[sub + "|" + n] = winreg.QueryValueEx(k, n)[0]
        except OSError:
            out[sub + "|" + n] = None
    return out


def fg():
    h = win32gui.GetForegroundWindow()
    return (win32process.GetWindowThreadProcessId(h)[1] if h else None), win32gui.GetWindowText(h)[:40]


def winstate(hw):
    try:
        ws = m.get(m.app(), "WindowState")
    except pythoncom.com_error as e:
        ws = "busy %s" % e.hresult
    return {"IsIconic": bool(win32gui.IsIconic(hw)), "IsWindowVisible": bool(win32gui.IsWindowVisible(hw)),
            "WindowState": ws, "foreground": fg()}


class Guard(m.DialogGuard):
    def run(self):
        first = {}
        while not self.stop:
            for h, title, texts in m.dialogs(self.pids):
                if h not in first:
                    first[h] = time.time()
                    self.seen.append((h, title, texts))
                    log("DIALOG", title, texts)
                win32gui.PostMessage(h, win32con.WM_COMMAND, win32con.IDCANCEL, 0)
                if time.time() - first[h] > 3:
                    win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
            time.sleep(self.period)


READER = r'''
import os, sys, time
sys.path.insert(0, os.environ["AUTOCAD_SKILL_SCRIPTS"])
import mepcom as m, pythoncom
a, ok, rej, t = m.app(%d), 0, 0, time.time()
while time.time() - t < %f:
    for k in ("Caption", "HWND"):
        try:
            m.get(a, k); ok += 1
        except pythoncom.com_error:
            rej += 1
    time.sleep(0.2)
print(ok, rej)
'''
MINIMIZER = r'''
import time, win32gui
h, n, t = %d, 0, time.time()
while time.time() - t < %f:
    win32gui.ShowWindow(h, 7); n += 1
    time.sleep(0.3)
print(n)
'''


def draw(doc, ms, y, side=None):
    """One 240 in. Glued 4 in. pipe at y; side = a helper process started just before the command."""
    n0, l0 = m.get(ms, "Count"), os.path.getsize(LOGFILE) if os.path.exists(LOGFILE) else 0
    helper = subprocess.Popen([sys.executable, "-c", side], stdout=subprocess.PIPE, text=True) if side else None
    if helper:
        time.sleep(0.8)
    m.send('_-AECBPIPEADD\nR\nGlued\nSI\n4"\n_non\n0,%d,120\n_non\n240,%d,120\n\n' % (y, y))
    time.sleep(1)
    idle = m.wait_idle(90)
    side_out = helper.communicate(timeout=60)[0].strip() if helper else None
    pipes = []
    for i in range(n0, m.get(ms, "Count")):
        e = m.call(ms, "Item", i)
        if m.get(e, "ObjectName") == "AecbDbPipe":
            pipes.append(round(m.get(e, "Length"), 4))
    txt = open(LOGFILE, "rb").read()[l0:].decode("utf-8", "ignore") if os.path.exists(LOGFILE) else ""
    return {"idle": idle, "new_pipes": pipes, "helper": side_out, "log": [l.strip() for l in txt.splitlines() if l.strip()][-14:]}


running = m._acad_pids()
if running:
    raise SystemExit("acad.exe %s is running: ask the user before launching another" % sorted(running))
REG0 = reg_read()
pid, LOGFILE, logmode_set = None, None, False
try:
    fg0, t0 = fg(), time.time()
    a, pid = m.launch(timeout=420)
    R["launch_s"] = round(time.time() - t0, 1)
    guard = Guard(cancel=True, pid=pid)
    guard.start()
    hw = m.get(a, "HWND")
    R["after_launch"] = winstate(hw)
    log("launch() pid %d in %.0f s; window after launch: %s; foreground before: %s" % (pid, R["launch_s"], R["after_launch"], fg0))
    check("launch() minimized it through COM and took no focus", R["after_launch"]["IsIconic"] and R["after_launch"]["foreground"][0] != pid, R["after_launch"])
    uservars.save()
    work = os.path.join(W, "rp_C.dwg")
    shutil.copyfile(SRC, work)
    doc = m.call(m.get(a, "Documents"), "Open", work)
    m.wait_idle(120)
    m.call(doc, "SetVariable", "TILEMODE", 1)
    m.call(doc, "SetVariable", "LOGFILEMODE", 1)
    logmode_set = True
    LOGFILE = m.call(doc, "GetVariable", "LOGFILENAME")
    R["after_open"] = winstate(hw)
    log("after Open: %s | active %s | log file %s" % (R["after_open"], m.get(m.doc(), "Name"), LOGFILE))
    check("the window stayed minimized through Documents.Open", R["after_open"]["IsIconic"], R["after_open"])
    ms = m.get(doc, "ModelSpace")
    for k, y, side in (("1 alone", 0, None),
                       ("2 with COM reads from another process", 120, READER % (pid, 8.0)),
                       ("3 with ShowWindow minimize from another process", 240, MINIMIZER % (hw, 8.0))):
        r = draw(doc, ms, y, side)
        r["window"] = winstate(hw)
        R["draw " + k] = r
        log("draw %s: %s" % (k, json.dumps({x: r[x] for x in ("idle", "new_pipes", "helper", "window")})))
        for line in r["log"]:
            log("    | " + line[:200])
        check("draw %s: one 240 in. pipe" % k, r["idle"] and r["new_pipes"] == [240.0], r["new_pipes"])
    m.call(doc, "Close", False)
    m.wait_idle(30)
    doc = ms = None
finally:
    if logmode_set:
        try:
            log("uservars restore:", uservars.restore())
        except Exception as e:
            log("uservars restore failed:", e)
    uservars.saved.clear()                       # its exit hook must never reach another AutoCAD
    if pid:
        a = None
        log("quit_unsaved:", m.quit_unsaved(pid, 90))
        st = None
        import glob, tempfile
        for d in sorted(glob.glob(os.path.join(tempfile.gettempdir(), "mepcom_hold_*")), key=os.path.getmtime, reverse=True):
            if any(e.get("pid") == pid for e in m._events(os.path.join(d, "holder.jsonl"))):
                st = os.path.join(d, "holder.jsonl")
                break
        ev = None
        t = time.time()
        while st and not ev and time.time() - t < 150:
            ev = ([e for e in m._events(st) if e.get("event") == "exit"] or [None])[-1]
            time.sleep(0.5)
        check("holder exited after AutoCAD and put the registry back", bool(ev) and ev.get("registry") == "put back", ev)
        R["holder_events"] = m._events(st) if st else None
    diff = {k: (REG0[k], v) for k, v in reg_read().items() if v != REG0[k]}
    check("registry (startup values, FILEDIA, CMDDIA) as found", not diff, diff)
    check("no acad.exe and no locator left", not m._acad_pids() and not m._held_pids(), (sorted(m._acad_pids()), m._held_pids()))
    R["checks"] = CHECKS
    json.dump(R, open(os.path.join(W, "retest_results.json"), "w"), indent=1, default=str)
    log("RESULT: %d of %d checks passed" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
