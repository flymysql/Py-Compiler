"""语义分析：中间代码生成——四元式。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .lexer import Lexer
from .lr import Node, analysis
from .utils import is_number

_OPERATOR = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


@dataclass
class Mnode:
    """四元式对象：op, arg1, arg2, result。

    特殊四元式：
    1. (code_block, 0, 0, block1)   代码块开始标记
    2. (j, 0, 0, +2)                跳转语句，往后跳两行
    3. (j<, a, b, block1)           条件跳转 if(a<b) then jmp block1
    4. (print, 0, 0, a)             打印变量 a
    """

    op: str = "undefined"
    arg1: Optional[object] = None
    arg2: Optional[object] = None
    re: Optional[object] = None

    def __str__(self) -> str:
        return f"({self.op},{self.arg1},{self.arg2},{self.re})"

    __repr__ = __str__


class MidCodeGen:
    """四元式中间代码生成器（封装原全局状态）。"""

    def __init__(self) -> None:
        self.mid_result: list[Mnode] = []  # 四元式序列
        self.while_flag: list[list] = []   # while 语句标记栈
        self.arr: dict = {}                # 数组定义
        self.tmp: int = 0                  # 临时变量计数
        self.type_flag: str = ""           # 当前数据类型

    # ------------------------------------------------------------------
    # 递归遍历语法树
    # ------------------------------------------------------------------
    def view_astree(self, root: Optional[Node]) -> Optional[object]:
        if root is None:
            return None
        if root.type == "type":
            self.type_flag = root.text  # type: ignore
        if root.text == "(" or root.text == ")":
            return None
        if len(root.child) == 0 and root.text is not None:
            return root.text
        if root.type == "L":
            self.math_op(root)
        elif root.type == "Pan":
            self.judge(root)
        elif root.type == "OUT":
            self.out(root)
        else:
            result = ""
            for c in root.child:
                cre = self.view_astree(c)
                if cre is not None and str(cre) not in "[]}{)(\"'":
                    result = str(cre)
            return result
        return None

    def math_op(self, root: Optional[Node], ft: Optional[object] = None) -> Optional[object]:
        if root is None:
            return None
        if len(root.child) == 0 and root.text is not None:
            return root.text

        # 变量声明语句：直接赋值 / 不赋值 / 数组
        if root.type == "L":
            c1 = root.child[1]
            if len(c1.child) == 1:
                self.mid_result.append(Mnode("=", 0, 0, self.math_op(root.child[0].child[0])))
            elif c1.child[0].type == "=":
                self.mid_result.append(Mnode("=", self.math_op(c1), 0, self.math_op(root.child[0].child[0])))
            else:
                if len(c1.child[1].child) > 1:
                    cc1 = c1.child[1]
                    self.mid_result.append(Mnode("=", self.math_op(cc1), 0, self.math_op(root.child[0].child[0]) + "[]" + self.math_op(c1.child[0])))
                if str(self.math_op(root.child[0].child[0])) not in self.arr:
                    self.arr[str(self.math_op(root.child[0].child[0]))] = [self.math_op(c1.child[0]), self.type_flag]
                    self.type_flag = ""

        # 表达式：加减（ET）乘除（TT）
        elif root.type == "ET" or root.type == "TT":
            if len(root.child) > 1:
                op = self.math_op(root.child[0])
                arg1 = self.math_op(root.child[1])
                if is_number(str(arg1)) and is_number(str(ft)):
                    return str(_OPERATOR[op](int(arg1), int(ft)))  # type: ignore
                t = "T" + str(self.tmp)
                self.tmp += 1
                self.mid_result.append(Mnode(op, arg1, ft, t))
                ct = self.math_op(root.child[2], t)
                if ct is not None:
                    return ct
                return t

        elif root.type == "E" or root.type == "T":
            if len(root.child[1].child) > 1:
                op = self.math_op(root.child[1].child[0])
                arg1 = self.math_op(root.child[0])
                arg2 = self.math_op(root.child[1].child[1])
                # 静态计算提前算好
                if is_number(str(arg1)) and is_number(str(arg2)):
                    return str(_OPERATOR[op](int(arg1), int(arg2)))  # type: ignore
                t = "T" + str(self.tmp)
                self.tmp += 1
                self.mid_result.append(Mnode(op, arg1, arg2, t))
                ct = self.math_op(root.child[1].child[2], t)
                if ct is not None:
                    return ct
                return t
            else:
                return self.math_op(root.child[0])

        elif root.type == "F" and len(root.child) == 2:
            c = root.child
            if c[1].child and c[1].child[0].type == "Size":
                return str(c[0].child[0].text) + "[]" + str(self.math_op(c[1]))
            else:
                return str(c[0].child[0].text)

        else:
            result = ""
            for c in root.child:
                cre = self.math_op(c)
                if cre is not None and str(cre) not in "[]}{)(\"'":
                    result = str(cre)
            return result
        return None

    # ------------------------------------------------------------------
    # 控制语句（if / while）代码块处理
    # ------------------------------------------------------------------
    def judge(self, root: Optional[Node]) -> Optional[object]:
        if root is None:
            return None
        if len(root.child) == 0 and root.text is not None:
            return root.text
        if root.type == "Ptype":
            if root.child[0].text == "if":
                self.while_flag.append([False])
            else:
                cur = len(self.mid_result)
                self.while_flag.append([True, cur])
                self.mid_result.append(Mnode("code_block", 0, 0, "W" + str(cur)))
        if root.type == "Pbc":
            Pm = root.child[1].child
            if len(Pm) == 1:
                self.mid_result.append(Mnode("j=", 1, self.math_op(root.child[0]), "code" + str(len(self.mid_result) + 1)))
            else:
                self.mid_result.append(Mnode("j" + str(self.judge(Pm[0])), self.math_op(root.child[0]), self.math_op(Pm[1]), "code" + str(len(self.mid_result) + 1)))
            return None
        if root.type == "Pro":
            w = self.while_flag.pop()
            code_block = len(self.mid_result)
            code = "block" + str(code_block)
            self.mid_result.append(Mnode("j", 0, 0, code))
            self.mid_result.append(Mnode("code_block", 0, 0, "code" + str(code_block)))
            self.view_astree(root)
            if w[0]:
                self.mid_result.append(Mnode("j", 0, 0, "W" + str(w[1])))
            self.mid_result.append(Mnode("code_block", 0, 0, code))
            code_block += 1
            return None
        else:
            result = ""
            for c in root.child:
                cre = self.judge(c)
                if cre is not None and str(cre) not in "[]}{)(\"'":
                    result = str(cre)
            return result
        return None

    # ------------------------------------------------------------------
    # 输出语句 printf 处理
    # ------------------------------------------------------------------
    def out(self, root: Optional[Node]) -> None:
        if root is None:
            return
        if root.type == "V":
            if len(root.child) <= 1:
                self.mid_result.append(Mnode("print", "-1", "-1", "-1"))
                return
            else:
                name = [self.math_op(root.child[1])]
                v = root.child[2]
                while len(v.child) > 1:
                    name.append(self.math_op(v.child[1]))
                    v = v.child[2]
                name.extend(["-1", "-1", "-1"])
                self.mid_result.append(Mnode("print", name[0], name[1], name[2]))
        else:
            for c in root.child:
                self.out(c)

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------
    def generate(self, filename: str) -> dict:
        """对 C 源码文件执行完整编译（词法+语法+中间代码），返回编译产物。"""
        self.arr = {}
        self.tmp = 0
        self.mid_result = []
        self.type_flag = ""

        w_list = Lexer(filename)
        word_table = w_list.word_list
        ok, root = analysis(word_table)
        if not ok:
            raise RuntimeError("语法分析失败，无法生成中间代码")
        self.view_astree(root)

        return {
            "name_list": w_list.name_list,
            "mid_code": self.mid_result,
            "tmp": self.tmp,
            "strings": w_list.string_list,
            "arrs": self.arr,
        }


def creat_mcode(filename: str) -> dict:
    """兼容旧接口：生成中间代码（四元式）。"""
    return MidCodeGen().generate(filename)


def main() -> None:
    filename = "test/test.c"
    result = creat_mcode(filename)
    for r in result["mid_code"]:
        print(r)


if __name__ == "__main__":
    main()
