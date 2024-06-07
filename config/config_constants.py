import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

API_KEY1 = config['DEFAULT']['API_KEY1']
SECRET_KEY1 = config['DEFAULT']['SECRET_KEY1']
API_KEY2 = config['DEFAULT']['API_KEY2']
SECRET_KEY2 = config['DEFAULT']['SECRET_KEY2']
