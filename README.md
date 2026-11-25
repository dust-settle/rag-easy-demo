# 英冠 4.0 牛奶 · RAG 智能客服

一个基于 **RAG（检索增强生成）** 的智能客服项目：把产品资料导入本地向量库，用户提问时先检索相关资料，再交给大模型组织成专业、合规的回答。

本项目是一个**学习用的 RAG 基础工程**，代码保持简单直白，适合一步步理解和改造。

---

## 一、它能做什么

- **有据可依地回答**：只根据知识库里的资料回答，资料里没有的就说"没有提到"，不编造产品信息。
- **多格式资料入库**：支持 `md`、`txt`、`json`、`jsonl`、`csv`、`xlsx` 六种格式。
- **合规红线**：内置牛奶品类的合规要求（1 岁以内婴儿不建议、不承诺疗效、不用绝对化用语等）。
- **多轮对话**：保留聊天历史，能结合上下文追问。
- **去重与幂等**：靠 md5 记录防止同一份资料重复入库，脚本可反复执行。

技术栈：

| 组件                        | 用途            |
| ------------------------- | ------------- |
| Python 3.14               | 运行环境          |
| LangChain + langchain-qwq | 编排检索与问答链路     |
| 阿里云百炼（DashScope）          | 文字转向量 + 大模型回答 |
| Chroma                    | 本地向量数据库       |
| Streamlit                 | 网页聊天界面        |



---

## 二、目录结构

```
rag-easy-demo/               ← 仓库根（.git 在这一层）
├── README.md               ← 本文件
├── src/                    ← 7 个 Python 源码（核心代码）
├── data/                   ← 原始知识资料（要传 GitHub）
├── runtime/                ← 运行时数据（向量库等，不传 GitHub）
├── .env                    ← API 密钥（绝不传 GitHub，已加入 .gitignore）
├── .gitignore              ← 忽略规则（密钥/缓存/运行时数据）
├── 项目结构说明.md          ← 每个文件夹/文件的详细用途
└── ingest逐行精讲.md        ← 学习文档：逐行讲解 ingest.py
```

每个文件具体干什么，见 [`项目结构说明.md`](项目结构说明.md)。

---

## 三、快速开始（从零跑通）

以下命令都在**仓库根目录**执行。

### 1. 准备 Python 环境

建议用 Python 3.14，并为项目单独建一个虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安装依赖

```powershell
pip install streamlit==1.67.0 langchain==1.5.0 langchain-core==1.8.2 langchain-community==0.4.2 langchain-qwq chromadb==1.5.9 dashscope==2.0.3 python-dotenv==1.2.4 pandas==3.1.1 ollama==0.6.3
```

> 如果要导入 `.xlsx` 文件，还需额外安装 `openpyxl`。

### 3. 配置密钥

在**仓库根目录**新建 `.env` 文件，填入你的阿里云百炼密钥：

```
DASHSCOPE_API_KEY=你的密钥
```

密钥去阿里云百炼控制台申请。这个文件**绝对不要提交到 GitHub**。

### 4. 导入知识库

把资料放进 `data\`，然后进入 `src` 目录执行一次入库脚本：

```powershell
cd src
python ingest.py
```

看到导入成功的日志后，可以跑自检确认检索正常：

```powershell
python ingest.py --verify
```

> 规则：**改了 `data\` 里的资料，就要重新跑一次 `ingest.py`**，新资料才会生效。

### 5. 启动聊天界面

仍在 `src` 目录下：

```powershell
streamlit run app_qa.py
```

浏览器打开 `http://localhost:8501` 即可对话。

如果提示找不到 `streamlit` 命令，用这个等价写法：

```powershell
python -m streamlit run app_qa.py
```

---

## 四、常见问题

**Q：为什么回答不出内容 / 页面报 Missing credentials？**  
A：`.env` 没放对或没填密钥。程序从运行目录附近查找它，确认仓库根目录的 `.env` 存在且键名是 `DASHSCOPE_API_KEY`。

**Q：为什么打开前端问不到新加的资料？**  
A：没跑 `ingest.py`。资料放进 `data\` 后必须先入库。

**Q：为什么在仓库根目录运行 `streamlit run app_qa.py` 找不到文件？**  
A：`app_qa.py` 在 `src\` 子目录里，先 `cd src` 再运行。

**Q：会联网搜索吗？**  
A：不会。它只检索本地知识库；联网只是调用阿里云接口做向量化和生成回答，不会去互联网找新资料。

---

## 五、上传 GitHub 前必读

提交前请确认以下内容**不会**被上传：

| 内容                     | 原因                |
| ---------------------- | ----------------- |
| `.env`                 | 含真实 API 密钥，泄露会被盗用 |
| `runtime/`             | 向量库和聊天记录，体积大且是生成物 |
| `.venv/`               | 虚拟环境，平台相关且体积大     |
| `.idea/`               | 编辑器个人配置           |
| `__pycache__/`、`*.pyc` | Python 编译缓存       |

本项目已经配置好 `.gitignore`（内容如下），并已实测 `git add -A` 不会暂存任何敏感文件；`.env` 也从未进入过提交历史：

```gitignore
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
.venv/
runtime/
.idea/
```

万一 `.env` 曾被误加到暂存区，用下面的命令移除（硬盘上的文件会保留）：

```powershell
git rm --cached .env
```

别人 clone 后，按上面"快速开始"的步骤装依赖、填自己的密钥、跑一次 `ingest.py` 重建向量库，即可使用。

---

## 六、说明

这是学习阶段的项目，故意保持了简单结构，方便对照着理解 RAG 的每一步。后续可以按版本逐步打磨（例如配置集中化、引用溯源、按语义分块、加测试等）。详细的改进方向见 [`项目结构说明.md`](项目结构说明.md)。
