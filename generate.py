"""
语义分析:中间代码产生——四元式
作者：刘金明
博客：me.idealli.com
Github：github.com/flymysql
"""
from parser import Node,build_ast
from LR import analysis
import sys, os, re
sys.path.append(os.pardir)
from lexer import word_list

"""
四元式对象
成员：　op，arg1,arg2,result 分别对于操作数，两个变量，结果
特殊的自定义四元式语法：
    1.  (code_block, 0, 0, block1)   代码块开始标记
    2.  (j, 0, 0, , +2)              跳转语句，往后跳两行
    3.  (j<, ａ, b, block1)          条件跳转 if(a<b) then　jmp block1
    4.  (print, 0, 0, a)             打印变量ａ
"""
class Mnode:
    def __init__(self, op="undefined", a1=None, a2=None, re=None):
        self.op = op
        self.arg1 = a1
        self.arg2 = a2
        self.re = re
    """字符化输出"""
    def __str__(self):
        return "({0},{1},{2},{3})".format(self.op, self.arg1, self.arg2, self.re)

    def __repr__(self):
        return self.__str__()

"""
两个全局 mid_result 存放四元式对象
tmp记录零时变量id
"""
mid_result = []
while_flag = []
tmp = 0

"""
递归遍历语法树
遇到相应非终结符做相应处理，遇到终结符返回终结符，其他字符递归处理其子节点

"""
def view_astree(root, ft=None):
    if root == None or root.text == "(" or root.text == ")":
        return
    elif len(root.child) == 0 and root.text != None:
        return root.text
    if root.type == "L":
        math_op(root)
    elif root.type == "Pan":
        judge(root)
    elif root.type == "OUT":
        out(root)
    else:
        re = ""
        for c in root.child:
            cre = view_astree(c)
            if cre != None:
                re = cre
        return re

def math_op(root, ft=None):
    if root == None or root.text == "(" or root.text == ")":
        return
    elif len(root.child) == 0 and root.text != None:
        return root.text
    global mid_result
    global tmp
    """
    变量声明语句，两种情况
    1. 直接赋值
    2. 不赋值
    """
    if root.type == "L":
        if len(root.child[1].child) == 1:
            mid_result.append(Mnode("=",0,0,math_op(root.child[0])))
        else:
            mid_result.append(Mnode("=",math_op(root.child[1]),0,math_op(root.child[0])))

    elif root.type == "ET" or root.type == "TT":
        if len(root.child) > 1:
            """
            临时变量Tn
     ft 为父节点传入的操作符左边部分临时id
            """
            t = "T" + str(tmp)
            tmp += 1
            mid_result.append(Mnode(math_op(root.child[0]), math_op(root.child[1]), ft,t))
            ct = math_op(root.child[2], t)
 
            if ct != None:
                return ct
            return t

    elif root.type == "E" or root.type == "T":
        """
        赋值语句处理
        如果存在右递归，进行四则运算的解析
        不存在右递归的话直接赋值
        """
        if len(root.child[1].child) > 1:
            t = "T" + str(tmp)
            tmp += 1
            mid_result.append(Mnode(math_op(root.child[1].child[0]), math_op(root.child[0]), math_op(root.child[1].child[1]),t))
            ct = math_op(root.child[1].child[2], t)
            if ct != None:
                return ct
            return t
        else:
            return math_op(root.child[0])
    elif root.type == "Pan":
        judge(root)
        return
    else:
        re = ""
        for c in root.child:
            cre = math_op(c)
            if cre != None:
                re = cre
        return re


"""
控制语句的程序块处理
可处理语句：
    １. if语句
    ２. while语句
    ３. if和while的相互嵌套语句
"""
def judge(root):
    if root == None or root.text == "(" or root.text == ")":
        return
    elif len(root.child) == 0 and root.text != None:
        return root.text
    if root.type == "Ptype":
        if root.child[0].text == "if":
            while_flag.append([False])
        else:
            """
            对whilie语句进行代码块标记，方便跳转
            """
            cur = len(mid_result)
            while_flag.append([True,cur])
            mid_result.append(Mnode("code_bloc", 0, 0, "W" + str(cur)))
    if root.type == "Pbc":
        """
        判断语句括号中的的两种情况
        1. (E)
        2. (E1 cmp E2)
        """
        Pm = root.child[1].child
        if len(Pm) == 1:
            mid_result.append(Mnode("j=", 1, math_op(root.child[0]),"+2"))
        else:
            mid_result.append(Mnode("j"+judge(Pm[0]), math_op(root.child[0]), math_op(Pm[1]),"+2"))
        return
    if root.type == "Pro":
        """
        控制语句的代码块前后做标记
        判断标记
        跳转->结束标记
        {
            code
        }
        while跳转->判断标记
        结束标记
        """
        w = while_flag.pop()
        code_block = len(mid_result)
        code = "block" + str(code_block)
        mid_result.append(Mnode("j",0, 0,code))
        view_astree(root)
        if w[0] == True:
            mid_result.append(Mnode("j",0,0,"W"+str(w[1])))    
        mid_result.append(Mnode("code_block",0,0,code))
        code_block += 1
        return
    else:
        re = ""
        for c in root.child:
            cre = judge(c)
            if cre != None:
                re = cre
        return re


"""
输出处理
可处理语句：printf(a,b) 该语法：在括号内只能传入变量参数
"""
def out(root):
    if root == None or root.text == "(" or root.text == ")":
        return
    elif root.type == "name":
        mid_result.append(Mnode("print", 0, 0,root.text))
        return
    else:
        for c in root.child:
            out(c)

        
if __name__ == "__main__":
    filename = 'test/test.c'
    w_list = word_list(filename)
    word_table = w_list.word_list
    root = analysis(word_table)[1]
    view_astree(root)
    for r in mid_result:
        print(r)
