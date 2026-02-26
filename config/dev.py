import os

# Flask配置
DEBUG = True
SECRET_KEY = os.urandom(24)

# MySQL配置
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/autistic_easy?charset=utf8mb4')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # 关闭SQL打印