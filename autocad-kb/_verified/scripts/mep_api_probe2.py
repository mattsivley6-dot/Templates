"""Live probe v2 of the AutoCAD MEP 2027 COM API (AecX ... 8.9) on a scratch copy of the routing preference library.

Every value sent to a prompt is validated first (v1 sent an error string into -AECBPIPEADD and MEP spun at the prompt).
usage: py -3.14 mep_api_probe2.py <scratch_dir>
"""
import json, os, shutil, sys, time, traceback
import pythoncom
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m

SCR = sys.argv[1].replace("\\", "/")
os.makedirs(SCR, exist_ok=True)
LOG = []
PUT = pythoncom.DISPATCH_PROPERTYPUT


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)


def put(o, name, val):
    return o.Invoke(o.GetIDsOfNames(name), 0, PUT, False, val)


def tryget(o, name, *a):
    try:
        return m.get(o, name, *a)
    except Exception as e:
        return "ERR " + str(e)[:90]


def lisp_to_file(doc, body, path, timeout=30):
    """Run LISP that writes lines to `path` via handle f; return the lines."""
    if os.path.exists(path):
        os.remove(path)
    expr = '(progn (setq f (open "%s" "w")) %s (close f) (setq f nil) (princ))\n' % (path, body)
    m.call(doc, "SendCommand", expr)
    t = time.time()
    while time.time() - t < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            time.sleep(0.3)
            return open(path, encoding="utf-8", errors="ignore").read().splitlines()
        time.sleep(0.3)
    return []


def cmdlog_new(doc, start):
    p = m.call(doc, "GetVariable", "LOGFILENAME")
    try:
        data = open(p, "rb").read()[start:]
        return data.decode("utf-8", "ignore"), p
    except Exception as e:
        return "LOGREAD ERR %s" % e, p


guard = m.DialogGuard(cancel=True)
guard.start()
try:
    a = m.app()
    try:
        put(a, "WindowState", 2)
    except Exception as e:
        log("minimize failed", e)
    src = r"C:\ProgramData\Autodesk\MEP 2027\enu\Styles\Imperial\Routing Preferences (US Imperial).dwg"
    dst = SCR + "/rp_probe2.dwg"
    shutil.copyfile(src, dst)
    docs = m.get(a, "Documents")
    doc = m.call(docs, "Open", dst)
    m.wait_idle(120)
    m.call(doc, "SetVariable", "TILEMODE", 1)
    m.call(doc, "SetVariable", "LOGFILEMODE", 1)
    db = m.get(doc, "Database")
    log("opened", m.get(doc, "Name"), "| CPROFILE", m.call(doc, "GetVariable", "CPROFILE"))

    # A. names straight from the drawing dictionaries (AutoLISP)
    nod = lisp_to_file(doc, '(foreach p (entget (namedobjdict)) (if (= (car p) 3) (write-line (cdr p) f)))', SCR + "/nod.txt")
    log("NOD keys:", [k for k in nod if k.upper().startswith(("AECB", "AEC_"))][:60])
    rpn = lisp_to_file(doc, '(foreach p (dictsearch (namedobjdict) "AECB_PIPE_PARTROUTINGPREFERENCES_STYLES") (if (= (car p) 3) (write-line (cdr p) f)))', SCR + "/rp.txt")
    log("routing preferences (dictionary):", len(rpn), rpn)
    sysn = lisp_to_file(doc, '(foreach p (dictsearch (namedobjdict) "AECB_PIPESYSTEMDEFS") (if (= (car p) 3) (write-line (cdr p) f)))', SCR + "/sys.txt")
    log("pipe systems (dictionary):", sysn)

    # B. same through COM
    pdb = m.call(a, "GetInterfaceObject", "AecX.AecbPipeDatabase.8.9")
    m.call(pdb, "Init", db)
    rps = m.get(pdb, "PipePartCatPrefStyles")
    log("COM PipePartCatPrefStyles.Count =", m.get(rps, "Count"))
    for nm in (rpn[:3] if rpn else ["Standard"]):
        try:
            log("  Has(%r) =" % nm, m.call(rps, "Has", nm))
        except Exception as e:
            log("  Has(%r) ERR" % nm, e)
        try:
            it = m.call(rps, "Item", nm)
            log("  Item(%r).Name =" % nm, tryget(it, "Name"))
        except Exception as e:
            log("  Item(%r) ERR" % nm, e)
    sds = m.get(pdb, "PipeSystemDefs")
    log("COM PipeSystemDefs:", [m.get(m.call(sds, "Item", i), "Name") for i in range(m.get(sds, "Count"))])
    for k in ("PipeStyles", "PipeFittingStyles", "PipeFlexStyles", "PipeCustomFittingStyles", "PipeRiseDropStyles"):
        log(k, "count", tryget(m.get(pdb, k), "Count"))

    # C. create a pipe system definition over COM (no spaces in the name: a space ends input at MEP prompts)
    sysname = "CHWS"
    if not m.call(sds, "Has", sysname):
        sd = m.call(sds, "Add", sysname)
        put(sd, "LabelName", "CHWS")
        put(sd, "FamilyName", "Chilled Water")
        put(sd, "Description", "Chilled water supply (created by COM probe)")
        log("added system", m.get(sd, "Name"), "label", m.get(sd, "LabelName"), "family", m.get(sd, "FamilyName"),
            "layerkey", repr(tryget(sd, "LayerKey")), "min dia", tryget(sd, "MinimumNominalDiameter"))
    sysn2 = lisp_to_file(doc, '(foreach p (dictsearch (namedobjdict) "AECB_PIPESYSTEMDEFS") (if (= (car p) 3) (write-line (cdr p) f)))', SCR + "/sys2.txt")
    log("pipe systems after COM Add (dictionary):", sysn2)

    # D. draw a pipe run on the command line with validated values
    pref = next((p for p in rpn if p.lower() == "glued"), None) or next((p for p in rpn if " " not in p), None)
    if not pref or " " in pref:
        raise SystemExit("no space-free routing preference to test with: %r" % rpn)
    lp = m.call(doc, "GetVariable", "LOGFILENAME")
    start = os.path.getsize(lp) if os.path.exists(lp) else 0
    cmd = '_-AECBPIPEADD\nR\n%s\nSY\n%s\nSI\n4"\n_non\n0,0,120\n_non\n240,0,120\n_non\n240,240,120\n\n' % (pref, sysname)
    log("sending:", cmd.replace("\n", " / "))
    m.send(cmd)
    ok = m.wait_idle(90)
    txt, lp = cmdlog_new(doc, start)
    log("idle after pipe command:", ok, "| command log since send:\n" + txt[-2500:])
    if not ok:
        raise SystemExit("MEP not idle after pipe command; stopping before more input")

    ms = m.get(doc, "ModelSpace")
    pipes, fittings = [], []
    for i in range(m.get(ms, "Count")):
        e = m.call(ms, "Item", i)
        on = m.get(e, "ObjectName")
        (pipes if on == "AecbDbPipe" else fittings if "Fitting" in on else []).append(e)
        log("entity", i, on, m.get(e, "Layer"), m.get(e, "Handle"))
    for k, p in enumerate(pipes):
        info = {f: tryget(p, f) for f in ("StartPoint", "EndPoint", "Length", "CutLength", "SizeName", "CrossSectionSize",
                                           "NominalSize", "SystemName", "SystemAbbreviation", "SystemFamily",
                                           "PartDescription", "StyleName", "Elevation", "TopElevation", "BottomElevation",
                                           "LockSize", "InsulationThickness", "Type", "SubType", "Name", "Description")}
        log("pipe", k, json.dumps(info, default=str))
        cons = m.get(p, "Connectors")
        for j in range(m.get(cons, "Count")):
            c = m.call(cons, "Item", j)
            cm = tryget(c, "ConnectedMembers")
            log("   connector", j, "loc", tryget(c, "Location"), "dir", tryget(c, "Direction"), "type", tryget(c, "ConnectionType"),
                "size", tryget(c, "WidthorDiameter"), "connected", tryget(cm, "Count") if not isinstance(cm, str) else cm)
    for k, f in enumerate(fittings):
        log("fitting", k, m.get(f, "ObjectName"), "|", tryget(f, "PartDescription"), "|", tryget(f, "SizeName"), "|", tryget(f, "SystemName"))

    # E. write tests
    if pipes:
        p0 = pipes[0]
        for prop, val in (("Elevation", 132.0), ("InsulationThickness", 1.0)):
            try:
                put(p0, prop, val); m.wait_idle(30)
                log("put %s %s -> %s | start %s end %s" % (prop, val, tryget(p0, prop), tryget(p0, "StartPoint"), tryget(p0, "EndPoint")))
            except Exception as e:
                log("put %s ERR %s" % (prop, e))
        try:
            put(p0, "SystemName", "Standard"); log("put SystemName Standard ->", tryget(p0, "SystemName"))
            put(p0, "SystemName", sysname); log("put SystemName back ->", tryget(p0, "SystemName"))
        except Exception as e:
            log("put SystemName ERR", e)
        try:
            sp = list(tryget(p0, "StartPoint"))
            put(p0, "StartPoint", (sp[0] - 24.0, sp[1], sp[2])); m.wait_idle(30)
            log("put StartPoint -24 in x -> start", tryget(p0, "StartPoint"), "length", tryget(p0, "Length"))
        except Exception as e:
            log("put StartPoint ERR", e)
        try:
            mid = tryget(p0, "MidPoint")
            r = m.call(p0, "Break", mid); m.wait_idle(30)
            log("Break at midpoint -> returned", r, "| modelspace count", m.get(ms, "Count"))
        except Exception as e:
            log("Break ERR", e)

    # F. property sets and schedules
    try:
        sa = m.call(a, "GetInterfaceObject", "AecX.AecScheduleApplication.8.9")
        psds = m.call(sa, "PropertySetDefs", db)
        n = m.get(psds, "Count")
        log("PropertySetDefs:", n, [m.get(m.call(psds, "Item", i), "Name") for i in range(min(n, 25))])
        if pipes:
            pss = m.call(sa, "PropertySets", pipes[-1])
            log("PropertySets on a pipe:", m.get(pss, "Count"))
    except Exception as e:
        log("schedule API ERR", e)

    # G. building-services database graphs
    try:
        bdb = m.call(a, "GetInterfaceObject", "AecX.AecbDatabase.8.9")
        m.call(bdb, "Init", db)
        g = m.get(bdb, "Graphs")
        log("Graphs.Count", m.get(g, "Count"))
    except Exception as e:
        log("Graphs ERR", e)

    out = SCR + "/rp_probe2_after.dwg"
    m.call(doc, "SaveAs", out); m.wait_idle(60)
    log("saved", out)
    m.call(doc, "Close", False)
    log("closed")
except SystemExit as e:
    log("STOP:", e)
except Exception:
    log("FATAL", traceback.format_exc())
finally:
    guard.stop = True
    log("dialogs seen:", guard.seen)
    open(SCR + "/mep_api_probe2.log", "w", encoding="utf-8").write("\n".join(LOG))
