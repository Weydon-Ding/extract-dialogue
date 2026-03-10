---
alwaysApply: false
description: 当需要了解项目的环境变量配置、依赖项和配置步骤时使用
---

# 配置信息

## 1. 环境变量

项目通过 `.env` 文件管理配置，主要配置项包括：

```bash
# API密钥
DEEPSEEK_API="your-deepseek-api-key"
OPENAI_API_KEY="your-openai-api-key"
MOONSHOT_API_KEY="your-moonshot-api-key"
SILICONFLOW_API_KEY="your-siliconflow-api-key"

# 平台选择
LLM_PLATFORM="deepseek"  # 可选: deepseek, openai, moonshot, siliconflow

# 模型配置
DEEPSEEK_MODEL="deepseek-chat"
OPENAI_MODEL="gpt-3.5-turbo"
MOONSHOT_MODEL="moonshot-v1-8k"
SILICONFLOW_MODEL="mistralai/Mistral-7B-Instruct-v0.2"

# 分块配置
MAX_TOKEN_LEN=1500
COVER_CONTENT=200

# 并发配置
MAX_WORKERS=8

# 输出配置
OUTPUT_FORMAT="jsonl"
OUTPUT_ENCODING="utf-8"
```

## 2. 依赖项

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| openai | - | 与OpenAI兼容的API交互 |
| python-dotenv | - | 加载环境变量 |
| tiktoken | - | 文本token计数 |
| tqdm | - | 进度条显示 |

## 3. 配置步骤

1. **复制配置文件**：`cp env.example .env`
2. **编辑配置文件**：根据需要修改API密钥和平台设置
3. **保存配置**：保存修改后的 `.env` 文件
4. **验证配置**：运行命令时系统会自动验证配置的正确性