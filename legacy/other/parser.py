"""
语法分析:使用递归的自上而下方式
作者：刘金明
博客：me.idealli.com
Github：github.com/flymysql
"""
import sys, os, re
sys.path.append(os.pardir)
from lexer import word_list,k_list

"""
Expr      ->    Term ExprTail
ExprTail  ->    + Term ExprTail
          |     - Term ExprTail
          |     null

Term      ->    Factor TermTail
TermTail  ->    * Factor TermTail
          |     / Factor TermTail
          |     null

Factor    ->    (Expr)
          |     num
"""
grammars = {
    "Program":["type M C Pro"],
    "C":["( cc )"],
    "cc":["null"],
    "Pro":["{ Pr }"],
    "Pr":["P ; Pr", "null"],
    "P":["type L", "L","printf OUT"],
    "L":["M LM"],
    "LM":["= E", "null"],
    "M":["name"],
    "E":["T ET"],
    "ET":["+ T ET", "- T ET", "null"],
    "T":["F TT"],
    "TT":["* F TT", "/ F TT", "null"],
    "F":["number", "BRA"],
    "BRA": ["( E )"],
    "OUT":["( \" TEXT \" , V )"],
    "V":["name VV", "null"],
    "VV":[", name VV", "null"],
    "END_STATE": r"(null)|(number)|(name)|(type)|(operator)|(printf)|(separator)|(TEXT)|[+\-*/=;,\")({}]"
}


# 运算符表
operator = {"+","-","*","/","="}
f_list = {";","(",")","[","]","{","}", ".",":","\"","#","\'","\\","?"}
k_list = {"int", "main"}


def build_ast(tokens):
    root = Node("Program")
    # 建立根节点，自上而下分析
    offset = root.build_ast(tokens, token_index=0)
    if offset == len(tokens):
        return root
    else:
        raise ValueError("Error Grammar4")


class Node:
    def match_token(self, token):
        token_type = token['type']
        token_word = token['word']
        if self.type == "null" or self.type == token_type or self.type == token_word:
            return True
        return False
    def __init__(self, type):
        self.type = type
        self.text = None
        self.child = list()
    def build_ast(self, tokens: list, token_index=0):
        # 判断是否遇到终结符
        if re.match(grammars["END_STATE"], self.type):
            if self.type != "null":
                if token_index >= len(tokens):
                    raise ValueError("Error Grammar1")
                if self.match_token(tokens[token_index]):
                    self.text = tokens[token_index]['word']
                    # print(self.text, token_index)
                else:
                    raise ValueError("Error Grammar2")
                return 1
            return 0

        # 遍历当前可能的产生式
        for grammar in grammars[self.type]:
            offset = 0
            # 切割下一个产生式的字符
            grammar_tokens = grammar.split()
            tmp_nodes = list()
            try:
                # 遍历下一个产生式的字符，创建新节点
                for grammar_token in grammar_tokens:
                    node = Node(grammar_token)
                    tmp_nodes.append(node)
                    # token数组游标加上创建子节点后的游标长度
                    offset += node.build_ast(tokens, offset+token_index)
                else:
                    self.child = tmp_nodes
                    return offset
            except ValueError:
                pass
        raise ValueError("Error Grammar3")

    # 将语法树对象字符化输出
    def __str__(self):
        childs = list()
        for child in self.child:
            childs.append(child.__str__())
        out = "({type}, {text})".format(type=self.type, text=self.text)
        for child in childs:
            if child:
                for line in child.split("\n"):
                        out = out + "\n\t" + line
        return out

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    filename = 'test/test2.c'
    w_list = word_list(filename)
    word_table = w_list.word_list
    build_ast(word_table)
    print(build_ast(word_table))
    print("\n\n\t小鸡提示，这是写的第一个递归方式的语法分析！\n\t请运行　LL.py　执行非递归的预测表分析方法！\n\n")
