// Wrong on purpose: writes zeros instead of the product.
#include <cuda_runtime.h>

__global__ void zeros(float* C, long n) {
    long i = blockIdx.x * (long)blockDim.x + threadIdx.x;
    if (i < n) C[i] = 0.0f;
}

extern "C" void solve(const float* A, const float* B, float* C, int M, int N, int K) {
    long n = (long)M * N;
    zeros<<<(unsigned)((n + 255) / 256), 256>>>(C, n);
}
