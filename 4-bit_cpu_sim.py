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
# 0 = ADD   // adds the values in address1 and address2 then stores the result in register 0
#   Usage: 
#       Add value in reg1 and reg2 (result will be stored in reg0)
#       opcode: address1:   address2:
#       000     0001        0010
# 1 = SUB
#   Usage: 
#       Subtract value in reg2 from reg1 (result will be stored in reg0)
#       opcode: address1:   address2:
#       001     0001        0010
# 2 = MOV
#   Usage: 
#       Move value in reg1 to reg2
#       opcode: address1:   address2:
#       010     0001        0010
# 3 = IMMD
#   Usage: 
#       Insert value of 3 into reg4
#       opcode: address1:   value:
#       011     0100        0011
# 4 = JMP_IF_ZERO
#   Usage: 
#       Jump to address 5 in program memory if reg0 is equal to zero
#       opcode: address1:   address2:
#       100     0000        0101
# 5 = AND
#   Usage: 
#       And value in reg14 and reg2 (result will be stored in reg0)
#       opcode: address1:   address2:
#       101     1110        0010
# 6 = OR
#   Usage: 
#       Add value in reg5 and reg4 (result will be stored in reg0)
#       opcode: address1:   address2:
#       110     0101        0100
# 7 = NOT
#   Usage: 
#       Not the value in reg1 and store it in reg2
#       opcode: address1:   address2:
#       111     0001        0010
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

import time, os

# ========================== Helper Functions ==========================
def int_to_bits(n, bits=4):
    """Convert an integer to a list of bits (most-significant first)."""
    return [int(b) for b in format(n % (1 << bits), f"0{bits}b")]

def bits_to_int(bits):
    """Convert a list of bits to an integer."""
    return int("".join(map(str, bits)), 2)

# ========================== Global State ==========================
_registers = [[0]*4 for _ in range(15)] # 15 registers + clock
_clock = [0]*4
_program = [[0]*11 for _ in range(16)]  # 16 words for a program (3 for opcode + 4 for first instruction + 4 for second instruction = 11 bits per word)
_opcode = [0]*3  # inputs
_input1 = [0]*4
_input2 = [0]*4

_run_speed = 5  # in Hz

_prg_mode = False   # flag for jumping and state management

# ========================== System Functions ==========================
def clear_state():
    """
    Clears all of the registers and program memory
        - Accepts no inputs
        - Sets all values in the CPU to zero
        - Returns nothing
    """
    # include all of the values from global state
    global _registers, _clock, _program, _opcode, _input1, _input2, _output, _prg_mode

    # set all values to 0
    _registers[:] = [[0]*4 for _ in range(15)]
    _clock[:]     = [0]*4
    _program[:]   = [[0]*11 for _ in range(16)]
    _opcode[:]    = [0]*3
    _input1[:]    = [0]*4
    _input2[:]    = [0]*4
    _output[:]    = [0]*4
    _prg_mode     = False

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")    # added `cross platform` for the only thing that I could think of that wasn't gaurunteed to work

def increment_clk():
    """
    Increments the CLK register
        - Accepts no inputs
        - Performs 4-bit addition betwen CLK and the value 1
        - Returns nothing
            - output is stored in CLK register
    """
    # get the current clock and add one to it
    current = bits_to_int(_clock)
    _clock[:] = int_to_bits(current + 1, 4)

# ========================== Input Handling ==========================
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
            user_input = input("Enter opcode (3-bit) and two 4-bit inputs, separated by spaces:\n> ").strip().lower()

            # cases and handling non-binary commands
            if user_input in {"reset", "exit", "program", "run"} or (user_input == "end" and _prg_mode):
                if user_input == "reset":
                    clear_state()
                    print("System reset.")
                elif user_input == "exit":
                    exit(0)
                elif user_input == "program":
                    program()
                elif user_input == "run":
                    run()
                elif user_input == "end":
                    _prg_mode = False
                return None
            
            # regular binary input
            parts = user_input.split()
            if len(parts) != 3 or any(c not in "01" for c in "".join(parts)):
                print("Invalid input. Format: OPCODE (3-bit) INPUT1 (4-bit) INPUT2 (4-bit)")
                continue
            return int(parts[0], 2), int(parts[1], 2), int(parts[2], 2)
        
        # ctrl+c to exit
        except KeyboardInterrupt:
            exit(0)

# ========================== ALU and Instruction Execution ==========================
def add(v1, v2):
    """
    Adds two 4-bit arrays together
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Acts like 4 bit addition
        - No overflow flag, overflow is disregarded
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert both values into ints to add, cut off anything above 15, then turn back to int
    _registers[0] = int_to_bits((bits_to_int(_registers[v1]) + bits_to_int(_registers[v2])) % 16)

def sub(v1, v2):
    """
    Subtracts two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - subtracts 4-bit number in the register associated with value1 from value2
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert both values into ints to sub, cut off anything above 15, then turn back to int
    _registers[0] = int_to_bits((bits_to_int(_registers[v1]) - bits_to_int(_registers[v2])) % 16)

def move(v1, v2):
    """
    Moves a 4-bit array to another one
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Moves 4-bit array at address associated with value1 to value2
            - over-writes register at address value2 with register at address value2
        - Returns nothing
            - output is instead the register at address value2
    """
    _registers[v2] = _registers[v1][:]  # move reg1 over reg2

def immediate(v1, v2):
    """
    'Inserts' a value into a register
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Inserts a value2 at the register associated with value1
        - Returns nothing
            - output is instead at the register associated with value1
    """
    _registers[v1] = int_to_bits(v2)    # write it over

def jump_if_zero(v1, v2):
    """
    Sets the clock of the cpu to a given value if register at value2 is zero
        - Accepts one value in the form of 4-bit number
        - Overwrites the value in CLK with value1 if the value associated with the register at value2 is zero
        - Returns nothing
            - output is instead written into the CLK register
    """
    if bits_to_int(_registers[v2]) == 0:
        _clock[:] = int_to_bits(v1) # convert value1 to binary and move into clock
        return True
    return False    # tell calling function that a jump didn't happen

def logical_and(v1, v2):
    """
    Performs a logical and operation on two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Performs an `and` between the registers associated with value1 from value2
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert both values into ints to perform an and then turn back to int
    _registers[0] = int_to_bits(bits_to_int(_registers[v1]) & bits_to_int(_registers[v2]))

def logical_or(v1, v2):
    """
    Performs a logical or operation on two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Performs an `or` between the registers associated with value1 from value2
        - Returns nothing
            - output is instead added to the first register in the array
    """
    # convert both values into ints to perform an and then turn back to int
    _registers[0] = int_to_bits(bits_to_int(_registers[v1]) | bits_to_int(_registers[v2]))

def logical_not(v1, v2):
    """
    Performs a logical not operation on two 4-bit arrays
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Performs an `not` on the register associated with value1 and assigns it to the register associated with value2
        - Returns nothing
            - output is instead added to the register associated with value2
    """
    # convert the value into an int and not it then turn back to int
    _registers[v2] = int_to_bits(~bits_to_int(_registers[v1]) & 0xF)

def process_opcode(op, v1, v2):
    """
    Processes the input opcode
        - Accepts three values in the form of a 3-bit opcode and two 4-bit commands
        - Uses a match case to execute the appropriate function based off of the given opcode
        - Returns nothing
    """
    # map all opcodes to their respective value
    ops = {0: add, 1: sub, 2: move, 3: immediate, 4: jump_if_zero, 5: logical_and, 6: logical_or, 7: logical_not}
    # get the appropriate code and return
    return ops.get(op, lambda v1, v2: print("Invalid opcode."))(v1, v2) if op != 4 else jump_if_zero(v1, v2)

# ========================== Program Execution ==========================
def program():
    """
    Loops 16 times and takes the user input and puts that input into the 16 words of memory
        - Accepts two values in the form of 4-bit numbers that represent a register address
        - Stores input into memory
        - Returns nothing
            - output is instead stored in 16 words of memory
    """
    global _prg_mode, _run_speed    # include global var

    # set flag to true so no over incrementing clock
    _prg_mode = True

    # loop over program memory
    for i in range(16):
        # ui
        clear_screen()
        print_ui()

        user_input = get_user_input()
        if user_input is None:  # really means if 'end' is input
            break
        _program[i] = int_to_bits(user_input[0], 3) + int_to_bits(user_input[1], 4) + int_to_bits(user_input[2], 4)
        increment_clk()

    # reset clock and end program mode
    _clock[:] = [0]*4
    _prg_mode = False

def run():
    """
    Runs the program stored in memory
        - Accepts no values
        - Passes the values stored in the program array as the input to the cpu (opcode, value1, value2)
        - Returns nothing
    """
    global cycle    # include global var

    # reset clock
    _clock[:] = [0]*4
    speed = _run_speed / 10 # convert from Hz to seconds

    while True:
        # ui
        clear_screen()
        print_ui()
        
        # get address and split up it's values by opcode and value1 and value2
        addr = bits_to_int(_clock)
        op, v1, v2 = bits_to_int(_program[addr][:3]), bits_to_int(_program[addr][3:7]), bits_to_int(_program[addr][7:])
        if not process_opcode(op, v1, v2):
            increment_clk()
        
        # wait the correct amount of time
        time.sleep(speed)

# ========================== UI Functions ==========================
def print_ui():
    """
    Prints the main chunk of UI that shows the state of registers and program memory
        - Accepts no inputs
        - Returns nothing
            - instead prints out values
    """
    print("--------Registers-------Program--------")    # add a nice header
    for i in range(15): # print out first 15 registers and memory
        print(f"| R{i}\t| {''.join(map(str, _registers[i]))} | P{i}\t| {''.join(map(str, _program[i]))} |")
    # need another seperate print so that clock register is correctly labeled
    print(f"| CLK\t| {''.join(map(str, _clock))} | P{15}\t| {''.join(map(str, _program[15]))} |")
    print("---------------------------------------")

def main():
    """Main event loop"""
    global _prg_mode

    while True:
        # ui
        clear_screen()
        print_ui()
        
        user_input = get_user_input()   # get user input
        if user_input and not process_opcode(*user_input):
            increment_clk()

if __name__ == "__main__":
    main()  # run that thang'