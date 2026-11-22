![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# 2×2 INT4 Weight-Stationary Systolic Array (Tiny Tapeout)

A **2×2 Weight-Stationary Systolic Array** ASIC designed in Verilog for [Tiny Tapeout](https://tinytapeout.com), capable of 4-bit unsigned integer (`INT4`) matrix multiplication (`C = A × W`) with 8-bit accumulation inside a single `1x1` tile.

## Architecture Overview

The array is built from four identical Processing Elements (`simple_pe`) wired into a 2×2 grid (`systolic_2x2`) and wrapped for the Tiny Tapeout harness (`tt_um_systolic_array`):

* **Weight Loading (`uio_in[0] = 1`):** Shifts four 4-bit stationary weights into the grid from the left over 2 clock cycles via `ui_in[3:0]` (Row 0) and `ui_in[7:4]` (Row 1).
* **Matrix Multiplication (`uio_in[0] = 0`):** Streams skewed 4-bit activations horizontally left-to-right while accumulating 8-bit partial sums vertically top-to-bottom (`psum_out <= psum_in + (a_in * weight)`).
* **Output Multiplexing (`uio_in[1]`):** Selects whether Column 0 (`0`) or Column 1 (`1`) drives the 8 dedicated output pins (`uo_out[7:0]`).

### Pinout

| Pin | Direction | Function |
| :--- | :--- | :--- |
| `ui_in[3:0]` | Input | 4-bit activation / weight input for Row 0 |
| `ui_in[7:4]` | Input | 4-bit activation / weight input for Row 1 |
| `uio_in[0]` | Input | `load_weight` (`1` = load weights, `0` = compute) |
| `uio_in[1]` | Input | `col_select` (`0` = output Col 0, `1` = output Col 1) |
| `uo_out[7:0]` | Output | 8-bit accumulated result from the selected column |

## Interactive Visualizer

An interactive, cycle-by-cycle visualizer of this 2×2 systolic array is included in the repository:
* Open [`docs/2x2 Systolic Array Visualisation.html`](docs/2x2%20Systolic%20Array%20Visualisation.html) in any web browser to step through weight loading, skewed activation streaming, and partial-sum accumulation.

## Repository Structure

```text
├── docs/
│   ├── info.md                                # Tiny Tapeout project documentation
│   └── 2x2 Systolic Array Visualisation.html  # Interactive cycle-by-cycle visualizer
├── src/
│   ├── project.v                              # Top-level Tiny Tapeout wrapper (tt_um_systolic_array)
│   ├── systolic_2x2.v                         # 2×2 grid interconnect
│   └── simple_pe.v                            # Single INT4 weight-stationary Processing Element
├── test/
│   ├── Makefile                               # Simulation build rules
│   ├── tb.v                                   # Verilog testbench wrapper
│   └── test.py                                # cocotb test suite (basic, max-value 240, back-to-back, randomized)
└── info.yaml                                  # Tiny Tapeout shuttle configuration
```

## Running the Simulation

The `cocotb` test suite in `test/test.py` verifies basic matrix multiplication, max-value (`240`) overflow boundaries, back-to-back runs without reset, and 20 randomized 2×2 matrices.

```bash
cd test
make
```

## Documentation

For full cycle-by-cycle testing instructions, see [`docs/info.md`](docs/info.md).

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip. To learn more, visit [tinytapeout.com](https://tinytapeout.com).
