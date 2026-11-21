import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_systolic_array(dut):
    """Verify 2x2 matrix multiplication: [[1,2],[3,4]] * [[5,6],[7,8]]"""
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Phase 1: Load Weights W = [[5, 6], [7, 8]]
    dut.uio_in.value = 0x1  # load_weight = 1
    dut.ui_in.value = (8 << 4) | 6  # Tick 1: Right col (6, 8)
    await RisingEdge(dut.clk)
    dut.ui_in.value = (7 << 4) | 5  # Tick 2: Left col (5, 7)
    await RisingEdge(dut.clk)

    # Phase 2: Stream Skewed Inputs A = [[1, 2], [3, 4]]
    dut.uio_in.value = 0x0  # load_weight = 0, col_select = 0

    # Tick 3: a_row0 = 1, a_row1 = 0
    dut.ui_in.value = (0 << 4) | 1
    await RisingEdge(dut.clk)

    # Tick 4: a_row0 = 3, a_row1 = 2 -> Read c00 = 19
    dut.ui_in.value = (2 << 4) | 3
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")  # Wait for registers to update
    assert int(dut.uo_out.value) == 19, f"Expected 19, got {int(dut.uo_out.value)}"

    # Tick 5: a_row0 = 0, a_row1 = 4 -> Read c10 = 43, then c01 = 22
    dut.ui_in.value = (4 << 4) | 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")  # Wait for registers to update
    assert int(dut.uo_out.value) == 43, f"Expected 43, got {int(dut.uo_out.value)}"

    dut.uio_in.value = 0x2  # col_select = 1
    await Timer(1, unit="ns")  # Wait for mux to switch
    assert int(dut.uo_out.value) == 22, f"Expected 22, got {int(dut.uo_out.value)}"

    # Tick 6: Flush -> Read c11 = 50
    dut.ui_in.value = 0
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")  # Wait for registers to update
    assert int(dut.uo_out.value) == 50, f"Expected 50, got {int(dut.uo_out.value)}"

    dut._log.info("SUCCESS: All 4 matrix outputs (19, 43, 22, 50) verified!")
