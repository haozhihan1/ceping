#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
用于导出SQLite数据库结构和数据，为部署到生产环境做准备
"""

import sqlite3
import json
import os
from datetime import datetime

def export_database_structure(db_path='new_questions.db'):
    """导出数据库结构"""
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return None

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 获取所有表名
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    structure = {}
    for table in tables:
        table_name = table[0]
        # 获取表结构
        c.execute(f"PRAGMA table_info({table_name});")
        columns = c.fetchall()

        # 获取表数据
        c.execute(f"SELECT * FROM {table_name};")
        rows = c.fetchall()

        structure[table_name] = {
            'columns': columns,
            'data': rows
        }

    conn.close()
    return structure

def export_to_sql_file(db_path='new_questions.db', output_file='database_migration.sql'):
    """导出数据库为SQL文件"""
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return False

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"-- 数据库迁移文件\n")
        f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- 此文件包含完整的数据库结构和数据\n\n")

        # 获取所有表
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        for table in tables:
            table_name = table[0]

            # 跳过sqlite系统表
            if table_name.startswith('sqlite_'):
                continue

            f.write(f"-- 表: {table_name}\n")

            # 导出表结构
            c.execute(f"PRAGMA table_info({table_name});")
            columns = c.fetchall()

            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            column_defs = []
            for col in columns:
                col_def = f"    {col[1]} {col[2]}"
                if col[3]:  # NOT NULL
                    col_def += " NOT NULL"
                if col[4]:  # DEFAULT
                    col_def += f" DEFAULT {col[4]}"
                if col[5]:  # PRIMARY KEY
                    col_def += " PRIMARY KEY"
                column_defs.append(col_def)

            create_table_sql += ",\n".join(column_defs) + "\n);"
            f.write(create_table_sql + "\n\n")

            # 导出数据
            c.execute(f"SELECT * FROM {table_name};")
            rows = c.fetchall()

            if rows:
                f.write(f"-- 插入 {table_name} 表数据\n")
                for row in rows:
                    # 转义单引号
                    escaped_values = []
                    for value in row:
                        if value is None:
                            escaped_values.append('NULL')
                        elif isinstance(value, str):
                            escaped_values.append(f"'{value.replace(chr(39), chr(39) + chr(39))}'")
                        else:
                            escaped_values.append(str(value))

                    insert_sql = f"INSERT INTO {table_name} VALUES ({', '.join(escaped_values)});"
                    f.write(insert_sql + "\n")
                f.write("\n")

            # 导出索引
            c.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';")
            indexes = c.fetchall()

            for index in indexes:
                if index[1]:  # 有SQL定义
                    f.write(f"-- 索引: {index[0]}\n")
                    f.write(f"{index[1]};\n\n")

    conn.close()
    print(f"数据库已成功导出到 {output_file}")
    return True

def export_to_json_file(db_path='new_questions.db', output_file='database_backup.json'):
    """导出数据库为JSON文件"""
    structure = export_database_structure(db_path)

    if structure:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=2, default=str)
        print(f"数据库已成功导出到 {output_file}")
        return True
    return False

def get_database_stats(db_path='new_questions.db'):
    """获取数据库统计信息"""
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return None

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    stats = {}

    # 获取表信息
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue

        # 统计记录数
        c.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = c.fetchone()[0]
        stats[table_name] = count

    conn.close()
    return stats

def main():
    """主函数"""
    print("=" * 50)
    print("数据库迁移工具")
    print("=" * 50)

    db_file = 'new_questions.db'

    # 检查数据库文件
    if not os.path.exists(db_file):
        print(f"错误：数据库文件 {db_file} 不存在")
        print("请确保数据库文件在当前目录中")
        return

    # 获取数据库统计
    print("数据库统计信息：")
    stats = get_database_stats(db_file)
    if stats:
        for table, count in stats.items():
            print(f"  {table}: {count} 条记录")
    print()

    # 导出SQL文件
    print("正在导出SQL迁移文件...")
    if export_to_sql_file(db_file, 'database_migration.sql'):
        print("✓ SQL迁移文件导出成功")
    else:
        print("✗ SQL迁移文件导出失败")

    # 导出JSON备份
    print("正在导出JSON备份文件...")
    if export_to_json_file(db_file, 'database_backup.json'):
        print("✓ JSON备份文件导出成功")
    else:
        print("✗ JSON备份文件导出失败")

    print("\n迁移文件说明：")
    print("1. database_migration.sql - 完整的SQL迁移文件，包含结构和数据")
    print("2. database_backup.json - JSON格式的备份文件，便于查看和恢复")
    print("\n在生产环境中使用方法：")
    print("1. 上传这两个文件到服务器")
    print("2. 使用 database_migration.sql 文件重建数据库")
    print("3. 或使用 database_backup.json 文件进行数据恢复")

if __name__ == '__main__':
    main()
