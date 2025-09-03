import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    API_KEY = os.environ.get('API_KEY') or 'mock-server-admin'

    # MySQL配置 - 使用pymysql驱动
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'mockuser')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'mockpassword')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'mock_server')

    # 使用pymysql驱动，完全无需系统依赖
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10
        }
    }