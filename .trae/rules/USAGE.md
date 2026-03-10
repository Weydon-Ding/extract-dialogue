---
alwaysApply: false
description: 当需要了解项目的使用方法、命令行选项和示例命令时使用
---

# 使用方法

## 1. 基本用法

```bash
# 使用默认平台提取对话
python dialogue_extractor.py your_novel.txt --stats

# 指定平台提取对话
python dialogue_extractor.py your_novel.txt -p openai --stats

# 并发处理
python dialogue_extractor.py your_novel.txt --concurrent --stats
```

## 2. 高级选项

| 选项 | 描述 |
|------|------|
| --list-platforms | 列出所有支持的平台 |
| --no-chunk-id | 不包含chunk-id（向后兼容） |
| --save-chunk-text | 保存原始chunk文本 |
| --sort-output | 完成后按chunk-id排序 |
| --legacy-format | 生成旧格式文件 |
| -t, --threads | 指定并发线程数 |
| -p, --platform | 指定使用的AI平台 |
| --stats | 生成统计信息 |

## 3. 示例命令

### 3.1 列出支持的平台

```bash
python dialogue_extractor.py --list-platforms
```

### 3.2 使用默认平台提取对话

```bash
python dialogue_extractor.py data/test.txt --stats
```

### 3.3 使用指定平台提取对话

```bash
# 使用OpenAI
python dialogue_extractor.py data/test.txt -p openai --stats

# 使用Kimi
python dialogue_extractor.py data/test.txt -p moonshot --stats

# 使用SiliconFlow
python dialogue_extractor.py data/test.txt -p siliconflow --stats
```

### 3.4 并发处理

```bash
# 使用8个线程并发处理（默认）
python dialogue_extractor.py data/test.txt --concurrent --stats

# 指定线程数
python dialogue_extractor.py data/test.txt -t 16 --concurrent --stats
```

### 3.5 输出选项

```bash
# 不包含chunk-id（向后兼容）
python dialogue_extractor.py data/test.txt --no-chunk-id

# 保存原始chunk文本
python dialogue_extractor.py data/test.txt --save-chunk-text

# 完成后按chunk-id排序
python dialogue_extractor.py data/test.txt --sort-output

# 生成旧格式文件
python dialogue_extractor.py data/test.txt --legacy-format
```