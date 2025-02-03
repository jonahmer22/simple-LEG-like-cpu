// -----------------------------------------------------
// README! 
// 
// GENERAL COMMANDS:
// reset: does as it says, resets the machine
// exit: again does as it says and quits (ctrl+c also works)
// 
// ALU:
// the rusults of all ALU operations (and or sub add) are stored in reg0, not is by default stored in reg0 but a destination can be specified
// 
// OPCODES:
// 0 = ADD
// 1 = SUB
// 2 = MOV
// 3 = IMMD
// 4 = JMP
// 5 = AND
// 6 = OR
// 7 = NOT
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


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void get_user_input(int disp_registers[15][4], int disp_program[15][4], int disp_clock[4], int disp_opcode[3], int disp_input1[4], int disp_input2[4], int disp_output[4], int *opcode, int *value1, int *value2) {
    char user_input[20];
    while (1) {
        printf("Enter opcode (3-bit) and two 4-bit inputs, separated by spaces: ");
        fgets(user_input, sizeof(user_input), stdin);
        
        if (strncmp(user_input, "reset", 5) == 0) {
            for (int i = 0; i < 15; i++) {
                for (int j = 0; j < 4; j++) {
                    disp_registers[i][j] = 0;
                    disp_program[i][j] = 0;
                }
            }
            for (int i = 0; i < 4; i++) {
                disp_clock[i] = 0;
                disp_opcode[i] = 0;
                disp_input1[i] = 0;
                disp_input2[i] = 0;
                disp_output[i] = 0;
            }
            printf("System reset.\n");
            *opcode = 0;
            *value1 = 0;
            *value2 = 0;
            return;
        }

        if (strncmp(user_input, "exit", 4) == 0) {
            exit(0);
        }

        if (sscanf(user_input, "%3s %4s %4s", disp_opcode, disp_input1, disp_input2) == 3) {
            *opcode = strtol(disp_opcode, NULL, 2);
            *value1 = strtol(disp_input1, NULL, 2);
            *value2 = strtol(disp_input2, NULL, 2);
            return;
        } else {
            printf("Invalid input. Format: OPCODE (3-bit) INPUT1 (4-bit) INPUT2 (4-bit)\n");
        }
    }
}

void add(int value1, int value2, int registers[15][4]) {
    int reg1 = value1;
    int reg2 = value2;
    int carry = 0;
    for (int i = 3; i >= 0; i--) {  // left to right
        int sum_ = registers[reg1][i] + registers[reg2][i] + carry;
        registers[0][i] = sum_ % 2;
        carry = sum_ / 2;
    }
}

void sub(int value1, int value2, int registers[15][4]) {
    int reg1_index = value1;
    int reg2_index = value2;
    int borrow = 0;
    int result[4] = {0};    // temporary
    for (int i = 3; i >= 0; i--) {  // left to right
        int diff = registers[reg1_index][i] - registers[reg2_index][i] - borrow;
        if (diff < 0) {
            result[i] = 1;  // borrow bit becomes 1
            borrow = 1;
        } else {
            result[i] = diff;
            borrow = 0;
        }
    }
    for (int i = 0; i < 4; i++) {
        registers[0][i] = result[i];  // put in R0
    }
}

void move(int value1, int value2, int registers[15][4]) {
    int reg1 = value1;
    int reg2 = value2;
    for (int i = 0; i < 4; i++) {
        registers[reg2][i] = registers[reg1][i];
    }
}

void immediate(int value1, int value2, int registers[15][4]) {
    int register_index = value1;
    for (int i = 0; i < 4; i++) {
        registers[register_index][i] = (value2 >> (3 - i)) & 1;
    }
}

void jump(int value1, int clock[4]) {
    for (int i = 0; i < 4; i++) {
        clock[i] = (value1 >> (3 - i)) & 1;
    }
}

void logical_and(int value1, int value2, int registers[15][4]) {
    int reg1 = value1;
    int reg2 = value2;
    for (int i = 0; i < 4; i++) {
        registers[0][i] = registers[reg1][i] && registers[reg2][i];
    }
}

void logical_or(int value1, int value2, int registers[15][4]) {
    int reg1 = value1;
    int reg2 = value2;
    for (int i = 0; i < 4; i++) {
        registers[0][i] = registers[reg1][i] || registers[reg2][i];
    }
}

void logical_not(int value1, int value2, int registers[15][4]) {
    int reg1 = value1;
    int reg2 = value2;
    for (int i = 0; i < 4; i++) {
        registers[reg2][i] = 1 - registers[reg1][i];
    }
}

void update_display(int opcode, int value1, int value2, int disp_opcode[3], int disp_input1[4], int disp_input2[4]) {
    for (int i = 0; i < 3; i++) {
        disp_opcode[i] = (opcode >> (2 - i)) & 1;
    }
    for (int i = 0; i < 4; i++) {
        disp_input1[i] = (value1 >> (3 - i)) & 1;
        disp_input2[i] = (value2 >> (3 - i)) & 1;
    }
}

void process_opcode(int opcode, int value1, int value2, int registers[15][4], int clock[4], int output[4], int program[15][4]) {
    switch (opcode) {
        case 0:
            add(value1, value2, registers);
            break;
        case 1:
            sub(value1, value2, registers);
            break;
        case 2:
            move(value1, value2, registers);
            break;
        case 3:
            immediate(value1, value2, registers);
            break;
        case 4:
            jump(value1, clock);  // jumps to the location of value1
            break;
        case 5:
            logical_and(value1, value2, registers);
            break;
        case 6:
            logical_or(value1, value2, registers);
            break;
        case 7:
            logical_not(value1, value2, registers);
            break;
        default:
            printf("Invalid opcode.\n");
    }
}

int main() {
    int disp_registers[15][4] = {0};  // 15 registers
    int disp_program[15][4] = {0};    // 16 4 bit addresses for a program
    int disp_clock[4] = {0};
    int disp_opcode[3] = {0};
    int disp_input1[4] = {0};
    int disp_input2[4] = {0};
    int disp_output[4] = {0};

    int cycle = 0;
    while (1) {
        cycle++;
        printf("Total cycles: %d\n", cycle);
        printf("----------------------------------------\n");

        // UI display
        printf("---------------Registers----------------\n");
        for (int i = 0; i < 15; i++) {
            printf("| R%d\t| [%d][%d][%d][%d] |\n", i, disp_registers[i][0], disp_registers[i][1], disp_registers[i][2], disp_registers[i][3]);
        }
        printf("| CLK\t| [%d][%d][%d][%d] |\n", disp_clock[0], disp_clock[1], disp_clock[2], disp_clock[3]);
        printf("----------------------------------------\n");
        printf("OPCODE\t\tVALUE1\t\tVALUE2\t\tOUTPUT\n");
        printf("[%d][%d][%d] | [%d][%d][%d][%d] | [%d][%d][%d][%d] | [%d][%d][%d][%d]\n",
               disp_opcode[0], disp_opcode[1], disp_opcode[2],
               disp_input1[0], disp_input1[1], disp_input1[2], disp_input1[3],
               disp_input2[0], disp_input2[1], disp_input2[2], disp_input2[3],
               disp_output[0], disp_output[1], disp_output[2], disp_output[3]);

        // Get user input
        int opcode, value1, value2;
        get_user_input(disp_registers, disp_program, disp_clock, disp_opcode, disp_input1, disp_input2, disp_output, &opcode, &value1, &value2);
        update_display(opcode, value1, value2, disp_opcode, disp_input1, disp_input2);
        process_opcode(opcode, value1, value2, disp_registers, disp_clock, disp_output, disp_program);
    }

    return 0;
}