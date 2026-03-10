#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
速率限制器模块
"""

import time
from threading import Lock

from .base_config import Config


class RateLimiter:
    """速率限制器，用于控制API调用频率"""

    def __init__(self):
        """初始化速率限制器"""
        self.enabled = Config.RATE_LIMIT_ENABLED
        self.max_requests_per_minute = Config.MAX_REQUESTS_PER_MINUTE
        self.max_requests_per_second = Config.MAX_REQUESTS_PER_SECOND
        
        # 用于记录请求时间的列表
        self.request_times = []
        self.lock = Lock()
        self.last_request_time = 0

    def wait(self):
        """等待直到可以发送下一个请求"""
        if not self.enabled:
            return

        with self.lock:
            current_time = time.time()
            
            # 清理过期的请求时间记录（超过1分钟的）
            self.request_times = [t for t in self.request_times if current_time - t < 60]
            
            # 检查每分钟请求数限制
            if len(self.request_times) >= self.max_requests_per_minute:
                # 计算需要等待的时间
                oldest_time = self.request_times[0]
                wait_time = 60 - (current_time - oldest_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                # 再次清理过期记录
                current_time = time.time()
                self.request_times = [t for t in self.request_times if current_time - t < 60]
            
            # 检查每秒请求数限制
            if current_time - self.last_request_time < 1.0 / self.max_requests_per_second:
                wait_time = (1.0 / self.max_requests_per_second) - (current_time - self.last_request_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                current_time = time.time()
            
            # 记录本次请求时间
            self.request_times.append(current_time)
            self.last_request_time = current_time

    def reset(self):
        """重置速率限制器"""
        with self.lock:
            self.request_times = []
            self.last_request_time = 0
