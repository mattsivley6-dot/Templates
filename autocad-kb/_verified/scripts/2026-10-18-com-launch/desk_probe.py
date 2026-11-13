"""No AutoCAD: does a process started on a second desktop keep its windows off the user's desktop, and can we see and
message them? Child = python making one visible STATIC window and a #32770 dialog that logs WM_COMMAND."""
import os, subprocess, sys, time
import win32con, win32gui, win32process, win32service, win32event

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "desk_probe_child.txt")
CHILD = r'''
import time, win32gui, win32con, win32api
out = r"%s"
h = win32gui.CreateWindow("STATIC", "mepcom desk probe", 0x10000000, 0, 0, 200, 100, 0, 0, 0, None)
def dlgproc(hd, msg, wp, lp):
    if msg == win32con.WM_COMMAND:
        open(out, "a").write("WM_COMMAND %%d\n" %% win32api.LOWORD(wp))
        win32gui.DestroyWindow(hd)
        return True
    return msg == win32con.WM_INITDIALOG
tmpl = [["mepcom desk probe dialog", (0, 0, 120, 40), win32con.WS_POPUP | win32con.WS_CAPTION | win32con.WS_VISIBLE | win32con.DS_SETFONT, 0, (8, "MS Shell Dlg")]]
d = win32gui.CreateDialogIndirect(win32api.GetModuleHandle(None), tmpl, 0, dlgproc)
open(out, "a").write("child up: window %%d dialog %%d foreground %%d\n" %% (h, d, win32gui.GetForegroundWindow()))
t = time.time()
while time.time() - t < 8:
    win32gui.PumpWaitingMessages(); time.sleep(0.02)
''' % OUT
if os.path.exists(OUT):
    os.remove(OUT)
NAME = "mepcom_probe_%d" % os.getpid()
hd = win32service.CreateDesktop(NAME, 0, win32con.GENERIC_ALL, None)
si = win32process.STARTUPINFO()
si.lpDesktop = "WinSta0\\" + NAME
fg0 = win32gui.GetForegroundWindow()
hp, ht, pid, tid = win32process.CreateProcess(None, '"%s" -c "%s"' % (sys.executable, CHILD.replace('"', '\\"')), None, None, False,
                                              win32con.CREATE_NO_WINDOW, None, None, si)
time.sleep(3)


def mine(hw):
    return win32process.GetWindowThreadProcessId(hw)[1] == pid


try:
    on_hidden = [(h, win32gui.GetWindowText(h), win32gui.GetClassName(h)) for h in hd.EnumDesktopWindows() if mine(h)]
except Exception as e:
    on_hidden = "ERR %s" % e
on_default = []
win32gui.EnumWindows(lambda h, _: on_default.append(h) if mine(h) else True, None)
print("child pid", pid, "| its windows on the second desktop:", on_hidden)
print("its windows on the user's desktop:", on_default)
dlg = [h for h, t, c in on_hidden if c == "#32770"] if isinstance(on_hidden, list) else []
if dlg:
    print("PostMessage IDCANCEL to the dialog on the second desktop:", win32gui.PostMessage(dlg[0], win32con.WM_COMMAND, win32con.IDCANCEL, 0))
time.sleep(1)
print("foreground unchanged:", win32gui.GetForegroundWindow() == fg0)
win32event.WaitForSingleObject(hp, 15000)
print("child log:", open(OUT).read() if os.path.exists(OUT) else "none")
hd.CloseDesktop()
