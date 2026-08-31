"""PCC 编译器公共工具函数（现代化版本，替代 other/function.py）。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Any

# 运算符表
OPERATORS = {
    "+", "-", "*", "/", "<", "<=", ">", ">=", "=", "==", "!=", "^", ",",
    "&", "&&", "|", "||", "%", "~", "<<", ">>", "!",
}

# 分隔符表
SEPARATORS = {";", "(", ")", "[", "]", "{", "}", ".", ":", '"', "#", "'", "\\", "?"}

# 关键字表（与原版 lexer.py 一致：不含数据类型关键字，类型走 TYPES 分支标为 'type'）
KEYWORDS = {
    "auto", "break", "case", "const", "continue", "default", "do", "else",
    "enum", "extern", "for", "goto", "if", "register", "return", "short",
    "signed", "sizeof", "static", "struct", "switch", "typedef", "union",
    "volatile", "while", "printf",
}

# 比较运算符
COMPARISONS = ["<", ">", "==", "!=", "<=", ">="]

# 数据类型
TYPES = {"int", "float", "char", "double", "void", "long", "unsigned", "string"}

_NUM_RE = re.compile(r"^[0-9]+(\.[0-9]*)?$")
_NAME_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*")


def is_number(word: Any) -> bool:
    """判断是否为数字字面量。"""
    return isinstance(word, str) and bool(_NUM_RE.match(word))


def is_name(word: Any) -> bool:
    """判断是否为合法的变量名。"""
    return isinstance(word, str) and bool(_NAME_RE.match(word))


def has_name(name_list: Iterable[dict], name: str) -> bool:
    """判断变量名是否已存在于符号表中。"""
    return any(item.get("name") == name for item in name_list)


def print_lines(items: Iterable[Any]) -> None:
    """逐行打印列表元素。"""
    for item in items:
        print(item)


def get_word(filename: str | Path) -> list[dict[str, str]]:
    """读取源代码文件，按空白、运算符、分隔符切分为单词序列。

    返回列表，元素为 {"word": str, "line": str}。
    支持 // 行注释 与 /* ... */ 块注释。
    """
    text = Path(filename).read_text(encoding="utf-8")
    out_words: list[dict[str, str]] = []
    line_num = 0
    pass_block = False  # 是否处于 /* ... */ 块注释中

    for raw_line in text.splitlines():
        line_num += 1
        words = raw_line.split()
        for w in words:
            # 去除注释
            if "*/" in w:
                pass_block = False
                continue
            if "//" in w or pass_block:
                break
            if "/*" in w:
                pass_block = True
                break
            # 完整比较运算符（两个字符）
            if w in COMPARISONS:
                out_words.append({"word": w, "line": str(line_num)})
                continue
            ws = w
            for a in w:
                if a in SEPARATORS or a in OPERATORS:
                    index = ws.find(a)
                    if index != 0:
                        out_words.append({"word": ws[0:index], "line": str(line_num)})
                    ws = ws[index + 1:]
                    out_words.append({"word": a, "line": str(line_num)})
            if ws != "":
                out_words.append({"word": ws, "line": str(line_num)})
    return out_words
