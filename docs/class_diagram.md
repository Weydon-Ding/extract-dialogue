# 类关系图

## 项目类图

```mermaid
classDiagram
    %% 数据模型
    class DialogueItem {
        +str role
        +str dialogue
        +to_dict() dict
    }

    class ChunkDialogueItem {
        +int chunk_id
        +int dialogue_index
        +str role
        +str dialogue
        +Optional[str] chunk_text
        +to_dict(include_chunk_text: bool) dict
        +to_dialogue_item() DialogueItem
    }

    class WorkItem {
        +int index
        +int chunk_id
        +str chunk
        +str system_prompt
    }

    %% 配置模块
    class Config {
        +str CURRENT_PLATFORM
        +int MAX_WORKERS
        +int MAX_TOKEN_LEN
        +str DEFAULT_SCHEMA
        +get_current_platform_config() dict
        +set_platform(platform: str)
        +validate_config() List[str]
        +get_system_prompt_template() str
    }

    class ModelPlatform {
        +dict PLATFORMS
        +get_platform_config(platform: str) dict
        +list_platforms() dict
    }

    %% 提取器
    class DialogueExtractor {
        +str platform
        +str model_name
        +object client
        +object encoder
        +int max_workers
        +Set seen_dialogues

        +extract_dialogues(file_path: str, output_file: Optional[str]) str
        # _generate_system_prompt() str
        # _read_text_file(file_path: str) str
        # _chunk_text(text: str) List[str]
        # _split_long_line(long_line: str) List[str]
        # _call_api_with_retry(system_prompt: str, user_prompt: str) str
        # _parse_and_validate_response(response: str) List[DialogueItem]
        # _remove_duplicates(dialogues: List[DialogueItem]) List[DialogueItem]
        # _save_progress(file_path: str, processed_chunks: int, total_chunks: int)
        # _load_progress(file_path: str) Optional[int]
    }

    class ThreadSafeDialogueExtractor {
        -DialogueExtractor extractor
        -threading.Lock lock
        -Set seen_dialogues
        -int total_dialogues
        -int processed_chunks
        -list errors
        +bool include_chunk_id

        +process_chunk(work_item: WorkItem) List[ChunkDialogueItem]
    }

    %% 关系定义
    DialogueItem <|-- ChunkDialogueItem : 继承
    ChunkDialogueItem ..> DialogueItem : 转换 (to_dialogue_item)

    Config --> ModelPlatform : 依赖
    DialogueExtractor --> Config : 依赖

    ThreadSafeDialogueExtractor *-- DialogueExtractor : 组合 (包装)
```

## 设计模式说明

| 设计模式 | 类 | 说明 |
|---------|---|------|
| 装饰器模式 | `ThreadSafeDialogueExtractor` → `DialogueExtractor` | 包装原始提取器，添加线程安全功能 |
| 单例模式 | `Config` | 类变量保存全局| 工厂模式配置 |
 | `DialogueExtractor._parse_and_validate_response` | 创建 DialogueItem 对象 |

## 类职责

| 类 | 职责 |
|---|------|
| `DialogueItem` | 对话数据的基本结构 |
| `ChunkDialogueItem` | 带分块信息的对话数据 |
| `WorkItem` | 线程池工作单元 |
| `Config` | 统一管理所有配置 |
| `ModelPlatform` | 管理支持的 AI 平台 |
| `DialogueExtractor` | 核心对话提取逻辑 |
| `ThreadSafeDialogueExtractor` | 线程安全的提取器包装 |

**Validation Status**: ✅ Validated successfully
