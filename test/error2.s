	.file	"error2.c"
	.text
	.section	.rodata
.LC0:
	.string	"f(%d) = %d\n"
	.align 8
.LC1:
	.string	"\346\226\220\346\263\242\351\202\243\345\245\221\346\225\260\345\210\227\346\211\223\345\215\260\345\256\214\346\210\220\357\274\214\347\224\261\345\260\217\351\270\241\347\274\226\350\257\221\345\231\250\346\217\220\344\276\233"
	.text
	.globl	main
	.type	main, @function
main:
.LFB6:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	addq	$-128, %rsp
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	xorl	%eax, %eax
	movl	$1, -124(%rbp)
	movl	$1, -120(%rbp)
	movl	$2, -116(%rbp)
	movl	$2, -128(%rbp)
	movl	$1, -112(%rbp)
	movl	$2, -108(%rbp)
	movl	$3, -104(%rbp)
	jmp	.L2
.L3:
	movl	-128(%rbp), %eax
	subl	$2, %eax
	cltq
	movl	-112(%rbp,%rax,4), %eax
	movl	%eax, -120(%rbp)
	movl	-128(%rbp), %eax
	subl	$1, %eax
	cltq
	movl	-112(%rbp,%rax,4), %eax
	movl	%eax, -116(%rbp)
	movl	-120(%rbp), %edx
	movl	-116(%rbp), %eax
	addl	%eax, %edx
	movl	-128(%rbp), %eax
	cltq
	movl	%edx, -112(%rbp,%rax,4)
	addl	$1, -128(%rbp)
	movl	-116(%rbp), %edx
	movl	-128(%rbp), %eax
	movl	%eax, %esi
	leaq	.LC0(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
.L2:
	cmpl	$19, -128(%rbp)
	jle	.L3
	leaq	.LC1(%rip), %rdi
	call	puts@PLT
	movl	$0, %eax
	movq	-8(%rbp), %rcx
	xorq	%fs:40, %rcx
	je	.L5
	call	__stack_chk_fail@PLT
.L5:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"GCC: (GNU) 8.3.0"
	.section	.note.GNU-stack,"",@progbits
