"""Live test (2026-10-18): can a session get its OWN AutoCAD MEP 2027 over COM while another acad.exe runs?

mepcom.launch() starts a new AutoCAD with CoCreateInstance inside a holder process, which puts a locator for it in the
Running Object Table as !mepcom.acad.<pid>. app(pid) then reaches it, although only the FIRST AutoCAD registered is
reachable through the shared !{CLSID} entry (AutoCAD ActiveX reference, Application object).

usage: py -3.14 mepcom_comlaunch_test.py <work_dir> [--with PID ...]
  --with PID   an acad.exe the user OK'd to leave running during the test. Read only: HWND and Caption.
Round A: launch() with LastLaunchedProduct = ACAD (as the Core Console leaves it). It stays running.
Round B: launch() with mepcom.MEPREG while A runs: a new pid? reached by a later script? MEP? one pipe drawn?
         Then the lifetime checks (holder stopped, last reference released).
Two launches. Mouse and keyboard are never used. Only this test's own pids are ever quit or killed; a watchdog kills
our own acad.exe if a COM call into it sticks. Registry startup values and FILEDIA are recorded first and
checked (and put back if needed) at the end.
writes: <work_dir>/comlaunch_test.log and comlaunch_results.json
"""
import gc, glob, json, os, shutil, subprocess, sys, tempfile, threading, time, winreg
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import pythoncom, win32api, win32con, win32event, win32gui, win32process

W = os.path.abspath(sys.argv[1])
os.makedirs(W, exist_ok=True)
WITH = {int(sys.argv[i + 1]) for i, a in enumerate(sys.argv) if a == "--with"}
SRC = r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg"
LOGP = os.path.join(W, "comlaunch_test.log")
if os.path.exists(LOGP):
    os.remove(LOGP)
REGVALS = [(m.REG, "CurVer"), (m.REG, "LastLaunchedProduct"), (m.REG, "LastLaunchedLanguage"),
           (m.REG + r"\ACAD-A106:409\Profiles", ""), (m.REG + r"\ACAD-A101:409\Profiles", ""),
           (m.REG + r"\ACAD-A106:409\FixedProfile\General Configuration", "FileDialog"),
           (m.REG + r"\ACAD-A101:409\FixedProfile\General Configuration", "FileDialog"),
           (m.REG + r"\ACAD-A106:409\FixedProfile\General Configuration", "CommandDialogs"),   # CMDDIA
           (m.REG + r"\ACAD-A101:409\FixedProfile\General Configuration", "CommandDialogs")]
RESULTS, CHECKS = {"rounds": []}, []


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True)
    open(LOGP, "a", encoding="utf-8").write(s + "\n")


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok)))
    log("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + str(detail)) if detail != "" else ""))


def info(name, detail):
    log("INFO  %s  | %s" % (name, detail))


# ---------------------------------------------------------------- watchdog: a stuck call into OUR acad.exe kills it
DL = {"t": None, "what": "", "pid": None}


def _watchdog():
    while True:
        if DL["t"] and time.time() > DL["t"]:
            log("WATCHDOG: %s stuck past its deadline; killing our acad.exe %s" % (DL["what"], DL["pid"]))
            subprocess.run(["taskkill", "/PID", str(DL["pid"]), "/F"], capture_output=True)
            DL["t"] = None
        time.sleep(1)


threading.Thread(target=_watchdog, daemon=True).start()


class deadline:
    def __init__(self, secs, what, pid):
        self.v = (secs, what, pid)

    def __enter__(self):
        secs, what, pid = self.v
        DL.update(t=time.time() + secs, what=what, pid=pid)

    def __exit__(self, *a):
        DL["t"] = None


# ---------------------------------------------------------------- helpers
def reg_read():
    out = {}
    for sub, n in REGVALS:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub) as k:
                out[sub + "|" + n] = winreg.QueryValueEx(k, n)[0]
        except OSError:
            out[sub + "|" + n] = None
    return out


def reg_write(key, val):
    sub, n = key.split("|")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub, 0, winreg.KEY_SET_VALUE) as k:
        if val is None:
            winreg.DeleteValue(k, n)
        else:
            winreg.SetValueEx(k, n, 0, winreg.REG_DWORD if isinstance(val, int) else winreg.REG_SZ, val)


def alive(pid):
    try:
        h = win32api.OpenProcess(0x00100000, False, pid)
    except Exception:
        return False
    return win32event.WaitForSingleObject(h, 0) != win32event.WAIT_OBJECT_0


def wait_exit(pid, secs):
    t = time.time()
    while time.time() - t < secs:
        if not alive(pid):
            return True
        time.sleep(0.5)
    return not alive(pid)


def proc_info(pid):
    ps = ("$p = Get-CimInstance Win32_Process -Filter 'ProcessId=%d'; $q = Get-CimInstance Win32_Process -Filter ('ProcessId=' + $p.ParentProcessId); "
          "[pscustomobject]@{cmd=$p.CommandLine; parent=$p.ParentProcessId; parent_name=$q.Name; parent_cmd=$q.CommandLine} | ConvertTo-Json -Compress" % pid)
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"raw": r.stdout.strip()[:300]}


def fg():
    h = win32gui.GetForegroundWindow()
    return h, (win32process.GetWindowThreadProcessId(h)[1] if h else None), win32gui.GetWindowText(h)[:60]


def retry(f, secs=60):
    t = time.time()
    while True:
        try:
            return f()
        except pythoncom.com_error as e:
            if e.hresult in (-2147418111, -2147417846) and time.time() - t < secs:
                time.sleep(1)
                continue
            raise


def hwnd_pid(a):
    return win32process.GetWindowThreadProcessId(retry(lambda: m.get(a, "HWND")))[1]


def active_pid():
    import win32com.client
    try:
        return win32process.GetWindowThreadProcessId(m.get(win32com.client.GetActiveObject("AutoCAD.Application")._oleobj_, "HWND"))[1]
    except Exception as e:
        return "ERR %s" % e


def holder_state(pid):
    """holder.jsonl of the launch() that made <pid> (newest mepcom_hold_* temp folder that names it)."""
    for d in sorted(glob.glob(os.path.join(tempfile.gettempdir(), "mepcom_hold_*")), key=os.path.getmtime, reverse=True):
        st = os.path.join(d, "holder.jsonl")
        if any(e.get("pid") == pid for e in m._events(st)):
            return st
    return None


def holder_pid(st):
    for e in m._events(st):
        if "holder" in e:
            return e["holder"]
    return None


def holder_exit_event(st, secs):
    t = time.time()
    while time.time() - t < secs:
        ev = [e for e in m._events(st) if e.get("event") == "exit"]
        if ev:
            return ev[-1]
        time.sleep(0.5)
    return None


class NewGuard(m.DialogGuard):
    """Log and cancel dialogs of acad.exe pids that were NOT running when it started (this test's own)."""
    def __init__(self, before):
        super().__init__(cancel=True)
        self.before = set(before)

    def run(self):
        first = {}
        while not self.stop:
            mine = m._acad_pids() - self.before
            if mine:
                for h, title, texts in m.dialogs(mine):
                    if h not in first:
                        first[h] = time.time()
                        self.seen.append((h, title, texts))
                        log("DIALOG", win32process.GetWindowThreadProcessId(h)[1], title, texts)
                    win32gui.PostMessage(h, win32con.WM_COMMAND, win32con.IDCANCEL, 0)
                    if time.time() - first[h] > 3:
                        win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
            time.sleep(self.period)


def users1(doc, expr, pid, secs=20):
    """(setvar "USERS1" <expr>) through SendCommand; what USERS1 reads afterwards, or None if it never ran."""
    m.call(doc, "SetVariable", "USERS1", "")
    with deadline(90, "SendCommand " + expr, pid):
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


def child_reaches(pid):
    code = ("import os, sys; sys.path.insert(0, os.environ['AUTOCAD_SKILL_SCRIPTS']); import mepcom as m, win32process; "
            "a = m.app(%d); print(win32process.GetWindowThreadProcessId(m.get(a, 'HWND'))[1])" % pid)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    return out.stdout.strip() == str(pid), (out.stdout.strip(), out.stderr.strip()[-200:])


# ---------------------------------------------------------------- one round: launch() and look inside the new instance
def start_round(name, reg, others):
    """Launch, then check identity, window, product and MEP. Returns (results, app or None). Leaves it running."""
    R = {"round": name, "reg": reg}
    RESULTS["rounds"].append(R)
    log("==== round %s: launch(reg=%s) while acad.exe %s run" % (name, json.dumps(reg), sorted(m._acad_pids())))
    before = m._acad_pids()
    R["running_before"] = sorted(before)
    fg0, t0 = fg(), time.time()
    try:
        a, pid = m.launch(reg=reg, timeout=420)
    except Exception as e:
        R["launch_error"] = str(e)
        check("round %s: launch() returned an instance" % name, False, e)
        return R, None
    R["pid"], R["launch_s"] = pid, round(time.time() - t0, 1)
    if pid in before:                                   # attached to an AutoCAD that was already running: touch nothing
        R["attached_to_running"] = True
        check("round %s: launch() started a NEW acad.exe" % name, False, "it handed back pid %d, which was already running" % pid)
        m.bind(None)
        st = holder_state(pid)
        if st:
            open(st + ".stop", "w").close()
        return R, None
    R["mine"] = True
    check("round %s: launch() started a NEW acad.exe and handed back its object (%.0f s)" % (name, R["launch_s"]), True,
          "pid %d; running before: %s" % (pid, sorted(before)))
    check("round %s: launch() bound the new pid" % name, m.PID == pid)
    R["proc"] = proc_info(pid)
    info("round %s: new process" % name, R["proc"])
    check("round %s: the object's HWND belongs to that pid" % name, hwnd_pid(a) == pid)
    fg1 = fg()
    R["foreground"] = [fg0, fg1]
    check("round %s: the launch did not take the foreground window" % name, fg1[1] != pid, "before %s, after %s" % (fg0, fg1))
    hw = retry(lambda: m.get(a, "HWND"))
    R["hwnd"] = hw
    R["window"] = {"Visible": retry(lambda: m.get(a, "Visible")), "IsWindowVisible": bool(win32gui.IsWindowVisible(hw)),
                   "IsIconic": bool(win32gui.IsIconic(hw)), "WindowState": retry(lambda: m.get(a, "WindowState"))}
    info("round %s: window" % name, R["window"])
    for k in ("Caption", "Name", "Version", "FullName"):
        R[k] = retry(lambda: m.get(a, k))
    info("round %s: Caption / Version / FullName" % name, (R["Caption"], R["Version"], R["FullName"]))
    try:
        R["ActiveProfile"] = retry(lambda: m.get(m.get(m.get(a, "Preferences"), "Profiles"), "ActiveProfile"))
    except Exception as e:
        R["ActiveProfile"] = "ERR %s" % e
    arx = retry(lambda: m.call(a, "ListARX")) or ()
    R["arx_count"], R["aec_arx"] = len(arx), [x for x in arx if x.lower().startswith("aec")]
    info("round %s: active profile / AEC modules loaded" % name, (R["ActiveProfile"], len(R["aec_arx"]), R["aec_arx"][:10]))
    docs = retry(lambda: m.get(a, "Documents"))
    R["docs_at_start"] = retry(lambda: m.get(docs, "Count"))

    ok, d = child_reaches(pid)
    check("round %s: a separate later script reaches it with app(pid)" % name, ok, d)
    walk = [p for p, x in m._rot() if x is not None]
    R["clsid_walk"], R["getactiveobject"] = walk, active_pid()
    if others:
        check("round %s: the shared !{CLSID} entry still gives the first AutoCAD, not this one" % name,
              pid not in walk and set(walk) <= set(others), walk)
        check("round %s: unbound GetActiveObject (old scripts) still gives the first AutoCAD" % name,
              R["getactiveobject"] in others, R["getactiveobject"])
    else:
        info("round %s: nothing else running, so this one is first in the ROT" % name, (walk, R["getactiveobject"]))

    with deadline(240, "Documents.Add", pid):
        nd = retry(lambda: m.call(docs, "Add"), 120)
    m.wait_idle(120)
    R["CPROFILE"] = retry(lambda: m.call(nd, "GetVariable", "CPROFILE"))
    info("round %s: drawings at start %s, CPROFILE %r" % (name, R["docs_at_start"], R["CPROFILE"]), m.get(nd, "Name"))
    ping = users1(nd, '"PING"', pid)
    R["sendcommand_as_launched"] = ping == "PING"
    if ping != "PING":
        log("SendCommand did not run with the window as launched; showing it minimized without activation")
        win32gui.ShowWindow(hw, 7)                       # SW_SHOWMINNOACTIVE
        ping = users1(nd, '"PING"', pid)
        R["sendcommand_after_showminnoactive"] = ping == "PING"
        R["foreground_after_show"] = fg()
    check("round %s: SendCommand runs in the COM-launched instance" % name, ping == "PING",
          "as launched: %s, after SW_SHOWMINNOACTIVE: %s" % (R["sendcommand_as_launched"], R.get("sendcommand_after_showminnoactive", "not needed")))
    R["has_AECBPIPEADD"] = users1(nd, '(if (getcname "_-AECBPIPEADD") "YES" "NO")', pid)
    try:
        R["PipeSystemDefs"] = m.get(m.get(m.aec("AecX.AecbPipeDatabase.8.9", nd), "PipeSystemDefs"), "Count")
    except Exception as e:
        R["PipeSystemDefs"] = "ERR %s" % str(e)[:120]
    R["is_mep"] = R["has_AECBPIPEADD"] == "YES" and isinstance(R["PipeSystemDefs"], int)
    info("round %s: -AECBPIPEADD defined %r, PipeSystemDefs %r: MEP = %s" % (name, R["has_AECBPIPEADD"], R["PipeSystemDefs"], R["is_mep"]), R["CPROFILE"])
    if R["is_mep"]:
        import uservars                                  # FILEDIA/CMDDIA as found (another session asked; nothing here sets them)
        R["uservars_saved"] = uservars.save()
        work = os.path.join(W, "rp_%s.dwg" % name)
        shutil.copyfile(SRC, work)
        with deadline(240, "Documents.Open", pid):
            doc = retry(lambda: m.call(docs, "Open", work), 120)
        m.wait_idle(120)
        ms = m.get(doc, "ModelSpace")
        n0 = m.get(ms, "Count")
        m.call(doc, "SetVariable", "TILEMODE", 1)
        with deadline(180, "-AECBPIPEADD", pid):
            m.send('_-AECBPIPEADD\nR\nGlued\nSI\n4"\n_non\n0,0,120\n_non\n240,0,120\n\n')
            time.sleep(1)
            idle = m.wait_idle(90)
        pipes = []
        for i in range(n0, m.get(ms, "Count")):
            e = m.call(ms, "Item", i)
            if m.get(e, "ObjectName") == "AecbDbPipe":
                pipes.append(round(m.get(e, "Length"), 4))
        R["pipe_draw"] = {"idle": idle, "new_pipes": pipes}
        check("round %s: -AECBPIPEADD drew one 240 in. Glued 4 in. pipe" % name, idle and pipes == [240.0], R["pipe_draw"])
        try:
            R["uservars_after"] = uservars.restore()
        except Exception as e:
            R["uservars_after"] = "ERR %s" % e
        uservars.saved.clear()                           # its exit hook must never reach another AutoCAD
        with deadline(120, "Close", pid):
            m.call(doc, "Close", False)
        doc = ms = None
    with deadline(120, "Close", pid):
        m.call(nd, "Close", False)
    nd = docs = None
    return R, a


def end_round(R, lifetime):
    """Lifetime checks (optional), then make sure our acad.exe is gone and the holder put the registry back."""
    name, pid = R["round"], R["pid"]
    st = holder_state(pid)
    if lifetime and st:
        a = m.app(pid)
        open(st + ".stop", "w").close()
        t = time.time()
        while pid in m._held_pids() and time.time() - t < 15:
            time.sleep(0.5)
        check("round %s: the holder's stop file removes its locator from the ROT" % name, pid not in m._held_pids())
        check("round %s: AutoCAD still runs while this process holds it" % name, alive(pid))
        try:
            ok = hwnd_pid(a) == pid
        except Exception as e:
            ok = "ERR %s" % e
        check("round %s: the object this process holds still works (it goes straight to AutoCAD)" % name, ok is True, ok)
        a = None
        gc.collect()
        R["exits_when_released"] = wait_exit(pid, 45)
        info("round %s: AutoCAD exited by itself within 45 s once nothing held it" % name, R["exits_when_released"])
        if not R["exits_when_released"]:
            R["orphan_reachable_by_shared_entry"] = pid in {p for p, x in m._rot() if x is not None}
            info("round %s: left running with no holder; reachable through the shared entry" % name, R["orphan_reachable_by_shared_entry"])
    if alive(pid):
        R["end"] = m.quit_unsaved(pid, 90)
        log("round %s: quit_unsaved: %s" % (name, R["end"]))
    check("round %s: our acad.exe is gone" % name, wait_exit(pid, 60), pid)
    if st:
        ev = holder_exit_event(st, 150)
        R["holder_exit"] = ev
        check("round %s: holder exited after AutoCAD and put the registry back" % name,
              bool(ev) and ev.get("acad_exited") and ev.get("registry") == "put back", ev)
        hp = holder_pid(st)
        check("round %s: holder process gone" % name, wait_exit(hp, 30) if hp else False, hp)


# ---------------------------------------------------------------- run
running = m._acad_pids()
log("acad.exe running at start:", sorted(running), "| OK'd to stay:", sorted(WITH))
if running - WITH:
    raise SystemExit("acad.exe %s is running and was not OK'd with --with: ask the user first" % sorted(running - WITH))
REG0 = reg_read()
RESULTS["registry_at_start"] = REG0
log("registry at start:", json.dumps(REG0))
guard = NewGuard(running)
guard.start()
cap0 = {p: m.get(x, "Caption") for p, x in m._rot() if x is not None}
A = B = None
try:
    others = sorted(running)
    A, aA = start_round("A", {m.REG: {"LastLaunchedProduct": "ACAD"}}, others)
    if aA is not None:
        aA = None
        m.bind(None)
        B, aB = start_round("B", m.MEPREG, others + [A["pid"]])
        aB = None
        if B.get("mine"):
            end_round(B, lifetime=True)
finally:
    m.bind(None)
    for R in (B, A):                                    # ours only; one failure must not skip the other
        if R and R.get("mine") and (alive(R["pid"]) or "holder_exit" not in R):
            try:
                end_round(R, lifetime=False)
            except Exception as e:
                log("cleanup of round %s: %r" % (R["round"], e))
            if alive(R["pid"]):
                subprocess.run(["taskkill", "/PID", str(R["pid"]), "/F"], capture_output=True)
                log("round %s: killed our acad.exe %d in cleanup" % (R["round"], R["pid"]))
    guard.stop = True
    RESULTS["dialogs"] = [(t, x) for h, t, x in guard.seen]
    if guard.seen:
        info("dialogs seen in our instances", RESULTS["dialogs"])
    if WITH:
        cap1 = {p: m.get(x, "Caption") for p, x in m._rot() if x is not None}
        check("the AutoCAD that was already running is unchanged (same pid and caption)", cap0 == cap1, (cap0, cap1))
    end = reg_read()
    diff = {k: (REG0[k], v) for k, v in end.items() if v != REG0[k]}
    RESULTS["registry_diff_at_end"] = diff
    for k, (old, new) in diff.items():
        reg_write(k, old)
        log("put back %s: %r -> %r" % (k, new, old))
    check("registry (startup values, FILEDIA) as found at the start, after any put-back", reg_read() == REG0, diff)
    left = m._held_pids()
    check("no launch() locator left in the ROT", not left, left)
    RESULTS["checks"] = CHECKS
    json.dump(RESULTS, open(os.path.join(W, "comlaunch_results.json"), "w"), indent=1, default=str)
    log("RESULT: %d of %d checks passed" % (sum(ok for _, ok in CHECKS), len(CHECKS)))
