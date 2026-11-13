"""Recalculate a workbook in Excel (COM), save it, then list formulas that came back empty or as #errors.
usage: py -3.14 xl_recalc.py <workbook.xlsx>   (work on a copy; Excel must be installed)"""
import sys, win32com.client, pythoncom, openpyxl, os
p = os.path.abspath(sys.argv[1])
pythoncom.CoInitialize()
xl = win32com.client.DispatchEx("Excel.Application"); xl.Visible = False; xl.DisplayAlerts = False
try:
    import time
    wb = xl.Workbooks.Open(p); xl.CalculateFull(); wb.Save()
    for k in range(20):
        try:
            wb.Close(False); break
        except Exception:
            time.sleep(1.0)
finally:
    xl.Quit()
wbv = openpyxl.load_workbook(p, data_only=True)
wbf = openpyxl.load_workbook(p)
errs = []; nform = 0
for ws in wbf.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("="):
                nform += 1
                v = wbv[ws.title][c.coordinate].value
                if v is None or (isinstance(v, str) and v.startswith("#")):
                    errs.append((ws.title, c.coordinate, v, c.value[:60]))
print("formulas", nform, "errors", len(errs))
for e in errs[:25]: print(e)
