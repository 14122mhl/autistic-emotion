"""人脸检测模块"""
import cv2
import numpy as np
from loguru import logger
import time

# 全局加载人脸检测器
face_cascade = None

def init_face_detector():
    """初始化人脸检测器"""
    global face_cascade
    try:
        start_time = time.time()
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        logger.info(f"人脸检测器初始化完成，耗时: {((time.time() - start_time) * 1000):.2f}ms")
    except Exception as e:
        logger.error(f"人脸检测器初始化失败: {str(e)}")

# 初始化人脸检测器
init_face_detector()

def resize_image(img, target_width=640, target_height=480):
    """压缩图片到指定分辨率
    
    Args:
        img: 原始图像
        target_width: 目标宽度
        target_height: 目标高度
        
    Returns:
        压缩后的图像
    """
    try:
        start_time = time.time()
        resized = cv2.resize(img, (target_width, target_height))
        logger.info(f"图片压缩完成，耗时: {((time.time() - start_time) * 1000):.2f}ms")
        return resized
    except Exception as e:
        logger.error(f"图片压缩失败: {str(e)}")
        return img

def detect_face(image_data):
    """检测人脸
    
    Args:
        image_data: 图像数据
        
    Returns:
        bool: 是否检测到人脸
    """
    start_time = time.time()
    try:
        # 将图像数据转换为numpy数组
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("无法解码图像")
            return False
        
        # 压缩图片
        img = resize_image(img)
        
        # 检查人脸检测器是否初始化
        if face_cascade is None:
            init_face_detector()
            if face_cascade is None:
                logger.error("人脸检测器未初始化")
                return False
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        detect_time = (time.time() - start_time) * 1000
        logger.info(f"人脸检测完成，耗时: {detect_time:.2f}ms, 检测到 {len(faces)} 个人脸")
        
        return len(faces) > 0
    except Exception as e:
        detect_time = (time.time() - start_time) * 1000
        logger.error(f"人脸检测失败: {str(e)}, 耗时: {detect_time:.2f}ms")
        return False
