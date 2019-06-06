	.text
	.section	.rodata
	.comm	T0,4,4
	.comm	T1,4,4
.LC0:
	.string "f(%d)=%d\n"
.LC1:
	.string "斐波那契数列打印完成，由小鸡编译器提供\n"
	.text
	.globl	main
	.type	main, @function
main:

	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$32, %rsp
	movl	$1, -8(%rbp)
	movl	$1, -12(%rbp)
	movl	$2, -16(%rbp)
	movl	$0, -20(%rbp)
.W4:
	movl	-20(%rbp), %eax
	cmpl	$10, %eax
	jle	.code6
	jmp	.block6
.code6:
	movl	-16(%rbp), %eax
	movl	%eax, -24(%rbp)
	movl	-16(%rbp), %edx
	movl	-12(%rbp), %eax
	addl	%edx, %eax
	movl	%eax, T0(%rip)
	movl	T0(%rip), %eax
	movl	%eax, -16(%rbp)
	movl	-12(%rbp), %eax
	movl	%eax, -8(%rbp)
	movl	-24(%rbp), %eax
	movl	%eax, -12(%rbp)
	movl	-20(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T1(%rip)
	movl	T1(%rip), %eax
	movl	%eax, -20(%rbp)
	movl	-20(%rbp), %eax
	movl	-8(%rbp), %edx
	movl	%eax, %esi
	leaq	.LC0(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
	jmp	.W4
.block6:
	movl	$-1, %eax
	movl	$-1, %edx
	movl	%eax, %esi
	leaq	.LC1(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT

	movl	$0, %eax
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"PCC: 1.0.0"
