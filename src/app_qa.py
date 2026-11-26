import streamlit as st
import time

from rag import RagService
import config_data as config


def typewriter(text: str, cache: list):
    """v1.2：把完整回答逐字吐出，模拟打字机效果。

    结构化输出返回的是完整字典，stream() 只会给 1 块，没法像以前那样逐 token 显示，
    所以这里拿到 answer 后手动切成一个个字符 yield 给 write_stream。
    同时把每个字符存进 cache，循环结束后拼回完整文本存入会话历史。
    """
    for char in text:
        cache.append(char)
        yield char
        time.sleep(0.01)   # 每字停顿 10 毫秒，肉眼看得出打字效果

# 标题
st.title("英冠 4.0 牛奶 · 智能客服")
st.caption("基于产品知识库回答，资料里没有的不会编造")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "您好，我是英冠 4.0 有机纯牛奶客服，请问想了解什么？"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])


# 用户输入栏
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    with st.spinner("AI思考中。。。"):
        # v1.2：结构化输出返回完整字典，改用 invoke 一次拿到所有字段
        result = st.session_state["rag"].chain.invoke({"input": prompt}, config.session_config)

    answer_cache = []
    with st.chat_message("assistant"):
        st.write_stream(typewriter(result["answer"], answer_cache))

        # 结构化字段分开显示——这是 v1.2 演示效果的核心
        cols = st.columns([3, 1])
        with cols[0]:
            if result["sources"]:
                st.caption("资料来源：" + "、".join(result["sources"]))
            else:
                st.caption("资料来源：无（回答未依据知识库资料）")
        with cols[1]:
            confidence = result["confidence"]
            st.caption(f"置信度：{confidence:.0%}")

        if result["need_human"]:
            st.warning("⚠️ 该问题建议转人工客服进一步确认")

    # 界面历史仍存纯回答文本，保持原有显示逻辑不变
    st.session_state["message"].append({"role": "assistant", "content": "".join(answer_cache)})
