`default_nettype none

module systolic_2x2 (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       load_weight,
    input  wire [3:0] a_row0_in,
    input  wire [3:0] a_row1_in,
    output wire [7:0] c_col0_out,
    output wire [7:0] c_col1_out
);
    wire [3:0] a_row0_mid;
    wire [3:0] a_row1_mid;
    wire [3:0] a_row0_unused;
    wire [3:0] a_row1_unused;
    wire [7:0] psum_col0_mid;
    wire [7:0] psum_col1_mid;

    // Top-Left (Row 0, Col 0)
    simple_pe pe_00 (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_weight (load_weight),
        .a_in        (a_row0_in),
        .psum_in     (8'd0),
        .a_out       (a_row0_mid),
        .psum_out    (psum_col0_mid)
    );

    // Top-Right (Row 0, Col 1)
    simple_pe pe_01 (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_weight (load_weight),
        .a_in        (a_row0_mid),
        .psum_in     (8'd0),
        .a_out       (a_row0_unused),
        .psum_out    (psum_col1_mid)
    );

    // Bottom-Left (Row 1, Col 0)
    simple_pe pe_10 (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_weight (load_weight),
        .a_in        (a_row1_in),
        .psum_in     (psum_col0_mid),
        .a_out       (a_row1_mid),
        .psum_out    (c_col0_out)
    );

    // Bottom-Right (Row 1, Col 1)
    simple_pe pe_11 (
        .clk         (clk),
        .rst_n       (rst_n),
        .load_weight (load_weight),
        .a_in        (a_row1_mid),
        .psum_in     (psum_col1_mid),
        .a_out       (a_row1_unused),
        .psum_out    (c_col1_out)
    );

    wire _unused = &{a_row0_unused, a_row1_unused, 1'b0};
endmodule
