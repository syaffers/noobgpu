# Changelog

## Unreleased

- Onboarding guide page (`/guide`) with a line-by-line first-kernel walkthrough;
  easy-challenge starters rewritten with teaching comments.
- `noobgpu` prints a startup banner and the serving URL instead of auto-opening
  a browser (auto-open fell back to console browsers like lynx in sessions
  without a graphical display). The `--no-browser` flag is gone accordingly.

## 0.1.0 — 2026-07-17

First release.

- **Workspace**: LeetGPU-style split view — problem statement, Monaco editor with
  CUDA starter code, streaming console (SSE) with per-test results and verdicts.
- **Judge**: submissions compile with `nvcc -arch=native` and run on the local
  NVIDIA GPU under a subprocess sandbox (rlimits + wall-clock timeout). Verdicts:
  Accepted / Wrong Answer / Compile Error / Runtime Error / Time Limit Exceeded.
  Kernel time measured with CUDA events around `solve()` only.
- **Challenges**: five original packs — Vector Addition, Matrix Transpose, ReLU,
  Reverse Array, Matrix Multiplication (CC BY 4.0). Packs are pure data; expected
  outputs are generated from each pack's reference solution into a
  content-addressed cache.
- **Browser**: challenge list with search + difficulty filters; submissions
  history with code restore; drafts autosave and survive restarts (SQLite).
- **Failure states**: guidance screens for no GPU, missing CUDA toolkit, and
  server unreachable.
- **Packaging**: `make build` produces a wheel bundling the frontend and
  challenge packs; `noobgpu` starts the server and opens the browser.
