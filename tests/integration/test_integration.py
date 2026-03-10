#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
集成测试
"""

import os
import tempfile
import pytest
from src.extract_dialogue.dialogue_extractor import DialogueExtractor


class TestIntegration:
    """集成测试类"""

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
王五: 你们好，在聊什么呢？
张三: 我们在聊工作的事情。
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

    def test_full_extraction_flow(self, extractor, test_file):
        """测试完整的提取流程"""
        # 提取对话
        output_file = extractor.extract_dialogues(test_file)
        try:
            # 验证输出文件存在
            assert os.path.exists(output_file)
            
            # 验证文件不为空
            assert os.path.getsize(output_file) > 0
            
            # 获取统计信息
            stats = extractor.get_statistics(output_file)
            assert isinstance(stats, dict)
            assert stats['total_dialogues'] > 0
            
            # 测试排序功能
            sorted_file = extractor.sort_dialogues(output_file)
            assert os.path.exists(sorted_file)
            
            # 测试转换为旧格式
            legacy_file = extractor.convert_to_legacy_format(output_file)
            assert os.path.exists(legacy_file)
            
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)
            if os.path.exists(sorted_file):
                os.remove(sorted_file)
            if os.path.exists(legacy_file):
                os.remove(legacy_file)

    def test_concurrent_extraction(self, extractor, test_file):
        """测试并发提取"""
        # 并发提取对话
        output_file = extractor.extract_dialogues_concurrent(test_file)
        try:
            # 验证输出文件存在
            assert os.path.exists(output_file)
            
            # 验证文件不为空
            assert os.path.getsize(output_file) > 0
            
        finally:
            # 清理输出文件
            if os.path.exists(output_file):
                os.remove(output_file)


if __name__ == "__main__":
    pytest.main([__file__])
