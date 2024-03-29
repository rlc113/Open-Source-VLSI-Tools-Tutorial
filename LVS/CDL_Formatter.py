unmodified_cdl_file = "6_final.cdl"
modified_cdl_file = "6_final_lib.cdl"

ucf = open(unmodified_cdl_file, "r")
mcf = open(modified_cdl_file, "w")

ucf_lines = ucf.readlines()
mcf_lines = []

for i in range(len(ucf_lines)):
    #This code adds our include directive
    if "* CDL" in ucf_lines[i]:
        ucf_lines[i] += "\n.INCLUDE /usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice\n"
	
    mcf_lines.append(ucf_lines[i])

mcf.writelines(mcf_lines)

#Close files
ucf.close()
mcf.close()
