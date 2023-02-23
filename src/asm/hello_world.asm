section .data
	S44: "Hello, world!"
	NULL_TERM: 0
    IND: &S44
	
section .text
.start:	LD	*IND
		CMP	NULL_TERM
		JZ	.end
		ST	STDOUT
		LD	IND
		INC	; ADD #1
		ST	IND
		JMP	.start
		
.end:	HLT