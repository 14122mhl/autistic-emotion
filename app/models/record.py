"""情绪记录模型模块"""
from app import db
from datetime import datetime, timezone, timedelta

# 设置时区为中国上海（UTC+8）
CHINA_TZ = timezone(timedelta(hours=8))


class EmotionRecord(db.Model):
    """情绪记录模型"""
    __tablename__ = 'emotion_records'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    emotion = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(CHINA_TZ))
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 模型字典表示
        """
        return {
            'id': self.id,
            'request_id': self.request_id,
            'emotion': self.emotion,
            'confidence': self.confidence,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
