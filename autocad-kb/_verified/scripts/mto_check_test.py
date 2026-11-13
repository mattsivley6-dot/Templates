"""Prove mep_takeoff.py on the known-length test drawing made by mto_make_test_dwg.py.

Runs the takeoff twice on <work_dir>/mto_test.dwg (decimal units, then --keep-units = the drawing's own
architectural text) and checks it three independent ways:
  1. against what was DRAWN (design.json): pipes plus fittings must fill each drawn run end to end, no gap, no overlap;
  2. against MEP's own COM read-back taken in the GUI session (com_readback.json), handle by handle;
  3. summary tables against the drawn runs and the expected fitting list.
usage: py -3.14 mto_check_test.py <work_dir>
"""
import csv, json, math, os, re, subprocess, sys, time
from collections import Counter, defaultdict

W = os.path.abspath(sys.argv[1])
# mep_takeoff.py from the autocad skill: set AUTOCAD_SKILL_SCRIPTS, or keep this repo's layout
TAKEOFF = os.path.join(os.environ.get("AUTOCAD_SKILL_SCRIPTS") or os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "claude", "skills", "autocad", "scripts")), "mep_takeoff.py")
DWG = os.path.join(W, "mto_test.dwg")
design = json.load(open(os.path.join(W, "design.json")))
com = json.load(open(os.path.join(W, "com_readback.json")))
TOL = 1e-3            # inches
REPORT = {}
fails = []


def say(*a):
    print(" ".join(str(x) for x in a), flush=True)


def check(cond, msg):
    if not cond:
        fails.append(msg)
        say("  FAIL", msg)
    return cond


def run_takeoff(tag, extra):
    out = os.path.join(W, "takeoff_" + tag)
    t0 = time.time()
    p = subprocess.run([sys.executable, TAKEOFF, DWG, "--out", out, "--name", "mto_test"] + extra,
                       capture_output=True, text=True, encoding="utf-8")
    secs = time.time() - t0
    rows = list(csv.DictReader(open(os.path.join(out, "mto_test_objects.csv"), encoding="utf-8-sig")))
    summ = list(csv.DictReader(open(os.path.join(out, "mto_test_summary.csv"), encoding="utf-8-sig")))
    return p.returncode, p.stdout, rows, summ, secs, out


def f(x):
    return float(x) if x not in ("", None) else None


def pt(r, tag):
    return tuple(f(r["%s_%s" % (tag, k)]) for k in "xyz")


def cpts(r):
    return [tuple(float(v) for v in c.strip().strip("()").split(",")) for c in r["connection_points"].split(";") if c.strip()]


def proj(P, q):
    """(arc length along polyline P, distance) of point q."""
    best, s0 = (None, 1e18), 0.0
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        ab = [b[k] - a[k] for k in range(3)]
        L = math.sqrt(sum(c * c for c in ab))
        t = max(0.0, min(1.0, sum((q[k] - a[k]) * ab[k] for k in range(3)) / (L * L)))
        c = [a[k] + t * ab[k] for k in range(3)]
        d = math.dist(c, q)
        if d < best[1]:
            best = (s0 + t * L, d)
        s0 += L
    return best


# ------------------------------------------------------------------ 1. decimal run
rc, text, rows, summ, secs, outdir = run_takeoff("dec", [])
say(text)
REPORT["takeoff_exit"], REPORT["takeoff_secs"] = rc, round(secs, 1)
check(rc == 0, "takeoff exit code %s" % rc)
check("counts match" in text, "takeoff summary did not say counts match")

# ------------------------------------------------------------------ 2. handle by handle against the COM read-back
say("== COM read-back vs headless LIST, handle by handle")
TYPE = {"AecbDbPipe": "AECB_PIPE", "AecbDbPipeFitting": "AECB_PIPEFITTING"}
by_h = {r["handle"].upper(): r for r in rows}
com_h = {c["handle"].upper(): c for c in com}
check(set(by_h) == set(com_h), "handle sets differ: only LIST %s, only COM %s" % (sorted(set(by_h) - set(com_h)), sorted(set(com_h) - set(by_h))))
worst = defaultdict(float)
for h, c in com_h.items():
    r = by_h.get(h)
    if not r:
        continue
    check(r["type"] == TYPE.get(c["object"], c["object"]), "%s type %s vs %s" % (h, r["type"], c["object"]))
    check(r["layer"] == c["layer"], "%s layer %s vs %s" % (h, r["layer"], c["layer"]))
    check(r["style_reference"] == c["SizeName"], "%s style %r vs SizeName %r" % (h, r["style_reference"], c["SizeName"]))
    check(r["system"] == re.sub(r"\s*\(.*\)$", "", c["SystemName"]), "%s system %r vs %r" % (h, r["system"], c["SystemName"]))
    if c["object"] == "AecbDbPipe":
        for k_r, k_c in (("length_ft", "Length"), ("cut_length_ft", "CutLength")):
            dv = abs(f(r[k_r]) * 12.0 - float(c[k_c]))
            worst[k_c] = max(worst[k_c], dv)
            check(dv < 1e-4, "%s %s %s ft vs COM %s in" % (h, k_r, r[k_r], c[k_c]))
        for tag, k_c in (("start", "StartPoint"), ("end", "EndPoint")):
            dv = math.dist(pt(r, tag), c[k_c])
            worst[k_c] = max(worst[k_c], dv)
            check(dv < 1e-4, "%s %s point %s vs %s" % (h, tag, pt(r, tag), c[k_c]))
        ins_r = f(r["insulation_in"]) or 0.0
        check(abs(ins_r - float(c["InsulationThickness"])) < 1e-6, "%s insulation %s vs %s" % (h, ins_r, c["InsulationThickness"]))
        check(abs(f(r["nominal_in"]) - float(c["NominalSize"])) < 1e-6, "%s nominal %s vs %s" % (h, r["nominal_in"], c["NominalSize"]))
    else:
        a, b = sorted(cpts(r)), sorted(tuple(v) for v in c["connectors"])
        check(len(a) == len(b) and all(math.dist(x, y) < 1e-4 for x, y in zip(a, b)),
              "%s connection points %s vs COM connectors %s" % (h, a, b))
REPORT["max_abs_diff_vs_com_in"] = {k: round(v, 9) for k, v in worst.items()}
say("  objects: LIST %d, COM %d; worst differences (in):" % (len(rows), len(com)), REPORT["max_abs_diff_vs_com_in"])

# ------------------------------------------------------------------ 3. pipes plus fittings fill each drawn run
say("== drawn runs vs takeoff (pipes plus fittings must fill each run)")
pipes = [r for r in rows if r["type"] == "AECB_PIPE"]
fits = [r for r in rows if r["type"] == "AECB_PIPEFITTING"]
used = Counter()
runs_out = []
for d in design:
    P = [tuple(map(float, p)) for p in d["pts"]]
    L = d["drawn_in"]
    iv = []
    for r in pipes:
        (s1, d1), (s2, d2) = proj(P, pt(r, "start")), proj(P, pt(r, "end"))
        if d1 < TOL and d2 < TOL:
            iv.append((min(s1, s2), max(s1, s2), "pipe", r["handle"]))
            used[r["handle"]] += 1
    for r in fits:
        on = [proj(P, q) for q in cpts(r)]
        ss = sorted(s for s, dd in on if dd < TOL)
        if len(ss) >= 2:
            iv.append((ss[0], ss[-1], "fitting", r["handle"]))
            used[r["handle"]] += 1
        elif len(ss) == 1 and d.get("starts_on"):
            # branch outlet of the tee at this run's start: the tee centre must be the run's start point
            others = [q for q in cpts(r) if proj(P, q)[1] >= TOL]
            centre = tuple(sum(q[k] for q in others) / len(others) for k in range(3)) if len(others) == 2 else None
            check(centre is not None and math.dist(centre, P[0]) < TOL, "%s tee centre %s is not the branch start %s" % (r["handle"], centre, P[0]))
            iv.append((0.0, ss[0], "fitting", r["handle"]))
            used[r["handle"]] += 1
    iv.sort()
    gaps, overlaps, cur = [], [], 0.0
    for a, b, kind, h in iv:
        if a > cur + TOL:
            gaps.append((round(cur, 4), round(a, 4)))
        if a < cur - TOL:
            overlaps.append((round(a, 4), round(cur, 4), h))
        cur = max(cur, b)
    if cur < L - TOL:
        gaps.append((round(cur, 4), round(L, 4)))
    pipe_in = sum(b - a for a, b, k, _ in iv if k == "pipe")
    fit_in = sum(b - a for a, b, k, _ in iv if k == "fitting")
    row = {"run": d["id"], "system": d["system"], "size": d["size"], "drawn_ft": L / 12.0, "pipe_ft": pipe_in / 12.0,
           "fitting_ft": fit_in / 12.0, "sum_minus_drawn_in": pipe_in + fit_in - L, "pieces": sum(1 for x in iv if x[2] == "pipe"),
           "fittings": sum(1 for x in iv if x[2] == "fitting"), "gaps": gaps, "overlaps": overlaps}
    runs_out.append(row)
    check(not gaps and not overlaps and abs(row["sum_minus_drawn_in"]) < TOL,
          "%s: gaps %s overlaps %s, pipe+fittings-drawn = %.6f in" % (d["id"], gaps, overlaps, row["sum_minus_drawn_in"]))
    say("  %s %-8s %-6s drawn %8.4f ft = pipe %8.4f + fittings %6.4f ft (pieces %d, fittings %d) | diff %.6f in | gaps %s overlaps %s"
        % (d["id"], d["system"], d["size"], row["drawn_ft"], row["pipe_ft"], row["fitting_ft"], row["pieces"], row["fittings"],
           row["sum_minus_drawn_in"], gaps, overlaps))
check(all(used[r["handle"]] == 1 for r in pipes), "pipes not on exactly one run: %s" % [r["handle"] for r in pipes if used[r["handle"]] != 1])
check(all(used[r["handle"]] >= 1 for r in fits), "fittings on no run: %s" % [r["handle"] for r in fits if not used[r["handle"]]])
REPORT["runs"] = runs_out

# ------------------------------------------------------------------ 4. summary tables vs drawn runs and the expected fittings
say("== summary tables")
# expected length per system and size: the pipes that fill the drawn runs (section 3), bucketed by MEP's own
# COM NominalSize and SystemName for each handle (MEP puts a short 4 in stub between the tee and the 4x2 reducer)
FMT = {4.0: '4"', 2.0: '2"', 1.5: '1-1/2"', 0.75: '3/4"'}
exp_len = defaultdict(float)
for r in pipes:
    c = com_h[r["handle"].upper()]
    k = (re.sub(r"\s*\(.*\)$", "", c["SystemName"]), FMT[float(c["NominalSize"])])
    exp_len[k] += float(c["Length"]) / 12.0
got_len = {(s["system"], s["size"]): float(s["length_ft"]) for s in summ if s["section"] == "length"}
for k in sorted(set(exp_len) | set(got_len)):
    check(k in got_len and k in exp_len and abs(got_len[k] - exp_len[k]) < 1e-4, "length %s: summary %s vs COM %s" % (k, got_len.get(k), exp_len.get(k)))
    say("  %-9s %-7s summary %9.4f ft | COM lengths of the same pipes %9.4f ft" % (k[0], k[1], got_len.get(k, float("nan")), exp_len.get(k, float("nan"))))
check(abs(sum(got_len.values()) + sum(r["fitting_ft"] for r in runs_out) - sum(r["drawn_ft"] for r in runs_out)) < 1e-4,
      "all pipe in the summary plus fitting lengths does not equal all drawn length")
say("  all pipe %.4f ft + fittings %.4f ft = %.4f ft; drawn %.4f ft" % (
    sum(got_len.values()), sum(r["fitting_ft"] for r in runs_out), sum(got_len.values()) + sum(r["fitting_ft"] for r in runs_out),
    sum(r["drawn_ft"] for r in runs_out)))
got_fit = {(s["kind"], s["size"]): int(s["count"]) for s in summ if s["section"] == "fitting_by_type"}
exp_fit = {("Elbow 90", '4"'): 1, ("Elbow 90", '2"'): 1, ("Tee", '4"'): 1, ("Reducer, concentric", '4" x 2"'): 1}
say("  fittings by type and size:", got_fit)
check(got_fit == exp_fit, "fitting counts %s, expected %s" % (got_fit, exp_fit))
r4 = [r for r in pipes if r["layer"] == "M-HOLD"]
check(len(r4) == 1 and abs(f(r4[0]["slope_pct"]) + 1.0) < 1e-6 and r4[0]["orientation"] == "sloped",
      "sloped pipe on the frozen layer: %s" % [(r["handle"], r["slope_pct"], r["orientation"]) for r in r4])
if r4:
    say("  frozen-layer pipe %s: slope %s %% (%s in/ft, %s deg; LIST field %r), length %s ft" % (
        r4[0]["handle"], r4[0]["slope_pct"], r4[0]["slope_in_per_ft"], r4[0]["slope_deg"], r4[0]["slope_list"], r4[0]["length_ft"]))
ins = {(s["system"], s["size"], s["insulation"]): float(s["length_ft"]) for s in summ if s["section"] == "insulated"}
say("  insulated:", ins)
check(list(ins) == [("CHWR", '2"', '1-1/2"')], "insulated rows %s" % ins)
REPORT["summary_lengths"] = {"%s %s" % k: v for k, v in got_len.items()}
REPORT["fittings"] = {"%s %s" % k: v for k, v in got_fit.items()}

# ------------------------------------------------------------------ 5. the drawing's own architectural text parses to the same numbers
say("== --keep-units (architectural text from the drawing) vs decimal")
rc2, text2, rows2, summ2, secs2, out2 = run_takeoff("arch", ["--keep-units"])
check(rc2 == 0, "keep-units exit %s" % rc2)
b2 = {r["handle"]: r for r in rows2}
wl = 0.0
for r in pipes:
    wl = max(wl, abs(f(b2[r["handle"]]["length_ft"]) - f(r["length_ft"])) * 12.0)
say("  worst pipe length difference: %.5f in (architectural text is rounded to the drawing's LUPREC)" % wl)
check(wl <= 1 / 64.0 + 1e-9, "architectural parse differs by %.5f in" % wl)
REPORT["keep_units_worst_in"] = round(wl, 6)
REPORT["keep_units_secs"] = round(secs2, 1)

REPORT["fails"] = fails
json.dump(REPORT, open(os.path.join(W, "check_report.json"), "w"), indent=1, default=str)
say("\nRESULT:", "ALL CHECKS PASSED" if not fails else "%d FAILED" % len(fails))
sys.exit(1 if fails else 0)
