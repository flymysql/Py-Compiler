# PCC —— Python 实现的 C 语言编译器

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

编译原理课程设计：实现 C 语言子集到 **x86-64 汇编** 的完整编译器，链接部分使用 gcc。

**流水线：词法分析 → LL(1) 预测分析 → 语法树 → 四元式中间代码 → x86-64 汇编**

## ✨ 2026 现代化升级（v2.0）

- **Python 3.10+**：`dataclass`（Token / Mnode / Node）、类型标注、`pathlib`、f-string
- **包结构**：代码重组为 `pcc/` 包，支持 `pip install` 与 `pcc` 命令行
- **CLI 重构**：`argparse` 标准参数解析；**移除 `os.system()` 执行用户输入的隐患**
- **测试套件**：14 个 pytest 用例（词法 / 语法 / 中间代码 / 汇编 / gcc 端到端）
- **行为兼容**：生成的四元式与汇编与 v1.0 逐字节一致（仅 `.ident` 版本号变化）
- 旧版代码保留在 [`legacy/`](legacy/) 供学习对比

## 安装

```bash
pip install .            # 安装为 pcc 命令
# 或直接使用：
python -m pcc.cli -h
```

## 使用

```bash
pcc -o <file.c>      # 直接编译生成可执行程序（需 gcc）
pcc -s <file.c>      # 生成汇编源码 (.s)
pcc -m <file.c>      # 查看生成的四元式（中间代码）
pcc -t <file.c>      # 查看语法树生成过程
pcc -l <file.c>      # 查看词法分析
pcc -p               # 查看预测分析表
pcc -g               # 查看语法推导
pcc -v               # 显示版本
pcc                  # 交互模式
```

## 测试

```bash
pip install pytest
python -m pytest tests/ -v
```

## 源码结构

| 模块 | 职责 |
|---|---|
| `pcc/utils.py` | 公共工具函数（切词、判断、符号表） |
| `pcc/lexer.py` | 词法分析器（Token dataclass） |
| `pcc/get_predict_table.py` | FIRST/FOLLOW 集合与 LL(1) 预测分析表 |
| `pcc/lr.py` | 非递归预测分析（语法树生成） |
| `pcc/generate.py` | 中间代码生成（四元式） |
| `pcc/to_asm.py` | x86-64 汇编生成 |
| `pcc/cli.py` | 命令行入口 |
| `tests/` | pytest 测试套件 |
| `legacy/` | v1.0 原始代码（存档） |

## 支持的语法

1. **声明与赋值**
```c
int a;
a = 10;
int b = a;
```
2. **混合四则运算**
```c
int a = 1 + 2*(3 - 4);
```
3. **数组**（下标支持嵌套表达式）
```c
int arr[10];
a[0] = 1;
int b = a[0];
arr[arr[(index+1)*2-1]] = 7;
```
4. **printf 输出**（最多三个参数，支持表达式）
```c
printf("三个参数：%d,%d,%d",a,b,c);
printf("%d", d + 2*(3+4));
```
5. **if 嵌套**
```c
if(a < 2*10){
	a = a + 1;
	if(c < a){
		printf("%d", a*c);
	}
}
```
6. **while 嵌套**

## 示例：打印 99 乘法表

```c
int main(){
    int i = 1;
    printf("正在由pcc编译器为你打印99乘法表！\n");
    while(i < 10){
        int j = i;
        while(j < 10){
            printf("%d*%d=%d\t",i, j, i*j);
            j = j + 1;
        }
        printf("\n");
        i = i +1;
    }
}
```

```bash
$ pcc -o test/99mul.c
编译成功，执行：test/99mul
1*1=1	1*2=2	1*3=3	1*4=4	1*5=5	...
```

## 生成的汇编示例

```s
	.text
	.section	.rodata
.LC0:
	.string "f(%d)=%d\n"
	.text
	.globl	main
	.type	main, @function
main:
	.cfi_startproc
	pushq	%rbp
	...
	call	printf@PLT
```

## License

[MIT](LICENSE) © flymysql
