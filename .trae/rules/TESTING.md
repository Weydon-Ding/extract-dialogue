---
alwaysApply: false
globs: tests/**/*.py
---
# 测试规范

## 测试文件结构

### 目录结构
项目的测试文件应按照以下目录结构组织：

```
tests/
├── e2e/          # 端到端测试
├── integration/  # 集成测试
├── unit/         # 单元测试
└── __init__.py   # 测试包初始化文件
```

### 命名规范
- 测试文件应使用 `test_*.py` 的命名格式
- 测试函数应使用 `test_*` 的命名格式
- 测试类应使用 `Test*` 的命名格式

## 测试类型

### 1. 单元测试 (unit)
- 测试单个函数或类的功能
- 应放在 `tests/unit/` 目录中
- 示例：`tests/unit/test_rate_limiter.py`

### 2. 集成测试 (integration)
- 测试多个模块之间的交互
- 应放在 `tests/integration/` 目录中
- 示例：`tests/integration/test_integration.py`

### 3. 端到端测试 (e2e)
- 测试整个系统的功能流程
- 应放在 `tests/e2e/` 目录中
- 示例：`tests/e2e/test_e2e.py`

## 测试最佳实践

### 1. 测试文件位置
- **禁止**将测试文件放在项目根目录
- **禁止**将测试文件与源代码放在同一目录
- **必须**将测试文件放在 `tests/` 目录下的相应子目录中

### 2. 测试代码规范
- 使用 pytest 框架编写测试
- 为每个测试函数添加明确的测试目标
- 使用 fixtures 管理测试资源
- 测试应覆盖正常情况和边缘情况
- 测试代码应具有可读性和可维护性

### 3. 测试运行
- 使用 `pytest` 命令运行测试
- 运行特定目录的测试：`pytest tests/unit/ -v`
- 运行特定文件的测试：`pytest tests/unit/test_rate_limiter.py -v`
- 运行所有测试：`pytest tests/ -v`

### 4. 测试覆盖
- 应努力提高测试覆盖率
- 使用 `pytest-cov` 插件查看测试覆盖率
- 命令：`pytest --cov=src tests/`

## 测试文件示例

### 单元测试示例
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
速率限制器单元测试
"""

import time
import pytest
from src.extract_dialogue.config import RateLimiter


def test_rate_limiter_basic():
    """测试速率限制器的基本功能"""
    rate_limiter = RateLimiter()

    start_time = time.time()
    for i in range(3):
        rate_limiter.wait()
        time.sleep(0.1)
    end_time = time.time()

    # 验证至少等待了 3 秒（每秒最多 1 次调用）
    assert end_time - start_time >= 3


def test_rate_limiter_disabled():
    """测试禁用速率限制器"""
    from src.extract_dialogue.config.base_config import Config

    # 临时禁用速率限制
    original_value = Config.RATE_LIMIT_ENABLED
    Config.RATE_LIMIT_ENABLED = False

    try:
        rate_limiter = RateLimiter()

        start_time = time.time()
        for i in range(3):
            rate_limiter.wait()
            time.sleep(0.1)
        end_time = time.time()

        # 验证几乎没有等待时间
        assert end_time - start_time < 1
    finally:
        # 恢复原始设置
        Config.RATE_LIMIT_ENABLED = original_value
```

## 总结

遵循以上测试规范，有助于：
- 保持项目结构清晰
- 提高测试的可维护性
- 确保测试覆盖的全面性
- 便于团队协作和代码审查

所有测试文件都应按照此规范组织和编写。