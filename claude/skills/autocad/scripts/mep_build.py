"""AutoCAD MEP version of a 3D piping model in one pass, driven by raw COM (no mouse, no keyboard).

1. Open a copy of MEP's US Imperial routing-preference drawing (has the Glued Sch 40 PVC preference).
2. Bring in the finished CAD model (exploded insert of the model DWG) and its sheet layouts (-LAYOUT Template).
3. Erase the solid pipe, elbows and reducers on the pipe layers inside the building.
4. Draw every run from model.RUNS as real MEP pipe; MEP adds the PVC elbows, tees and reducers.
5. Hangers off, viewports set, title text changed, save, plot each layout to PDF.
Settings AutoCAD saves per user (FILEDIA and others) are read first and put back at the end (uservars.py).

Needs: AutoCAD MEP running and answering COM (see the skill), and a model source folder (--src) holding the
op-list package (geom.py with OPS and side_layer(), model.py with RUNS and build_all()) and the finished model DWG.
Edit PIPE_LAYERS, SYS_LAYERS and LAYOUT_RE below to match your model's layer and layout names.

Usage: py -3.14 mep_build.py [all|pipes|plot] --src <model folder> [--work <folder>] [--model-dwg model3d.dwg]
                             [--out-name model_mep.dwg] [--acad-dir <AutoCAD folder>] [--routing-dwg <dwg>]
Environment defaults: MEP_BUILD_SRC, MEP_BUILD_WORK, ACAD_DIR.
Paths are typed at AutoCAD prompts: keep the work folder free of spaces.
"""
import os, sys, time, json, shutil, re, argparse, tempfile

ap = argparse.ArgumentParser(description="Draw a 3D piping model as native AutoCAD MEP pipe over COM.")
ap.add_argument("stage", nargs="?", default="all", choices=("all", "pipes", "plot"))
ap.add_argument("--src", default=os.environ.get("MEP_BUILD_SRC"),
                help="model source folder: geom.py, model.py and the model DWG (env MEP_BUILD_SRC)")
ap.add_argument("--work", default=os.environ.get("MEP_BUILD_WORK") or os.path.join(tempfile.gettempdir(), "mep_build"),
                help="work folder for the MEP drawing, PDFs, progress files and log (env MEP_BUILD_WORK)")
ap.add_argument("--model-dwg", default="model3d.dwg", help="finished CAD model DWG inside --src (model3d.dwg)")
ap.add_argument("--out-name", default="model_mep.dwg", help="name of the MEP drawing written in --work (model_mep.dwg)")
ap.add_argument("--acad-dir", default=os.environ.get("ACAD_DIR") or r"C:\Program Files\Autodesk\AutoCAD 2027",
                help="AutoCAD install folder, used to relaunch MEP after a lock (env ACAD_DIR)")
ap.add_argument("--routing-dwg",
                default=r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg",
                help="MEP routing preference drawing to copy as the starting drawing")
A = ap.parse_args()
if not A.src:
    ap.error("--src (or MEP_BUILD_SRC) is required")
SRC = os.path.abspath(A.src)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC); sys.path.insert(0, HERE)     # mepcom and uservars from this folder, geom and model from SRC
from mepcom import *
import uservars
import geom, model

W = os.path.abspath(A.work)
os.makedirs(W, exist_ok=True)
WF = W.replace("\\", "/")
MODEL_DWG = os.path.join(SRC, A.model_dwg)
CAD = os.path.join(W, os.path.splitext(A.model_dwg)[0] + "_src.dwg")
CADF = CAD.replace("\\", "/")
OUT = os.path.join(W, A.out_name)
OUT_STEM = os.path.splitext(A.out_name)[0].lower()
STAGE = A.stage
LOG = open(os.path.join(W, "mep_build_log.txt"), "a", encoding="utf-8")
def say(*a):
    s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + "\n"); LOG.flush()

SIZE = {4: '4"', 3: '3"', 2: '2"', 1.5: '1 1/2"', 1: '1"', 0.75: '3/4"', 0.5: '1/2"'}
# pipe layers of the model (wildcards); edit to match yours
PIPE_LAYERS = ["M-CHWS-*", "M-CHWR-*", "M-BYPASS-*", "M-CHEM-0*", "M-CHEM-1*", "M-DRAIN-*", "M-MAKEUP-*", "M-RELIEF-*"]
LAYOUT_RE = r"M3D-\d"                 # sheet layouts brought in from the model DWG and plotted

def pt(p):
    return "%.4f,%.4f,%.4f" % (float(p[0]), float(p[1]), float(p[2]))

# ------------------------------------------------------------------ geometry from the model
model.build_all()
runs = list(model.RUNS.values())
ys = [p[1] for r in runs for p in r.p]
BOX_YMIN = min(ys) - 60.0          # inches; the parts gallery and typical details sit far below the building

def ordered(runs):
    """Parents before children: a run that starts or ends on another run is drawn after it."""
    by = {r.name: r for r in runs}; seen, out = set(), []
    def visit(r, stack=()):
        if r.name in seen or r.name in stack: return
        for k in (r.start, r.end):
            if isinstance(k, str) and k.startswith("on:") and k[3:] in by:
                visit(by[k[3:]], stack + (r.name,))
        seen.add(r.name); out.append(r)
    for r in runs: visit(r)
    return out

def plan(r):
    """Point and size lists, reversed when only the END lands on a parent (MEP makes the tee at a run's start)."""
    p, sz = list(r.p), list(r.sz)
    st = isinstance(r.start, str) and r.start.startswith("on:")
    en = isinstance(r.end, str) and r.end.startswith("on:")
    if en and not st:
        p, sz = p[::-1], sz[::-1]
    return p, sz

def pipe_cmd(p, sz, ends_on=False):
    s = ["_-AECBPIPEADD", "R", "Glued", "SI", SIZE[sz[0]], "_non", pt(p[0])]
    cur = sz[0]
    for i in range(1, len(p)):
        if sz[i - 1] != cur:
            s += ["SI", SIZE[sz[i - 1]]]; cur = sz[i - 1]
        s += ["_non", pt(p[i])]
    return "\n".join(s) + ("\n\n\n" if ends_on else "\n\n")

def logtail(n0):
    lf = var("LOGFILENAME")
    return open(lf, "rb").read()[n0:].decode("utf-8", "ignore"), lf

def probe_size():
    """A space ends the input at the size prompt, so 1 1/2" cannot be typed. Find a spelling MEP accepts."""
    lf = var("LOGFILENAME")
    for cand in ('1-1/2"', '1.5"', '1.5'):
        n0 = os.path.getsize(lf)
        run("_-AECBPIPEADD\nSI\n%s\n\n\n" % cand, 0.5, 30)
        t = open(lf, "rb").read()[n0:].decode("utf-8", "ignore")
        say("size probe", cand, "->", " | ".join(l.strip() for l in t.splitlines() if "Size" in l or "not" in l or "nvalid" in l)[:300])
        if not re.search(r"not found|Invalid|not valid|Requires", t):
            return cand
    return None

def layer_lisp(r):
    """New MEP objects land on M-Pipe-Std. Move each onto this system's layer for its own size
    (pipes by NominalSize, fittings by the first size in SizeName). Objects already on a model layer keep it."""
    pairs = " ".join("'(%s . \"%s\")" % (float(k), geom.side_layer(r.system, k)) for k in (4, 3, 2, 1.5, 1, 0.75, 0.5))
    main = geom.side_layer(r.system, max(r.sz))
    return ('(progn (setq zz_m (list %s)) (setq zz_e (if zz_mk (entnext zz_mk) (entnext))) (setq zz_n 0) '
            '(while zz_e (setq zz_d (entget zz_e)) '
            '(if (and (wcmatch (cdr (assoc 0 zz_d)) "AECB_PIPE*") (= (strcase (cdr (assoc 8 zz_d))) "M-PIPE-STD")) '
            '(progn (setq zz_o (vlax-ename->vla-object zz_e)) '
            '(setq zz_s (if (= (cdr (assoc 0 zz_d)) "AECB_PIPE") (vl-catch-all-apply (function vlax-get-property) (list zz_o (quote NominalSize))) '
            '(atof (vl-princ-to-string (vl-catch-all-apply (function vlax-get-property) (list zz_o (quote SizeName))))))) '
            '(setq zz_l (if (numberp zz_s) (cdr (assoc zz_s zz_m)) nil)) '
            '(setq zz_l (if (and zz_l (tblsearch "LAYER" zz_l)) zz_l (if (tblsearch "LAYER" "%s") "%s" nil))) '
            '(if zz_l (vl-catch-all-apply (function vla-put-layer) (list zz_o zz_l))))) '
            '(if (wcmatch (cdr (assoc 0 zz_d)) "AECB*") (setq zz_n (1+ zz_n))) (setq zz_e (entnext zz_e))) '
            '(setq zz_mk (entlast)) (setvar "USERI1" zz_n) (princ))\n') % (pairs, main, main)

# ------------------------------------------------------------------ helpers
def wait_ready(limit=600):
    t0 = time.time()
    while time.time() - t0 < limit:
        try:
            a = app(); get(get(a, "Documents"), "Count"); return True
        except Exception:
            time.sleep(3)
    return False

def run(seq, settle=1.0, limit=300):
    send(seq); time.sleep(settle); ok = wait_idle(limit)
    if not ok: say("NOT IDLE after", limit, "s:", seq[:80].replace("\n", " | "))
    return ok

def lisp_val(expr):
    run('(setvar "USERS1" (vl-princ-to-string %s)) (princ)\n' % expr)
    return var("USERS1")

# ------------------------------------------------------------------ stages
guard = DialogGuard(cancel=True); guard.start()
say("stage", STAGE, "| runs", len(runs), "| BOX_YMIN", round(BOX_YMIN, 1))
if not wait_ready():
    say("MEP never answered COM"); sys.exit(2)
o = app(); o.Invoke(o.GetIDsOfNames("WindowState"), 0, P, False, 2)
uservars.save()

if STAGE == "all":
    shutil.copy2(MODEL_DWG, CAD)
    shutil.copy2(A.routing_dwg, OUT)
    docs = get(app(), "Documents")
    call(docs, "Open", OUT); time.sleep(3); wait_idle(120)
    say("opened", var("DWGNAME"), "INSUNITS", var("INSUNITS"))
    uservars.save()
    run('(setvar "FILEDIA" 0) (setvar "CMDECHO" 0) (setvar "BACKGROUNDPLOT" 0) (setvar "INSUNITS" 1) (setvar "LOGFILEMODE" 1) (vl-load-com) (setvar "TILEMODE" 1) (princ)\n')
    # model content, exploded
    t = time.time()
    run("_.-INSERT\n*%s\n_non\n0,0,0\n1\n0\n" % CADF, 3, 900)
    say("insert done", round(time.time() - t), "s | solids", lisp_val('(sslength (ssget "X" (list (cons 0 "3DSOLID"))))'))
    # sheet layouts
    t = time.time()
    run("_.-LAYOUT\n_T\n%s\n*\n" % CADF, 3, 600)
    say("layouts done", round(time.time() - t), "s |", lisp_val("(layoutlist)"))
    # erase the solid pipe inside the building
    flt = ",".join(PIPE_LAYERS)
    run(('(progn (setq zz_ss (ssget "X" (list (cons 0 "3DSOLID") (cons 8 "%s") (cons 410 "Model")))) (setq zz_i 0 zz_k 0) '
         '(while (and zz_ss (< zz_i (sslength zz_ss))) (setq zz_o (vlax-ename->vla-object (ssname zz_ss zz_i))) '
         '(vla-getboundingbox zz_o (quote zz_mn) (quote zz_mx)) '
         '(if (> (cadr (vlax-safearray->list zz_mn)) %.1f) (progn (vla-delete zz_o) (setq zz_k (1+ zz_k)))) (setq zz_i (1+ zz_i))) '
         '(setvar "USERI2" zz_k) (princ))\n') % (flt, BOX_YMIN), 2, 600)
    say("solid pipe erased", var("USERI2"))
    run("_.QSAVE\n", 2, 300)

if STAGE in ("all", "pipes"):
    if STAGE == "pipes":
        docs = get(app(), "Documents")
        for k in range(get(docs, "Count") - 1, -1, -1):
            dd = call(docs, "Item", k)
            if get(dd, "Name").lower() == A.out_name.lower():
                call(dd, "Close", False); time.sleep(2)
        call(get(app(), "Documents"), "Open", OUT); time.sleep(3); wait_idle(120)
        uservars.save()
        run('(setvar "FILEDIA" 0) (setvar "CMDECHO" 0) (setvar "BACKGROUNDPLOT" 0) (setvar "LOGFILEMODE" 1) (vl-load-com) (setvar "TILEMODE" 1) (princ)\n')
        run("_.PROPERTIESCLOSE\n"); run("_.-VIEW\n_SEISO\n")
        say("reopened", var("DWGNAME"), "solids", lisp_val('(sslength (ssget "X" (list (cons 0 "3DSOLID"))))'))
    s15 = probe_size()
    if not s15:
        say("ABORT: no 1-1/2 size spelling accepted"); sys.exit(4)
    SIZE[1.5] = s15
    DONE = os.path.join(W, "mep_done.json")
    done = json.load(open(DONE)) if os.path.exists(DONE) else []
    def responsive(limit=10):
        t = time.time()
        while time.time() - t < limit:
            try:
                o_ = app(); d_ = o_.Invoke(o_.GetIDsOfNames("ActiveDocument"), 0, G, True)
                d_.Invoke(d_.GetIDsOfNames("GetVariable"), 0, M, True, "CMDACTIVE"); return True
            except Exception:
                time.sleep(1)
        return False
    def restart_mep():
        import subprocess
        say("MEP locked: restarting and resuming from", len(done), "saved runs")
        subprocess.run(["taskkill", "/F", "/IM", "acad.exe"], capture_output=True); time.sleep(2)
        subprocess.Popen([os.path.join(A.acad_dir, "acad.exe"), "/ld", os.path.join(A.acad_dir, "AecBase.dbx"),
                          "/p", "AutoCAD MEP (US Imperial)", "/product", "MEP", "/language", "en-US", "/nologo"])
        time.sleep(20)
        if not wait_ready(600): say("MEP never came back"); sys.exit(5)
        time.sleep(5)
        o_ = app(); o_.Invoke(o_.GetIDsOfNames("WindowState"), 0, P, False, 2)
        call(get(app(), "Documents"), "Open", OUT); time.sleep(3); wait_idle(120)
        run('(setvar "FILEDIA" 0) (setvar "CMDECHO" 0) (setvar "BACKGROUNDPLOT" 0) (setvar "LOGFILEMODE" 1) (vl-load-com) (setvar "TILEMODE" 1) (princ)\n')
        run("_.PROPERTIESCLOSE\n"); run("_.-VIEW\n_SEISO\n")
        SIZE[1.5] = probe_size() or SIZE[1.5]
        run('(setq zz_mk (entlast)) (princ)\n')
    import threading, subprocess
    SKIP = os.path.join(W, "mep_skip.json")
    skip = json.load(open(SKIP)) if os.path.exists(SKIP) else []
    beat = [time.time(), None]                 # last progress time, current run name
    # command log folder, read here on the main thread (COM stays off the watchdog thread)
    try:
        LOGDIR = os.path.dirname(var("LOGFILENAME"))
    except Exception:
        LOGDIR = ""
    if not LOGDIR:
        LOGDIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Autodesk", "MEP 2027", "enu")
    def dog():
        while True:
            time.sleep(2)
            try:
                lf = max((os.path.join(LOGDIR, f) for f in os.listdir(LOGDIR) if f.lower().startswith(OUT_STEM)), key=os.path.getmtime)
                with open(lf, "rb") as h:
                    h.seek(max(0, os.path.getsize(lf) - 6000)); tail = h.read().decode("utf-8", "ignore")
            except Exception:
                tail = ""
            looping = tail.count("Next point or [") > 25 or "Multiple objects found" in tail[-1500:]
            if beat[1] and (looping or time.time() - beat[0] > 45):
                say("WATCHDOG: MEP stuck on run", beat[1], "(loop)" if looping else "(no progress 45 s)", "-> killing acad")
                subprocess.run(["taskkill", "/F", "/IM", "acad.exe"], capture_output=True)
                beat[0] = time.time() + 120
    threading.Thread(target=dog, daemon=True).start()
    run("_.PROPERTIESCLOSE\n"); run("_.-VIEW\n_SEISO\n")
    run('(setq zz_mk (entlast)) (princ)\n')
    # system letter -> its pipe layers (frozen while other systems draw); edit to match your model
    SYS_LAYERS = {"S": "M-CHWS-*", "R": "M-CHWR-*", "B": "M-BYPASS-*", "M": "M-MAKEUP-*", "C": "M-CHEM-0*,M-CHEM-1*",
                  "D": "M-DRAIN-*", "V": "M-RELIEF-*"}
    bad, since = [], []
    t = time.time()
    order = ordered(runs)
    i = 0
    while i < len(order):
        r = order[i]
        if r.name in done or r.name in skip:
            i += 1; continue
        p, sz = plan(r)
        ends_on = str(r.start).startswith("on:") and str(r.end).startswith("on:")
        beat[0], beat[1] = time.time(), r.name
        keep = {r.system} | {model.RUNS[k[3:]].system for k in (str(r.start), str(r.end)) if k.startswith("on:") and k[3:] in model.RUNS}
        frz = ",".join(SYS_LAYERS[k] for k in SYS_LAYERS if k not in keep)
        try:
            send("_.-LAYER\n_THAW\n*\n" + ("_FREEZE\n%s\n" % frz if frz else "") + "\n"); wait_idle(20)
            send(pipe_cmd(p, sz, ends_on)); time.sleep(0.4)
            if not responsive(12):
                raise RuntimeError("not responsive")
            wait_idle(60)
            run(layer_lisp(r), 0.1, 60)
            n = var("USERI1")
        except Exception as e:
            say("run", r.name, "failed:", str(e)[:80], "| skipping it, redoing", len(since), "unsaved runs")
            skip.append(r.name); json.dump(skip, open(SKIP, "w"))
            beat[1] = None
            restart_mep(); since = []
            i = 0
            continue
        beat[0] = time.time()
        if not n: bad.append(r.name)
        since.append(r.name)
        if i % 10 == 0: say("run", i, r.name, "objects", n)
        if len(since) >= 5 or i == len(order) - 1:
            run("_.QSAVE\n", 2, 300); done += since; since = []
            json.dump(done, open(DONE, "w"))
        i += 1
    beat[1] = None
    run("_.-LAYER\n_THAW\n*\n\n")
    say("pipes done", round(time.time() - t), "s | runs with no MEP objects:", bad, "| skipped:", skip)
    say("MEP objects", lisp_val('(sslength (ssget "X" (list (cons 0 "AECB_PIPE,AECB_PIPEFITTING"))))'),
        "pipes", lisp_val('(sslength (ssget "X" (list (cons 0 "AECB_PIPE"))))'))
    run("_.QSAVE\n", 2, 300)

if STAGE in ("all", "pipes", "plot"):
    if STAGE == "plot":   # the earlier stages set these; a plot-only run sets them itself
        uservars.save()
        run('(setvar "FILEDIA" 0) (setvar "CMDECHO" 0) (vl-load-com) (princ)\n')
    # hangers stay in the model but off; title text says MEP
    run('(command "_.-LAYER" "_OFF" "M-HGR-STRUT,M-HGR-ROD,M-HGR-CLEVIS,M-INSUL" "") (princ)\n')
    run(('(progn (setq zz_ss (ssget "X" (list (cons 0 "TEXT,MTEXT") (cons 1 "*3D MODEL*")))) (setq zz_i 0) '
         '(while (and zz_ss (< zz_i (sslength zz_ss))) (setq zz_o (vlax-ename->vla-object (ssname zz_ss zz_i))) '
         '(vla-put-textstring zz_o (vl-string-subst "AUTOCAD MEP MODEL" "3D MODEL" (vla-get-textstring zz_o))) (setq zz_i (1+ zz_i))) (princ))\n'))
    lays = [l for l in re.findall(LAYOUT_RE, lisp_val("(layoutlist)"))]
    lays = sorted(set(lays))
    say("layouts", lays)
    for L in lays:
        # shaded viewports: Realistic, no obscured edges, as displayed
        run(('(progn (command "_.LAYOUT" "_S" "%s") (setq zz_v (ssget "X" (list (cons 0 "VIEWPORT") (cons 410 "%s")))) (setq zz_i 0 zz_sh 0) '
             '(command "_.PSPACE") (command "_.MVIEW" "_L" "_OFF" "_ALL" "") (command "_.MSPACE") '
             '(while (and zz_v (< zz_i (sslength zz_v))) (setq zz_d (entget (ssname zz_v zz_i))) '
             '(if (/= (cdr (assoc 69 zz_d)) 1) (progn (setvar "CVPORT" (cdr (assoc 69 zz_d))) (command "_.VSCURRENT" "_R") '
             '(setvar "VSOBSCUREDEDGES" 0) (setvar "VSEDGES" 0) (setq zz_sh (1+ zz_sh)))) (setq zz_i (1+ zz_i))) '
             '(command "_.PSPACE") (command "_.MVIEW" "_L" "_ON" "_ALL" "") (setvar "USERI3" zz_sh) (princ))\n') % (L, L), 1, 120)
        shaded = var("USERI3")
        pdf = "%s/mep_%s.pdf" % (WF, L)
        if os.path.exists(pdf): os.remove(pdf)
        tail = "_Q\n_C\n250\n_N\n_Y\n" if shaded else "_N\n_Y\n"
        seq = ("_.-PLOT\n_Y\n%s\nDWG To PDF.pc3\nANSI full bleed B (17.00 x 11.00 Inches)\n_I\n_L\n_N\n_W\n0,0\n17,11\n_F\n0,0\n_Y\n"
               ".\n_Y\n_N\n_N\n_N\n%s\n" % (L, pdf)) + tail
        t = time.time(); run(seq, 3, 300)
        say("plot", L, "viewports", shaded, "|", round(time.time() - t), "s |", os.path.exists(pdf))
    run('(command "_.LAYOUT" "_S" "Model") (princ)\n')
    run("_.QSAVE\n", 2, 300)

say("user settings put back:", uservars.restore())
guard.stop = True
say("DIALOGS SEEN:", [(d[1], d[2][:4]) for d in guard.seen])
say("END")
