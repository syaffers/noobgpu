#include <cuda_runtime.h>

__global__ void matmul(const float* A, const float* B, float* C, int M, int N, int K) {
    // TODO: C[i * N + j] = sum_k A[i * K + k] * B[k * N + j]
}

// A (MxK), B (KxN), C (MxN) are device pointers, row-major.
extern "C" void solve(const float* A, const float* B, float* C, int M, int N, int K) {
    // TODO: launch your kernel
}
