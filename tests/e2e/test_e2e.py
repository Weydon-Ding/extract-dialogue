#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端测试
"""

import os
import tempfile
import pytest
from src.extract_dialogue.dialogue_extractor import DialogueExtractor


class TestE2E:
    """端到端测试类"""

    @pytest.fixture
    def extractor(self):
        """创建对话提取器实例"""
        return DialogueExtractor()

    @pytest.fixture
    def test_text(self):
        """测试文本"""
        return """第一章 相遇

张三: 你好，我是张三。
李四: 你好，我是李四。很高兴认识你。
张三: 我也很高兴认识你。你是哪里人？
李四: 我是北京人，你呢？
张三: 我是上海人。

第二章 工作

张三: 你在哪里工作？
李四: 我在一家科技公司工作，你呢？
张三: 我在一家金融公司工作。
李四: 工作忙吗？
张三: 挺忙的，经常加班。
李四: 我也是。
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

    def test_end_to_end_flow(self, extractor, test_file):
        """测试端到端流程"""
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
            assert stats['unique_roles'] >= 2
            
            # 测试排序功能
            sorted_file = extractor.sort_dialogues(output_file)
            assert os.path.exists(sorted_file)
            
            # 测试按chunk筛选
            filtered_file = extractor.filter_by_chunk(output_file, [0])
            assert os.path.exists(filtered_file)
            
            # 测试获取chunk统计信息
            chunk_stats = extractor.get_chunk_statistics(output_file)
            assert isinstance(chunk_stats, dict)
            assert 'total_chunks' in chunk_stats
            assert 'total_dialogues' in chunk_stats
            
            # 测试转换为旧格式
            legacy_file = extractor.convert_to_legacy_format(output_file)
            assert os.path.exists(legacy_file)
            
        finally:
            # 清理输出文件
            files_to_clean = [output_file, sorted_file, filtered_file, legacy_file]
            for file in files_to_clean:
                if os.path.exists(file):
                    os.remove(file)


if __name__ == "__main__":
    pytest.main([__file__])
