from pathlib import Path

from fastapi import FastAPI

from noobgpu import __version__
from noobgpu.api import router
from noobgpu.challenges import find_challenges_root
from noobgpu.store import Store, default_db_path


def create_app(
    challenges_root: Path | None = None, db_path: Path | None = None
) -> FastAPI:
    application = FastAPI(title="NoobGPU", version=__version__)
    application.state.challenges_root = challenges_root or find_challenges_root()
    application.state.store = Store(db_path or default_db_path())
    application.include_router(router)

    @application.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    return application


app = create_app()
