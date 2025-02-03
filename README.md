# README! 

## GENERAL STATEMENT:
- this code is a very simple simulation it is not an exact emulation and should not be treated as such.
- please try to understand the code, this helps with using the cpu (and may have the added benefit of a slightly deeper, albeit simplified, understanding of the general functions of a cpu)

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

## License
MIT License

Copyright (c) 2025 Jonah Merriam

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.