# Reverse Array

Reverse an array of 32-bit floats **in place** on the GPU: after `solve`
returns, `input[i]` must hold the value that was at `input[N - 1 - i]`.

## Requirements

- Implement `solve(float* input, int N)`.
- `input` is a **device** pointer; reverse it in place.
- Do not change the `solve` signature.

## Example

```
Input:  [1.0, 2.0, 3.0, 4.0]
Output: [4.0, 3.0, 2.0, 1.0]
```

## Constraints

- `1 <= N <= 1,048,576`
- Values are in `[-1.0, 1.0]`
- Exact match required (tolerance `0`)
