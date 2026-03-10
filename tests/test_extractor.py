#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试对话提取器
"""

import json
import os
import tempfile
import pytest
from src.extract_dialogue.dialogue_extractor import DialogueExtractor
from src.extract_dialogue.models import DialogueItem, ChunkDialogueItem


class TestDialogueExtractor:
    """测试对话提取器类"""

    @pytest.fixture
    def extractor(self):
        """创建对话提取器实例"""
        return DialogueExtractor()

    @pytest.fixture
    def test_text(self):
        """测试文本"""
        return """张三: 你好，李四！
李四: 你好，张三！最近怎么样？
张三: 还不错，工作挺忙的。
李四: 我也是，一直在加班。
"""

    @pytest.fixture
    def test_file(self, test_text):
        """创建测试文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_text)
            temp_file = f.name
        yield temp_file
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def test_init(self, extractor):
        """测试初始化"""
        assert extractor is not None
        assert hasattr(extractor, 'platform')
        assert hasattr(extractor, 'model_name')

    def test_chunk_text(self, extractor, test_text):
        """测试文本分块"""
        chunks = extractor._chunk_text(test_text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_split_long_line(self, extractor):
        """测试长行分割"""
        long_line = "这是一条很长的句子，包含多个分句，需要被分割成多个短句子。这是第二部分，同样很长。"
        chunks = extractor._split_long_line(long_line)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_parse_and_validate_response(self, extractor):
        """测试解析和验证响应"""
        test_response = '[["张三", "你好，李四！"], ["李四", "你好，张三！"]]'
        dialogues = extractor._parse_and_validate_response(test_response)
        assert isinstance(dialogues, list)

    def test_remove_duplicates(self, extractor):
        """测试去重功能"""
        dialogues = [
            DialogueItem(role="张三", dialogue="你好"),
            DialogueItem(role="张三", dialogue="你好"),  # 重复
            DialogueItem(role="李四", dialogue="你好")
        ]
        unique_dialogues = extractor._remove_duplicates(dialogues)
        assert len(unique_dialogues) == 2

    def test_get_statistics(self, extractor, test_file):
        """测试获取统计信息"""
        # 先提取对话
        output_file = extractor.extract_dialogues(test_file)
        try:
            stats = extractor.get_statistics(output_file)
            assert isinstance(stats, dict)
            assert 'total_dialogues' in stats
            assert 'unique_roles' in stats
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_sort_dialogues(self, extractor, test_file):
        """测试排序对话"""
        # 先提取对话
        output_file = extractor.extract_dialogues(test_file)
        try:
            sorted_file = extractor.sort_dialogues(output_file)
            assert os.path.exists(sorted_file)
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)
            if os.path.exists(sorted_file):
                os.remove(sorted_file)

    def test_filter_by_chunk(self, extractor, test_file):
        """测试按chunk筛选对话"""
        # 先提取对话
        output_file = extractor.extract_dialogues(test_file)
        try:
            filtered_file = extractor.filter_by_chunk(output_file, [0])
            assert os.path.exists(filtered_file)
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)
            if os.path.exists(filtered_file):
                os.remove(filtered_file)

    def test_get_chunk_statistics(self, extractor, test_file):
        """测试获取chunk统计信息"""
        # 先提取对话
        output_file = extractor.extract_dialogues(test_file)
        try:
            stats = extractor.get_chunk_statistics(output_file)
            assert isinstance(stats, dict)
            assert 'total_chunks' in stats
            assert 'total_dialogues' in stats
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_convert_to_legacy_format(self, extractor, test_file):
        """测试转换为旧格式"""
        # 先提取对话
        output_file = extractor.extract_dialogues(test_file)
        try:
            legacy_file = extractor.convert_to_legacy_format(output_file)
            assert os.path.exists(legacy_file)
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)
            if os.path.exists(legacy_file):
                os.remove(legacy_file)


if __name__ == "__main__":
    pytest.main([__file__])
