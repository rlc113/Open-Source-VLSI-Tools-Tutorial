module counter (input clk,  
                input rst,
                output reg [7:0] out);
            
  always @ (posedge clk or posedge rst) begin
	if (rst) begin
	    out <= 0;
        end else begin
            out <= out + 1;
        end
    end
endmodule
