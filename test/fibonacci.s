	.text
	.section	.rodata
	.comm	T0,4,4
	.comm	T1,4,4
	.comm	T2,4,4
	.comm	T3,4,4
.LC0:
	.string "f(%d)=%d\n"
.LC1:
	.string "完成斐波那契数列打印！由小鸡编译器提供——pcc\n"
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
	subq	$120, %rsp
	movl	$0, -8(%rbp)
	movl	$1, -112(%rbp)
	movl	$2, -108(%rbp)
	movl	$3, -104(%rbp)
.W4:
	movl	-8(%rbp), %eax
	cmpl	$20, %eax
	jle	.code6
	jmp	.block6
.code6:
	movl	-8(%rbp), %eax
	cltq
	movl	-112(%rbp, %rax, 4), %ecx
	movl	%ecx, -12(%rbp)
	movl	-8(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T0(%rip)
	movl	T0(%rip), %eax
	cltq
	movl	-112(%rbp, %rax, 4), %edx
	movl	-12(%rbp), %eax
	addl	%edx, %eax
	movl	%eax, T1(%rip)
	movl	-8(%rbp), %edx
	movl	$2, %eax
	addl	%edx, %eax
	movl	%eax, T2(%rip)
	movl	T2(%rip), %eax
	cltq
	movl	T1(%rip), %ecx
	movl	%ecx, -112(%rbp, %rax, 4)
	movl	-8(%rbp), %eax
	movl	-12(%rbp), %edx
	movl	%eax, %esi
	leaq	.LC0(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
	movl	-8(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T3(%rip)
	movl	T3(%rip), %ecx
	movl	%ecx, -8(%rbp)
	jmp	.W4
.block6:
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
