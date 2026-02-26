# 基础镜像（轻量化）
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（OpenCV需要）
RUN apt update && apt install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY ../requirements.txt .

# 安装Python依赖（国内镜像加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY .. .

# 暴露端口
EXPOSE 5000

# 启动命令（生产环境用Gunicorn）
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]