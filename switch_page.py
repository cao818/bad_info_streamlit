import logging
import streamlit as st

from utils import configure_logging
from config.config import load_config
from data.database import init_db, load_users

from pages.register import register_page
from pages.login import login_page
from pages.text_detection import text_detection_page
from pages.image_detection import image_detection_page
from pages.batch_image_detection import batch_image_detection_page
from pages.video_detection import video_detection_page
from pages.manage_users import manage_users_page

# 加载配置文件
config = load_config('config/config.ini')
API_KEY1 = config['DEFAULT']['API_KEY1']
SECRET_KEY1 = config['DEFAULT']['SECRET_KEY1']
API_KEY2 = config['DEFAULT']['API_KEY2']
SECRET_KEY2 = config['DEFAULT']['SECRET_KEY2']

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
configure_logging()

# 初始化数据库
init_db('data/users.db')
registered_users = load_users('data/users.db')

# 设置页面标题和样式
file_name="custom_styles.css"
with open(file_name) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 初始化会话状态
if 'page' not in st.session_state:
    st.session_state.page = "登录"  # 默认页面
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

def switch_page():
    # 如果用户已登录
    if st.session_state.logged_in_user:
        st.sidebar.title(f"欢迎, {st.session_state.logged_in_user}")
        page_options = ["文本检测", "图像检测", "视频检测", "批量图像检测", "用户管理"]
        if st.session_state.page not in page_options:
            st.session_state.page = page_options[0]  # 如果当前页面不在选项中，重置为第一个页面
        selected_page = st.sidebar.selectbox("选择页面", page_options, index=page_options.index(st.session_state.page))
        st.session_state.page = selected_page  # 更新当前选择的页面

        # 根据选择的页面调用相应的页面处理函数
        if selected_page == "文本检测":
            text_detection_page(API_KEY1, SECRET_KEY1)
        elif selected_page == "图像检测":
            image_detection_page(API_KEY2, SECRET_KEY2)
        elif selected_page == "视频检测":
            video_detection_page(API_KEY2, SECRET_KEY2)
        elif selected_page == "批量图像检测":
            batch_image_detection_page(API_KEY2, SECRET_KEY2)
        elif selected_page == "用户管理":
            manage_users_page(registered_users)
    else:
        # 用户未登录
        page_options = ["登录", "注册"]
        if st.session_state.page not in page_options:
            st.session_state.page = page_options[0]  # 如果当前页面不在选项中，重置为第一个页面
        selected_page = st.sidebar.selectbox("选择页面", page_options, index=page_options.index(st.session_state.page))
        st.session_state.page = selected_page  # 更新当前选择的页面

        # 根据选择的页面调用相应的页面处理函数
        if selected_page == "登录":
            login_page(registered_users)
        else:
            register_page(registered_users)


# 启动程序
switch_page()
