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

One sentence: *open a terminal, run `noobgpu`, a browser tab opens with a LeetGPU-style
challenge workspace, and Run/Submit executes CUDA on your GPU in under a second of overhead.*

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

### M0 — Skeleton (small)
Repo scaffolding: git init, `server/` (uv, ruff, pytest, FastAPI hello route),
`web/` (Vite + React + TS + Tailwind + ESLint), `challenges/` dir, Makefile/justfile
for `dev`, `test`, `build`. GitHub Actions running lint + tests on both halves.

**Done when:** `just dev` starts backend and frontend with hot reload; CI is green on a
trivial test in each half.

### M1 — Runner core (medium)
No UI. GPU detection via NVML (`pynvml`): name, memory, compute capability, SM count,
driver version. `SubprocessRunner`: temp workdir, `setrlimit` (CPU, address space, file
size), wall-clock timeout with process-tree kill. Compile step (`nvcc` invocation with
captured diagnostics) and execute step. Structured `RunResult`. A throwaway CLI
(`python -m noobgpu.judge <file.cu>`) for exercising it.

**Done when:** the CLI compiles and runs a vector-add `.cu` file on the real GPU and
prints a structured result; an infinite-loop kernel is killed at the timeout; a missing
GPU or missing `nvcc` produces a distinct, typed error.

### M2 — Challenges + judge (medium)
Challenge pack format and loader (with schema validation and good error messages for
malformed packs). Harness convention (`solve()` entry point, JSON-per-test output,
CUDA-event timing). Judge: compile once, run per test, compare with per-challenge float
tolerance, aggregate verdict. **Five seed challenges**: Vector Addition, Matrix
Transpose, ReLU, Reverse Array, Matrix Multiplication.

**Done when:** for every seed challenge, a known-good solution gets Accepted and a
deliberately wrong one gets Wrong Answer, verified by pytest running the real judge
end-to-end on the GPU.

### M3 — API layer (small)
FastAPI routes: `GET /api/challenges`, `GET /api/challenges/{id}`, `POST .../run`
(sample tests, SSE stream of compile output + per-test events), `POST .../submit`
(hidden tests, SSE, persists result), `GET .../submissions`, `GET /api/gpu`,
draft save/load endpoints. SQLite via a thin layer (SQLModel or raw `sqlite3` — decide
in-milestone, whichever reads better). OpenAPI docs come free from FastAPI.

**Done when:** the full challenge lifecycle works from `curl`/httpie alone, including
watching an SSE stream during a run; submissions survive a server restart.

### M4 — Workspace UI (large)
The core screen, mirroring the LeetGPU workspace layout: header (logo, GPU badge, Run,
Submit), left panel rendering `description.md` (markdown + math), right panel Monaco with
CUDA syntax + starter code + Reset button, bottom console streaming SSE output with
compile errors and verdicts styled distinctly. GPU spec modal fed by `/api/gpu`. Draft
autosave. Keyboard shortcut for Run.

**Done when:** you can solve Vector Addition start-to-finish in the browser — see the
problem, edit code, watch a failing run stream in, fix it, submit, get Accepted with a
kernel time — without touching a terminal.

### M5 — Browser + submissions UI (medium)
Challenge list page (cards, search, difficulty filter), routing between list and
workspace, Submissions tab in the workspace (verdict history, click to view/restore that
code). Empty/error states: no GPU detected, `nvcc` missing, server unreachable — each
with a screen that says what to do about it.

**Done when:** the full LeetGPU-style flow (browse → filter → open → solve → review past
submissions → restore old code) works, and pulling the GPU/toolkit out from under the app
shows guidance instead of a broken page.

### M6 — Release v0.1.0 (medium)
Grow to **10 challenges** (add: Matrix Addition, Leaky ReLU, 1D Convolution, Color
Inversion, Reduction/Sum). Packaging: frontend built into the Python package as static
files; `uvx noobgpu` (or `pipx run noobgpu`) starts the server and opens the browser.
README with a screenshot-led quickstart, CONTRIBUTING with a "write a challenge pack"
guide, LICENSE (MIT for code; challenges CC BY 4.0 so others *can* reuse ours), CHANGELOG,
tagged GitHub release.

**Done when:** a stranger with an NVIDIA GPU, CUDA toolkit, and `uv` installed goes from
zero to an Accepted submission using only the README — tested by actually doing this in a
clean VM/machine.

### Post-1.0 backlog (recorded, not committed)
Triton and PyTorch runtimes (revisits the CPU-fallback question), `DockerRunner` for
untrusted code, free-form playground page (compile/run arbitrary `.cu` with no judge —
M1's runner already does the work), first-class `noobgpu run file.cu` CLI (promote M1's
throwaway judge CLI), community challenge-pack index, local performance leaderboard
(best kernel ms per challenge), multi-GPU selection, Windows-native runner,
CUDA-simulator integration for GPU-less machines.

## Open questions (fine to defer, listed for accountability)

1. **Kernel timing semantics** — time only the `solve()` call via CUDA events (fair,
   excludes H2D/D2H copies the harness performs)? Proposed: yes; decide in M2.
2. **Resource limits per challenge** — global defaults with per-challenge overrides in
   `challenge.toml`? Proposed: yes; decide in M2.
3. **SQLModel vs raw sqlite3** — decide in M3 by writing the submissions table both ways
   and keeping the more readable one.
4. **Frontend state** — plain React Query + context vs a store like Zustand; decide in
   M4 once the workspace's real state shape exists.
