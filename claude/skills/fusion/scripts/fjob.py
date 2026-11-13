"""Run one Python job inside Fusion through the ClaudeJobRunner add-in and print its RESULT.

  python fjob.py <job.py> [timeout_s] [--jobs <dir>]        (default timeout 180 s)

The job file runs on Fusion's main thread via exec() with `app`, `adsk`, `JOBS` and `RESULT` in scope.
Set RESULT to a string to return text. Exit code: 0 done, 1 job raised (traceback printed), 2 timeout,
3 runner not live. The file is copied in atomically (the runner only globs *.py, so a .tmp is ignored).

Jobs folder: --jobs, else the FUSION_JOBS_DIR environment variable, else %TEMP%\\claude-fusion\\jobs.
It must match the folder the add-in polls (same rule in ClaudeJobRunner.py).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

DEFAULT_JOBS = os.environ.get("FUSION_JOBS_DIR") or os.path.join(tempfile.gettempdir(), "claude-fusion", "jobs")


def fusion_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Fusion360.exe", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True).stdout
    return "Fusion360.exe" in out


def main():
    argv = sys.argv[1:]
    jobs = DEFAULT_JOBS
    if "--jobs" in argv:
        i = argv.index("--jobs")
        jobs = argv[i + 1]
        del argv[i:i + 2]
    if not argv:
        sys.exit(__doc__)
    src = argv[0]
    tmo = float(argv[1]) if len(argv) > 1 else 180.0
    if not fusion_running():
        print("RUNNER NOT LIVE: Fusion360.exe is not running")
        sys.exit(3)
    os.makedirs(jobs, exist_ok=True)
    name = os.path.basename(src)
    dst = os.path.join(jobs, name)
    for ext in (".done", ".err", ".queued", ""):
        if os.path.exists(dst + ext):
            os.remove(dst + ext)
    shutil.copyfile(src, dst + ".tmp")
    os.replace(dst + ".tmp", dst)
    t0 = time.time()
    queued_seen = False
    while time.time() - t0 < tmo:
        if os.path.exists(dst + ".done"):
            print(f"DONE in {time.time() - t0:.1f} s")
            print(open(dst + ".done", encoding="utf-8").read())
            return 0
        if os.path.exists(dst + ".err"):
            print(f"ERR after {time.time() - t0:.1f} s")
            print(open(dst + ".err", encoding="utf-8").read())
            return 1
        if not queued_seen and os.path.exists(dst + ".queued"):
            queued_seen = True
        if not queued_seen and time.time() - t0 > 10:
            print("RUNNER NOT LIVE: job not picked up within 10 s (add-in not loaded, wrong jobs folder, or Fusion busy)")
            return 3
        time.sleep(0.25)
    started = dst + ".started"
    st = " | ".join(open(started, encoding="utf-8").read().split()) if os.path.exists(started) else "not started (main thread busy or blocked)"
    cpu = ""
    try:
        ps = ("$p=Get-Process Fusion360 -ErrorAction Stop; $c=$p.CPU; Start-Sleep 3; $p.Refresh(); "
              "'Fusion CPU over 3 s: ' + [math]::Round($p.CPU-$c,2) + ' s (about 3 = one core pinned, likely hung); responding=' + $p.Responding")
        cpu = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception as e:
        cpu = "cpu check failed: %s" % e
    print(f"TIMEOUT after {tmo:.0f} s (queued={queued_seen}). started: {st}. {cpu}")
    print("Fusion may still be running the job: do not resend blindly. A hang after closing a drawing usually means a command was active; see SKILL.md.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
