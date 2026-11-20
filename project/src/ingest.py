# -*- coding: utf-8 -*-
"""把 data 目录下的知识文件导入向量库，并做一次自检。

支持格式（按扩展名自动选择读取方式）：
    .txt / .md   纯文本，直接读
    .json        单个 JSON 对象/数组，提取其中的文字
    .jsonl       每行一条 JSON（kb_chunks.jsonl 就是这种）
    .csv / .xlsx 表格，按行转成可读文本

用法（在 src 目录下执行）：
    python ingest.py            # 导入所有支持的文件
    python ingest.py --verify   # 只自检，不导入

可以重复执行：同一份内容不会重复入库（靠 md5.txt 去重）。
"""
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

import config_data as config
from knowledge_base import (
    KnowledgeBaseService,
    Mydashscopeembedding,
    get_string_md5,
)
from vector_stores import VectorStoreService

BASE_DIR = config.DATA_DIR
SUPPORTED_EXTS = (".txt", ".md", ".json", ".jsonl", ".csv", ".xlsx")
# 这些不是"知识正文"，跳过：去重记录 / 资料包说明 / 来源清单 / 评测题
SKIP_FILES = {"md5.txt", "README.md", "sources.md", "eval_set.jsonl"}


def list_knowledge_files():
    """列出 data 目录下所有可作为知识库的文件。"""
    return [
        f for f in sorted(os.listdir(BASE_DIR))
        if f.lower().endswith(SUPPORTED_EXTS) and f not in SKIP_FILES
    ]


def read_text(path):
    """纯文本：txt / md。"""
    with open(path, "r", encoding="utf-8", errors="replace") as fp:
        return fp.read()


def read_jsonl(path):
    """每行一条 JSON，取其中的文字字段，拼成可读文本。"""
    lines = []
    with open(path, "r", encoding="utf-8", errors="replace") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            # kb_chunks 里正文在 text 字段；评测集在 question 字段（已跳过）
            content = obj.get("text") or obj.get("content") or ""
            title = obj.get("title", "")
            if title:
                lines.append(f"【{title}】\n{content}")
            elif content:
                lines.append(content)
    return "\n\n".join(lines)


def read_json(path):
    """单个 JSON：递归把里面的字符串取出来。"""
    with open(path, "r", encoding="utf-8", errors="replace") as fp:
        obj = json.load(fp)

    texts = []

    def collect(node):
        if isinstance(node, str):
            texts.append(node)
        elif isinstance(node, list):
            for item in node:
                collect(item)
        elif isinstance(node, dict):
            for key, value in node.items():
                # 跳过纯编号/计数等元数据字段，只留有内容的
                if key in ("chars", "id"):
                    continue
                collect(value)

    collect(obj)
    return "\n".join(texts)


def read_csv(path):
    """CSV 表格：表头 + 每行拼成 '列名：值'，可读且检索友好。"""
    import csv
    rows = []
    with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as fp:
        for row in csv.DictReader(fp):
            parts = [f"{k}：{v}" for k, v in row.items() if v and str(v).strip()]
            if parts:
                rows.append("；".join(parts))
    return "\n".join(rows)


def read_xlsx(path):
    """Excel 表格：用 pandas 读第一个工作表，方式和 CSV 类似。"""
    import pandas as pd
    df = pd.read_excel(path)
    rows = []
    for _, row in df.iterrows():
        parts = [f"{k}：{v}" for k, v in row.items() if pd.notna(v)]
        if parts:
            rows.append("；".join(parts))
    return "\n".join(rows)


def read_knowledge_file(path):
    """按扩展名分派读取函数——以后加新格式，只在这里加一个分支。"""
    ext = os.path.splitext(path)[1].lower()
    readers = {
        ".txt": read_text,
        ".md": read_text,
        ".json": read_json,
        ".jsonl": read_jsonl,
        ".csv": read_csv,
        ".xlsx": read_xlsx,
    }
    return readers[ext](path)


def clean_test_data(service: KnowledgeBaseService):
    """清理旧测试写进来的脏数据（source='testfile'）。"""
    try:
        service.chroma.delete(where={"source": "testfile"})
        print("[清理] 已删除 source='testfile' 的测试数据")
    except Exception as exc:                       # 老版本 chroma 可能不支持 where
        print(f"[清理] 跳过（{exc}）")


def ingest():
    service = KnowledgeBaseService()
    print(f"[库] {config.persist_directory} (collection={config.collection_name})")

    clean_test_data(service)

    files = list_knowledge_files()
    if not files:
        print(f"[跳过] {BASE_DIR} 下没有可导入的文件")
        return

    print(f"[清单] 共 {len(files)} 个文件待导入")
    for name in files:
        path = os.path.join(BASE_DIR, name)
        try:
            text = read_knowledge_file(path)
        except Exception as exc:
            print(f"[跳过] {name} 读取失败：{type(exc).__name__} {exc}")
            continue
        if not text.strip():
            print(f"[跳过] {name} 没有可导入的内容")
            continue
        print(f"[导入] {name}  {len(text)} 字  md5={get_string_md5(text)}")
        print("       ->", service.upload_by_str(text, name))


def verify(question="这款牛奶一盒多少毫升，每100毫升蛋白质多少？"):
    service = KnowledgeBaseService()
    total = service.chroma._collection.count()          # noqa: SLF001 仅用于自检
    print(f"[自检] collection={config.collection_name} 当前文档块数 = {total}")

    sample = service.chroma.get(limit=20, include=["metadatas", "documents"])
    for i, meta in enumerate(sample.get("metadatas") or []):
        doc = (sample.get("documents") or [""] * 20)[i]
        print(f"  #{i} source={meta.get('source')!r} len={len(doc)} head={doc[:40]!r}")

    retriever = VectorStoreService(
        Mydashscopeembedding("text-embedding-v4")).get_retriever()
    docs = retriever.invoke(question)
    print(f"\n[检索] {question!r} -> 命中 {len(docs)} 条 (k={config.similarity_threshold})")
    for i, d in enumerate(docs):
        print(f"  --- 第{i + 1}条  source={d.metadata.get('source')!r} len={len(d.page_content)}")
        print("  " + d.page_content[:300].replace("\n", " "))


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        ingest()
        print()
        verify()
