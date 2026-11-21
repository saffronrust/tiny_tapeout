`default_nettype none

module tt_um_systolic_array (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (0=input, 1=output)
    input  wire       ena,      // Always 1 when design is powered
    input  wire       clk,      // Clock
    input  wire       rst_n     // Active-low reset
);
    wire [3:0] a_row0_in   = ui_in[3:0];
    wire [3:0] a_row1_in   = ui_in[7:4];
    wire       load_weight = uio_in[0];
    wire       col_select  = uio_in[1];

    wire [7:0] c_col0_out;
    wire [7:0] c_col1_out;

    systolic_2x2 my_grid (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_weight (load_weight),
        .a_row0_in   (a_row0_in),
        .a_row1_in   (a_row1_in),
        .c_col0_out  (c_col0_out),
        .c_col1_out  (c_col1_out)
    );

    assign uo_out  = col_select ? c_col1_out : c_col0_out;
    assign uio_oe  = 8'b0000_0000;
    assign uio_out = 8'b0000_0000;

    wire _unused = &{ena, uio_in[7:2], 1'b0};
endmodule