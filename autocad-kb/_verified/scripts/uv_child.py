"""Child for test_uservars.py. mode "exit": save, change, sys.exit(3) with no restore() (the exit hook
must put the values back). mode "gone": same, but every COM call fails first, as if MEP had died
(the exit hook must fall back to writing FILEDIA into the registry)."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
# the autocad skill's scripts folder (mepcom, uservars, mep_takeoff): set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
SKILL_SCRIPTS = os.environ.setdefault("AUTOCAD_SKILL_SCRIPTS", os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "claude", "skills", "autocad", "scripts")))
sys.path.insert(0, SKILL_SCRIPTS)
import mepcom as m
import uservars
m.bind(int(sys.argv[2]))         # only the test MEP

mode = sys.argv[1]
print("saved", uservars.save(), flush=True)
m.send('(setvar "FILEDIA" 0) (setvar "CMDDIA" 0) (setvar "LOGFILEMODE" 1) (princ)\n')
m.wait_idle(30)
print("changed", {n: int(m.var(n)) for n in uservars.NAMES}, flush=True)
if mode == "gone":
    def dead(*a, **k):
        raise RuntimeError("MEP gone (simulated)")
    uservars.send = dead
sys.exit(3)
