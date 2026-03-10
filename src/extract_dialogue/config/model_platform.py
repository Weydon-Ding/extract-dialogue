#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型平台配置模块
"""


class ModelPlatform:
    """模型平台配置类"""

    # 支持的模型平台
    PLATFORMS = {
        'deepseek': {
            'api_key_env': 'DEEPSEEK_API',
            'base_url_env': 'DEEPSEEK_BASE_URL',
            'default_base_url': 'https://api.deepseek.com',
            'default_model': 'deepseek-chat',
            'description': 'DeepSeek AI平台'
        },
        'openai': {
            'api_key_env': 'OPENAI_API_KEY',
            'base_url_env': 'OPENAI_BASE_URL',
            'default_base_url': 'https://api.openai.com/v1',
            'default_model': 'gpt-3.5-turbo',
            'description': 'OpenAI官方平台'
        },
        'siliconflow': {
            'api_key_env': 'SILICONFLOW_API_KEY',
            'base_url_env': 'SILICONFLOW_BASE_URL',
            'default_base_url': 'https://api.siliconflow.cn/v1',
            'default_model': 'Qwen/Qwen3-30B-A3B-Instruct-2507',
            'description': 'SiliconFlow AI平台'
        },
        'moonshot': {
            'api_key_env': 'MOONSHOT_API_KEY',
            'base_url_env': 'MOONSHOT_BASE_URL',
            'default_base_url': 'https://api.moonshot.cn/v1',
            'default_model': 'kimi-k2-0905-preview',
            'description': '月之暗面Kimi平台'
        },
        'custom': {
            'api_key_env': 'CUSTOM_API_KEY',
            'base_url_env': 'CUSTOM_BASE_URL',
            'default_base_url': 'https://your-custom-endpoint.com/v1',
            'default_model': 'custom-model',
            'description': '自定义API端点'
        }
    }

    @classmethod
    def get_platform_config(cls, platform: str) -> dict:
        """获取指定平台的配置"""
        if platform not in cls.PLATFORMS:
            raise ValueError(f"不支持的平台: {platform}。支持的平台: {list(cls.PLATFORMS.keys())}")

        return cls.PLATFORMS[platform]

    @classmethod
    def list_platforms(cls) -> dict:
        """列出所有支持的平台"""
        return {name: config['description'] for name, config in cls.PLATFORMS.items()}
