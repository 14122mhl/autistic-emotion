import os
import time
import pymysql
import redis
import random
from datetime import datetime
import cv2
import numpy as np

# 导入项目中的人脸检测模块
from app.utils.face_detect import detect_face as detect_face_func

# 模拟情绪检测函数
def detect_emotion(image_path):
    """检测图片中的情绪
    
    Args:
        image_path: 图片路径
        
    Returns:
        tuple: (情绪标签, 置信度)
    """
    try:
        # 读取图片
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 检测人脸
        has_face = detect_face_func(image_data)
        
        if has_face:
            # 模拟情绪识别结果（与项目中保持一致）
            emotions = ['开心', '悲伤', '愤怒', '惊讶', '中性']
            emotion = random.choice(emotions)
            confidence = round(random.uniform(0.7, 0.99), 4)
        else:
            emotion = '无人脸'
            confidence = 0.0
        
        return emotion, confidence
    except Exception as e:
        print(f"检测失败: {str(e)}")
        return '未知', 0.0

# ===================== 核心配置（直接改这里的参数） =====================
# 1. 图片文件夹路径（你的实际路径，已填好）
IMAGE_FOLDER = r"D:\python_chuangxin\v10face_expression\datasets\train\images"
# 支持的图片格式
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".gif")

# 2. MySQL配置（改成你的实际配置）
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "486908",
    "database": "emotion_db",  # 必须是创建新表的数据库名
    "charset": "utf8mb4"
}

# 3. Redis配置（不需要缓存可注释掉下面内容）
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password":None
}
# Redis缓存过期时间：7天（60*60*24*7）
REDIS_EXPIRE_SECONDS = 604800

# 4. 批量任务标识（方便追踪本次两万张图片的检测）
BATCH_TASK_ID = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
# 每批插入MySQL的数量（避免内存溢出，100条/批）
BATCH_INSERT_SIZE = 100


# ===================== 初始化连接 =====================
def init_mysql():
    """初始化MySQL连接（容错处理）"""
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        print("✅ MySQL连接成功")
        return conn
    except Exception as e:
        print(f"❌ MySQL连接失败：{str(e)}")
        exit(1)


def init_redis():
    """初始化Redis连接（可选）"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()  # 测试连接
        print("✅ Redis连接成功")
        return r
    except Exception as e:
        print(f"⚠️ Redis连接失败（非必需）：{str(e)}")
        return None


# ===================== 单张图片处理逻辑 =====================
def process_single_image(image_path, redis_client):
    """处理单张图片：检测+收集入库数据+缓存"""
    # 初始化返回数据
    result = {
        "success": False,
        "data": None,
        "error": ""
    }

    try:
        # 1. 获取图片基础信息
        image_name = os.path.basename(image_path)  # 文件名
        image_format = os.path.splitext(image_name)[1].lstrip(".")  # 格式（jpg/png）
        image_size = os.path.getsize(image_path)  # 大小（字节）

        # 2. 调用检测模型（记录检测耗时）
        start_detect = time.time()
        # 替换成你的实际检测逻辑，返回 (情绪标签, 置信度)
        emotion_label, confidence = detect_emotion(image_path)
        detect_duration = round(time.time() - start_detect, 4)  # 检测耗时（秒）

        # 3. 格式化置信度（0-1，保留4位）
        confidence = round(float(confidence), 4)

        # 4. 收集入库数据（严格匹配新表字段）
        result["data"] = (
            BATCH_TASK_ID,  # batch_task_id
            image_path,  # image_path
            image_name,  # image_name
            image_format,  # image_format
            image_size,  # image_size
            emotion_label,  # emotion
            confidence,  # confidence
            "v1.0",  # detect_model_version（可改成你的模型版本）
            datetime.now(),  # detect_time
            detect_duration,  # detect_duration
            1,  # is_valid（1=有效）
            ""  # error_msg
        )

        # 5. Redis缓存（可选，连接失败则跳过）
        if redis_client:
            cache_key = f"emotion:batch:{BATCH_TASK_ID}:{image_path}"
            cache_value = {
                "batch_task_id": BATCH_TASK_ID,
                "image_name": image_name,
                "emotion": emotion_label,
                "confidence": confidence,
                "detect_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "detect_duration": detect_duration
            }
            redis_client.hmset(cache_key, cache_value)
            redis_client.expire(cache_key, REDIS_EXPIRE_SECONDS)

        result["success"] = True
        return result

    except Exception as e:
        # 检测失败时的处理
        error_msg = str(e)[:500]  # 限制错误信息长度
        image_name = os.path.basename(image_path)
        # 失败数据也入库（标记为无效）
        result["data"] = (
            BATCH_TASK_ID,
            image_path,
            image_name,
            os.path.splitext(image_name)[1].lstrip("."),
            os.path.getsize(image_path) if os.path.exists(image_path) else 0,
            "",  # emotion（空）
            0.0,  # confidence（0）
            "v1.0",
            datetime.now(),
            0.0,  # detect_duration
            0,  # is_valid（0=无效）
            error_msg
        )
        result["error"] = error_msg
        return result


# ===================== 批量入库核心逻辑 =====================
def batch_detect_and_save():
    # 初始化连接
    mysql_conn = init_mysql()
    redis_client = init_redis()
    cursor = mysql_conn.cursor()

    # 收集批量数据
    batch_data = []
    # 统计变量
    total = 0
    success = 0
    fail = 0
    start_total = time.time()

    # 1. 遍历所有图片
    print(f"📌 开始批量检测，任务ID：{BATCH_TASK_ID}")
    print(f"📂 图片文件夹：{IMAGE_FOLDER}")
    for root, dirs, files in os.walk(IMAGE_FOLDER):
        for file_name in files:
            if file_name.lower().endswith(SUPPORTED_FORMATS):
                total += 1
                image_path = os.path.abspath(os.path.join(root, file_name))  # 绝对路径

                # 2. 处理单张图片
                result = process_single_image(image_path, redis_client)

                # 3. 统计结果
                if result["success"]:
                    success += 1
                    print(f"✅ [{total}] 成功：{image_path} → {result['data'][6]}（置信度：{result['data'][7]}）")
                else:
                    fail += 1
                    print(f"❌ [{total}] 失败：{image_path} → 错误：{result['error']}")

                # 4. 加入批量数据
                if result["data"]:
                    batch_data.append(result["data"])

                # 5. 批量插入MySQL（达到批次大小则插入）
                if len(batch_data) >= BATCH_INSERT_SIZE:
                    insert_sql = """
                        INSERT IGNORE INTO batch_emotion_detection (
                            batch_task_id, image_path, image_name, image_format, image_size,
                            emotion, confidence, detect_model_version, detect_time, detect_duration,
                            is_valid, error_msg
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_sql, batch_data)
                    mysql_conn.commit()
                    print(f"📥 批量插入 {len(batch_data)} 条数据完成")
                    batch_data.clear()

    # 6. 插入剩余数据
    if batch_data:
        insert_sql = """
            INSERT IGNORE INTO batch_emotion_detection (
                batch_task_id, image_path, image_name, image_format, image_size,
                emotion, confidence, detect_model_version, detect_time, detect_duration,
                is_valid, error_msg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_sql, batch_data)
        mysql_conn.commit()
        print(f"📥 插入剩余 {len(batch_data)} 条数据完成")

    # 7. 关闭连接
    cursor.close()
    mysql_conn.close()
    if redis_client:
        redis_client.close()

    # 8. 输出汇总报告
    total_time = round(time.time() - start_total, 2)
    print("\n" + "=" * 50)
    print(f"📊 批量检测完成汇总")
    print(f"总图片数：{total}")
    print(f"成功数：{success} | 失败数：{fail}")
    print(f"总耗时：{total_time} 秒 | 平均每张：{round(total_time / total, 4)} 秒")
    print(f"任务ID：{BATCH_TASK_ID}（可用于查询本次批量数据）")
    print("=" * 50)


# ===================== 执行入口 =====================
if __name__ == "__main__":
    # 检查图片文件夹是否存在
    if not os.path.exists(IMAGE_FOLDER):
        print(f"❌ 图片文件夹不存在：{IMAGE_FOLDER}")
        exit(1)
    # 执行批量检测
    batch_detect_and_save()