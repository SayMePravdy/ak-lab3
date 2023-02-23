# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=too-many-return-statements

import re
from typing import List, Tuple, Dict

from src.exceptions.exeptions import TranslationException
from src.machine.config import MAX_BUSINESS_ADDRESS, INTERRUPT_START_ADDRESS, MAX_INTERRUPT_ADDRESS
from src.model import Opcode, operations_without_args
from src.translator.input_model import InstructionInput, ArgInput, ArgInputType, forbidden_labels


class TranslationContext:

    def __init__(self, addr: int):
        self.addr = addr

    def get_and_inc_addr(self):
        addr = self.addr
        self.addr += 1
        return addr

    def get_addr(self):
        return self.addr

    def set_addr(self, val: int):
        self.addr = val


LABEL_PATTERN = r'\.?[A-Za-z_]+'
INT_PATTERN = r'-?[0-9]+'


def deserialize(file: str) -> Tuple[Dict[int, InstructionInput], int, int]:
    with open(file, 'r', encoding="utf8") as program_f:
        ctx = TranslationContext(INTERRUPT_START_ADDRESS)
        program_input: dict[int, InstructionInput] = {}
        program_str: str = prepare_program(program_f.read())
        loc = len(program_str.split('\n'))

        inter_section, data_section, text_section = get_program_sections(program_str)

        program_input.update(read_inter_section(inter_section, ctx))
        if ctx.get_addr() > MAX_INTERRUPT_ADDRESS:
            raise TranslationException('Too big interrupt handler')

        ctx.set_addr(MAX_BUSINESS_ADDRESS + 1)
        program_input.update(read_data_section(data_section, ctx))
        program_input.update(read_text_section(text_section, ctx))

        return program_input, loc, len(program_input)


def read_inter_section(inter_section: List[str], ctx: TranslationContext) -> Dict[int, InstructionInput]:
    if inter_section:
        interrupt_code = read_text_section(inter_section, ctx)
        if interrupt_code[sorted(interrupt_code.keys())[-1]].opcode != Opcode.EI:
            raise TranslationException('Interrupt end not found!')
        return interrupt_code
    return {
        ctx.get_and_inc_addr(): InstructionInput(None, Opcode.EI, None)
    }


def read_data_section(data_section: List[str], ctx: TranslationContext) -> Dict[int, InstructionInput]:
    program_data_input: Dict[int, InstructionInput] = {}

    for line in data_section:
        label, value = map(str.strip, line.split(':'))
        check_label(label, None)

        if value[0] == '"' and value[-1] == '"':
            program_data_input[ctx.get_and_inc_addr()] = \
                InstructionInput(label, None, ArgInput(ord(value[1]), ArgInputType.VALUE))
            for symbol in value[2:-1]:
                program_data_input[ctx.get_and_inc_addr()] = \
                    InstructionInput(None, None, ArgInput(ord(symbol), ArgInputType.VALUE))
            continue

        arg_input_type = ArgInputType.VALUE
        if not is_int(value):
            if value.startswith('&') and re.match(LABEL_PATTERN, value[1::]):
                value = value[1::]
                arg_input_type = ArgInputType.LINK
            elif re.match(LABEL_PATTERN, value):
                arg_input_type = ArgInputType.LABEL
            else:
                raise TranslationException(f'Variable {label} has undefined value {value}')

        program_data_input[ctx.get_and_inc_addr()] = InstructionInput(label, None, ArgInput(value, arg_input_type))

    return program_data_input


def read_text_section(text_section: List[str], ctx: TranslationContext) -> Dict[int, InstructionInput]:
    if not text_section:
        raise TranslationException('Error! Empty section .text found')

    program_text_input: Dict[int, InstructionInput] = {}
    label = ''
    for line in text_section:
        if ':' in line:
            if label:
                raise TranslationException(f'Labels {label} and {line.split(":")[0].strip()} in a row')

            if line[-1] == ':':
                label = line[:-1].strip()

            else:
                parsed_line = line.split(':')
                if len(parsed_line) > 2:
                    raise TranslationException(f'Syntax error on line: {line}')
                program_text_input[ctx.get_and_inc_addr()] = parse_instruction(parsed_line[1].strip(), parsed_line[0])
        else:
            program_text_input[ctx.get_and_inc_addr()] = parse_instruction(line, label)
            label = ''
    return program_text_input


def parse_instruction(instruction: str, label: str) -> InstructionInput:
    if label:
        check_label(label, None)

    parsed_instruction = instruction.split(' ')
    try:
        opcode: Opcode = Opcode[parsed_instruction[0]]
        if opcode in operations_without_args:
            if len(parsed_instruction) > 1:
                raise TranslationException(f'Invalid {opcode.value} operation arguments.'
                                           f' Expected 0 but got {len(parsed_instruction) - 1}')
            return InstructionInput(label if label else None, opcode, None)

        if len(parsed_instruction) > 2:
            raise TranslationException(f'Invalid {opcode.value} operation arguments.'
                                       f' Expected 1 but got {len(parsed_instruction) - 1}')

        return InstructionInput(
            label if label else None,
            opcode,
            parse_instruction_argument(parsed_instruction[1], opcode)
        )

    except KeyError as exception:
        raise TranslationException(f'Unknown operation {parsed_instruction[0]}') from exception


# if arg starts with # => it's direct loading otherwise => label (if label starts with * => indirect addressing)
def parse_instruction_argument(arg: str, opcode: Opcode) -> ArgInput:
    if arg.startswith('#'):
        if opcode == Opcode.ST:
            raise TranslationException('ST operation doesn\'t support direct value loading')
        digit_arg = arg[1::]
        if not is_int(digit_arg):
            raise TranslationException(f'Invalid operation argument: {arg}')
        return ArgInput(int(digit_arg), ArgInputType.VALUE)

    if arg.startswith('*'):
        if opcode == Opcode.ST:
            raise TranslationException('ST operation doesn\'t support links')
        check_label(arg[1::], None)
        return ArgInput(arg[1::], ArgInputType.LINK)

    check_label(arg, opcode)
    return ArgInput(arg, ArgInputType.LABEL)


def get_program_sections(program: str) -> Tuple[List[str], List[str], List[str]]:
    inter_part = program.lower().find('section .interrupt')
    data_part = program.lower().find('section .data')
    code_part = program.lower().find('section .text')
    if code_part == -1:
        raise TranslationException('section .text expected')

    inter_section = list(map(str.strip, program[inter_part:data_part].splitlines()[1::]))
    data_section = list(map(str.strip, program[data_part:code_part].splitlines()[1::]))
    text_section = list(map(str.strip, program[code_part::].splitlines()[1::]))

    return inter_section, data_section, text_section


def prepare_program(program: str) -> str:
    program_lines: List[str] = program.splitlines()

    #  delete comments
    program_without_comment = map(lambda line: re.sub(r';.*', '', line), program_lines)
    #  strip lines
    strip_program = map(str.strip, program_without_comment)
    #  delete empty lines
    program_without_empty_lines = filter(None, strip_program)
    #  delete extra spaces
    program_without_extra_spaces = map(lambda line: re.sub(r'\s+', ' ', line), program_without_empty_lines)

    return '\n'.join(program_without_extra_spaces)


def check_label(label: str, opcode: Opcode) -> None:
    stdin_case: bool = label == ArgInputType.STDIN.value and opcode == Opcode.LD
    stdout_case: bool = label == ArgInputType.STDOUT.value and opcode == Opcode.ST

    if not re.match(LABEL_PATTERN, label):
        raise TranslationException(f'Found incorrect label: {label}')

    if (label in forbidden_labels) and not stdin_case and not stdout_case:
        raise TranslationException(f'Label {label} is forbidden in this place')


def is_int(arg: str) -> bool:
    if re.match(INT_PATTERN, arg):
        return True
    return False
