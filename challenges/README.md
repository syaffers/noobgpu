# Challenge packs

One directory per challenge. Challenges are data: adding a pack requires zero
backend changes. All challenges here are original work, licensed CC BY 4.0.

## Pack layout

```
my-challenge/
├── challenge.toml    id, title, difficulty, tolerance, limits, test cases
├── description.md    problem statement shown in the UI
├── starter.cu        template the user starts from (defines solve())
├── reference.cu      known-good solution; generates expected test outputs
├── harness.cu        owns main(); calls the user's solve()
└── .cache/           expected outputs, generated lazily (gitignored)
```

## challenge.toml

```toml
id = "my-challenge"        # must match the directory name
title = "My Challenge"
difficulty = "easy"        # easy | medium | hard
tolerance = 1e-5           # max absolute error allowed per element

[limits]                   # optional; overrides judge defaults
wall_time_s = 5.0

[[tests]]
name = "sample-16"
sample = true              # sample tests run on "Run"; all tests on "Submit"
args = [16, 1]             # integers passed to the harness (meaning is per-pack)
```

## Harness contract

`harness.cu` includes `_common/noobgpu_harness.h` and is compiled together
with a solution (`nvcc -O2 -arch=native -I _common harness.cu solution.cu`).
The judge invokes the binary as:

```
program gen   <expected-file> <tolerance> <args...>   # reference build: write expected output
program check <expected-file> <tolerance> <args...>   # submission build: compare + report
```

In check mode the harness prints exactly one JSON line:

```
{"pass": true, "max_abs_err": 0, "kernel_ms": 0.014}
```

Rules the harness must follow:

- Generate inputs deterministically from the test args via `harness_gen_floats`
  (seeded xorshift64*), so gen and check runs see identical data.
- Time **only the `solve()` call** with `HarnessTimer` (CUDA events); host
  copies are excluded from `kernel_ms`.
- The harness owns `main()` and stdout; user code only provides `solve()`,
  so a submission cannot fake a verdict.
- Exit 0 when the harness completes (even on a failed comparison); exit 2 on
  CUDA/setup errors.
