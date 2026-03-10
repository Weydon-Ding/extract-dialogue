#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对话数据类模块
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class DialogueItem:
    """对话数据类"""
    role: str
    dialogue: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "dialogue": self.dialogue}

    def __hash__(self) -> int:
        """用于去重的哈希值"""
        return hash((self.role.strip().lower(), self.dialogue.strip().lower()))
