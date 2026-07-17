from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from noobgpu import __version__
from noobgpu.api import router
from noobgpu.challenges import find_challenges_root
from noobgpu.store import Store, default_db_path

PACKAGED_STATIC = Path(__file__).parent / "static"


def create_app(
    challenges_root: Path | None = None,
    db_path: Path | None = None,
    static_dir: Path | None = None,
) -> FastAPI:
    application = FastAPI(title="NoobGPU", version=__version__)
    application.state.challenges_root = challenges_root or find_challenges_root()
    application.state.store = Store(db_path or default_db_path())
    application.include_router(router)

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    # Serve the built frontend when present (packaged installs; `make dev`
    # uses Vite instead). Registered after the API routes, so /api wins;
    # unknown paths fall back to index.html for SPA routing.
    static = static_dir if static_dir is not None else PACKAGED_STATIC
    if static.is_dir():

        @application.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            candidate = static / path
            if path and ".." not in path and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(static / "index.html")

    return application


app = create_app()
