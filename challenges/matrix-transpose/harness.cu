#include "noobgpu_harness.h"

extern "C" void solve(const float* input, float* output, int rows, int cols);

int main(int argc, char** argv) {
    HarnessArgs args = harness_parse(argc, argv);
    int rows = args.ints[0];
    int cols = args.ints[1];
    uint64_t seed = args.ints[2];
    long n = (long)rows * cols;

    float* h_in = harness_gen_floats(n, seed);
    float* h_out = (float*)malloc(n * sizeof(float));

    float *d_in, *d_out;
    HARNESS_CHECK(cudaMalloc(&d_in, n * sizeof(float)));
    HARNESS_CHECK(cudaMalloc(&d_out, n * sizeof(float)));
    HARNESS_CHECK(cudaMemcpy(d_in, h_in, n * sizeof(float), cudaMemcpyHostToDevice));
    HARNESS_CHECK(cudaMemset(d_out, 0, n * sizeof(float)));

    HarnessTimer timer;
    timer.start();
    solve(d_in, d_out, rows, cols);
    float kernel_ms = timer.stop_ms();
    HARNESS_CHECK(cudaGetLastError());

    HARNESS_CHECK(cudaMemcpy(h_out, d_out, n * sizeof(float), cudaMemcpyDeviceToHost));
    return harness_finish(args, h_out, n, kernel_ms);
}
