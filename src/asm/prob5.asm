section .data
	VAL:		116396280
	MAX_DIV:	20
	CNT:		2
	STEP:		969969 ; multiply primes
	
section .text
.start:	
		LD	VAL
		.check_divide:
			MOD	CNT
			JNZ	.value_does_not_match
			LD	CNT
			INC
			ST	CNT
			CMP MAX_DIV
			JZ	.end
			JMP	.start
		
		
.value_does_not_match:
		LD	#2
		ST	CNT
		LD	VAL
		ADD	STEP
		ST	VAL
		JMP	.check_divide
.end:
	LD	VAL
	ST	STDOUT
	HLT