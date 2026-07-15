// M1 smoke test: self-contained vector addition that verifies its own output.
#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CUDA_CHECK(call)                                                      \
    do {                                                                      \
        cudaError_t err = (call);                                             \
        if (err != cudaSuccess) {                                             \
            fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__,  \
                    cudaGetErrorString(err));                                 \
            exit(1);                                                          \
        }                                                                     \
    } while (0)

__global__ void add(const float* a, const float* b, float* c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) c[i] = a[i] + b[i];
}

int main() {
    const int n = 1 << 20;
    const size_t bytes = n * sizeof(float);

    float* ha = (float*)malloc(bytes);
    float* hb = (float*)malloc(bytes);
    float* hc = (float*)malloc(bytes);
    for (int i = 0; i < n; i++) {
        ha[i] = (float)i;
        hb[i] = 2.0f * (float)i;
    }

    float *da, *db, *dc;
    CUDA_CHECK(cudaMalloc(&da, bytes));
    CUDA_CHECK(cudaMalloc(&db, bytes));
    CUDA_CHECK(cudaMalloc(&dc, bytes));
    CUDA_CHECK(cudaMemcpy(da, ha, bytes, cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(db, hb, bytes, cudaMemcpyHostToDevice));

    add<<<(n + 255) / 256, 256>>>(da, db, dc, n);
    CUDA_CHECK(cudaGetLastError());
    CUDA_CHECK(cudaMemcpy(hc, dc, bytes, cudaMemcpyDeviceToHost));

    for (int i = 0; i < n; i++) {
        if (hc[i] != 3.0f * (float)i) {
            fprintf(stderr, "mismatch at %d: got %f\n", i, hc[i]);
            printf("FAIL\n");
            return 1;
        }
    }
    printf("PASS\n");
    return 0;
}
