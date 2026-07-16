#include "noobgpu_harness.h"

extern "C" void solve(const float* A, const float* B, float* C, int N);

int main(int argc, char** argv) {
    HarnessArgs args = harness_parse(argc, argv);
    int n = args.ints[0];
    uint64_t seed = args.ints[1];

    float* hA = harness_gen_floats(n, seed);
    float* hB = harness_gen_floats(n, seed + 1);
    float* hC = (float*)malloc(n * sizeof(float));

    float *dA, *dB, *dC;
    HARNESS_CHECK(cudaMalloc(&dA, n * sizeof(float)));
    HARNESS_CHECK(cudaMalloc(&dB, n * sizeof(float)));
    HARNESS_CHECK(cudaMalloc(&dC, n * sizeof(float)));
    HARNESS_CHECK(cudaMemcpy(dA, hA, n * sizeof(float), cudaMemcpyHostToDevice));
    HARNESS_CHECK(cudaMemcpy(dB, hB, n * sizeof(float), cudaMemcpyHostToDevice));
    HARNESS_CHECK(cudaMemset(dC, 0, n * sizeof(float)));

    HarnessTimer timer;
    timer.start();
    solve(dA, dB, dC, n);
    float kernel_ms = timer.stop_ms();
    HARNESS_CHECK(cudaGetLastError());

    HARNESS_CHECK(cudaMemcpy(hC, dC, n * sizeof(float), cudaMemcpyDeviceToHost));
    return harness_finish(args, hC, n, kernel_ms);
}
