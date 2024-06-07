import re
import hashlib
from data.database import save_user


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


def register_user(username, password):
    """
    注册新用户，将用户名和哈希后的密码保存到数据库。
    :param username: 用户名
    :param password: 密码
    """
    if not validate_username(username):
        raise ValueError("用户名无效，请使用3-20个字母、数字或下划线。")
    if not validate_password(password):
        raise ValueError("密码无效，密码至少为8个字符。")

    hashed_password = hash_password(password)
    save_user(username, hashed_password)


def login_user(username, password, registered_users):
    """
    验证用户登录信息。
    :param username: 用户名
    :param password: 密码
    :param registered_users: 已注册用户的字典
    :return: 如果登录成功，返回True；否则返回False
    """
    hashed_password = hash_password(password)  # 对输入的密码进行哈希
    return username in registered_users and registered_users[username] == hashed_password


def change_password(username, new_password, registered_users):
    """
    更改用户密码。
    :param username: 用户名
    :param new_password: 新密码
    :param registered_users: 已注册用户的字典
    """
    if not validate_password(new_password):
        raise ValueError("新密码无效，密码至少为8个字符。")

    registered_users[username] = hash_password(new_password)
    save_user(username, registered_users[username])


def delete_user(username, registered_users):
    """
    删除用户。
    :param username: 用户名
    :param registered_users: 已注册用户的字典
    """
    if username not in registered_users:
        raise ValueError("用户名不存在。")

    del registered_users[username]
    save_user(registered_users)

def generate_reset_token(email):
    """
    生成重置令牌。

    :param email: 用户邮箱
    :return: 重置令牌
    """
    return hash_password(email + "reset_token")
