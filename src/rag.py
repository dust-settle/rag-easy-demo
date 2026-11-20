from dotenv import load_dotenv
from langchain_classic.chains.qa_generation.prompt import templ1
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from file_history_store import get_history
load_dotenv()
import os
from vector_stores import VectorStoreService
from knowledge_base import Mydashscopeembedding
import  config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_qwq import ChatQwen


def print_prompt(prompt):
    print("=" * 20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt




class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding=Mydashscopeembedding(config.embedding_model_name),
        )

        self.prompt_template = ChatPromptTemplate(
            [
                ("system", "你是英冠 4.0 有机纯牛奶的客服助手。"
                 "根据下面提供的知识库资料，简洁、专业、友好地回答顾客问题。"
                 "参考资料:{context}。"),
                ("system", "重要规则：\n"
                 "1. 严格以参考资料为准，资料里没有的就回答"
                 "'抱歉，资料中没有提到这一点'，不要编造产品信息。\n"
                 "2. 资料中标注 verified=medium 的内容（如保质期、工厂、产地）"
                 "回答时要提醒'以实物包装为准'；标注 verified=low 的价格、促销、库存"
                 "不得给出确定数值，要引导顾客查看商品页。\n"
                 "3. 合规红线：不承诺长高、提高免疫力、治疗疾病、防骨质疏松等功效，"
                 "不替代医生判断，1 岁以内婴儿不建议喝纯牛奶，不使用'最好/第一/唯一/绝对'等绝对化用语，"
                 "不引导站外交易。"),
                ("system", "之前的对话历史如下:"),
                MessagesPlaceholder("history"),
                ("user", "请回答顾客提问:{input}")
            ]
        )

        self.chat_model = ChatQwen(
            model = config.chat_model_name,
            api_key = os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://cn-beijing.maas.qianwenaiapi.com/compatible-mode/v1"
        )

        self.chain = self.__get_chain()

    def __get_chain(self):
        retriever = self.vector_service.get_retriever()


        def format_document(docs: list(Document)):
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段:{doc.page_content}\n文档元数据:{doc.metadata}\n\n"

            return formatted_str

        def formar_for_retriever(value: dict) -> str:
            return value["input"]

        def formar_for_prompt_template(value):
                new_value = {}
                new_value["input"] = value["input"]["input"]
                new_value["context"] = value["context"]
                new_value["history"] = value["input"]["history"]
                return new_value

        chain = (
             {
                    "input": RunnablePassthrough(),
                    "context": RunnableLambda(formar_for_retriever) | retriever | format_document
             } | RunnableLambda(formar_for_prompt_template) | self.prompt_template | print_prompt | self.chat_model | StrOutputParser()
    )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain

if __name__ == '__main__':
    session_config = {
        "configurable":{
            "session_id": "user_001"
        }
    }
    res = RagService().chain.invoke({"input":"这款牛奶一盒多少毫升？"}, session_config)
    print(res)
