#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
带chunk-id的对话数据类模块
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .dialogue_item import DialogueItem


@dataclass
class ChunkDialogueItem:
    """带chunk-id的对话数据类"""
    chunk_id: int
    dialogue_index: int
    role: str
    dialogue: str
    chunk_text: Optional[str] = None

    def to_dict(self, include_chunk_text: bool = False) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "chunk_id": self.chunk_id,
            "dialogue_index": self.dialogue_index,
            "role": self.role,
            "dialogue": self.dialogue
        }
        if include_chunk_text and self.chunk_text:
            result["chunk_text"] = self.chunk_text
        return result

    def to_dialogue_item(self) -> DialogueItem:
        """转换为普通对话项（向后兼容）"""
        return DialogueItem(role=self.role, dialogue=self.dialogue)

    def __hash__(self) -> int:
        """用于去重的哈希值"""
        return hash((self.role.strip().lower(), self.dialogue.strip().lower()))

    def __eq__(self, other) -> bool:
        """用于去重的等价比较"""
        if isinstance(other, ChunkDialogueItem):
            return self.role == other.role and self.dialogue == other.dialogue
        elif isinstance(other, DialogueItem):
            return self.role == other.role and self.dialogue == other.dialogue
        return False
