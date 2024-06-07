import cv2
import concurrent.futures
import shutil
import os
import streamlit as st
from config.config_constants import API_KEY2, SECRET_KEY2
from functions.image_processing import image_processing


def process_frame(frame, frame_path):
    """
    处理单帧图像并调用图像处理函数。

    :param frame: 要处理的图像帧
    :param frame_path: 保存图像帧的路径
    :return: 图像处理结果
    """
    cv2.imwrite(frame_path, frame)
    return image_processing(API_KEY2, SECRET_KEY2, frame_path)


def video_processing(video_path):
    """
    处理视频，将视频分成帧并调用图像处理函数。

    :param video_path: 视频文件路径
    :return: 处理结果列表
    """
    frame_directory = "frames"
    if not os.path.exists(frame_directory):
        os.makedirs(frame_directory)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # 获取视频的帧率
    frame_interval = int(fps / 2)  # 设置帧间隔，处理每秒2帧

    count = 0
    results = []
    frame_paths = []

    # 读取视频帧并保存到指定路径
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % frame_interval == 0:
            frame_path = os.path.join(frame_directory, f"frame{count:03d}.jpg")
            frame_paths.append((frame, frame_path))
        count += 1

    cap.release()  # 释放视频捕获对象

    # 使用多线程并发处理帧
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_frame = {executor.submit(process_frame, frame, path): path for frame, path in frame_paths}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_frame)):
            results.append(future.result())
            st.progress((i + 1) / len(frame_paths))  # 更新进度条

    # 删除保存帧的临时目录
    shutil.rmtree(frame_directory)
    return results


def main():
    st.title("视频处理与百度API")

    video_file = st.file_uploader("上传视频文件", type=["mp4", "avi", "mov", "mkv"])

    if video_file is not None:
        with open("temp_video.mp4", "wb") as f:
            f.write(video_file.read())

        if st.button("处理视频"):
            with st.spinner("视频处理中..."):
                results = video_processing("temp_video.mp4")
                st.success("视频处理完成！")
                st.json(results)

            os.remove("temp_video.mp4")  # 处理完后删除临时视频文件


if __name__ == "__main__":
    main()
