"""Colored STEP of a 3D piping model for Fusion, from the same op list as the AutoCAD build.
Hangers, insulation, typical details and the parts gallery are left out (hangers are hidden on the sheets).
Model is in inches; scaled x25.4 because CadQuery writes mm STEP. One assembly part per layer, colored like the CAD layers.

Usage: py -3.14 fusion_step.py --src <model folder> [--out <folder>] [--name model]
  --src  folder holding geom.py, model.py and emit.py (its LAYERS dict gives the colors); env MEP_BUILD_SRC
  --out  output folder (default <temp>/fusion_step); env FUSION_STEP_OUT
  --name assembly name and STEP file stem (default "model")
"""
import os, sys, ast, time, math, argparse, tempfile

ap = argparse.ArgumentParser(description="Write a colored STEP assembly from a piping op list.")
ap.add_argument("--src", default=os.environ.get("MEP_BUILD_SRC"), help="model source folder (env MEP_BUILD_SRC)")
ap.add_argument("--out", default=os.environ.get("FUSION_STEP_OUT") or os.path.join(tempfile.gettempdir(), "fusion_step"),
                help="output folder (env FUSION_STEP_OUT)")
ap.add_argument("--name", default="model", help="assembly name and STEP file stem")
A = ap.parse_args()
if not A.src:
    ap.error("--src (or MEP_BUILD_SRC) is required")
SRC = os.path.abspath(A.src)
OUT = os.path.abspath(A.out)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SRC)
import cadquery as cq
import geom, model

t0 = time.time()
model.build_all()
ops = list(geom.OPS)

# layer colors straight from emit.py's LAYERS dict (parsed, so emit.py's build code does not run)
src = open(os.path.join(SRC, "emit.py"), encoding="utf-8").read()
i = src.index("LAYERS = {"); j = src.index("\n}", i) + 2
LAYERS = ast.literal_eval(src[i + len("LAYERS = "):j])

SKIP = ("M-HGR-", "M-INSUL", "D-", "A-FLOORPLAN")
ymin = -2000.0   # inches: the parts gallery and typical details sit far below the building
S = 25.4
V = lambda p: cq.Vector(p[0] * S, p[1] * S, p[2] * S)
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def norm(a): return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)

def solid(kind, a):
    if kind == "cyl":
        d = sub(a[1], a[0]); L = norm(d)
        return cq.Solid.makeCylinder(a[2] * S, L * S, V(a[0]), cq.Vector(*d))
    if kind == "cone":
        d = sub(a[1], a[0]); L = norm(d)
        return cq.Solid.makeCone(a[2] * S, max(a[3], 0.01) * S, L * S, V(a[0]), cq.Vector(*d))
    if kind == "sph":
        return cq.Solid.makeSphere(a[1] * S, V(a[0]), angleDegrees1=-90, angleDegrees2=90)
    if kind == "box":
        p0 = [min(a[0][k], a[1][k]) for k in range(3)]; p1 = [max(a[0][k], a[1][k]) for k in range(3)]
        return cq.Solid.makeBox((p1[0] - p0[0]) * S, (p1[1] - p0[1]) * S, (p1[2] - p0[2]) * S, V(p0))
    if kind == "torus":
        return cq.Solid.makeTorus(a[1] * S, a[2] * S, V(a[0]), cq.Vector(0, 0, 1))
    if kind == "elb":
        P1, d1, O, n, r = a
        w = cq.Wire.makeCircle(r * S, V(P1), cq.Vector(*d1))
        return cq.Solid.revolve(cq.Face.makeFromWires(w), 90, V(O), V((O[0] + n[0], O[1] + n[1], O[2] + n[2])))
    if kind in ("strut", "wall"):
        b = solid("box", (a[0], a[1])); c = solid("box", (a[2], a[3]))
        return b.cut(c)
    if kind == "cstrap":
        o = solid("cyl", (a[0], a[1], a[2])); i_ = solid("cyl", (a[0], a[1], a[3])); q = solid("box", (a[4], a[5]))
        return o.cut(i_).cut(q)
    raise ValueError(kind)

by = {}
bad = 0
for lay, kind, a in ops:
    if lay.startswith(SKIP): continue
    pts = [x for x in a if isinstance(x, tuple) and len(x) == 3]
    if pts and min(p[1] for p in pts) < ymin: continue          # gallery and typical details
    try:
        by.setdefault(lay, []).append(solid(kind, a))
    except Exception as e:
        bad += 1
print("solids by layer", sum(len(v) for v in by.values()), "layers", len(by), "failed", bad, round(time.time() - t0, 1), "s", flush=True)

assy = cq.Assembly(name=A.name)
for lay, sols in sorted(by.items()):
    rgb = LAYERS.get(lay, (160, 160, 165))
    # one clean solid per layer: a compound of overlapping solids (pipe through its fittings) shows holes in Fusion
    try:
        comp = sols[0].fuse(*sols[1:]).clean() if len(sols) > 1 else sols[0]
        if not comp.isValid(): raise ValueError("invalid fuse")
    except Exception as e:
        print("fuse failed on", lay, e, flush=True); comp = cq.Compound.makeCompound(sols)
    assy.add(comp, name=lay.replace("-", "_"), color=cq.Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255))
step = os.path.join(OUT, A.name + ".step")
assy.save(step) if hasattr(assy, "save") else assy.export(step)
print("STEP", step, os.path.getsize(step), round(time.time() - t0, 1), "s", flush=True)
