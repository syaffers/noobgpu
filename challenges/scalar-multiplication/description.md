# Scalar Multiplication

Write a GPU program that multiplies every element of a vector by a scalar value:
`C[i] = A[i] * scalar` for every `i` in `[0, N)`.

## Requirements

- Implement `solve(const float* A, float* C, int N, float scalar)`.
- `A` and `C` are **device** pointers, already allocated; write the result to `C`.
- Do not change the `solve` signature.

## Example

```
Input:  A = [1.0, 2.0, 3.0, 4.0]
        scalar = 2.5
Output: C = [2.5, 5.0, 7.5, 10.0]
```

## Constraints

- `1 <= N <= 1,048,576`
- Values are in `[-1.0, 1.0]`
- Scalar is in `[-10.0, 10.0]`
- Absolute tolerance: `1e-5`
