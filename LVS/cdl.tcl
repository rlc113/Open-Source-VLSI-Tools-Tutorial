#Read in the final output of the toolflow
read_db /home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/6_final.odb

#Write the CDL file
write_cdl -masters /home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/platforms/sky130hd/cdl/sky130hd.cdl 6_final.cdl


