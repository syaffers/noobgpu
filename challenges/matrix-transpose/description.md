# Matrix Transpose

Transpose a matrix of 32-bit floats on the GPU. The input is a `rows x cols`
matrix in row-major order; the output must be the `cols x rows` transpose,
also row-major: `output[j * rows + i] = input[i * cols + j]`.

## Requirements

- Implement `solve(const float* input, float* output, int rows, int cols)`.
- `input` and `output` are **device** pointers to distinct buffers.
- Do not change the `solve` signature.

## Example

```
Input (2 x 3):  [1, 2, 3,
                 4, 5, 6]
Output (3 x 2): [1, 4,
                 2, 5,
                 3, 6]
```

## Constraints

- `1 <= rows, cols <= 1024` and `rows * cols <= 1,048,576`
- Values are in `[-1.0, 1.0]`
- Exact match required (tolerance `0`)
