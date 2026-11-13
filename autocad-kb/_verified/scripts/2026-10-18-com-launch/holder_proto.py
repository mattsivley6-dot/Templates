"""Prototype, no AutoCAD: can a holder process put a PROXY to another process's object in the ROT under its own name,
so any later process reaches that object (the second instance under a duplicate !{CLSID} name)?
roles:  main <work_dir> | server <log> <secs> | holder <server_pid> <log> <secs> | client <server_pid>
"""
import json, os, subprocess, sys, time
import pythoncom, pywintypes, win32com.server.util

TEST_CLSID = "{3F6B2E1A-9C4D-4B7E-8A21-5D0C7E9F1B42}"      # same test CLSID the stand-ins use
G, M = pythoncom.DISPATCH_PROPERTYGET, pythoncom.DISPATCH_METHOD
HERE = os.path.dirname(os.path.abspath(__file__))
STANDIN = os.path.join(os.path.dirname(HERE), "mepcom_standin.py")      # the stand-in one folder up


def item(name):
    return pythoncom.CreateItemMoniker("!", name)


def log(path, **k):
    k["pid"], k["t"] = os.getpid(), round(time.time(), 3)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(k) + "\n")


def events(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if os.path.exists(path) else []


def wait_event(path, name, secs=20):
    t = time.time()
    while time.time() - t < secs:
        for e in events(path):
            if e.get("event") == name:
                return e
        time.sleep(0.1)
    return None


def call(o, name, *a):
    return o.Invoke(o.GetIDsOfNames(name), 0, M, True, *a)


def lookup(name):
    rot = pythoncom.GetRunningObjectTable()
    o = rot.GetObject(item(name)).QueryInterface(pythoncom.IID_IDispatch)
    if name.startswith("mepcom.acad."):      # the holder's locator: its App property is the instance itself
        o = o.Invoke(o.GetIDsOfNames("App"), 0, G, True)
    return o


def clsid_walk():
    rot, ctx, out = pythoncom.GetRunningObjectTable(), pythoncom.CreateBindCtx(0), []
    want = ("!" + TEST_CLSID).upper()
    for mk in rot.EnumRunning():
        try:
            if mk.GetDisplayName(ctx, None).upper() == want:
                out.append(call(rot.GetObject(mk).QueryInterface(pythoncom.IID_IDispatch), "Pid"))
        except pythoncom.com_error:
            pass
    return out


ROLE = sys.argv[1]
if ROLE == "server":                         # models the SECOND acad.exe: duplicate !{CLSID} entry plus a hand-off name
    LOGP, SECS = sys.argv[2], float(sys.argv[3])

    class App:
        _public_methods_ = ["Pid"]

        def Pid(self):
            return os.getpid()

    ob = win32com.server.util.wrap(App())
    try:
        dup = pythoncom.RegisterActiveObject(ob, pywintypes.IID(TEST_CLSID), 0)
    except pywintypes.com_error as e:
        if e.hresult != 262631:              # MK_S_MONIKERALREADYREGISTERED: stored, unreachable (what acad #2 gets)
            raise
        dup = None
    rot = pythoncom.GetRunningObjectTable()
    hand = rot.Register(0, ob, item("mepcom-handoff.%d" % os.getpid()))
    log(LOGP, event="ready", dup_handle=dup)
    t, revoked = time.time(), False
    while time.time() - t < SECS and not os.path.exists(LOGP + ".stop"):
        if not revoked and os.path.exists(LOGP + ".handed"):
            rot.Revoke(hand); revoked = True
            log(LOGP, event="handoff_revoked")
        pythoncom.PumpWaitingMessages()
        time.sleep(0.02)
    if dup is not None:
        pythoncom.RevokeActiveObject(dup)
    log(LOGP, event="exit")

elif ROLE == "holder":                       # models mepcom's holder: keeps the proxy, registers it under its own name
    spid, LOGP, SECS = int(sys.argv[2]), sys.argv[3], float(sys.argv[4])
    proxy = lookup("mepcom-handoff.%d" % spid)
    got = call(proxy, "Pid")
    rot, tries = pythoncom.GetRunningObjectTable(), {}
    for flags in (1, 0):                     # the proxy itself: 1 = ROTFLAGS_REGISTRATIONKEEPSALIVE
        try:
            rot.Revoke(rot.Register(flags, proxy, item("mepcom-proxytry.%d" % spid))); tries[flags] = "ok"
        except pythoncom.com_error as e:
            tries[flags] = [e.hresult, e.strerror]

    class Locator:                           # a real object in this process (the ROT accepts those); App hands out the proxy
        _public_methods_ = []
        _public_attrs_ = _readonly_attrs_ = ["App", "Pid"]
        App, Pid = proxy, spid

    cookie = rot.Register(1, win32com.server.util.wrap(Locator()), item("mepcom.acad.%d" % spid))
    log(LOGP, event="ready", proxy_pid=got, registered=True, proxy_register_tries=tries)
    t = time.time()
    while time.time() - t < SECS and not os.path.exists(LOGP + ".stop"):
        pythoncom.PumpWaitingMessages()
        time.sleep(0.02)
    if cookie is not None:
        rot.Revoke(cookie)
    log(LOGP, event="exit")

elif ROLE == "client":                       # a later, separate script
    spid = int(sys.argv[2])
    try:
        print(json.dumps({"reached": call(lookup("mepcom.acad.%d" % spid), "Pid")}))
    except pythoncom.com_error as e:
        print(json.dumps({"error": [e.hresult, e.strerror]}))

else:                                        # main
    W = os.path.abspath(sys.argv[2]); os.makedirs(W, exist_ok=True)
    la, lb, lh = (os.path.join(W, n) for n in ("a.jsonl", "b.jsonl", "h.jsonl"))
    for p in (la, lb, lh):
        for x in (p, p + ".stop", p + ".handed"):
            if os.path.exists(x):
                os.remove(x)
    R = []

    def check(name, ok, detail=""):
        R.append(bool(ok)); print("%s  %s  | %s" % ("PASS" if ok else "FAIL", name, detail), flush=True)

    pa = subprocess.Popen([sys.executable, STANDIN, la, "90"]); wait_event(la, "ready")
    pb = subprocess.Popen([sys.executable, __file__, "server", lb, "90"]); wait_event(lb, "ready")
    A, B = pa.pid, pb.pid
    print("A (first) pid %d, B (duplicate) pid %d" % (A, B))
    try:
        check("the !{CLSID} walk gives A for both entries (B unreachable by that name)", clsid_walk() == [A, A], clsid_walk())
        ph = subprocess.Popen([sys.executable, __file__, "holder", str(B), lh, "90"])
        e = wait_event(lh, "ready")
        check("holder got B's object and registered a locator under !mepcom.acad.<B>", e and e["proxy_pid"] == B and e["registered"], e)
        open(lb + ".handed", "w").close(); wait_event(lb, "handoff_revoked")
        mine = lookup("mepcom.acad.%d" % B)
        check("this process reaches B by the holder's name (hand-off name gone)", call(mine, "Pid") == B)
        out = subprocess.run([sys.executable, __file__, "client", str(B)], capture_output=True, text=True).stdout.strip()
        check("a separate later process reaches B by the holder's name", json.loads(out).get("reached") == B, out)
        check("the !{CLSID} walk still gives A, A (unchanged)", clsid_walk() == [A, A], clsid_walk())
        open(lh + ".stop", "w").close(); ph.wait(15)
        try:
            lookup("mepcom.acad.%d" % B); gone = False
        except pythoncom.com_error:
            gone = True
        check("holder exit removes its ROT entry", gone)
        try:
            still = call(mine, "Pid") == B
        except pythoncom.com_error as x:
            still = "com_error %s" % x.hresult
        check("a proxy fetched before the holder exited still reaches B (goes straight to B, not through the holder)", still is True, still)
    finally:
        for p in (la, lb, lh):
            open(p + ".stop", "w").close()
        for p in (pa, pb):
            try:
                p.wait(15)
            except subprocess.TimeoutExpired:
                p.kill()
    check("nothing left under the test name", clsid_walk() == [], clsid_walk())
    print("RESULT: %d of %d" % (sum(R), len(R)))
