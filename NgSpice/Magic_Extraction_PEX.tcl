#Read in the design
gds read /home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/6_final.gds

#Load and flatten the design - necessary for resistance extraction
load counter
flatten design_flatten
load design_flatten

#Select the top cell and do extraction
select top cell
extract all

#Convert the extracted file to a sim file
ext2sim labels on
ext2sim

#Extract resistance
extresist

#Convert extraction to SPICE with resistances
ext2spice lvs
ext2spice cthresh 0
ext2spice extresist on
ext2spice

#Exit
exit
