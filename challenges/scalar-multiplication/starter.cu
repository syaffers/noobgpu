#include <cuda_runtime.h>

// THE KERNEL — runs on the GPU. Thousands of copies execute at once;
// each copy (thread) should compute exactly ONE element of C.
__global__ void scalar_mul(const float* A, float* C, int N, float scalar) {
    // 1. Work out which element this thread owns:
    //      int i = blockIdx.x * blockDim.x + threadIdx.x;
    // 2. Guard against threads past the end of the array (i >= N).
    // 3. Write C[i] = A[i] * scalar.
}

// SOLVE — runs on the CPU. The judge calls it with device pointers that
// already hold the input data; you own the kernel launch. Pick a block
// size, compute how many blocks cover N elements (round UP!), and launch:
//     scalar_mul<<<blocks, threads>>>(A, C, N, scalar);
// New to this pattern? Open the Guide (top right) for a full walkthrough.
extern "C" void solve(const float* A, float* C, int N, float scalar) {
}
