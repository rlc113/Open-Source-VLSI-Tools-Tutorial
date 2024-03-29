echo "Hello"

#Please uncomment and change the various paths that are defined here for the script to work

#This is the path to the results folder - make sure the final / is there
RESULTS_PATH=/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/

#This is the path to the openROAD installation - make sure the final / is there
OPENROAD_PATH=/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/

#This is the same DESIGN_NAME that was set in your config.mk file
DESIGN_NAME="counter"

#Now extract the SPICE file using Magic
magic -T sky130A -noconsole -dnull Magic_Extraction.tcl "${RESULTS_PATH}6_final.gds"

#Then, copy the needed files to the current directory
cp "${OPENROAD_PATH}flow/results/sky130hd/counter/base/6_final.odb" .
cp "${OPENROAD_PATH}flow/platforms/sky130hd/cdl/sky130hd.cdl" .

#Next, extract the CDL file using openROAD
${OPENROAD_PATH}tools/install/OpenROAD/bin/openroad -exit cdl.tcl

#Next, format the CDL file by adding the include line
python3 CDL_Formatter.py

#Do LVS
netgen -batch lvs "counter.spice ${DESIGN_NAME}" "6_final_lib.cdl ${DESIGN_NAME}" /usr/local/share/pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl nolog
