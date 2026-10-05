#!/usr/bin/env python3
"""Regenerate every drawing from design/parts.json: Blender views + views.json, verification, sheets 01-09.
Sheet 09 (full BOM) runs last: its "sheets" column reads the balloon registry that sheets 01-08 write.

    uv run -q --with matplotlib --with numpy --with pillow python design/draw/make_all.py
"""
import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
runpy.run_path(str(HERE / "views.py"), run_name="__main__")
r = subprocess.run([sys.executable, str(HERE / "verify_views.py")], capture_output=True, text=True)
print(r.stdout.splitlines()[-1] if r.stdout else r.stderr)
for s in ("sheet01_ga", "sheet02_barrel", "sheet03_drive", "sheet04_melt", "sheet05_tdie", "sheet06_feed_vacuum", "sheet07_pid",
          "sheet08_utilities", "sheet09_bom"):
    runpy.run_path(str(HERE / f"{s}.py"), run_name="__main__")
sys.exit(r.returncode)
