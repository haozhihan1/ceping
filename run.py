#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本
用于初始化数据库并启动员工能力测评系统
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        import requests
        print("✓ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def init_database():
    """初始化数据库"""
    if not os.path.exists('new_questions.db'):
        print("正在初始化数据库...")
        try:
            from init_database import init_database
            init_database()
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            return False
    else:
        print("✓ 数据库已存在")
    return True

def start_app():
    """启动应用"""
    print("正在启动员工能力测评系统...")
    try:
        from new_app import app
        print("✓ 系统启动成功！")
        print("✓ 访问地址: http://localhost:5000")
        print("✓ 按 Ctrl+C 停止服务")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"启动失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("员工能力测评系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 初始化数据库
    if not init_database():
        return
    
    # 启动应用
    start_app()

if __name__ == '__main__':
    main() 