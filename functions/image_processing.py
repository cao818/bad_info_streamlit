import base64
import logging
import streamlit as st
import requests
import urllib


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


def get_file_content_as_base64(file_path, urlencoded=False):
    """读取文件并将其内容编码为Base64。

    Args:
        file_path (str): 文件路径。
        urlencoded (bool): 是否对Base64字符串进行URL编码。

    Returns:
        str: Base64编码的文件内容，可能经过URL编码。
    """
    try:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            if urlencoded:
                content = urllib.parse.quote_plus(content)
        return content
    except Exception as e:
        st.error(f"读取文件 {file_path} 时出错: {e}")
        return None


@st.cache_data
def image_processing(api_key, secret_key, image_path):
    """使用百度API处理图像。

    Args:
        api_key (str): 认证用的API密钥。
        secret_key (str): 认证用的密钥。
        image_path (str): 图像文件的路径。

    Returns:
        dict: API返回的JSON格式结果。
    """
    try:
        access_token = get_access_token(api_key, secret_key)
        if not access_token:
            st.error("无法获取访问令牌。")
            return None

        url = f"https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined?access_token={access_token}"
        image = get_file_content_as_base64(image_path, True)
        if not image:
            return None

        payload = f"image={image}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        st.error(f"API请求错误: {e}")
        return None
    except Exception as e:
        st.error(f"处理图像时出错: {e}")
        return None


def main():
    st.title("使用百度API进行图像处理")

    api_key = st.text_input("API密钥", type="password")
    secret_key = st.text_input("密钥", type="password")
    image_path = st.text_input("图像路径")

    if st.button("处理图像"):
        if not api_key or not secret_key or not image_path:
            st.error("请提供API密钥、密钥和图像路径。")
        else:
            with st.spinner("处理中..."):
                result = image_processing(api_key, secret_key, image_path)
                if result:
                    st.success("图像处理成功！")
                    st.json(result)
                else:
                    st.error("图像处理失败。")


if __name__ == "__main__":
    main()
