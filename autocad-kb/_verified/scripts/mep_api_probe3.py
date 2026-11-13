"""Live probe v3: point-array writes, Break, layer changes, connected members and graph walking on MEP pipes.

usage: py -3.14 mep_api_probe3.py <scratch_dir>
"""
import os, shutil, sys, time, traceback
import pythoncom, win32com.client
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


def pt(x, y, z):
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (float(x), float(y), float(z)))


def tryget(o, name, *a):
    try:
        return m.get(o, name, *a)
    except Exception as e:
        return "ERR " + str(e)[:90]


def members(conn):
    """ConnectedMembers comes back as a variant; show what it is."""
    try:
        v = m.get(conn, "ConnectedMembers")
    except Exception as e:
        return "ERR %s" % e
    if v is None:
        return "None"
    if isinstance(v, (tuple, list)):
        out = []
        for x in v:
            try:
                out.append((m.get(x, "ObjectName"), m.get(x, "Handle")))
            except Exception as e:
                out.append(repr(x)[:60])
        return out
    try:
        n = m.get(v, "Count")
        return [(m.get(m.call(v, "Item", i), "ObjectName"), m.get(m.call(v, "Item", i), "Handle")) for i in range(n)]
    except Exception as e:
        return "type %s %s" % (type(v).__name__, e)


guard = m.DialogGuard(cancel=True)
guard.start()
try:
    a = m.app()
    put(a, "WindowState", 2)
    src = SCR.replace("mep_probe3", "mep_probe2") + "/rp_probe2_after.dwg"
    dst = SCR + "/rp_probe3.dwg"
    shutil.copyfile(src, dst)
    doc = m.call(m.get(a, "Documents"), "Open", dst)
    m.wait_idle(120)
    m.call(doc, "SetVariable", "TILEMODE", 1)
    db = m.get(doc, "Database")
    ms = m.get(doc, "ModelSpace")
    ents = [m.call(ms, "Item", i) for i in range(m.get(ms, "Count"))]
    pipes = [e for e in ents if m.get(e, "ObjectName") == "AecbDbPipe"]
    fits = [e for e in ents if "Fitting" in m.get(e, "ObjectName")]
    log("pipes", len(pipes), "fittings", len(fits))
    for p in pipes:
        log("pipe", m.get(p, "Handle"), "start", tryget(p, "StartPoint"), "end", tryget(p, "EndPoint"), "elev", tryget(p, "Elevation"), "sys", tryget(p, "SystemName"))
    p0, p1 = pipes[0], pipes[1]

    # connectors and connected members
    for p in pipes + fits:
        cons = m.get(p, "Connectors")
        n = m.get(cons, "Count")
        rows = []
        for j in range(n):
            try:
                c = m.call(cons, "Item", j)
                rows.append((j, tryget(c, "Location"), members(c)))
            except Exception as e:
                rows.append((j, "ERR %s" % str(e)[:60]))
        log(m.get(p, "ObjectName"), m.get(p, "Handle"), "connectors.Count", n, rows)

    # elevation back to 120 so the run reconnects? report what happens to the fitting
    put(p0, "Elevation", 120.0); m.wait_idle(30)
    log("p0 elevation back to 120 -> start", tryget(p0, "StartPoint"))

    # StartPoint with a VT_R8 array
    try:
        sp = tryget(p0, "StartPoint")
        put(p0, "StartPoint", pt(sp[0] - 24.0, sp[1], sp[2])); m.wait_idle(30)
        log("put StartPoint (VT_R8 array) -> start", tryget(p0, "StartPoint"), "length", tryget(p0, "Length"))
    except Exception as e:
        log("put StartPoint VT_R8 ERR", e)
    # EndPoint of the second pipe
    try:
        ep = tryget(p1, "EndPoint")
        put(p1, "EndPoint", pt(ep[0], ep[1] + 36.0, ep[2])); m.wait_idle(30)
        log("put EndPoint (VT_R8 array) -> end", tryget(p1, "EndPoint"), "length", tryget(p1, "Length"))
    except Exception as e:
        log("put EndPoint VT_R8 ERR", e)
    # Break with a VT_R8 array
    try:
        mid = tryget(p1, "MidPoint")
        r = m.call(p1, "Break", pt(*mid)); m.wait_idle(30)
        log("Break(VT_R8 mid) -> returned", r, "modelspace count", m.get(ms, "Count"))
    except Exception as e:
        log("Break VT_R8 ERR", e)

    # SystemName variants
    for v in ("CHWS (CHWS)", "CHWS"):
        try:
            put(p0, "SystemName", v); log("put SystemName %r ->" % v, tryget(p0, "SystemName"))
        except Exception as e:
            log("put SystemName %r ERR %s" % (v, e))

    # Layer change on an MEP pipe (plain AcadEntity property)
    try:
        lays = m.get(doc, "Layers")
        try:
            m.call(lays, "Add", "M-CHWS")
        except Exception:
            pass
        put(p0, "Layer", "M-CHWS"); log("put Layer M-CHWS ->", tryget(p0, "Layer"))
    except Exception as e:
        log("put Layer ERR", e)

    # graph walk
    try:
        bdb = m.call(a, "GetInterfaceObject", "AecX.AecbDatabase.8.9")
        m.call(bdb, "Init", db)
        gs = m.get(bdb, "Graphs")
        n = m.get(gs, "Count")
        log("Graphs.Count", n)
        for gi in range(n):
            g = m.call(gs, "Item", gi)
            cnt = tryget(g, "Count")
            names = []
            try:
                for k in range(cnt):
                    mem = m.call(g, "Item", k)
                    names.append((m.get(mem, "ObjectName"), m.get(mem, "Handle")))
            except Exception as e:
                names.append("ERR %s" % str(e)[:60])
            log("  graph", gi, "count", cnt, names)
            try:
                it = m.call(g, "Iterator")
                steps = []
                guard_n = 0
                while not m.get(it, "Done") and guard_n < 50:
                    mem = m.get(it, "Member")
                    steps.append(m.get(mem, "Handle"))
                    m.call(it, "Step")
                    guard_n += 1
                log("  iterator walk:", steps)
            except Exception as e:
                log("  iterator ERR", e)
    except Exception as e:
        log("graph ERR", e)

    out = SCR + "/rp_probe3_after.dwg"
    m.call(doc, "SaveAs", out); m.wait_idle(60)
    log("saved", out)
    m.call(doc, "Close", False)
except Exception:
    log("FATAL", traceback.format_exc())
finally:
    guard.stop = True
    log("dialogs seen:", guard.seen)
    open(SCR + "/mep_api_probe3.log", "w", encoding="utf-8").write("\n".join(LOG))
