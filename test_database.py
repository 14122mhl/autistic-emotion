"""数据库连接测试脚本"""
import os
from dotenv import load_dotenv
from app import create_app, db
from app.models.record import EmotionRecord
import uuid
import random
from datetime import datetime, timezone, timedelta

# 加载环境变量
load_dotenv()

# 设置时区为中国上海（UTC+8）
CHINA_TZ = timezone(timedelta(hours=8))

def test_database_connection():
    """测试数据库连接"""
    print("开始测试数据库连接...")
    
    try:
        # 创建应用实例
        app = create_app()
        
        with app.app_context():
            # 测试数据库连接
            db.engine.connect()
            print("数据库连接成功！")
            
            # 测试数据库保存
            test_save_record()
            
            # 测试数据库查询
            test_query_record()
            
            print("所有数据库测试通过！")
            
    except Exception as e:
        print(f"数据库测试失败: {str(e)}")

def test_save_record():
    """测试数据库保存"""
    print("\n测试数据库保存...")
    
    try:
        # 创建测试记录
        request_id = str(uuid.uuid4())
        emotions = ['开心', '悲伤', '愤怒', '惊讶', '中性']
        emotion = random.choice(emotions)
        confidence = round(random.uniform(0.7, 0.99), 2)
        
        # 保存到数据库
        record = EmotionRecord(
            request_id=request_id,
            emotion=emotion,
            confidence=confidence
        )
        db.session.add(record)
        db.session.commit()
        
        print(f"数据库保存成功！请求ID: {request_id}, 情绪: {emotion}, 置信度: {confidence}")
        
    except Exception as e:
        print(f"数据库保存失败: {str(e)}")
        raise

def test_query_record():
    """测试数据库查询"""
    print("\n测试数据库查询...")
    
    try:
        # 查询最新的记录
        record = EmotionRecord.query.order_by(EmotionRecord.id.desc()).first()
        
        if record:
            print(f"数据库查询成功！")
            print(f"ID: {record.id}")
            print(f"请求ID: {record.request_id}")
            print(f"情绪: {record.emotion}")
            print(f"置信度: {record.confidence}")
            print(f"创建时间: {record.created_at}")
        else:
            print("数据库中没有记录")
            
    except Exception as e:
        print(f"数据库查询失败: {str(e)}")
        raise

if __name__ == "__main__":
    test_database_connection()
