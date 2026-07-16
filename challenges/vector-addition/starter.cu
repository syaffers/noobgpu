#include <cuda_runtime.h>

__global__ void vector_add(const float* A, const float* B, float* C, int N) {
    // TODO: compute C[i] = A[i] + B[i]
}

// A, B, C are device pointers.
extern "C" void solve(const float* A, const float* B, float* C, int N) {
    // TODO: launch your kernel
}
