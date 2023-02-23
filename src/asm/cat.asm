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