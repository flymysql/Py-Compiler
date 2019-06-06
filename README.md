## PCC——python实现编译器

编译原理课设，实现源码到汇编代码的翻译，链接部分使用gcc的功能

## 源码说明

1. lexer.py     词法分析器
2. get_predict_table.py     生成预测分析表
3. LR.py        非递归的语法分析器
4. generate.py  中间代码生成
5. to_asm.py    汇编代码生成
6. pcc.py       入口函数

## 使用

```python
$ python pcc.py
```

**命令说明**

```
pcc -o (filename)       直接编译生成可执行程序
pcc -s (filename)       生成汇编源码
pcc -t (filename)       查看语法树生成过程
pcc -l (filename)       查看词法分析
pcc -h                  查看帮助
pcc -p                  查看本编译器的预测分析表
pcc -g                  查看本编译器的语法推导
exit                    退出
```

![](./other/help.png)

### 编译代码

```
pcc -o ./test/test.c
```
![](./other/pcc-o.png)

**ｃ语言源码**

```c
// 兰州小红鸡的注释测试
int main(){
    int a = 1;
    int b = 1;
    int c = 2;
    int index = 0;
    // 求０～２０的斐波那契数列
    while(index < 10 ){
        int tmp = c;
        c = c+b;
        a = b;
        b = tmp;
        index = index + 1;
        printf("f(%d) = %d\n", index,a);
    }
    printf("斐波那契数列打印完成，由小鸡编译器提供\n");
}
```

**生成的中间代码（四元式）**

```
(=,1,0,a)
(=,1,0,b)
(=,2,0,c)
(=,0,0,index)
(code_block,0,0,W4)
(j<,index,10,code6)
(j,0,0,block6)
(code_block,0,0,code6)
(=,c,0,tmp)
(+,c,b,T0)
(=,T0,0,c)
(=,b,0,a)
(=,tmp,0,b)
(+,index,1,T1)
(=,T1,0,index)
(print,index,a,-1)
(j,0,0,W4)
(code_block,0,0,block6)
(print,-1,-1,-1)
```

**生成的汇编代码**

```s
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

```

其他命令自行发觉hhh