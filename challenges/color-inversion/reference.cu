#include <cuda_runtime.h>

__global__ void invert(const float* input, float* output, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) output[i] = (i % 4 == 3) ? input[i] : 1.0f - input[i];
}

extern "C" void solve(const float* input, float* output, int N) {
    int threads = 256;
    int blocks = (N + threads - 1) / threads;
    invert<<<blocks, threads>>>(input, output, N);
}
