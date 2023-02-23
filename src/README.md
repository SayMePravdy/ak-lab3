# AK-Lab3

# Asm. ���������� � ������

- ������� ������ �������������.
- `asm | acc | neum | hw | instr | struct | trap | mem | prob5`

## ���� ����������������

``` ebnf
program ::= instruction

instruction ::= 
       variable
       | comment
       | command [operand]

command ::= "ADD" | "SUB" | "MUL" | "MOD" | "INC" | "ST" | "LD" | "CMP" | "JMP" | "JZ" | "JNZ" | "EI" | "HLT"

comment ::= <all symbols after ; >
```

��� ����������� ���������������. 

���� ������������ ����� (������). ����� ��������� �����������, ��� ��� �������� ����� ���� ������� `;` ��������� ������������.


��� ����������� �� 3 ������:

- ���������������� ���������� ���������� (���������� � ��������� `section .interrupt` ). ���� ��� ���, �� ����� ����������� ��������� ����������, ������ ����������� ����������
- ������ � ����������� (���������� � ��������� `section .data` ). ��������� ����� ���������� �������� ������, ���� �� ��������� � ���� ����� ������ ���������� (����������� ��� ������ ���� ������� `&`). 
- ��� ��������� (����������� � ��������� `section .text` ). ����� ������, ������� ����� ��������� �� ���� ��������. ���������� ��� ���� ����������:
     - ���������������� �������� (����������� ��� ������ ���� ������� `#`)
     - ��������� (�� �����)
     - ���������� � ��������� ���������� (����� ��������� � `*` � ������).
������� ������������� ������ ������������������ � ���������: [hello_world](asm/hello_world.asm)


## ����������� ������

������ ������ ����������:

�������� ����� -- 32 ����, ��������. ����������� ��������: ���� - ����� (int), �������� - ����������. ���� ����� -- ���� ������

������, ����������� ������������� ������������� �� ������ ���� ������ �� ������.

```
Memory
+-----------------------------+
| 00  : input                 |
| 01  : output                |
|    ...                      |
| k   : interrupt handler     |
|    ...                      |
| n   : data                  |
|    ...                      |
| m   : program               |
|    ...                      |
+-----------------------------+
```



## ������� ������

����������� ����������:

- �������� ����� -- 32 ����, ��������.
- ������ ������:
    - ���������� ����� ������� `AR`;
    - ����� ���� �������� �� ������������ `ACC`;
    - ����� ���� ��������� � ������� `DR`.
- ���:
    - ����� �������� ��������:
        - ��������
        - ���������
        - ���������
        - ��������� ������ �� �������
    - �� ����� ���� ��������� `ACC`
    - �� ������ ���� ��������� `DR`
    - �� ���������� �������� ���������� ���� Z
- ����-����� --  memory-mapped, �� ����������. ���� 2 ����������� ����� STDIN � STDOUT, ������������ ��� ����� � ������ ��������������
- `PC` -- ������� ������:
    - ���������������� ����� ������ ���������� ��� ���������������� ����������� ��������.

### ����� ����������

| Syntax   | Mnemonic       | ���-�� ������         | Comment                                               |
|:---------|:---------------|-----------------------|:------------------------------------------------------|
| `ADD`    | add            | 2-4                   | ���������� ����������� � ���������                    |
| `SUB`    | subtract       | 2-4                   | �������� �� ������������ �������                      |
| `INC`    | increment      | 2                     | �������������� �����������                            |
| `MUL`    | multiply       | 2-4                   | �������� ����������� �� �������                       |
| `MOD`    | mod            | 2-4                   | �������� ������ �� ������� ������������ �� ��������   |
| `CMP`    | compare        | 2-4                   | ���������� ����������� � ������� (���������� ���� Z)  |
| `ST`     | store          | 2                     | ��������� ����������� � ������                        |
| `LD`     | load           | 2-4                   | ��������� �������� �� ������ � �����������            |
| `JMP`    | jump           | 1                     | ����������� �������                                   |
| `JNZ`    | jnz            | 1                     | ������� ���� ���� Z == 0                              |
| `JZ`     | jz             | 1                     | ������� ���� ���� Z == 1                              |        
| `EI`     |end interrupt   | 8                     | ������������� ����������                              |
| `HLT`    | halt           | 0                     | ������������� ���������                               |

���������� ������ ����� �������� �� ���� ���������

### ����������� ����������

�������� ��� ������������� � ����� ������.

## ����������

��������� ��������� ������: `program_translator.py <input_file> <target_file>"`

����������� � ������: [translator](translator/program_translator.py)

����� ���������� (������� `translate`):

1. �������������� ��������� � input ������
2. ��������� input ������ � ���������� �� �� ���������� (�������� ������������� �������, ���������� �� ������������, �������� (��� ���������), ���������� ������� � ������ � ��)
3. ������������ � ��������� ����

������� ��������� ��������� ����:

- ���� ����� ����� -- ���� ����������;
- ��� ������, ���������� ��������������� ����������� -- ������ �����������;

## ������ ����������

����������� � ������: [machine](machine/acc_machine.py).

### ControlUnit
![plot](processor.jpg)

���������� � ������ `ControlUnit`.

- Hardwired (����������� ��������� �� python).
- ������������� �� ������ ����������.
- ���������� ���������� � ������������������ ��������: `decode_and_execute_instruction`.

����������� ������ ������:

- ��� ������� ��������� ���������� ������������ ����������� ������ logging � ����������������� ���������������.
- ��������� ������������� �������������� ��� ������ ����������:
    - `EOFError` -- ���� ��� ������ ��� ������ �� ����� �����-������;
    - `StopIteration` -- ���� ��������� ���������� `halt`.
    - `MachineException` -- ����������� ������ ������ (������ ����������, ������� �� ���� � ��)
- ���������� ���������� ����������� � ������� `simulate`.

## ���������

� �������� ������ ������������ ��� ���������:

1. [hello world](asm/hello_world.asm) -- ��������� ������� "Hello, world!"
2. [cat](asm/cat.asm) -- ��������� `cat`, ��������� ���� �� ������.
2. [prob5](asm/prob5.asm) -- �������� ������, ������� ����������� �����, ������� ������� �� ��� ����� �� 1 �� 20

�������������� ����� ����������� ���: [integration_test](integration_test.py) � ���� golden tests, ������������ ������� ����� � ����� [golden](golden)

CI:

``` yaml
Test:
  stage: test
  image:
    name: python-tools
    entrypoint: [ "" ]
  script:
    - cd src
    - pip3 install --no-cache-dir -r requirements.txt
    - python3 -m pytest --verbose
    - apt install pylint
    - pylint --max-line-length=120 ./translator/deserializer.py ./utils.py ./translator/validator.py ./machine/acc_machine.py
```

���:

- `pytest` -- ������� ��� ������� ������.
- `pylint` -- ������� ��� �������� �������� ����. ��������� ������� ��������� � ��������� ������� � ����� ��������� ����.

������ ������������� � ������ ������ ���������� �� ������� `cat`:

``` console
> cat asm/cat.asm
section .interrupt
	LD	STDIN
	CMP	NULL_TERM
	JZ	.handle_end_symbol
	ST	STDOUT
	JMP	.end_interrupt
	.handle_end_symbol:
		LD	#0
		ST	CHECK_END
		
		.end_interrupt:
			EI

section .data
	NULL_TERM: 10
	CHECK_END: 1
	
section .text
.start:
		LD	#0	
		.loop:
			CMP	CHECK_END
			JNZ	.loop
		.end:
			HLT
> cat input/interrupt.json 
[
    {"tick": 1, "char": "f"},
    {"tick": 2, "char": "o"},
    {"tick": 6, "char": "o"},
    {"tick": 45, "char": "\n"}
]

> ./translator/program_translator.py asm/cat.asm target.out
Program successfully translated!
LoC: 22
Code: 14
> ./machine/acc_machine.py target.out examples/interrupt.json
Machine - DEBUG - {TICK: 0, PC: 102, AR: 0, DR: 0, ACC: 0, Z: False} LD ArgType.VAL 0
Machine - DEBUG - {TICK: 3, PC: 103, AR: 0, DR: 0, ACC: 0, Z: True} CMP ArgType.ADDR 101
Machine - DEBUG - Interrupt TICK: {3}
Machine - DEBUG - 0 -> MEM(90)
Machine - DEBUG - 1 -> MEM(91)
Machine - DEBUG - 103 -> MEM(92)
Machine - DEBUG - input -> f
Machine - DEBUG - {TICK: 15, PC: 11, AR: 0, DR: 102, ACC: 102, Z: False} CMP ArgType.ADDR 100
Machine - DEBUG - {TICK: 19, PC: 12, AR: 100, DR: 10, ACC: 102, Z: False} JZ ArgType.VAL 15
Machine - DEBUG - {TICK: 20, PC: 13, AR: 100, DR: 10, ACC: 102, Z: False} ST ArgType.STDOUT 1
Machine - DEBUG - f -> output
Machine - DEBUG - {TICK: 23, PC: 14, AR: 1, DR: 10, ACC: 102, Z: False} JMP ArgType.VAL 17
Machine - DEBUG - {TICK: 25, PC: 17, AR: 1, DR: 17, ACC: 102, Z: False} EI  --   -- 
Machine - DEBUG - Interrupt end!
Machine - DEBUG - {TICK: 34, PC: 103, AR: 90, DR: 0, ACC: 0, Z: True} CMP ArgType.ADDR 101
Machine - DEBUG - Interrupt TICK: {34}
Machine - DEBUG - 0 -> MEM(90)
Machine - DEBUG - 1 -> MEM(91)
Machine - DEBUG - 103 -> MEM(92)
Machine - DEBUG - input -> o
Machine - DEBUG - {TICK: 46, PC: 11, AR: 0, DR: 111, ACC: 111, Z: False} CMP ArgType.ADDR 100
Machine - DEBUG - {TICK: 50, PC: 12, AR: 100, DR: 10, ACC: 111, Z: False} JZ ArgType.VAL 15
Machine - DEBUG - {TICK: 51, PC: 13, AR: 100, DR: 10, ACC: 111, Z: False} ST ArgType.STDOUT 1
Machine - DEBUG - o -> output
Machine - DEBUG - {TICK: 54, PC: 14, AR: 1, DR: 10, ACC: 111, Z: False} JMP ArgType.VAL 17
Machine - DEBUG - {TICK: 56, PC: 17, AR: 1, DR: 17, ACC: 111, Z: False} EI  --   -- 
Machine - DEBUG - Interrupt end!
Machine - DEBUG - {TICK: 65, PC: 103, AR: 90, DR: 0, ACC: 0, Z: True} CMP ArgType.ADDR 101
Machine - DEBUG - Interrupt TICK: {65}
Machine - DEBUG - 0 -> MEM(90)
Machine - DEBUG - 1 -> MEM(91)
Machine - DEBUG - 103 -> MEM(92)
Machine - DEBUG - input -> o
Machine - DEBUG - {TICK: 77, PC: 11, AR: 0, DR: 111, ACC: 111, Z: False} CMP ArgType.ADDR 100
Machine - DEBUG - {TICK: 81, PC: 12, AR: 100, DR: 10, ACC: 111, Z: False} JZ ArgType.VAL 15
Machine - DEBUG - {TICK: 82, PC: 13, AR: 100, DR: 10, ACC: 111, Z: False} ST ArgType.STDOUT 1
Machine - DEBUG - o -> output
Machine - DEBUG - {TICK: 85, PC: 14, AR: 1, DR: 10, ACC: 111, Z: False} JMP ArgType.VAL 17
Machine - DEBUG - {TICK: 87, PC: 17, AR: 1, DR: 17, ACC: 111, Z: False} EI  --   -- 
Machine - DEBUG - Interrupt end!
Machine - DEBUG - {TICK: 96, PC: 103, AR: 90, DR: 0, ACC: 0, Z: True} CMP ArgType.ADDR 101
Machine - DEBUG - Interrupt TICK: {96}
Machine - DEBUG - 0 -> MEM(90)
Machine - DEBUG - 1 -> MEM(91)
Machine - DEBUG - 103 -> MEM(92)

Machine - DEBUG - {TICK: 108, PC: 11, AR: 0, DR: 10, ACC: 10, Z: False} CMP ArgType.ADDR 100
Machine - DEBUG - {TICK: 112, PC: 12, AR: 100, DR: 10, ACC: 10, Z: True} JZ ArgType.VAL 15
Machine - DEBUG - {TICK: 114, PC: 15, AR: 100, DR: 15, ACC: 10, Z: True} LD ArgType.VAL 0
Machine - DEBUG - {TICK: 117, PC: 16, AR: 100, DR: 0, ACC: 0, Z: True} ST ArgType.ADDR 101
Machine - DEBUG - 0 -> MEM(101)
Machine - DEBUG - {TICK: 120, PC: 17, AR: 101, DR: 0, ACC: 0, Z: True} EI  --   -- 
Machine - DEBUG - Interrupt end!
Machine - DEBUG - {TICK: 129, PC: 103, AR: 90, DR: 0, ACC: 0, Z: True} CMP ArgType.ADDR 101
Machine - DEBUG - {TICK: 133, PC: 104, AR: 101, DR: 0, ACC: 0, Z: True} JNZ ArgType.VAL 103
Machine - DEBUG - {TICK: 134, PC: 105, AR: 101, DR: 0, ACC: 0, Z: True} HLT  --   -- 
Output: foo
Instructions: 28
Ticks: 135
```

| ���           | ���.  | LoC       | code ���� | code �����.  | �����. | ����. | ������� |
|---------------|-------|-----------|-----------|--------------|--------|-------|---------|
| ������� �.�.  | hello | 14        | -         | 25           | 112    | 419   | ...     |
| ������� �.�.  | cat   | 22        | -         | 14           | 28     | 135   | ...     |
| ������� �.�.  | prob5 | 28        | -         | 23           | 2730   | 8171  | ...     |

