import redis
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    # 从环境变量获取Redis配置
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    
    print(f"Redis配置: host={redis_host}, port={redis_port}, password={redis_password}")
    
    # 尝试连接Redis服务器
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=0,
        decode_responses=True,
        socket_timeout=5
    )
    
    # 测试连接
    response = r.ping()
    print(f"Redis连接测试: {'成功' if response else '失败'}")
    
    # 测试基本读写操作
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"Redis读写测试: {'成功' if value else '失败'}")
    print(f"读取的值: {value}")
    
    # 清理测试数据
    r.delete('test_key')
    print("测试完成，已清理测试数据")
    
except Exception as e:
    print(f"Redis连接失败: {str(e)}")
