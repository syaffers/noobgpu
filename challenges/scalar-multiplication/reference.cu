#include <cuda_runtime.h>

__global__ void scalar_mul(const float* A, float* C, int N, float scalar) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) C[i] = A[i] * scalar;
}

extern "C" void solve(const float* A, float* C, int N, float scalar) {
    int threads = 256;
    int blocks = (N + threads - 1) / threads;
    scalar_mul<<<blocks, threads>>>(A, C, N, scalar);
}
