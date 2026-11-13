"""Dump the op list of a Python piping model (geom.py + model.py + emit.py) to ops.json for ops_to_fusion.py.

  python dump_ops.py <model_root> <out ops.json> [--skip PREFIX,PREFIX,...] [--min-y <inches>]

Expected model layout (your own model code, not shipped here):
  <model_root>/3d/geom.py   collects every solid in a list OPS of (layer, kind, args) tuples, inches, Z up
  <model_root>/3d/model.py  has build_all(), which fills geom.OPS (it may read json files from 3d/)
  <model_root>/3d/emit.py   has a literal dict LAYERS = {layer: (r, g, b), ...}
Kinds are the ones ops_to_fusion.py builds (cyl, cone, sph, box, torus, elb, strut, wall, cstrap).

Filters: layers whose name starts with a --skip prefix are dropped (default: hangers, insulation, typical
details and the floor plan: M-HGR-, M-INSUL, D-, A-FLOORPLAN), and pieces with any point at Y below --min-y
(default -2000 in, where a parts gallery or detail area may sit off to the side) are dropped. Adjust both to
your own layer standard. Run on a COPY of the model folder if anyone else may be editing it.
"""
import ast
import collections
import json
import os
import sys
import time

DEFAULT_SKIP = ("M-HGR-", "M-INSUL", "D-", "A-FLOORPLAN")
DEFAULT_MIN_Y = -2000.0


def main(root, out, skip=DEFAULT_SKIP, min_y=DEFAULT_MIN_Y):
    src = os.path.join(root, "3d")
    sys.path.insert(0, src)
    os.chdir(src)
    t0 = time.time()
    import geom
    import model
    model.build_all()
    ops = list(geom.OPS)
    text = open(os.path.join(src, "emit.py"), encoding="utf-8").read()
    i = text.index("LAYERS = {")
    j = text.index("\n}", i) + 2
    layers_rgb = ast.literal_eval(text[i + len("LAYERS = "):j])
    keep = []
    for lay, kind, a in ops:
        if skip and lay.startswith(tuple(skip)):
            continue
        pts = [x for x in a if isinstance(x, tuple) and len(x) == 3]
        if pts and min(p[1] for p in pts) < min_y:
            continue
        keep.append([lay, kind, [list(x) if isinstance(x, tuple) else x for x in a]])
    kinds = collections.Counter(k for _, k, _ in keep)
    lays = collections.Counter(l for l, _, _ in keep)
    colors = {l: layers_rgb.get(l, (160, 160, 165)) for l in lays}
    json.dump({"ops": keep, "colors": colors}, open(out, "w"))
    print("all ops", len(ops), "kept", len(keep), "layers", len(lays), "kinds", dict(kinds), "%.1f s" % (time.time() - t0))


if __name__ == "__main__":
    args = sys.argv[1:]
    skip = DEFAULT_SKIP
    min_y = DEFAULT_MIN_Y
    if "--skip" in args:
        k = args.index("--skip")
        skip = tuple(s for s in args[k + 1].split(",") if s)
        del args[k:k + 2]
    if "--min-y" in args:
        k = args.index("--min-y")
        min_y = float(args[k + 1])
        del args[k:k + 2]
    if len(args) < 2:
        sys.exit(__doc__)
    main(os.path.abspath(args[0]), os.path.abspath(args[1]), skip, min_y)
