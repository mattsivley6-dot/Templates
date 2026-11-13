"""Headless takeoff from AutoCAD MEP drawings: no MEP window, no COM, nothing on the user's screen.

For each DWG: copy it to a scratch folder, run the AutoCAD 2027 Core Console on the copy with a script that
selects every MEP object in model space with (ssget "X") (so pipes on frozen or locked layers count too; _ALL
skips frozen layers) and runs _.LIST on it with decimal units, parse the UTF-16-LE log into one record per
object, and write:
  <name>_objects.csv   one row per object: type, handle, layer, system, routing preference, style (size and
                       part), length, cut length, start and end point, slope, insulation, connection points
  <name>_summary.csv   pipe (and any other linear object) length by system and nominal size, fitting counts
                       by type and size, by part and size, insulated pipe, other MEP objects
  <name>_summary.txt   the same tables, readable (also printed)

usage:
  py -3.14 mep_takeoff.py <drawing.dwg> [more.dwg ...] [--out DIR] [--name NAME] [--timeout SEC]
                          [--units in|ft|mm|cm|m] [--keep-units] [--keep-copy] [--filter "AECB_*"]
  py -3.14 mep_takeoff.py --log <saved_list.log> [--out DIR]     re-parse a saved console log, no AutoCAD

Limits: objects inside xrefs or blocks are not listed (the summary names any xrefs; run their files too).
Exit codes: 0 ok, 1 bad arguments, 2 a console run failed, 3 outputs written but a cross-check failed.
AutoCAD location: set the ACCORECONSOLE environment variable (or --acc) if accoreconsole.exe is not in the
default AutoCAD 2027 folder.
Test write-up: autocad-kb/_verified/2026-10-18-mep-takeoff-test.md in this repo.
"""
import argparse, csv, datetime, json, math, os, re, shutil, subprocess, sys, tempfile, time
from collections import Counter, defaultdict
from fractions import Fraction

ACC = os.environ.get("ACCORECONSOLE") or r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"
CREATE_NO_WINDOW = 0x08000000

# INSUNITS code -> feet per drawing unit (AutoCAD INSUNITS table)
_SURVEY_FT = 1200.0 / 3937.0 / 0.3048
FT_PER_UNIT = {1: 1 / 12.0, 2: 1.0, 4: 1 / 304.8, 5: 1 / 30.48, 6: 1 / 0.3048, 10: 3.0, 14: 1 / 3.048,
               21: _SURVEY_FT, 22: _SURVEY_FT / 12.0}
UNIT_NAME = {1: "inches", 2: "feet", 4: "millimeters", 5: "centimeters", 6: "meters", 10: "yards",
             14: "decimeters", 21: "US survey feet", 22: "US survey inches"}
UNIT_ARG = {"in": 1, "ft": 2, "mm": 4, "cm": 5, "m": 6}

FILTER_OK = re.compile(r"^[A-Za-z0-9_*?,#@.~-]+$")


# ------------------------------------------------------------------ console run
def lisp_print(tag, expr):
    """One-line LISP form that prints 'MTO-<tag> <value>' on its own line and returns quietly."""
    return '(progn (princ (strcat (chr 10) "MTO-%s " %s (chr 10))) (princ))' % (tag, expr)


def build_script(flt, keep_units):
    vars_ = ('(strcat "INSUNITS=" (itoa (getvar "INSUNITS")) " LUNITS=" (itoa (getvar "LUNITS")) " LUPREC=" '
             '(itoa (getvar "LUPREC")) " AUNITS=" (itoa (getvar "AUNITS")) " AUPREC=" (itoa (getvar "AUPREC")) '
             '" TILEMODE=" (itoa (getvar "TILEMODE")))')
    lines = ['(setvar "CMDECHO" 1)', lisp_print("VARS", vars_), '(setvar "TILEMODE" 1)']
    if not keep_units:
        lines += ['(setvar "LUNITS" 2)', '(setvar "LUPREC" 8)', '(setvar "AUNITS" 0)', '(setvar "AUPREC" 4)']
    lines += [
        '(setq mto_ss (ssget "X" (list (cons 0 "%s") (cons 410 "Model"))))' % flt,
        '(if (not mto_ss) (setq mto_ss (ssadd)))',
        # independent count by type straight from the database, to check the LIST output against
        '(progn (setq mto_t nil mto_i 0) (repeat (sslength mto_ss) (setq mto_n (cdr (assoc 0 (entget (ssname mto_ss mto_i)))) '
        'mto_a (assoc mto_n mto_t) mto_t (if mto_a (subst (cons mto_n (1+ (cdr mto_a))) mto_a mto_t) (cons (cons mto_n 1) mto_t)) '
        'mto_i (1+ mto_i))) (princ (strcat (chr 10) "MTO-COUNT " (itoa (sslength mto_ss)) (chr 10) "MTO-TYPES " '
        '(vl-prin1-to-string mto_t) (chr 10))) (princ))',
        # xref names: their objects are not in this drawing's takeoff
        '(progn (setq mto_x "" mto_b (tblnext "BLOCK" T)) (while mto_b (if (= 4 (logand 4 (cdr (assoc 70 mto_b)))) '
        '(setq mto_x (strcat mto_x "|" (cdr (assoc 2 mto_b))))) (setq mto_b (tblnext "BLOCK"))) '
        '(princ (strcat (chr 10) "MTO-XREFS " mto_x (chr 10))) (princ))',
        "_.LIST", "!mto_ss", "",
        lisp_print("END", '"done"'),
        "_.QUIT", "_Y",
    ]
    return "\r\n".join(lines) + "\r\n\r\n"


def safe_name(s, n=60):
    return (re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_.") or "drawing")[:n]


def run_console(dwg, work, flt, keep_units, timeout, keep_copy):
    os.makedirs(work, exist_ok=True)
    stem = safe_name(os.path.splitext(os.path.basename(dwg))[0])
    copy = os.path.join(work, stem + ".dwg")
    scr = os.path.join(work, stem + "_list.scr")
    log = os.path.join(work, stem + "_list.log")
    for p in (copy, scr, log):
        if os.path.exists(p):
            os.remove(p)
    shutil.copy2(dwg, copy)
    with open(scr, "w", newline="", encoding="ascii") as fh:
        fh.write(build_script(flt, keep_units))
    t0 = time.time()
    with open(log, "wb") as fh:
        p = subprocess.Popen([ACC, "/i", copy, "/s", scr, "/l", "en-US"], stdout=fh, stderr=subprocess.STDOUT,
                             cwd=work, creationflags=CREATE_NO_WINDOW)
        try:
            status = "exit %s" % p.wait(timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            try:
                p.wait(30)
            except subprocess.TimeoutExpired:
                pass
            status = "TIMEOUT after %d s, killed" % timeout
    secs = time.time() - t0
    if not keep_copy:
        try:
            os.remove(copy)
        except OSError:
            pass
    return log, status, secs


def read_log(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    txt = raw.decode("utf-16-le", "ignore")
    if "Command" not in txt and b"Command" in raw:          # not UTF-16 after all
        txt = raw.decode("utf-8", "ignore")
    return txt.replace("\r\n", "\n").replace("\r", "\n")


# ------------------------------------------------------------------ value parsing
_FTIN = re.compile(r"""^(?:(\d+(?:\.\d+)?)')?\s*-?\s*(?:(?:(\d+(?:\.\d+)?)(?:[\s-]+(\d+)/(\d+))?|(\d+)/(\d+))")?$""")


def parse_len(s):
    """'136.65' (decimal), 11'-4 21/32" (architectural) or 11'-4.656" (engineering) -> float.
    Feet-inch text comes back in inches (the drawing unit those formats assume)."""
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        pass
    neg = s.startswith("-")
    body = s[1:].strip() if neg else s
    m = _FTIN.match(body)
    if not m or (m.group(1) is None and m.group(2) is None and m.group(5) is None):
        return None
    v = float(m.group(1) or 0) * 12.0
    if m.group(2) is not None:
        v += float(m.group(2)) + (float(m.group(3)) / float(m.group(4)) if m.group(3) else 0.0)
    elif m.group(5) is not None:
        v += float(m.group(5)) / float(m.group(6))
    return -v if neg else v


def parse_pt(s):
    if not s:
        return None
    parts = s.strip().strip("()").split(",")
    vals = [parse_len(x) for x in parts]
    if len(vals) != 3 or any(v is None for v in vals):
        return None
    return tuple(vals)


def split_system(s):
    """'CHWS (Chilled water supply (made by COM))' -> ('CHWS', 'Chilled water supply (made by COM)')."""
    s = (s or "").strip()
    if s.endswith(")"):
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ")":
                depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    if s[:i].strip():
                        return s[:i].strip(), s[i + 1:-1].strip()
                    break
    return s, ""


_NUM = r"(?:\d+ \d+/\d+|\d+(?:\.\d+)?-\d+/\d+|\d+/\d+|\d+(?:\.\d+)?)"
_SZ = _NUM + r"\s*(?:Inch(?:es)?\b|in\b\.?|\"|mm\b)"
_LEAD = re.compile(r"^\s*(" + _SZ + r"(?:\s*x\s*" + _SZ + r")*)\s*(.*)$", re.I)
_ONE = re.compile(r"(" + _NUM + r")\s*(Inch(?:es)?\b|in\b\.?|\"|mm\b)", re.I)


def _num(t):
    t = t.strip()
    m = re.match(r"^(\d+(?:\.\d+)?)[ -](\d+)/(\d+)$", t)
    if m:
        return float(m.group(1)) + float(m.group(2)) / float(m.group(3))
    if "/" in t:
        a, b = t.split("/")
        return float(a) / float(b)
    return float(t)


def parse_style(style):
    """'1.50 Inch x 1.00 Inch Glued - Sch 40 - Concentric Reducer' -> ([1.5, 1.0], '1-1/2" x 1"', 'Glued - Sch 40 - Concentric Reducer').
    Sizes come back in inches (mm sizes converted, but shown in mm). ([], '', style) when no leading size is found."""
    m = _LEAD.match(style or "")
    if not m:
        return [], "", (style or "").strip()
    sizes, shown = [], []
    for num, unit in _ONE.findall(m.group(1)):
        v = _num(num)
        if unit.lower() == "mm":
            sizes.append(v / 25.4)
            shown.append("%g mm" % v)
        else:
            sizes.append(v)
            shown.append(fmt_in(v))
    return sizes, " x ".join(shown), m.group(2).strip()


def fmt_in(v):
    if v is None:
        return ""
    fr = Fraction(v).limit_denominator(64)
    if abs(float(fr) - v) > 1e-6:
        return ("%.3f" % v).rstrip("0").rstrip(".") + '"'
    w, r = divmod(fr.numerator, fr.denominator)
    if r == 0:
        return '%d"' % w
    return ('%d/%d"' % (r, fr.denominator)) if w == 0 else ('%d-%d/%d"' % (w, r, fr.denominator))


_KINDS = [("concentric reducer", "Reducer, concentric"), ("eccentric reducer", "Reducer, eccentric"), ("reducer", "Reducer"),
          ("elbow", "Elbow"), ("bend", "Bend"), ("tee", "Tee"), ("wye", "Wye"), ("cross", "Cross"), ("lateral", "Lateral"),
          ("coupling", "Coupling"), ("union", "Union"), ("cap", "Cap"), ("plug", "Plug"), ("flange", "Flange"),
          ("bushing", "Bushing"), ("adapter", "Adapter"), ("nipple", "Nipple"), ("transition", "Transition"),
          ("takeoff", "Takeoff"), ("valve", "Valve"), ("olet", "Olet")]


def fitting_kind(part):
    low = part.lower()
    for key, label in _KINDS:
        if re.search(r"\b" + key + r"\b", low) or (key == "olet" and re.search(r"olet\b", low)):
            if label in ("Elbow", "Bend"):
                a = re.search(r"(\d+(?:\.\d+)?)\s*deg", low)
                if a:
                    return "%s %s" % (label, ("%g" % float(a.group(1))))
            return label
    return "Other"


def type_label(t):
    t = t[5:] if t.startswith("AECB_") else t
    return {"PIPE": "Pipe", "PIPEFITTING": "Pipe fitting", "PIPECUSTOMFITTING": "Pipe custom fitting", "PIPEFLEX": "Flex pipe",
            "DUCT": "Duct", "DUCTFITTING": "Duct fitting", "DUCTCUSTOMFITTING": "Duct custom fitting", "DUCTFLEX": "Flex duct",
            "CONDUIT": "Conduit", "CONDUITFITTING": "Conduit fitting", "CABLETRAY": "Cable tray",
            "CABLETRAYFITTING": "Cable tray fitting", "MVPART": "Multi-view part"}.get(t, t.replace("_", " ").title())


# ------------------------------------------------------------------ log parsing
_HDR = re.compile(r'^\s*([A-Z][A-Z0-9_]*)\s+Layer:\s*"([^"]*)"\s*$')
_SPACE = re.compile(r"^\s*Space:\s*(.*?)\s*$")
_HANDLE = re.compile(r"^\s*Handle\s*=\s*([0-9A-Fa-f]+)\s*$")
_FIELD = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 ./()-]*?)\s+:\s?(.*?)\s*$")
_OTHER = re.compile(r"^\s*([A-Za-z][A-Za-z ]*?):\s+(.*?)\s*$")


def parse_log(txt):
    meta = {"vars": {}, "count": None, "types": {}, "xrefs": [], "found": None, "end": False, "errors": [],
            "press_enter": False, "version": "", "unparsed": 0, "list_closed": False, "not_current": 0}
    m = re.search(r"AutoCAD Core Engine Console.*?\(([^)]*)\)", txt)
    meta["version"] = m.group(1) if m else ""
    m = re.search(r"^MTO-VARS (.*)$", txt, re.M)
    if m:
        meta["vars"] = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", m.group(1))}
    m = re.search(r"^MTO-COUNT (\d+)", txt, re.M)
    meta["count"] = int(m.group(1)) if m else None
    m = re.search(r"^MTO-TYPES (.*)$", txt, re.M)
    if m:
        meta["types"] = {k: int(v) for k, v in re.findall(r'\("([^"]+)" \. (\d+)\)', m.group(1))}
    m = re.search(r"^MTO-XREFS (.*)$", txt, re.M)
    if m:
        meta["xrefs"] = [x for x in m.group(1).strip().split("|") if x]
    meta["end"] = bool(re.search(r"^MTO-END", txt, re.M))
    meta["errors"] = [l.strip() for l in txt.split("\n") if re.search(r"; error|Unknown command|\*Invalid", l)][:20]
    meta["press_enter"] = bool(re.search(r"(?i)press enter to continue", txt))

    lines = txt.split("\n")
    start = next((i for i, l in enumerate(lines) if re.match(r"^Command:\s*_\.LIST\s*$", l.strip())), None)
    recs = []
    if start is None:
        return recs, meta
    cur = None
    for l in lines[start + 1:]:
        if l.startswith("Command:"):
            meta["list_closed"] = True
            break
        s = l.rstrip()
        if not s.strip() or s.strip() == "CoreHeartBeat":
            continue
        fm = re.match(r"^\s*(\d+) found", s)
        if fm and cur is None:
            meta["found"] = int(fm.group(1))
            continue
        fm = re.match(r"^\s*(\d+) (?:was|were) not in current space", s)
        if fm and cur is None:
            meta["not_current"] = int(fm.group(1))
            continue
        h = _HDR.match(s)
        if h:
            cur = {"type": h.group(1), "layer": h.group(2), "space": "", "handle": "", "fields": defaultdict(list)}
            recs.append(cur)
            continue
        if cur is None:
            continue
        m = _SPACE.match(s)
        if m:
            cur["space"] = m.group(1)
            continue
        m = _HANDLE.match(s)
        if m:
            cur["handle"] = m.group(1).upper()
            continue
        m = _FIELD.match(s) or _OTHER.match(s)
        if m:
            cur["fields"][m.group(1).strip()].append(m.group(2))
        else:
            meta["unparsed"] += 1
    return recs, meta


# ------------------------------------------------------------------ records
def derive(rec, ftu, units_label, drawing):
    f = rec["fields"]
    one = lambda k: (f.get(k) or [None])[0]
    length, cut = parse_len(one("Length")), parse_len(one("Cut Length"))
    sp, ep = parse_pt(one("Start Point")), parse_pt(one("End Point"))
    ins = parse_len(one("Insulation Thickness"))
    sysname, sysdesc = split_system(one("System Reference"))
    style = (one("Style Reference") or "").strip()
    sizes, size_txt, part = parse_style(style)
    linear = length is not None
    if rec["type"] == "AECB_PIPE":
        kind = "Pipe"
    elif linear:
        kind = type_label(rec["type"])
    elif "FITTING" in rec["type"]:
        kind = fitting_kind(part)
    else:
        kind = type_label(rec["type"])
    row = {"drawing": drawing, "handle": rec["handle"], "type": rec["type"], "layer": rec["layer"], "system": sysname,
           "system_description": sysdesc, "routing_preference": (one("Routing Preference") or "").strip(),
           "style_reference": style, "part": part, "kind": kind, "size": size_txt,
           "nominal_in": round(sizes[0], 4) if sizes else "",
           "length_ft": round(length * ftu, 6) if linear else "", "cut_length_ft": round(cut * ftu, 6) if cut is not None else "",
           "units": units_label}
    for tag, p in (("start", sp), ("end", ep)):
        for k, v in zip("xyz", p or ("", "", "")):
            row["%s_%s" % (tag, k)] = round(v, 6) if v != "" else ""
    row["slope_list"] = (one("Slope") or "").strip()
    row.update({"slope_deg": "", "slope_pct": "", "slope_in_per_ft": "", "orientation": ""})
    row["length_check"] = ""
    if sp and ep:
        dx, dy, dz = (ep[i] - sp[i] for i in range(3))
        hrz, d3 = math.hypot(dx, dy), math.sqrt(dx * dx + dy * dy + dz * dz)
        tol = 1e-4 + 1e-7 * d3
        if d3 <= tol:
            row["orientation"] = "zero length"
        elif hrz <= tol:
            row["orientation"], row["slope_deg"] = "vertical", (90.0 if dz > 0 else -90.0)
        else:
            row["slope_deg"] = round(math.degrees(math.atan2(dz, hrz)), 4)
            row["slope_pct"] = round(100.0 * dz / hrz, 4)
            row["slope_in_per_ft"] = round(12.0 * dz / hrz, 4)
            row["orientation"] = "level" if abs(dz) <= tol else "sloped"
        if linear:
            row["length_check"] = round((length - d3) * ftu * 12.0, 4)      # inches; straight pipe reads 0
    row["insulation_in"] = round(ins * ftu * 12.0, 4) if ins is not None else ""
    row["connection_points"] = "; ".join(f.get("Connection Point", []))
    row["insertion"] = (one("Insertion") or "").strip()
    row["rotation"] = (one("Rotation") or "").strip()
    known = {"Length", "Cut Length", "Start Point", "End Point", "Insulation Thickness", "System Reference", "Style Reference",
             "Routing Preference", "Slope", "Connection Point", "Insertion", "Rotation", "Normal"}
    other = {k: v if len(v) > 1 else v[0] for k, v in f.items() if k not in known}
    row["other"] = json.dumps(other) if other else ""
    row["_len"], row["_cut"], row["_sizes"], row["_ins"] = (length * ftu if linear else None,
                                                            cut * ftu if cut is not None else None, sizes,
                                                            ins * ftu * 12.0 if ins is not None else 0.0)
    return row


COLS = ["drawing", "handle", "type", "kind", "layer", "system", "system_description", "routing_preference", "size", "nominal_in",
        "part", "style_reference", "length_ft", "cut_length_ft", "start_x", "start_y", "start_z", "end_x", "end_y", "end_z",
        "units", "orientation", "slope_deg", "slope_pct", "slope_in_per_ft", "slope_list", "length_check", "insulation_in",
        "connection_points", "insertion", "rotation", "other"]


def units_for(meta, override):
    """(feet per drawing unit, label, warning or None)."""
    v = meta["vars"]
    code = UNIT_ARG[override] if override else v.get("INSUNITS")
    if code in FT_PER_UNIT:
        return FT_PER_UNIT[code], UNIT_NAME[code], None
    if code == 0 or code is None:
        why = "INSUNITS is %s" % ("0 (unitless)" if code == 0 else "unknown")
        return 1 / 12.0, "inches (assumed)", why + ": lengths assume 1 unit = 1 inch; pass --units if not"
    raise SystemExit("INSUNITS %s is not supported; pass --units in|ft|mm|cm|m" % code)


# ------------------------------------------------------------------ summary
def summarize(rows):
    """The summary tables as lists of dicts: lengths, fittings by type, fittings by part, insulated, other."""
    lin = [r for r in rows if r["_len"] is not None]
    pipes = defaultdict(lambda: [0, 0.0, 0.0, None])
    for r in lin:
        k = (r["kind"], r["system"], r["size"] or "(size not read)")
        p = pipes[k]
        p[0] += 1
        p[1] += r["_len"]
        p[2] += r["_cut"] or 0.0
        p[3] = r["_sizes"][0] if r["_sizes"] else -1.0
    t_pipe = [{"kind": k[0], "system": k[1], "size": k[2], "count": v[0], "length_ft": v[1], "cut_length_ft": v[2], "_n": v[3]}
              for k, v in pipes.items()]
    t_pipe.sort(key=lambda d: (d["kind"] != "Pipe", d["kind"], d["system"].lower(), -d["_n"]))
    fits = [r for r in rows if r["_len"] is None and "FITTING" in r["type"]]
    ck, cp = Counter(), Counter()
    nsz = {}
    for r in fits:
        sz = r["size"] or "(size not read)"
        ck[(r["kind"], sz)] += 1
        cp[(r["part"] or r["style_reference"], sz)] += 1
        nsz[sz] = r["_sizes"][0] if r["_sizes"] else -1.0
    t_kind = [{"kind": k, "size": s, "count": n} for (k, s), n in sorted(ck.items(), key=lambda x: (x[0][0], -nsz[x[0][1]]))]
    t_part = [{"part": p, "size": s, "count": n} for (p, s), n in sorted(cp.items(), key=lambda x: (x[0][0], -nsz[x[0][1]]))]
    ins = defaultdict(float)
    for r in lin:
        if r["_ins"]:
            ins[(r["system"], r["size"], fmt_in(r["_ins"]))] += r["_len"]
    t_ins = [{"system": k[0], "size": k[1], "insulation": k[2], "length_ft": v} for k, v in sorted(ins.items())]
    oth = Counter((type_label(r["type"]), r["style_reference"]) for r in rows if r["_len"] is None and "FITTING" not in r["type"])
    t_oth = [{"type": k[0], "style": k[1], "count": n} for k, n in sorted(oth.items())]
    return t_pipe, t_kind, t_part, t_ins, t_oth


FAIL, WARN, NOTE = "CHECK FAILED", "WARNING", "NOTE"


def checks(runs):
    """[(level, text)]. FAIL = the takeoff may be missing or double counting objects."""
    out = []
    for run in runs:
        meta, rows, d = run["meta"], run.get("rows", []), run["drawing"]
        if not run["ok"]:
            out.append((FAIL, "%s: console run did not finish (%s); left out of the takeoff (%d objects had printed)"
                        % (d, run["status"], run.get("parsed", 0))))
            continue
        n = len(rows)
        if meta["count"] is not None and meta["count"] != n:
            out.append((FAIL, "%s: database has %d MEP objects in model space but %d were parsed from LIST" % (d, meta["count"], n)))
        if meta["found"] is not None and meta["found"] - meta["not_current"] != n:
            out.append((FAIL, "%s: LIST kept %d objects but %d were parsed" % (d, meta["found"] - meta["not_current"], n)))
        if meta["not_current"]:
            out.append((WARN, "%s: LIST skipped %d objects not in the current space" % (d, meta["not_current"])))
        got = Counter(r["type"] for r in rows)
        for t, c in sorted(meta["types"].items()):
            if got.get(t, 0) != c:
                out.append((FAIL, "%s: %s count is %d in the database, %d parsed" % (d, t, c, got.get(t, 0))))
        handles = Counter(r["handle"] for r in rows)
        dup = [h for h, c in handles.items() if c > 1]
        if dup:
            out.append((FAIL, "%s: handles listed twice: %s" % (d, ", ".join(dup[:10]))))
        if meta["press_enter"]:
            out.append((FAIL, "%s: LIST paused for Enter; output may be cut short" % d))
        if meta["errors"]:
            out.append((WARN, "%s: console reported: %s" % (d, " | ".join(meta["errors"][:3]))))
        if meta["unparsed"]:
            out.append((WARN, "%s: %d LIST lines did not parse (kept going)" % (d, meta["unparsed"])))
        bad = [r["handle"] for r in rows if r["_len"] is not None and r["length_check"] != "" and abs(r["length_check"]) > 0.01]
        if bad:
            out.append((WARN, "%s: %d linear objects whose Length differs from the start-to-end distance by over 0.01 in (curved or flex?): %s"
                        % (d, len(bad), ", ".join(bad[:10]))))
        if meta["xrefs"]:
            out.append((NOTE, "%s: xrefs are not in this takeoff (run their DWGs too): %s" % (d, ", ".join(meta["xrefs"]))))
        if run.get("unit_warning"):
            out.append((NOTE, "%s: %s" % (d, run["unit_warning"])))
        nos = [r["handle"] for r in rows if not r["_sizes"]]
        if nos:
            out.append((NOTE, "%s: no size in the style name of %d objects (grouped by full name): %s" % (d, len(nos), ", ".join(nos[:10]))))
    return out


def write_outputs(rows, runs, out, name, warn):
    os.makedirs(out, exist_ok=True)
    f_obj = os.path.join(out, name + "_objects.csv")
    f_sum = os.path.join(out, name + "_summary.csv")
    f_txt = os.path.join(out, name + "_summary.txt")
    t_pipe, t_kind, t_part, t_ins, t_oth = summarize(rows)
    with open(f_obj, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with open(f_sum, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "kind", "system", "size", "part_or_style", "insulation", "count", "length_ft", "cut_length_ft"])
        for d in t_pipe:
            w.writerow(["length", d["kind"], d["system"], d["size"], "", "", d["count"], round(d["length_ft"], 4), round(d["cut_length_ft"], 4)])
        for d in t_kind:
            w.writerow(["fitting_by_type", d["kind"], "", d["size"], "", "", d["count"], "", ""])
        for d in t_part:
            w.writerow(["fitting_by_part", "", "", d["size"], d["part"], "", d["count"], "", ""])
        for d in t_ins:
            w.writerow(["insulated", "", d["system"], d["size"], "", d["insulation"], "", round(d["length_ft"], 4), ""])
        for d in t_oth:
            w.writerow(["other", d["type"], "", "", d["style"], "", d["count"], "", ""])

    L = []
    names = ", ".join(r["drawing"] for r in runs)
    L.append("MEP takeoff: %s" % names)
    L.append("Run %s with the AutoCAD Core Console (headless). Lengths in feet." % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    for r in runs:
        m = r["meta"]
        L.append("  %s: %s in %.0f s, units %s, %s MEP objects in model space, %d listed and parsed."
                 % (r["drawing"], r["status"], r["secs"], r.get("units", "?"), m["count"] if m["count"] is not None else "?",
                    r["parsed"]))
    nfail = sum(1 for lv, _ in warn if lv == FAIL)
    L.append("Checks: " + ("%d FAILED" % nfail if nfail else "counts match, nothing missing or doubled"))
    for lv, x in warn:
        L.append("  %s: %s" % (lv, x))

    def table(title, head, data, fmt):
        L.append("")
        L.append(title)
        if not data:
            L.append("  (none)")
            return
        cells = [head] + [[str(v) for v in fmt(d)] for d in data]
        wd = [max(len(c[i]) for c in cells) for i in range(len(head))]
        isnum = [all(re.match(r"^-?\d+(\.\d+)?$", c[i]) or c[i] == "" for c in cells[1:]) for i in range(len(head))]
        for c in cells:
            L.append("  " + "  ".join(v.rjust(wd[i]) if isnum[i] else v.ljust(wd[i]) for i, v in enumerate(c)).rstrip())

    # pipe length table with system subtotals
    rows_t = []
    for kind in sorted({d["kind"] for d in t_pipe}, key=lambda k: (k != "Pipe", k)):
        sel = [d for d in t_pipe if d["kind"] == kind]
        for sysn in sorted({d["system"] for d in sel}, key=str.lower):
            ss = [d for d in sel if d["system"] == sysn]
            for d in ss:
                rows_t.append([kind, sysn, d["size"], d["count"], "%.2f" % d["length_ft"], "%.2f" % d["cut_length_ft"]])
            if len(ss) > 1:
                rows_t.append(["", sysn + " total", "", sum(d["count"] for d in ss), "%.2f" % sum(d["length_ft"] for d in ss),
                               "%.2f" % sum(d["cut_length_ft"] for d in ss)])
        rows_t.append(["", "ALL " + kind.upper(), "", sum(d["count"] for d in sel), "%.2f" % sum(d["length_ft"] for d in sel),
                       "%.2f" % sum(d["cut_length_ft"] for d in sel)])
    table("LENGTH BY SYSTEM AND SIZE (pipe pieces between fittings)", ["Object", "System", "Size", "Pieces", "Length ft", "Cut ft"],
          rows_t, lambda d: d)
    if rows_t:
        L.append("  Totals add unrounded lengths.")
    table("FITTINGS BY TYPE AND SIZE", ["Type", "Size", "Count"], t_kind, lambda d: [d["kind"], d["size"], d["count"]])
    if t_kind:
        L.append("  %s total fittings" % sum(d["count"] for d in t_kind))
    table("FITTINGS BY PART AND SIZE", ["Part", "Size", "Count"], t_part, lambda d: [d["part"], d["size"], d["count"]])
    if t_ins:
        table("INSULATED", ["System", "Size", "Insulation", "Length ft"], t_ins,
              lambda d: [d["system"], d["size"], d["insulation"], "%.2f" % d["length_ft"]])
    if t_oth:
        table("OTHER MEP OBJECTS", ["Type", "Style", "Count"], t_oth, lambda d: [d["type"], d["style"], d["count"]])
    L.append("")
    L.append("Files: %s | %s | logs: %s" % (f_obj, f_sum, " ; ".join(r["log"] for r in runs)))
    text = "\n".join(L) + "\n"
    with open(f_txt, "w", encoding="utf-8") as fh:
        fh.write(text)
    return f_obj, f_sum, f_txt, text


# ------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description="Headless pipe and fitting takeoff from AutoCAD MEP drawings.")
    ap.add_argument("dwg", nargs="*", help="MEP drawing(s); each is copied, never opened in place")
    ap.add_argument("--log", help="re-parse a saved console log instead of running AutoCAD")
    ap.add_argument("--out", help="output folder (default: the scratch run folder)")
    ap.add_argument("--name", help="output file prefix (default: drawing name, or 'combined')")
    ap.add_argument("--timeout", type=float, default=600, help="seconds per drawing before the console is killed (600)")
    ap.add_argument("--units", choices=sorted(UNIT_ARG), help="drawing unit if INSUNITS is wrong or 0")
    ap.add_argument("--keep-units", action="store_true", help="do not switch LUNITS to decimal (parse the drawing's own format)")
    ap.add_argument("--keep-copy", action="store_true", help="keep the scratch copy of the DWG")
    ap.add_argument("--filter", default="AECB_*", help='entity type filter for (ssget "X"), default "AECB_*"')
    ap.add_argument("--acc", help="path to accoreconsole.exe (default: ACCORECONSOLE env var, else the AutoCAD 2027 folder)")
    a = ap.parse_args(argv)
    global ACC
    if a.acc:
        ACC = a.acc
    if not FILTER_OK.match(a.filter):
        ap.error("--filter may hold only letters, digits and _*?,#@.~-")
    if bool(a.dwg) == bool(a.log):
        ap.error("give drawing(s) or --log, not both and not neither")

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    runs = []
    if a.log:
        name = a.name or safe_name(os.path.splitext(os.path.basename(a.log))[0])
        work = os.path.dirname(os.path.abspath(a.log))
        runs.append({"drawing": os.path.basename(a.log), "log": os.path.abspath(a.log), "status": "parsed from saved log",
                     "secs": 0.0})
    else:
        if not os.path.exists(ACC):
            raise SystemExit("accoreconsole.exe not found at " + ACC)
        for d in a.dwg:
            if not os.path.isfile(d):
                ap.error("no such file: " + d)
            if not d.lower().endswith(".dwg"):
                ap.error("not a .dwg: " + d)
        name = a.name or (safe_name(os.path.splitext(os.path.basename(a.dwg[0]))[0]) if len(a.dwg) == 1 else "combined")
        work = os.path.join(tempfile.gettempdir(), "mep_takeoff", stamp + "_" + safe_name(name, 40))
        for i, d in enumerate(a.dwg):
            sub = work if len(a.dwg) == 1 else os.path.join(work, "%02d_%s" % (i + 1, safe_name(os.path.splitext(os.path.basename(d))[0], 40)))
            log, status, secs = run_console(os.path.abspath(d), sub, a.filter, a.keep_units, a.timeout, a.keep_copy)
            runs.append({"drawing": os.path.basename(d), "log": log, "status": status, "secs": secs})
    out = a.out or work
    for suffix in ("_objects.csv", "_summary.csv", "_summary.txt"):       # never leave stale outputs behind a failed run
        p = os.path.join(out, name + suffix)
        if os.path.exists(p):
            os.remove(p)

    rows = []
    for run in runs:
        txt = read_log(run["log"])
        recs, meta = parse_log(txt)
        run["meta"] = meta
        run["ok"] = (meta["end"] or (bool(a.log) and meta["list_closed"])) and not run["status"].startswith("TIMEOUT")
        run["parsed"] = len(recs)
        if not run["ok"]:
            continue
        ftu, ulabel, uwarn = units_for(meta, a.units)
        run["units"], run["unit_warning"] = ulabel, uwarn
        rr = [derive(r, ftu, ulabel, run["drawing"]) for r in recs]
        run["parsed"], run["rows"] = len(rr), rr
        rows += rr
    warn = checks(runs)
    f_obj, f_sum, f_txt, text = write_outputs(rows, runs, out, name, warn)
    sys.stdout.write(text)
    if any(not r["ok"] for r in runs):
        return 2
    return 3 if any(lv == FAIL for lv, _ in warn) else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
