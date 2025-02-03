# README! 

## GENERAL COMMANDS:
- reset: does as it says, resets the machine
- exit: again does as it says and quits (ctrl+c also works)

## ALU:
- the rusults of all ALU operations (and or sub add) are stored in reg0, not is by default stored in reg0 but a destination can be specified

## OPCODES:
0. = ADD
1. = SUB
2. = MOV
3. = IMMD
4. = JMP
5. = AND
6. = OR
7. = NOT
### NOTE: all of these have to be in binary (000-111) not decimal for input.

### input format:
| OPCODE | Value1 | Value2 |
|----------|----------|----------|
| 000 to 111 | 0000 to 1111 | 0000 to 1111 |

#### Example:
inserting the number 5 into register 1:

| IMMD | R1 | 5  |
|------|----|----|
| 011  |0001|0101|

---