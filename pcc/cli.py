"""PCC 编译器命令行入口（现代化版本）。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from . import __version__
from .generate import creat_mcode
from .get_predict_table import GRAMMARS
from .lexer import Lexer, print_lines
from .lr import analysis
from .to_asm import to_asm

HEAD = f"""
:::PCC编译器——C语言编译器，当前版本 {__version__}
:::作者：小鸡\t项目地址: https://github.com/flymysql/Py-Compiler
:::查看使用帮助：pcc -h
"""

HELP = """\t用法:
\t  pcc -o <filename>   直接编译生成可执行程序（需 gcc）
\t  pcc -s <filename>   生成汇编源码 (.s)
\t  pcc -m <filename>   查看生成的四元式（中间代码）
\t  pcc -t <filename>   查看语法树生成过程
\t  pcc -l <filename>   查看词法分析
\t  pcc -p              查看本编译器的预测分析表
\t  pcc -g              查看本编译器的语法推导
\t  pcc -v              显示版本
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pcc",
        description="PCC —— Python 实现的 C 语言编译器（源码 → x86-64 汇编）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP,
    )
    parser.add_argument("-v", "--version", action="version", version=f"PCC {__version__}")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o", metavar="FILE", help="直接编译生成可执行程序")
    group.add_argument("-s", metavar="FILE", help="生成汇编源码 (.s)")
    group.add_argument("-m", metavar="FILE", help="查看生成的四元式（中间代码）")
    group.add_argument("-t", metavar="FILE", help="查看语法树生成过程")
    group.add_argument("-l", metavar="FILE", help="查看词法分析")
    group.add_argument("-p", action="store_true", help="查看预测分析表")
    group.add_argument("-g", action="store_true", help="查看语法推导")
    return parser


def cmd_o(filename: str) -> None:
    """编译并调用 gcc 生成可执行程序。"""
    try:
        asm = to_asm(filename)
        out_base = filename[:-2]  # 去掉 .c
        gcc_result = subprocess.run(
            ["gcc", filename[:-1] + "s", "-o", out_base],
            capture_output=True, text=True,
        )
        if gcc_result.returncode != 0:
            print("gcc 链接失败：")
            print(gcc_result.stderr)
            sys.exit(1)
        print(f"编译成功，执行：{out_base}")
        # 直接运行产物（可选）
        run = subprocess.run([f"./{out_base}"], capture_output=True, text=True)
        if run.stdout:
            print(run.stdout)
    except FileNotFoundError:
        print("编译失败：未找到 gcc，请先安装 GCC 工具链")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"编译失败！！！{exc}")
        sys.exit(1)


def cmd_s(filename: str) -> None:
    """生成汇编源码。"""
    try:
        to_asm(filename)
        print(f"\t编译成功，生成汇编代码 {filename[:-1]}s")
    except Exception as exc:  # noqa: BLE001
        print(f"\t编译失败！！！{exc}")


def cmd_m(filename: str) -> None:
    """打印四元式（中间代码）。"""
    try:
        mid = creat_mcode(filename)["mid_code"]
        for m in mid:
            print(m)
    except Exception as exc:  # noqa: BLE001
        print(f"编译失败！！！{exc}")


def cmd_t(filename: str) -> None:
    """打印语法树生成过程。"""
    try:
        w_list = Lexer(filename)
        ok, root = analysis(w_list.word_list, True)
        if ok:
            print("\n\n是否继续打印语法树？(可能树很高，屏幕挤不下)\t1.打印 \t2.任意键退出")
            if input() == "1":
                print(root)
                print("\n\n语法树打印完成！")
    except Exception as exc:  # noqa: BLE001
        print(f"编译失败！！！{exc}")


def cmd_l(filename: str) -> None:
    """打印词法分析结果。"""
    try:
        w_list = Lexer(filename)
        if w_list.flag:
            print("\n输出字符串如下")
            print_lines(w_list.word_list)
    except Exception as exc:  # noqa: BLE001
        print(f"编译失败！！！{exc}")


def cmd_p() -> None:
    """打印预测分析表。"""
    from .get_predict_table import show_tables
    show_tables()


def cmd_g() -> None:
    """打印语法推导。"""
    for g in GRAMMARS:
        print(g, GRAMMARS[g])


def interactive() -> None:
    """交互模式（保持与原版一致的 REPL 风格）。"""
    print(HEAD)
    while True:
        try:
            s = input("(pcc)>>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nhave a good time!")
            return
        if not s:
            continue
        args = s.split()
        if args[0] == "exit":
            print("have a good time!")
            return
        if args[0] != "pcc" or len(args) > 3:
            print("命令格式错误，请参考帮助：")
            print(HELP)
            continue
        try:
            if args[1] == "-h":
                print(HELP)
            elif args[1] == "-o":
                cmd_o(args[2])
            elif args[1] == "-m":
                cmd_m(args[2])
            elif args[1] == "-s":
                cmd_s(args[2])
            elif args[1] == "-t":
                cmd_t(args[2])
            elif args[1] == "-l":
                cmd_l(args[2])
            elif args[1] == "-p":
                cmd_p()
            elif args[1] == "-g":
                cmd_g()
            else:
                print(HELP)
        except IndexError:
            print("参数不足，请参考帮助：")
            print(HELP)
        except Exception as exc:  # noqa: BLE001
            print(f"命令执行失败：{exc}")


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        interactive()
        return
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.o:
        cmd_o(args.o)
    elif args.s:
        cmd_s(args.s)
    elif args.m:
        cmd_m(args.m)
    elif args.t:
        cmd_t(args.t)
    elif args.l:
        cmd_l(args.l)
    elif args.p:
        cmd_p()
    elif args.g:
        cmd_g()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
