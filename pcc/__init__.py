"""PCC —— Python 实现的 C 语言编译器（现代化版本）。

从源码到 x86-64 汇编的完整教学型编译器：
词法分析 → LL(1) 预测分析 → 语法树 → 四元式中间代码 → 汇编。

模块结构：
- utils:              公共工具函数
- lexer:              词法分析器
- get_predict_table:  预测分析表生成（FIRST/FOLLOW 集合）
- lr:                 非递归预测分析（语法树生成）
- generate:           中间代码生成（四元式）
- to_asm:             汇编代码生成
- cli:                命令行入口
"""

from .lexer import Lexer, Token, word_list
from .lr import Node, analysis

__version__ = "2.0.0"
__all__ = ["Lexer", "Token", "word_list", "Node", "analysis", "__version__"]
