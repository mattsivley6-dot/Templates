"""ClaudeJobRunner v2. Runs job scripts dropped in a folder, on Fusion's main thread. No mouse, no keyboard.

Jobs folder: the FUSION_JOBS_DIR environment variable if set (Fusion must be started with it in its
environment), else %TEMP%\\claude-fusion\\jobs. fjob.py and fusion_up.ps1 use the same rule.

Drop <name>.py in JOBS (write <name>.tmp first, then rename, so a half-written file is never run).
The runner execs it with app, adsk, JOBS and RESULT in scope, then writes:
  <name>.py.queued   the poller saw it (worker thread)
  <name>.py.started  the main thread began it; first line is the active command at that moment
  <name>.py.done     RESULT, then anything the job print()ed
  <name>.py.err      traceback (and "[transaction aborted]" when the job ran in a transaction)
Flags: put a line "# runner: <words>" in the first 5 lines of the job.
  txn       wrap the job in PTransaction.Start/Commit: one undo step for the whole job, and a job that
            raises is rolled back (PTransaction.Abort) so it leaves no half-built geometry.
  force     run even when a command is active in Fusion. Without it the job is REFUSED when
            UserInterface.activeCommand is not "SelectCommand" (the user may be in the middle of a dialog;
            Autodesk's own MCP server refuses scripts the same way). Note: after a drawing export Fusion
            starts FusionDrawingAutoDimensionEditCommand by itself; a forced job may end it with
            app.userInterface.terminateActiveCommand().
  readonly  same as force, for jobs that only read (inspection while a dialog is open). Not enforced.
A job written MCP-style (it defines def run(_context: str) and does nothing at top level) is also run.
"""
import adsk.core, adsk.fusion, traceback, threading, os, glob, time, io, contextlib, tempfile

JOBS = os.environ.get("FUSION_JOBS_DIR") or os.path.join(tempfile.gettempdir(), "claude-fusion", "jobs")
EVT = "ClaudeJobRunnerEvent"
POLL_S = 0.5
IDLE = ("SelectCommand", "")  # "" is what activeCommand returns when no document is open (Home screen)
app = None
handlers = []
STOP = None
evt = None
busy = False


def _log(msg):
    try:
        app.log("ClaudeJobRunner: " + msg, adsk.core.LogLevels.InfoLogLevel, adsk.core.LogTypes.FileLogType)
    except Exception:
        pass


def _flags(src):
    words = set()
    for line in src.splitlines()[:5]:
        s = line.strip().lower()
        if s.startswith("# runner:"):
            words.update(s[len("# runner:"):].replace(",", " ").split())
    return words


class JobHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global busy
        path = args.additionalInfo
        name = os.path.basename(path)
        if busy:  # a job called adsk.doEvents(); let the poller fire this one again later
            try:
                os.remove(path + ".queued")
            except Exception:
                pass
            return
        busy = True
        txn = False
        t0 = time.time()
        try:
            ui = app.userInterface
            active = ui.activeCommand
            open(path + ".started", "w", encoding="utf-8").write("activeCommand=%s\n%s\n" % (active, time.ctime()))
            src = open(path, encoding="utf-8").read()
            fl = _flags(src)
            if active not in IDLE and not ({"force", "readonly"} & fl):
                raise RuntimeError("REFUSED: command '%s' is active in Fusion (a dialog may be open). "
                                   "Nothing was run. Wait, or resend with '# runner: force' (or readonly)." % active)
            g = {"app": app, "adsk": adsk, "JOBS": JOBS, "RESULT": ""}
            buf = io.StringIO()
            if "txn" in fl:
                app.executeTextCommand('PTransaction.Start "%s"' % name.replace('"', ""))
                txn = True
            with contextlib.redirect_stdout(buf):
                exec(compile(src, path, "exec"), g)
                if "def run(_context" in src and callable(g.get("run")):
                    g["run"]("")
            if txn:
                app.executeTextCommand("PTransaction.Commit")
                txn = False
            out = str(g.get("RESULT", ""))
            printed = buf.getvalue()
            if printed:
                out = (out + "\n" if out else "") + printed
            open(path + ".done", "w", encoding="utf-8").write(out)
            _log("%s done in %.1f s" % (name, time.time() - t0))
        except Exception:
            note = ""
            if txn:
                try:
                    app.executeTextCommand("PTransaction.Abort")
                    note = "\n[transaction aborted: the design was rolled back to before this job]"
                except Exception:
                    note = "\n[transaction abort FAILED: check the design for partial changes]"
            open(path + ".err", "w", encoding="utf-8").write(traceback.format_exc() + note)
            _log("%s failed after %.1f s" % (name, time.time() - t0))
        finally:
            busy = False


class Poller(threading.Thread):
    def __init__(self, ev):
        super().__init__(daemon=True)
        self.ev = ev

    def run(self):
        while not self.ev.wait(POLL_S):
            now = time.time()
            for f in sorted(glob.glob(os.path.join(JOBS, "*.py"))):
                q = f + ".queued"
                try:
                    if os.path.exists(q) or now - os.path.getmtime(f) < 0.5:
                        continue  # already queued, or possibly still being written
                    open(q, "w").write(time.ctime())
                    app.fireCustomEvent(EVT, f)
                except Exception:
                    pass


def run(context):
    global app, evt, STOP
    try:
        app = adsk.core.Application.get()
        os.makedirs(JOBS, exist_ok=True)
        evt = app.registerCustomEvent(EVT)
        h = JobHandler()
        evt.add(h)
        handlers.append(h)
        STOP = threading.Event()
        Poller(STOP).start()
        open(os.path.join(JOBS, "runner_started.txt"), "w").write(time.ctime() + "\nClaudeJobRunner v2\n")
        _log("v2 started, polling " + JOBS)
    except Exception:
        try:
            os.makedirs(JOBS, exist_ok=True)
            open(os.path.join(JOBS, "runner_error.txt"), "w").write(traceback.format_exc())
        except Exception:
            pass


def stop(context):
    try:
        if STOP:
            STOP.set()
        if evt and handlers:
            evt.remove(handlers[0])
        app.unregisterCustomEvent(EVT)
    except Exception:
        pass
