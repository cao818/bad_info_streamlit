import base64
import concurrent.futures
import configparser
import gettext
import hashlib
import logging
import os
import re
import shutil
import sqlite3
import tempfile
import urllib
from io import BytesIO

import cv2
import requests
import streamlit as st
from PIL import Image
#读取api
# 创建 ConfigParser 对象
config = configparser.ConfigParser()
# 读取配置文件
config.read('config.ini')
# 获取 API Key 和 Secret Key
API_KEY1 = config['DEFAULT']['API_KEY1']
SECRET_KEY1 = config['DEFAULT']['SECRET_KEY1']
API_KEY2 = config['DEFAULT']['API_KEY2']
SECRET_KEY2 = config['DEFAULT']['SECRET_KEY2']

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def configure_logging():
    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 创建文件处理程序，用于记录到文件
    file_handler = logging.FileHandler('../app.log')
    file_handler.setLevel(logging.INFO)

    # 创建控制台处理程序，用于输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 创建日志格式器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # 将格式器添加到处理程序
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理程序添加到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
configure_logging()


# Initialize session state
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# 初始化数据库
def init_db():
    conn = sqlite3.connect('../data/users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
init_db()
def load_users():
    conn = sqlite3.connect('../data/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users')
    users = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return users
# 将用户数据保存到数据库中
def save_user(username, password):
    conn = sqlite3.connect('../data/users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()


# 修改注册函数以保存到数据库
def register_page(registered_users):
    st.title("用户注册")
    st.write("### Welcome to the Bad Information Detection System")
    new_username = st.text_input("Choose a username", key="register_username")
    new_password = st.text_input("Set a password", type="password", key="register_password")
    register_button = st.button("Register")

    if register_button:
        if new_username in registered_users:
            st.error("This username is already taken. Please choose another one.")
        elif new_username and new_password:
            hashed_password = hash_password(new_password)
            save_user(new_username, hashed_password)  # 在这里调用哈希函数来保存密码
            st.success(f"User {new_username} registered successfully!")
        else:
            st.error("Username and password cannot be empty.")

def get_file_content_as_base64(file_path, urlencoded=False):
    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content
def get_access_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            logging.error(f"Error: {result['error']}")
            st.error(f"Error: {result['error']}")
            return None
        return result["access_token"]
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        st.error(f"Request failed: {e}")
        return None


def set_language(language_code):
    lang = gettext.translation('messages', localedir='locale', languages=[language_code], fallback=True, codeset='utf-8')
    lang.install()
    _ = lang.gettext
    return _




def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def upload_text(api_key, secret_key, text):
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "text": text,
        "type": "1",  # 1表示自定义敏感词，2表示自定义敏感句子
        "custom_dict": '{"敏感词1": "替换词1", "敏感词2": "替换词2"}'
    }
    params = {"access_token": get_access_token(api_key, secret_key)}

    # 调用文本检测API
    response = requests.post(url, data=data, params=params, headers=headers)
    result = response.json()
    return result
# 可以使用st.cache缓存已经处理的结果。对于视频处理，可以缓存每一帧的检测结果。
@st.cache
def upload_image(image_path):
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token=" + get_access_token(
        API_KEY2, SECRET_KEY2)
    image = get_file_content_as_base64(image_path, True)
    payload = "image=" + str(image)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    result = response.json()
    return result
def process_frame(frame, frame_path):
    cv2.imwrite(frame_path, frame)
    return upload_image(frame_path)
def upload_video(video_path):
    frame_directory = "frames"
    if not os.path.exists(frame_directory):
        os.makedirs(frame_directory)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps / 2)

    count = 0
    results = []
    frame_paths = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frame_path = os.path.join(frame_directory, f"frame{count:03d}.jpg")
            frame_paths.append((frame, frame_path))
        count += 1

    cap.release()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_frame = {executor.submit(process_frame, frame, path): path for frame, path in frame_paths}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_frame)):
            results.append(future.result())
            st.progress((i + 1) / len(frame_paths))

    shutil.rmtree(frame_directory)
    return results
# 可以将每一帧的检测结果显示在页面上，以便用户更好地了解具体哪个帧存在问题。
def display_video_results(results):
    for count, result in enumerate(results):
        st.markdown(f"### Frame {count}")
        if result.get("conclusion") == "不合规":
            st.error(f"Frame {count} contains inappropriate content!")
        else:
            st.success(f"Frame {count} is normal.")
        st.write(result)


# 登录页面
def login_page(registered_users):
    st.title("用户登录")
    st.write("### 欢迎来到不良信息检测系统")
    username = st.text_input("用户名", key="login_username")
    password = st.text_input("密码", type="password", key="login_password")
    login_button = st.button("登录")

    if login_button:
        hashed_password = hash_password(password)
        if username in registered_users and registered_users[username] == hashed_password:
            st.session_state.logged_in_user = username
            st.success("登录成功！")
        else:
            st.error("用户名或密码无效。")





def main_page():

    # gettext.bindtextdomain('messages', 'locale')
    # gettext.textdomain('messages')
    # _ = gettext.gettext
    #
    # if _ is None:
    #     logging.error("Error setting language. Defaulting to English.")
    #     st.error("Error setting language. Defaulting to English.")
    #     return
    #
    # # 假设用户选择语言
    # language_code = st.selectbox("选择语言", ["en", "zh"])
    # _ = set_language(language_code)
    #
    # # 在代码中使用翻译函数
    # st.title(_("不良信息检测系统"))
    # st.header(_("文本检测"))

    # 文本检测
    st.header("文本检测")
    text_input = st.text_area("输入文本:")
    if st.button("检测文本"):
        result = upload_text(API_KEY1, SECRET_KEY1, text_input)
        if result.get("conclusion") == "不合规":
            st.error("检测为不良文本!")
        else:
            st.success("文本正常")
        st.write(result)

    # 图像检测
    st.header("图像检测")
    uploaded_image = st.file_uploader("上传图像", type=["jpg", "png", "jpeg"])
    display_image = st.checkbox("显示图像")
    if uploaded_image is not None:
        # 创建一个临时文件夹
        temp_folder = tempfile.mkdtemp()
        # 获取上传的文件名
        image_filename = os.path.join(temp_folder, uploaded_image.name)
        # 将上传的图片数据写入临时文件
        with open(image_filename, "wb") as f:
            f.write(uploaded_image.read())

        # 显示上传的图像     #这里也要加一个按钮看是否要显示
        # st.image(Image.open(image_filename), caption="Uploaded Image", use_column_width=True)

        if uploaded_image is not None and display_image:
            # 显示上传的图像
            st.image(Image.open(image_filename), caption="Uploaded Image", use_column_width=True)

        st.markdown("### 图像检测结果:")
        result = upload_image(image_filename)
        if result.get("conclusion") == "不合规":
            st.error("检测为不良图像!")
        else:
            st.success("图像正常")
        st.write(result)
        # 清理临时文件夹
        shutil.rmtree(temp_folder)

    # 视频检测
    st.header("视频检测")
    uploaded_video = st.file_uploader("上传视频", type=["mp4"])
    display_video = st.checkbox("显示视频")
    if uploaded_video is not None:
        # 创建一个临时文件夹
        temp_folder = tempfile.mkdtemp()
        # 获取上传的文件名
        video_filename = os.path.join(temp_folder, uploaded_video.name)
        # 将上传的视频数据写入临时文件
        with open(video_filename, "wb") as f:
            f.write(uploaded_video.read())

        # 显示上传的视频  #这里要看加一个按钮是否要显示
        if display_video:
            video_file = open(video_filename, "rb").read()
            video_bytes = BytesIO(video_file)
            st.video(video_bytes, format="video/mp4", start_time=0)

        st.markdown("### 视频检测结果:")
        # 调用视频检测函数
        results = upload_video(video_filename)
        display_video_results(results)
        # 检查每一帧的检测结果
        for count, result in enumerate(results):
            if result.get("conclusion") == "不合规":
                st.error("视频中检测到不良图像!")
                st.write(result)
                break
            else:
                st.success("视频正常")

        # 清理临时文件夹
        shutil.rmtree(temp_folder)


# Rest of the code remains the same...
# 增加用户修改密码和删除用户功能。
def manage_users_page(registered_users):
    st.title("用户管理")
    st.write("### Manage your account")

    if st.button("Log Out"):
        st.session_state.logged_in_user = None
        st.success("Logged out successfully.")

    if st.button("Change Password"):
        new_password = st.text_input("New Password", type="password", key="new_password")
        if new_password:
            hashed_password = hash_password(new_password)
            registered_users[st.session_state.logged_in_user] = hashed_password
            save_user(st.session_state.logged_in_user, hashed_password)  # 更新密码到数据库
            st.success("Password changed successfully.")

    if st.button("Delete Account"):
        del registered_users[st.session_state.logged_in_user]
        save_user(registered_users)  # 更新用户信息到数据库
        st.session_state.logged_in_user = None
        st.success("Account deleted successfully.")


# 切换页面
def switch_page(registered_users):
    if st.session_state.logged_in_user:
        main_page()
    else:
        selected_page = st.sidebar.selectbox("Select Page", ["Login", "Register"])
        if selected_page == "Login":
            login_page(registered_users)
        else:
            register_page(registered_users)

# 加载用户数据
registered_users = load_users()
# 根据用户的选择显示页面
switch_page(registered_users)
