.PHONY: dev test lint build

dev: ## Run backend (:8000) and frontend (:5173) with hot reload
	@trap 'kill 0' EXIT; \
	(cd server && uv run uvicorn noobgpu.app:app --reload --port 8000) & \
	(cd web && npm run dev) & \
	wait

test:
	cd server && uv run pytest

lint:
	cd server && uv run ruff check .
	cd web && npm run lint

build:
	cd web && npm run build
