"""Flask应用初始化模块"""
import os
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import redis
import logging
from logging.handlers import RotatingFileHandler
from app.utils.logger import init_logger
from flask_cors import CORS

# 设置时区为中国上海（UTC+8）
CHINA_TZ = timezone(timedelta(hours=8))
time.tzset = lambda: None  # 避免Windows系统问题

# 加载环境变量
load_dotenv()
# 初始化日志
init_logger()

# 全局变量
db = SQLAlchemy()
migrate = Migrate()
redis_client = None


def create_app(config_name="dev"):
    """创建Flask应用实例
    
    Args:
        config_name: 配置名称，默认为'dev'
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")

    # 加载配置
    if config_name == "dev":
        app.config.from_object("config.dev")
    else:
        app.config.from_object("config.prod")

    # 确保数据库配置正确
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/autistic_easy?charset=utf8mb4'

    # 配置CORS，允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 配置SQLAlchemy连接池
    app.config['SQLALCHEMY_POOL_SIZE'] = 10
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
    app.config['SQLALCHEMY_POOL_PRE_PING'] = True
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 配置Flask日志
    configure_logging(app)

    # 初始化数据库
    db.init_app(app)
    migrate.init_app(app, db)

    # 初始化Redis
    try:
        global redis_client
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD", None),
            db=0,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            max_connections=50,
            health_check_interval=30
        )
        # 测试连接
        redis_client.ping()
        app.logger.info("Redis初始化成功")
    except Exception as e:
        app.logger.error(f"Redis初始化失败: {e}")
        redis_client = None

    # 延迟导入蓝图，确保db已初始化
    from app.routes.emotion import emotion_bp
    from app.routes.index import index_bp
    app.register_blueprint(emotion_bp, url_prefix="/api/emotion")
    app.register_blueprint(index_bp)
    return app

def configure_logging(app):
    """配置Flask日志系统"""
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建RotatingFileHandler
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # 创建StreamHandler（控制台）
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    # 创建一个不使用颜色的格式化器
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)
    
    # 添加处理器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    
    # 记录应用启动信息
    app.logger.info("Flask应用初始化完成，日志系统配置成功")
