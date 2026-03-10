#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对话提取器：从小说文本中提取角色对话
入口文件，提供向后兼容的导出
"""

import logging

from .config import Config
from .dialogue_extractor import DialogueExtractor
from .models import ChunkDialogueItem, DialogueItem, WorkItem
from .thread_safe_extractor import ThreadSafeDialogueExtractor

# 设置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导出主要类和类型，保持向后兼容
__all__ = [
    'DialogueItem',
    'ChunkDialogueItem',
    'WorkItem',
    'DialogueExtractor',
    'ThreadSafeDialogueExtractor',
]

logger.debug("对话提取器模块已加载")
