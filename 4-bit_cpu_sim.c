#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>

// Function prototypes
void print_ui(void);
void program(void);
void run(void);

// -----------------------------------------------------
// README! CURRENTLY STILL V2 MOST UP TO DATE IS PYTHON VERSION
// 
// GENERAL COMMANDS:
// reset: does as it says, resets the machine
// exit: again does as it says and quits (ctrl+c also works)
// program: captures all user input and puts it into program memory until either the cpu runs out of memory or the user types end
//   - end: stops programming early
// run: resets the clock and runs the program currently in memory
// 
// ALU:
// the rusults of all ALU operations (and or sub add) are stored in reg0, not is by default stored in reg0 but a destination can be specified
// 
// OPCODES:
// 0 = ADD   // adds the values in address1 and address2 then stores the result in register 0
//   Usage: 
//       Add value in reg1 and reg2 (result will be stored in reg0)
//       opcode: address1:   address2:
//       000     0001        0010
// 1 = SUB
//   Usage: 
//       Subtract value in reg2 from reg1 (result will be stored in reg0)
//       opcode: address1:   address2:
//       001     0001        0010
// 2 = MOV
//   Usage: 
//       Move value in reg1 to reg2
//       opcode: address1:   address2:
//       010     0001        0010
// 3 = IMMD
//   Usage: 
//       Insert value of 3 into reg4
//       opcode: address1:   value:
//       011     0100        0011
// 4 = JMP_IF_ZERO
//   Usage: 
//       Jump to address 5 in program memory if reg0 is equal to zero
//       opcode: address1:   address2:
//       100     0000        0101
// 5 = AND
//   Usage: 
//       And value in reg14 and reg2 (result will be stored in reg0)
//       opcode: address1:   address2:
//       101     1110        0010
// 6 = OR
//   Usage: 
//       Add value in reg5 and reg4 (result will be stored in reg0)
//       opcode: address1:   address2:
//       110     0101        0100
// 7 = NOT
//   Usage: 
//       Not the value in reg1 and store it in reg2
//       opcode: address1:   address2:
//       111     0001        0010
// NOTE: all of these have to be in binary (000-111) not decimal for input
// 
// input format:
// OPCODE:   VALUE1:     VALUE2:
// 000 to 111   0000 to 1111   0000 to 1111
// 
// Example: 
// inserting the number 5 into register 1
// IMMD  R1   5
// 011 0001 0101
// -----------------------------------------------------

// global variables for all registers and storage
int registers[15][4];  // 15_registers + clock
int clock_reg[4];      // clock register
int program_memory[16][11]; // 16 words for a program (3 for opcode + 4 for first instruction + 4 for second instruction = 11 bits per word)
int opcode_arr[3];   // inputs
int input1_arr[4];
int input2_arr[4];
int output_arr[4];   // output

int prg_mode = 0;
int cycle = 0;

// Helper function to convert an integer to a binary string with fixed width
void toBinaryString(int value, int bits, char *buffer) {
    buffer[bits] = '\0';
    for (int i = bits - 1; i >= 0; i--) {
        buffer[i] = (value & 1) ? '1' : '0';
        value >>= 1;
    }
}

/*
Handles user input:
    - Accepts no values
    - Returns 3 integers based on user input:
        000 0000 0000 to 111 1111 1111
    - commands:
        - clear: clears the machine (exluding a Total Cycles count)
        - exit: safely exits the program
*/
void get_user_input(int *opcode, int *value1, int *value2) {
    char input_line[100];
    while (1) {
        printf("Enter opcode (3-bit) and two 4-bit inputs, separated by spaces: \n> ");
        if (fgets(input_line, sizeof(input_line), stdin) == NULL) {
            exit(0);
        }
        // Convert input to lowercase
        for (int i = 0; input_line[i] != '\0'; i++) {
            input_line[i] = tolower(input_line[i]);
        }
        // Remove newline if present
        char *newline = strchr(input_line, '\n');
        if (newline) {
            *newline = '\0';
        }
        
        // cases and handling non-binary commands
        if (strcmp(input_line, "reset") == 0) {
            int i, j;
            // reset registers
            for (i = 0; i < 15; i++)
                for (j = 0; j < 4; j++)
                    registers[i][j] = 0;
            // reset program memory
            for (i = 0; i < 16; i++)
                for (j = 0; j < 11; j++)
                    program_memory[i][j] = 0;
            // reset clock
            for (i = 0; i < 4; i++)
                clock_reg[i] = 0;
            // reset opcode, input and output arrays
            for (i = 0; i < 3; i++)
                opcode_arr[i] = 0;
            for (i = 0; i < 4; i++) {
                input1_arr[i] = 0;
                input2_arr[i] = 0;
                output_arr[i] = 0;
            }
            prg_mode = 0;
            
            printf("System reset.\n");
            *opcode = 0;
            *value1 = 0;
            *value2 = 0;
            return;
        } else if (strcmp(input_line, "exit") == 0) {
            exit(0);
        } else if (strcmp(input_line, "program") == 0) {
            program();
            *opcode = 0;
            *value1 = 0;
            *value2 = 0;
            return;
        } else if (strcmp(input_line, "run") == 0) {
            run();
            *opcode = 0;
            *value1 = 0;
            *value2 = 0;
            return;
        } else if (strcmp(input_line, "end") == 0 && prg_mode == 1) {
            prg_mode = 0;
            *opcode = 0;
            *value1 = 0;
            *value2 = 0;
            return;
        }
        
        // Split input into parts
        char *parts[3];
        int count = 0;
        char *token = strtok(input_line, " ");
        while (token != NULL && count < 3) {
            parts[count++] = token;
            token = strtok(NULL, " ");
        }
        
        if (count != 3) {
            printf("Invalid input. Format: OPCODE (3-bit) INPUT1 (4-bit) INPUT2 (4-bit)\n");
            continue;
        }
        
        if (strlen(parts[0]) == 3 && strlen(parts[1]) == 4 && strlen(parts[2]) == 4) {
            int valid = 1;
            for (int i = 0; i < 3; i++) {
                if (parts[0][i] != '0' && parts[0][i] != '1')
                    valid = 0;
            }
            for (int i = 0; i < 4; i++) {
                if (parts[1][i] != '0' && parts[1][i] != '1')
                    valid = 0;
            }
            for (int i = 0; i < 4; i++) {
                if (parts[2][i] != '0' && parts[2][i] != '1')
                    valid = 0;
            }
            if (valid) {
                *opcode = (int) strtol(parts[0], NULL, 2);
                *value1 = (int) strtol(parts[1], NULL, 2);
                *value2 = (int) strtol(parts[2], NULL, 2);
                return;
            } else {
                printf("Invalid input. Ensure OPCODE is 3-bit and inputs are 4-bit binary values.\n");
            }
        } else {
            printf("Invalid input. Ensure OPCODE is 3-bit and inputs are 4-bit binary values.\n");
        }
    }
}

/*
Increments the CLK register
    - Accepts no inputs
    - Performs 4-bit addition betwen CLK and the a 4-bit array of value 1
    - Returns nothing
        - output is stored in CLK register
*/
void increment_clk() {
    int temp[4] = {0, 0, 0, 1};
    int carry = 0;   // flag for carrying when adding between bits
    for (int i = 3; i >= 0; i--) {  // right to left
        int sum = clock_reg[i] + temp[i] + carry;
        clock_reg[i] = sum % 2;
        carry = sum / 2;  // carry or not
    }
}

/*
Loops 16 times and takes the user input and puts that input into the 16 words of memory
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Stores input into memory
    - Returns nothing
        - output is instead stored in 16 words of memory
*/
void program() {
    int i, j;
    prg_mode = 1;
    system("clear");  // technically this only works on unix-like os', maybe change it to detect os and use `cls` if on windows
    printf("PROGRAMMING MODE\n");
    printf("--------------------------4-Bit LEG Like CPU-------------------------\n");
    print_ui();  // reprint the ui

    // reset the clock
    for (i = 0; i < 4; i++) {
        clock_reg[i] = 0;
    }

    // programming loop
    for (i = 0; i < 16; i++) {
        // address = convert clock to decimal (not used further)
        int address = 0;
        for (j = 0; j < 4; j++) {
            address = address * 10 + clock_reg[j];
        }
        
        int op, val1, val2;
        get_user_input(&op, &val1, &val2);
        
        // give the user the option to exit programming early
        if (prg_mode == 0)
            break;
        
        // correctly assign values to program memory
        char opcode_str[4], val1_str[5], val2_str[5], word[13];
        toBinaryString(op, 3, opcode_str);
        toBinaryString(val1, 4, val1_str);
        toBinaryString(val2, 4, val2_str);
        snprintf(word, sizeof(word), "%s%s%s", opcode_str, val1_str, val2_str);
        for (j = 0; j < 11; j++) {
            program_memory[i][j] = word[j] - '0';
        }
        
        // update the user on changes
        system("clear");
        printf("PROGRAMMING MODE\n");
        printf("--------------------------4-Bit LEG Like CPU-------------------------\n");
        print_ui();
        
        // step through the words of memory by incrementing the clock
        increment_clk();
    }
    // reset the clock
    for (i = 0; i < 4; i++) {
        clock_reg[i] = 0;
    }
    prg_mode = 0;   // show the user the cpu is no longer in program mode

    system("clear");
    printf("REGULAR MODE\n");
    printf("--------------------------4-Bit LEG Like CPU-------------------------\n");
    print_ui();
}

/*
Adds two 4-bit arrays together
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Acts like 4 bit addition
    - No overflow flag, overflow is disregarded
    - Returns nothing
        - output is instead added to the first register in the array
*/
void add(int value1, int value2) {
    int reg1 = value1;
    int reg2 = value2;
    int carry = 0;   // flag for carrying when adding between bits
    for (int i = 3; i >= 0; i--) {  // right to left
        int sum = registers[reg1][i] + registers[reg2][i] + carry;
        registers[0][i] = sum % 2;
        carry = sum / 2;
    }
}

/*
Subtracts two 4-bit arrays
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - subtracts 4-bit number in the register associated with value1 from value2
    - Returns nothing
        - output is instead added to the first register in the array
*/
void sub(int value1, int value2) {
    int reg1 = value1;
    int reg2 = value2;
    
    // make sure the address is within range
    if (reg1 >= 0 && reg1 < 15 && reg2 >= 0 && reg2 < 15) {
        int borrow = 0;
        int result[4] = {0, 0, 0, 0};    // temporary
        
        for (int i = 3; i >= 0; i--) {  // right to left
            int diff = registers[reg1][i] - registers[reg2][i] - borrow;
            if (diff < 0) {
                result[i] = 1 + diff;  // borrow bit becomes 1
                borrow = 1;
            } else {
                result[i] = diff;
                borrow = 0;
            }
        }
        
        for (int i = 0; i < 4; i++) {
            registers[0][i] = result[i];
        }
    } else {
        printf("Invalid register address.\n");
    }
}

/*
Moves a 4-bit array to another one
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Moves 4-bit array at address associated with value1 to value2
        - over-writes register at address value2 with register at address value2
    - Returns nothing
        - output is instead the register at address value2
*/
void move(int value1, int value2) {
    int reg1 = value1;
    int reg2 = value2;
    if (reg1 >= 0 && reg1 < 15 && reg2 >= 0 && reg2 < 15) {
        for (int i = 0; i < 4; i++) {
            registers[reg2][i] = registers[reg1][i];
        }
    }
}

/*
'Inserts' a value into a register
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Inserts a value2 at the register associated with value1
    - Returns nothing
        - output is instead at the register associated with value1
*/
void immediate(int value1, int value2) {
    int reg1 = value1;  // converts value1 to decimal
    char data_str[5];
    toBinaryString(value2, 4, data_str);
    int data[4];
    for (int i = 0; i < 4; i++) {
        data[i] = data_str[i] - '0';
    }
    
    if (reg1 >= 0 && reg1 < 15) {  // within bounds
        for (int i = 0; i < 4; i++) {
            registers[reg1][i] = data[i];
        }
    } else {
        printf("Invalid register address.\n");
    }
}

/*
Sets the clock of the cpu to a given value if register at value2 is zero
    - Accepts one value in the form of 4-bit number
    - Overwrites the value in CLK with value1 if the value associated with the register at value2 is zero
    - Returns nothing
        - output is instead written into the CLK register
*/
int jump_if_zero(int value1, int value2) {
    int reg2 = value2;
    int is_zero = 1;
    if (reg2 >= 0 && reg2 < 15) {
        for (int i = 0; i < 4; i++) {
            if (registers[reg2][i] != 0) {
                is_zero = 0;
                break;
            }
        }
        if (is_zero) {
            char binary_value[5];
            toBinaryString(value1, 4, binary_value);
            for (int i = 0; i < 4; i++) {
                clock_reg[i] = binary_value[i] - '0';
            }
            return 1;
        }
    }
    return 0;
}

/*
Performs a logical and operation on two 4-bit arrays
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Performs an `and` between the registers associated with value1 from value2
    - Returns nothing
        - output is instead added to the first register in the array
*/
void logical_and(int value1, int value2) {
    int reg1 = value1;
    int reg2 = value2;
    if (reg1 >= 0 && reg1 < 15 && reg2 >= 0 && reg2 < 15) {
        for (int i = 0; i < 4; i++) {
            registers[0][i] = registers[reg1][i] && registers[reg2][i];
        }
    }
}

/*
Performs a logical or operation on two 4-bit arrays
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Performs an `or` between the registers associated with value1 from value2
    - Returns nothing
        - output is instead added to the first register in the array
*/
void logical_or(int value1, int value2) {
    int reg1 = value1;
    int reg2 = value2;
    if (reg1 >= 0 && reg1 < 15 && reg2 >= 0 && reg2 < 15) {
        for (int i = 0; i < 4; i++) {
            registers[0][i] = registers[reg1][i] || registers[reg2][i];
        }
    }
}

/*
Performs a logical not operation on two 4-bit arrays
    - Accepts two values in the form of 4-bit numbers that represent a register address
    - Performs an `not` on the register associated with value1 and assigns it to the register associated with value2
    - Returns nothing
        - output is instead added to the register associated with value2
*/
void logical_not(int value1, int value2) {
    int reg1 = value1;
    int reg2 = value2;
    if (reg1 >= 0 && reg1 < 15 && reg2 >= 0 && reg2 < 15) {
        for (int i = 0; i < 4; i++) {
            registers[reg2][i] = 1 - registers[reg1][i];
        }
    } else {
        printf("Invalid register address.\n");
    }
}

/*
Updates the contents of arrays associated with user input
    - Accepts three values in the form of a 3-bit opcode and two 4-bit commands
    - Updates the values in `_opcode, _input1, and _input2`
    - Returns nothing
        - output is stored in the arrays `_opcode, _input1, and _input2`
*/
void update_display(int opcode, int value1, int value2) {
    char bin_opcode[4], bin_value1[5], bin_value2[5];
    toBinaryString(opcode, 3, bin_opcode);
    toBinaryString(value1, 4, bin_value1);
    toBinaryString(value2, 4, bin_value2);
    
    for (int i = 0; i < 3; i++) {
        opcode_arr[i] = bin_opcode[i] - '0';
    }
    for (int i = 0; i < 4; i++) {
        input1_arr[i] = bin_value1[i] - '0';
        input2_arr[i] = bin_value2[i] - '0';
    }
}

/*
Processes the input opcode
    - Accepts three values in the form of a 3-bit opcode and two 4-bit commands
    - Uses a switch case to execute the appropriate function based off of the given opcode
    - Returns nothing
*/
int process_opcode(int opcode, int value1, int value2) {
    int jmp_flag = 0;    // ensure that clock does not over increment on a jump
    switch (opcode) {
        case 0:
            add(value1, value2);
            break;
        case 1:
            sub(value1, value2);
            break;
        case 2:
            move(value1, value2);
            break;
        case 3:
            immediate(value1, value2);
            break;
        case 4:
            jmp_flag = jump_if_zero(value1, value2);
            break;
        case 5:
            logical_and(value1, value2);
            break;
        case 6:
            logical_or(value1, value2);
            break;
        case 7:
            logical_not(value1, value2);
            break;
        default:
            printf("Invalid opcode.\n");
            break;
    }
    return jmp_flag;
}

/*
Prints the main chunk of UI that shows the state of registers and program memory
    - Accepts no inputs
    - Returns nothing
        - instead prints out values
*/
void print_ui(void) {
    int i, j;
    printf("------------Registers--------------------------Program---------------\n");
    for (i = 0; i < 15; i++) {
        printf("| R%d\t| [%d][%d][%d][%d] | P%d\t| [", i, registers[i][0], registers[i][1], registers[i][2], registers[i][3], i);
        for (j = 0; j < 11; j++) {
            printf("%d", program_memory[i][j]);
            if (j < 10)
                printf("][");
        }
        printf("] |\n");
    }
    printf("| CLK\t| [%d][%d][%d][%d] | P15\t| [", clock_reg[0], clock_reg[1], clock_reg[2], clock_reg[3]);
    for (j = 0; j < 11; j++) {
        printf("%d", program_memory[15][j]);
        if (j < 10)
            printf("][");
    }
    printf("] |\n");
    printf("---------------------------------------------------------------------\n");
    printf("OPCODE\t\tVALUE1\t\tVALUE2\t\tOUTPUT\t PRG_MODE\n");
    printf("[%d][%d][%d] | ", opcode_arr[0], opcode_arr[1], opcode_arr[2]);
    printf("[%d][%d][%d][%d] | ", input1_arr[0], input1_arr[1], input1_arr[2], input1_arr[3]);
    printf("[%d][%d][%d][%d] | ", input2_arr[0], input2_arr[1], input2_arr[2], input2_arr[3]);
    printf("[%d][%d][%d][%d] | [%d]\n", output_arr[0], output_arr[1], output_arr[2], output_arr[3], prg_mode);
    printf("---------------------------------------------------------------------\n");
}

/*
Runs the program stored in memory
    - Accepts no values
    - Passes the values stored in the program array as the input to the cpu (opcode, value1, value2)
    - Returns nothing
*/
void run(void) {
    int address, op, instr1, instr2;
    int jmp_flag;
    int i, j;
    
    // reset the clock
    for (i = 0; i < 4; i++) {
        clock_reg[i] = 0;
    }
    
    while (1) {
        cycle++;
        
        // convert clock to decimal (treating clock_reg as binary)
        address = 0;
        for (i = 0; i < 4; i++) {
            address = (address << 1) | clock_reg[i];
        }
        
        int instruction[11];
        for (i = 0; i < 11; i++) {
            instruction[i] = program_memory[address][i];
        }
        
        op = 0;
        for (i = 0; i < 3; i++) {
            op = (op << 1) | instruction[i];
        }
        instr1 = 0;
        for (i = 3; i < 7; i++) {
            instr1 = (instr1 << 1) | instruction[i];
        }
        instr2 = 0;
        for (i = 7; i < 11; i++) {
            instr2 = (instr2 << 1) | instruction[i];
        }
        
        // Process the opcode with extracted values
        jmp_flag = process_opcode(op, instr1, instr2);
        
        // print 'header' with cycle count
        printf("Total cycles: %d\n", cycle);
        printf("--------------------------4-Bit LEG Like CPU-------------------------\n");
        print_ui();
        
        // increment the clock register to progress through the program if we haven't just jumped
        if (!jmp_flag)
            increment_clk();
        
        usleep(200000);  // set clock to 5 Hz (200ms delay)
        system("clear");
    }
}

/*
Main function
*/
int main() {
    int op, val1, val2;
    int jmp_flag;
    
    system("clear");  // initially clear the screen
    cycle = 0;   // this has no effect on simulation; just nice to see cycle count
    prg_mode = 0; // init with program mode off
    
    // main logic loop
    while (1) {
        cycle++;
        
        // print 'header' with cycle count
        printf("Total cycles: %d\n", cycle);
        printf("--------------------------4-Bit LEG Like CPU-------------------------\n");
        print_ui();
        
        // Get user input
        get_user_input(&op, &val1, &val2);
        update_display(op, val1, val2);  // update the arrays so reprinted screen displays correct values
        jmp_flag = process_opcode(op, val1, val2);  // decode the opcode and execute command
        
        // increment the clock register to progress through the program
        if (!jmp_flag)
            increment_clk();
        
        system("clear");  // clear the screen so next cycle the screen is printed cleanly
    }
    
    return 0;
}
