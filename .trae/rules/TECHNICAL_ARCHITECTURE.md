---
alwaysApply: false
description: 当需要了解项目的技术架构、核心模块、数据流和关键模块详细说明时使用
---

# 技术架构

## 1. 核心模块

| 模块 | 职责 | 文件位置 |
|------|------|----------|
| 对话提取器 | 核心提取逻辑，API调用，结果处理 | src/extract_dialogue/dialogue_extractor.py |
| 线程安全提取器 | 处理并发任务，确保线程安全 | src/extract_dialogue/thread_safe_extractor.py |
| 配置管理 | 管理多平台配置和环境变量 | src/extract_dialogue/config/ |
| 数据模型 | 定义对话和工作项结构 | src/extract_dialogue/models/ |
| 命令行参数 | 处理用户输入参数 | src/extract_dialogue/Argument.py |

## 2. 数据流

1. **输入**：小说文本文件
2. **处理**：
   - 文本分块 → API调用 → 响应解析 → 去重处理
3. **输出**：JSONL格式的对话数据

## 3. 关键模块详细说明

### 3.1 对话提取器 (DialogueExtractor)

**主要功能**：
- 文本分块：将长文本分割成适合API处理的小块
- API调用：与不同AI平台的API交互
- 响应解析：解析API返回的对话内容
- 去重处理：移除重复的对话
- 结果保存：将提取的对话保存到文件
- 统计分析：生成对话统计信息

**关键方法**：
- `extract_dialogues()`: 单线程提取对话
- `extract_dialogues_concurrent()`: 多线程并发提取对话
- `_chunk_text()`: 智能文本分块算法
- `_call_api_with_retry()`: 带重试机制的API调用
- `get_statistics()`: 获取对话统计信息

### 3.2 线程安全提取器 (ThreadSafeDialogueExtractor)

**主要功能**：
- 提供线程安全的对话处理
- 管理并发任务的执行
- 确保结果的正确性和一致性

### 3.3 配置管理

**主要功能**：
- 管理多平台API配置
- 加载环境变量
- 提供默认配置值

### 3.4 数据模型

**主要模型**：
- `DialogueItem`: 基本对话项，包含角色和对话内容
- `ChunkDialogueItem`: 带chunk信息的对话项
- `WorkItem`: 工作项，用于并发处理