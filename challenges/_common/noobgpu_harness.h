// Shared helpers for challenge harnesses. The harness owns main() and the
// result format; user code only provides solve(), so it cannot fake a verdict.
//
// Invocation contract (the judge builds these command lines):
//   program gen   <expected-file> <tolerance> <int args...>   (reference build)
//   program check <expected-file> <tolerance> <int args...>   (submission build)
//
// gen writes the computed output as the expected file. check compares the
// computed output against the expected file and prints exactly one JSON line:
//   {"pass": true|false, "max_abs_err": <float>, "kernel_ms": <float>}
// Exit codes: 0 = harness completed (pass or fail), 2 = harness/CUDA error.
#pragma once

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cuda_runtime.h>

#define HARNESS_CHECK(call)                                                   \
    do {                                                                      \
        cudaError_t err_ = (call);                                            \
        if (err_ != cudaSuccess) {                                            \
            fprintf(stderr, "CUDA error at %s:%d: %s\n", __FILE__, __LINE__,  \
                    cudaGetErrorString(err_));                                \
            exit(2);                                                          \
        }                                                                     \
    } while (0)

struct HarnessArgs {
    bool gen;
    const char* path;
    double tolerance;
    int ints[8];
    int n_ints;
};

static HarnessArgs harness_parse(int argc, char** argv) {
    if (argc < 4 || (strcmp(argv[1], "gen") != 0 && strcmp(argv[1], "check") != 0)) {
        fprintf(stderr, "usage: %s gen|check <file> <tolerance> <ints...>\n", argv[0]);
        exit(2);
    }
    HarnessArgs a;
    a.gen = strcmp(argv[1], "gen") == 0;
    a.path = argv[2];
    a.tolerance = atof(argv[3]);
    a.n_ints = argc - 4;
    if (a.n_ints > 8) {
        fprintf(stderr, "too many int args (max 8)\n");
        exit(2);
    }
    for (int i = 0; i < a.n_ints; i++) a.ints[i] = atoi(argv[4 + i]);
    return a;
}

// Deterministic input generation (xorshift64*), uniform in [-1, 1].
static float* harness_gen_floats(long n, uint64_t seed) {
    float* p = (float*)malloc(n * sizeof(float));
    if (!p) {
        fprintf(stderr, "host allocation of %ld floats failed\n", n);
        exit(2);
    }
    uint64_t s = seed * 0x9E3779B97F4A7C15ULL + 0xD1B54A32D192ED03ULL;
    for (long i = 0; i < n; i++) {
        s ^= s >> 12;
        s ^= s << 25;
        s ^= s >> 27;
        uint32_t r = (uint32_t)((s * 0x2545F4914F6CDD1DULL) >> 40);
        p[i] = (r / (float)(1 << 24)) * 2.0f - 1.0f;
    }
    return p;
}

// Times the solve() call only — H2D/D2H copies happen outside start()/stop().
struct HarnessTimer {
    cudaEvent_t begin, end;
    void start() {
        HARNESS_CHECK(cudaEventCreate(&begin));
        HARNESS_CHECK(cudaEventCreate(&end));
        HARNESS_CHECK(cudaEventRecord(begin));
    }
    float stop_ms() {
        HARNESS_CHECK(cudaEventRecord(end));
        HARNESS_CHECK(cudaEventSynchronize(end));
        float ms = 0.0f;
        HARNESS_CHECK(cudaEventElapsedTime(&ms, begin, end));
        return ms;
    }
};

// File format: int64 count, then count float32 values.
static void harness_write_expected(const char* path, const float* data, long n) {
    FILE* f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "cannot write %s\n", path);
        exit(2);
    }
    int64_t count = n;
    fwrite(&count, sizeof(count), 1, f);
    fwrite(data, sizeof(float), n, f);
    fclose(f);
}

static float* harness_read_expected(const char* path, long* n_out) {
    FILE* f = fopen(path, "rb");
    if (!f) {
        fprintf(stderr, "cannot read %s\n", path);
        exit(2);
    }
    int64_t count = 0;
    if (fread(&count, sizeof(count), 1, f) != 1) {
        fprintf(stderr, "corrupt expected file %s\n", path);
        exit(2);
    }
    float* data = (float*)malloc(count * sizeof(float));
    if (!data || fread(data, sizeof(float), count, f) != (size_t)count) {
        fprintf(stderr, "corrupt expected file %s\n", path);
        exit(2);
    }
    fclose(f);
    *n_out = count;
    return data;
}

// gen mode: write the expected file. check mode: compare + print the JSON line.
// Returns the process exit code.
static int harness_finish(const HarnessArgs& a, const float* output, long n, float kernel_ms) {
    if (a.gen) {
        harness_write_expected(a.path, output, n);
        return 0;
    }
    long expected_n = 0;
    float* expected = harness_read_expected(a.path, &expected_n);
    double max_abs_err = 0.0;
    bool nan_seen = false;
    bool pass = expected_n == n;
    if (pass) {
        for (long i = 0; i < n; i++) {
            double err = fabs((double)output[i] - (double)expected[i]);
            if (std::isnan(err)) {
                nan_seen = true;
                pass = false;
                continue;
            }
            if (err > max_abs_err) max_abs_err = err;
            if (err > a.tolerance) pass = false;
        }
    }
    if (nan_seen) max_abs_err = 9e99;  // sentinel: NaN itself is not valid JSON
    printf("{\"pass\": %s, \"max_abs_err\": %g, \"kernel_ms\": %g}\n",
           pass ? "true" : "false", max_abs_err, kernel_ms);
    return 0;
}
