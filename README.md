## python实现编译器

第一个程序——词法分析器

第一个程序——语法分析器

## 非递归的预测分析表

###　First集构造流程

对于 X -> ＡＢＣ...

1. 若右边第一个符号是终结符或 `null` ，则直接将其加入 First（X）
2. 若右边第一个符号是非终结符，则将其 First 集的的非 `null`  元素加入 First（X）
3. 若右边第一个符号是非终结符而且紧随其后的是很多个非终结符，这个时候就要注意是否有 `null`  。
4. 若第 i 个非终结符的 First 集有 `null`  ，则可将第 i+1 个非终结符去除 `null`  的 First 集加入 First（X）。
5. 若所有的非终结符都能够推导出 `null` ，则将  `null`  也加入到 First（X）


### Follow集构造流程

1. 将`#`符号加入产生开始的非终结符`Ｅ`
1. 将所有产生式右部的非终结符的`follow`集合等于自身`follow`集合加上后继节点`first`集合
    E.G.  用 A -> aBC 来说就是，当前扫描到 B 了，而 B 的右侧有非终结符 C，则将去掉 `null`  的 First（C）加入 Follow（B）中。若存在 C -> `null` ，则将 Follow（A）也加入 Follow（B）中。
2. 若右边没有符号了，例如这里的 C，那么可以将 Follow（A）中的元素全部加入到 Follow（C）中。

**一个问题**

其中生成follow集合的过程较为复杂（我不知道正常情况是不是这样）非终结符的后继非终结符的first集合可能存在如下情况

1. A -> BC 
2. C -> D | null 
3. D -> (A) | i 

那么在一次遍历过程中，因为C的first集合存在null，所以需要将follow（A）加入follow（B） （**重点**）但是！此时的follow（A），并不是完整的，它可能在后续的遍历中会继续更新自身的follow集合所以此时follow(B) 中加入的follow(A) 并不是完整的follow（A）

为了解决这种情况，我加入了订阅者模式，一种实时更新的机制，订阅者为一个字典，字典键值为产生式左部，字典内容为产生式右部。
简而言之：follow（A）发生了更新，那么曾经将follow（A）加入自身的B，C也更新其follow。并且，这是一个递归过程。详细说明见代码。

```python
observer = {}

"""
初始化订阅者
订阅者： 用于求follow集合的过程中特殊情况：
    非终结符的后继非终结符的first集合可能存在null
    eg： A -> BC     C -> D | null   D -> (A) | i
    那么在一次遍历过程中，因为C的first集合存在null，所以需要将follow（A）加入follow（B）
    （重点）但是！此时的follow（A），并不是完整的，它可能在后续的遍历中会继续更新自身的follow集合
    所以此时会出现遗漏的follow
    所以我在这里用到一个订阅者模式
    订阅者为一个字典，字典键值为产生式左部，字典内容为产生式右部
"""
def init_observer():
    for k in grammars:
        follow_table[k] = []
        observer[k] = []
        for next_grammar in grammars[k]:
            last_k = next_grammar.split()[-1]
            if last_k in grammars and last_k != k:
                observer[k].append(last_k) 
"""
刷新订阅
检测到某个follow集合更新时，对其订阅的所有产生式左部的follow集合进行更新
简而言之：follow（A）发生了更新，那么曾经将follow（A）加入自身的B，C也更新其follow
并且，这是一个递归过程
"""
def refresh(k):
    for lk in observer[k]:
        newlk = U(follow_table[k], follow_table[lk])
        if newlk != follow_table[lk]:
            follow_table[lk] = newlk
            refresh(lk)
```

### 预测表的构造

1. 对于每个属于 First(B) 的终结符 m ，都把 A -> BC 添加到预测表中的 [A, m] 中去
2. 如果 null 也属于 First(B)，那么对于任何属于 Follow(A) 的字符 n，都把 A ->  null  加入到 [A, n] 中去

### 代码

```python
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
}

first_table = {}
follow_table = {}
predict_table = {}
observer = {}

"""
初始化订阅者
订阅者： 用于求follow集合的过程中特殊情况：
    非终结符的后继非终结符的first集合可能存在null
    eg： A -> BC     C -> D | null   D -> (A) | i
    那么在一次遍历过程中，因为C的first集合存在null，所以需要将follow（A）加入follow（B）
    （重点）但是！此时的follow（A），并不是完整的，它可能在后续的遍历中会继续更新自身的follow集合
    所以此时会出现遗漏的follow
    所以我在这里用到一个订阅者模式
    订阅者为一个字典，字典键值为产生式左部，字典内容为产生式右部
"""
def init_observer():
    for k in grammars:
        follow_table[k] = []
        observer[k] = []
        for next_grammar in grammars[k]:
            last_k = next_grammar.split()[-1]
            if last_k in grammars and last_k != k:
                observer[k].append(last_k) 
"""
刷新订阅
检测到某个follow集合更新时，对其订阅的所有产生式左部的follow集合进行更新
简而言之：follow（A）发生了更新，那么曾经将follow（A）加入自身的B，C也更新其follow
并且，这是一个递归过程
"""
def refresh(k):
    for lk in observer[k]:
        newlk = U(follow_table[k], follow_table[lk])
        if newlk != follow_table[lk]:
            follow_table[lk] = newlk
            refresh(lk)

"""
合并两个list并且去重
"""
def U(A,B):
    return list(set(A+B))

"""
查找指定非终结符的first集合
"""
def find_first(key):
    if key not in grammars:
        return [key]
    l = []
    for next_grammar in grammars[key]: 
        next_k = next_grammar.split()[0]
        l.extend(find_first(next_k))
    return l

"""
查找所有非终结符follow
"""
def find_follow():
    init_observer()
    follow_table["E"] = ["#"]
    for k in grammars:
        for next_grammar in grammars[k]:
            next_k = next_grammar.split()
            
            for i in range(0,len(next_k)-1):
                if next_k[i] in grammars:
                    if next_k[i+1] not in grammars:
                        """
                        如果后继字符不是终结符，加入
                        """
                        new_follow = U([next_k[i+1]], follow_table[next_k[i]])
                        if new_follow != follow_table[next_k[i]]:
                            follow_table[next_k[i]] = new_follow
                            refresh(next_k[i])
                    else:
                        new_follow = U(first_table[next_k[i+1]], follow_table[next_k[i]])
                        """
                        如果后继字符的first集合中含有null，通知所有订阅者更新follow集合
                        """
                        if "null" in first_table[next_k[i+1]]:
                            new_follow = U(follow_table[k], new_follow)
                            observer[k].append(next_k[i])
                        if new_follow != follow_table[next_k[i]]:
                            follow_table[next_k[i]] = new_follow
                            refresh(next_k[i])
            """
            产生式左部的follow集合加入最后一个非终结符的follow集合
            """
            if next_k[-1] in grammars:
                if next_k[-1] not in follow_table:
                    follow_table[next_k[-1]] = []
                if next_k[-1] != k:
                    follow_table[next_k[-1]] = U(follow_table[next_k[-1]], follow_table[k])

    for k in follow_table:
        if "null" in follow_table[k]:
            follow_table[k].remove("null")

"""
获取所有非终结符的first集合
在此同时直接将first集合加入predict表中
"""
def get_first_table():
    for k in grammars:
        predict_table[k] = {}
        first_table[k] = []
        for next_grammar in grammars[k]:
            next_k = next_grammar.split()[0]
            kl = find_first(next_k)
            first_table[k].extend(kl)
            for kk in kl:
                if kk != "null":
                    predict_table[k][kk] = next_grammar

"""
将follow集合中的部分内容加入predict表中
"""
def get_predict_table():
    for k in grammars:
        for next_grammar in grammars[k]:
            next_k = next_grammar.split()[0]
            if next_k in grammars and "null" in first_table[next_k] or next_k == "null":
                for fk in follow_table[k]:
                    predict_table[k][fk] = next_grammar

```