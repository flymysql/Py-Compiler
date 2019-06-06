from to_asm import to_asm
from generate import creat_mcode
from get_predict_table import grammars
from LR import analysis
import os
from lexer import word_list

head = """
:::PCC编译器——Ｃ语言语法编译器，当前版本1.00
:::作者：小鸡\t项目地址:https://github.com/flymysql/Py-Compiler
:::查看使用帮助：pcc -h
"""

phelp = """\tpcc -o (filename)\t直接编译生成可执行程序
\tpcc -s (filename)\t生成汇编源码
\tpcc -t (filename)\t查看语法树生成过程
\tpcc -l (filename)\t查看词法分析
\tpcc -p \t查看本编译器的预测分析表
\tpcc -g \t查看本编译器的语法推导
\texit\t退出
"""

def begin():
    print(head)
    while True:
        print("(pcc)>>>",end="")
        s = input()
        slist = s.split()
        if len(slist) == 0:
            continue
        if slist[0] != "pcc" or len(slist) > 3:
            try:
                os.system(s)
            except:
                print("命令错误，请重新输入")
                print(phelp)
            continue
        if slist[0] == "exit":
            print("have a good time!")
            return
        elif slist[1] == "-h":
            print(phelp)
        elif slist[1] == "-o":
            try:
                to_asm(slist[2])
                os.system("gcc " + slist[2][:-1] + "s -o "+slist[2][:-2])
                print("编译成功，执行："+slist[2][:-2])
            except:
                print("\t编译失败！！！")
        elif slist[1] == "-s":
            try:
                to_asm(slist[2])
                name = slist[2].split("/")[-1]
                # os.system("gcc -c " + slist[2][:-1] + "s && gcc " + slist[2][:-1] + "o -o " + name)
                print("\t编译成功，生成汇编代码"+slist[2][:-1]+"s")
            except:
                print("\t编译失败！！！")
        elif slist[1] == "-t":
            w_list = word_list(slist[2])
            word_table = w_list.word_list
            root = analysis(word_table, True)
            if root[0]:
                print("\n\n是否继续打印语法树？(可能树很高，屏幕挤不下)\t1.打印 \t2.任意键退出")
                if input() == "1":
                    print(root[1])
                    print("\n\n语法树打印完成！")
        elif slist[1] == "-l":
            w_list = word_list(slist[2])
            if w_list.flag:
                print("\n输出字符串如下")
                for w in w_list.word_list:
                    print(w)
        elif slist[1] == "-p":
            os.system("python get_predict_table.py")
        elif slist[1] == "-g":
            for g in grammars:   
                print(g, grammars[g])
        

if __name__ == "__main__":
    begin()