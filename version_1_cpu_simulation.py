# -----------------------------------------------------
# README! 
# 
# GENERAL COMMANDS:
# reset: does as it says, resets the machine
# exit: again does as it says and quits (ctrl+c also works)
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

import os

def get_user_input(disp_registers, disp_program, disp_clock, disp_opcode, disp_input1, disp_input2, disp_output):
    while True:
        try:
            user_input = input("Enter opcode (3-bit) and two 4-bit inputs, separated by spaces: ")
            if user_input == "reset":
                disp_registers.clear()
                disp_registers.extend([[0] * 4 for _ in range(15)])
                
                disp_program.clear()
                disp_program.extend([[0] * 4 for _ in range(15)])
                
                disp_clock.clear()
                disp_clock.extend([0] * 4)
                
                disp_opcode.clear()
                disp_opcode.extend([0] * 3)
                
                disp_input1.clear()
                disp_input1.extend([0] * 4)
                
                disp_input2.clear()
                disp_input2.extend([0] * 4)
                
                disp_output.clear()
                disp_output.extend([0] * 4)
                
                print("System reset.")
                return 000, 0000, 0000
            
            elif user_input == "exit":
                exit(0)

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

def add(value1, value2, registers):
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    carry = 0
    for i in range(3, -1, -1):  # left ot right
        sum_ = registers[reg1][i] + registers[reg2][i] + carry
        registers[0][i] = sum_ % 2
        carry = sum_ // 2  # carr or not

def sub(value1, value2, registers):
    reg1_index = int(f"{value1:04b}", 2)
    reg2_index = int(f"{value2:04b}", 2)
    
    if 0 <= reg1_index < len(registers) and 0 <= reg2_index < len(registers):
        borrow = 0
        result = [0] * 4    # temporary
        
        for i in range(3, -1, -1):  # left to right
            diff = registers[reg1_index][i] - registers[reg2_index][i] - borrow
            if diff < 0:
                result[i] = 1  # borrow bit becomes 1
                borrow = 1
            else:
                result[i] = diff
                borrow = 0
        
        registers[0] = result  # put in R0
    else:
        print("Invalid register address.")

def move(value1, value2, registers):
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)

    registers[reg2] = registers[reg1]

def immediate(value1, value2, registers):
    register_index = int(f"{value1:04b}", 2)
    data = [int(bit) for bit in f"{value2:04b}"]

    if 0 <= register_index < len(registers):  # within bounds
        registers[register_index] = data
    else:
        print("Invalid register address.")

def jump(value1, clock):
    binary_value = f"{value1:04b}"
    clock[:] = [int(bit) for bit in binary_value]   # move into clock

def logical_and(value1, value2, registers):
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    for i in range(4):
        registers[0][i] = registers[reg1][i] and registers[reg2][i]

def logical_or(value1, value2, registers):
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    for i in range(4):
        registers[0][i] = registers[reg1][i] or registers[reg2][i]

def logical_not(value1, value2, registers):
    reg1 = int(f"{value1:04b}", 2)
    reg2 = int(f"{value2:04b}", 2)
    
    if 0 <= reg1 < len(registers) and 0 <= reg2 < len(registers):
        registers[reg2] = [1 - bit for bit in registers[reg1]]
    else:
        print("Invalid register address.")

def update_display(opcode, value1, value2, disp_opcode, disp_input1, disp_input2):
    bin_opcode = f"{opcode:03b}"
    bin_value1 = f"{value1:04b}"
    bin_value2 = f"{value2:04b}"

    disp_opcode[:] = [int(bit) for bit in bin_opcode]
    disp_input1[:] = [int(bit) for bit in bin_value1]
    disp_input2[:] = [int(bit) for bit in bin_value2]

def process_opcode(opcode, value1, value2, registers, clock, output, program):
    match opcode:
        case 0:
            add(value1, value2, registers)
        case 1:
            sub(value1, value2, registers)
        case 2:
            move(value1, value2, registers)
        case 3:
            immediate(value1, value2, registers)
        case 4:
            jump(value1, clock) # jumps to the location of value1
        case 5:
            logical_and(value1, value2, registers)
        case 6:
            logical_or(value1, value2, registers)
        case 7:
            logical_not(value1, value2, registers)
        case _:
            print("Invalid opcode.")

def main():
    disp_registers = [[0] * 4 for _ in range(15)]  # 15 registers
    disp_program = [[0] * 4 for _ in range(15)] # 16 4 bit addresses for a program
    disp_clock = [0] * 4
    disp_opcode = [0] * 3
    disp_input1 = [0] * 4
    disp_input2 = [0] * 4
    disp_output = [0] * 4

    cycle = 0
    os.system("clear")
    while True:
        cycle += 1
        print(f"Total cycles: {cycle}")
        print("----------------------------------------")

        # UI display
        print("---------------Registers----------------")
        for i in range(15):
            print(f"| R{i}\t| [{disp_registers[i][0]}][{disp_registers[i][1]}][{disp_registers[i][2]}][{disp_registers[i][3]}] |")
        print(f"| CLK\t| [{disp_clock[0]}][{disp_clock[1]}][{disp_clock[2]}][{disp_clock[3]}] |")
        print("----------------------------------------")
        print("OPCODE\t\tVALUE1\t\tVALUE2\t\tOUTPUT")
        print(f"[{disp_opcode[0]}][{disp_opcode[1]}][{disp_opcode[2]}] | "
              f"[{disp_input1[0]}][{disp_input1[1]}][{disp_input1[2]}][{disp_input1[3]}] | "
              f"[{disp_input2[0]}][{disp_input2[1]}][{disp_input2[2]}][{disp_input2[3]}] | "
              f"[{disp_output[0]}][{disp_output[1]}][{disp_output[2]}][{disp_output[3]}]")

        # Get user input
        opcode, value1, value2 = get_user_input(disp_registers, disp_program, disp_clock, disp_opcode, disp_input1, disp_input2, disp_output)
        update_display(opcode, value1, value2, disp_opcode, disp_input1, disp_input2)
        process_opcode(opcode, value1, value2, disp_registers, disp_clock, disp_output, disp_program)

        os.system("clear")

if __name__ == "__main__":
    main()