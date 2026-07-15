# Overview of LeetGPU
LeetGPU (leetgpu.com) is a browser-based GPU programming platform — essentially "LeetCode for GPU kernels." It launched around January 2025 with the pitch of removing the hardware barrier to learning CUDA: no GPU is required, drivers don't need installing, and there's no queue for shared hardware — you write and run CUDA in the browser for free.

## Core tech
- **CPU-based GPU emulation, two modes:** a "functional" mode that executes code fast and returns program output, and a "cycle-accurate" mode that models real GPU architecture to estimate actual hardware runtime.
- The cycle-accurate simulator is built on Accel-Sim.
- It supports most of the core CUDA Runtime API and lets you simulate against a range of NVIDIA GPU models.

## Language/framework support
Started CUDA-only, then expanded — Mojo support was rolled out to all challenges, and later tinygrad support was added to all challenges as well. Community solution logs also show challenges solvable in **PyTorch and Triton**, so a given problem typically has starter templates across multiple frameworks — each challenge includes a problem description, reference implementation, test cases, and starter templates for multiple GPU programming frameworks.

## Product surface
- **Web playground** — write/compile/run kernels directly in-browser.
- **CLI** — a free CUDA Playground accessible from the command line to compile and run CUDA code locally, no GPU required, available on Linux, macOS, and Windows.
- **Challenges repo** — the problem set itself is open on GitHub (`AlphaGPU/leetgpu-challenges`), licensed CC BY-NC-ND 4.0, and open to community contributions/bug reports.
- **Discord community** for support and discussion around challenges.

## Positioning
It's aimed at people learning parallel/GPU programming without spending on cloud GPU rental — students, ML engineers picking up CUDA/Triton, and people doing "100 days of GPU programming"-style practice (a recurring theme in their social posts). Typical challenges: matrix transpose/multiply, elementwise ops, PyTorch model inference — ramping from basic kernels to more involved ML-adjacent problems.

One caveat worth noting for you as a dev: since it's CPU-emulated (not real silicon), the cycle-accurate timings are architectural estimates, not ground-truth benchmarks — fine for learning/correctness, less so for real perf tuning on production hardware.
