#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对话提取器：从小说文本中提取角色对话
包入口文件
"""


import logging

from dotenv import find_dotenv, load_dotenv

from .Argument import instance as Argument
from .config import Config
from .dialogue_extractor import DialogueExtractor

# 加载环境变量
load_dotenv(find_dotenv())

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


def main():
    """主函数 - 示例用法"""

    try:
        # 创建提取器实例
        extractor = DialogueExtractor(
            platform=Argument.platform,
            max_workers=Argument.threads,
            include_chunk_id=not Argument.no_chunk_id,
            save_chunk_text=Argument.save_chunk_text
        )

        # 提取对话
        if Argument.concurrent:
            print(f"🚀 使用多线程并发处理 ({extractor.max_workers} 个线程)")
            output_file = extractor.extract_dialogues_concurrent(Argument.input_file, Argument.output)
        else:
            print("📝 使用单线程处理")
            output_file = extractor.extract_dialogues(Argument.input_file, Argument.output)

        # 后处理：排序输出
        if Argument.sort_output and extractor.include_chunk_id:
            print("🔄 按chunk_id排序输出文件...")
            sorted_file = extractor.sort_dialogues(output_file)
            print(f"✅ 排序完成: {sorted_file}")
            output_file = sorted_file

        # 后处理：生成旧格式文件
        if Argument.legacy_format and extractor.include_chunk_id:
            print("📄 生成旧格式文件...")
            legacy_file = extractor.convert_to_legacy_format(output_file)
            print(f"✅ 旧格式文件: {legacy_file}")

        # 显示统计信息
        if Argument.stats:
            stats = extractor.get_statistics(output_file)
            print("\n=== 统计信息 ===")
            print(f"使用平台: {extractor.platform}")
            print(f"使用模型: {extractor.model_name}")
            if Argument.concurrent:
                print(f"处理方式: 多线程并发 ({extractor.max_workers} 个线程)")
            else:
                print("处理方式: 单线程")
            print(f"输出格式: {'包含chunk-id' if extractor.include_chunk_id else '不包含chunk-id'}")
            print(f"总对话数: {stats['total_dialogues']}")
            print(f"角色数量: {stats['unique_roles']}")
            print(f"平均对话长度: {stats['average_dialogue_length']:.1f} 字符")

            # 如果包含chunk-id，显示chunk统计信息
            if extractor.include_chunk_id:
                chunk_stats = extractor.get_chunk_statistics(output_file)
                if chunk_stats:
                    print(f"总块数: {chunk_stats['total_chunks']}")
                    print(f"平均每块对话数: {chunk_stats['average_dialogues_per_chunk']:.1f}")

                    # 显示前5个最活跃的chunk
                    if chunk_stats['chunk_details']:
                        print("\n最活跃的文本块:")
                        sorted_chunks = sorted(chunk_stats['chunk_details'].items(),
                                              key=lambda x: x[1]['dialogue_count'], reverse=True)[:5]
                        for chunk_id, details in sorted_chunks:
                            print(f"  块 {chunk_id}: {details['dialogue_count']} 条对话")

            print("\n角色分布:")
            for role, count in sorted(stats['role_distribution'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {role}: {count} 条")

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
