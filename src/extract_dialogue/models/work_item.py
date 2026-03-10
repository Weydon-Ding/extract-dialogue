#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作单元数据类模块
"""

from dataclasses import dataclass


@dataclass
class WorkItem:
    """工作单元数据类"""
    index: int
    chunk_id: int
    chunk: str
    system_prompt: str
