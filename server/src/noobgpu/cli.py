"""The `noobgpu` command: start the server and open the workspace."""

import argparse
import os
import threading
import webbrowser
from pathlib import Path

import uvicorn

from noobgpu.app import create_app


def _default_cache_dir() -> Path:
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_home / "noobgpu"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="noobgpu", description="Local-first CUDA challenge playground"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true", help="don't open a browser tab")
    args = parser.parse_args()

    # Keep the expected-output cache out of site-packages for installed copies.
    os.environ.setdefault("NOOBGPU_CACHE_DIR", str(_default_cache_dir()))

    app = create_app()
    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, [url]).start()
    print(f"NoobGPU serving on {url}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
