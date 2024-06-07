import logging
import os
import tempfile

import streamlit as st

from functions.video_processing import video_processing
from utils import display_video_results


def video_detection_page(API_KEY, SECRET_KEY):
    # 初始化用户session状态
    if 'logged_in_user' not in st.session_state:
        st.session_state.logged_in_user = None

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
