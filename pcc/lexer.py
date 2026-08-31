"""PCC 词法分析器（现代化版本）。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .utils import (
    COMPARISONS,
    KEYWORDS,
    OPERATORS,
    SEPARATORS,
    TYPES,
    get_word,
    has_name,
    is_name,
    is_number,
    print_lines,
)


@dataclass
class Token:
    """一个词法单元。"""

    line: int
    type: str
    word: str
    id: Optional[int] = None

    def __str__(self) -> str:
        if self.id is not None:
            return f"{{'line': {self.line}, 'type': '{self.type}', 'word': '{self.word}', 'id': {self.id}}}"
        return f"{{'line': {self.line}, 'type': '{self.type}', 'word': '{self.word}'}}"

    __repr__ = __str__


# 括号配对
_KUO_CP = {"{": "}", "[": "]", "(": ")"}


class LexError(Exception):
    """词法分析错误。"""


# 词法分析时记录最近的数据类型，供符号表登记
_current_type = ""


def type_flag(value: str | None = None) -> str:
    """读写当前数据类型标记（保持与原实现行为一致）。"""
    global _current_type
    if value is not None:
        _current_type = value
    return _current_type


class Lexer:
    """词法分析器：将 C 源码切分为单词表，并分类存入各符号表。"""

    def __init__(self, filename: str = "test.c"):
        self.word_list: list[Token] = []       # 输出单词表
        self.separator_list: list[Token] = []  # 分隔符
        self.operator_list: list[Token] = []   # 运算符
        self.name_list: list[dict] = []        # 变量表
        self.key_word_table: list[Token] = []  # 关键字
        self.string_list: list[str] = []       # 字符串常量
        self.flag: bool = True                 # 源码是否正确

        self._build_tables(get_word(filename))

    def _build_tables(self, in_words: list[dict[str, str]]) -> None:
        name_id = 0
        kuo_list: list[tuple[str, int]] = []   # 括号栈 (符号, 行号)
        char_flag = False
        str_flag = False
        strings = ""
        chars = ""

        for item in in_words:
            w = item["word"]
            line = int(item["line"])

            # 字符串字面量
            if w == '"':
                if not str_flag:
                    str_flag = True
                else:
                    str_flag = False
                    self.word_list.append(Token(line, "TEXT", strings))
                    self.string_list.append(strings)
                    strings = ""
                continue
            if str_flag:
                strings += w
                continue

            # 字符字面量
            if w == "'":
                if not char_flag:
                    char_flag = True
                else:
                    char_flag = False
                    self.word_list.append(Token(line, "CHAR", chars))
                    chars = ""
                continue
            if char_flag:
                chars += w
                continue

            # 关键字
            if w in KEYWORDS:
                self.key_word_table.append(Token(line, "keyword", w))
                self.word_list.append(Token(line, w, w))
            elif w in COMPARISONS:
                self.word_list.append(Token(line, "Cmp", w))
            # 数据类型
            elif w in TYPES:
                type_flag(w)
                self.key_word_table.append(Token(line, "type", w))
                self.word_list.append(Token(line, "type", w))
            # 运算符
            elif w in OPERATORS:
                self.operator_list.append(Token(line, "operator", w))
                self.word_list.append(Token(line, w, w))
            # 分隔符
            elif w in SEPARATORS:
                if w in _KUO_CP:
                    # 左括号入栈
                    kuo_list.append((w, line))
                elif w in _KUO_CP.values():
                    # 右括号：匹配则弹出，否则报错
                    if kuo_list and w == _KUO_CP[kuo_list[-1][0]]:
                        kuo_list.pop()
                    else:
                        raise LexError(
                            f"第 {line} 行的 '{w}' 无法匹配括号，请检查代码正确性！"
                        )
                # 其余分隔符（; , . 等）无需括号配对
                self.separator_list.append(Token(line, "separator", w))
                self.word_list.append(Token(line, w, w))
            # 数字 / 变量名 / 错误
            else:
                if is_number(w):
                    self.word_list.append(Token(line, "number", w))
                elif is_name(w):
                    if has_name(self.name_list, w):
                        self.word_list.append(Token(line, "name", w, name_id))
                    else:
                        self.name_list.append(
                            {"line": line, "id": name_id, "word": 0.0, "name": w, "flag": type_flag()}
                        )
                        self.word_list.append(Token(line, "name", w, name_id))
                        name_id += 1
                else:
                    raise LexError(
                        f"第 {line} 行的变量名 '{w}' 不可识别，请检查代码正确性！"
                    )

        if kuo_list:
            sym, line = kuo_list[0]
            raise LexError(f"第 {line} 行的 '{sym}' 无法匹配括号，请检查代码正确性！")


class word_list(Lexer):
    """向后兼容的旧类名（原接口为 word_list(filename)）。"""

    def __init__(self, filename: str = "test.c"):
        super().__init__(filename)


def main() -> None:
    filename = input("请输入要编译的.c文件: ") or "test/test.c"
    w_list = Lexer(filename)
    if w_list.flag:
        print("\n输出字符串如下")
        print_lines(w_list.word_list)
        print("\n\n输出变量表如下\n")
        print_lines(w_list.name_list)


if __name__ == "__main__":
    main()
