#include <cuda_runtime.h>

__global__ void transpose(const float* input, float* output, int rows, int cols) {
    int j = blockIdx.x * blockDim.x + threadIdx.x;  // column in input
    int i = blockIdx.y * blockDim.y + threadIdx.y;  // row in input
    if (i < rows && j < cols) output[j * rows + i] = input[i * cols + j];
}

extern "C" void solve(const float* input, float* output, int rows, int cols) {
    dim3 threads(16, 16);
    dim3 blocks((cols + 15) / 16, (rows + 15) / 16);
    transpose<<<blocks, threads>>>(input, output, rows, cols);
}
