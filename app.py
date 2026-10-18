#!/usr/bin/env python3
"""Root app.py entry point that delegates to app/app.py."""
import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import app

if __name__ == "__main__":
    app.main()
