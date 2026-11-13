"""Wait until AutoCAD MEP answers COM (Documents.Count), up to N seconds."""
import os, sys, time
import pythoncom, win32com.client
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m

limit = float(sys.argv[1]) if len(sys.argv) > 1 else 420
t0 = time.time()
while time.time() - t0 < limit:
    try:
        a = m.app()
        n = m.get(m.get(a, "Documents"), "Count")
        print("COM READY after %.0f s, documents open: %s" % (time.time() - t0, n), flush=True)
        sys.exit(0)
    except Exception as e:
        time.sleep(5)
print("COM NOT READY after %.0f s" % (time.time() - t0))
sys.exit(1)
