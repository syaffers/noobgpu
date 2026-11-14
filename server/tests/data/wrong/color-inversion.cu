// Wrong on purpose: inverts the alpha channel as well.
#include <cuda_runtime.h>

__global__ void invert_all(const float* input, float* output, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) output[i] = 1.0f - input[i];
}

extern "C" void solve(const float* input, float* output, int N) {
    invert_all<<<(N + 255) / 256, 256>>>(input, output, N);
}
