#include "noobgpu_harness.h"

extern "C" void solve(const float* A, const float* B, float* C, int M, int N, int K);

int main(int argc, char** argv) {
    HarnessArgs args = harness_parse(argc, argv);
    int m = args.ints[0];
    int n = args.ints[1];
    int k = args.ints[2];
    uint64_t seed = args.ints[3];
    long size_a = (long)m * k, size_b = (long)k * n, size_c = (long)m * n;

    float* hA = harness_gen_floats(size_a, seed);
    float* hB = harness_gen_floats(size_b, seed + 1);
    float* hC = (float*)malloc(size_c * sizeof(float));

    float *dA, *dB, *dC;
    HARNESS_CHECK(cudaMalloc(&dA, size_a * sizeof(float)));
    HARNESS_CHECK(cudaMalloc(&dB, size_b * sizeof(float)));
    HARNESS_CHECK(cudaMalloc(&dC, size_c * sizeof(float)));
    HARNESS_CHECK(cudaMemcpy(dA, hA, size_a * sizeof(float), cudaMemcpyHostToDevice));
    HARNESS_CHECK(cudaMemcpy(dB, hB, size_b * sizeof(float), cudaMemcpyHostToDevice));
    HARNESS_CHECK(cudaMemset(dC, 0, size_c * sizeof(float)));

    HarnessTimer timer;
    timer.start();
    solve(dA, dB, dC, m, n, k);
    float kernel_ms = timer.stop_ms();
    HARNESS_CHECK(cudaGetLastError());

    HARNESS_CHECK(cudaMemcpy(hC, dC, size_c * sizeof(float), cudaMemcpyDeviceToHost));
    return harness_finish(args, hC, size_c, kernel_ms);
}
