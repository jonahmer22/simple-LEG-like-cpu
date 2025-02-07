# TODO

## Fix all bugs with SIM2 and release as SIM2.1
    - Run program only executes the first word of memory on first run for some reason
    - maybe add actuall gui with like a fake front pannel, switches and lights:
        - maybe look like an altair8800 or a pdp11/70 front pannel (except 4 bit of course)
    - implement halt command that only works when running, but stops execution
    - rewrite in C

Something I might try in the future:
---
I think I'm going to be nerdy and give this a 'top secret codename', "Prince" based off of the name for Princess a 4 qubit computer released in 2024
```
Total cycles: 1
------------------------------------------------------------
           4-Qubit Quantum CPU Simulator
------------------------------------------------------------
Quantum Register:
   Q0: |0>   
   Q1: |0>
   Q2: |0>
   Q3: |0>
------------------------------------------------------------
Current State Vector (basis amplitudes):
 [ |0000>: 1.000 + 0.000i , |0001>: 0.000 + 0.000i , … , |1111>: 0.000 + 0.000i ]
------------------------------------------------------------
Program Memory (16-bit words):
| P0   | [0001][00][00][0000] |   ; For example, opcode 0001 = H, targeting qubit 0
| P1   | [0011][00][01][0000] |   ; Opcode 0011 = CNOT, with control = qubit 0, target = qubit 1
| P2   | [0010][10][00][0000] |   ; Opcode 0010 = X, on qubit 2
| P3   | [0100][11][00][0000] |   ; Opcode 0100 = MEAS, on qubit 3
| P4   | [0000][00][00][0000] |  
| P5   | [0000][00][00][0000] |
| ...  | ...                  |
| P15  | [0000][00][00][0000] |
------------------------------------------------------------
Instruction Format:
  OPCODE (4 bits) | OPERAND1 (2 bits) | OPERAND2 (2 bits) | PARAMETER (4 bits)
------------------------------------------------------------
Current Instruction:
  OPCODE: [0001]  OPERAND1: [00]  OPERAND2: [00]  PARAMETER: [0000]   QMODE: [0]
------------------------------------------------------------
Enter instruction as: <opcode> <operand1> <operand2> <parameter>
   (all in binary, with appropriate bit-width)
> 
```