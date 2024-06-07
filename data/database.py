# database.py

import sqlite3
import os


def init_db(db_file):
    """初始化数据库"""
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT)''')
        conn.commit()
        conn.close()


def load_users(db_file):
    """从数据库加载用户"""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = {row[0]: row[1] for row in c.fetchall()}
    conn.close()
    return users


def save_user(username, hashed_password):
    """保存用户到数据库"""
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
