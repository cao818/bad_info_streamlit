import streamlit as st

from data.database import save_user
from user_management import hash_password, validate_username, validate_password


def register_page(registered_users):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

    st.title("用户注册")
    st.write("### 欢迎使用不良信息检测系统")

    with st.form(key='register_form'):
        new_username = st.text_input("选择用户名")
        new_password = st.text_input("设置密码", type="password")
        register_button = st.form_submit_button("注册")

        if register_button:
            if not validate_username(new_username):
                st.error("用户名无效，请使用3-20个字母、数字或下划线。")
            elif not validate_password(new_password):
                st.error("密码无效，密码至少为8个字符。")
            elif new_username in registered_users:
                st.error("该用户名已被占用，请选择其他用户名。")
            else:
                hashed_password = hash_password(new_password)
                save_user(new_username, hashed_password)
                st.success(f"用户 {new_username} 注册成功！")
                registered_users[new_username] = hashed_password