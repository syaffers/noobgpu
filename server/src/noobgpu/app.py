from fastapi import FastAPI

from noobgpu import __version__

app = FastAPI(title="NoobGPU", version=__version__)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
