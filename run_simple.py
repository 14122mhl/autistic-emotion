"""简化版应用启动文件"""
import os
from flask import Flask

# 创建Flask应用
app = Flask(__name__, static_folder="frontend", template_folder="frontend")

# 配置
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.urandom(24)

# 首页路由
@app.route('/')
def index():
    return "Hello, World! 应用启动成功!"

# 测试API路由
@app.route('/api/test')
def test_api():
    return {"message": "API测试成功"}

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )