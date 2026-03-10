#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
线程安全提取器模块：提供线程安全的对话提取功能
"""

import logging
import threading
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .dialogue_extractor import DialogueExtractor

from .models import ChunkDialogueItem, WorkItem

logger = logging.getLogger(__name__)


class ThreadSafeDialogueExtractor:
    """线程安全的对话提取器"""

    def __init__(self, extractor: 'DialogueExtractor', include_chunk_id: bool = True):
        self.extractor = extractor
        self.lock = threading.Lock()
        self.seen_dialogues = set()
        self.total_dialogues = 0
        self.processed_chunks = 0
        self.errors = []
        self.include_chunk_id = include_chunk_id

    def process_chunk(self, work_item: WorkItem) -> List[ChunkDialogueItem]:
        """处理单个文本块"""
        try:
            # 调用API提取对话
            response = self.extractor._call_api_with_retry(
                work_item.system_prompt,
                work_item.chunk
            )
            dialogues = self.extractor._parse_and_validate_response(response)

            # 线程安全的去重和转换
            with self.lock:
                unique_dialogues = []
                for dialogue_index, dialogue in enumerate(dialogues):
                    if dialogue not in self.seen_dialogues:
                        self.seen_dialogues.add(dialogue)

                        if self.include_chunk_id:
                            # 创建带chunk-id的对话项
                            chunk_dialogue = ChunkDialogueItem(
                                chunk_id=work_item.chunk_id,
                                dialogue_index=dialogue_index,
                                role=dialogue.role,
                                dialogue=dialogue.dialogue,
                                chunk_text=work_item.chunk if self.extractor.save_chunk_text else None
                            )
                            unique_dialogues.append(chunk_dialogue)
                        else:
                            # 保持向后兼容
                            unique_dialogues.append(dialogue)

                self.total_dialogues += len(unique_dialogues)
                self.processed_chunks += 1

                return unique_dialogues

        except Exception as e:
            with self.lock:
                self.errors.append(f"处理第 {work_item.index + 1} 个块时发生错误: {e}")
            logger.error(f"处理第 {work_item.index + 1} 个块时发生错误: {e}")
            return []
