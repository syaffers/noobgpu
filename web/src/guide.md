# Your first CUDA kernel

New to GPU programming? This page walks through one complete solution, line by
line, so the challenge templates make sense. It uses a task even simpler than
Vector Addition: **double every element of an array**.

## The two halves of every solution

Every NoobGPU challenge asks you to fill in two things, and they run in two
different places:

1. **The kernel** — a function marked `__global__` that runs **on the GPU**.
   The GPU runs *thousands of copies of it at once*, and each copy (a
   *thread*) handles a tiny piece of the work — usually one array element.
2. **`solve()`** — a normal C++ function that runs **on the CPU**. The judge
   calls it after copying the input data onto the GPU for you. Its job is to
   *launch* the kernel: decide how many threads to start, arranged how.

You never write `main()`, never allocate GPU memory, never copy data in these
challenges — the judge's harness does all of that. `solve()` receives
**device pointers** (memory that lives on the GPU) that are ready to use.

## A complete solution, annotated

```cuda
#include <cuda_runtime.h>

// Runs on the GPU. Each thread doubles ONE element.
__global__ void double_all(const float* in, float* out, int n) {
    // Which element am I? Threads are grouped into blocks, so my global
    // index is: (my block) x (threads per block) + (my slot in the block).
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    // The guard. We always launch a few more threads than n (see below),
    // so threads past the end must do nothing — or they'd write out of
    // bounds and corrupt memory.
    if (i < n) {
        out[i] = 2.0f * in[i];
    }
}

// Runs on the CPU. The judge calls this with device pointers.
extern "C" void solve(const float* in, float* out, int n) {
    // You pick threads-per-block. 256 is a solid default.
    int threads = 256;

    // Enough blocks to cover all n elements, rounding UP. This ceil-division
    // idiom appears in almost every CUDA program you will ever read:
    // for n = 1000 and threads = 256, (1000 + 255) / 256 = 4 blocks
    // = 1024 threads — 24 spare threads that the guard turns away.
    int blocks = (n + threads - 1) / threads;

    // The launch. <<<blocks, threads>>> is CUDA syntax for "start this many
    // copies of the kernel on the GPU".
    double_all<<<blocks, threads>>>(in, out, n);
}
```

That's the entire pattern. Vector Addition is this exact program with
`a[i] + b[i]` instead of `2.0f * in[i]`.

## Why do I write the launch myself?

Because it's half of what CUDA programming *is*. The launch configuration is
a real decision, and it grows with the challenges:

- 1D problems (vectors): one number per dimension, like above.
- 2D problems (matrices): `dim3 threads(16, 16)` and a 2D grid, so threads map
  naturally onto rows and columns.
- Multi-step problems (reductions, softmax): `solve()` launches *several*
  kernels in sequence.

The block size also affects speed — the kernel time NoobGPU reports is a
scoreboard for exactly these choices.

## Run, Submit, and verdicts

- **Run** (Ctrl/Cmd+Enter) compiles your code and runs the *sample* tests —
  fast feedback while you iterate.
- **Submit** runs every test, records the attempt under the Submissions tab,
  and reports your kernel time (measured on the GPU with CUDA events, copies
  excluded).
- Verdicts: **Accepted**, **Wrong Answer** (output mismatch — check the max
  abs error shown), **Compile Error** (nvcc's message appears in the console),
  **Runtime Error** (your code crashed), **Time Limit Exceeded** (likely a
  hang or a grid that's far too small doing serial work).

## The five classic beginner bugs

1. **Missing guard** — no `if (i < n)`: out-of-bounds writes, corrupt output,
   or a crash.
2. **Rounding the grid down** — `n / threads` instead of the ceil-division:
   the tail of the array is never touched. (Our tests use odd sizes like
   65,537 specifically to catch this.)
3. **Forgetting the launch** — an empty `solve()` compiles fine and fails
   every test: the output buffer just stays zeroed.
4. **Swapping rows and columns** in 2D index math — transpose will teach you
   this one personally.
5. **Racing against yourself** — in-place challenges (Reverse Array) need
   care that two threads don't stomp each other's reads; think about which
   thread reads and writes which element.

Pick an easy challenge, keep this page open in a second tab, and go get your
first **Accepted**.
