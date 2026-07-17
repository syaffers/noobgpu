#include <cuda_runtime.h>

// THE KERNEL — runs on the GPU, one thread per element.
// ReLU: output[i] = input[i] if it's positive, else 0.
__global__ void relu(const float* input, float* output, int N) {
    // Compute this thread's index from blockIdx/blockDim/threadIdx,
    // guard against i >= N, then write the result.
}

// SOLVE — runs on the CPU; the judge calls it with device pointers that
// already hold the input. Launch enough threads to cover all N elements,
// rounding the block count UP. (New here? See the Guide, top right.)
extern "C" void solve(const float* input, float* output, int N) {
}
