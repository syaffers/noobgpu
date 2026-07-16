#include "noobgpu_harness.h"

extern "C" void solve(float* input, int N);

int main(int argc, char** argv) {
    HarnessArgs args = harness_parse(argc, argv);
    int n = args.ints[0];
    uint64_t seed = args.ints[1];

    float* h_in = harness_gen_floats(n, seed);
    float* h_out = (float*)malloc(n * sizeof(float));

    float* d_in;
    HARNESS_CHECK(cudaMalloc(&d_in, n * sizeof(float)));
    HARNESS_CHECK(cudaMemcpy(d_in, h_in, n * sizeof(float), cudaMemcpyHostToDevice));

    HarnessTimer timer;
    timer.start();
    solve(d_in, n);
    float kernel_ms = timer.stop_ms();
    HARNESS_CHECK(cudaGetLastError());

    HARNESS_CHECK(cudaMemcpy(h_out, d_in, n * sizeof(float), cudaMemcpyDeviceToHost));
    return harness_finish(args, h_out, n, kernel_ms);
}
