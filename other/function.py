# 环境：python3.6
# 编译原理——词法分析器
# 刘金明——320160939811
import re

# 运算符表
y_list = {"+","-","*","/","<","<=",">",">=","=","==","!=","^",",","&","&&","|","||","%","~","<<",">>","!"}
# 分隔符表
f_list = {";","(",")","[","]","{","}", ".",":","\"","#","\'","\\","?"}
# 关键字表
k_list = {
    "auto", "break", "case", "char", "const", "continue","default", "do", "double", "else", "enum", "extern",
    "float", "for", "goto", "if", "int", "long","register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "typedef", "union", "unsigned", "void","volatile", "while", "printf"
}

Cmp = ["<", ">", "==", "!=", "<=", ">="]

# 正则表达式判断是否为数字
def if_num(int_word):
    if re.match("^([0-9]{1,}[.][0-9]*)$",int_word) or re.match("^([0-9]{1,})$",int_word) == None:
        return False
    else:
        return True

# 判断是否为为变量名
def if_name(int_word):
    if re.match("[a-zA-Z_][a-zA-Z0-9_]*",int_word) == None:
        return False
    else:
        return True

# 判断是否为终结符
# def END_STATE(int_word):
#     if 

# 判断变量名是否已存在
def have_name(name_list,name):
    for n in name_list:
        if name == n['name']:
            return True
    return False

# list的换行输出
def printf(lists):
    for l in lists:
        print(l)

# 分割并获取文本单词
# 返回值为列表out_words
# 列表元素{'word':ws, 'line':line_num}分别对应单词与所在行号
def get_word(filename):
    global f_list
    out_words = []
    f = open(filename,'r+',encoding='UTF-8')
    # 先逐行读取，并记录行号
    lines = f.readlines()
    line_num = 1
    # 判断是否含有注释块的标识
    pass_block = False
    for line in lines:
        words = list(line.split())
        for w in words:
            # 去除注释
            if '*/' in w:
                pass_block = False
                continue
            if '//' in w or pass_block:
                break
            if '/*' in w:
                pass_block = True
                break
            # 分析单词
            if w in Cmp:
                out_words.append({'word':w, 'line':line_num})
                continue
            ws = w
            for a in w:
                if a in f_list or a in y_list:
                    # index为分隔符的位置，将被分隔符或运算符隔开的单词提取
                    index = ws.find(a)
                    if index!=0:
                        # 存储单词与该单词的所在行号，方便报错定位
                        out_words.append({'word':ws[0:index], 'line':line_num})
                    ws = ws[index+1:]
                    out_words.append({'word':a, 'line':line_num})
            if ws!='':
                out_words.append({'word':ws, 'line':line_num})
        line_num += 1
    return out_words