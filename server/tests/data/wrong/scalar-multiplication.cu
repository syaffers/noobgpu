// Wrong on purpose: adds the scalar instead of multiplying.
#include <cuda_runtime.h>

__global__ void scalar_add(const float* A, float* C, int N, float scalar) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) C[i] = A[i] + scalar;
}

extern "C" void solve(const float* A, float* C, int N, float scalar) {
    scalar_add<<<(N + 255) / 256, 256>>>(A, C, N, scalar);
}
