"""Factory probe (2026-10-18): does CoCreateInstance connect to an acad.exe that WE started with /Automation -Embedding
(class factory registered), instead of starting another? If it hands back <pid>, serve it like launch()'s holder
(mepcom._serve: ROT locator !mepcom.acad.<pid>) so app(pid) reaches it; if it started another acad.exe, quit that one.
usage: py -3.14 mepcom_factory_probe.py <pid of the acad.exe we started> <state.jsonl>
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import pythoncom, win32process

want, state = int(sys.argv[1]), sys.argv[2]
before = m._acad_pids()
t = time.time()
a = pythoncom.CoCreateInstance(m.CLSID, None, pythoncom.CLSCTX_LOCAL_SERVER, pythoncom.IID_IDispatch)
secs = round(time.time() - t, 1)
tid = pid = 0
while not tid and time.time() - t < 300:
    try:
        tid, pid = win32process.GetWindowThreadProcessId(m.get(a, "HWND"))
    except pythoncom.com_error:
        pass
    if not tid:
        time.sleep(0.5)
res = {"cocreate_s": secs, "pid": pid, "wanted": want, "new_pids": sorted(m._acad_pids() - before)}
m._event(state, event="probe", **res)
print(json.dumps(res), flush=True)
if pid == want:
    m._serve(a, pid, state, [])                         # keeps the locator until that acad.exe exits or a stop file
else:
    try:
        m.call(a, "Quit")                               # COM started another acad.exe: ours, end it
    except Exception:
        pass
