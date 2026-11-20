
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
        return self.vector_store.as_retriever(search_kwargs = {"k":config.similarity_threshold})



if __name__ == "__main__":
    retriever = VectorStoreService(Mydashscopeembedding("text-embedding-v4")).get_retriever()

    res = retriever.invoke("刘维学过哪些技术？")

    print(res)



