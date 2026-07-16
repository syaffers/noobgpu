#include <cuda_runtime.h>

__global__ void reverse(float* input, int N) {
    // TODO: swap elements so the array ends up reversed
}

// input is a device pointer; reverse it in place.
extern "C" void solve(float* input, int N) {
    // TODO: launch your kernel
}
