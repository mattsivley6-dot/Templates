"""Probes for the headless MEP takeoff: LIST format under LUNITS 2, LIST !ss, frozen/locked layers, paging on a big drawing.
usage: py -3.14 mto_probe_list.py <A|B|C|ALL> [work_dir with p1.dwg] [large MEP drawing for C]
"""
import os, re, shutil, subprocess, sys, time
W = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))  # holds p1.dwg
ACC = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"
BIG_SRC = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("MTO_BIG_DWG")   # a large MEP drawing for test C


def run(dwg, lines, tag, timeout=300):
    scr = os.path.join(W, tag + ".scr")
    log = os.path.join(W, tag + ".log")
    if os.path.exists(log):
        os.remove(log)
    open(scr, "w", newline="").write("\r\n".join(lines) + "\r\n\r\n")
    t0 = time.time()
    with open(log, "wb") as fh:
        p = subprocess.Popen([ACC, "/i", dwg, "/s", scr, "/l", "en-US"], stdout=fh, stderr=subprocess.STDOUT, cwd=W)
        try:
            p.wait(timeout)
            st = "exit %s" % p.returncode
        except subprocess.TimeoutExpired:
            p.kill()
            st = "TIMEOUT killed"
    txt = open(log, "rb").read().decode("utf-16-le", "ignore")
    return st, round(time.time() - t0, 1), txt


SS = '(setq ss (ssget "X" (list (cons 0 "AECB_*") (cons 410 "Model"))))'
SSN = '(princ (strcat "MTO-SS " (itoa (if ss (sslength ss) 0))))'
VARS = '(princ (strcat "MTO-VARS INSUNITS=" (itoa (getvar "INSUNITS")) " LUNITS=" (itoa (getvar "LUNITS")) " LUPREC=" (itoa (getvar "LUPREC")) " AUNITS=" (itoa (getvar "AUNITS")) " TILEMODE=" (itoa (getvar "TILEMODE"))))'
which = sys.argv[1] if len(sys.argv) > 1 else "ALL"

if which in ("A", "ALL"):
    d = os.path.join(W, "pA.dwg"); shutil.copyfile(os.path.join(W, "p1.dwg"), d)
    st, dt, t = run(d, ['(setvar "CMDECHO" 1)', VARS, '(setvar "TILEMODE" 1)', SS, SSN, '(setvar "LUNITS" 2)', '(setvar "LUPREC" 8)',
                        "_.LIST", "!ss", "", '(princ "MTO-END")', "_.QUIT", "_Y"], "pA")
    i = t.find("MTO-VARS")
    print("=== A", st, dt, "s\n", t[i:i + 6000])

if which in ("B", "ALL"):
    d = os.path.join(W, "pB.dwg"); shutil.copyfile(os.path.join(W, "p1.dwg"), d)
    st, dt, t = run(d, ['(setvar "CMDECHO" 1)', '(setvar "TILEMODE" 1)', '(setvar "CLAYER" "0")',
                        "_.-LAYER", "_FREEZE", "M-CHWS", "_LOCK", "M-Pipe-Std", "",
                        '(princ "MTO-B1")', "_.LIST", "_ALL", "",
                        '(princ "MTO-B2")', SS, SSN, "_.LIST", "!ss", "",
                        '(princ "MTO-B3")', "_.-LAYER", "_THAW", "*", "_UNLOCK", "*", "", "_.LIST", "_ALL", "",
                        '(princ "MTO-END")', "_.QUIT", "_Y"], "pB")
    for mk in ("MTO-B1", "MTO-B2", "MTO-B3"):
        i = t.find(mk)
        seg = t[i:t.find("MTO-", i + 8)]
        print("=== B", mk, st, dt, "s | AECB blocks:", len(re.findall(r"^\s+AECB_\w+\s+Layer:", seg, re.M)),
              "| select lines:", [l.strip() for l in seg.splitlines() if re.search(r"found|locked|frozen|not in current", l)])

if which in ("C", "ALL"):
    if not BIG_SRC:
        raise SystemExit("test C needs a large MEP drawing: pass it as the third argument or set MTO_BIG_DWG")
    d = os.path.join(W, "pC.dwg"); shutil.copyfile(BIG_SRC, d)
    st, dt, t = run(d, ['(setvar "CMDECHO" 1)', VARS, '(setvar "TILEMODE" 1)', SS, SSN, '(setvar "LUNITS" 2)', '(setvar "LUPREC" 8)',
                        "_.LIST", "!ss", "", '(princ "MTO-END")', "_.QUIT", "_Y"], "pC", timeout=420)
    blocks = re.findall(r"^\s+(AECB_\w+)\s+Layer:", t, re.M)
    from collections import Counter
    print("=== C", st, dt, "s | log chars", len(t), "| blocks", len(blocks), Counter(blocks))
    print("MTO lines:", [l.strip()[:200] for l in t.splitlines() if "MTO-" in l][:12])
    print("press-enter lines:", [l for l in t.splitlines() if re.search(r"(?i)press enter|continue", l)][:5])
    j = t.find("MTO-SS"); print(t[j:j + 3000])
