default:
    @just --list

# Run backend (:8000) and frontend (:5173) with hot reload
dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    (cd server && uv run uvicorn noobgpu.app:app --reload --port 8000) &
    (cd web && npm run dev) &
    wait

test:
    cd server && uv run pytest

lint:
    cd server && uv run ruff check .
    cd web && npm run lint

# Build the distributable wheel (frontend + challenges bundled)
build:
    cd web && npm run build
    rm -rf server/src/noobgpu/static server/src/noobgpu/data server/dist
    cp -r web/dist server/src/noobgpu/static
    mkdir -p server/src/noobgpu/data
    cp -r challenges server/src/noobgpu/data/challenges
    rm -rf server/src/noobgpu/data/challenges/*/.cache
    cd server && uv build --wheel
    @ls server/dist/*.whl
