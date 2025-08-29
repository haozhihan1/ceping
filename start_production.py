#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生产环境启动脚本
使用Gunicorn作为WSGI服务器运行Flask应用
"""

import os
import sys
from new_app import app

def check_environment():
    """检查生产环境配置"""
    required_vars = [
        'DEEPSEEK_API_KEY',
        'SECRET_KEY',
        'ADMIN_USERNAME',
        'ADMIN_PASSWORD'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        print("警告：以下环境变量未设置：")
        for var in missing_vars:
            print(f"  - {var}")
        print("请设置这些环境变量或在.env文件中配置")
        return False

    return True

def main():
    """主函数"""
    print("=" * 50)
    print("员工能力测评系统 - 生产环境启动")
    print("=" * 50)

    # 检查环境变量
    if not check_environment():
        print("环境配置检查失败，请检查环境变量设置")
        sys.exit(1)

    # 设置默认端口
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    workers = int(os.environ.get('WORKERS', 4))

    print(f"启动配置：")
    print(f"  主机: {host}")
    print(f"  端口: {port}")
    print(f"  工作进程数: {workers}")
    print(f"  调试模式: {app.config['DEBUG']}")
    print()

    # 启动Gunicorn
    try:
        from gunicorn.app.wsgiapp import WSGIApplication

        # 设置Gunicorn配置
        sys.argv = [
            'gunicorn',
            'new_app:app',
            '-w', str(workers),
            '-b', f'{host}:{port}',
            '--log-level', 'info',
            '--access-logfile', 'access.log',
            '--error-logfile', 'error.log',
            '--capture-output',
            '--enable-stdio-inheritance'
        ]

        WSGIApplication().run()

    except ImportError:
        print("错误：未安装Gunicorn")
        print("请运行: pip install gunicorn")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
