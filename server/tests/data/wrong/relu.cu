// Wrong on purpose: copies without clamping negatives.
#include <cuda_runtime.h>

__global__ void copy(const float* input, float* output, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) output[i] = input[i];
}

extern "C" void solve(const float* input, float* output, int N) {
    copy<<<(N + 255) / 256, 256>>>(input, output, N);
}
