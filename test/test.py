import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut):
    """Initialize inputs and hold active-low reset for 2 clock cycles."""
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


async def run_matmul(dut, A, W):
    """Load 2x2 weights W, stream skewed 2x2 inputs A, and verify C = A * W."""
    # Expected golden reference values
    exp_c00 = A[0][0] * W[0][0] + A[0][1] * W[1][0]
    exp_c01 = A[0][0] * W[0][1] + A[0][1] * W[1][1]
    exp_c10 = A[1][0] * W[0][0] + A[1][1] * W[1][0]
    exp_c11 = A[1][0] * W[0][1] + A[1][1] * W[1][1]

    # Phase 1: Load Weights (uio_in[0] = 1)
    dut.uio_in.value = 0x1
    dut.ui_in.value = (W[1][1] << 4) | W[0][1]  # Tick 1: Right col
    await RisingEdge(dut.clk)
    dut.ui_in.value = (W[1][0] << 4) | W[0][0]  # Tick 2: Left col
    await RisingEdge(dut.clk)

    # Phase 2: Stream Skewed Inputs (uio_in[0] = 0, col_select = 0)
    dut.uio_in.value = 0x0

    # Tick 3: Row 0 starts, Row 1 skewed by 1 cycle
    dut.ui_in.value = (0 << 4) | A[0][0]
    await RisingEdge(dut.clk)

    # Tick 4: Read c00 on Column 0
    dut.ui_in.value = (A[0][1] << 4) | A[1][0]
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    c00 = int(dut.uo_out.value)
    assert c00 == exp_c00, f"c00 mismatch: expected {exp_c00}, got {c00} (A={A}, W={W})"

    # Tick 5: Read c10 on Column 0, then switch to Column 1 for c01
    dut.ui_in.value = (A[1][1] << 4) | 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    c10 = int(dut.uo_out.value)
    assert c10 == exp_c10, f"c10 mismatch: expected {exp_c10}, got {c10} (A={A}, W={W})"

    dut.uio_in.value = 0x2  # col_select = 1
    await Timer(1, unit="ns")
    c01 = int(dut.uo_out.value)
    assert c01 == exp_c01, f"c01 mismatch: expected {exp_c01}, got {c01} (A={A}, W={W})"

    # Tick 6: Flush and read c11 on Column 1
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    c11 = int(dut.uo_out.value)
    assert c11 == exp_c11, f"c11 mismatch: expected {exp_c11}, got {c11} (A={A}, W={W})"


@cocotb.test()
async def test_basic_matmul(dut):
    """1. Basic 2x2 matrix multiplication: [[1,2],[3,4]] * [[5,6],[7,8]]."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    A = [[1, 2], [3, 4]]
    W = [[5, 6], [7, 8]]
    await run_matmul(dut, A, W)
    dut._log.info("PASS: Basic matrix multiplication verified (19, 22, 43, 50).")


@cocotb.test()
async def test_max_value_240(dut):
    """2. Max-value boundary test: A=8, W=15 -> all outputs equal 240 (no 8-bit overflow)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    A = [[8, 8], [8, 8]]
    W = [[15, 15], [15, 15]]
    await run_matmul(dut, A, W)
    dut._log.info("PASS: Max-value (240) boundary test verified.")


@cocotb.test()
async def test_back_to_back(dut):
    """3. Back-to-back matrix multiplications without pulsing reset in between."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    cases = [
        ([[8, 8], [8, 8]], [[15, 15], [15, 15]]),  # High values first
        ([[0, 0], [0, 0]], [[15, 15], [15, 15]]),  # Zero activations (checks stale psum leak)
        ([[2, 5], [7, 1]], [[3, 9], [4, 6]]),      # Mixed values immediately after
    ]
    for idx, (A, W) in enumerate(cases):
        await run_matmul(dut, A, W)
        dut._log.info(f"PASS: Back-to-back run {idx + 1}/3 succeeded without reset.")


@cocotb.test()
async def test_randomized_matrices(dut):
    """4. 20 randomized 2x2 matrix multiplications (A in 0..8, W in 0..15)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    await reset_dut(dut)

    rng = random.Random(42)  # Fixed seed for reproducible CI runs
    for i in range(20):
        A = [[rng.randint(0, 8) for _ in range(2)] for _ in range(2)]
        W = [[rng.randint(0, 15) for _ in range(2)] for _ in range(2)]
        await run_matmul(dut, A, W)

    dut._log.info("PASS: All 20 randomized 2x2 matrix multiplications verified.")
