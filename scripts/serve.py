#!/usr/bin/env python3
"""Build site and serve locally; rebuild when data/ changes."""

from __future__ import annotations

import http.server
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WATCH_PATHS = [
    DATA_DIR / "shared.json",
    DATA_DIR / "publications.json",
    DATA_DIR / "zh",
    DATA_DIR / "en",
    ROOT / "templates",
    ROOT / "scripts" / "build.py",
]
PORT = 11454


def latest_mtime() -> float:
    latest = 0.0
    for path in WATCH_PATHS:
        if not path.exists():
            continue
        if path.is_file():
            latest = max(latest, path.stat().st_mtime)
            continue
        for file in path.rglob("*"):
            if file.is_file():
                latest = max(latest, file.stat().st_mtime)
    return latest


def run_build() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build.py")], check=True)


def main() -> None:
    run_build()
    last_mtime = latest_mtime()
    print(f"Serving at http://localhost:{PORT}/  (Ctrl+C to stop)")
    print("Watching data/ — saves trigger rebuild automatically.\n")

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(  # noqa: E731
        *args, directory=str(ROOT), **kwargs
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    server.timeout = 1

    try:
        while True:
            server.handle_request()
            current = latest_mtime()
            if current > last_mtime:
                last_mtime = current
                print("Data changed, rebuilding...")
                run_build()
                print(f"Rebuild done. Refresh http://localhost:{PORT}/\n")
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
