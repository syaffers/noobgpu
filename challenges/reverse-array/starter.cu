#include <cuda_runtime.h>

// THE KERNEL — runs on the GPU. The reversal is IN PLACE, which makes this
// one interesting: if every element had its own thread, two threads would
// overwrite each other's input. Classic approach: one thread per PAIR —
// thread i swaps element i with element N-1-i, and only the front half of
// the array needs a thread.
__global__ void reverse(float* input, int N) {
}

// SOLVE — runs on the CPU; the judge calls it with a device pointer that
// already holds the array. Think about how many threads a swap-based
// kernel actually needs. (New here? See the Guide, top right.)
extern "C" void solve(float* input, int N) {
}
