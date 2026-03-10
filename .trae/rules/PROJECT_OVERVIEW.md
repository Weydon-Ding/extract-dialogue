---
alwaysApply: false
description: 当需要了解项目的基本概述、价值、应用场景、技术栈和快速开始指南时使用
---

# 项目概述

## 1. 项目简介

Extract Dialogue 是一个用于从小说文本中自动提取对话内容的工具，利用多平台AI模型（如DeepSeek、OpenAI、SiliconFlow、Kimi等）来识别和提取对话。该项目为Character AI提供了从小说中建立数据集的功能。

## 2. 项目价值

- 为Character AI提供了从小说中建立数据集的功能
- 简化了对话提取的流程，提高了效率
- 支持多平台AI模型，增加了灵活性
- 提供了详细的统计分析功能，便于数据质量评估
- 并发处理能力大幅提升了处理速度

## 3. 应用场景

- 从小说中提取对话数据集，用于Character AI训练
- 构建对话语料库
- 小说分析和研究
- 对话内容自动提取和整理

## 4. 技术栈

- **编程语言**：Python 3.7+
- **核心库**：openai, python-dotenv, tiktoken, tqdm
- **API集成**：OpenAI兼容接口
- **并发处理**：ThreadPoolExecutor
- **文件格式**：JSONL

## 5. 快速开始

1. **克隆仓库**：`git clone https://github.com/Weydon-Ding/extract-dialogue.git`
2. **安装依赖**：`pip install -r requirements.txt`
3. **配置环境**：`cp env.example .env` 并编辑API密钥
4. **运行提取**：`python dialogue_extractor.py data/test.txt --stats`

## 6. 注意事项

- 确保配置了正确的API密钥
- 处理大文件时，建议使用`--concurrent`选项提高速度
- 对于长文本，推荐使用Kimi平台（擅长长文本处理）
- 提取结果可能需要人工审核，以确保质量