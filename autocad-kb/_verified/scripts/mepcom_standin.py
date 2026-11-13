"""Stand-in for one AutoCAD instance, no AutoCAD involved (used by mepcom_pid_test.py, 2026-10-18).

Registers an object in the Running Object Table under a test CLSID with the same RegisterActiveObject call AutoCAD
makes (item moniker !{CLSID}), gives it an HWND owned by this process, and shows one #32770 dialog off screen that is
never activated (no focus change, no taskbar button) and logs every WM_COMMAND it gets.
usage: py -3.14 mepcom_standin.py <log.jsonl> <max seconds> [--handoff]     (stops early when <log.jsonl>.stop exists)
--handoff (added 2026-10-18 for the launch() holder test): also register the object as !mepcom-handoff.<pid>, so a
stand-in holder can take it the way the real holder gets AutoCAD from CoCreateInstance; that name is revoked when
<log.jsonl>.handed appears.
"""
import json, os, sys, time
import pythoncom, pywintypes, win32api, win32con, win32gui
import win32com.server.util

TEST_CLSID = "{3F6B2E1A-9C4D-4B7E-8A21-5D0C7E9F1B42}"
LOGP, SECS = sys.argv[1], float(sys.argv[2])
HANDOFF = "--handoff" in sys.argv[3:]


def log(**k):
    k["pid"], k["t"] = os.getpid(), round(time.time(), 3)
    with open(LOGP, "a", encoding="utf-8") as f:
        f.write(json.dumps(k) + "\n")


hidden = win32gui.CreateWindowEx(0, "STATIC", "mepcom stand-in %d" % os.getpid(), win32con.WS_POPUP, 0, 0, 0, 0, 0, 0, 0, None)


class App:
    _public_methods_ = ["Pid"]
    _public_attrs_ = _readonly_attrs_ = ["HWND", "Caption"]
    HWND = hidden
    Caption = "mepcom stand-in %d" % os.getpid()

    def Pid(self):
        return os.getpid()


def dlgproc(h, msg, wp, lp):
    if msg == win32con.WM_INITDIALOG:
        return True
    if msg == win32con.WM_COMMAND:
        log(event="WM_COMMAND", id=win32api.LOWORD(wp))
        if win32api.LOWORD(wp) == win32con.IDCANCEL:
            win32gui.DestroyWindow(h)
        return True
    return False


tmpl = [["mepcom stand-in dialog %d" % os.getpid(), (0, 0, 120, 40), win32con.WS_POPUP | win32con.WS_CAPTION | win32con.DS_SETFONT,
         win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_NOACTIVATE, (8, "MS Shell Dlg")],
        ["Button", "OK", win32con.IDOK, (5, 5, 40, 14), win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON]]
dlg = win32gui.CreateDialogIndirect(win32api.GetModuleHandle(None), tmpl, 0, dlgproc)
win32gui.SetWindowPos(dlg, 0, -32000, -32000, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
win32gui.ShowWindow(dlg, win32con.SW_SHOWNOACTIVATE)

ob = win32com.server.util.wrap(App())
try:
    reg = pythoncom.RegisterActiveObject(ob, pywintypes.IID(TEST_CLSID), 0)
except pywintypes.com_error as e:
    if e.hresult != 262631:     # MK_S_MONIKERALREADYREGISTERED: a success code, registered anyway (what a second AutoCAD gets)
        raise
    reg = None
hand = None
if HANDOFF:
    rot = pythoncom.GetRunningObjectTable()
    hand = rot.Register(0, ob, pythoncom.CreateItemMoniker("!", "mepcom-handoff.%d" % os.getpid()))
log(event="ready", hwnd=hidden, dialog=dlg, rot_handle=reg, handoff=HANDOFF)
t = time.time()
while time.time() - t < SECS and not os.path.exists(LOGP + ".stop"):
    if hand is not None and os.path.exists(LOGP + ".handed"):
        rot.Revoke(hand)
        hand = None
        log(event="handoff_revoked")
    pythoncom.PumpWaitingMessages()
    time.sleep(0.02)
if hand is not None:
    rot.Revoke(hand)
if reg is not None:
    pythoncom.RevokeActiveObject(reg)
log(event="exit", dialog_alive=bool(win32gui.IsWindow(dlg)))
