"""StemClaw entry point: python -m stemclaw."""

import os
import sys

# Ensure UTF-8 and VT100 ANSI processing on Windows consoles
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    os.system("")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from stemclaw.cli import main

if __name__ == "__main__":
    sys.exit(main())
