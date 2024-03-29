# Read the GDS file
gds read "/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/6_final.gds"

# Load the module that was just read
load counter

# Extract the module to an .ext file
extract

# Configure the ext2spice command for LVS
ext2spice LVS

# Extract the module to a SPICE file
ext2spice counter

# Terminate
exit

