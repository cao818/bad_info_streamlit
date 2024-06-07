# 导入所需库
import logging
import os
import tempfile
from functools import lru_cache
import streamlit as st
from PIL import Image
from config.config import load_config
from data.database import init_db, load_users, save_user
from functions.image_processing import image_processing
from functions.text_processing import text_processing
from functions.video_processing import video_processing
from user_management import hash_password, validate_password, validate_username
from utils import display_video_results, configure_logging,save_uploaded_file,visualize_detection_results

# 加载配置文件
config = load_config('../config/config.ini')
API_KEY1 = config['DEFAULT']['API_KEY1']
SECRET_KEY1 = config['DEFAULT']['SECRET_KEY1']
API_KEY2 = config['DEFAULT']['API_KEY2']
SECRET_KEY2 = config['DEFAULT']['SECRET_KEY2']

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
configure_logging()

# 初始化数据库
init_db('../data/users.db')
registered_users = load_users('../data/users.db')

# 初始化用户session状态
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# 设置页面标题和样式
st.markdown(open("../custom_styles.css").read(), unsafe_allow_html=True)

@lru_cache(maxsize=128)
def cached_upload_image(api_key, secret_key, image_path):
    return image_processing(api_key, secret_key, image_path)

# 用户交互和体验优化
def register_page():
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


def login_page():
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


def text_detection_page():
    st.title("文本检测")
    st.write("### 在下方输入文本进行检测")

    with st.form(key='text_detection_form'):
        text_input = st.text_area("输入文本:", height=150)
        detect_button = st.form_submit_button("检测文本")

        if detect_button:
            try:
                result = text_processing(API_KEY1, SECRET_KEY1, text_input)
                if result.get("conclusion") == "不合规":
                    st.error("检测为不良文本!")
                else:
                    st.success("文本正常")
                st.write(result)
            except Exception as e:
                logging.error(f"文本检测失败: {e}")
                st.error("文本检测失败，请稍后再试。")





def image_detection_page():
    st.title("图像检测")
    st.write("### 上传图像进行检测")

    uploaded_image = st.file_uploader("上传图像", type=["jpg", "png", "jpeg"])
    display_image = st.checkbox("显示图像")
    if uploaded_image:
        with tempfile.TemporaryDirectory() as temp_folder:
            image_filename = os.path.join(temp_folder, uploaded_image.name)
            with open(image_filename, "wb") as f:
                f.write(uploaded_image.read())

            if display_image:
                st.image(Image.open(image_filename), caption="上传的图像", use_column_width=True)

            st.markdown("### 图像检测结果:")
            try:
                result = image_processing(API_KEY2, SECRET_KEY2, image_filename)
                visualize_detection_results([result.get("conclusion")])
                if result.get("conclusion") == "不合规":
                    st.error("检测为不良图像!")
                else:
                    st.success("图像正常")
                st.write(result)
            except Exception as e:
                logging.error(f"图像检测失败: {e}")
                st.error("图像检测失败，请稍后再试。")


def batch_image_detection_page():
    st.title("批量图像检测")
    st.write("### 上传多个图像进行检测")

    uploaded_images = st.file_uploader("上传图像", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    display_images = st.checkbox("显示图像")
    if uploaded_images:
        with tempfile.TemporaryDirectory() as temp_folder:
            for uploaded_image in uploaded_images:
                image_filename = os.path.join(temp_folder, uploaded_image.name)
                with open(image_filename, "wb") as f:
                    f.write(uploaded_image.read())

                if display_images:
                    st.image(Image.open(image_filename), caption=uploaded_image.name, use_column_width=True)

                st.markdown(f"### 图像 {uploaded_image.name} 检测结果:")
                try:
                    result = image_processing(API_KEY2, SECRET_KEY2, image_filename)
                    if result.get("conclusion") == "不合规":
                        st.error(f"检测为不良图像: {uploaded_image.name}")
                    else:
                        st.success(f"图像 {uploaded_image.name} 正常")
                    st.write(result)
                except Exception as e:
                    logging.error(f"图像 {uploaded_image.name} 检测失败: {e}")
                    st.error(f"图像 {uploaded_image.name} 检测失败，请稍后再试。")


def video_detection_page():
    st.title("视频检测")
    st.write("### 上传视频进行检测")

    uploaded_video = st.file_uploader("上传视频", type=["mp4"])
    display_video = st.checkbox("显示视频")
    if uploaded_video:
        with tempfile.TemporaryDirectory() as temp_folder:
            video_filename = os.path.join(temp_folder, uploaded_video.name)
            with open(video_filename, "wb") as f:
                f.write(uploaded_video.read())

            if display_video:
                st.video(video_filename, format="video/mp4", start_time=0)

            st.markdown("### 视频检测结果:")
            try:
                results = video_processing(video_filename)
                display_video_results(results)
                for count, result in enumerate(results):
                    if result.get("conclusion") == "不合规":
                        st.error("视频中检测到不良图像!")
                        st.write(result)
                        break
                    else:
                        st.success("视频正常")
            except Exception as e:
                logging.error(f"视频检测失败: {e}")
                st.error("视频检测失败，请稍后再试。")


def manage_users_page():
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


def switch_page():
    # 通过侧边栏选择页面
    if st.session_state.logged_in_user:
        st.sidebar.title(f"欢迎, {st.session_state.logged_in_user}")
        selected_page = st.sidebar.selectbox("选择页面",
                                             ["文本检测", "图像检测", "视频检测", "批量图像检测", "用户管理"])
        if selected_page == "文本检测":
            text_detection_page()
        elif selected_page == "图像检测":
            image_detection_page()
        elif selected_page == "视频检测":
            video_detection_page()
        elif selected_page == "批量图像检测":
            batch_image_detection_page()
        elif selected_page == "用户管理":
            manage_users_page()
    else:
        selected_page = st.sidebar.selectbox("选择页面", ["登录", "注册"])
        if selected_page == "登录":
            login_page()
        else:
            register_page()


# 启动程序
switch_page()
