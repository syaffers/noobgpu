#include "noobgpu_harness.h"

extern "C" void solve(const float* A, float* C, int N, float scalar);

int main(int argc, char** argv) {
    HarnessArgs args = harness_parse(argc, argv);
    int n = args.ints[0];
    int scalar_tenths = args.ints[1];
    uint64_t seed = args.ints[2];

    float* hA = harness_gen_floats(n, seed);
    float* hC = (float*)malloc(n * sizeof(float));

    float *dA, *dC;
    HARNESS_CHECK(cudaMalloc(&dA, n * sizeof(float)));
    HARNESS_CHECK(cudaMalloc(&dC, n * sizeof(float)));
    HARNESS_CHECK(cudaMemcpy(dA, hA, n * sizeof(float), cudaMemcpyHostToDevice));
    HARNESS_CHECK(cudaMemset(dC, 0, n * sizeof(float)));

    float scalar = (float)scalar_tenths / 10.0f;

    HarnessTimer timer;
    timer.start();
    solve(dA, dC, n, scalar);
    float kernel_ms = timer.stop_ms();
    HARNESS_CHECK(cudaGetLastError());

    HARNESS_CHECK(cudaMemcpy(hC, dC, n * sizeof(float), cudaMemcpyDeviceToHost));
    return harness_finish(args, hC, n, kernel_ms);
}
