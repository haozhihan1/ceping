#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境Flask应用启动文件
适配腾讯云CentOS服务器部署
"""

from flask import Flask, request, jsonify, make_response, render_template, send_file
from flask_cors import CORS
import sqlite3
import logging
import json
import requests
from datetime import datetime
import re
import csv
import io
import pandas as pd
import os
import multiprocessing
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 生产环境配置
class ProductionConfig:
    # 基础配置
    DEBUG = False
    TESTING = False
    
    # 密钥配置 - 必须从环境变量获取
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("生产环境必须设置 SECRET_KEY 环境变量")
    
    # API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    if not DEEPSEEK_API_KEY:
        raise ValueError("生产环境必须设置 DEEPSEEK_API_KEY 环境变量")
    
    # 管理员配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # 数据库配置
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/home/www/flask_project/data/new_questions.db')
    
    # 服务器配置
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 8000))
    WORKERS = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))

# 应用配置
app.config.from_object(ProductionConfig)

# 确保必要目录存在
def ensure_directories():
    """确保必要的目录存在"""
    dirs = [
        '/home/www/flask_project/data',
        '/home/www/flask_project/logs',
        '/home/www/flask_project/uploads',
        '/home/www/flask_project/backup'
    ]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

# 配置日志
def setup_logging():
    """配置生产环境日志"""
    ensure_directories()
    
    # 创建日志格式器
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    
    # 文件日志处理器 - 自动轮转
    file_handler = RotatingFileHandler(
        '/home/www/flask_project/logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 配置Flask应用日志
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # 配置其他库的日志
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# 初始化日志
logger = setup_logging()

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(app.config['DATABASE_PATH'])
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def init_db():
    """初始化数据库"""
    logger.info("正在初始化数据库...")
    
    # 确保数据库目录存在
    db_dir = Path(app.config['DATABASE_PATH']).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # 创建问题表
        c.execute('''CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            题目 TEXT NOT NULL,
            选项 TEXT NOT NULL,
            题目类型 TEXT NOT NULL,
            正确答案 TEXT
        )''')
        
        # 创建人员表
        c.execute('''CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            姓名 TEXT NOT NULL,
            工号 TEXT NOT NULL,
            公司名称 TEXT,
            管理能力 REAL DEFAULT 0,
            战略思维 REAL DEFAULT 0,
            团队领导 REAL DEFAULT 0,
            执行管控 REAL DEFAULT 0,
            跨部门协作 REAL DEFAULT 0,
            性格特质分数 REAL DEFAULT 0,
            外向性 REAL DEFAULT 0,
            宜人性 REAL DEFAULT 0,
            开放性 REAL DEFAULT 0,
            责任心 REAL DEFAULT 0,
            性格特质类型 TEXT,
            行为模式类型 TEXT,
            行为模式分数 REAL DEFAULT 0,
            通用能力 INTEGER DEFAULT 0,
            言语理解 INTEGER DEFAULT 0,
            数量分析 INTEGER DEFAULT 0,
            逻辑推理 INTEGER DEFAULT 0,
            空间认知 INTEGER DEFAULT 0,
            创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # 管理员表
        c.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        
        # 初始化默认管理员
        c.execute('SELECT COUNT(*) FROM admins')
        count = c.fetchone()[0]
        if count == 0:
            c.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (
                app.config['ADMIN_USERNAME'], 
                app.config['ADMIN_PASSWORD']
            ))
            logger.info("已创建默认管理员账户")
        
        # 添加数据库索引优化查询性能
        c.execute('CREATE INDEX IF NOT EXISTS idx_employees_gonghao ON employees(工号)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_employees_create_time ON employees(创建时间)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(题目类型)')
        
        conn.commit()
        logger.info("数据库初始化完成")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

# 导入原有的路由处理逻辑，但使用新的数据库连接方法
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT 1')
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        公司名称 = data.get('公司名称', '')
        员工名称 = data.get('员工名称', '')
        员工工号 = data.get('员工工号', '')
        
        if not all([公司名称, 员工名称, 员工工号]):
            return jsonify({"msg": "请填写完整信息"}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # 检查是否已存在该员工
        c.execute('SELECT id FROM employees WHERE 工号 = ?', (员工工号,))
        existing = c.fetchone()
        
        if existing:
            # 更新现有记录
            c.execute('''UPDATE employees SET 姓名 = ?, 公司名称 = ? WHERE 工号 = ?''', 
                     (员工名称, 公司名称, 员工工号))
        else:
            # 创建新记录
            c.execute('''INSERT INTO employees (姓名, 工号, 公司名称) VALUES (?, ?, ?)''', 
                     (员工名称, 员工工号, 公司名称))
        
        conn.commit()
        conn.close()
        
        return jsonify({"msg": "登录成功", "员工工号": 员工工号})
        
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({"msg": "登录失败", "error": str(e)}), 500

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """获取所有题目"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT id, 题目, 选项, 题目类型, 正确答案 FROM questions ORDER BY id')
        
        all_data = []
        for row in c.fetchall():
            question_type = row[3]
            options_text = row[2]
            
            # 根据题目类型处理选项格式
            if question_type in ['情境题', '双向选择题']:
                if ';' in options_text:
                    options = options_text.split(';')
                else:
                    options = [options_text]
            elif question_type == '反向题':
                if '，' in options_text:
                    options = options_text.split('，')
                elif ',' in options_text:
                    options = options_text.split(',')
                else:
                    options = [options_text]
            else:
                if ';' in options_text:
                    options = options_text.split(';')
                elif '，' in options_text:
                    options = options_text.split('，')
                elif ',' in options_text:
                    options = options_text.split(',')
                else:
                    options = [options_text]
            
            all_data.append({
                "id": row[0],
                "content": row[1],
                "options": options,
                "question_type": row[3],
                "correct_answer": row[4]
            })
        
        conn.close()
        return jsonify(all_data)
        
    except Exception as e:
        logger.error(f"获取题目失败: {str(e)}")
        return jsonify({"msg": "获取题目失败", "error": str(e)}), 500

# 在这里添加其他所有的路由处理函数...
# (由于篇幅限制，这里只显示关键部分，实际部署时需要复制所有路由)

# 错误处理器
@app.errorhandler(404)
def not_found(error):
    return jsonify({"msg": "接口不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"服务器内部错误: {error}")
    return jsonify({"msg": "服务器内部错误"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"未处理的异常: {e}")
    return jsonify({"msg": "系统错误", "error": str(e)}), 500

# Gunicorn配置
def create_app():
    """应用工厂函数"""
    ensure_directories()
    init_db()
    logger.info("应用启动完成")
    return app

if __name__ == '__main__':
    # 开发模式启动
    ensure_directories()
    init_db()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=False
    )
