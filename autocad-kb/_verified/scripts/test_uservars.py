"""Live test of scripts/uservars.py in a minimized AutoCAD MEP 2027 (2026-10-18).
1. Normal path: save(), a typical MEP build script's setvar line (plus CMDDIA 0), restore(): every value comes back.
2. Early exit: a child saves, changes, then sys.exit(3) with no restore(): the exit hook puts them back.
3. MEP unreachable: a child saves, changes, then its COM calls fail: the exit hook writes FILEDIA to the registry.
Runs only when no acad.exe is running. Leaves MEP at FILEDIA 1 and CMDDIA 1 (dialogs
back on), closes its own MEP without saving, and puts the registry default profile back.
"""
import os, subprocess, sys, time, winreg
import win32con, win32gui
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
SK = SKILL_SCRIPTS
sys.path.insert(0, SK)
import mepcom as m
import uservars

ACAD = r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe"
AECBASE = r"C:\Program Files\Autodesk\AutoCAD 2027\AecBase.dbx"
PROFILE = "AutoCAD MEP (US Imperial)"
PROFKEY = r"Software\Autodesk\AutoCAD\R26.0\ACAD-A106:409\Profiles"
FDKEY = r"Software\Autodesk\AutoCAD\R26.0\ACAD-A106:409\FixedProfile\General Configuration"
NAMES = uservars.NAMES
MEP_LINE = ('(setvar "FILEDIA" 0) (setvar "CMDECHO" 0) (setvar "BACKGROUNDPLOT" 0) (setvar "INSUNITS" 1) '
            '(setvar "LOGFILEMODE" 1) (vl-load-com) (setvar "TILEMODE" 1) (setvar "CMDDIA" 0) (princ)\n')
results = []


def log(*a):
    print(time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a), flush=True)


def check(name, ok, detail=""):
    results.append((name, ok))
    log("PASS" if ok else "FAIL", name, detail)


def reg(key, name):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
        return winreg.QueryValueEx(k, name)[0]


def regset(v):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, FDKEY, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "FileDialog", 0, winreg.REG_DWORD, v)


def values():
    return {n: int(m.var(n)) for n in NAMES}


class Guard(m.DialogGuard):
    """Cancel any MEP dialog by message; WM_CLOSE after 3 s (Drawing Recovery has no Cancel)."""
    def run(self):
        first = {}
        while not self.stop:
            for h, title, texts in m.dialogs():
                if h not in first:
                    first[h] = time.time(); self.seen.append((h, title, texts)); log("DIALOG", title, texts[:4])
                win32gui.PostMessage(h, win32con.WM_COMMAND, win32con.IDCANCEL, 0)
                if time.time() - first[h] > 3:
                    win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
            time.sleep(self.period)


if m._acad_pids():
    raise SystemExit("acad.exe is already running: not starting a test MEP")
prof_before = reg(PROFKEY, "")
log("default profile before:", prof_before, "| registry FileDialog (MEP key) before:", reg(FDKEY, "FileDialog"))
si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = 7
t0 = time.time()
proc = subprocess.Popen([ACAD, "/ld", AECBASE, "/p", PROFILE, "/product", "MEP", "/language", "en-US", "/nologo"], startupinfo=si)
m.bind(proc.pid)                 # every COM call and the dialog guard: this acad.exe only
guard = Guard(cancel=True); guard.start()
try:
    a = None
    while time.time() - t0 < 360:
        try:
            a = m.app(); m.get(m.get(a, "Documents"), "Count"); break
        except Exception:
            a = None; time.sleep(3)
    if a is None:
        raise SystemExit("MEP never answered COM in 360 s")
    log("COM answered after %.0f s, pid %d" % (time.time() - t0, proc.pid))
    try:
        m.put(a, "WindowState", 2)
    except Exception as e:
        log("minimize failed:", e)
    docs = m.get(a, "Documents")
    if m.get(docs, "Count") == 0:
        m.call(docs, "Add")
    m.wait_idle(120)
    log("found in MEP:", values())

    # baseline = the user's normal settings: dialogs on, no command log
    m.send('(setvar "FILEDIA" 1) (setvar "CMDDIA" 1) (setvar "LOGFILEMODE" 0) (princ)\n'); m.wait_idle(30)
    base = values()
    log("baseline:", base)
    check("setvar FILEDIA 1 reaches the registry at once", reg(FDKEY, "FileDialog") == 1)

    # 1. normal path
    s = uservars.save()
    check("save() reads the current values", s == base, s)
    m.send(MEP_LINE); m.wait_idle(30)
    ch = values()
    check("build script setvar line changes them", ch["FILEDIA"] == 0 and ch["CMDDIA"] == 0 and ch["LOGFILEMODE"] == 1, ch)
    check("setvar FILEDIA 0 reaches the registry at once", reg(FDKEY, "FileDialog") == 0)
    back = uservars.restore()
    check("restore() puts every value back", back == base, back)
    check("restore() clears its list", uservars.saved == {})
    check("restore() puts the registry back to 1", reg(FDKEY, "FileDialog") == 1)

    # 2. early exit: the exit hook restores
    r = subprocess.run([sys.executable, os.path.join(HERE, "uv_child.py"), "exit", str(proc.pid)], capture_output=True, text=True, timeout=180)
    log("child exit:", r.returncode, r.stdout.strip().replace("\n", " | "), r.stderr.strip()[-300:])
    m.wait_idle(30)
    v = values()
    check("early exit: exit hook put values back", r.returncode == 3 and v == base, v)

    # 3. MEP unreachable at exit: registry fallback for FILEDIA
    regset(0)                        # start from the broken state, so only the fallback can make it 1
    r = subprocess.run([sys.executable, os.path.join(HERE, "uv_child.py"), "gone", str(proc.pid)], capture_output=True, text=True, timeout=180)
    log("child gone:", r.returncode, r.stdout.strip().replace("\n", " | "), r.stderr.strip()[-300:])
    check("COM lost: fallback wrote FileDialog 1 to the registry", r.returncode == 3 and reg(FDKEY, "FileDialog") == 1,
          "registry %s, MEP still holds %s" % (reg(FDKEY, "FileDialog"), values()))
    # MEP itself still holds the child's 0s: set the baseline again so it does not write them back
    m.send('(setvar "FILEDIA" 1) (setvar "CMDDIA" 1) (setvar "LOGFILEMODE" 0) (princ)\n'); m.wait_idle(30)
    log("final in MEP:", values(), "| registry:", reg(FDKEY, "FileDialog"))
finally:
    try:
        ds = m.get(m.app(), "Documents")
        for i in range(m.get(ds, "Count") - 1, -1, -1):
            m.call(m.call(ds, "Item", i), "Close", False)
    except Exception as e:
        log("closing drawings:", str(e)[:100])
    try:
        m.call(m.app(), "Quit")
    except Exception as e:
        log("Quit call:", str(e)[:100])
    try:
        proc.wait(120); log("acad.exe exited, code", proc.returncode)
    except subprocess.TimeoutExpired:
        log("acad.exe still running 120 s after Quit; killing our pid", proc.pid)
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    guard.stop = True
    if reg(PROFKEY, "") != prof_before:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PROFKEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, prof_before)
        log("default profile put back to", reg(PROFKEY, ""))
    fd_after = reg(FDKEY, "FileDialog")
    check("registry still 1 after MEP closed", fd_after == 1, fd_after)
    log("dialogs seen:", [(t, x[:3]) for _, t, x in guard.seen])
    log("RESULT: %d of %d passed" % (sum(ok for _, ok in results), len(results)))
