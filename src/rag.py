from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from pydantic import BaseModel, Field
from file_history_store import get_history
load_dotenv()
import os
from dashscope import TextReRank
from vector_stores import VectorStoreService
from knowledge_base import Mydashscopeembedding
import  config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_qwq import ChatQwen


class AnswerOutput(BaseModel):
    """v1.2：客服回答的结构化输出格式。

    用 Pydantic 定义字段，大模型会按这个格式返回，LangChain 自动校验类型。
    - answer:     给顾客的回答正文
    - sources:    回答依据的资料来源文件名列表（没有依据就空列表）
    - confidence: 把握程度 0~1
    - need_human: 是否建议转人工
    """
    answer: str = Field(description="给顾客的回答正文，简洁专业友好")
    sources: list[str] = Field(default_factory=list, description="回答依据的资料来源文件名列表，没有依据则为空列表")
    confidence: float = Field(description="对回答的把握程度，0到1之间；资料明确时接近1，资料不足时较低")
    need_human: bool = Field(description="当资料不足、涉及价格促销库存或医疗健康判断时设为true，建议转人工")


def to_output_dict(obj: AnswerOutput) -> dict:
    """把 Pydantic 对象转成字典，兼容会话历史中间件。

    RunnableWithMessageHistory 只认字符串/字典，直接吃 Pydantic 对象会报错，
    且历史写不进去。转成字典后：
    - output 键：拼上来源标注的完整文本，给历史中间件存进对话历史
    - 其余键：完整结构化字段，留给前端分开显示
    """
    tail = f"\n\n（资料来源：{'、'.join(obj.sources)}）" if obj.sources else ""
    return {
        "output": obj.answer + tail,
        "answer": obj.answer,
        "sources": obj.sources,
        "confidence": obj.confidence,
        "need_human": obj.need_human,
    }


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
                 "不引导站外交易。\n"
                 "4. 把回答依据的资料来源文件名填入 sources 字段（如 ['07_FAQ.md']）；"
                 "资料不足或无依据时 sources 留空列表，不要编造来源。\n"
                 "5. 资料里有明确依据时 confidence 接近 1；资料没有答案或需要主观判断时降低 confidence。"
                 "当资料不足、涉及价格/促销/库存、或医疗健康判断时把 need_human 设为 true，建议转人工。"),
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

        def retrieve_and_rerank(value) -> list:
            """取问题 -> Chroma 粗召回 -> DashScope Reranker 精排 -> 文档列表。

            v1.1 新增：粗召回 retrieve_k 条，重排后只留 rerank_top_n 条。
            重排接口失败时自动降级为原始顺序，不让整个问答崩掉。
            """
            raw = value["input"]
            # 兼容 value["input"] 是纯字符串，或经过消息历史包装后的一层 dict
            query = raw["input"] if isinstance(raw, dict) else raw

            docs = retriever.invoke(query)
            if not docs:
                return docs
            try:
                resp = TextReRank.call(
                    model=config.rerank_model_name,
                    query=query,
                    documents=[d.page_content for d in docs],
                    top_n=config.rerank_top_n,
                    api_key=os.getenv("DASHSCOPE_API_KEY"),
                )
                if resp.status_code != 200:
                    print(f"[重排] 调用失败：{resp.message}，退回原始顺序")
                    return docs[:config.rerank_top_n]
                # output["results"] 形如 [{"index": 2, "relevance_score": 0.9}]，已按相关度降序
                results = resp.output["results"]
                return [docs[item["index"]] for item in results]
            except Exception as exc:
                print(f"[重排] 异常：{exc}，退回原始顺序")
                return docs[:config.rerank_top_n]

        def formar_for_prompt_template(value):
                new_value = {}
                new_value["input"] = value["input"]["input"]
                new_value["context"] = value["context"]
                new_value["history"] = value["input"]["history"]
                return new_value

        # v1.2：用结构化输出替代 StrOutputParser，模型直接返回 AnswerOutput 对象
        structured_model = self.chat_model.with_structured_output(AnswerOutput)

        chain = (
             {
                    "input": RunnablePassthrough(),
                    "context": RunnableLambda(retrieve_and_rerank) | format_document
             } | RunnableLambda(formar_for_prompt_template) | self.prompt_template | print_prompt
             | structured_model | RunnableLambda(to_output_dict)
    )

        conversation_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
            output_messages_key="output",   # v1.2：从字典的 output 键取文本写入历史
        )
        return conversation_chain

if __name__ == '__main__':
    session_config = {
        "configurable":{
            "session_id": "user_001"
        }
    }
    res = RagService().chain.invoke({"input":"这款牛奶一盒多少毫升？"}, session_config)
    print("回答:", res["answer"])
    print("来源:", res["sources"])
    print("置信度:", res["confidence"])
    print("建议转人工:", res["need_human"])
