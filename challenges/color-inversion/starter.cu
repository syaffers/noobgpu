#include <cuda_runtime.h>

// THE KERNEL — runs on the GPU, one thread per channel value (4 values per pixel).
// Red/green/blue flip to 1 - value; alpha is copied through unchanged.
__global__ void invert(const float* input, float* output, int N) {
    // 1. Compute this thread's index from blockIdx/blockDim/threadIdx.
    // 2. Guard against i >= N.
    // 3. Every 4th value starting at 3 (i % 4 == 3) is alpha: copy it.
    //    The other three become 1.0f - input[i].
}

// SOLVE — runs on the CPU; the judge calls it with device pointers that
// already hold the input. Pick a block size, compute how many blocks cover
// all N values (round UP!), and launch:
//   invert<<<blocks, threads>>>(input, output, N);
// (New here? See the Guide, top right.)
extern "C" void solve(const float* input, float* output, int N) {
}
