"""Headless AutoCAD 2027 Core Console tests: -PDFIMPORT and IMAGEASYNCWAIT before -PLOT.

usage: py -3.14 core_tests.py <work_dir>
"""
import os, subprocess, sys, time
import ezdxf, fitz

W = sys.argv[1].replace("\\", "/")
os.makedirs(W, exist_ok=True)
ACC = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"


def run(dxf, scr, log, timeout=150):
    for p in (log,):
        if os.path.exists(p):
            os.remove(p)
    t0 = time.time()
    with open(log, "wb") as fh:
        p = subprocess.Popen([ACC, "/i", dxf, "/s", scr, "/l", "en-US"], stdout=fh, stderr=subprocess.STDOUT, cwd=W)
        try:
            p.wait(timeout)
            status = "exit %s" % p.returncode
        except subprocess.TimeoutExpired:
            p.kill()
            status = "TIMEOUT killed"
    txt = open(log, "rb").read().decode("utf-16-le", "ignore")
    return status, time.time() - t0, txt


def scr(path, lines):
    open(path, "w", newline="").write("\r\n".join(lines) + "\r\n\r\n")


# inputs
pdf = W + "/sample.pdf"
d = fitz.open(); pg = d.new_page(width=792, height=612)
pg.draw_rect(fitz.Rect(72, 72, 720, 540), color=(0, 0, 0), width=1.5)
pg.draw_line((72, 306), (720, 306), color=(0, 0, 1), width=1)
pg.insert_text((90, 100), "PDFIMPORT TEST 4\" CHWS", fontsize=14)
d.save(pdf)
png = W + "/swatch.png"
pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 200, 100), False); pix.set_rect(pix.irect, (200, 30, 30)); pix.save(png)

base = W + "/base.dxf"
doc = ezdxf.new("R2018", setup=True); doc.header["$INSUNITS"] = 1
doc.modelspace().add_line((0, 0), (10, 0))
doc.saveas(base)

img = W + "/img.dxf"
doc = ezdxf.new("R2018", setup=True); doc.header["$INSUNITS"] = 1
msp = doc.modelspace()
idef = doc.add_image_def(filename=png.replace("/", "\\"), size_in_pixel=(200, 100))
msp.add_image(idef, insert=(0, 0), size_in_units=(20, 10))
msp.add_line((0, -2), (20, -2))
doc.saveas(img)

results = []

# Test 1: -PDFIMPORT in the Core Console
s1 = W + "/t1.scr"
scr(s1, ["(setvar \"CMDECHO\" 1)", "_.FILEDIA", "0", "_-PDFIMPORT", "_F", pdf, "1", "0,0", "1", "0",
         '(princ (strcat "\\nCOUNT " (itoa (if (setq ss (ssget "X")) (sslength ss) 0)) "\\n"))',
         "_.SAVEAS", "2018", W + "/t1_out.dwg", "_.QUIT", "_Y"])
st, dt, txt = run(base, s1, W + "/t1.log")
results.append(("T1 -PDFIMPORT", st, round(dt), [l for l in txt.splitlines() if any(k in l for k in ("PDFIMPORT", "Unknown", "COUNT", "page", "Page", "error", "file name", "Select PDF"))][:20]))

# Test 2a: plot an IMAGE without IMAGEASYNCWAIT; 2b: with it
for tag, pre in (("T2a no wait", []), ("T2b IMAGEASYNCWAIT", ["_IMAGEASYNCWAIT"])):
    out = W + "/%s.pdf" % tag.split()[0]
    if os.path.exists(out):
        os.remove(out)
    s2 = W + "/%s.scr" % tag.split()[0]
    scr(s2, ["(setvar \"CMDECHO\" 1)"] + pre + ["_.-PLOT", "_Y", "Model", "DWG To PDF.pc3", "ANSI full bleed B (17.00 x 11.00 Inches)",
             "_I", "_L", "_N", "_E", "_F", "_C", "_Y", "acad.ctb", "_Y", "_A", out, "_N", "_Y", "_.QUIT", "_Y"])
    st, dt, txt = run(img, s2, W + "/%s.log" % tag.split()[0])
    imgs = []
    if os.path.exists(out):
        dd = fitz.open(out)
        imgs = [(i[2], i[3]) for i in dd[0].get_images()]
        ndraw = len(dd[0].get_drawings())
    else:
        ndraw = None
    results.append((tag, st, round(dt), {"pdf": os.path.exists(out), "images": imgs, "paths": ndraw},
                    [l for l in txt.splitlines() if any(k in l for k in ("IMAGEASYNC", "Unknown", "error", "plotting area", "Effective"))][:8]))

for r in results:
    print(r)
