import hashlib
import re


def validate_username(username):
    """
    验证用户名是否符合要求：只包含字母、数字和下划线，长度为3到20个字符。
    :param username: 待验证的用户名
    :return: 如果用户名有效，返回True；否则返回False
    """
    return re.match("^[a-zA-Z0-9_]{3,20}$", username) is not None


def validate_password(password):
    """
    验证密码是否符合要求：至少8个字符。
    :param password: 待验证的密码
    :return: 如果密码有效，返回True；否则返回False
    """
    return len(password) >= 8


def hash_password(password):
    """
    将密码进行哈希处理。
    :param password: 待哈希的密码
    :return: 哈希后的密码
    """
    return hashlib.sha256(password.encode()).hexdigest()
