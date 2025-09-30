#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境配置文件
"""

import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = False
    TESTING = False

    # 数据库配置
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'new_questions.db')

    # Flask配置
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    # 会话配置
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # CORS配置
    CORS_HEADERS = 'Content-Type'

    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')

    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-d7f98fb5f40d4e669906aa439bfa1e74')
    DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

    # 管理员配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False

    # 生产环境数据库路径
    DATABASE_PATH = os.path.join('/app/data', 'new_questions.db')

    # 生产环境日志路径
    LOG_FILE = '/app/logs/app.log'

    # 生产环境上传路径
    UPLOAD_FOLDER = '/app/uploads'

    # 生产环境密钥必须从环境变量获取
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("生产环境必须设置 SECRET_KEY 环境变量")
        return key

    # 生产环境API密钥必须从环境变量获取
    @property
    def DEEPSEEK_API_KEY(self):
        key = os.environ.get('DEEPSEEK_API_KEY')
        if not key:
            raise ValueError("生产环境必须设置 DEEPSEEK_API_KEY 环境变量")
        return key

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = ':memory:'
    WTF_CSRF_ENABLED = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """获取配置"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(config_name, config['default'])
