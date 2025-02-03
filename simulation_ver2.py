# -----------------------------------------------------
# README! 
# 
# GENERAL COMMANDS:
# reset: does as it says, resets the machine
# exit: again does as it says and quits (ctrl+c also works)
# program: captures all user input and puts it into program memory until either the cpu runs out of memory or the user types end
#   - end: stops programming early
# run: resets the clock and runs the program currently in memory
# 
# ALU:
# the rusults of all ALU operations (and or sub add) are stored in reg0, not is by default stored in reg0 but a destination can be specified
# 
# OPCODES:
# 0 = ADD
# 1 = SUB
# 2 = MOV
# 3 = IMMD
# 4 = JMP
# 5 = AND
# 6 = OR
# 7 = NOT
# NOTE: all of these have to be in binary (000-111) not decimal for input
# 
# input format:
# OPCODE:   VALUE1:     VALUE2:
# 000 to 111   0000 to 1111   0000 to 1111
# 
# Example: 
# inserting the number 5 into register 1
# IMMD  R1   5
# 011 0001 0101
# -----------------------------------------------------

import time
import os

# global variables for all registers and storage
_registers = [[0] * 4 for _ in range(15)]  # 15_registers + clock
_clock = [0] * 4
_program = [[0] * 11 for _ in range(16)] # 16 words for a program (3 for opcode + 4 for first instruction + 4 for second instruction = 11 bits per word)
_opcode = [0] * 3   # inputs
_input1 = [0] * 4
_input2 = [0] * 4
_output = [0] * 4   # output

def get_user_input():
    """
    Handles user input:
        - Accepts no values
        - Returns 3 integers based on user input:
            000 0000 0000 to 111 1111 1111
        - commands:
            - clear: clears the machine (exluding a Total Cycles count)
            - exit: safely exits the program
    """
    global _prg_mode    # include global var

    while True:
        try:
            user_input = input("Enter opcode (3-bit) and two 4-bit inputs, separated by spaces: \n> ")
            user_input = user_input.lower()
            
            # cases and handling non-binary commands
            if user_input == "reset":
                _registers.clear()
                _registers.extend([[0] * 4 for _ in range(15)])
                
                _program.clear()
                _program.extend([[0] * 11 for _ in range(16)])
                
                _clock.clear()
                _clock.extend([0] * 4)
                
                _opcode.clear()
                _opcode.extend([0] * 3)
                
                _input1.clear()
                _input1.extend([0] * 4)
                
                _input2.clear()
                _input2.extend([0] * 4)
                
                _output.clear()
                _output.extend([0] * 4)

                _prg_mode = 0
                
                print("System reset.")
                return 0, 0, 0  # make sure cpu goes onto next cycle with fresh input registers

            elif user_input == "exit":
                exit(0)

            elif user_input == "program":
                program()

            elif user_input == "run":
                run()

            elif user_input == "end" and _prg_mode == 1:
                _prg_mode = 0
                return 0, 0, 0# make sure cpu goes onto next cycle with fresh input registers
            
            parts = user_input.split()
            
            if len(parts) != 3:
                print("Invalid input. Format: OPCODE (3-bit) INPUT1 (4-bit) INPUT2 (4-bit)")
                continue
            
            bin_opcode, bin1, bin2 = parts
            
            if (
                len(bin_opcode) == 3 and len(bin1) == 4 and len(bin2) == 4 and
                all(c in '01' for c in bin_opcode + bin1 + bin2)
            ):
                opcode = int(bin_opcode, 2)
                num1 = int(bin1, 2)
                num2 = int(bin2, 2)
                return opcode, num1, num2
            else:
                print("Invalid input. Ensure OPCODE is 3-bit and inputs are 4-bit binary values.")

        except ValueError:
            print("Invalid input. Please enter valid binary numbers separated by spaces.")
        except KeyboardInterrupt:
            exit(0)

def increment_clk():
    """
    Increments the CLK register
        - Accepts no inputs
        - Performs 4-bit addition betwen CLK and the a 4-bit array of value 1
        - Returns nothing
            - output is stored in CLK register
    """
    # the number 1 in 4-bit array to add to the clock register
    temp = [0,0,0,1]
    # adder
    carry = 0   # flag for carrying when adding between bits
    for i in range(3, -1, -1):  # left ot right
        sum_ = _clock[i] +  temp[i] + carry
        _clock[i] = sum_ % 2
        carry = sum_ // 2  # carry or not

def program():
    """
    Loops 16 times and takes the user input and puts that input into the 16 words of memory
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Stores input into memory
        - Returns nothing
            - output is instead stored in 16 words of memory
    """
    global _prg_mode    # include global var

    # show the user the cpu is in program mode
    _prg_mode = 1
    # clear the screen for better reading
    os.system("clear")
    print(f"PROGRAMMING MODE")  # add a nice header
    print("--------------------------4-Bit LEG Like CPU-------------------------")
    print_ui()  # reprint the ui

    # reset the clock
    _clock.clear()
    _clock.extend([0] * 4)

    # programming loop
    for i in range(16):
        address = int(''.join(map(str, _clock)))    # convert clock to decimal

        # get user input
        opcode, value1, value2 = get_user_input()

        # give the user the option to exit programming early
        if _prg_mode == 0:
            break

        # correctly assign values to program memory
        word = f"{opcode:03b}{value1:04b}{value2:04b}"
        _program[i] = [int(bit) for bit in word]

        # update the user on changes
        os.system("clear")
        print(f"PROGRAMMING MODE")  # add a nice header
        print("--------------------------4-Bit LEG Like CPU-------------------------")
        print_ui()

        # step through the words of memory by incrementing the clock
        increment_clk()

    # reset the clock
    _clock.clear()
    _clock.extend([0] * 4)
    _prg_mode = 0   # show the user the cpu is no longer in program mode

    os.system("clear")
    print(f"REGULAR MODE")  # add a nice header
    print("--------------------------4-Bit LEG Like CPU-------------------------")
    print_ui()

def add(value1, value2):
    """
    Adds two 4-bit arrays together
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Acts like 4 bit addition
        - No overflow flag, overflow is disregarded
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert value1 and value2 into decimal to access registers
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    carry = 0   # flag for carrying when adding between bits
    for i in range(3, -1, -1):  # left ot right
        sum_ = _registers[reg1][i] + _registers[reg2][i] + carry
        _registers[0][i] = sum_ % 2
        carry = sum_ // 2  # carry or not

def sub(value1, value2):
    """
    Subtracts two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - subtracts 4-bit number in the register associated with value1 from value2
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert value1 and value2 to decimal
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    
    # make sure the address is within range
    if 0 <= reg1 < len(_registers) and 0 <= reg2 < len(_registers):
        borrow = 0
        result = [0] * 4    # temporary
        
        for i in range(3, -1, -1):  # left to right
            diff = _registers[reg1][i] - _registers[reg2][i] - borrow
            if diff < 0:
                result[i] = 1 + diff  # borrow bit becomes 1
                borrow = 1
            else:
                result[i] = diff
                borrow = 0
        
        _registers[0] = result  # put in R0
    else:
        print("Invalid register address.")

def move(value1, value2):
    """
    Moves a 4-bit array to another one
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Moves 4-bit array at address associated with value1 to value2
            - over-writes register at address value2 with register at address value2
        - Returns nothing
            - output is instead the register at address value2
    """
    # convert value1 and value2 to decimal
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)

    _registers[reg2] = _registers[reg1][:] # move reg1 over reg2

def immediate(value1, value2):
    """
    'Inserts' a value into a register
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Inserts a value2 at the register associated with value1
        - Returns nothing
            - output is instead at the register associated with value1
    """
    reg1 = int(f"{value1:04b}", 2)  # converts value1 to decimal
    data = [int(bit) for bit in f"{value2:04b}"]    # converts value2 to a 4-bit array

    if 0 <= reg1 < len(_registers):  # within bounds
       _registers[reg1] = data
    else:
        print("Invalid register address.")

def jump(value1):
    """
    Sets the clock of the cpu to a given value
        - Accepts one value in the form of 4-bit number
        - Overwrites the value in CLK with value1
        - Returns nothing
            - output is instead written into the CLK register
    """
    binary_value = f"{value1:04b}"  # convert value1 to binary
    _clock[:] = [int(bit) for bit in binary_value]   # move into clock

def logical_and(value1, value2):
    """
    Performs a logical and operation on two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Performs an `and` between the registers associated with value1 from value2
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert value1 and value2 to decimal
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)

    # and the contents of the two arrays
    for i in range(4):
       _registers[0][i] = _registers[reg1][i] and _registers[reg2][i]

def logical_or(value1, value2):
    """
    Performs a logical or operation on two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Performs an `or` between the registers associated with value1 from value2
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert value1 and value2 to decimal
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)

    # or the values of the two arrays
    for i in range(4):
       _registers[0][i] = _registers[reg1][i] or _registers[reg2][i]

def logical_not(value1, value2):
    """
    Performs a logical not operation on two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Performs an `not` on the register associated with value1 and assigns it to the register associated with value2
        - Returns nothing
            - output is instead added to the register associated with value2
    """
    # convert value1 and value2 to decimal
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    
    # make sure the address value1 and value2 are valid
    if 0 <= reg1 < len(_registers) and 0 <= reg2 < len(_registers):
       _registers[reg2] = [1 - bit for bit in _registers[reg1]] # perform a not by subtracting and assign it to register associated with value2
    else:
        print("Invalid register address.")

def update_display(opcode, value1, value2):
    """
    Updates the contents of arrays associated with user input
        - Accepts three values in the form of a 3-bit opcode and two 4-bit commands
        - Updates the values in `_opcode, _input1, and _input2`
        - Returns nothing
            - output is stored in the arrays `_opcode, _input1, and _input2`
    """
    # convert inputs to binary strings
    bin_opcode = f"{opcode:03b}"
    bin_value1 = f"{value1:04b}"
    bin_value2 = f"{value2:04b}"

    # overwrite the values of the arrays with new contents
    _opcode[:] = [int(bit) for bit in bin_opcode]
    _input1[:] = [int(bit) for bit in bin_value1]
    _input2[:] = [int(bit) for bit in bin_value2]

def process_opcode(opcode, value1, value2):
    """
    Processes the input opcode
        - Accepts three values in the form of a 3-bit opcode and two 4-bit commands
        - Uses a match case to execute the appropriate function based off of the given opcode
        - Returns nothing
    """
    match opcode:
        case 0:
            add(value1, value2)
        case 1:
            sub(value1, value2)
        case 2:
            move(value1, value2)
        case 3:
            immediate(value1, value2)   # 'inserts' value2 at the register associated with value1
        case 4:
            jump(value1) # jumps to the location of value1
        case 5:
            logical_and(value1, value2)
        case 6:
            logical_or(value1, value2)
        case 7:
            logical_not(value1, value2)
        case _:
            print("Invalid opcode.")

def print_ui():
    """
    Prints the main chunk of UI that shows the state of registers and program memory
        - Accepts no inputs
        - Returns nothing
            - instead prints out values
    """
    global _prg_mode    # include global var

    # UI display
    print("------------Registers--------------------------Program---------------")
    for i in range(15): # print the registers
        print(f"| R{i}\t| [{_registers[i][0]}][{_registers[i][1]}][{_registers[i][2]}][{_registers[i][3]}] | P{i}\t| [{_program[i][0]}][{_program[i][1]}][{_program[i][2]}][{_program[i][3]}][{_program[i][4]}][{_program[i][5]}][{_program[i][6]}][{_program[i][7]}][{_program[i][8]}][{_program[i][9]}][{_program[i][10]}] |")
    print(f"| CLK\t| [{_clock[0]}][{_clock[1]}][{_clock[2]}][{_clock[3]}] | P{15}\t| [{_program[15][0]}][{_program[15][1]}][{_program[15][2]}][{_program[15][3]}][{_program[15][4]}][{_program[15][5]}][{_program[15][6]}][{_program[15][7]}][{_program[15][8]}][{_program[15][9]}][{_program[15][10]}] |")
    # print the bottom layer that contains the inputs and output
    print("---------------------------------------------------------------------")
    print("OPCODE\t\tVALUE1\t\tVALUE2\t\tOUTPUT\t PRG_MODE")
    print(f"[{_opcode[0]}][{_opcode[1]}][{_opcode[2]}] | "
          f"[{_input1[0]}][{_input1[1]}][{_input1[2]}][{_input1[3]}] | "
          f"[{_input2[0]}][{_input2[1]}][{_input2[2]}][{_input2[3]}] | "
          f"[{_output[0]}][{_output[1]}][{_output[2]}][{_output[3]}] | [{_prg_mode}]")
    print("---------------------------------------------------------------------")

# TODO: runs the program at 10 cycles per second, once started there is no stopping (for now at least)
def run():
    """
    Runs the program stored in memory
        - Accepts no values
        - Passes the values stored in the program array as the input to the cpu (opcode, value1, value2)
        - Returns nothing
    """
    global cycle    # include global var

    # reset the clock
    _clock.clear()
    _clock.extend([0] * 4)

    while True:
        cycle += 1

        # convert clock to decimal
        address = int(''.join(map(str, _clock)), 2)

        instruction = _program[address]

        opcode = int(''.join(map(str, instruction[:3])), 2)
        instr1 = int(''.join(map(str, instruction[3:7])), 2)
        instr2 = int(''.join(map(str, instruction[7:11])), 2)

        # Process the opcode with extracted values
        process_opcode(opcode, instr1, instr2)

        # print 'header' with cycle count
        print(f"Total cycles: {cycle}")
        print("--------------------------4-Bit LEG Like CPU-------------------------")
        print_ui()  # print the rest of the ui

        # increment the clock register to progress through the program
        increment_clk()

        # set clock to 5 hz
        time.sleep(0.2)

        os.system("clear")  # clear the screen so next cycle the screen is printed cleanly

def main():
    # define the global _prg_mode for later
    global _prg_mode
    global cycle    # make cycle accessable to run()   
    os.system("clear")  # initially clear the screen
    
    cycle = 0   # this has no effect on simulation I just thought it was nice to see how many cycles you have gone through

    # init with program mode off
    _prg_mode = 0

    # main logic loop
    while True:
        cycle += 1

        # print 'header' with cycle count
        print(f"Total cycles: {cycle}")
        print("--------------------------4-Bit LEG Like CPU-------------------------")
        print_ui()  # print the rest of the ui
        
        # Get user input
        opcode, value1, value2 = get_user_input()
        update_display(opcode, value1, value2)  # update the arrays so reprinted screen displays correct values
        process_opcode(opcode, value1, value2)  # decode the opcode and move on from there to execute command

        # increment the clock register to progress through the program
        increment_clk()

        os.system("clear")  # clear the screen so next cycle the screen is printed cleanly

# start
if __name__ == "__main__":
    main()