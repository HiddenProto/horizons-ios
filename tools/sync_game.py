"""Copy the live game out of ../Horizons into the app and pack it.

    python tools/sync_game.py

The game is developed in Documents/Horizons; this project never edits it. What ships is:
horizons.py + hz/*.py (minus the Tk watch window) + web/bridge.py, zipped to web/game.zip,
which the page unpacks into Pyodide's filesystem at boot. stuff/ is NOT copied - no saves,
and none of the spoiler docs.
"""
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(os.path.dirname(HERE), "Horizons")
DST = os.path.join(HERE, "game")
WEB = os.path.join(HERE, "web")
SKIP = {"watcher.py"}


def main():
    # CI has no ../Horizons next to it: there, pack the copy that was committed last time.
    n = 0
    if os.path.isdir(SRC) and "--pack-only" not in sys.argv:
        if os.path.isdir(DST):
            shutil.rmtree(DST)
        os.makedirs(os.path.join(DST, "hz"))
        shutil.copy2(os.path.join(SRC, "horizons.py"), DST)
        n = 1
        for f in sorted(os.listdir(os.path.join(SRC, "hz"))):
            if f.endswith(".py") and f not in SKIP:
                shutil.copy2(os.path.join(SRC, "hz", f), os.path.join(DST, "hz", f))
                n += 1
    shutil.copy2(os.path.join(WEB, "bridge.py"), DST)
    out = os.path.join(WEB, "game.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(DST):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, DST).replace(os.sep, "/"))
    print("synced %d game files + bridge -> %s (%d KB)" % (n, out, os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
