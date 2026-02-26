"""日志初始化模块"""
import os
from loguru import logger


def init_logger():
    """初始化日志配置"""
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        compression="zip",
        level="INFO"
    )
