// Wrong on purpose: subtracts instead of adds.
#include <cuda_runtime.h>

__global__ void vector_sub(const float* A, const float* B, float* C, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) C[i] = A[i] - B[i];
}

extern "C" void solve(const float* A, const float* B, float* C, int N) {
    vector_sub<<<(N + 255) / 256, 256>>>(A, B, C, N);
}
