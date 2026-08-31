"""中间代码转汇编代码（x86-64 AT&T 语法）。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

from pathlib import Path

from .generate import creat_mcode
from .utils import is_number

_GLOBAL_HEAD = """;----------------------Welcome to Pcc--------------------------
; by 兰州小红鸡
;-------------------------------------------------------------------
"""

_CODE_HEAD = """
\t.cfi_startproc
\tpushq\t%rbp
\t.cfi_def_cfa_offset 16
\t.cfi_offset 6, -16
\tmovq\t%rsp, %rbp
\t.cfi_def_cfa_register 6
"""

_CODE_FOOTER = """
\tmovl\t$0, %eax
\tleave
\t.cfi_def_cfa 7, 8
\tret
\t.cfi_endproc
.LFE6:
\t.size\tmain, .-main
\t.ident\t"PCC: 2.0.0"
"""


class AsmGen:
    """四元式 → x86-64 汇编代码生成器。"""

    def __init__(self) -> None:
        self.lc: int = 0    # 字符串常量计数
        self.re: str = ""   # 汇编代码缓存

    # ------------------------------------------------------------------
    # 变量寻址
    # ------------------------------------------------------------------
    def args(self, n: object, name: dict) -> str:
        """将变量名解析为汇编寻址方式。

        支持：栈上变量 / 数组寻址 / 临时变量 / 立即数。
        """
        s = str(n)
        if s in name:
            return "-" + name[s][0] + "(%rbp)"
        elif "[]" in s:
            ags = s.split("[]")
            if is_number(ags[1]):
                if name[ags[0]][1] == "char":
                    return "-" + str(int(name[ags[0]][0]) - int(ags[1])) + "(%rbp)"
                elif name[ags[0]][1] == "int":
                    return "-" + str(int(name[ags[0]][0]) - int(ags[1]) * 4) + "(%rbp)"
            else:
                self.re += "\tmovl\t" + self.args(ags[1], name) + ", %eax\n\tcltq\n"
                if name[ags[0]][1] == "char":
                    return "-" + name[ags[0]][0] + "(%rbp, %rax, 1)"
                elif name[ags[0]][1] == "int":
                    return "-" + name[ags[0]][0] + "(%rbp, %rax, 4)"
        elif "T" in s:
            return s + "(%rip)"
        elif is_number(s):
            return "$" + s
        else:
            return s
        return s

    # ------------------------------------------------------------------
    # 变量 / 字符串初始化
    # ------------------------------------------------------------------
    def init_data(self, name_list: list[dict], arrs: dict) -> tuple[dict, int]:
        """为变量分配栈上地址，返回 (地址表, 栈帧高度)。"""
        result: dict = {}
        i = 0
        for n in name_list:
            if n["name"] != "main":
                if n["flag"] == "int":
                    i += 4
                    result[n["name"]] = [str(i), "int"]
                elif n["flag"] == "char":
                    i += 1
                    result[n["name"]] = [str(i), "char"]
        for a in arrs:
            if arrs[a][1] == "int":
                i += int(arrs[a][0]) * 4
                result[a] = [str(i), "int"]
            elif arrs[a][1] == "char":
                i += int(arrs[a][0])
                result[a] = [str(i), "char"]
        return result, (int(i / 12) + 1) * 12

    def init_string(self, strings: list[str]) -> str:
        """生成字符串常量段（.LC 标签）。"""
        out = ""
        for i, s in enumerate(strings):
            out += f".LC{i}:\n\t.string \"{s}\"\n"
        return out

    # ------------------------------------------------------------------
    # 汇编指令生成
    # ------------------------------------------------------------------
    def generate_code(self, mid_code: list, name: dict) -> str:
        """根据四元式序列生成汇编指令。"""
        self.re = ""
        for m in mid_code:
            a1 = self.args(m.arg1, name)
            a2 = self.args(m.arg2, name)
            r = self.args(m.re, name)

            if m.op == "=":
                if m.re in name and name[m.re][1] == "char":
                    self.re += f"\tmovb\t${ord(m.arg1)}, {r}\n"
                elif m.arg1 in name or "T" in str(m.arg1) or "[]" in str(m.arg1):
                    self.re += f"\tmovl\t{a1}, %ecx\n"
                    self.re += f"\tmovl\t%ecx, {r}\n"
                else:
                    self.re += f"\tmovl\t{a1}, {r}\n"

            elif m.op == "code_block":
                self.re += f".{m.re}:\n"
                continue

            elif "j" in m.op:
                if m.op == "j":
                    self.re += f"\tjmp\t.{m.re}\n"
                else:
                    self.re += f"\tmovl\t{a1}, %eax\n"
                    self.re += f"\tcmpl\t{a2}, %eax\n"
                    if ">" in m.op:
                        self.re += f"\tjg\t.{m.re}\n"
                    elif "<" in m.op:
                        self.re += f"\tjle\t.{m.re}\n"
                    elif "=" in m.op:
                        self.re += f"\tje\t.{m.re}\n"

            elif m.op in "+-":
                self.re += f"\tmovl\t{a1}, %edx\n"
                self.re += f"\tmovl\t{a2}, %eax\n"
                if m.op == "+":
                    self.re += "\taddl\t%edx, %eax\n"
                else:
                    self.re += "\tsubl\t%edx, %eax\n"
                self.re += f"\tmovl\t%eax, {r}\n"

            elif m.op in "*/":
                if m.arg1 in name:
                    self.re += f"\tmovl\t{a2}, %eax\n"
                    self.re += f"\timull\t{a1}, %eax\n"
                    self.re += f"\tmovl\t%eax, {r}\n"
                elif m.arg2 in name and m.arg1 not in name:
                    self.re += f"\tmovl\t{a2}, %eax\n"
                    self.re += f"\timull\t{a1}, %eax, %eax\n"
                    self.re += f"\tmovl\t%eax, {r}\n"
                elif m.arg2 not in name and m.arg1 not in name:
                    num = int(m.arg2) * int(m.arg1)
                    self.re += f"\tmovl\t${num}, {r}\n"

            elif m.op == "print":
                if m.arg1 != "-1":
                    if m.arg1 in name and name[m.arg1][1] == "char":
                        self.re += f"\tmovsbl\t{a1}, %eax\n"
                    else:
                        self.re += f"\tmovl\t{a1}, %eax\n"
                if m.arg2 != "-1":
                    if m.arg2 in name and name[m.arg2][1] == "char":
                        self.re += f"\tmovsbl\t{a2}, %edx\n"
                    else:
                        self.re += f"\tmovl\t{a2}, %edx\n"
                if m.re != "-1":
                    if m.re in name and name[m.re][1] == "char":
                        self.re += f"\tmovsbl\t{r}, %ecx\n"
                    else:
                        self.re += f"\tmovl\t{r}, %ecx\n"
                self.re += "\tmovl\t%eax, %esi\n" + f"\tleaq\t.LC{self.lc}(%rip), %rdi\n"
                self.lc += 1
                self.re += "\tmovl\t$0, %eax\n\tcall\tprintf@PLT\n"

        return self.re

    # ------------------------------------------------------------------
    # 拼接完整汇编
    # ------------------------------------------------------------------
    def connect(self, tmp: int, strs: str, code: str, subq: int) -> str:
        data = ""
        for i in range(0, tmp):
            data += f"\t.comm\tT{i},4,4\n"
        return (
            "\t.text\n\t.section\t.rodata\n" + data + strs +
            "\t.text\n\t.globl\tmain\n\t.type\tmain, @function\nmain:\n" + _CODE_HEAD +
            f"\tsubq\t${subq}, %rsp\n" + code + _CODE_FOOTER
        )

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------
    def to_asm(self, filename: str) -> str:
        """编译 C 源码，生成 .s 汇编文件，返回汇编文本。"""
        self.lc = 0
        mid_result = creat_mcode(filename)
        mid_code = mid_result["mid_code"]
        name_list = mid_result["name_list"]
        tmp = mid_result["tmp"]
        strings = mid_result["strings"]
        arrs = mid_result["arrs"]

        name = self.init_data(name_list, arrs)
        string_list = self.init_string(strings)
        asm = self.generate_code(mid_code, name[0])
        result = self.connect(tmp, string_list, asm, name[1])

        out_path = Path(filename[:-1] + "s")
        out_path.write_text(result, encoding="utf-8")
        return result


def to_asm(filename: str) -> str:
    """兼容旧接口：编译 C 源码生成 .s 汇编文件。"""
    return AsmGen().to_asm(filename)


def main() -> None:
    to_asm("./test/test.c")


if __name__ == "__main__":
    main()
