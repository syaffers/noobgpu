#include <cuda_runtime.h>

__global__ void transpose(const float* input, float* output, int rows, int cols) {
    // TODO: output[j * rows + i] = input[i * cols + j]
}

// input, output are device pointers (row-major).
extern "C" void solve(const float* input, float* output, int rows, int cols) {
    // TODO: launch your kernel
}
