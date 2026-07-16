#include <cuda_runtime.h>

__global__ void relu(const float* input, float* output, int N) {
    // TODO: compute output[i] = max(0, input[i])
}

// input, output are device pointers.
extern "C" void solve(const float* input, float* output, int N) {
    // TODO: launch your kernel
}
