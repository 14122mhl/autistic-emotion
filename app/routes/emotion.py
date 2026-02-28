"""情绪识别路由模块"""
import uuid
import random
import time
import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.record import EmotionRecord
from app.utils.face_detect import detect_face
from app.utils.monitor import timing_decorator, monitor_memory_usage

# 设置时区为中国上海（UTC+8）
CHINA_TZ = timezone(timedelta(hours=8))

# 尝试导入redis_client，如果失败则设置为None
try:
    from app import redis_client
except Exception as e:
    logger.warning(f'Redis导入失败: {e}')
    redis_client = None

emotion_bp = Blueprint('emotion', __name__)


@emotion_bp.route('/detect', methods=['POST'])
@timing_decorator
def detect_emotion():
    """检测情绪
    
    Returns:
        json: 检测结果
    """
    # 监控内存使用情况
    monitor_memory_usage()
    total_start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        logging.info(f'[{request_id}] 开始处理情绪识别请求')
        
        # 检查文件
        if 'image' not in request.files:
            logging.warning(f'[{request_id}] 未提供图像文件')
            return jsonify({'error': '未提供图像文件'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            logging.warning(f'[{request_id}] 未选择图像文件')
            return jsonify({'error': '未选择图像文件'}), 400
        
        # 读取图像数据
        read_start_time = time.time()
        image_data = image_file.read()
        read_time = (time.time() - read_start_time) * 1000
        logging.info(f'[{request_id}] 读取图像完成，耗时: {read_time:.2f}ms')
        
        # 检测人脸
        face_detect_start_time = time.time()
        has_face = detect_face(image_data)
        face_detect_time = (time.time() - face_detect_start_time) * 1000
        logging.info(f'[{request_id}] 人脸检测完成，耗时: {face_detect_time:.2f}ms, 结果: {has_face}')
        
        if not has_face:
            logging.warning(f'[{request_id}] 未检测到人脸')
            return jsonify({'error': '未检测到人脸'}), 400
        
        # 模拟情绪识别结果（实际项目中应使用真实的模型）
        emotion_start_time = time.time()
        emotions = ['开心', '悲伤', '愤怒', '惊讶', '中性']
        emotion = random.choice(emotions)
        confidence = round(random.uniform(0.7, 0.99), 2)
        emotion_time = (time.time() - emotion_start_time) * 1000
        logging.info(f'[{request_id}] 情绪识别完成，耗时: {emotion_time:.2f}ms, 情绪: {emotion}, 置信度: {confidence}')
        
        # 保存到数据库
        db_start_time = time.time()
        try:
            record = EmotionRecord(
                request_id=request_id,
                emotion=emotion,
                confidence=confidence
            )
            db.session.add(record)
            db.session.commit()
            db_time = (time.time() - db_start_time) * 1000
            logging.info(f'[{request_id}] 数据库保存完成，耗时: {db_time:.2f}ms')
        except Exception as db_error:
            db_time = (time.time() - db_start_time) * 1000
            logging.error(f'[{request_id}] 数据库保存失败: {db_error}, 耗时: {db_time:.2f}ms')
            # 即使数据库失败，也继续返回结果
        
        # 保存到Redis缓存（如果Redis可用）
        if redis_client:
            redis_start_time = time.time()
            try:
                cache_key = f'emotion:{request_id}'
                cache_data = {
                    'emotion': emotion,
                    'confidence': confidence,
                    'detect_time': datetime.now(CHINA_TZ).isoformat()
                }
                redis_client.setex(cache_key, 3600, str(cache_data))
                redis_time = (time.time() - redis_start_time) * 1000
                logging.info(f'[{request_id}] Redis缓存完成，耗时: {redis_time:.2f}ms')
            except Exception as redis_error:
                redis_time = (time.time() - redis_start_time) * 1000
                logging.warning(f'[{request_id}] Redis缓存失败: {redis_error}, 耗时: {redis_time:.2f}ms')
                # 缓存失败不影响主流程，继续执行
        
        total_time = (time.time() - total_start_time) * 1000
        logging.info(f'[{request_id}] 情绪识别请求处理完成，总耗时: {total_time:.2f}ms')
        
        return jsonify({
            'request_id': request_id,
            'emotion': emotion,
            'confidence': confidence,
            'detect_time': datetime.now(CHINA_TZ).isoformat()
        })
    except Exception as e:
        total_time = (time.time() - total_start_time) * 1000
        logging.error(f'[{request_id}] 情绪识别失败: {str(e)}, 总耗时: {total_time:.2f}ms')
        return jsonify({'error': '情绪识别失败'}), 500


@emotion_bp.route('/query/<request_id>', methods=['GET'])
@timing_decorator
def query_result(request_id):
    """查询情绪识别结果
    
    Args:
        request_id: 请求ID
        
    Returns:
        json: 查询结果
    """
    # 监控内存使用情况
    monitor_memory_usage()
    total_start_time = time.time()
    
    try:
        logging.info(f'[{request_id}] 开始处理查询请求')
        
        # 先从Redis缓存查询（如果Redis可用）
        if redis_client:
            redis_start_time = time.time()
            try:
                cache_key = f'emotion:{request_id}'
                cached_data = redis_client.get(cache_key)
                
                if cached_data:
                    # 解析缓存数据
                    import ast
                    try:
                        data = ast.literal_eval(cached_data)
                        redis_time = (time.time() - redis_start_time) * 1000
                        logging.info(f'[{request_id}] Redis查询成功，耗时: {redis_time:.2f}ms')
                        return jsonify({
                            'request_id': request_id,
                            'emotion': data.get('emotion'),
                            'confidence': data.get('confidence'),
                            'detect_time': data.get('detect_time')
                        })
                    except (ValueError, SyntaxError):
                        redis_time = (time.time() - redis_start_time) * 1000
                        logging.warning(f'[{request_id}] 缓存数据解析失败, 耗时: {redis_time:.2f}ms')
            except Exception as redis_error:
                redis_time = (time.time() - redis_start_time) * 1000
                logging.warning(f'[{request_id}] Redis查询失败: {redis_error}, 耗时: {redis_time:.2f}ms')
        
        # 从数据库查询
        db_start_time = time.time()
        try:
            record = EmotionRecord.query.filter_by(request_id=request_id).first()
            if not record:
                db_time = (time.time() - db_start_time) * 1000
                logging.warning(f'[{request_id}] 未找到记录, 耗时: {db_time:.2f}ms')
                return jsonify({'error': '未找到记录'}), 404
            
            db_time = (time.time() - db_start_time) * 1000
            logging.info(f'[{request_id}] 数据库查询成功，耗时: {db_time:.2f}ms')
            
            total_time = (time.time() - total_start_time) * 1000
            logging.info(f'[{request_id}] 查询请求处理完成，总耗时: {total_time:.2f}ms')
            
            return jsonify({
                'request_id': request_id,
                'emotion': record.emotion,
                'confidence': record.confidence,
                'detect_time': record.created_at.isoformat() if record.created_at else None
            })
        except Exception as db_error:
            db_time = (time.time() - db_start_time) * 1000
            logging.error(f'[{request_id}] 数据库查询失败: {db_error}, 耗时: {db_time:.2f}ms')
            return jsonify({'error': '数据库查询失败'}), 500
    except Exception as e:
        total_time = (time.time() - total_start_time) * 1000
        logging.error(f'[{request_id}] 查询结果失败: {str(e)}, 总耗时: {total_time:.2f}ms')
        return jsonify({'error': '查询失败'}), 500
