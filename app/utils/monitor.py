"""监控工具模块"""
import time
import logging
from functools import wraps


def timing_decorator(func):
    """耗时统计装饰器
    
    用于监控函数执行耗时，并将耗时信息记录到日志
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒
            logging.info(f"Function {func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            logging.error(f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
            raise
    return wrapper


def monitor_memory_usage():
    """监控内存使用情况
    
    Returns:
        dict: 内存使用情况
    """
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage = {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }
        logging.info(f"Memory usage: RSS={memory_usage['rss']:.2f}MB, VMS={memory_usage['vms']:.2f}MB, Percent={memory_usage['percent']:.2f}%")
        return memory_usage
    except ImportError:
        logging.warning("psutil not installed, memory monitoring disabled")
        return None
