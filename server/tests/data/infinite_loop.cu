// M1 timeout test: kernel that never terminates.
#include <cstdio>
#include <cuda_runtime.h>

__global__ void spin(volatile int* flag) {
    while (*flag == 0) {
    }
}

int main() {
    int* flag;
    cudaMalloc(&flag, sizeof(int));
    cudaMemset(flag, 0, sizeof(int));
    spin<<<1, 1>>>(flag);
    cudaDeviceSynchronize();  // blocks forever
    printf("unreachable\n");
    return 0;
}
