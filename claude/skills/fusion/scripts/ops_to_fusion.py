"""Turn an op list (the geom.py op format, see dump_ops.py) into a ready-to-run Fusion job that builds it natively.

  python ops_to_fusion.py <ops.json> <out_job.py> [--parametric] [--png <path>] [--view SWISO|SEISO|NEISO|NWISO]
  python fjob.py <out_job.py> 900

ops.json = {"ops": [[layer, kind, args], ...], "colors": {layer: [r, g, b]}}, all in INCHES, Z up.
Kinds (same meaning as the autocad skill's scripts/fusion_step.py): cyl (p0, p1, r), cone (p0, p1, r0, r1), sph (c, r),
box (p0, p1) axis aligned, torus (c, R, r) ring in the XY plane, elb (P1, d1, O, n, r) 90 deg sweep of a circle
at P1 about the axis through O along n, strut/wall (box a0-a1 minus box a2-a3), cstrap (cyl a0-a1 r=a2 minus r=a3
minus box a4-a5).
The job makes one component per layer holding ONE body (all pieces unioned, pairwise so it stays fast), colors each
layer, frames an iso view and saves a PNG. Direct design by default (fastest, no timeline). It writes progress to
JOBS/<job>.progress.txt. It does not save the document: save or close it with a later job.
Verified 2026-10-17 on a chilled water piping model of about 5,000 pieces; see references/hands-on-2026-10-17.md
for the timing.
"""
import os
import sys

TEMPLATE = r'''# runner: force
import adsk.core, adsk.fusion, json, math, os, time
OPS_JSON = %(ops)r
PNG = %(png)r
PARAMETRIC = %(param)r
VIEW = %(view)r
LOG = os.path.join(JOBS, "ops_build.progress.txt")
def log(s):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("%%H:%%M:%%S ") + s + "\n")
open(LOG, "w").close()
T0 = time.time()
IN = 2.54
data = json.load(open(OPS_JSON, encoding="utf-8"))
ops, colors = data["ops"], data.get("colors", {})
tbm = adsk.fusion.TemporaryBRepManager.get()
UNI = adsk.fusion.BooleanTypes.UnionBooleanType
DIF = adsk.fusion.BooleanTypes.DifferenceBooleanType
INT = adsk.fusion.BooleanTypes.IntersectionBooleanType
P = lambda p: adsk.core.Point3D.create(p[0] * IN, p[1] * IN, p[2] * IN)
V = lambda v: adsk.core.Vector3D.create(v[0], v[1], v[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a): return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)
def unit(a):
    n = norm(a); return (a[0] / n, a[1] / n, a[2] / n)
def place(body, origin_in, X, Y, Z):
    m = adsk.core.Matrix3D.create()
    m.setToAlignCoordinateSystems(adsk.core.Point3D.create(0, 0, 0), V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1)),
                                  P(origin_in), V(X), V(Y), V(Z))
    tbm.transform(body, m)
    return body
def box(p0, p1):
    lo = [min(p0[k], p1[k]) for k in range(3)]; hi = [max(p0[k], p1[k]) for k in range(3)]
    c = [(lo[k] + hi[k]) / 2 for k in range(3)]
    return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P(c), V((1, 0, 0)), V((0, 1, 0)),
                         (hi[0] - lo[0]) * IN, (hi[1] - lo[1]) * IN, (hi[2] - lo[2]) * IN))
def cyl(p0, p1, r0, r1):
    return tbm.createCylinderOrCone(P(p0), r0 * IN, P(p1), max(r1, 0.01) * IN)
def ring(c, R, r):
    # createTorus ignores its center in 2705.1.30: build at the origin and move it
    t = tbm.createTorus(adsk.core.Point3D.create(0, 0, 0), V((0, 0, 1)), R * IN, r * IN)
    return place(t, c, (1, 0, 0), (0, 1, 0), (0, 0, 1))
def elb(P1, d1, O, n, r):
    u = sub(P1, O); R = norm(u); u = unit(u); n = unit(n); v = cross(n, u)
    t = tbm.createTorus(adsk.core.Point3D.create(0, 0, 0), V((0, 0, 1)), R * IN, r * IN)
    s = (R + r) * 1.02
    q = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(adsk.core.Point3D.create(s / 2 * IN, s / 2 * IN, 0),
                      V((1, 0, 0)), V((0, 1, 0)), s * IN, s * IN, (2 * r + 0.2) * IN))
    tbm.booleanOperation(t, q, INT)
    return place(t, O, u, v, n)
def solid(kind, a):
    if kind == "cyl": return cyl(a[0], a[1], a[2], a[2])
    if kind == "cone": return cyl(a[0], a[1], a[2], a[3])
    if kind == "sph": return tbm.createSphere(P(a[0]), a[1] * IN)
    if kind == "box": return box(a[0], a[1])
    if kind == "torus": return ring(a[0], a[1], a[2])
    if kind == "elb": return elb(*a)
    if kind in ("strut", "wall"):
        b = box(a[0], a[1]); tbm.booleanOperation(b, box(a[2], a[3]), DIF); return b
    if kind == "cstrap":
        o = cyl(a[0], a[1], a[2], a[2]); tbm.booleanOperation(o, cyl(a[0], a[1], a[3], a[3]), DIF)
        tbm.booleanOperation(o, box(a[4], a[5]), DIF); return o
    raise ValueError(kind)
def merge(bodies):
    """pairwise union keeps each boolean small; pieces that fail to union stay separate bodies"""
    extra = []
    while len(bodies) > 1:
        nxt = []
        for i in range(0, len(bodies), 2):
            a = bodies[i]
            if i + 1 < len(bodies):
                if not tbm.booleanOperation(a, bodies[i + 1], UNI):
                    extra.append(bodies[i + 1])
            nxt.append(a)
        bodies = nxt
    return bodies + extra, len(extra)

by, bad, empty = {}, 0, 0
t = time.time()
for lay, kind, a in ops:
    try:
        b = solid(kind, a)
        if b is None or b.faces.count == 0:
            empty += 1; continue
        by.setdefault(lay, []).append(b)
    except Exception as e:
        bad += 1
log("temp pieces %%d in %%d layers, failed %%d, empty %%d, %%.1f s" %% (sum(len(v) for v in by.values()), len(by), bad, empty, time.time() - t))
t = time.time()
merged, fails = {}, 0
for lay, bl in by.items():
    m, f = merge(bl); merged[lay] = m; fails += f
log("unions done %%.1f s, union failures kept as extra bodies: %%d" %% (time.time() - t, fails))

doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
des = adsk.fusion.Design.cast(app.activeProduct)
if not PARAMETRIC:
    des.designType = adsk.fusion.DesignTypes.DirectDesignType
root = des.rootComponent
lib = app.materialLibraries.itemByName("Fusion Appearance Library")
base = lib.appearances.itemByName("Paint - Enamel Glossy (Grey)") if lib else None
t = time.time()
nb = 0
for lay in sorted(merged):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component; comp.name = lay
    bf = None
    if PARAMETRIC:
        bf = comp.features.baseFeatures.add(); bf.startEdit()
    for b in merged[lay]:
        (comp.bRepBodies.add(b, bf) if bf else comp.bRepBodies.add(b)); nb += 1
    if bf:
        bf.finishEdit()
    rgb = colors.get(lay)
    if base and rgb:
        try:
            ap = des.appearances.itemByName("L " + lay)
        except Exception:
            ap = None
        if not ap:
            ap = des.appearances.addByCopy(base, "L " + lay)
            for i in range(ap.appearanceProperties.count):
                pr = ap.appearanceProperties.item(i)
                if pr.objectType.endswith("ColorProperty"):
                    adsk.core.ColorProperty.cast(pr).value = adsk.core.Color.create(int(rgb[0]), int(rgb[1]), int(rgb[2]), 255)
                    break
        occ.appearance = ap
log("design: %%d components, %%d bodies, add + color %%.1f s" %% (len(merged), nb, time.time() - t))

vp = app.activeViewport
bb = root.boundingBox
c = [(bb.minPoint.asArray()[k] + bb.maxPoint.asArray()[k]) / 2 for k in range(3)]
size = max(bb.maxPoint.asArray()[k] - bb.minPoint.asArray()[k] for k in range(3))
dirs = {"SWISO": (-1, -1, 1), "SEISO": (1, -1, 1), "NEISO": (1, 1, 1), "NWISO": (-1, 1, 1)}
d = unit(dirs.get(VIEW, (-1, -1, 1)))
cam = vp.camera
cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
cam.target = adsk.core.Point3D.create(*c)
cam.eye = adsk.core.Point3D.create(c[0] + d[0] * size, c[1] + d[1] * size, c[2] + d[2] * size)
cam.upVector = V((0, 0, 1))
cam.isSmoothTransition = False
cam.isFitView = True
vp.camera = cam
if PNG:
    o = adsk.core.SaveImageFileOptions.create(PNG); o.width, o.height = 2400, 1500; o.isAntiAliased = True
    vp.saveAsImageFileWithOptions(o)
log("view and PNG done; total %%.1f s" %% (time.time() - T0))
RESULT = open(LOG, encoding="utf-8").read()
'''


def main(a):
    if len(a) < 2:
        sys.exit(__doc__)
    ops, out = os.path.abspath(a[0]), os.path.abspath(a[1])
    png = a[a.index("--png") + 1] if "--png" in a else ""
    view = a[a.index("--view") + 1] if "--view" in a else "SWISO"
    s = TEMPLATE % {"ops": ops, "png": os.path.abspath(png) if png else "", "param": "--parametric" in a, "view": view}
    open(out, "w", encoding="utf-8").write(s)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])
