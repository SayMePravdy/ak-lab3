from enum import Enum, unique
from typing import List

from src.model import Opcode


forbidden_labels: List[str] = ['STDIN', 'STDOUT', 'DOPSA']


@unique
class ArgInputType(Enum):
    LABEL = 'LABEL'  # label
    LINK = 'LINK'  # indirect operand loading
    VALUE = 'VALUE'  # direct operand loading
    STDIN = 'STDIN'  # input
    STDOUT = 'STDOUT'  # output


class ArgInput:

    def __init__(self, val, arg_type: ArgInputType):
        self.val = val
        self.arg_type = arg_type

    def __str__(self):
        return f'{self.arg_type}, Value: {self.val}'


class InstructionInput:

    def __init__(self, label: str, opcode: Opcode, arg: ArgInput):
        self.label = label
        self.arg = arg
        self.opcode = opcode

    def __str__(self):
        return f'Instruction: [' \
               f'label: {self.label}, ' \
               f'operation: {self.opcode},' \
               f' arg: {self.arg}]'
