import logging
import os
import tempfile

import streamlit as st
from PIL import Image

from functions.image_processing import image_processing


def batch_image_detection_page(API_KEY, SECRET_KEY):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

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
                    result = image_processing(API_KEY, SECRET_KEY, image_filename)
                    if result.get("conclusion") == "不合规":
                        st.error(f"检测为不良图像: {uploaded_image.name}")
                    else:
                        st.success(f"图像 {uploaded_image.name} 正常")
                    st.write(result)
                except Exception as e:
                    logging.error(f"图像 {uploaded_image.name} 检测失败: {e}")
                    st.error(f"图像 {uploaded_image.name} 检测失败，请稍后再试。")
