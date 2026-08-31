"""非递归预测分析（LL(1)）——语法树生成。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .get_predict_table import creat_predict_table
from .lexer import Token

predict_table = creat_predict_table()


class ParseError(Exception):
    """语法分析错误。"""


@dataclass
class Node:
    """语法树节点。"""

    type: str
    text: Optional[str] = None
    child: list["Node"] = field(default_factory=list)

    def __str__(self) -> str:
        childs = [child.__str__() for child in self.child]
        out = f"<{self.type}, {self.text}>"
        for child in childs:
            if child:
                for line in child.split("\n"):
                    out = out + "\n     " + line
        return out

    __repr__ = __str__


def stack_text(stack: list[Node]) -> list[str]:
    """输出栈中节点的 type。"""
    return [s.type for s in stack]


def analysis(word_table: list, show: bool = False) -> tuple[bool, Optional[Node]]:
    """基于预测分析表的非递归语法分析，返回 (是否成功, 语法树根节点)。

    word_table: 词法分析器输出的单词表（Token 对象或 dict，需有 type / word 字段）
    show:       是否打印分析过程
    """
    stack: list[Node] = []
    root = Node("Program")
    end = Node("#")
    stack.append(end)
    stack.append(root)
    index = 0

    def tok_type(i: int) -> str:
        item = word_table[i]
        return item.type if isinstance(item, Token) else item["type"]

    def tok_word(i: int) -> str:
        item = word_table[i]
        return item.word if isinstance(item, Token) else item["word"]

    def tok_line(i: int) -> object:
        item = word_table[i]
        return getattr(item, "line", None) if isinstance(item, Token) else item.get("line")

    while len(stack) != 0:
        cur = stack.pop()

        # 状态 1: 解析完成
        if cur.type == "#" and len(stack) == 0:
            print("分析完成!")
            return True, root

        # 状态 2: 终结符匹配
        elif index < len(word_table) and cur.type == tok_type(index):
            if show:
                print("符号栈：", stack_text(stack), "\n匹配字符: ", tok_word(index))
            cur.text = tok_word(index)
            index += 1

        # 状态 3: 非终结符展开
        else:
            w = tok_type(index) if index < len(word_table) else "#"
            if cur.type in predict_table and w in predict_table[cur.type]:
                if predict_table[cur.type][w] == "null":
                    continue
                next_pr = predict_table[cur.type][w].split()
                if show:
                    print("\n符号栈：", stack_text(stack), "\n产生式: ", cur.type, "->", predict_table[cur.type][w])
                node_list = [Node(np) for np in next_pr]
                cur.child.extend(node_list)
                node_list.reverse()
                stack.extend(node_list)
            # 状态 4: 错误
            else:
                line_info = f" (第 {tok_line(index)} 行)" if index < len(word_table) else "（输入结束）"
                raise ParseError(f"语法错误: 期望 {cur.type}，但遇到 {w}{line_info}")

    return True, root


def main() -> None:
    """命令行入口：分析 test/test.c 并打印语法树。"""
    from .lexer import word_list

    w_list = word_list("./test/test.c")
    ok, root = analysis(w_list.word_list, True)
    if ok:
        print("\n\n是否继续打印语法树？\t1.打印 \t2.任意键退出\tTip：运行 generate.py 输出中间代码（四元式）\n请输入")
        if input() == "1":
            print(root)
            print("\n\n语法树打印完成！运行 generate.py 生成四元式\n\n")


if __name__ == "__main__":
    main()
