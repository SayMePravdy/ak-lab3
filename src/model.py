from enum import Enum, unique
from typing import List, Dict


@unique
class Opcode(Enum):  # case sensitive
    ST = 'ST'  # ACC -> MEM
    LD = 'LD'  # MEM -> ACC
    ADD = 'ADD'  # ACC + VAL -> ACC
    SUB = 'SUB'  # ACC - VAL -> ACC
    INC = 'INC'  # ACC++
    MUL = 'MUL'  # ACC * VAL -> ACC
    MOD = 'MOD'  # ACC % VAL -> Z
    CMP = 'CMP'  # ACC - VAL -> Z
    JMP = 'JMP'  # VAL -> IP
    JZ = 'JZ'  # if Z == 1 VAL -> IP
    JNZ = 'JNZ'  # if Z == 0 VAL -> IP
    EI = 'EI'  # End interrupt
    HLT = 'HLT'  # Stop the program


@unique
class ArgType(Enum):
    ADDR = 'ADDR'  # address
    LINK = 'LINK'  # indirect addressing
    VAL = 'VAL'  # value
    STDIN = 'STDIN'  # input
    STDOUT = 'STDOUT'  # output


class Arg:

    def __init__(self, val: int, arg_type: ArgType):
        self.val = val
        self.arg_type = arg_type

    def __str__(self):
        return f'{self.arg_type}, Value: {self.val}'


class Instruction:

    def __init__(self, opcode: Opcode, arg: Arg):
        self.opcode = opcode
        self.arg = arg

    def __str__(self):
        return f'Instruction: [operation: {self.opcode}, arg: {self.arg}]'


class Program:

    def __init__(self, instructions: Dict[int, Instruction], start_addr: int):
        self.instructions = instructions
        self.start_addr = start_addr

    def __str__(self):
        return '\n'.join(map(str, self.instructions)) + f'\nStart address: {self.start_addr}'


condition_operations: List[Opcode] = [Opcode.JZ, Opcode.JMP, Opcode.JNZ]

operations_without_args: List[Opcode] = [Opcode.HLT, Opcode.INC, Opcode.EI]
