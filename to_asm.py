from generate import creat_mcode
from other.function import if_num

global_head = """
;----------------------Welcome to Pcc--------------------------
; by 兰州小红鸡
; 编译： nasm -f elf 文件名
; 链接： ld -m elf_i386 helloworld.o -o helloworld
;        64位系统需要 elf_i386 选项
; 运行： ./helloworld
;-------------------------------------------------------------------
"""

code_head = """
\t.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
"""

code_footer = """
\tmovl\t$0, %eax
	leave
\t.cfi_def_cfa 7, 8
	ret
\t.cfi_endproc
.LFE6:
	.size\tmain, .-main
	.ident\t"PCC: 1.0.0"
"""

LC = 0
re = ""
cltq = True
def args(n, name):
    global re
    if n in name:
        return "-" + name[n][0] + "(%rbp)"
    elif "[]" in str(n):
        global cltq
        ags = n.split("[]")
        if if_num(ags[1]):
            if name[ags[0]][1] == "char":
                return "-" + str(int(name[ags[0]][0])-int(ags[1])) + "(%rbp)"
            elif name[ags[0]][1] == "int":
                return "-" + str(int(name[ags[0]][0])-int(ags[1])*4) + "(%rbp)"
        else:
            re += "\tmovl\t" + args(ags[1], name) + ", %eax\n\tcltq\n"
            if name[ags[0]][1] == "char":
                return "-" + name[ags[0]][0] + "(%rbp, %rax, 1)"
            elif name[ags[0]][1] == "int":
                return "-" + name[ags[0]][0] + "(%rbp, %rax, 4)"

    elif "T" in str(n):
        return n + "(%rip)"
    elif if_num(str(n)):
        return "$" + str(n)
    
    else:
        return n

def array_n(a1,a2,name):
    if name[a1][1] == "char":
        return "-" + str(int(name[a1][0])-a2) + "(%rbp)"
    elif name[a1][1] == "int":
        return "-" + str(int(name[a1][0])-int(a2)*4) + "(%rbp)"


def init_data(name_list, arrs):
    re = {}
    i = 0
    for n in name_list:
        if n['name'] != "main":
            if n['flag'] == "int":
                i += 4
                re[n['name']] = [str(i), "int"]
            elif n['flag'] == 'char':
                i += 1
                re[n['name']] = [str(i), "char"]
    for a in arrs:
        if arrs[a][1] == "int":
            i += int(arrs[a][0])*4
            re[a] = [str(i), "int"]
        elif arrs[a][1] == "char":
            i += int(arrs[a][0])
            re[a] = [str(i), "char"]
    return [re, (int(i/12) + 1)*12]

def init_string(strings):
    re = ""
    for i in range(0, len(strings)):
        re += ".LC" + str(i) + ":\n\t.string \"" + strings[i] + "\"\n"
    return re

def generate_code(mid_code, name):
    global re
    re = ""
    for m in mid_code:
        # args = arg(m, name)
        a1 = args(m.arg1, name)
        a2 = args(m.arg2, name)
        r = args(m.re, name)
        if m.op == "=":
            if m.re in name and name[m.re][1] == "char":
                re += "\tmovb\t$" + str(ord(m.arg1)) + ", " + r + "\n"
            elif m.arg1 in name or "T" in m.arg1 or "[]" in m.arg1:
                re += "\tmovl\t" + a1 + ", %ecx\n"
                re += "\tmovl\t%ecx, " + r + "\n"
            else:
                re += "\tmovl\t" + a1 + ", " + r + "\n"
        elif m.op == "code_block":
            re += "." + m.re + ":\n"
            continue
        elif "j" in m.op:
            if m.op == "j":
                re += "\tjmp\t." + m.re + "\n"
            else: 
                re += "\tmovl\t" + a1 + ", %eax\n"
                re += "\tcmpl\t" + a2 + ", %eax\n"
                if ">" in m.op:
                    re += "\tjg\t." + m.re + "\n"
                elif "<" in m.op:
                    re += "\tjle\t." + m.re + "\n"
                elif "=" in m.op:
                    re += "\tje\t." + m.re + "\n"
        elif m.op in "+-":
            re += "\tmovl\t" + a1 +", %edx\n"
            re += "\tmovl\t" + a2 +", %eax\n"
            if m.op == "+":
                re += "\taddl\t%edx, %eax\n"
            else:
                re += "\tsubl\t%edx, %eax\n"
            re += "\tmovl\t%eax, " + r + "\n"
        elif m.op in "*/":
            if m.arg1 in name:
                re += "\tmovl\t" + a2 +", %eax\n"
                re += "\timull\t"+ a1 +", %eax\n"
                re += "\tmovl\t%eax, "+ r +"\n"
            elif m.arg2 in name and m.arg1 not in name:
                re += "\tmovl\t" + a2 +", %eax\n"
                re += "\timull\t"+ a1 +", %eax, %eax\n"
                re += "\tmovl\t%eax, "+ r +"\n"
            elif m.arg2 not in name and m.arg1 not in name:
                num = int(m.arg2)*int(m.arg1)
                re += "\tmovl\t$" + str(num) +", "+ r +"\n"
        elif m.op == "print":
            global LC
            if m.arg1 != "-1":
                if name[m.arg1][1] == "char":
                    re += "\tmovsbl\t" + a1 + ", %eax\n"
                else:
                    re += "\tmovl\t" + a1 + ", %eax\n"
            if m.arg2 != "-1":
                if name[m.arg2][1] == "char":
                    re += "\tmovsbl\t" + a2 + ", %edx\n"
                else:
                    re += "\tmovl\t" + a2 + ", %edx\n"
            re += "\tmovl\t%eax, %esi\n" + "\tleaq\t.LC" + str(LC) + "(%rip), %rdi\n"
            LC += 1
            re += "\tmovl\t$0, %eax\n\tcall\tprintf@PLT\n"
            
    return re

def connect(tmp, strs, code, subq):
    data = ""
    for i in range(0, tmp):
        data += "\t.comm\tT" + str(i) + ",4,4\n"
    re = "\t.text\n\t.section\t.rodata\n" + data + strs + \
        "\t.text\n\t.globl	main\n\t.type	main, @function\nmain:\n" + code_head +\
             "\tsubq\t$" + str(subq) + ", %rsp\n" + code + code_footer
    return re

def to_asm(filename):
    global LC
    LC = 0
    mid_result = creat_mcode(filename)
    mid_code = mid_result['mid_code']
    name_list = mid_result['name_list']
    tmp = mid_result['tmp']
    strings = mid_result['strings']
    arrs = mid_result['arrs']
    name = init_data(name_list, arrs)
    string_list = init_string(strings)
    asm = generate_code(mid_code, name[0])
    result = connect(tmp, string_list, asm, name[1])
    re_asm = open(filename[:-1] + "s", "w").write(result)

if __name__ == "__main__":
    to_asm("./test/test.c")