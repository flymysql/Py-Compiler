"""预测分析表生成：FIRST 集合、FOLLOW 集合、LL(1) 预测分析表。

作者：刘金明
GitHub: github.com/flymysql/Py-Compiler
"""

from __future__ import annotations

from .lexer import KEYWORDS, OPERATORS, SEPARATORS, TYPES

# 文法（LL(1)）
GRAMMARS: dict[str, list[str]] = {
    "Program": ["type M C Pro"],
    "C": ["( cc )"],
    "cc": ["null"],

    "Pro": ["{ Pr }"],
    "Pr": ["P Pr", "null"],
    "P": ["type L ;", "L ;", "printf OUT ;", "Pan"],

    "L": ["M LM"],
    "LM": ["= FE", "Size AM", "null"],
    "FE": ["E", "TEXT", "CHAR"],
    "M": ["name"],

    "E": ["T ET"],
    "ET": ["+ T ET", "- T ET", "null"],
    "T": ["F TT"],
    "TT": ["* F TT", "/ F TT", "null"],
    "F": ["number", "BRA", "M MS"],
    "MS": ["Size", "null"],
    "BRA": ["( E )"],

    "OUT": ["( TXT V )"],
    "TXT": ["TEXT"],
    "V": [", E VV", "null"],
    "VV": [", E VV", "null"],

    "Pan": ["Ptype P_block Pro"],
    "Ptype": ["if", "while"],
    "P_block": ["( Pbc )"],
    "Pbc": ["E PM"],
    "PM": ["Cmp E", "null"],

    "Size": ["[ E ]"],
    "AM": ["= E", "null"],
}

# 兼容旧接口
grammars = GRAMMARS

first_table: dict[str, list[str]] = {}
follow_table: dict[str, list[str]] = {}
predict_table: dict[str, dict[str, str]] = {}
observer: dict[str, list[str]] = {}


def _union(a: list[str], b: list[str]) -> list[str]:
    """合并两个列表并去重。"""
    return list(set(a + b))


def init_observer() -> None:
    """初始化订阅者：记录每个非终结符产生式右部最后一个符号的依赖关系。

    用于求 FOLLOW 集合时的特殊情况——右部末位是非终结符时，
    FOLLOW(左部) 需要传播到该非终结符。
    """
    for k in GRAMMARS:
        follow_table[k] = []
        observer[k] = []
        for next_grammar in GRAMMARS[k]:
            last_k = next_grammar.split()[-1]
            if last_k in GRAMMARS and last_k != k:
                observer[k].append(last_k)


def refresh(k: str) -> None:
    """递归刷新所有依赖 FOLLOW(k) 的订阅者。"""
    for lk in observer[k]:
        newlk = _union(follow_table[k], follow_table[lk])
        if newlk != follow_table[lk]:
            follow_table[lk] = newlk
            refresh(lk)


def find_first(key: str) -> list[str]:
    """查找非终结符的 FIRST 集合。"""
    if key not in GRAMMARS:
        return [key]
    result: list[str] = []
    for next_grammar in GRAMMARS[key]:
        next_k = next_grammar.split()[0]
        result.extend(find_first(next_k))
    return result


def find_follow() -> None:
    """计算所有非终结符的 FOLLOW 集合。"""
    init_observer()
    follow_table["Program"] = ["#"]
    for k in GRAMMARS:
        for next_grammar in GRAMMARS[k]:
            next_k = next_grammar.split()
            for i in range(0, len(next_k) - 1):
                if next_k[i] in GRAMMARS:
                    if next_k[i + 1] not in GRAMMARS:
                        new_follow = _union([next_k[i + 1]], follow_table[next_k[i]])
                        if new_follow != follow_table[next_k[i]]:
                            follow_table[next_k[i]] = new_follow
                            refresh(next_k[i])
                    else:
                        new_follow = _union(first_table[next_k[i + 1]], follow_table[next_k[i]])
                        if "null" in first_table[next_k[i + 1]]:
                            new_follow = _union(follow_table[k], new_follow)
                            observer[k].append(next_k[i])
                        if new_follow != follow_table[next_k[i]]:
                            follow_table[next_k[i]] = new_follow
                            refresh(next_k[i])
            if next_k[-1] in GRAMMARS:
                if next_k[-1] not in follow_table:
                    follow_table[next_k[-1]] = []
                if next_k[-1] != k:
                    follow_table[next_k[-1]] = _union(follow_table[next_k[-1]], follow_table[k])

    for k in follow_table:
        if "null" in follow_table[k]:
            follow_table[k].remove("null")


def get_first_table() -> None:
    """获取所有非终结符的 FIRST 集合，同时填入预测表。"""
    for k in GRAMMARS:
        predict_table[k] = {}
        first_table[k] = []
        for next_grammar in GRAMMARS[k]:
            next_k = next_grammar.split()[0]
            kl = find_first(next_k)
            first_table[k].extend(kl)
            for kk in kl:
                if kk != "null":
                    predict_table[k][kk] = next_grammar


def get_predict_table() -> None:
    """将 FOLLOW 集合中的内容并入预测表（处理可空产生式）。"""
    for k in GRAMMARS:
        for next_grammar in GRAMMARS[k]:
            next_k = next_grammar.split()[0]
            if (next_k in GRAMMARS and "null" in first_table[next_k]) or next_k == "null":
                for fk in follow_table[k]:
                    predict_table[k][fk] = next_grammar


def creat_predict_table() -> dict[str, dict[str, str]]:
    """生成完整预测分析表。"""
    get_first_table()
    find_follow()
    get_predict_table()
    return predict_table


def show_tables() -> None:
    """打印 FIRST / FOLLOW / 预测表（调试用）。"""
    get_first_table()
    find_follow()
    get_predict_table()
    print("\nfirst集合如下\n")
    for k in first_table:
        print(k, first_table[k])
    print("\nfollow集合如下\n")
    for k in follow_table:
        print(k, follow_table[k])
    print("\n预测表如下\n")
    for k in predict_table:
        print(k, predict_table[k])


if __name__ == "__main__":
    show_tables()
