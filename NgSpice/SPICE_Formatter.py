def smart_input(prompt, responses = ['Y', 'N']):
    print(prompt, end = "")
    x = input()
    while x.upper() not in responses:
        print("Please enter a valid response: ", end = "")
        x = input()
    return x.upper()

def smart_input_number(prompt):
    print(prompt, end = "")
    while True:
        x = input()
        try:
            x = float(x)
            if (x >= 0): return x
            print("Please enter a positive decimal: ", end = "")
        except ValueError:
            print("Your response was not a decimal number. Please enter a postive decimal number: ", end = "")

def smart_intput_number(prompt):
    print(prompt, end = "")
    while True:
        x = input()
        try:
            x = int(x)
            if (x >= 0): return x
            print("Please enter a positive integer: ", end = "")
        except ValueError:
            print("Your response was not an integer number. Please enter a postive integer number: ", end = "")

unmodified_sim_file = "/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/PEX/CDC_PEX_1_Test.cir"
modified_sim_file = "/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/PEX/out.cir"
SPICE_file = "/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/PEX/design_flatten.spice"
verilog_file = "/home/tutorial/openroad_script_files/OpenROAD-flow-scripts/flow/results/sky130hd/counter/base/PEX/6_final.v"

design_name = "design_flatten"

usf = open(unmodified_sim_file, "r")
spf = open(SPICE_file, "r")
vf = open(verilog_file, "r")
msf = open(modified_sim_file, "w")

usf_lines = usf.readlines()
spf_lines = spf.readlines()
vf_lines = vf.readlines()
msf_lines = []

#First find the list of ports - we expect that this will be several lines, each with "+" preceding them
ports = []
plus_streak = False
for i in range(len(spf_lines)):
    if ".subckt " + design_name in spf_lines[i]:
        ports = spf_lines[i].strip().split(" ")[2:]
        plus_streak = True
    elif plus_streak == True and spf_lines[i].split(" ")[0] == "+":
        ports += spf_lines[i].strip().split(" ")[1:]
    else:
        plus_streak = False

#Next, we need to figure out whether the ports are input or output ports
input_ports = []
output_ports = []
for i in range(len(vf_lines)):
    if "input" in vf_lines[i]:
        #Do some preprocessing - eliminate whitespace, remove semicolons, etc.
        vf_lines[i] = vf_lines[i].strip().replace(";", "")
        input_ports += vf_lines[i].strip().split(" ")[-1:]
    elif "output" in vf_lines[i]:
        vf_lines[i] = vf_lines[i].strip().replace(";", "")
        output_ports += vf_lines[i].strip().split(" ")[-1:]
    else:
        plus_streak = False

#The ports that we get from the Verilog file still don't account for vectors - we do that here
new_input_ports = []
for i in range(len(input_ports)):
    selected_input_port = input_ports[i]
    matching_spice_ports = []
    for j in range(len(ports)):
        if selected_input_port in ports[j]: matching_spice_ports.append(ports[j])
    new_input_ports += matching_spice_ports
input_ports = new_input_ports

new_output_ports = []
for i in range(len(output_ports)):
    selected_output_port = output_ports[i]
    matching_spice_ports = []
    for j in range(len(ports)):
        if selected_output_port in ports[j]: matching_spice_ports.append(ports[j])
    new_output_ports += matching_spice_ports
output_ports = new_output_ports

#Let's also figure out if the design has a clock
has_clock = smart_input("Please enter whether your design has a clock or not (Y/N): ")
has_clock = (has_clock == 'Y')

#If it has a clock, then we need to know what it and the reset are called.
clock = ""
reset = ""
reset_high = True
if has_clock:
    print("Please enter the name of your clock signal: ", end = "")
    clock = input()
    while clock not in input_ports:
        print("Signal not found. The available input ports are as follows: " + str(input_ports))
        print("Please select another signal: ", end = "")
        clock = input()

    #Remove the clock
    input_ports.remove(clock)

    print("Please enter the name of your reset signal: ", end = "")
    reset = input()
    while reset not in input_ports:
        print("Signal not found. The available input ports are as follows: " + str(input_ports))
        print("Please select another signal: ", end = "")
        reset = input()

    #Remove the reset
    input_ports.remove(reset)

    reset_high = smart_input("Please enter whether your reset is active high or not (Y/N): ")
    reset_high = (reset_high == 'Y')

sim_time = 0

#Now we are ready to start writing to our simulation file
for i in range(len(usf_lines)):
    #This code changes our include directive to reference the correct design file
    if ".include" in usf_lines[i]:
        usf_lines[i] = '.include "' + SPICE_file + '"\n'

    #This code changes the module instantiation such that it has the correct ports and name
    if "X0" in usf_lines[i]:
        usf_lines[i] = "X0 "
        for j in range(len(ports)): usf_lines[i] += ports[j].replace("[", ".").replace("]", "") + " "
        usf_lines[i] += design_name + "\n"

    #This code will insert inputs as the user desires.
    if "V2" == usf_lines[i].strip().split(" ")[0]:
        usf_lines[i] = ""
        Current_V = 2

        #First, if we have a clock, we should figure out what its period is and declare the clock
        if has_clock:
            clock_period = smart_input_number("Please enter the desired clock period in nanoseconds: ")
            usf_lines[i] += "V2 " + str(clock) + " 0 DC PULSE(1.8V 0 0ns 1fs 1fs " + str(clock_period/2) + "ns " + str(clock_period) + "ns)\n"
            Current_V += 1

        #Also, if we have a clock, we should figure out how long the user wishes to keep it reset at first, and declare the reset
        if has_clock:
            reset_time = smart_input_number("Please enter the desired reset time in nanoseconds: ")
            if reset_high: usf_lines[i] += "V3 " + str(reset) + " 0 DC PULSE(1.8V 0 " + str(reset_time) + "ns 1fs 1fs 1000000ns 1000000ns)\n"
            else: usf_lines[i] += "V3 " + str(reset) + " 0 DC PULSE(0 1.8V " + str(reset_time) + "ns 1fs 1fs 1000000ns 1000000ns)\n"
            Current_V += 1

        #After the above is placed (if necessary), then we shall do the rest of the inputs by prompting the user for each of them
        for p in input_ports:
            custom_input = smart_input('Please enter whether the input "' + p + '" should be statically set to a specific value for the duration of the simulation, or whether it should be set to a custom signal (Static/Custom): ', responses = ['STATIC', 'CUSTOM'])

            if (custom_input == "STATIC"):
                #If we get here, we need to know whether the user wants a '0' or a '1'
                x = smart_input('Please enter whether the input "' + p + '" should be set to 0 or 1 (0/1): ', responses = ['0', '1'])
                if (x == '1'): usf_lines[i] += "V" + str(Current_V) + " " + p + " 0 DC 1.8V\n"
                else: usf_lines[i] += "V" + str(Current_V) + " " + p + " 0 DC 0V\n"

            else:
                #If we get here, the user will wish to have a custom desired input:
                x = input('Please enter what custom voltage the input "' + p + '" should be set to: ')
                usf_lines[i] += "V" + str(Current_V) + " " + p + " 0 DC " + x + "\n"

            Current_V += 1


    #This code changes the simulation time and precision
    if ".tran" in usf_lines[i]:
        sim_time = smart_input_number('Please enter the simulation time in nanoseconds: ')
        y = smart_input_number('Please enter the precision in picoseconds: ')
        usf_lines[i] = ".tran " + str(y) + "ps " + str(sim_time) + "ns uic\n"


    #This code makes sure that the power is measured properly
    if "meas tran AVG_POWER" in usf_lines[i]:
        usf_lines[i] = "    meas tran AVG_POWER AVG POWER_VECTOR from=1ns to=" + str(sim_time - 1) + "ns\n"

    #Finally, we will ask the user to plot some variables
    if "plot" in usf_lines[i]:
        plotted_ports = []
        
        if has_clock:
            #First, ask the user if they wish to plot the clock
            x = smart_input('Please enter whether you wish to plot the clock (Y/N): ')
            if (x == 'Y'): plotted_ports.append(clock)

            #Next, ask the user if they wish to plot the restet
            x = smart_input('Please enter whether you wish to plot the reset (Y/N): ')
            if (x == 'Y'): plotted_ports.append(reset)

        #Format the list of output signals
        for i in range(len(output_ports)): output_ports[i] = output_ports[i].replace("[", ".").replace("]", "")

        num_vars = smart_intput_number('Please enter the number of output signals that you wish to plot: ')
        while num_vars > len(output_ports): num_vars = smart_intput_number('The total number of output signals is ' + str(len(output_ports)) + '. Please enter a lower number: ')

        for i in range(num_vars):
            print("Please enter signal " + str(i) + " that you wish to plot: ", end = "")
            x = input()
            
            while x not in output_ports:
                print("The previous entry was not found in the list of remaining output ports, shown below:")
                print(output_ports)
                print("Please enter another signal: ", end = "")
                x = input()
            
            plotted_ports.append(x)

        usf_lines[i] = "    plot " + " ".join(plotted_ports) + "\n"
            

    msf_lines.append(usf_lines[i])

#Write back to file
msf.writelines(msf_lines)

#Close files
usf.close()
spf.close()
msf.close()
vf.close()
