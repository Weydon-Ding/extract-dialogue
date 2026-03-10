---
alwaysApply: false
description: 当需要了解项目的输出格式、文件命名规则和统计信息示例时使用
---

# 输出格式

## 1. 标准格式 (包含chunk-id)

```json
{"chunk_id": 0, "dialogue_index": 0, "role": "克莱恩", "dialogue": "在帮警察们调查那起连环杀人案，虽然不一定能有收获，但赏金足够诱人，而且，和警察部门建立良好的关系对我们私家侦探来说非常重要。"}
{"chunk_id": 0, "dialogue_index": 1, "role": "塔利姆", "dialogue": "这果然是大侦探忙碌的事情。"}
{"chunk_id": 1, "dialogue_index": 0, "role": "塔利姆", "dialogue": "莫里亚蒂先生，我能请教一个问题吗？"}
{"chunk_id": 1, "dialogue_index": 1, "role": "克莱恩", "dialogue": "这单免费，还有，叫我夏洛克就行了。"}
```

### 字段说明

- `chunk_id`：文本块的ID，用于追踪对话来源
- `dialogue_index`：对话在当前文本块中的索引
- `role`：说话者角色名称
- `dialogue`：对话内容

## 2. 旧格式 (向后兼容)

```json
{"role": "艾伦", "dialogue": "不，不要提，这真是太倒霉了！我从楼梯上摔了下去，出现了较为严重的骨裂，只能打石膏做固定。"}
{"role": "克莱恩", "dialogue": "真是不够走运啊。"}
```

### 字段说明

- `role`：说话者角色名称
- `dialogue`：对话内容

## 3. 包含chunk文本的格式

当使用 `--save-chunk-text` 选项时，输出格式会包含原始chunk文本：

```json
{"chunk_id": 0, "dialogue_index": 0, "role": "克莱恩", "dialogue": "在帮警察们调查那起连环杀人案，虽然不一定能有收获，但赏金足够诱人，而且，和警察部门建立良好的关系对我们私家侦探来说非常重要。", "chunk_text": "克莱恩坐在办公室里，面前放着一份案件资料。塔利姆走进来说：'莫里亚蒂先生，我能请教一个问题吗？' 克莱恩抬头看了他一眼，说：'这单免费，还有，叫我夏洛克就行了。'"}
```

### 额外字段说明

- `chunk_text`：原始文本块内容，用于参考对话的上下文

## 4. 输出文件命名规则

- 标准输出：`{文件名}_dialogues.jsonl`
- 并发输出：`{文件名}_dialogues_concurrent.jsonl`
- 排序输出：`{文件名}_dialogues_sorted.jsonl`
- 旧格式输出：`{文件名}_dialogues_legacy.jsonl`

## 5. 统计信息示例

```
=== 统计信息 ===
使用平台: deepseek
使用模型: deepseek-chat
处理方式: 多线程并发 (8 个线程)
输出格式: 包含chunk-id
总对话数: 1,247
角色数量: 15
平均对话长度: 45.2 字符
总块数: 42
平均每块对话数: 29.7

角色分布:
  克莱恩: 423 条
  塔利姆: 198 条
  梅丽莎: 156 条
  班森: 134 条
  ...
```