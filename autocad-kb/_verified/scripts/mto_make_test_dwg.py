"""Build the known-length test drawing for mep_takeoff.py: minimized AutoCAD MEP 2027 over raw COM, no mouse, no keyboard.

Works on a COPY of MEP's "Routing Preferences (US Imperial).dwg". Draws 5 runs of known centerline length with
-AECBPIPEADD (every value validated before it is sent), sets layers, insulation, one sloped pipe and one frozen and one
locked layer by COM, reads every MEP object back by COM (independent of the console LIST path), saves on a layout tab,
closes MEP and puts the registry profile and LOGFILEMODE back the way they were.
Every mepcom call and the dialog guard are bound to the acad.exe this script starts (its Popen pid), so it never
closes, quits or cancels another session's MEP (2026-10-18).
usage: py -3.14 mto_make_test_dwg.py <work_dir>
writes: <work_dir>/mto_test.dwg, design.json, com_readback.json, make_test_dwg.log
"""
import json, math, os, re, shutil, subprocess, sys, time, winreg
import pythoncom, win32con, win32gui
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m

W = os.path.abspath(sys.argv[1])
os.makedirs(W, exist_ok=True)
WF = W.replace("\\", "/")
if " " in WF:
    raise SystemExit("work dir must have no spaces (LISP file paths): " + WF)
SRC = r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg"
ACAD = r"C:\Program Files\Autodesk\AutoCAD 2027\acad.exe"
AECBASE = r"C:\Program Files\Autodesk\AutoCAD 2027\AecBase.dbx"
PROFILE = "AutoCAD MEP (US Imperial)"
REGKEY = r"Software\Autodesk\AutoCAD\R26.0\ACAD-A106:409\Profiles"
WORK = os.path.join(W, "mto_test_work.dwg")
OUT = os.path.join(W, "mto_test.dwg")
LOGP = os.path.join(W, "make_test_dwg.log")
for p in (WORK, OUT, LOGP, os.path.join(W, "design.json"), os.path.join(W, "com_readback.json")):
    if os.path.exists(p):
        os.remove(p)
LOG = []


def log(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)
    open(LOGP, "a", encoding="utf-8").write(s + "\n")


# ---------------------------------------------------------------- design: 5 runs, inches, all at 10 ft (z = 120)
RUNS = [
    {"id": "R1", "system": "CHWS", "size": '4"', "layer": "M-CHWS", "pts": [(0, 0, 120), (480, 0, 120), (480, 360, 120)]},
    {"id": "R3", "system": "CHWS", "size": '2"', "layer": "M-CHWS", "pts": [(240, 0, 120), (240, 240, 120)], "starts_on": "R1"},
    {"id": "R2", "system": "CHWR", "size": '2"', "layer": "M-CHWR", "pts": [(0, -60, 120), (360, -60, 120), (360, -300, 120)],
     "insulation": 1.5, "lock_layer": True},
    {"id": "R4", "system": "CHWR", "size": '1-1/2"', "layer": "M-HOLD", "pts": [(600, 0, 120), (1200, 0, 120)],
     "end_after": (1200, 0, 114), "freeze_layer": True},
    {"id": "R5", "system": "Standard", "size": '3/4"', "layer": None, "pts": [(0, 600, 120), (120, 600, 120)]},
]
SIZE_OK = {'4"', '3"', '2"', '1-1/2"', '1"', '3/4"'}      # pipe size spellings MEP accepted in testing
NAME_OK = re.compile(r"^[A-Za-z0-9_]+$")
LAYER_OK = re.compile(r"^[A-Za-z0-9_-]+$")


def drawn_length(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def validate(r, prefs, systems):
    if r["size"] not in SIZE_OK:
        raise SystemExit("bad size %r" % r["size"])
    if not NAME_OK.match(r["system"]) or r["system"] not in systems:
        raise SystemExit("system %r not space-free or not in the drawing %s" % (r["system"], systems))
    if "Glued" not in prefs:
        raise SystemExit("routing preference Glued not in the drawing")
    if r["layer"] and not LAYER_OK.match(r["layer"]):
        raise SystemExit("bad layer %r" % r["layer"])
    for p in r["pts"] + ([r["end_after"]] if "end_after" in r else []):
        if len(p) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in p):
            raise SystemExit("bad point %r" % (p,))


def pipe_cmd(r):
    s = ["_-AECBPIPEADD", "R", "Glued", "SY", r["system"], "SI", r["size"]]
    for p in r["pts"]:
        s += ["_non", "%.4f,%.4f,%.4f" % tuple(float(v) for v in p)]
    return "\n".join(s) + "\n\n"


# ---------------------------------------------------------------- helpers
class Guard(m.DialogGuard):
    """Cancel any MEP dialog by message; WM_CLOSE if it is still there after 3 s (Drawing Recovery has no Cancel)."""
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


def acad_pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq acad.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    return {int(l.split('","')[1]) for l in out.splitlines() if l.startswith('"acad')}


def reg_profile():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGKEY) as k:
        return winreg.QueryValueEx(k, "")[0]


def tryget(o, name):
    try:
        return m.get(o, name)
    except Exception as e:
        return "ERR " + str(e)[:80]


def handles(ms):
    return {m.get(m.call(ms, "Item", i), "Handle") for i in range(m.get(ms, "Count"))}


def by_handle(doc, h):
    return m.call(doc, "HandleToObject", h)


def lisp_lines(doc, body, name, timeout=30):
    path = WF + "/" + name
    if os.path.exists(path):
        os.remove(path)
    m.send('(progn (setq f (open "%s" "w")) %s (close f) (setq f nil) (princ))\n' % (path, body))
    t = time.time()
    while time.time() - t < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            time.sleep(0.3)
            return open(path, encoding="utf-8", errors="ignore").read().splitlines()
        time.sleep(0.3)
    return []


def cmdlog_since(doc, n0):
    p = m.call(doc, "GetVariable", "LOGFILENAME")
    try:
        return open(p, "rb").read()[n0:].decode("utf-8", "ignore")
    except OSError:
        return ""


def cmdlog_size(doc):
    p = m.call(doc, "GetVariable", "LOGFILENAME")
    return os.path.getsize(p) if os.path.exists(p) else 0


# ---------------------------------------------------------------- run
running = acad_pids()
if running:
    raise SystemExit("acad.exe %s is already running: COM reaches only the first AutoCAD registered (AutoCAD ActiveX reference, Application object), "
                     "so this script could not reach its own; ask the user before launching another" % sorted(running))
prof_before = reg_profile()
log("registry default profile before:", prof_before)
shutil.copyfile(SRC, WORK)
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = 7                                   # SW_SHOWMINNOACTIVE: start minimized, do not take focus
t0 = time.time()
proc = subprocess.Popen([ACAD, "/ld", AECBASE, "/p", PROFILE, "/product", "MEP", "/language", "en-US", "/nologo"], startupinfo=si)
log("launched acad.exe pid", proc.pid)
m.bind(proc.pid)                                     # every mepcom call below talks only to this acad.exe
guard = Guard(cancel=True, pid=proc.pid)             # and the guard cancels only its dialogs
guard.start()
ok_all = False
reached = False
logmode_old = None
try:
    a = None
    while time.time() - t0 < 360:
        try:
            a = m.app()
            m.get(m.get(a, "Documents"), "Count")
            break
        except Exception:
            a = None
            other = sorted(p for p in m.instances() if p != proc.pid)
            if other:
                raise SystemExit("acad.exe %s registered first, so COM cannot reach ours (pid %d)" % (other, proc.pid))
            time.sleep(3)
    if a is None:
        raise SystemExit("MEP never answered COM in 360 s")
    reached = True
    log("COM answered after %.0f s" % (time.time() - t0))
    try:
        m.put(a, "WindowState", 2)
    except Exception as e:
        log("minimize failed:", e)
    docs = m.get(a, "Documents")
    doc = m.call(docs, "Open", WORK)
    m.wait_idle(120)
    log("opened", m.get(doc, "Name"), "| CPROFILE", m.call(doc, "GetVariable", "CPROFILE"))
    m.call(doc, "SetVariable", "TILEMODE", 1)
    logmode_old = m.call(doc, "GetVariable", "LOGFILEMODE")
    m.call(doc, "SetVariable", "LOGFILEMODE", 1)
    m.call(doc, "SetVariable", "CLAYER", "0")
    log("LOGFILEMODE was", logmode_old, "| log file", m.call(doc, "GetVariable", "LOGFILENAME"))

    prefs = lisp_lines(doc, '(foreach p (dictsearch (namedobjdict) "AECB_PIPE_PARTROUTINGPREFERENCES_STYLES") (if (= (car p) 3) (write-line (cdr p) f)))', "rp.txt")
    log("routing preferences:", len(prefs), "| Glued present:", "Glued" in prefs)
    pdb = m.aec("AecX.AecbPipeDatabase.8.9", doc)
    sds = m.get(pdb, "PipeSystemDefs")
    for nm, desc in (("CHWS", "Chilled water supply (takeoff test)"), ("CHWR", "Chilled water return (takeoff test)")):
        if not m.call(sds, "Has", nm):
            sd = m.call(sds, "Add", nm)
            m.put(sd, "LabelName", nm)
            m.put(sd, "FamilyName", "Chilled Water")
            m.put(sd, "Description", desc)
    systems = m.names(sds)
    log("pipe systems:", systems)
    lays = m.get(doc, "Layers")
    for ln in ("M-CHWS", "M-CHWR", "M-HOLD"):
        m.call(lays, "Add", ln)
    for r in RUNS:
        validate(r, prefs, systems)
    log("all runs validated")

    ms = m.get(doc, "ModelSpace")
    design = []
    for r in RUNS:
        before = handles(ms)
        n0 = cmdlog_size(doc)
        cmd = pipe_cmd(r)
        log("run", r["id"], "send:", cmd.replace("\n", " / "))
        m.send(cmd)
        time.sleep(1.0)
        idle = m.wait_idle(90)
        txt = cmdlog_since(doc, n0)
        new = sorted(handles(ms) - before)
        log("run", r["id"], "idle", idle, "| new objects", len(new), "| log tail:", " | ".join(l.strip() for l in txt.splitlines()[-6:])[:600])
        if not idle:
            raise SystemExit("MEP not idle after run %s; stopping before more input" % r["id"])
        objs = [(h, by_handle(doc, h)) for h in new]
        kinds = [(h, m.get(o, "ObjectName")) for h, o in objs]
        log("   ", kinds)
        if r["layer"]:
            for h, o in objs:
                m.put(o, "Layer", r["layer"])
        if "insulation" in r:
            for h, o in objs:
                if m.get(o, "ObjectName") == "AecbDbPipe":
                    m.put(o, "InsulationThickness", float(r["insulation"]))
        if "end_after" in r:
            ps = [o for h, o in objs if m.get(o, "ObjectName") == "AecbDbPipe"]
            if len(ps) != 1:
                raise SystemExit("expected one pipe in %s, got %d" % (r["id"], len(ps)))
            m.put(ps[0], "EndPoint", m.pt(*r["end_after"]))
            m.wait_idle(30)
            log("   sloped: end", tryget(ps[0], "EndPoint"), "length", tryget(ps[0], "Length"))
        pts = list(r["pts"])
        if "end_after" in r:
            pts[-1] = r["end_after"]
        design.append({"id": r["id"], "system": r["system"], "size": r["size"], "layer": r["layer"] or "M-Pipe-Std",
                       "pts": pts, "drawn_in": drawn_length(pts), "starts_on": r.get("starts_on"),
                       "insulation": r.get("insulation", 0.0), "new_handles": new})
    for r in RUNS:
        if r.get("lock_layer"):
            m.put(m.call(lays, "Item", r["layer"]), "Lock", True)
        if r.get("freeze_layer"):
            m.put(m.call(lays, "Item", r["layer"]), "Freeze", True)
    log("layers: M-CHWR locked, M-HOLD frozen")

    # independent read-back of every MEP object by COM
    rb = []
    for i in range(m.get(ms, "Count")):
        e = m.call(ms, "Item", i)
        on = m.get(e, "ObjectName")
        if not on.startswith("AecbDb"):
            continue
        d = {"handle": m.get(e, "Handle"), "object": on, "layer": m.get(e, "Layer")}
        props = ["SizeName", "SystemName", "PartDescription"]
        if on == "AecbDbPipe":
            props += ["Length", "CutLength", "StartPoint", "EndPoint", "NominalSize", "InsulationThickness"]
        for k in props:
            v = tryget(e, k)
            d[k] = list(v) if isinstance(v, tuple) else v
        if on != "AecbDbPipe":
            d["connectors"] = [list(loc) for _, loc, _ in m.connected(e)]
        rb.append(d)
    log("COM read-back:", len(rb), "MEP objects", dict((k, sum(1 for x in rb if x["object"] == k)) for k in {x["object"] for x in rb}))
    json.dump(design, open(os.path.join(W, "design.json"), "w"), indent=1)
    json.dump(rb, open(os.path.join(W, "com_readback.json"), "w"), indent=1, default=str)

    m.call(doc, "SetVariable", "TILEMODE", 0)       # save on a layout tab: the takeoff must switch back to model space itself
    m.call(doc, "SetVariable", "LOGFILEMODE", logmode_old)
    logmode_old = None
    m.call(doc, "SaveAs", OUT)
    m.wait_idle(60)
    log("saved", OUT, os.path.getsize(OUT), "bytes")
    m.call(doc, "Close", False)
    m.wait_idle(30)
    ok_all = True
except SystemExit as e:
    log("STOP:", e)
except Exception as e:
    import traceback
    log("FATAL", traceback.format_exc())
finally:
    try:
        if logmode_old is not None:
            m.call(m.doc(), "SetVariable", "LOGFILEMODE", logmode_old)
    except Exception:
        pass
    try:                                            # close every drawing unsaved first, so Quit cannot stop on a save prompt
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
        proc.wait(120 if reached else 1)                # never reached by COM: no Quit got there, so do not wait for one
        log("acad.exe exited, code", proc.returncode)
    except subprocess.TimeoutExpired:
        log("acad.exe still running %s; killing our pid" % ("120 s after Quit" if reached else "and never reached by COM"), proc.pid)
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
    guard.stop = True
    prof_after = reg_profile()
    if prof_after != prof_before:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGKEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, prof_before)
        log("registry default profile was changed to %r; restored %r" % (prof_after, reg_profile()))
    else:
        log("registry default profile unchanged:", prof_after)
    log("dialogs seen:", [(t, x) for _, t, x in guard.seen])
    log("DONE ok" if ok_all else "DONE with errors")
