---
alwaysApply: false
globs: src/extract_dialogue/config/rate_limiter.py
---
# 速率限制 (Rate Limiting) 规则

## 背景
由于 LLM API 提供商通常会对 API 调用频率进行限制，为了避免因过快的 API 调用而被限制或禁用，项目实现了速率限制机制。

## 实现方案

### 1. 速率限制器类
项目使用 `RateLimiter` 类来控制 API 调用频率，实现了以下功能：
- 每分钟最大请求数限制
- 每秒最大请求数限制
- 线程安全的实现，适用于多线程并发场景

### 2. 配置选项
在 `Config` 类中添加了速率限制相关的配置：

| 配置项 | 默认值 | 描述 |
|-------|-------|------|
| `RATE_LIMIT_ENABLED` | `True` | 是否启用速率限制 |
| `MAX_REQUESTS_PER_MINUTE` | `60` | 每分钟最大请求数 |
| `MAX_REQUESTS_PER_SECOND` | `1` | 每秒最大请求数 |

### 3. 集成方式
- 在 `DialogueExtractor` 初始化时创建 `RateLimiter` 实例
- 在 `_call_api_with_retry` 方法中，每次 API 调用前使用 `rate_limiter.wait()` 来控制调用频率
- 线程安全提取器 `ThreadSafeDialogueExtractor` 也会自动应用速率限制

## 使用方法

### 1. 默认配置
速率限制已默认启用，配置为：
- 每分钟 60 次请求
- 每秒 1 次请求

### 2. 调整配置
可以在 `src/extract_dialogue/config/base_config.py` 文件中修改速率限制参数：

```python
# 速率限制配置
RATE_LIMIT_ENABLED = True  # 是否启用速率限制
MAX_REQUESTS_PER_MINUTE = 60  # 每分钟最大请求数
MAX_REQUESTS_PER_SECOND = 1  # 每秒最大请求数
```

### 3. 禁用速率限制
将 `RATE_LIMIT_ENABLED` 设置为 `False` 即可禁用速率限制：

```python
RATE_LIMIT_ENABLED = False  # 禁用速率限制
```

## 最佳实践

### 1. 根据 API 提供商的限制调整参数
不同的 LLM API 提供商可能有不同的速率限制要求，建议根据实际使用的 API 提供商的限制调整配置参数。

### 2. 多线程场景下的注意事项
- 速率限制器已经实现了线程安全，适用于多线程并发场景
- 但仍建议根据 API 提供商的限制合理设置 `MAX_WORKERS`，避免线程数过多导致的速率限制问题

### 3. 监控和调整
- 观察 API 调用的成功率和响应时间
- 根据实际情况调整速率限制参数，找到最佳平衡点

### 4. 错误处理
- 即使启用了速率限制，仍可能遇到 API 提供商的限制
- 项目已实现了重试机制，可以在 `Config` 中调整 `MAX_RETRIES` 和 `RETRY_DELAY` 参数

## 测试
可以使用以下命令测试速率限制器的功能：

```bash
python tests/unit/test_rate_limiter.py
```

## 总结
速率限制是确保项目稳定运行的重要机制，通过合理配置和使用，可以有效避免因 API 调用频率过高而被限制或禁用，同时保持系统的性能和响应速度。