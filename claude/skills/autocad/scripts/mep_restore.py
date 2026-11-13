"""Put the original solid pipe back for runs MEP could not draw (listed in <work>/mep_skip.json by mep_build.py),
so nothing is missing. Solids are the same ops the AutoCAD build used: cylinders, elbows and reducers on the pipe
layers that lie on the run. Run it with the MEP drawing open in AutoCAD MEP.

Usage: py -3.14 mep_restore.py --src <model folder> [--work <folder>]
Environment defaults: MEP_BUILD_SRC, MEP_BUILD_WORK (same as mep_build.py).
"""
import os, sys, json, time, math, argparse, tempfile

ap = argparse.ArgumentParser(description="Restore solid pipe for runs mep_build.py skipped.")
ap.add_argument("--src", default=os.environ.get("MEP_BUILD_SRC"),
                help="model source folder with geom.py and model.py (env MEP_BUILD_SRC)")
ap.add_argument("--work", default=os.environ.get("MEP_BUILD_WORK") or os.path.join(tempfile.gettempdir(), "mep_build"),
                help="mep_build.py work folder holding mep_skip.json (env MEP_BUILD_WORK)")
A = ap.parse_args()
if not A.src:
    ap.error("--src (or MEP_BUILD_SRC) is required")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(A.src)); sys.path.insert(0, HERE)
from mepcom import *
import geom, model
model.build_all()
skip = json.load(open(os.path.join(os.path.abspath(A.work), "mep_skip.json")))
# pipe layer prefixes of the model; edit to match yours
PIPE = ("M-CHWS-", "M-CHWR-", "M-BYPASS-", "M-CHEM-0", "M-CHEM-1", "M-DRAIN-", "M-MAKEUP-", "M-RELIEF-")

def seg_d(q, a, b):
    ab = [b[i] - a[i] for i in range(3)]; L2 = sum(x * x for x in ab) or 1e-9
    t = max(0.0, min(1.0, sum((q[i] - a[i]) * ab[i] for i in range(3)) / L2))
    return math.dist(q, [a[i] + t * ab[i] for i in range(3)])
def on_run(q, r):
    return any(seg_d(q, r.p[i], r.p[i + 1]) < 0.6 for i in range(len(r.p) - 1))

P = lambda p: "'(%.3f %.3f %.3f)" % tuple(float(x) for x in p)
lines = ['(defun zl (n) (setvar "CLAYER" n))',
         '(defun zc (a b r) (command "_.CYLINDER" "_non" a r "_A" "_non" b))',
         '(defun zk (a b r0 r1) (command "_.CONE" "_non" a r0 "_T" r1 "_A" "_non" b))',
         '(defun ze (p1 d1 o n r / c) (command "_.UCS" "_ZA" "_non" p1 "_non" (mapcar (quote +) p1 d1)) (command "_.CIRCLE" "_non" (list 0.0 0.0 0.0) r) (setq c (entlast)) (command "_.UCS" "_W") (command "_.REVOLVE" c "" "_non" o "_non" (mapcar (quote +) o n) 90))']
n = 0
for lay, kind, a in geom.OPS:
    if not lay.startswith(PIPE) or kind not in ("cyl", "cone", "elb"): continue
    if a[0][1] < -2000: continue                       # gallery and details
    rs = [model.RUNS[k] for k in skip if k in model.RUNS]
    if not any(on_run(a[0], r) and (kind == "elb" or on_run(a[1], r)) for r in rs): continue
    lines.append('(zl "%s")' % lay)
    if kind == "cyl": lines.append("(zc %s %s %.3f)" % (P(a[0]), P(a[1]), a[2]))
    elif kind == "cone": lines.append("(zk %s %s %.3f %.3f)" % (P(a[0]), P(a[1]), a[2], max(a[3], 0.01)))
    else: lines.append("(ze %s %s %s %s %.3f)" % (P(a[0]), P(a[1]), P(a[2]), P(a[3]), a[4]))
    n += 1
print("skipped runs", skip, "| solids to restore", n, flush=True)
if n:
    send('(setvar "CMDECHO" 0) (setvar "TILEMODE" 1) (princ)\n'); wait_idle(30)
    for k in range(0, len(lines), 30):
        send("\n".join(lines[k:k + 30]) + "\n"); time.sleep(0.3); wait_idle(120)
    send('(setvar "CLAYER" "0") (princ)\n'); wait_idle(30)
    send("_.QSAVE\n"); time.sleep(2); wait_idle(300)
print("restored", n, flush=True)
