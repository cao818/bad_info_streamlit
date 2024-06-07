import logging
import os
import tempfile
import streamlit as st
from PIL import Image
from functions.image_processing import image_processing
from utils import visualize_detection_results


def image_detection_page(API_KEY, SECRET_KEY):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

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
                result = image_processing(API_KEY, SECRET_KEY, image_filename)
                visualize_detection_results([result.get("conclusion")])
                if result.get("conclusion") == "不合规":
                    st.error("检测为不良图像!")
                else:
                    st.success("图像正常")
                st.write(result)
            except Exception as e:
                logging.error(f"图像检测失败: {e}")
                st.error("图像检测失败，请稍后再试。")
