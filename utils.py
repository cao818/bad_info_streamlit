import logging
import os

import aiofiles
import streamlit as st
from matplotlib import pyplot as plt


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
