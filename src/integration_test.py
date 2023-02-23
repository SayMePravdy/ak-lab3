import contextlib
import io
import logging
import os
import tempfile
import unittest

import pytest

from src.machine import acc_machine
from src.translator import program_translator


@pytest.mark.golden_test("golden/*.yml")
def test_whole_by_golden(golden):
    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source.asm")
        input_stream = os.path.join(tmpdirname, "input.json")
        target = os.path.join(tmpdirname, "target.o")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            program_translator.translate(source, target)
            acc_machine.run([target, input_stream])

        assert stdout.getvalue() == golden.out["output"]
