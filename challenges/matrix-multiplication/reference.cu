#include <cuda_runtime.h>

__global__ void matmul(const float* A, const float* B, float* C, int M, int N, int K) {
    int j = blockIdx.x * blockDim.x + threadIdx.x;  // column of C
    int i = blockIdx.y * blockDim.y + threadIdx.y;  // row of C
    if (i < M && j < N) {
        float acc = 0.0f;
        for (int k = 0; k < K; k++) acc += A[i * K + k] * B[k * N + j];
        C[i * N + j] = acc;
    }
}

extern "C" void solve(const float* A, const float* B, float* C, int M, int N, int K) {
    dim3 threads(16, 16);
    dim3 blocks((N + 15) / 16, (M + 15) / 16);
    matmul<<<blocks, threads>>>(A, B, C, M, N, K);
}
