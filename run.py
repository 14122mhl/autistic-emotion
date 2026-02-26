"""应用启动文件"""
import os
import sys

# 确保在所有导入前加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 解决Windows asyncio问题
if sys.platform == 'win32':
    os.environ['PYTHONASYNCIODEBUG'] = '1'

from app import create_app

app = create_app(config_name=os.getenv("FLASK_ENV", "dev"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("APP_PORT", "5000")),
        debug=(os.getenv("FLASK_ENV") == "dev")
    )
