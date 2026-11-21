`default_nettype none

module simple_pe (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       load_weight,
    input  wire [3:0] a_in,
    input  wire [7:0] psum_in,
    output reg  [3:0] a_out,
    output reg  [7:0] psum_out
);
    reg [3:0] weight;

    always @(posedge clk) begin
        if (!rst_n) begin
            weight   <= 4'd0;
            a_out    <= 4'd0;
            psum_out <= 8'd0;
        end else if (load_weight) begin
            weight   <= a_in;
            a_out    <= a_in;  // Pass incoming weight immediately to the right
        end else begin
            a_out    <= a_in;
            psum_out <= psum_in + (a_in * weight);
        end
    end
endmodule