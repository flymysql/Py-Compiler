from generate import creat_mcode

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
	subq	$32, %rsp
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

def arg(m, name):
    if m.arg1 in name:
        a1 = "-" + name[m.arg1] + "(%rbp)"
    elif "T" in str(m.arg1):
        a1 = m.arg1 + "(%rip)"
    else:
        a1 = "$" + str(m.arg1)
    if m.arg2 in name:
        a2 = "-" + name[m.arg2] + "(%rbp)"
    elif "T" in str(m.arg2):
        a2 = m.arg2 + "(%rip)"
    else:
        a2 = "$" + str(m.arg2)
    if "T" in m.re:
        r = m.re + "(%rip)"
    elif m.re in name:
        r = "-" + name[m.re] + "(%rbp)"
    else:
        r = m.re
    return [a1, a2, r]

def init_data(name_list):
    re = {}
    i = 8
    for n in name_list:
        if n['name'] != "main":
            re[n['name']] = str(i)
            i += 4
    return re

def init_string(strings):
    re = ""
    for i in range(0, len(strings)):
        re += ".LC" + str(i) + ":\n\t.string \"" + strings[i] + "\"\n"
    return re

def generate_code(mid_code, name):
    re = ""
    for m in mid_code:
        args = arg(m, name)
        a1 = args[0]
        a2 = args[1]
        r = args[2]
        if m.op == "=":
            if m.arg1 in name or "T" in m.arg1:
                re += "\tmovl\t" + a1 + ", %eax\n"
                re += "\tmovl\t%eax, " + r + "\n"
            else:
                re += "\tmovl\t" + a1 + ", " + r + "\n"
        elif m.op == "code_block":
            re += "." + m.re + ":\n"
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
        elif m.op == "print":
            global LC
            if m.arg1 != -1:
                re += "\tmovl\t" + a1 + ", %eax\n"
            if m.arg2 != -1:
                re += "\tmovl\t" + a2 + ", %edx\n"
            re += "\tmovl\t%eax, %esi\n" + "\tleaq\t.LC" + str(LC) + "(%rip), %rdi\n"
            LC += 1
            re += "\tmovl\t$0, %eax\n\tcall\tprintf@PLT\n"
            
    return re

def connect(tmp, strs, code):
    data = ""
    for i in range(0, tmp):
        data += "\t.comm\tT" + str(i) + ",4,4\n"
    re = "\t.text\n\t.section\t.rodata\n" + data + strs + \
        "\t.text\n\t.globl	main\n\t.type	main, @function\nmain:\n" + code_head + code + code_footer
    return re

def to_asm(filename):
    mid_result = creat_mcode(filename)
    mid_code = mid_result['mid_code']
    name_list = mid_result['name_list']
    tmp = mid_result['tmp']
    strings = mid_result['strings']
    name = init_data(name_list)
    string_list = init_string(strings)
    asm = generate_code(mid_code, name)
    result = connect(tmp, string_list, asm)
    re_asm = open(filename[:-1] + "s", "w").write(result)
