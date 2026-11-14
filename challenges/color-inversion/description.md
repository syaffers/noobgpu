# Color Inversion

Invert the color channels of an image stored as a flat array of 32-bit floats — four
values per pixel, in `R, G, B, A` order.

## Requirements

- Implement `solve(const float* input, float* output, int N)`.
- `input` and `output` are **device** pointers holding `N` channel values (`N / 4` pixels).
- Red, green, and blue become `1 - value`. Alpha (`input[4k + 3]`) is **copied**, not inverted.
- Do not change the `solve` signature.

## Example

```
Input:  [0.25, 0.75, 1.00, 1.00,  0.00, 0.50, 0.25, 0.50]
Output: [0.75, 0.25, 0.00, 1.00,  1.00, 0.50, 0.75, 0.50]
```

## Constraints

- `1 <= N <= 1,048,576`, and `N` is always a multiple of 4
- Channel values are in `[0.0, 1.0]`
- Absolute error must be within tolerance `1e-5`
