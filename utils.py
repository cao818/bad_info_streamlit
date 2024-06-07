import gettext
import logging
import os
import smtplib
from email.mime.text import MIMEText

import aiofiles
import requests
import streamlit as st
from matplotlib import pyplot as plt


def set_language(language_code):
    """
    设置语言代码并返回相应的翻译函数。

    :param language_code: 语言代码
    :return: 翻译函数 _
    """
    lang = gettext.translation('messages', localedir='locale', languages=[language_code])
    lang.install()
    _ = lang.gettext
    return _


def get_access_token(api_key, secret_key):
    """
    获取百度API的访问令牌。

    :param api_key: API Key
    :param secret_key: Secret Key
    :return: 访问令牌或None
    """
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
        return result.get("access_token")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        st.error(f"Request failed: {e}")
        return None


def display_video_results(results):
    """
    显示视频检测结果。

    :param results: 检测结果列表
    """
    for count, result in enumerate(results):
        print(f"### Frame {count}")
        if result.get("conclusion") == "不合规":
            print(f"Frame {count} contains inappropriate content!")
        else:
            print(f"Frame {count} is normal.")
        print(result)


def send_reset_email(email, reset_token):
    """
    发送重置密码的邮件。

    :param email: 收件人邮箱
    :param reset_token: 重置令牌
    """
    msg = MIMEText(f"请点击以下链接重置您的密码: https://example.com/reset_password?token={reset_token}")
    msg['Subject'] = '重置密码'
    msg['From'] = 'no-reply@example.com'
    msg['To'] = email

    try:
        server = smtplib.SMTP('smtp.example.com')
        server.login('your_email@example.com', 'your_password')
        server.sendmail('no-reply@example.com', [email], msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f"发送邮件失败: {e}")
        st.error("发送邮件失败，请稍后再试。")


def configure_logging():
    """
    配置日志记录器。
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


async def save_uploaded_file(uploaded_file, temp_folder):
    """
    保存上传的文件到指定的临时文件夹。

    :param uploaded_file: 上传的文件
    :param temp_folder: 临时文件夹路径
    :return: 文件保存路径
    """
    file_path = os.path.join(temp_folder, uploaded_file.name)
    async with aiofiles.open(file_path, 'wb') as out_file:
        while True:
            content = await uploaded_file.read(1024)
            if not content:
                break
            await out_file.write(content)
    return file_path


def visualize_detection_results(results):
    """
    可视化检测结果。

    :param results: 检测结果列表
    """
    labels = ['合规', '不合规']
    sizes = [results.count('合规'), results.count('不合规')]
    colors = ['#4CAF50', '#FF5252']
    explode = (0, 0.1)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=140)
    ax1.axis('equal')
    st.pyplot(fig1)
