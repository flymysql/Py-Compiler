	.text
	.section	.rodata
	.comm	T0,4,4
	.comm	T1,4,4
	.comm	T2,4,4
.LC0:
	.string "正在由小pcc编译器为你打印99乘法表！\n"
.LC1:
	.string "%d*%d=%d\t"
.LC2:
	.string "\n"
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
	subq	$12, %rsp
	movl	$1, -4(%rbp)
	movl	%eax, %esi
	leaq	.LC0(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
.W2:
	movl	-4(%rbp), %eax
	cmpl	$10, %eax
	jle	.code4
	jmp	.block4
.code4:
	movl	-4(%rbp), %ecx
	movl	%ecx, -8(%rbp)
.W7:
	movl	-8(%rbp), %eax
	cmpl	$10, %eax
	jle	.code9
	jmp	.block9
.code9:
	movl	-8(%rbp), %eax
	imull	-4(%rbp), %eax
	movl	%eax, T0(%rip)
	movl	-4(%rbp), %eax
	movl	-8(%rbp), %edx
	movl	T0(%rip), %ecx
	movl	%eax, %esi
	leaq	.LC1(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
	movl	-8(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T1(%rip)
	movl	T1(%rip), %ecx
	movl	%ecx, -8(%rbp)
	jmp	.W7
.block9:
	movl	%eax, %esi
	leaq	.LC2(%rip), %rdi
	movl	$0, %eax
	call	printf@PLT
	movl	-4(%rbp), %edx
	movl	$1, %eax
	addl	%edx, %eax
	movl	%eax, T2(%rip)
	movl	T2(%rip), %ecx
	movl	%ecx, -4(%rbp)
	jmp	.W2
.block4:

	movl	$0, %eax
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	main, .-main
	.ident	"PCC: 1.0.0"
