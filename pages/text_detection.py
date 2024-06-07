import logging
import streamlit as st
from functions.text_processing import text_processing


def text_detection_page(API_KEY, SECRET_KEY):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

    st.title("文本检测")
    st.write("### 在下方输入文本进行检测")

    with st.form(key='text_detection_form'):
        text_input = st.text_area("输入文本:", height=150)
        detect_button = st.form_submit_button("检测文本")

        if detect_button:
            try:
                result = text_processing(API_KEY, SECRET_KEY, text_input)
                if result.get("conclusion") == "不合规":
                    st.error("检测为不良文本!")
                else:
                    st.success("文本正常")
                st.write(result)
            except Exception as e:
                logging.error(f"文本检测失败: {e}")
                st.error("文本检测失败，请稍后再试。")
