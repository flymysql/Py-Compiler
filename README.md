## PCC——python实现编译器

编译原理课设，实现源码到汇编代码的翻译，链接部分使用gcc的功能

## 源码说明

1. lexer.py     词法分析器
2. get_predict_table.py     生成预测分析表
3. LR.py        非递归的语法分析器
4. generate.py  中间代码生成
5. to_asm.py    汇编代码生成
6. pcc.py       入口函数

## 使用

```python
$ python pcc.py
```

**命令说明**

```
pcc -o (filename)       直接编译生成可执行程序
pcc -s (filename)       生成汇编源码
pcc -t (filename)       查看语法树生成过程
pcc -l (filename)       查看词法分析
pcc -h                  查看帮助
pcc -p                  查看本编译器的预测分析表
pcc -g                  查看本编译器的语法推导
exit                    退出
```

![](./other/help.png)

### 编译代码

```
pcc -o ./test/test.c
```

![](./other/pcc-o.png)

其他命令自行发觉hhh