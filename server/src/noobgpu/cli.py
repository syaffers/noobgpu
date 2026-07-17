"""The `noobgpu` command: start the server and print where to find it."""

import argparse
import os
from pathlib import Path

import uvicorn

from noobgpu.app import create_app

# Generated with https://manytools.org/hacker-tools/ascii-banner/ (3D-ASCII font).
BANNER = r"""
 ________   ________  ________  ________  ________  ________  ___  ___
|\   ___  \|\   __  \|\   __  \|\   __  \|\   ____\|\   __  \|\  \|\  \
\ \  \\ \  \ \  \|\  \ \  \|\  \ \  \|\ /\ \  \___|\ \  \|\  \ \  \\\  \
 \ \  \\ \  \ \  \\\  \ \  \\\  \ \   __  \ \  \  __\ \   ____\ \  \\\  \
  \ \  \\ \  \ \  \\\  \ \  \\\  \ \  \|\  \ \  \|\  \ \  \___|\ \  \\\  \
   \ \__\\ \__\ \_______\ \_______\ \_______\ \_______\ \__\    \ \_______\
    \|__| \|__|\|_______|\|_______|\|_______|\|_______|\|__|     \|_______|
"""


def _default_cache_dir() -> Path:
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_home / "noobgpu"


def display_host(host: str) -> str:
    """A host you can actually put in a browser (0.0.0.0/:: are bind addresses)."""
    return "127.0.0.1" if host in ("0.0.0.0", "::") else host


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="noobgpu", description="Local-first CUDA challenge playground"
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Keep the expected-output cache out of site-packages for installed copies.
    os.environ.setdefault("NOOBGPU_CACHE_DIR", str(_default_cache_dir()))

    app = create_app()
    url = f"http://{display_host(args.host)}:{args.port}"

    print(BANNER)
    print(f"  Serving at {url}")
    if args.host in ("0.0.0.0", "::"):
        print(
            "  Listening on all interfaces — also reachable via this"
            f" machine's network address, port {args.port}."
        )
    print("  Press Ctrl+C to stop.\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
