from typing import Dict

from src.exceptions.exeptions import TranslationException
from src.model import Program
from src.translator.deserializer import deserialize
from src.translator.validator import validate_input_program
from src.utils import serialize_program


def translate(input_file: str, output_file: str) -> None:
    try:
        program_input, loc, code_len = deserialize(input_file)
        program = validate_input_program(program_input)
        serialize_program(output_file, program)
        print('Program successfully translated!')
        print(f'LoC: {loc}')
        print(f'Code: {code_len}')
    except TranslationException as e:
        print(e.get_msg())
    except FileNotFoundError as e:
        print(f'File {e.filename} not found')


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Incorrect arguments! Please run: program_translator.py <input_file> <target_file>')
    else:
        translate(sys.argv[1], sys.argv[2])
