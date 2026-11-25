# ingest.py 逐行精讲（零基础友好版）

> 面向对象：学过 Python 基础语法、函数、Pandas，但对具体"单词/语法"不熟的人。
> 读法建议：**先看第 0 节的读码顺序，再看第 1 节术语速查，最后对着第 2 节逐段看源码。**

---

## 0. 先别从第 1 行往下读

新手最常见的错误就是打开第 1 行开始顺读，读到第 40 行就晕了。正确顺序是**从程序的入口倒着读**：

```
第 193 行  if __name__ == "__main__":   ← 先看这里，搞清楚"程序从哪开始跑"
    ↓
第 148 行  ingest()                     ← 入口调用了它，看主流程
    ↓
第 41 行   list_knowledge_files()       ← 主流程调用了哪些小函数，再逐个看
第 125 行  read_knowledge_file()
第 49~122 行 各种 read_xxx()
```

记住一句话：**代码是给人看的，函数怎么排列不重要，谁调用谁才是脉络。**

---

## 1. 术语速查表（你卡住的"单词"都在这）

### 1.1 字符串处理方法

| 写法 | 作用 | 例子 |
|---|---|---|
| `strip()` | 去掉字符串**首尾**的空白字符（空格、换行 `\n`、制表符 `\t`） | `"  abc\n".strip()` → `"abc"` |
| `lower()` | 全部转小写 | `"README.MD".lower()` → `"readme.md"` |
| `endswith(x)` | 判断是否以 x 结尾 | `"a.md".endswith(".md")` → `True` |
| `join(列表)` | 用"分隔符"把列表拼成一个字符串 | `"\n".join(["a","b"])` → `"a\nb"` |
| `replace(a,b)` | 把 a 替换成 b | `"a\nb".replace("\n"," ")` → `"a b"` |
| `[:40]` | 切片，取前 40 个字符 | `"你好世界"[:2]` → `"你好"` |

**`strip()` 为什么要重点讲？** 看这段真实代码（第 59-62 行）：

```python
for line in fp:              # 一行一行读文件
    line = line.strip()      # 去掉这行首尾的空白
    if not line:             # 如果去掉后是空的
        continue             # 跳过这一行
```

文件里的"空行"长这样：`"\n"`（一个换行符），或者 `"   \n"`（几个空格加换行）。
如果你不 strip，`if not line` 判断的是 `"\n"`——它不是空字符串，所以**不会**被跳过，后面 `json.loads("\n")` 就会报错。
strip 之后变成 `""`（真正的空字符串），`not ""` 才是 `True`，才能正确跳过。

一句话：**strip 是"把肉眼看不见的空白擦干净"，让后面的判断和解析不出错。**

### 1.2 文件与路径

| 写法 | 作用 |
|---|---|
| `with open(...) as fp:` | 打开文件，并且**用完自动关闭**（不用手写 `fp.close()`） |
| `"r"` | 打开模式：read，只读 |
| `encoding="utf-8"` | 用 UTF-8 解码，中文才不乱码 |
| `encoding="utf-8-sig"` | 带 BOM 的 UTF-8，专治 Excel 导出的 CSV 开头隐藏字符 |
| `errors="replace"` | 遇到解不开的字符，用替代符号顶上，不让程序崩 |
| `newline=""` | 交给 csv 模块自己处理换行，避免 Windows 下多出空行 |
| `os.listdir(目录)` | 列出目录下所有文件名，返回列表 |
| `os.path.join(a,b)` | 拼接路径，自动补斜杠 |
| `os.path.splitext(p)[1]` | 取扩展名，如 `"产品.md"` → `".md"` |

### 1.3 Python 语法结构

| 写法 | 作用 | 例子 |
|---|---|---|
| 列表推导式 | 用一行代码从列表生成新列表 | `[f for f in files if f.endswith(".md")]` |
| `for ... in ...` | 遍历 | `for line in fp:` |
| `continue` | 跳过本次循环，进入下一次 | 读到坏行就跳过 |
| `return` | 结束函数并返回值 | |
| `try / except` | 尝试执行，出错就走 except，不让程序崩 | 解析坏 JSON 时跳过 |
| `with` | 自动管理资源（文件、连接） | 上面的 open |
| `def 名(参数):` | 定义函数 | |
| `f"...{变量}..."` | f-string，把 `{}` 里的变量值嵌进字符串 | `f"共 {len(files)} 个文件"` |
| `{!r}` | f-string 里用 repr 格式显示（字符串带引号，看得更清楚） | `f"{x!r}"` |
| `lambda` / 函数当值 | 函数可以存进字典、当参数传递 | 第 128 行的 readers 字典 |
| `递归` | 函数自己调用自己 | 第 84 行 collect 处理嵌套 JSON |
| `if __name__ == "__main__":` | 只有"直接运行本文件"时才执行，被 import 时不执行 | 第 193 行 |
| `sys.argv` | 命令行参数列表，`[0]` 是脚本名，`[1]` 是第一个参数 | 判断有没有 `--verify` |

### 1.4 几个容易混淆的"双胞胎"

| 对比 | 区别 |
|---|---|
| `json.load(fp)` vs `json.loads(s)` | load 读**文件对象**，loads 读**字符串**（s = string） |
| `dict.get(k)` vs `dict[k]` | get 找不到返回 `None` 不报错；`[]` 找不到直接 KeyError 崩溃 |
| `or` vs `and` | `a or b or ""`：从左到右取第一个"非空/真"的值；`and` 要求全部为真 |
| `isinstance(x, str)` vs `type(x) == str` | 前者更规范，子类型也算 |
| `pd.notna(v)` | Pandas 里判断"不是空值"，因为空值是 `NaN`，不能用 `v != None` |

---

## 2. 逐段精讲（对着源码看）

### 第 1~15 行：文件头说明

```python
# -*- coding: utf-8 -*-
"""把 data 目录下的知识文件导入向量库，并做一次自检。..."""
```

- 第 1 行：声明编码 UTF-8。Python 3 默认就是 UTF-8，这行是历史习惯，写上也无害（你文件里有中文注释，留着更保险）。
- 第 2~15 行：**三引号字符串**。放在文件最开头就称为"模块文档字符串"，纯说明，不影响运行。相当于贴在文件封面上的便利贴。

### 第 19~33 行：导入工具

```python
import json, os, sys                      # 合并写了，实际是三行
from dotenv import load_dotenv
load_dotenv()                             # 读取 .env，把密钥装进环境变量
import config_data as config              # 导入配置，改名 config
from knowledge_base import KnowledgeBaseService, Mydashscopeembedding, get_string_md5
from vector_stores import VectorStoreService
```

- `load_dotenv()` 是关键：你 `.env` 里的 `DASHSCOPE_API_KEY` 靠它才能被 `os.getenv()` 读到。
- `as config` 是起别名，后面写 `config.DATA_DIR` 比 `config_data.DATA_DIR` 短。
- 从 `knowledge_base` 一次导入 3 个东西：一个类（服务）、一个 embedding 类、一个 md5 函数。

### 第 35~38 行：全局常量

```python
BASE_DIR = config.DATA_DIR
SUPPORTED_EXTS = (".txt", ".md", ".json", ".jsonl", ".csv", ".xlsx")
SKIP_FILES = {"md5.txt", "README.md", "sources.md", "eval_set.jsonl"}
```

- `SUPPORTED_EXTS` 用的是**元组**（圆括号 + 逗号），`SKIP_FILES` 用的是**集合**（花括号）。集合查找速度快，适合做"在不在名单里"的判断。

### 第 41~46 行：列出要导入的文件

```python
return [
    f for f in sorted(os.listdir(BASE_DIR))
    if f.lower().endswith(SUPPORTED_EXTS) and f not in SKIP_FILES
]
```

这一坨叫**列表推导式**，拆开写成普通循环就是：

```python
结果 = []
for f in sorted(os.listdir(BASE_DIR)):           # 列出并排序目录下的文件名
    if f.lower().endswith(SUPPORTED_EXTS) \      # 扩展名在支持列表里
       and f not in SKIP_FILES:                   # 且不在跳过名单里
        结果.append(f)
return 结果
```

两种写法完全等价。列表推导式只是把 5 行压成 1 行——**看不懂时就在脑子里展开成循环**，这是最实用的阅读技巧。

### 第 49~52 行：读纯文本（md / txt）

```python
with open(path, "r", encoding="utf-8", errors="replace") as fp:
    return fp.read()
```

- `with ... as fp`：打开文件并命名为 fp；缩进块执行完后**自动关闭文件**。
- `fp.read()`：把整个文件读成一个大字符串返回。
- 类比你学过的爬虫：`requests.get(url).text` 拿到网页文本，这里 `fp.read()` 拿到文件文本，作用一样。

### 第 55~74 行：读 jsonl（每行一条 JSON）

这是术语最密集的一段，逐行拆：

```python
lines = []                                 # 准备一个空列表，用来装每条知识
for line in fp:                            # 一行一行读
    line = line.strip()                    # 擦掉首尾空白（见 1.1 节）
    if not line:                           # 擦完是空的 → 原本是空行
        continue                           # 跳过，看下一行
    try:
        obj = json.loads(line)             # 把 JSON 字符串 → Python 字典
    except json.JSONDecodeError:           # 这行不是合法 JSON
        continue                           # 跳过，不让程序崩
    content = obj.get("text") or obj.get("content") or ""
    # 上面这行：优先取 text 字段；没有就取 content；都没有就用空字符串
    title = obj.get("title", "")           # 取标题，没有就用空字符串
    if title:
        lines.append(f"【{title}】\n{content}")   # 拼成「【标题】正文」
    elif content:
        lines.append(content)
return "\n\n".join(lines)                  # 用两个换行把所有条目连成一大段
```

### 第 77~98 行：读 JSON（递归提取文字）

```python
def collect(node):                         # 函数自己调用自己 = 递归
    if isinstance(node, str):              # 如果节点是字符串
        texts.append(node)                 # 收下它
    elif isinstance(node, list):           # 如果是列表
        for item in node:
            collect(item)                  # 对每个元素再来一次
    elif isinstance(node, dict):           # 如果是字典
        for key, value in node.items():    # 遍历所有键值对
            if key in ("chars", "id"):     # 数字编号之类的元数据不要
                continue
            collect(value)                 # 对值再来一次
collect(obj)                               # 从最外层开始
```

为什么用递归？因为 JSON 可能层层嵌套（字典里套列表，列表里套字典）。递归能一直往下钻，直到钻出字符串为止。

### 第 101~122 行：读表格（CSV / Excel）

```python
for row in csv.DictReader(fp):             # 每行读成一个字典：列名→值
    parts = [f"{k}：{v}" for k, v in row.items() if v and str(v).strip()]
    #        ↑ 把每个"有值"的单元格变成 "列名：值"
    if parts:
        rows.append("；".join(parts))      # 一行里的各列用中文分号连起来
return "\n".join(rows)                     # 各行之间用换行连起来
```

为什么要把表格转成文字？因为向量库只吃文本。转成"蛋白质：4.0g；规格：200ml"这种形式，既保留了含义，检索时又容易命中关键词。

`read_xlsx` 用 `pd.read_excel()`（你学过 Pandas，这个很熟），`df.iterrows()` 逐行遍历，`pd.notna(v)` 过滤空值——逻辑和 CSV 完全一样。

### 第 125~136 行：分派器（本文件的精华）

```python
ext = os.path.splitext(path)[1].lower()     # 取扩展名并转小写
readers = {
    ".txt": read_text,                     # 注意：这里放的是"函数本身"，不是调用结果
    ".md": read_text,
    ".json": read_json,
    ...
}
return readers[ext](path)                  # 按扩展名取出函数，立刻调用它
```

**重点理解**：字典里存的是函数（`(path)` 没有加括号，所以不是调用，是把函数当值存起来）。最后一行 `readers[ext](path)` 先取出对应函数，再加 `(path)` 调用。

这样写的好处：以后要支持新格式（比如 `.pdf`），只要写个 `read_pdf` 函数，再在字典里加一行 `.pdf: read_pdf`——**别的代码一行都不用改**。这就是工程上说的"可扩展"。

### 第 139~145 行：清理测试脏数据

```python
try:
    service.chroma.delete(where={"source": "testfile"})   # 删除带这个标记的旧数据
except Exception as exc:
    print(f"[清理] 跳过（{exc}）")
```

- `try/except`：删除失败（比如老版本 Chroma 不支持 `where`）也不让程序崩，只是打印一句。
- `where={"source": "testfile"}`：相当于 SQL 的 `WHERE source='testfile'`。

### 第 148~171 行：主流程 ingest()

```python
service = KnowledgeBaseService()           # 创建服务实例
clean_test_data(service)                   # 先清脏数据
files = list_knowledge_files()             # 列出要导入的文件
if not files:                              # 一个都没有
    print(...); return                     # 打印提示并提前结束
for name in files:                         # 逐个文件处理
    path = os.path.join(BASE_DIR, name)    # 拼出完整路径
    try:
        text = read_knowledge_file(path)   # 读成文本
    except Exception as exc:               # 读失败（比如编码问题）
        print(...); continue               # 跳过这个，继续下一个
    if not text.strip():                   # 读出来是空的
        print(...); continue
    print(...)
    print("       ->", service.upload_by_str(text, name))   # 交给服务层入库
```

这段体现了两个重要的工程思想：
1. **单个文件出错不拖垮全局**：每个文件都包在 try/except 里，一个坏了继续处理其他的。
2. **自己只干"读"的活**：把文本读出来就交给 `knowledge_base` 的 `upload_by_str`，去重/切块/向量化全不管。

### 第 174~190 行：自检 verify()

```python
total = service.chroma._collection.count()  # 数库里有多少块（下划线=内部API）
sample = service.chroma.get(limit=20, include=["metadatas", "documents"])
for i, meta in enumerate(sample.get("metadatas") or []):    # enumerate 同时给索引和内容
    doc = (sample.get("documents") or [""] * 20)[i]
    print(f"  #{i} source={meta.get('source')!r} len={len(doc)} head={doc[:40]!r}")
    #   {!r} 让字符串带引号显示，{doc[:40]} 只显示前 40 字
retriever = VectorStoreService(...).get_retriever()
docs = retriever.invoke(question)          # 实际检索一次
for i, d in enumerate(docs):
    print(d.page_content[:300].replace("\n", " "))   # 打印命中的正文前 300 字
```

`or []` 是防御写法：万一 `get()` 返回 `None`，也不会因为遍历 `None` 而崩。

### 第 193~199 行：程序入口

```python
if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()                           # python ingest.py --verify → 只自检
    else:
        ingest()                           # python ingest.py → 导入
        print()
        verify()                           # 导入完顺便自检
```

`__name__` 是 Python 自动设置的变量：
- 直接运行这个文件 → `__name__` 等于 `"__main__"` → 代码块执行。
- 被别的文件 `import ingest` → `__name__` 等于 `"ingest"` → 代码块**不执行**（避免你只是导入函数却触发一遍导入流程）。

`sys.argv` 是命令行参数列表。你敲 `python ingest.py --verify`，`sys.argv` 就是 `["ingest.py", "--verify"]`，所以 `"--verify" in sys.argv` 为 True。

---

## 3. 怎么验证你真的懂了（动手练习）

光看不算懂，打开 Python 交互环境（`python` 回车），亲手试这几条：

```python
>>> "  你好\n".strip()
'你好'
>>> "README.MD".lower().endswith(".md")
True
>>> "\n\n".join(["第一段", "第二段"])
'第一段\n\n第二段'
>>> import json
>>> obj = json.loads('{"text": "刘维学过Python", "chars": 8}')
>>> obj.get("text") or obj.get("content") or ""
'刘维学过Python'
>>> [f for f in ["a.md", "b.txt", "md5.txt"] if f.endswith((".md", ".txt")) and f != "md5.txt"]
['a.md', 'b.txt']
```

每一条都对应源码里的一个实际用法。敲一遍，比看十遍印象深刻。

## 4. 下一步建议

按同样的方法继续攻：`knowledge_base.py`（md5 / 切块 / 向量化）→ `vector_stores.py`（最短，10 分钟）→ `rag.py`（chain 组装，最难，放最后）。

不要追求"一次全懂"——你从网络安全到爬虫到 RAG 只用了几个月，本来就走在快车道上。把每个"单词"查清楚、每个函数能用自己的话复述，就是真懂了。
