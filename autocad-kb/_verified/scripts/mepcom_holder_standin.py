"""Stand-in for the launch() holder, no AutoCAD involved (used by mepcom_pid_test.py, 2026-10-18).

Takes a stand-in's object by its hand-off name (mepcom_standin.py --handoff), the way the real holder gets AutoCAD's
object from CoCreateInstance, then runs mepcom._serve on it: the same locator registration, message loop, stop file and
process-exit handling the real holder runs.
usage: py -3.14 mepcom_holder_standin.py <stand-in pid> <state.jsonl>
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import pythoncom

pid, state = int(sys.argv[1]), sys.argv[2]
o = pythoncom.GetRunningObjectTable().GetObject(pythoncom.CreateItemMoniker("!", "mepcom-handoff.%d" % pid))
m._serve(o.QueryInterface(pythoncom.IID_IDispatch), pid, state, [])
