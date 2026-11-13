"""Does a Core Console script need FILEDIA 0? Run -PDFIMPORT with FILEDIA 1 and see.
Leaves the registry FileDialog value exactly as it found it.
usage: py -3.14 fd_test.py [work_dir]        (default: a fdtest folder in the temp directory)
"""
import os, subprocess, sys, tempfile, winreg
import fitz, ezdxf

W = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(tempfile.gettempdir(), "fdtest")
ACC = r"C:\Program Files\Autodesk\AutoCAD 2027\accoreconsole.exe"
KEY = r"Software\Autodesk\AutoCAD\R26.0\ACAD-A101:409\FixedProfile\General Configuration"
os.makedirs(W, exist_ok=True)
pdf, dxf, scr, log = (os.path.join(W, n) for n in ("t.pdf", "base.dxf", "t.scr", "t.log"))
for f in (scr, log):
    if os.path.exists(f):
        os.remove(f)

d = fitz.open(); pg = d.new_page(width=612, height=792)
pg.draw_line((72, 72), (300, 300)); pg.draw_rect(fitz.Rect(320, 320, 420, 380)); pg.insert_text((100, 450), "FILEDIA TEST")
d.save(pdf); d.close()
ezdxf.new("R2018").saveas(dxf)


def reg(val=None):
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_READ | winreg.KEY_SET_VALUE)
    try:
        if val is not None:
            winreg.SetValueEx(k, "FileDialog", 0, winreg.REG_DWORD, val)
        return winreg.QueryValueEx(k, "FileDialog")[0]
    finally:
        winreg.CloseKey(k)


before = reg()
lines = [
    '(setq oldd (getvar "FILEDIA") oldf (getvar "PDFIMPORTFILTER") oldm (getvar "PDFIMPORTMODE"))',
    '(setvar "FILEDIA" 1)',
    '(princ (strcat "\\nMARK FILEDIA=" (itoa (getvar "FILEDIA"))))',
    '(setvar "PDFIMPORTFILTER" 8)',
    '(setvar "PDFIMPORTMODE" 6)',
    '_-PDFIMPORT', '_F', pdf.replace("\\", "/"), '1', '_non', '0,0', '1', '0',
    '(princ (strcat "\\nMARK COUNT=" (itoa (if (ssget "X") (sslength (ssget "X")) 0))))',
    '(setvar "PDFIMPORTFILTER" oldf)',
    '(setvar "PDFIMPORTMODE" oldm)',
    '(setvar "FILEDIA" oldd)',
    '(princ (strcat "\\nMARK RESTORED=" (itoa (getvar "FILEDIA"))))',
    '_.QUIT', '_Y', '',
]
open(scr, "w", encoding="ascii", newline="\r\n").write("\n".join(lines) + "\n")

with open(log, "wb") as fh:
    p = subprocess.Popen([ACC, "/i", dxf, "/s", scr, "/l", "en-US"], stdout=fh, stderr=subprocess.STDOUT,
                         cwd=W, creationflags=0x08000000)
    try:
        p.wait(120); timed_out = False
    except subprocess.TimeoutExpired:
        p.kill(); p.wait(); timed_out = True

txt = open(log, "rb").read().decode("utf-16-le", "ignore")
after = reg()
print("registry FileDialog before", before, "after run", after, "| timed out:", timed_out, "| exit", p.returncode)
for ln in txt.splitlines():
    s = ln.strip()
    if s.startswith("MARK") or "PDF" in s or "file" in s.lower() or "error" in s.lower():
        print("  log:", s[:200])
if after != before:
    print("registry put back to", reg(before))
