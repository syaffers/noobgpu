"""The `noobgpu` command: start the server and print where to find it."""

import argparse
import os
import socket
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


def lan_ip() -> str | None:
    """This machine's LAN address (no traffic is actually sent)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
    except OSError:
        return None


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

    print(BANNER)
    if args.host in ("0.0.0.0", "::"):
        print(f"  Local:   http://127.0.0.1:{args.port}")
        if ip := lan_ip():
            print(f"  Network: http://{ip}:{args.port}")
        print(
            "\n  Caution: NoobGPU has no authentication and runs submitted code.\n"
            "  Only bind all interfaces on networks you trust; for remote GPU\n"
            "  boxes prefer SSH port forwarding (see README)."
        )
    else:
        print(f"  Serving at http://{args.host}:{args.port}")
    print("  Press Ctrl+C to stop.\n")

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
