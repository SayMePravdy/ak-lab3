# pylint: disable=too-many-return-statements

"""
    Incoming program validator
"""

from typing import Dict, Set

from src.exceptions.exeptions import TranslationException
from src.machine.config import INPUT_ADDRESS, OUTPUT_ADDRESS, START_LABEL
from src.model import Program, Instruction, ArgType, condition_operations, Arg, operations_without_args
from src.translator.input_model import InstructionInput, ArgInputType


def validate_input_program(program_input: Dict[int, InstructionInput]) -> Program:
    """
        Translate labels into addresses and map input model to internal
    """
    instructions: Dict[int, Instruction] = {}
    first_operation_addr: int = None

    for addr, instruction_input in program_input.items():
        arg = get_argument(program_input, addr, set())
        instructions[addr] = Instruction(instruction_input.opcode, arg)

        if not first_operation_addr and instruction_input.opcode:
            first_operation_addr = addr

    start_addr = find_address_by_label(program_input, START_LABEL, False)
    if not start_addr:
        start_addr = first_operation_addr
    return Program(instructions, start_addr)


def get_argument(program: Dict[int, InstructionInput], instruction_addr: int, calls_history: Set[str]) -> Arg:
    """
        Get argument for current instruction
    """
    instruction: InstructionInput = program[instruction_addr]
    # check IO
    if instruction.opcode and instruction.arg:
        if instruction.arg.val == ArgType.STDIN.value:
            return Arg(INPUT_ADDRESS, ArgType.STDIN)
        if instruction.arg.val == ArgType.STDOUT.value:
            return Arg(OUTPUT_ADDRESS, ArgType.STDOUT)

    # for operation
    if instruction.opcode:
        if instruction.opcode in operations_without_args:
            return None
        if instruction.arg.arg_type == ArgInputType.VALUE:
            return Arg(instruction.arg.val, ArgType.VAL)

        is_variable_arg: bool = instruction.opcode not in condition_operations
        var_addr = find_address_by_label(
            program,
            instruction.arg.val,
            is_variable_arg
        )

        if var_addr is not None:

            if instruction.opcode in condition_operations:
                return Arg(var_addr, ArgType.VAL)

            return Arg(var_addr, ArgType.ADDR if instruction.arg.arg_type == ArgInputType.LABEL else ArgType.LINK)

        raise TranslationException(f'Undefined {"variable" if is_variable_arg else "label"} {instruction.arg.val}')

    # for variable
    if instruction.label in calls_history:
        raise TranslationException(f'Cyclic dependency of variables: {calls_history}')

    if instruction.arg.arg_type == ArgInputType.VALUE:
        return Arg(int(instruction.arg.val), ArgType.VAL)

    var_addr = find_address_by_label(program, instruction.arg.val, True)
    if var_addr:
        if instruction.arg.arg_type == ArgInputType.LINK:
            return Arg(var_addr, ArgType.VAL)
        calls_history.add(instruction.label)
        return get_argument(program, var_addr, calls_history)
    raise TranslationException(f'Undefined variable {instruction.arg.val}')


def find_address_by_label(program: Dict[int, InstructionInput], label: str, is_variable: bool) -> int:
    """
        Return address by label
    """
    instruction = list(
        filter(lambda instr: instr[1].label == label and (instr[1].opcode is None) == is_variable, program.items())
    )
    cnt = len(instruction)
    if cnt > 1:
        raise TranslationException(f'Unexpectedly identified multiple labels with the same name: {label}')
    if cnt == 0:
        return None
    return instruction[0][0]
