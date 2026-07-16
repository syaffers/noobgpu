# ReLU

Apply the Rectified Linear Unit activation to a vector of 32-bit floats:
`output[i] = max(0, input[i])` for every `i` in `[0, N)`.

## Requirements

- Implement `solve(const float* input, float* output, int N)`.
- `input` and `output` are **device** pointers.
- Do not change the `solve` signature.

## Example

```
Input:  [-0.5, 0.0, 1.5, -2.0]
Output: [ 0.0, 0.0, 1.5,  0.0]
```

## Constraints

- `1 <= N <= 1,048,576`
- Values are in `[-1.0, 1.0]`
- Exact match required (tolerance `0`)
