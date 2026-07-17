# Contributing to NoobGPU

## Dev setup

Requirements: Linux, an NVIDIA GPU + driver, CUDA toolkit (`nvcc`),
[uv](https://docs.astral.sh/uv/), Node.js.

```bash
git clone https://github.com/syaffers/noobgpu.git
cd noobgpu
make dev     # backend :8000 + frontend :5173, hot reload on both
make test    # server tests; GPU-marked tests auto-skip without a GPU
make lint
```

Conventions: conventional commits (`feat:`, `fix:`, `docs:`, …); CI must be green;
milestone progress is tracked in [ROADMAP.md](ROADMAP.md).

## Writing a challenge pack

Challenges are data — a new pack needs **zero backend changes**. Copy an existing
pack (e.g. `challenges/relu/`) and adapt:

```
challenges/my-challenge/
├── challenge.toml    id (= directory name), title, difficulty, tolerance, tests
├── description.md    problem statement (markdown)
├── starter.cu        template with an empty solve() the user fills in
├── reference.cu      your known-good solution — generates expected outputs
└── harness.cu        owns main(); calls solve(); ~40 lines using the shared header
```

The full format and harness contract are documented in
[challenges/README.md](challenges/README.md). The important rules:

1. **The harness owns `main()` and stdout.** User code only provides `solve()`, so
   it can never fake a verdict.
2. **Inputs are generated deterministically** from each test's `args` via
   `harness_gen_floats(n, seed)` — gen and check runs must see identical data.
3. **Time only `solve()`** with `HarnessTimer` (CUDA events).
4. **Zero output buffers** with `cudaMemset` before calling `solve()` so stale
   device memory can't accidentally pass a do-nothing submission.
5. Include at least one `sample = true` test (used by Run) and one hidden test
   (Submit judges all of them).

Verify your pack before opening a PR:

```bash
cd server
uv run python -m noobgpu.judge submit my-challenge ../challenges/my-challenge/reference.cu
# expect: "verdict": "accepted"
uv run pytest tests/test_challenges.py   # loader validation
```

Add a deliberately wrong solution to `server/tests/data/wrong/my-challenge.cu` and
extend the pack test parametrization if you want it covered by CI's GPU-machine runs
(see `server/tests/test_judge_packs.py` — the test discovers packs automatically).

Challenge content is licensed CC BY 4.0; by contributing a pack you agree to that.
All challenges must be original work — don't port content from LeetGPU or other
copyrighted problem sets.
