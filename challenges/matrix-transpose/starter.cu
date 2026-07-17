#include <cuda_runtime.h>

// THE KERNEL — runs on the GPU. Matrices are row-major, so element (i, j)
// of the input lives at input[i * cols + j] and must land at
// output[j * rows + i]. A 2D launch maps threads onto (row, column) pairs
// naturally: threadIdx/blockIdx have .x and .y components.
__global__ void transpose(const float* input, float* output, int rows, int cols) {
    // Guard BOTH dimensions before writing — rows and cols rarely divide
    // your block size evenly.
}

// SOLVE — runs on the CPU; the judge calls it with device pointers.
// For 2D launches use dim3, e.g.:
//     dim3 threads(16, 16);
//     dim3 blocks((cols + 15) / 16, (rows + 15) / 16);
extern "C" void solve(const float* input, float* output, int rows, int cols) {
}
