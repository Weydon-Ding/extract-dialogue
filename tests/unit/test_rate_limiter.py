#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试速率限制器
"""

import time
from src.extract_dialogue.config import RateLimiter


def test_rate_limiter():
    """测试速率限制器"""
    print("测试速率限制器...")

    # 创建速率限制器实例
    rate_limiter = RateLimiter()

    # 测试10次API调用
    start_time = time.time()
    for i in range(10):
        print(f"执行第 {i+1} 次API调用")
        rate_limiter.wait()
        # 模拟API调用
        time.sleep(0.1)
    end_time = time.time()

    print(f"\n完成10次API调用，耗时: {end_time - start_time:.2f}秒")
    print("预期耗时应大于等于10秒（因为每秒最多1次调用）")


if __name__ == "__main__":
    test_rate_limiter()
