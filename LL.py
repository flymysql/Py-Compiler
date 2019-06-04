"""
使用非递归的预测分析表做语法分析————语法树生成
作者：刘金明
博客：me.idealli.com
Github：github.com/flymysql
"""

from get_predict_table import creat_predict_table
import re
from lexer import word_list

predict_table = creat_predict_table()

# 语法树节点
class Node:
    def __init__(self, Type, text=None):
        self.type = Type
        self.text = text
        self.child = list()
    # 将语法树对象字符化输出
    def __str__(self):
        childs = list()
        for child in self.child:
            childs.append(child.__str__())
        out = "<{type}, {text}>".format(type=self.type, text=self.text)
        for child in childs:
            if child:
                for line in child.split("\n"):
                    out = out + "\n     " + line
        return out

    def __repr__(self):
        return self.__str__()

# 输出栈中节点的type
def stack_text(stack):
    ss = []
    for s in stack:
        ss.append(s.type)
    return ss

def analysis(word_table, show=False):
    stack = []
    root = Node("Program")
    End = Node("#")
    stack.append(End)
    stack.append(root)
    index = 0
    """
    分析预测表的三个状态
    1. cur = #  解析完成
    2. cur = w  输入的字符表与符号栈中节点匹配
    3. cur 为非终结符，继续生成子节点
    4. error
    """
    while len(stack) != 0:
        cur = stack.pop()
        # 状态 1
        if cur.type == "#" and len(stack) == 0:
            print("分析完成!")
            return [True, root]
        # 状态 2
        elif cur.type == word_table[index]['type']:
            if show:
                print("符号栈：", stack_text(stack), "\n匹配字符: ", word_table[index]['word'])
            cur.text = word_table[index]['word']
            index += 1
        # 状态 3
        else:
            w = word_table[index]['type']
            if w in predict_table[cur.type]:
                if predict_table[cur.type][w] == "null":
                    continue
                next_pr = predict_table[cur.type][w].split()
                if show:
                    print("\n符号栈：", stack_text(stack), "\n产生式: ", cur.type,"->", predict_table[cur.type][w])
                node_list = []
                """
                产生式右部符号入栈
                子节点入栈
                注意：子节点入栈顺序应该与产生式符号相反
                """
                for np in next_pr:
                    node_list.append(Node(np))
                for nl in node_list:
                    cur.child.append(nl)
                node_list.reverse()
                for nl in node_list:
                    stack.append(nl)
            # 状态 4 错误
            else:
                print("error", stack, cur.type , word_table[index]['type'])
                return [False]

if __name__ == "__main__":
    w_list = word_list("./test/test.c")
    word_table = w_list.word_list
    root = analysis(word_table, True)
    if root[0]:
        print("\n\n是否继续打印语法树？\t1.打印 \t2.任意键退出\tTip：运行generate.py输出中间代码（四元式）\n请输入")
        if input() == "1":
            print(root[1])
            print("\n\n语法树打印完成！运行 genenrate.py 生成四元式\n\n")
        # print(root[1])