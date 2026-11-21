<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project implements a **2×2 Weight-Stationary Systolic Array** designed for 4-bit unsigned integer (`INT4`) matrix multiplication ($C = A \times W$) with 8-bit accumulation.

The array consists of four identical Processing Elements (`simple_pe`) arranged in a 2×2 grid:
* **Weight Loading (`uio_in[0] = 1`):** Weights are shifted horizontally into the array from the left via `ui_in[3:0]` (Row 0) and `ui_in[7:4]` (Row 1). Pulsing the clock twice loads all four 4-bit stationary weights into the PEs.
* **Matrix Multiplication (`uio_in[0] = 0`):** On each rising clock edge, 4-bit activations stream horizontally from left to right while 8-bit partial sums accumulate vertically from top to bottom (`psum_out <= psum_in + (a_in * weight)`).
* **Output Multiplexing (`uio_in[1]`):** Because the 2×2 grid produces two 8-bit column outputs (`c_col0_out` and `c_col1_out`) and Tiny Tapeout provides 8 dedicated output pins (`uo_out[7:0]`), `uio_in[1]` acts as a combinational selector switch (`0` = Column 0, `1` = Column 1).

### Pinout Summary

| Pin | Function |
| :--- | :--- |
| `ui_in[3:0]` | 4-bit activation / weight input for Row 0 |
| `ui_in[7:4]` | 4-bit activation / weight input for Row 1 |
| `uio_in[0]` | `load_weight` (`1` = load weights, `0` = compute) |
| `uio_in[1]` | `col_select` (`0` = output Col 0, `1` = output Col 1) |
| `uo_out[7:0]` | 8-bit accumulated result from the selected column |

## How to test

To verify the chip, multiply two 2×2 matrices:

$$A = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}, \quad W = \begin{bmatrix} 5 & 6 \\ 7 & 8 \end{bmatrix} \implies C = \begin{bmatrix} 19 & 22 \\ 43 & 50 \end{bmatrix}$$

1. **Reset:** Pull `rst_n` low (`0`) for 2 clock cycles, then release (`1`).
2. **Load Weights (`uio_in[0] = 1`):**
   * **Cycle 1:** Set `ui_in = 0x86` (`Row 1 = 8`, `Row 0 = 6`) and pulse `clk`.
   * **Cycle 2:** Set `ui_in = 0x75` (`Row 1 = 7`, `Row 0 = 5`) and pulse `clk`.
3. **Stream Skewed Activations (`uio_in[0] = 0`, `uio_in[1] = 0`):**
   * **Cycle 3:** Set `ui_in = 0x01` (`Row 1 = 0`, `Row 0 = 1`) and pulse `clk`.
   * **Cycle 4:** Set `ui_in = 0x23` (`Row 1 = 2`, `Row 0 = 3`) and pulse `clk`. Read `uo_out` = **`19`** ($c_{00}$).
   * **Cycle 5:** Set `ui_in = 0x40` (`Row 1 = 4`, `Row 0 = 0`) and pulse `clk`. Read `uo_out` = **`43`** ($c_{10}$). Then set `uio_in[1] = 1` and read `uo_out` = **`22`** ($c_{01}$).
   * **Cycle 6:** Set `ui_in = 0x00` and pulse `clk` (with `uio_in[1] = 1`). Read `uo_out` = **`50`** ($c_{11}$).

### External hardware

No external hardware is required. The design can be driven directly from the Tiny Tapeout demo board's onboard RP2040/RP2350 microcontroller or tested via the included `cocotb` testbench (`make -C test`).
