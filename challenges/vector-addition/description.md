# Vector Addition

Write a GPU program that adds two vectors of 32-bit floats element by element:
`C[i] = A[i] + B[i]` for every `i` in `[0, N)`.

## Requirements

- Implement `solve(const float* A, const float* B, float* C, int N)`.
- `A`, `B`, and `C` are **device** pointers, already allocated; write the result to `C`.
- Do not change the `solve` signature.

## Example

```
Input:  A = [1.0, 2.0, 3.0, 4.0]
        B = [5.0, 6.0, 7.0, 8.0]
Output: C = [6.0, 8.0, 10.0, 12.0]
```

## Constraints

- `1 <= N <= 1,048,576`
- Values are in `[-1.0, 1.0]`
- Absolute tolerance: `1e-5`
