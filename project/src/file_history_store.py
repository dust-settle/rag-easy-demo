import os, json

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from collections.abc import Sequence


import config_data as config

# 会话历史属于运行时数据，放 runtime/chat_history/runnable
STORE_DIR = os.path.join(config.RUNTIME_DIR, "chat_history", "runnable")


def get_history(session_id):
    # 同一个 session_id 永远映射到同一个文件 -> 进程重启也能接着聊（长期记忆）
    return FileChatMessageHistory(session_id, STORE_DIR)

class FileChatMessageHistory(BaseChatMessageHistory):

    def __init__(self, session_id, storage_path):
        self.session_id = session_id                # 会话id
        self.storage_path = storage_path            # 不同会话id的存储文件，所在的文件夹路径
        # 完整的文件路径（加 .json 后缀，方便查看和区分）
        self.file_path = os.path.join(self.storage_path, f"{self.session_id}.json")

        # 确保文件夹是存在的
        os.makedirs(self.storage_path, exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # sequence序列，类似list，tuple
        all_messages = list(self.messages)      # 已有消息列表
        all_messages.extend(messages)                        # 新的和已有的融合成一个list

        # 将数据同步写入到文件中
        # 类对象写入文件 -》 一堆二进制
        # 为了方便可以将BaseMessage消息转为字典(借助json模块以json字符串写入文件)
        # 官方 message_to_dict 能把【单条】BaseMessage 转成字典；
        # messages_to_dict 是给【消息列表】用的，传单条会迭代出 tuple 并报 AttributeError
        new_messages = [message_to_dict(message) for message in all_messages]
        # 将数据写入文件（ensure_ascii=False + indent 让中文可读、方便排查问题）
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=2)

    @property             # 装饰器将messages方法变成成员属性使用
    def messages(self) -> list[BaseMessage]:
        # 当前文件内: list【字典】
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)      # 返回值是:list[字典]
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            # 文件为空/内容损坏时，当作"没有历史"，不要让整个会话直接崩掉
            print(f"[警告] 历史文件损坏，已忽略: {self.file_path}")
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)