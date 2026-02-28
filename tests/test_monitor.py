"""监控埋点测试用例"""
import unittest
import logging
import time
from app.utils.monitor import timing_decorator, monitor_memory_usage


class TestMonitor(unittest.TestCase):
    """监控埋点测试类"""
    
    def test_timing_decorator(self):
        """测试耗时统计装饰器"""
        # 记录日志输出
        log_messages = []
        
        def mock_logger_info(msg):
            log_messages.append(msg)
        
        # 保存原始的info方法
        original_info = logging.info
        try:
            # 替换为mock方法
            logging.info = mock_logger_info
            
            # 创建一个测试函数
            @timing_decorator
            def test_function():
                time.sleep(0.1)
                return "test result"
            
            # 执行函数
            result = test_function()
            
            # 验证结果
            self.assertEqual(result, "test result")
            
            # 验证日志输出
            self.assertTrue(any("test_function executed in" in msg for msg in log_messages))
            
        finally:
            # 恢复原始的info方法
            logging.info = original_info
    
    def test_monitor_memory_usage(self):
        """测试内存使用监控"""
        # 调用内存监控函数
        memory_usage = monitor_memory_usage()
        
        # 验证返回值
        if memory_usage:
            self.assertIn('rss', memory_usage)
            self.assertIn('vms', memory_usage)
            self.assertIn('percent', memory_usage)
            self.assertGreater(memory_usage['rss'], 0)
        else:
            # 如果psutil未安装，应该返回None
            self.assertIsNone(memory_usage)
    
    def test_timing_decorator_with_exception(self):
        """测试耗时统计装饰器处理异常"""
        # 记录日志输出
        log_messages = []
        
        def mock_logger_error(msg):
            log_messages.append(msg)
        
        # 保存原始的error方法
        original_error = logging.error
        try:
            # 替换为mock方法
            logging.error = mock_logger_error
            
            # 创建一个会抛出异常的测试函数
            @timing_decorator
            def error_function():
                time.sleep(0.05)
                raise ValueError("Test error")
            
            # 执行函数，应该抛出异常
            with self.assertRaises(ValueError):
                error_function()
            
            # 验证日志输出
            self.assertTrue(any("error_function failed after" in msg for msg in log_messages))
            self.assertTrue(any("Test error" in msg for msg in log_messages))
            
        finally:
            # 恢复原始的error方法
            logging.error = original_error


if __name__ == '__main__':
    unittest.main()
