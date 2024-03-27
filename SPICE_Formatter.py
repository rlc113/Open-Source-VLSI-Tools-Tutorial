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

unmodified_sim_file = "C:/Ryan/Courses/S2024/ECE 1898/SPICE Formatter/CDC_PEX_1_Test.cir"
modified_sim_file = "C:/Ryan/Courses/S2024/ECE 1898/SPICE Formatter/out.txt"
SPICE_file = "C:/Ryan/Courses/S2024/ECE 1898/SPICE Formatter/CDC.spice"
verilog_file = "C:/Ryan/Courses/S2024/ECE 1898/SPICE Formatter/Synthesized.v"

design_name = "CDC"

usf = open(unmodified_sim_file, "r")
spf = open(SPICE_file, "r")
msf = open(modified_sim_file, "w")
vf = open(verilog_file, "r")

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

#Now clean the ports of potential new lines
#for i in range(len(ports)): ports[i] = ports[i].strip()

#Let's override it for now to represent our SPICE file w/ proper ports
ports = ['Reset', 'D_SUB1[0]', 'D_SUB1[1]', 'D_SUB1[2]', 'D_SUB1[3]', 'D_SUB1[4]',
         'D_SUB2[0]', 'D_SUB2[1]', 'D_SUB2[2]', 'D_SUB2[3]', 'D_SUB2[4]',
         'D_MAIN[0]', 'D_MAIN[1]', 'D_MAIN[2]', 'D_MAIN[3]', 'D_MAIN[4]', 'Conversion_Finished', 'VDD', 'VSS']

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

    print("Please enter the name of your reset signal: ", end = "")
    reset = input()
    while reset not in input_ports:
        print("Signal not found. The available input ports are as follows: " + str(input_ports))
        print("Please select another signal: ", end = "")
        reset = input()

    reset_high = smart_input("Please enter whether your reset is active high or not (Y/N): ")
    reset_high = (reset_high == 'Y')

#Temp input stuff
input_ports.append("Enable")
input_ports.append("Double")

#Now we are ready to start writing to our simulation file
for i in range(len(usf_lines)):
    #This code changes our include directive to reference the correct design file
    if ".include" in usf_lines[i]:
        usf_lines[i] = '.include "' + SPICE_file + '"\n'

    #This code changes the module instantiation such that it has the correct ports and name
    if "X0" in usf_lines[i]:
        usf_lines[i] = "X0 "
        for j in range(len(ports)): usf_lines[i] += ports[j] + " "
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
            if p != clock and p!= reset:
                custom_input = smart_input('Please enter whether the input "' + p + '" should be statically set to a specific value for the duration of the simulation, or whether it should be set to a custom signal (Static/Custom): ', responses = ['STATIC', 'CUSTOM'])
                if (custom_input == "STATIC"):
                    usf_lines[i] += "V" + str(Current_V) + " " + p + " 0 DC 1.8V\n"

    msf_lines.append(usf_lines[i])

#Write back to file
msf.writelines(msf_lines)

#Close files
usf.close()
spf.close()
msf.close()
vf.close()