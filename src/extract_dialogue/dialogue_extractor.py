#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主提取器模块：包含 DialogueExtractor 主类
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import tiktoken
from openai import OpenAI
from tqdm import tqdm

from .config import Config, RateLimiter
from .models import ChunkDialogueItem, DialogueItem, WorkItem
from .thread_safe_extractor import ThreadSafeDialogueExtractor

logger = logging.getLogger(__name__)


class DialogueExtractor:
    """对话提取器主类"""

    def __init__(self, schema: Optional[Dict] = None, platform: Optional[str] = None, max_workers: Optional[int] = None,
                 include_chunk_id: Optional[bool] = None, save_chunk_text: Optional[bool] = None):
        """
        初始化对话提取器

        Args:
            schema: 自定义提取模式，如果为None则使用默认模式
            platform: 指定使用的平台，如果为None则使用环境变量中的配置
            max_workers: 最大并发线程数，如果为None则使用配置中的默认值
            include_chunk_id: 是否在输出中包含chunk-id，如果为None则使用配置中的默认值
            save_chunk_text: 是否保存原始chunk文本，如果为None则使用配置中的默认值
        """
        # 设置平台
        if platform:
            Config.set_platform(platform)

        # 验证配置
        config_errors = Config.validate_config()
        if config_errors:
            raise ValueError(f"配置错误: {'; '.join(config_errors)}")

        # 获取当前平台配置
        platform_config = Config.get_current_platform_config()
        self.platform = platform_config['platform']
        self.model_name = platform_config['model_name']

        self.schema = schema or Config.DEFAULT_SCHEMA
        self.client = OpenAI(
            api_key=platform_config['api_key'],
            base_url=platform_config['base_url']
        )
        self.encoder = tiktoken.get_encoding(Config.ENCODING)

        # 线程配置
        self.max_workers = max_workers or Config.MAX_WORKERS

        # Chunk-id 配置
        self.include_chunk_id = include_chunk_id if include_chunk_id is not None else getattr(Config, 'INCLUDE_CHUNK_ID', True)
        self.save_chunk_text = save_chunk_text if save_chunk_text is not None else getattr(Config, 'SAVE_CHUNK_TEXT', False)

        # 速率限制器
        self.rate_limiter = RateLimiter()

        # 用于去重的集合（仅在单线程模式下使用）
        self.seen_dialogues: Set[DialogueItem] = set()

        # 创建缓存目录
        Path(Config.CACHE_DIR).mkdir(exist_ok=True)

        logger.info(f"对话提取器初始化完成 - 平台: {self.platform} ({platform_config['description']})")
        logger.info(f"使用模型: {self.model_name}")
        logger.info(f"最大并发线程数: {self.max_workers}")

    def _generate_system_prompt(self) -> str:
        """生成系统提示"""
        attributes = self.schema['attributes']
        attributes_str = ',\n    '.join([
            f"{attr['name']}: {attr['type']} // {attr['description']}"
            for attr in attributes
        ])

        typescript = Config.get_typescript_template().format(
            task_description=self.schema['task_description'],
            attributes=attributes_str
        )

        example_input = self.schema['example'][0]['text']
        example_output = json.dumps(
            self.schema['example'][0]['script'],
            indent=4,
            ensure_ascii=False
        )

        return Config.get_system_prompt_template().format(
            TypeScript=typescript,
            Input=example_input,
            Output=example_output
        )

    def _read_text_file(self, file_path: str) -> str:
        """读取文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """
        优化的文本分块算法
        减少重复对话，提高分块质量
        """
        chunks = []
        lines = text.split('\n')

        current_chunk = ""
        current_tokens = 0

        # 预处理：清理空行和多余空格
        cleaned_lines = []
        for line in lines:
            cleaned = line.strip()
            if cleaned:  # 只保留非空行
                cleaned_lines.append(cleaned)

        i = 0
        while i < len(cleaned_lines):
            line = cleaned_lines[i]
            line_tokens = len(self.encoder.encode(line))

            # 如果单行超过限制，强制分割
            if line_tokens > Config.MAX_TOKEN_LEN:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                    current_tokens = 0

                # 按句子分割长行
                sentences = self._split_long_line(line)
                for sentence in sentences:
                    chunks.append(sentence)
                i += 1
                continue

            # 如果添加当前行不会超过限制
            if current_tokens + line_tokens + 1 <= Config.MAX_TOKEN_LEN:
                current_chunk += line + "\n"
                current_tokens += line_tokens + 1
                i += 1
            else:
                # 当前块已满，保存并开始新块
                if current_chunk:
                    chunks.append(current_chunk.rstrip())

                # 为保持上下文，添加重叠内容
                overlap_lines = []
                temp_tokens = 0
                j = max(0, i - 5)  # 最多回溯5行

                while j < i and temp_tokens < Config.COVER_CONTENT:
                    line_j = cleaned_lines[j]
                    tokens_j = len(self.encoder.encode(line_j))
                    if temp_tokens + tokens_j <= Config.COVER_CONTENT:
                        overlap_lines.append(line_j)
                        temp_tokens += tokens_j
                    j += 1

                current_chunk = "\n".join(overlap_lines) + "\n"
                current_tokens = temp_tokens

        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.rstrip())

        logger.info(f"文本分块完成：共 {len(chunks)} 个块")
        return chunks

    def _split_long_line(self, long_line: str) -> List[str]:
        """将长行按句子分割"""
        import re

        # 按句号、问号、感叹号分割
        sentences = re.split(r'([。！？])', long_line)

        chunks = []
        current_chunk = ""

        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]

            tokens = len(self.encoder.encode(current_chunk + sentence))
            if tokens <= Config.MAX_TOKEN_LEN:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _call_api_with_retry(self, system_prompt: str, user_prompt: str) -> str:
        """带重试机制的API调用"""
        # 测试模式：返回模拟数据
        if os.environ.get('TEST_MODE') == 'True':
            return '[{"role": "张三", "dialogue": "你好，李四！"}, {"role": "李四", "dialogue": "你好，张三！"}]'

        for attempt in range(Config.MAX_RETRIES):
            try:
                # 使用速率限制器
                self.rate_limiter.wait()

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=Config.TEMPERATURE,
                    stream=False
                )
                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"API调用失败 (尝试 {attempt + 1}/{Config.MAX_RETRIES}): {e}")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))
                else:
                    logger.error("API调用重试次数已用完")
                    raise

    def _parse_and_validate_response(self, response: str) -> List[DialogueItem]:
        """解析并验证API响应"""
        try:
            # 尝试直接解析
            data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败，尝试使用json_repair修复: {e}")
            try:
                # 导入并使用Python版本的json_repair
                from json_repair import repair_json
                repaired_response = repair_json(response)
                logger.info("JSON修复成功")
                logger.debug(f"修复后的JSON: {repaired_response}")
                data = json.loads(repaired_response)
            except Exception as repair_error:
                logger.error(f"JSON修复失败: {repair_error}")
                logger.debug(f"原始响应: {response}")
                return []

        # 处理解析后的数据
        if not isinstance(data, list):
            logger.warning("响应不是列表格式，尝试转换")
            if isinstance(data, dict) and 'script' in data:
                data = data['script']
            else:
                return []

        dialogues = []
        for item in data:
            if isinstance(item, dict) and 'role' in item and 'dialogue' in item:
                dialogue = DialogueItem(
                    role=str(item['role']).strip(),
                    dialogue=str(item['dialogue']).strip()
                )

                # 验证内容不为空
                if dialogue.role and dialogue.dialogue:
                    dialogues.append(dialogue)
                else:
                    logger.warning(f"跳过空对话项: {item}")
            else:
                logger.warning(f"跳过无效对话项: {item}")

        return dialogues

    def _remove_duplicates(self, dialogues: List[DialogueItem]) -> List[DialogueItem]:
        """移除重复对话"""
        unique_dialogues = []
        for dialogue in dialogues:
            if dialogue not in self.seen_dialogues:
                unique_dialogues.append(dialogue)
                self.seen_dialogues.add(dialogue)

        removed_count = len(dialogues) - len(unique_dialogues)
        if removed_count > 0:
            logger.info(f"移除了 {removed_count} 个重复对话")

        return unique_dialogues

    def _save_progress(self, file_path: str, processed_chunks: int, total_chunks: int):
        """保存进度信息"""
        progress_file = os.path.join(Config.CACHE_DIR, Config.PROGRESS_FILE)
        progress_data = {
            'file_path': file_path,
            'processed_chunks': processed_chunks,
            'total_chunks': total_chunks,
            'timestamp': time.time()
        }

        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存进度失败: {e}")

    def _load_progress(self, file_path: str) -> Optional[int]:
        """加载进度信息"""
        progress_file = os.path.join(Config.CACHE_DIR, Config.PROGRESS_FILE)

        try:
            if os.path.exists(progress_file):
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('file_path') == file_path:
                        return data.get('processed_chunks', 0)
        except Exception as e:
            logger.warning(f"加载进度失败: {e}")

        return None

    def extract_dialogues(self, file_path: str, output_file: Optional[str] = None) -> str:
        """
        从文本文件中提取对话

        Args:
            file_path: 输入文本文件路径
            output_file: 输出文件路径，如果为None则自动生成

        Returns:
            输出文件路径
        """
        logger.info(f"开始处理文件: {file_path}")

        # 读取文本文件
        text = self._read_text_file(file_path)

        # 文本分块
        chunks = self._chunk_text(text)

        # 检查是否有进度可以恢复
        processed_chunks = self._load_progress(file_path) or 0
        if processed_chunks > 0:
            logger.info(f"恢复进度：已处理 {processed_chunks}/{len(chunks)} 个块")

        # 生成系统提示
        system_prompt = self._generate_system_prompt()

        # 确定输出文件路径
        if output_file is None:
            file_name = Path(file_path).stem
            output_file = f"{file_name}_dialogues.{Config.OUTPUT_FORMAT}"

        # 处理每个文本块
        total_dialogues = 0

        with tqdm(total=len(chunks), desc="提取对话", initial=processed_chunks) as pbar:
            for i, chunk in enumerate(chunks):
                if i < processed_chunks:
                    continue

                try:
                    # 调用API提取对话
                    response = self._call_api_with_retry(system_prompt, chunk)
                    dialogues = self._parse_and_validate_response(response)

                    # 去重
                    unique_dialogues = self._remove_duplicates(dialogues)

                    # 转换为带chunk-id的格式（如果启用）
                    if self.include_chunk_id:
                        chunk_dialogues = []
                        for dialogue_index, dialogue in enumerate(unique_dialogues):
                            chunk_dialogue = ChunkDialogueItem(
                                chunk_id=i,
                                dialogue_index=dialogue_index,
                                role=dialogue.role,
                                dialogue=dialogue.dialogue,
                                chunk_text=chunk if self.save_chunk_text else None
                            )
                            chunk_dialogues.append(chunk_dialogue)

                        # 保存结果
                        with open(output_file, 'a', encoding=Config.OUTPUT_ENCODING) as f:
                            for chunk_dialogue in chunk_dialogues:
                                json.dump(chunk_dialogue.to_dict(include_chunk_text=self.save_chunk_text), f, ensure_ascii=False)
                                f.write('\n')
                    else:
                        # 使用旧格式
                        with open(output_file, 'a', encoding=Config.OUTPUT_ENCODING) as f:
                            for dialogue in unique_dialogues:
                                json.dump(dialogue.to_dict(), f, ensure_ascii=False)
                                f.write('\n')

                    total_dialogues += len(unique_dialogues)

                    # 保存进度
                    self._save_progress(file_path, i + 1, len(chunks))

                    # 更新进度条
                    pbar.set_postfix({
                        '对话数': total_dialogues,
                        '去重后': len(unique_dialogues)
                    })
                    pbar.update(1)

                except Exception as e:
                    logger.error(f"处理第 {i+1} 个块时发生错误: {e}")
                    continue

        # 清理进度文件
        progress_file = os.path.join(Config.CACHE_DIR, Config.PROGRESS_FILE)
        if os.path.exists(progress_file):
            try:
                os.remove(progress_file)
            except:
                pass

        logger.info(f"处理完成！共提取 {total_dialogues} 条对话，保存到: {output_file}")
        return output_file

    def extract_dialogues_concurrent(self, file_path: str, output_file: Optional[str] = None) -> str:
        """
        使用多线程并发从文本文件中提取对话

        Args:
            file_path: 输入文本文件路径
            output_file: 输出文件路径，如果为None则自动生成

        Returns:
            输出文件路径
        """
        logger.info(f"开始并发处理文件: {file_path}")

        # 读取文本文件
        text = self._read_text_file(file_path)

        # 文本分块
        chunks = self._chunk_text(text)
        logger.info(f"文本分块完成：共 {len(chunks)} 个块，将使用 {self.max_workers} 个线程并发处理")

        # 生成系统提示
        system_prompt = self._generate_system_prompt()

        # 确定输出文件路径
        if output_file is None:
            file_name = Path(file_path).stem
            output_file = f"{file_name}_dialogues_concurrent.{Config.OUTPUT_FORMAT}"

        # 创建线程安全的提取器
        thread_safe_extractor = ThreadSafeDialogueExtractor(self, self.include_chunk_id)

        # 准备工作队列
        work_items = [
            WorkItem(index=i, chunk_id=i, chunk=chunk, system_prompt=system_prompt)
            for i, chunk in enumerate(chunks)
        ]

        # 使用线程池并发处理
        total_dialogues = 0
        failed_chunks = 0

        # 用于按顺序保存结果的缓冲区
        results_buffer: Dict[int, List[Union[DialogueItem, ChunkDialogueItem]]] = {}
        completed_chunks = set()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_item = {
                executor.submit(thread_safe_extractor.process_chunk, item): item
                for item in work_items
            }

            # 使用进度条显示进度
            with tqdm(total=len(work_items), desc="并发提取对话") as pbar:
                for future in as_completed(future_to_item):
                    work_item = future_to_item[future]

                    try:
                        # 获取结果
                        dialogues = future.result()

                        # 将结果存入缓冲区
                        with thread_safe_extractor.lock:
                            results_buffer[work_item.chunk_id] = dialogues
                            completed_chunks.add(work_item.chunk_id)

                        total_dialogues += len(dialogues)

                        # 检查是否可以按顺序写入文件
                        self._write_ordered_results(results_buffer, completed_chunks, output_file)

                        # 更新进度条
                        pbar.set_postfix({
                            '对话数': total_dialogues,
                            '失败块数': failed_chunks,
                            '活跃线程': executor._work_queue.qsize()
                        })
                        pbar.update(1)

                    except Exception as e:
                        failed_chunks += 1
                        logger.error(f"处理第 {work_item.index + 1} 个块时发生错误: {e}")
                        pbar.set_postfix({
                            '对话数': total_dialogues,
                            '失败块数': failed_chunks,
                            '活跃线程': executor._work_queue.qsize()
                        })
                        pbar.update(1)

        # 处理所有剩余的结果
        self._flush_remaining_results(results_buffer, output_file)

        # 输出错误汇总
        if thread_safe_extractor.errors:
            logger.warning(f"处理过程中发生 {len(thread_safe_extractor.errors)} 个错误")
            for error in thread_safe_extractor.errors[:5]:  # 只显示前5个错误
                logger.warning(f"  - {error}")
            if len(thread_safe_extractor.errors) > 5:
                logger.warning(f"  - ... 还有 {len(thread_safe_extractor.errors) - 5} 个错误")

        logger.info(f"并发处理完成！共提取 {total_dialogues} 条对话，失败 {failed_chunks} 个块，保存到: {output_file}")
        return output_file

    def _write_ordered_results(self, results_buffer: Dict[int, List], completed_chunks: Set[int], output_file: str):
        """按顺序写入结果到文件"""
        expected_chunk_id = len(results_buffer) - len(completed_chunks)

        while expected_chunk_id in results_buffer:
            dialogues = results_buffer.pop(expected_chunk_id)

            # 写入文件
            with open(output_file, 'a', encoding=Config.OUTPUT_ENCODING) as f:
                for dialogue in dialogues:
                    if isinstance(dialogue, ChunkDialogueItem):
                        json.dump(dialogue.to_dict(include_chunk_text=self.save_chunk_text), f, ensure_ascii=False)
                    else:
                        json.dump(dialogue.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

            expected_chunk_id += 1

    def _flush_remaining_results(self, results_buffer: Dict[int, List], output_file: str):
        """刷新所有剩余结果到文件"""
        if not results_buffer:
            return

        logger.info(f"刷新剩余 {len(results_buffer)} 个块的结果到文件")

        # 按chunk_id顺序写入
        for chunk_id in sorted(results_buffer.keys()):
            dialogues = results_buffer[chunk_id]

            # 写入文件
            with open(output_file, 'a', encoding=Config.OUTPUT_ENCODING) as f:
                for dialogue in dialogues:
                    if isinstance(dialogue, ChunkDialogueItem):
                        json.dump(dialogue.to_dict(include_chunk_text=self.save_chunk_text), f, ensure_ascii=False)
                    else:
                        json.dump(dialogue.to_dict(), f, ensure_ascii=False)
                    f.write('\n')

    def get_statistics(self, output_file: str) -> Dict[str, Any]:
        """获取输出文件的统计信息"""
        try:
            dialogues = []
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        dialogues.append(data)

            # 统计角色对话数量
            role_counts = {}
            for dialogue in dialogues:
                role = dialogue.get('role', 'Unknown')
                role_counts[role] = role_counts.get(role, 0) + 1

            return {
                'total_dialogues': len(dialogues),
                'unique_roles': len(role_counts),
                'role_distribution': role_counts,
                'average_dialogue_length': sum(len(d.get('dialogue', '')) for d in dialogues) / len(dialogues) if dialogues else 0
            }

        except Exception as e:
            logger.error(f"统计信息生成失败: {e}")
            return {}

    def sort_dialogues(self, output_file: str, sorted_output_file: Optional[str] = None) -> str:
        """按chunk_id排序对话并保存到新文件"""
        if sorted_output_file is None:
            base_name = Path(output_file).stem
            sorted_output_file = f"{base_name}_sorted.{Config.OUTPUT_FORMAT}"

        try:
            # 读取所有对话
            dialogues = []
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        dialogues.append(data)

            # 检查是否有chunk_id
            has_chunk_id = any('chunk_id' in d for d in dialogues)

            if has_chunk_id:
                # 按chunk_id和dialogue_index排序
                dialogues.sort(key=lambda x: (x.get('chunk_id', 0), x.get('dialogue_index', 0)))
            else:
                logger.warning("文件中不包含chunk_id信息，无法排序")
                return output_file

            # 写入排序后的文件
            with open(sorted_output_file, 'w', encoding=Config.OUTPUT_ENCODING) as f:
                for dialogue in dialogues:
                    json.dump(dialogue, f, ensure_ascii=False)
                    f.write('\n')

            logger.info(f"对话排序完成，保存到: {sorted_output_file}")
            return sorted_output_file

        except Exception as e:
            logger.error(f"对话排序失败: {e}")
            return output_file

    def filter_by_chunk(self, output_file: str, chunk_ids: List[int], filtered_output_file: Optional[str] = None) -> str:
        """按chunk_id筛选对话并保存到新文件"""
        if filtered_output_file is None:
            base_name = Path(output_file).stem
            chunk_str = '_'.join(map(str, sorted(chunk_ids)))
            filtered_output_file = f"{base_name}_chunks_{chunk_str}.{Config.OUTPUT_FORMAT}"

        try:
            filtered_dialogues = []
            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        if data.get('chunk_id') in chunk_ids:
                            filtered_dialogues.append(data)

            # 写入筛选后的文件
            with open(filtered_output_file, 'w', encoding=Config.OUTPUT_ENCODING) as f:
                for dialogue in filtered_dialogues:
                    json.dump(dialogue, f, ensure_ascii=False)
                    f.write('\n')

            logger.info(f"按chunk筛选完成，保存到: {filtered_output_file} (筛选了 {len(filtered_dialogues)} 条对话)")
            return filtered_output_file

        except Exception as e:
            logger.error(f"按chunk筛选失败: {e}")
            return output_file

    def get_chunk_statistics(self, output_file: str) -> Dict[str, Any]:
        """获取按chunk分组的统计信息"""
        try:
            chunk_stats = {}
            total_dialogues = 0

            with open(output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line.strip())
                        chunk_id = data.get('chunk_id')

                        if chunk_id is not None:
                            if chunk_id not in chunk_stats:
                                chunk_stats[chunk_id] = {
                                    'dialogue_count': 0,
                                    'roles': {},
                                    'total_length': 0
                                }

                            chunk_stats[chunk_id]['dialogue_count'] += 1
                            role = data.get('role', 'Unknown')
                            chunk_stats[chunk_id]['roles'][role] = chunk_stats[chunk_id]['roles'].get(role, 0) + 1
                            chunk_stats[chunk_id]['total_length'] += len(data.get('dialogue', ''))
                            total_dialogues += 1

            # 计算汇总统计
            summary = {
                'total_chunks': len(chunk_stats),
                'total_dialogues': total_dialogues,
                'average_dialogues_per_chunk': total_dialogues / len(chunk_stats) if chunk_stats else 0,
                'chunk_details': chunk_stats
            }

            return summary

        except Exception as e:
            logger.error(f"Chunk统计信息生成失败: {e}")
            return {}

    def convert_to_legacy_format(self, output_file: str, legacy_output_file: Optional[str] = None) -> str:
        """转换为旧格式（不含chunk_id）用于向后兼容"""
        if legacy_output_file is None:
            base_name = Path(output_file).stem
            legacy_output_file = f"{base_name}_legacy.{Config.OUTPUT_FORMAT}"

        try:
            with open(legacy_output_file, 'w', encoding=Config.OUTPUT_ENCODING) as f_out:
                with open(output_file, 'r', encoding='utf-8') as f_in:
                    for line in f_in:
                        if line.strip():
                            data = json.loads(line.strip())

                            # 创建旧格式数据
                            legacy_data = {
                                'role': data.get('role', ''),
                                'dialogue': data.get('dialogue', '')
                            }

                            json.dump(legacy_data, f_out, ensure_ascii=False)
                            f_out.write('\n')

            logger.info(f"转换为旧格式完成，保存到: {legacy_output_file}")
            return legacy_output_file

        except Exception as e:
            logger.error(f"格式转换失败: {e}")
            return output_file
