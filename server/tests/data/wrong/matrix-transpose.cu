// Wrong on purpose: copies row-major without transposing.
#include <cuda_runtime.h>

__global__ void copy(const float* input, float* output, long n) {
    long i = blockIdx.x * (long)blockDim.x + threadIdx.x;
    if (i < n) output[i] = input[i];
}

extern "C" void solve(const float* input, float* output, int rows, int cols) {
    long n = (long)rows * cols;
    copy<<<(unsigned)((n + 255) / 256), 256>>>(input, output, n);
}
