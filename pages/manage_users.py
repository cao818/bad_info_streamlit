import streamlit as st

from data.database import save_user
from user_management import hash_password


def manage_users_page(registered_users):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

    st.title("用户管理")
    st.write(f"当前用户: {st.session_state.logged_in_user}")

    with st.form(key='manage_users_form'):
        new_password = st.text_input("新密码", type="password")
        change_password_button = st.form_submit_button("更改密码")
        if change_password_button:
            if new_password:
                hashed_password = hash_password(new_password)
                registered_users[st.session_state.logged_in_user] = hashed_password
                save_user(st.session_state.logged_in_user, hashed_password)
                st.success("密码修改成功！")
            else:
                st.error("新密码不能为空。")

        delete_account_button = st.form_submit_button("删除账户")
        if delete_account_button:
            del registered_users[st.session_state.logged_in_user]
            save_user(registered_users)
            st.session_state.logged_in_user = None
            st.success("账户删除成功！")
            st.experimental_rerun()