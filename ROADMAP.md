# NoobGPU — Roadmap to v0.1.0

An open-source, local-first take on [LeetGPU](https://leetgpu.com): a challenge-based
CUDA playground that runs in your browser but executes on **your own machine**. If an
NVIDIA GPU is present, NoobGPU detects it and uses it as the runtime for submitted code.

**Decided (2026-07-16):**

| Decision        | Choice                                                                 |
| --------------- | ---------------------------------------------------------------------- |
| Languages (v1)  | CUDA C++ only                                                          |
| No-GPU fallback | None — v1 requires an NVIDIA GPU + CUDA toolkit; app degrades gracefully with a clear "GPU required" state |
| Backend         | Python + FastAPI                                                       |
| Isolation       | Subprocess with `rlimit` caps + wall-clock timeout, behind a `Runner` interface; optional `DockerRunner` is post-1.0 |
| Challenge content | Original — LeetGPU's challenge repo is CC BY-NC-ND 4.0, so no derivation. Same spirit, our own problem text, tests, and starter code |

## Product definition

One sentence: *open a terminal, run `noobgpu`, open the printed URL in a browser to get
a LeetGPU-style challenge workspace, and Run/Submit executes CUDA on your GPU in under a
second of overhead.*

The differentiator vs LeetGPU is the inverse of their pitch: they remove the hardware
barrier via CPU emulation, so their timings are architectural estimates. NoobGPU assumes
you *have* the hardware — kernel times are ground truth, measured on real silicon.

**v1 features (and nothing more):**

1. **Challenge browser** — grid of challenge cards with title, difficulty badge, blurb;
   search box and All/Easy/Medium/Hard filter.
2. **Challenge workspace** — split view: problem statement (description, requirements,
   examples, constraints) on the left; Monaco code editor with CUDA starter template on
   the right; console output panel below the editor.
3. **Run** — compile + execute against the challenge's *sample* tests, stream compiler
   errors and program output to the console panel.
4. **Submit** — compile + execute against the *full hidden* test suite; verdict
   (Accepted / Wrong Answer / Compile Error / Runtime Error / Time Limit Exceeded),
   measured GPU kernel time on accept.
5. **Submissions history** — per-challenge list of past submissions with verdict, time,
   and the code as submitted (stored in SQLite).
6. **GPU runtime indicator** — header badge showing the detected GPU name; clicking it
   opens a spec sheet modal (memory, SM count, compute capability, etc., read live from
   the driver — not a static table).
7. **Editor persistence** — work-in-progress code survives reloads (saved per challenge).

**Explicit non-goals for v1** (each is a scope trap; revisit post-1.0):
accounts/auth, leaderboards, community solutions, CPU emulation of CUDA, languages other
than CUDA C++, cycle-accurate performance modeling, multi-GPU selection, Windows-native
support (Linux first; Windows via WSL2), cloud execution.

## Architecture

```
┌────────────────────────────────────────────────┐
│  Browser: React + TypeScript SPA               │
│  (Vite, Monaco editor, Tailwind, dark theme)   │
└───────────────▲────────────────────────────────┘
                │ REST + SSE (streamed run output)
┌───────────────┴────────────────────────────────┐
│  noobgpu server: FastAPI (single process)      │
│  ├─ api/          routes, SSE streaming        │
│  ├─ challenges/   loader for challenge packs   │
│  ├─ judge/        orchestrates compile→run→diff│
│  ├─ runner/       Runner interface             │
│  │    └─ SubprocessRunner (rlimit + timeout)   │
│  ├─ gpu/          detection via NVML           │
│  └─ store/        SQLite (submissions, drafts) │
└───────────────┬────────────────────────────────┘
                │ subprocess
        nvcc ──► compiled binary ──► your GPU
```

**Key contracts (defined once in M1/M2, everything else builds on them):**

- **`Runner` interface** — `run(cmd, workdir, limits) -> RunResult{exit_code, stdout,
  stderr, duration, timed_out}`. The only place code execution happens. `DockerRunner`
  slots in here later without touching the judge.
- **Challenge pack format** — one directory per challenge:
  `challenge.toml` (id, title, difficulty, limits, tolerance) + `description.md` +
  `starter.cu` + `reference.cu` (a known-good solution: generates expected test outputs
  at pack-build time and anchors the judge's end-to-end tests) + `harness.cu` (owns
  `main()`, calls the user's `solve()`) + `tests/` (sample + hidden case inputs;
  expected outputs derived from the reference). Challenges are data, not code paths —
  adding one requires zero backend changes.
- **Judge protocol** — harness prints one JSON line per test (pass/fail, max abs error,
  kernel ms via CUDA events); judge aggregates into a verdict. User code never controls
  the verdict format because the harness owns `main()` and output goes to a pipe the
  harness controls.

**Stack rationale:** Python owns the GPU tooling world and keeps the runner/judge
readable and hackable. Snappiness lives in the frontend: the SPA is static files served
by FastAPI, all state transitions are optimistic, and run output streams over SSE so the
console starts printing the moment nvcc speaks.

## Milestones

Each milestone is shippable and demoable on its own. "Done when" is the accountability
line — if it isn't true, the milestone isn't done.

### M0 — Skeleton (small) — ✅ done 2026-07-16
Repo scaffolding: git init, `server/` (uv, ruff, pytest, FastAPI health route),
`web/` (Vite + React + TS + Tailwind + oxlint), `challenges/` dir, Makefile for
`dev`, `test`, `lint`, `build`. GitHub Actions running lint + tests on both halves.

**Done when:** `make dev` starts backend and frontend with hot reload; CI is green on a
trivial test in each half. *(Verified: proxy `/api` works end-to-end locally; first
GitHub Actions run green on both jobs.)*

### M1 — Runner core (medium) — ✅ done 2026-07-16
No UI. GPU detection via NVML (`nvidia-ml-py`): name, memory, compute capability,
driver version (SM count isn't exposed by NVML — deferred to the M4 spec modal via a
different source). `SubprocessRunner`: temp workdir, `setrlimit` (CPU, file size),
wall-clock timeout with process-tree kill. No address-space cap — the CUDA runtime
reserves huge virtual ranges, so `RLIMIT_AS` breaks every GPU binary. Compile step
(`nvcc -arch=native` with captured diagnostics) and execute step. Structured
`RunResult`. A throwaway CLI (`python -m noobgpu.judge <file.cu>`) for exercising it.

**Done when:** the CLI compiles and runs a vector-add `.cu` file on the real GPU and
prints a structured result; an infinite-loop kernel is killed at the timeout; a missing
GPU or missing `nvcc` produces a distinct, typed error. *(Verified on RTX 5050: 12
tests pass — 4 GPU-marked e2e, auto-skipped where no GPU, so CI stays honest.)*

### M2 — Challenges + judge (medium) — ✅ done 2026-07-16
Challenge pack format and loader (with schema validation and good error messages for
malformed packs). Harness convention (`solve()` entry point, JSON-per-test output,
CUDA-event timing), documented in `challenges/README.md`; shared helpers live in
`challenges/_common/noobgpu_harness.h`. Judge: compile once, run per test, compare with
per-challenge float tolerance, aggregate verdict (Accepted / Wrong Answer / Compile
Error / Runtime Error / Time Limit Exceeded), stop at first failure. Expected outputs
are generated lazily from `reference.cu` into a content-addressed `.cache/`. **Five
seed challenges**: Vector Addition, Matrix Transpose, ReLU, Reverse Array, Matrix
Multiplication.

**Done when:** for every seed challenge, a known-good solution gets Accepted and a
deliberately wrong one gets Wrong Answer, verified by pytest running the real judge
end-to-end on the GPU. *(Verified on RTX 5050: 38 tests pass, covering all five
verdicts, sample-only runs, and cache reuse.)*

### M3 — API layer (small) — ✅ done 2026-07-16
FastAPI routes: `GET /api/challenges`, `GET /api/challenges/{id}`, `POST .../run`
(sample tests, SSE stream of compile output + per-test events), `POST .../submit`
(all tests, SSE, persists result), `GET .../submissions`, `GET /api/submissions/{id}`,
`GET /api/gpu`, draft save/load endpoints. SQLite via raw `sqlite3` (open question 3
resolved — see `store.py`). The judge emits progress events through an `on_event`
callback; the API bridges them to SSE via a worker thread + queue. `create_app()`
factory keeps tests hermetic; config via `NOOBGPU_CHALLENGES_DIR` / `NOOBGPU_DB`.

**Done when:** the full challenge lifecycle works from `curl`/httpie alone, including
watching an SSE stream during a run; submissions survive a server restart. *(Verified
with curl end-to-end: live SSE stream on submit, submission listed after a fresh server
process on the same DB. 49 tests pass.)*

### M4 — Workspace UI (large) — ✅ done 2026-07-16
The core screen, mirroring the LeetGPU workspace layout: header (logo, GPU badge, Run,
Submit, temporary challenge dropdown until M5's list page), left panel rendering
`description.md` (markdown via react-markdown + remark-gfm; math deferred until a
challenge needs it), right panel Monaco (bundled locally, no CDN — offline-first) with
C++ syntax + starter code + Reset button, bottom console streaming SSE output with
compile errors and verdicts styled distinctly. GPU spec modal fed by `/api/gpu`. Draft
autosave (debounced, forced before run/submit). Ctrl/Cmd+Enter runs.

**Done when:** you can solve Vector Addition start-to-finish in the browser — see the
problem, edit code, watch a failing run stream in, fix it, submit, get Accepted with a
kernel time — without touching a terminal. *(Verified in headless Chromium: starter →
Wrong Answer, fixed in-editor → Accepted with kernel time, draft survives reload, GPU
modal renders, zero console errors.)*

### M5 — Browser + submissions UI (medium) — ✅ done 2026-07-17
Challenge list page (cards, search, difficulty filter), react-router routing between
list and workspace, Submissions tab in the workspace (verdict history, click to
view/restore that code). `/api/gpu` gained `nvcc` status so the UI distinguishes the
failure causes. Error states: no GPU detected and `nvcc` missing render a guidance
banner with Run/Submit disabled; server unreachable renders a full retry screen.

**Done when:** the full LeetGPU-style flow (browse → filter → open → solve → review past
submissions → restore old code) works, and pulling the GPU/toolkit out from under the app
shows guidance instead of a broken page. *(Verified in headless Chromium: whole flow
end-to-end; nvcc state tested against a real stripped-PATH server; no-GPU state via a
stubbed /api/gpu response — a driverless environment can't be produced on this machine.)*

### M6 — Release v0.1.0 (medium) — ✅ done 2026-07-17
*(Descoped 2026-07-17: ships with the five M2 challenges; the five additional ones —
Matrix Addition, Leaky ReLU, 1D Convolution, Color Inversion, Reduction/Sum — moved to
the post-1.0 backlog.)* Packaging: `make build` bundles the built frontend and the
challenge packs into the wheel; the `noobgpu` command serves UI + API + judge from one
process (SPA fallback, packaged-challenges fallback, expected-output cache redirected
to `~/.cache/noobgpu`) and prints the serving URL. README with a screenshot-led quickstart,
CONTRIBUTING with a "write a challenge pack" guide, LICENSE (MIT for code; challenges
CC BY 4.0 so others *can* reuse ours), CHANGELOG, tagged v0.1.0.

**Done when:** a stranger with an NVIDIA GPU, CUDA toolkit, and `uv` installed goes from
zero to an Accepted submission using only the README — tested by actually doing this in a
clean VM/machine. *(Approximated on this machine: wheel installed into a fresh
`uv tool` environment, run from `$HOME` with the cache wiped — UI served, packaged
challenges listed, submission Accepted. The install test caught and fixed two real
bugs: missing `parents=True` on first cache creation, and SSE streams ending silently
on unexpected judge exceptions. A true clean-VM pass still deserves a run before
announcing the release.)*

### Post-1.0 backlog (recorded, not committed)
Five more challenges (Matrix Addition, Leaky ReLU, 1D Convolution, Color Inversion,
Reduction/Sum — descoped from M6),
Triton and PyTorch runtimes (revisits the CPU-fallback question), `DockerRunner` for
untrusted code, free-form playground page (compile/run arbitrary `.cu` with no judge —
M1's runner already does the work), first-class `noobgpu run file.cu` CLI (promote M1's
throwaway judge CLI), community challenge-pack index, local performance leaderboard
(best kernel ms per challenge), multi-GPU selection, Windows-native runner,
CUDA-simulator integration for GPU-less machines.

## Open questions (fine to defer, listed for accountability)

1. ~~**Kernel timing semantics**~~ — decided in M2: CUDA events around the `solve()`
   call only; harness H2D/D2H copies are excluded. Reported per test; the summary
   `kernel_ms` is the max across tests (the largest test dominates).
2. ~~**Resource limits per challenge**~~ — decided in M2: judge defaults with optional
   `[limits]` overrides (`wall_time_s`, `cpu_time_s`) in `challenge.toml`.
3. ~~**SQLModel vs raw sqlite3**~~ — decided in M3: raw `sqlite3`. Two small tables
   don't justify a SQLAlchemy dependency; the whole schema is one visible string in
   `store.py`, and per-operation connections give thread safety without locks.
   (Deviation note: decided by inspection rather than writing both versions — the
   comparison was lopsided enough not to warrant the exercise.)
4. ~~**Frontend state**~~ — decided in M4: plain React hooks, no state library. The
   workspace's real state is one challenge, one code string, one event list, and a few
   booleans — a store would be ceremony. Revisit only if M5 routing shows real
   prop-drilling pain.
