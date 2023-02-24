# pylint: disable=missing-function-docstring
# pylint: disable=too-many-instance-attributes
# pylint: disable=logging-fstring-interpolation
# pylint: disable=logging-not-lazy
# pylint: disable=consider-using-f-string
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements


"""
    Machine
"""
import json
import sys
from enum import Enum, unique
from typing import Tuple

from src.exceptions.exeptions import MachineException
from src.machine.config import MEM_SIZE, MAX_BUSINESS_ADDRESS, MIN_VAL, MAX_VAL, ACC_SAVE_ADDRESS, FLAG_SAVE_ADDRESS, \
    PC_SAVE_ADDRESS, INTERRUPT_START_ADDRESS, OUTPUT_ADDRESS, INPUT_ADDRESS
from src.model import Program, Instruction, Opcode, ArgType, Arg
from src.utils import deserialize_program, get_logger


logger = get_logger()

@unique
class AluOperation(Enum):
    """
        Alu operations
    """
    ADD = 0
    SUB = 1
    MUL = 2
    MOD = 3


opcode_to_alu_operation = {
    Opcode.ADD: AluOperation.ADD,
    Opcode.SUB: AluOperation.SUB,
    Opcode.CMP: AluOperation.SUB,
    Opcode.MUL: AluOperation.MUL,
    Opcode.MOD: AluOperation.MOD
}


class ControlUnit:

    """
        Machine Control Unit
    """

    def __init__(self, program: Program):
        self.program = dict.fromkeys(range(0, MEM_SIZE), Instruction(None, Arg(0, ArgType.VAL)))
        self.program.update(program.instructions)
        self.program_counter = program.start_addr
        self.acc = 0
        self.addr_reg = 0
        self.data_reg = 0
        self.tick = 0
        self.z_flag = False
        self.interrupted = False
        self.start_interrupt = False
        self.input_buffer = []
        self.output_buffer = []

    def _tick(self):
        self.tick += 1

    def set_z_flag(self, val: int):
        self.z_flag = val == 0

    def set_addr_reg(self, val: int) -> None:
        self.addr_reg = val

    def set_data_reg(self, val: int) -> None:
        self.data_reg = val

    def latch_acc(self, val: int) -> None:
        self.acc = val

    def read(self) -> None:
        self._tick()
        if self.addr_reg == INPUT_ADDRESS:
            if len(self.input_buffer) > 0:
                logger.debug(f'input -> {chr(self.input_buffer[0])}')
                self.data_reg = self.input_buffer.pop(0)
            else:
                raise EOFError
        else:
            self.data_reg = self.program[self.addr_reg].arg.val

    def write(self) -> None:
        if self.addr_reg == OUTPUT_ADDRESS:
            val = chr(self.acc) if 255 >= self.acc >= 0 else self.acc
            self.output_buffer.append(val)
            logger.debug(f'{val} -> output')
        else:
            self.program[self.addr_reg] = Instruction(None, Arg(self.acc, ArgType.VAL))
            logger.debug(f'{self.acc} -> MEM({self.addr_reg})')

        self._tick()

    def save_context(self):
        # save acc
        self._tick()
        self.set_addr_reg(ACC_SAVE_ADDRESS)
        self.write()

        # save flag
        self._tick()
        self.set_data_reg(self.z_flag)
        self.latch_acc(self.alu_compute(AluOperation.ADD, False))
        self._tick()
        self.set_addr_reg(FLAG_SAVE_ADDRESS)
        self.write()

        # save program counter
        self._tick()
        self.set_data_reg(self.program_counter)
        self.latch_acc(self.alu_compute(AluOperation.ADD, False))
        self._tick()
        self.set_addr_reg(PC_SAVE_ADDRESS)
        self.write()

    def _start_interrupt(self):
        logger.debug('Interrupt TICK: {%d}', self.tick)
        self.start_interrupt = False
        self.save_context()
        self.program_counter = INTERRUPT_START_ADDRESS

    def restore_context(self):
        # restore flag
        self.set_addr_reg(FLAG_SAVE_ADDRESS)
        self._tick()
        self.read()
        self.set_z_flag(self.alu_compute(AluOperation.ADD, False))
        self._tick()

        # restore program counter
        self.set_addr_reg(PC_SAVE_ADDRESS)
        self._tick()
        self.read()
        self.latch_program_counter(False)

        # restore acc
        self.set_addr_reg(ACC_SAVE_ADDRESS)
        self._tick()
        self.read()
        self.latch_acc(self.alu_compute(AluOperation.ADD, False))
        self._tick()

    def latch_program_counter(self, sel_next):
        """
            Increment program counter or set new value (from jump command)
        """
        if sel_next:
            self.program_counter += 1
        else:
            self.program_counter = self.data_reg

    def fetch_operand_value(self, arg: Arg) -> None:
        """
            Set operand value to data register
        """
        if arg.arg_type == ArgType.VAL:
            self.set_data_reg(arg.val)
            self._tick()
        elif arg.arg_type in (ArgType.ADDR, ArgType.STDIN):
            self.set_addr_reg(arg.val)
            self._tick()
            self.read()
        elif arg.arg_type == ArgType.LINK:
            self.set_addr_reg(arg.val)
            self._tick()
            self.read()
            self.set_addr_reg(self.data_reg)
            self._tick()
            self.read()

    def decode_and_execute_instruction(self) -> None:
        logger.debug(self)

        if self.start_interrupt:
            self._start_interrupt()

        instruction = self.program[self.program_counter]
        opcode = instruction.opcode
        arg = instruction.arg
        program_counter_select_next_signal = True
        self._tick()

        if opcode == Opcode.HLT:
            raise StopIteration

        if opcode == Opcode.ST:
            self.set_addr_reg(arg.val)
            self._tick()
            self.write()

        elif opcode == Opcode.LD:
            self.fetch_operand_value(arg)
            res = self.alu_compute(AluOperation.ADD, False)
            self.latch_acc(res)
            self._tick()

        elif opcode in [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.MOD, Opcode.CMP]:
            self.fetch_operand_value(arg)
            res = self.alu_compute(opcode_to_alu_operation[opcode])
            if opcode not in [Opcode.MOD, Opcode.CMP]:
                self.latch_acc(res)
            self._tick()

        elif opcode == Opcode.INC:
            self.set_data_reg(1)
            self._tick()
            res = self.alu_compute(AluOperation.ADD)
            self.latch_acc(res)
            self._tick()

        elif opcode == Opcode.JMP:
            self.fetch_operand_value(arg)
            program_counter_select_next_signal = False

        elif opcode == Opcode.JZ:
            if self.z_flag:
                self.fetch_operand_value(arg)
                program_counter_select_next_signal = False

        elif opcode == Opcode.JNZ:
            if not self.z_flag:
                self.fetch_operand_value(arg)
                program_counter_select_next_signal = False

        elif opcode == Opcode.EI:
            logger.debug("Interrupt end!")
            self.interrupted = False
            self.restore_context()
            return

        elif opcode is None:
            raise MachineException('Crash addressing')

        self.latch_program_counter(program_counter_select_next_signal)

    def alu_compute(self, operation: AluOperation, sel_left: bool = True, sel_right: bool = True) -> int:
        left_operand = self.acc if sel_left else 0
        right_operand = self.data_reg if sel_right else 0
        res = None
        if operation == AluOperation.ADD:
            res = left_operand + right_operand

        elif operation == AluOperation.SUB:
            res = left_operand - right_operand

        elif operation == AluOperation.MUL:
            res = left_operand * right_operand

        elif operation == AluOperation.MOD:
            if not right_operand:
                raise MachineException('Error! Trying to get MOD operation from 0')
            res = left_operand % right_operand

        self.set_z_flag(res)
        return self.check_value(res)

    @staticmethod
    def check_value(val: int) -> int:
        if val > MAX_VAL or val < MIN_VAL:
            raise MachineException('Overflow error!')
        return val

    def __repr__(self):
        state = f'{{TICK: {self.tick}, PC: {self.program_counter}, AR: {self.addr_reg}, DR: {self.data_reg}, ' \
                f'ACC: {self.acc}, Z: {self.z_flag}}}'

        instr = self.program[self.program_counter]
        action = f'{instr.opcode.value} ' \
                 f'{instr.arg.arg_type if instr.arg else " -- "}' \
                 f' {instr.arg.val if instr.arg else " -- "}'

        return "{} {}".format(state, action)


def simulation(program: Program, input_buffer: list, limit: int) -> Tuple[list, int, int]:
    if len(program.instructions) > MEM_SIZE - MAX_BUSINESS_ADDRESS - 1:
        raise MachineException('Program is too large')
    control_unit = ControlUnit(program)
    cnt = 0

    try:
        while True:
            if cnt > limit:
                raise MachineException('Too long execution! Increase limit')
            cnt += 1

            control_unit.decode_and_execute_instruction()
            check_for_interrupt(control_unit, input_buffer)

    except StopIteration:
        pass
    except EOFError as exception:
        raise MachineException('Input buffer is empty') from exception

    return control_unit.output_buffer, control_unit.tick, cnt


def check_for_interrupt(control_unit: ControlUnit, input_buffer: list):
    tick = control_unit.tick
    if len(input_buffer):
        if tick >= input_buffer[0]["tick"] and not control_unit.interrupted:
            control_unit.interrupted = True
            control_unit.start_interrupt = True
            control_unit.input_buffer.append(ord(input_buffer.pop(0)["char"]))


def run(run_args: list):
    program_file, input_file = run_args
    program: Program = deserialize_program(program_file)
    input_list = []
    if input_file:
        with open(input_file, encoding="utf-8") as file:
            input_text = file.read()
            if input_text:
                input_list = json.loads(input_text)
    try:
        output, ticks, instructions = simulation(program, input_list, 100000)
        print('Output: ' + ''.join(map(str, output)))
        print(f'Instructions: {instructions}')
        print(f'Ticks: {ticks}')

    except MachineException as exception:
        logger.error(exception.get_msg())


if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.error('Incorrect arguments! Please run: program_translator.py <translated_program> <input_file>')
    else:
        run(sys.argv[1:])
