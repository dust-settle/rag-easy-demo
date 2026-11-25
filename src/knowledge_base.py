
from dotenv import load_dotenv
load_dotenv()
import hashlib
import os
import config_data as config

import dashscope
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

# 检查传入的md5字符串是否已经被处理过了
def check_md5(md5_str: str):
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w', encoding="utf-8").close()
        return False
    else:
       with open(config.md5_path, 'r', encoding="utf-8") as f:
           for line in f:
              line = line.strip()
              if line == md5_str:
                 return True

# 将传入的md5字符串，记录到文件内保存
def save_md5(md5_str: str):
    with open(config.md5_path, 'a', encoding="utf-8") as f:
        f.write(md5_str+'\n')

# 将传入的字符串转换为md5
def get_string_md5(input_str: str, encoding='utf-8'):
    # 将字符串转换为bytes字符串
    str_bytes = input_str.encode(encoding=encoding)
    #创建md5对象
    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes,)
    md5_hex = md5_obj.hexdigest()
    return md5_hex

api_key = os.getenv("DASHSCOPE_API_KEY")

class Mydashscopeembedding(Embeddings):
    def __init__(self,model_name: str = "text-embedding-v4"):
        self.model_name = model_name

    def embed_documents(self, text:list[str])->list[list[float]]:
        #  DashScope embedding 接口单次最多 10 条，超了会报 batch size invalid，
        #  所以分批调用，每批 10 条，最后把结果拼起来（个人资料较大必须这么做）
        all_embeddings = []
        for start in range(0, len(text), 10):
            batch = text[start:start + 10]
            res = dashscope.TextEmbedding.call(
                model=self.model_name,
                input=batch,
                dashscope_api_key=api_key,
                text_type="document"
            )
            if res.status_code != 200:
                raise Exception(f"调用失败: {res.message}")
            all_embeddings.extend([item["embedding"] for item in res.output["embeddings"]])
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        # 查询检索，text_type="query"（RAG召回效果更好！）
        res = dashscope.TextEmbedding.call(
            model=self.model_name,
            input=text,
            text_type="query"
        )
        if res.status_code != 200:
            raise Exception(f"调用失败：{res.message}")
        return res.output["embeddings"][0]["embedding"]


class KnowledgeBaseService(object):
    def __init__(self):
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,  # 数据库的表名
            embedding_function=Mydashscopeembedding(),
            persist_directory=config.persist_directory  # 数据库本地储存文件夹
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,  #分割后的文本段最大长度
            chunk_overlap=config.chunk_overlap,  #连续文本段之间的字符重叠数量
            separators=config.separators,    #自然段落划分的符号
            length_function=len  #使用python自带的len函数做长度统计的依据
        )

    def upload_by_str(self,data: str, filename):
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks: list[str] = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source" : filename,
            "create_time" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator" : "小明"
        }

        # v1.1 修复"旧块残留"：同名文件内容改了以后 md5 变了会重新入库，
        # 但旧版本的块还留在库里，检索时新旧会一起被召回。
        # 所以写新块之前，先按 source 把该文件的旧块全部删掉。
        try:
            self.chroma.delete(where={"source": filename})
            print(f"[更新] 已清理 {filename} 的旧版本块")
        except Exception as exc:
            print(f"[警告] 清理旧块失败（不影响新块写入）: {exc}")

        # 将内容加载到向量库中
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas = [metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)

        return "[成功]内容已经成功载入向量库"

if __name__ == '__main__':
    # 单文件自测：不要直接往正式库写测试数据，避免污染个人资料库。
    # 需要验证入库流程时，请用 data/ 下的真实资料跑 ingest.py。
    print("请用 python ingest.py 导入 data/ 下的知识库文件。")


