import logging

import requests
import streamlit as st


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


def text_processing(api_key, secret_key, text):
    """
    使用百度API处理文本。

    :param api_key: API Key
    :param secret_key: Secret Key
    :param text: 要处理的文本
    :return: 处理结果的JSON格式
    """
    url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "text": text,
        "type": "1",  # 1表示自定义敏感词，2表示自定义敏感句子
        "custom_dict": '{"敏感词1": "替换词1", "敏感词2": "替换词2"}'
    }
    access_token = get_access_token(api_key, secret_key)
    if not access_token:
        return None
    params = {"access_token": access_token}

    try:
        response = requests.post(url, data=data, params=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        st.error(f"Request failed: {e}")
        return None


def main():
    st.title("文本处理与百度API")

    api_key = st.text_input("API密钥", type="password")
    secret_key = st.text_input("密钥", type="password")
    text = st.text_area("输入要处理的文本")

    if st.button("处理文本"):
        if not api_key or not secret_key or not text:
            st.error("请提供API密钥、密钥和文本内容。")
        else:
            with st.spinner("处理中..."):
                result = text_processing(api_key, secret_key, text)
                if result:
                    st.success("文本处理成功！")
                    st.json(result)
                else:
                    st.error("文本处理失败。")


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    main()
