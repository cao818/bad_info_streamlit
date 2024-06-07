import streamlit as st
from user_management import hash_password

def login_page(registered_users):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

    st.title("用户登录")
    st.write("### 欢迎使用不良信息检测系统")

    with st.form(key='login_form'):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        login_button = st.form_submit_button("登录")

        if login_button:
            hashed_password = hash_password(password)
            if username in registered_users and registered_users[username] == hashed_password:
                st.session_state.logged_in_user = username
                st.success("登录成功！")
            else:
                st.error("用户名或密码无效。")