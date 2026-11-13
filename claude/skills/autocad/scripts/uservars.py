"""Put back the AutoCAD settings that GUI automation changes and AutoCAD saves per user.

FILEDIA, CMDDIA, LOGFILEMODE and BACKGROUNDPLOT live in the registry, so a script that sets them
changes the user's own AutoCAD until someone sets them back (FILEDIA 0 left behind turns the
user's file dialogs off). Console (.scr) scripts should not set them at all: a running script gets
command-line prompts anyway (see the FILEDIA help page). Commands typed into the MEP window
through SendCommand may need FILEDIA 0, so GUI drivers use this module:

    import uservars
    uservars.save()      # before the first setvar; later calls keep the first reading
    ...
    uservars.restore()   # at the end; it also runs at exit, so an early sys.exit still restores
"""
import atexit, winreg
from mepcom import var, send, wait_idle

NAMES = ("FILEDIA", "CMDDIA", "LOGFILEMODE", "BACKGROUNDPLOT")
# where the MEP window keeps FILEDIA, for the fallback when MEP no longer answers COM
FILEDIA_KEY = r"Software\Autodesk\AutoCAD\R26.0\ACAD-A106:409\FixedProfile\General Configuration"
saved = {}


def save(names=NAMES):
    """Read each value once. A relaunched MEP reads the changed value, so the first reading wins."""
    for n in names:
        if n not in saved:
            try:
                saved[n] = int(var(n))
            except Exception:
                pass
    return dict(saved)


def restore():
    """Set every saved value back and return what AutoCAD reads afterwards."""
    if not saved:
        return {}
    send(" ".join('(setvar "%s" %d)' % (n, v) for n, v in saved.items()) + " (princ)\n")
    wait_idle(60)
    now = {n: int(var(n)) for n in saved}
    if now == saved:
        saved.clear()   # done: the exit hook has nothing left to do
    return now


def _at_exit():
    try:
        restore()
    except Exception:
        if "FILEDIA" in saved:   # MEP gone: write the one that hides dialogs straight to the registry
            try:
                k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, FILEDIA_KEY, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "FileDialog", 0, winreg.REG_DWORD, saved["FILEDIA"])
                winreg.CloseKey(k)
            except OSError:
                pass


atexit.register(_at_exit)
