# Matrix Multiplication

Multiply two matrices of 32-bit floats on the GPU: `C = A x B`, where `A` is
`M x K`, `B` is `K x N`, and `C` is `M x N`. All matrices are row-major:

```
C[i * N + j] = sum over k of A[i * K + k] * B[k * N + j]
```

## Requirements

- Implement `solve(const float* A, const float* B, float* C, int M, int N, int K)`.
- `A`, `B`, `C` are **device** pointers; write the result to `C`.
- Do not change the `solve` signature.

## Example

```
A (2 x 2): [1, 2,      B (2 x 2): [5, 6,
            3, 4]                  7, 8]
C = A x B: [19, 22,
            43, 50]
```

## Constraints

- `1 <= M, N, K <= 512`
- Values are in `[-1.0, 1.0]`
- Absolute tolerance: `1e-3`
