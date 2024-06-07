# config.py

import configparser
import os


def load_config(config_file_path):
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config
