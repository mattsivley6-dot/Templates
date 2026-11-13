"""Start AutoCAD the way a desktop shortcut does (minimized), read FILEDIA and CMDDIA in the
window, close it without saving. Read only: changes no setting.
usage: py -3.14 check_gui_dialogs.py acad|mep
"""
import os, subprocess, sys, time, winreg
import win32con, win32gui
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m

ACAD = r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe"
ARGS = {"acad": ["/product", "ACAD", "/language", "en-US", "/nologo"],
        "mep": ["/ld", r"C:\Program Files\Autodesk\AutoCAD 2027\AecBase.dbx", "/p", "AutoCAD MEP (US Imperial)",
                "/product", "MEP", "/language", "en-US", "/nologo"]}[sys.argv[1]]
PROFKEY = r"Software\Autodesk\AutoCAD\R26.0\ACAD-A106:409\Profiles"


def reg(key, name):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
        return winreg.QueryValueEx(k, name)[0]


class Guard(m.DialogGuard):
    def run(self):
        first = {}
        while not self.stop:
            for h, title, texts in m.dialogs():
                if h not in first:
                    first[h] = time.time(); self.seen.append((h, title, texts))
                win32gui.PostMessage(h, win32con.WM_COMMAND, win32con.IDCANCEL, 0)
                if time.time() - first[h] > 3:
                    win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
            time.sleep(self.period)


if m._acad_pids():
    raise SystemExit("acad.exe is already running")
prof_before = reg(PROFKEY, "")
si = subprocess.STARTUPINFO(); si.dwFlags |= subprocess.STARTF_USESHOWWINDOW; si.wShowWindow = 7
t0 = time.time()
proc = subprocess.Popen([ACAD] + ARGS, startupinfo=si)
m.bind(proc.pid)
guard = Guard(cancel=True); guard.start()
try:
    while True:
        try:
            a = m.app(); m.get(m.get(a, "Documents"), "Count"); break
        except Exception:
            if time.time() - t0 > 360:
                raise SystemExit("no COM answer in 360 s")
            time.sleep(3)
    try:
        m.put(a, "WindowState", 2)
    except Exception:
        pass
    docs = m.get(a, "Documents")
    if m.get(docs, "Count") == 0:
        m.call(docs, "Add")
    m.wait_idle(120)
    print("window %s after %.0f s: PRODUCT %s | CPROFILE %s | FILEDIA %s | CMDDIA %s | LOGFILEMODE %s" % (
        sys.argv[1], time.time() - t0, m.var("PRODUCT"), m.var("CPROFILE"), m.var("FILEDIA"), m.var("CMDDIA"),
        m.var("LOGFILEMODE")), flush=True)
finally:
    try:
        ds = m.get(m.app(), "Documents")
        for i in range(m.get(ds, "Count") - 1, -1, -1):
            m.call(m.call(ds, "Item", i), "Close", False)
        m.call(m.app(), "Quit")
    except Exception as e:
        print("close:", str(e)[:100])
    try:
        proc.wait(120)
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    guard.stop = True
    if reg(PROFKEY, "") != prof_before:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PROFKEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, prof_before)
        print("MEP default profile put back to", prof_before)
    print("dialogs seen:", [(t, x[:3]) for _, t, x in guard.seen])
