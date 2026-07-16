#include <cuda_runtime.h>

__global__ void reverse(float* input, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N / 2) {
        float tmp = input[i];
        input[i] = input[N - 1 - i];
        input[N - 1 - i] = tmp;
    }
}

extern "C" void solve(float* input, int N) {
    int threads = 256;
    int blocks = (N / 2 + threads - 1) / threads;
    if (blocks == 0) blocks = 1;
    reverse<<<blocks, threads>>>(input, N);
}
