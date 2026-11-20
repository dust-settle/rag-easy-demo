from zoneinfo import reset_tzpath

import streamlit as st
import time

from yaml import add_implicit_resolver

from rag import RagService
import config_data as config

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

    ai_res_list = []

    with st.spinner("AI思考中。。。"):
        res_stream = st.session_state["rag"].chain.stream({"input": prompt}, config.session_config)

        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
