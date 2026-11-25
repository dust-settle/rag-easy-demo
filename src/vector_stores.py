
from langchain_chroma import Chroma
import config_data as config
from knowledge_base import Mydashscopeembedding


class VectorStoreService(object):

    def __init__(self, embedding):
        self.embedding = embedding

        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )
    # 返回向量检索器
    def get_retriever(self):
        # v1.1：粗召回 retrieve_k 条，真正的挑选交给后面的 Reranker
        return self.vector_store.as_retriever(search_kwargs = {"k": config.retrieve_k})



if __name__ == "__main__":
    retriever = VectorStoreService(Mydashscopeembedding("text-embedding-v4")).get_retriever()

    res = retriever.invoke("这款牛奶一盒多少毫升？")

    print(res)



