"""Prove mepcom's PID binding (2026-10-18) without starting a second AutoCAD.

Part 1 reads the AutoCAD that is running, read only (HWND reads and a dialog listing; it never cancels a real dialog).
Part 2 starts two stand-ins (mepcom_standin.py) that register the SAME !{CLSID} name in the Running Object Table, the
way two acad.exe do, and checks app(pid), instances(), bind(), dialogs(pids) and DialogGuard(pid) against them.
usage: py -3.14 mepcom_pid_test.py <work_dir>
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import pythoncom, win32gui, win32process

W = os.path.abspath(sys.argv[1])
os.makedirs(W, exist_ok=True)
TEST_CLSID = "{3F6B2E1A-9C4D-4B7E-8A21-5D0C7E9F1B42}"      # same as mepcom_standin.py
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  | " + str(detail)) if detail != "" else ""), flush=True)


def fails_closed(f):
    try:
        f()
        return False, "no error"
    except pythoncom.com_error as e:
        return e.hresult == m.MK_E_UNAVAILABLE, "com_error %s: %s" % (e.hresult, e.strerror)


def hwnd_pid(a):
    return win32process.GetWindowThreadProcessId(m.get(a, "HWND"))[1]


def owner(h):
    return win32process.GetWindowThreadProcessId(h)[1]


# ---------------------------------------------------------------- part 1: the real AutoCAD, read only
real = m._acad_pids()
print("acad.exe running:", sorted(real))
if real:
    inst = m.instances()
    print("PID map:", {p: m.get(a, "Caption") for p, a in inst.items()})
    shared = [p for p, a in m._rot() if a is not None]               # the one the shared !{CLSID} entry gives
    check("instances() maps the reachable AutoCAD (plus any launch() instance) to running acad.exe pids",
          shared and shared[0] in inst and set(inst) <= real, sorted(inst))
    p0 = shared[0]
    check("unbound app() (GetActiveObject, as before) is that same acad.exe", hwnd_pid(m.app()) == p0)
    check("app(%d) returns it" % p0, hwnd_pid(m.app(p0)) == p0)
    ok, d = fails_closed(lambda: m.app(4))
    check("app(pid with no acad.exe) fails closed", ok, d)
    m.bind(p0)
    check("bind(%d): app() and DialogGuard() follow the bound pid" % p0, hwnd_pid(m.app()) == p0 and m.DialogGuard(cancel=False).pids == {p0})
    m.bind(4)
    ok, d = fails_closed(m.app)
    check("bind(4): app() fails closed instead of using GetActiveObject", ok, d)
    m.bind(None)
    check("bind(None): app() is GetActiveObject again and DialogGuard() covers every acad.exe", hwnd_pid(m.app()) == p0 and m.DialogGuard(cancel=False).pids is None)
    d_all, d_p0, d_x = m.dialogs(), m.dialogs(p0), m.dialogs({4})
    print("real dialogs (listed, not touched):", [(t, x[:3]) for _, t, x in d_all])
    if len(real) == 1:
        check("dialogs(%d) equals unbound dialogs() with one acad.exe; dialogs({4}) is empty" % p0, [h for h, _, _ in d_all] == [h for h, _, _ in d_p0] and d_x == [])
    else:
        check("dialogs(%d) lists only that pid's dialogs; dialogs({4}) is empty" % p0,
              all(win32process.GetWindowThreadProcessId(h)[1] == p0 for h, _, _ in d_p0) and d_x == [])

# ---------------------------------------------------------------- part 2: two stand-ins under one ROT name
m.PROGID = TEST_CLSID                                        # same lookups, aimed at the stand-ins instead of AutoCAD
logs = [os.path.join(W, "standin_a.jsonl"), os.path.join(W, "standin_b.jsonl")]
for p in logs + [x + ".stop" for x in logs]:
    if os.path.exists(p):
        os.remove(p)
procs = []
for lp in logs:
    procs.append(subprocess.Popen([sys.executable, os.path.join(HERE, "mepcom_standin.py"), lp, "60"]))
    t = time.time()
    while time.time() - t < 20 and not (os.path.exists(lp) and '"ready"' in open(lp, encoding="utf-8").read()):
        time.sleep(0.1)
A, B = procs[0].pid, procs[1].pid
ready = [json.loads(open(lp, encoding="utf-8").readline()) for lp in logs]
print("stand-ins: A pid %d (ROT handle %s), B pid %d (ROT handle %s = registered as a duplicate)" % (A, ready[0]["rot_handle"], B, ready[1]["rot_handle"]))


def events(lp):
    return [json.loads(l) for l in open(lp, encoding="utf-8") if l.strip()]


try:
    rot = m._rot()
    check("the ROT lists both stand-ins, and BOTH entries give A (only the first registered is reachable)", [p for p, a in rot] == [A, A], [p for p, a in rot])
    check("instances() == {A}", set(m.instances()) == {A}, sorted(m.instances()))
    check("app(A) is A", m.call(m.app(A), "Pid") == A)
    ok, d = fails_closed(lambda: m.app(B))
    check("app(B) fails closed: B runs but COM cannot reach it", ok, d)
    check("unbound app() gives A, the first registered: the old cross-talk", m.call(m.app(), "Pid") == A)
    da, db = m.dialogs(A), m.dialogs({B})
    check("dialogs(A) lists only A's dialog", len(da) == 1 and owner(da[0][0]) == A, [(t, owner(h)) for h, t, _ in da])
    check("dialogs({B}) lists only B's dialog", len(db) == 1 and owner(db[0][0]) == B, [(t, owner(h)) for h, t, _ in db])
    check("unbound dialogs() lists acad.exe dialogs only, no stand-in", all(owner(h) in m._acad_pids() for h, _, _ in m.dialogs()))
    g = m.DialogGuard(pid=B)
    g.start(); time.sleep(2); g.stop = True; g.join(3)
    a_cmd = [e["id"] for e in events(logs[0]) if e["event"] == "WM_COMMAND"]
    b_cmd = [e["id"] for e in events(logs[1]) if e["event"] == "WM_COMMAND"]
    check("DialogGuard(pid=B) cancelled B's dialog (IDCANCEL = 2)", b_cmd[:1] == [2] and not win32gui.IsWindow(db[0][0]), b_cmd)
    check("DialogGuard(pid=B) left A's dialog alone", a_cmd == [] and win32gui.IsWindow(da[0][0]), a_cmd)
    m.bind(A)
    g2 = m.DialogGuard()
    check("bind(A): DialogGuard() and dialogs() default to A", g2.pids == {A} and [owner(h) for h, _, _ in m.dialogs()] == [A])
    g2.start(); time.sleep(2); g2.stop = True; g2.join(3)
    a_cmd = [e["id"] for e in events(logs[0]) if e["event"] == "WM_COMMAND"]
    check("bound DialogGuard() cancelled A's dialog", a_cmd[:1] == [2] and not win32gui.IsWindow(da[0][0]), a_cmd)
    m.bind(B)
    ok, d = fails_closed(m.app)
    check("bind(B): app() fails closed", ok, d)
    m.bind(None)
    check("unbound DialogGuard() still covers every acad.exe (pids None)", m.DialogGuard().pids is None)
finally:
    m.bind(None)
    for lp in logs:
        open(lp + ".stop", "w").close()
    for p in procs:
        try:
            p.wait(15)
        except subprocess.TimeoutExpired:
            p.kill()                                         # our own stand-in, by its Popen handle
left = m._rot()
m.PROGID = "AutoCAD.Application"
check("stand-ins gone: nothing left in the ROT under the test name", left == [], left)


# ---------------------------------------------------------------- part 3: launch()'s locator, with stand-ins (2026-10-18)
# The real holder gets AutoCAD from CoCreateInstance and runs mepcom._serve on it. mepcom_holder_standin.py runs the same
# _serve on a stand-in that registered SECOND under the shared name, so the shared entry cannot reach it (part 2).
def wait_for(lp, name, secs=20):
    t = time.time()
    while time.time() - t < secs:
        if os.path.exists(lp) and any(e.get("event") == name for e in events(lp)):
            return True
        time.sleep(0.1)
    return False


def exit_event(state, secs=20):
    t = time.time()
    while time.time() - t < secs:
        ev = [e for e in events(state) if e.get("event") == "exit"] if os.path.exists(state) else []
        if ev:
            return ev[-1]
        time.sleep(0.1)
    return None


m.PROGID = TEST_CLSID
la3, lb3, lc3 = (os.path.join(W, n) for n in ("standin3_a.jsonl", "standin3_b.jsonl", "standin3_c.jsonl"))
s1, s2 = os.path.join(W, "holder3_1.jsonl"), os.path.join(W, "holder3_2.jsonl")
for p in (la3, lb3, lc3, s1, s2):
    for x in (p, p + ".stop", p + ".handed"):
        if os.path.exists(x):
            os.remove(x)
procs3 = []


def standin(lp, *extra):
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "mepcom_standin.py"), lp, "90"] + list(extra))
    procs3.append(p)
    wait_for(lp, "ready")
    return p


def holder(pid, state):
    h = subprocess.Popen([sys.executable, os.path.join(HERE, "mepcom_holder_standin.py"), str(pid), state])
    procs3.append(h)
    wait_for(state, "ready")
    return h


try:
    A3, B3 = standin(la3).pid, standin(lb3, "--handoff").pid
    print("part 3 stand-ins: A pid %d (first), B pid %d (second, with a hand-off name)" % (A3, B3))
    ok, d = fails_closed(lambda: m.app(B3))
    check("no holder yet: app(B) fails closed (B registered second)", ok, d)
    h1 = holder(B3, s1)
    open(lb3 + ".handed", "w").close()
    wait_for(lb3, "handoff_revoked")
    check("_held_pids() lists B once its holder's locator is in the ROT", m._held_pids() == [B3], m._held_pids())
    check("app(B) reaches B through the locator (hand-off name gone)", m.call(m.app(B3), "Pid") == B3)
    check("instances() == {A, B}", set(m.instances()) == {A3, B3}, sorted(m.instances()))
    check("unbound app() still gives A (GetActiveObject, unchanged)", m.call(m.app(), "Pid") == A3)
    m.bind(B3)
    check("bind(B): app() is B, DialogGuard() covers only B", m.call(m.app(), "Pid") == B3 and m.DialogGuard(cancel=False).pids == {B3})
    m.bind(None)
    code = ("import os, sys; sys.path.insert(0, os.environ['AUTOCAD_SKILL_SCRIPTS']); import mepcom as m; "
            "print(m.call(m.app(%d), 'Pid'))" % B3)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    check("a separate later process reaches B with app(pid)", out.stdout.strip() == str(B3), (out.stdout.strip(), out.stderr.strip()[-200:]))
    held = m.app(B3)
    open(s1 + ".stop", "w").close()
    ev = exit_event(s1)
    check("holder stop file: exit event, locator gone, nothing set in the registry",
          bool(ev) and ev["why"] == "stop file" and ev["registry"] == "nothing set" and m._held_pids() == [], ev)
    check("an object fetched before the holder stopped still reaches B (straight to B)", m.call(held, "Pid") == B3)
    held = None
    ok, d = fails_closed(lambda: m.app(B3))
    check("holder gone: app(B) fails closed again", ok, d)
    C3 = standin(lc3, "--handoff").pid
    h2 = holder(C3, s2)
    check("second holder: _held_pids() == [C]", m._held_pids() == [C3], m._held_pids())
    open(lc3 + ".stop", "w").close()
    ev = exit_event(s2, 30)
    check("holder exits by itself when its process exits; locator gone",
          bool(ev) and ev["why"] == "acad.exe exited" and ev["acad_exited"] and m._held_pids() == [], ev)
    try:
        h2.wait(10)
        check("that holder process is gone", h2.returncode is not None, h2.returncode)
    except subprocess.TimeoutExpired:
        check("that holder process is gone", False, "still running")
finally:
    m.bind(None)
    for lp in (la3, lb3, lc3):
        open(lp + ".stop", "w").close()
    for p in (s1, s2):
        open(p + ".stop", "w").close()
    for p in procs3:
        try:
            p.wait(15)
        except subprocess.TimeoutExpired:
            p.kill()                                         # our own stand-ins and holders, by their Popen handles
left3, held3 = m._rot(), m._held_pids()
m.PROGID = "AutoCAD.Application"
check("part 3 cleanup: nothing left under the test name and no locator in the ROT", left3 == [] and held3 == [], (left3, held3))
print("RESULT: %d of %d checks passed" % (sum(ok for _, ok in RESULTS), len(RESULTS)))
