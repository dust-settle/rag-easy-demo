# 基于streamlit完成WEB网页上传服务
import streamlit as st
from knowledge_base import KnowledgeBaseService
import time
from huggingface_hub import upload_file
# 使用streamlit run 03rag项目/data/app_file_upload.py启动
st.title("知识库更新服务")

upload_file = st.file_uploader(
    '"请上传TXT文件',
    type = ['txt'],
    accept_multiple_files = False,      #是否接受多文件上传
)

service = KnowledgeBaseService()
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()

if upload_file is not None:
    file_name = upload_file.name
    file_type = upload_file.type
    file_size = upload_file.size

    st.subheader(f"文件名:{file_name}")
    st.write(f"格式:{file_type} | 大小:{file_size:.2f} kB)")

    text = upload_file.getvalue().decode("utf-8")

    with st.spinner("载入知识库中。。。"):
        time.sleep(1)
    result = st.session_state["service"].upload_by_str(text, file_name)
    st.write(result)