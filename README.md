# NoobGPU

**A local-first CUDA challenge playground.** Solve LeetCode-style GPU programming
challenges in your browser, with every submission compiled by `nvcc` and executed on
**your own NVIDIA GPU** — kernel times are ground truth, measured on real silicon with
CUDA events.

![The NoobGPU workspace: problem statement, CUDA editor, and streaming console](docs/img/workspace.png)

## What you get

- **Challenge workspace** — problem statement, Monaco editor with a CUDA starter
  template, and a console that streams compiler output and per-test results live.
- **Run vs Submit** — Run checks the sample tests; Submit judges the full suite and
  records the verdict (Accepted, Wrong Answer, Compile Error, Runtime Error, Time
  Limit Exceeded) with the measured kernel time.
- **Submissions history** — every submission is stored locally in SQLite; view old
  code and restore it to the editor.
- **Honest timing** — the judge times only your `solve()` call via CUDA events;
  host-side copies are excluded.
- Your code never leaves your machine.

![Challenge browser with difficulty filters](docs/img/challenges.png)

## Requirements

- Linux (Windows works via WSL2)
- An NVIDIA GPU with a recent driver (`nvidia-smi` should work)
- CUDA toolkit (`nvcc` on PATH)
- [uv](https://docs.astral.sh/uv/), [Node.js](https://nodejs.org), and
  [just](https://github.com/casey/just) (to build)

## Quickstart

```bash
git clone https://github.com/syaffers/noobgpu.git
cd noobgpu
just build                    # builds the frontend + a wheel with everything bundled
uv tool install ./server/dist/noobgpu-0.1.0-py3-none-any.whl
noobgpu                       # starts the server — open the printed URL in your browser
```

`noobgpu` serves everything from one process — UI, API, judge — and works from any
directory. Flags: `--port`, `--host`.

## Using a remote GPU box

Running NoobGPU on a cloud GPU instance (say, a T4 on AWS)? Don't expose it to the
internet — it has no authentication and it exists to compile and run submitted code.
Keep the default `127.0.0.1` binding on the remote machine and tunnel to it with SSH
port forwarding:

```bash
ssh -L 8000:localhost:8000 user@your-gpu-box   # from your laptop
# on the remote box:
noobgpu
# then browse http://localhost:8000 on your laptop
```

`--host 0.0.0.0` is for networks you trust (e.g., reaching your desktop's GPU from
another machine at home); the CLI prints both the local and network URLs when you use
it. Note that on cloud instances the printed network address is the *private* one —
one more reason the SSH tunnel is the right tool there.

## Development

```bash
just dev     # backend :8000 + frontend :5173 with hot reload
just test    # server test suite (GPU tests auto-skip without a GPU)
just lint    # ruff + oxlint
```

The repo layout: `server/` (FastAPI + judge), `web/` (React + Monaco), `challenges/`
(challenge packs — data, not code). See [ROADMAP.md](ROADMAP.md) for where the project
is headed and [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a challenge.

## How judging works

Each challenge pack ships a `harness.cu` that owns `main()` and a `reference.cu` known-
good solution. Your submission only provides `solve()` — it's compiled together with
the harness, run against deterministic generated inputs, and compared to the
reference's output within a per-challenge tolerance. Expected outputs are cached
content-addressed, so editing a pack invalidates them automatically. Details in
[challenges/README.md](challenges/README.md).

## License

Code is [MIT](LICENSE). Challenge content (`challenges/`) is
[CC BY 4.0](challenges/LICENSE) — reuse it, with attribution.

NoobGPU is an independent open-source project inspired by
[LeetGPU](https://leetgpu.com); it shares no code or challenge content with it.
