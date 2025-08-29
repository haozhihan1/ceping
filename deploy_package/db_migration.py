#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移工具
用于导出本地数据库结构和数据，生成迁移文件
"""

import sqlite3
import json
import os
import csv
import zipfile
from datetime import datetime
import shutil
import sys

class DatabaseMigrator:
    """数据库迁移工具类"""

    def __init__(self, db_path='new_questions.db', output_dir='migration_files'):
        self.db_path = db_path
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_schema(self):
        """导出数据库结构"""
        print("正在导出数据库结构...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema = {}

        for table in tables:
            table_name = table[0]
            print(f"  导出表结构: {table_name}")

            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # 获取索引信息
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()

            schema[table_name] = {
                'columns': [{
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                } for col in columns],
                'indexes': [{
                    'name': idx[1],
                    'unique': bool(idx[2]),
                    'origin': idx[3]
                } for idx in indexes if not idx[1].startswith('sqlite_')]
            }

        conn.close()

        # 保存结构到文件
        schema_file = os.path.join(self.output_dir, f'schema_{self.timestamp}.json')
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

        print(f"✓ 数据库结构已导出到: {schema_file}")
        return schema_file

    def export_data(self):
        """导出所有表的数据"""
        print("正在导出数据库数据...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        data_files = []

        for table in tables:
            table_name = table[0]
            print(f"  导出表数据: {table_name}")

            # 获取表数据
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # 获取列名
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            if rows:
                # 保存为CSV文件
                csv_file = os.path.join(self.output_dir, f'{table_name}_{self.timestamp}.csv')
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)  # 写入列名
                    writer.writerows(rows)   # 写入数据

                data_files.append(csv_file)
                print(f"    ✓ {table_name}: {len(rows)} 条记录")
            else:
                print(f"    - {table_name}: 无数据")

        conn.close()
        print(f"✓ 数据导出完成，共处理 {len(data_files)} 个数据文件")
        return data_files

    def create_migration_script(self):
        """创建数据库迁移脚本"""
        print("正在创建迁移脚本...")

        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - {self.timestamp}
用于在服务器端恢复数据库结构和数据
"""

import sqlite3
import csv
import os
import json
import sys
from datetime import datetime

class DatabaseRestorer:
    """数据库恢复工具类"""

    def __init__(self, db_path, migration_dir):
        self.db_path = db_path
        self.migration_dir = migration_dir
        self.conn = None

    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        print(f"✓ 连接数据库: {{self.db_path}}")

    def restore_schema(self, schema_file):
        """恢复数据库结构"""
        print("正在恢复数据库结构...")

        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)

        cursor = self.conn.cursor()

        for table_name, table_info in schema.items():
            print(f"  创建表: {{table_name}}")

            # 构建CREATE TABLE语句
            columns_sql = []
            primary_keys = []

            for col in table_info['columns']:
                col_sql = f"{{col['name']}} {{col['type']}}"

                if col['primary_key']:
                    primary_keys.append(col['name'])

                if col['not_null']:
                    col_sql += " NOT NULL"

                if col['default_value'] is not None:
                    col_sql += f" DEFAULT {{col['default_value']}}"

                columns_sql.append(col_sql)

            # 添加主键约束
            if primary_keys:
                columns_sql.append(f"PRIMARY KEY ({', '.join(primary_keys)})")

            create_sql = f"CREATE TABLE IF NOT EXISTS {{table_name}} ({', '.join(columns_sql)})"
            cursor.execute(create_sql)

            # 创建索引
            for idx in table_info['indexes']:
                if idx['unique']:
                    cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS {{idx['name']}} ON {{table_name}}({{idx['origin']}})")
                else:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {{idx['name']}} ON {{table_name}}({{idx['origin']}})")

        self.conn.commit()
        print("✓ 数据库结构恢复完成")

    def restore_data(self, data_files):
        """恢复数据"""
        print("正在恢复数据...")

        cursor = self.conn.cursor()

        for csv_file in data_files:
            table_name = os.path.basename(csv_file).split('_')[0]
            print(f"  恢复表数据: {{table_name}}")

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                columns = next(reader)  # 读取列名

                # 构建INSERT语句
                placeholders = ', '.join(['?'] * len(columns))
                insert_sql = f"INSERT OR REPLACE INTO {{table_name}} ({', '.join(columns)}) VALUES ({{placeholders}})"

                # 批量插入数据
                batch_size = 1000
                batch_data = []

                for row in reader:
                    batch_data.append(row)
                    if len(batch_data) >= batch_size:
                        cursor.executemany(insert_sql, batch_data)
                        batch_data = []

                # 处理剩余数据
                if batch_data:
                    cursor.executemany(insert_sql, batch_data)

                print(f"    ✓ 插入 {{len(batch_data)}} 条记录")

        self.conn.commit()
        print("✓ 数据恢复完成")

    def initialize_admin(self):
        """初始化管理员账户"""
        print("正在初始化管理员账户...")

        cursor = self.conn.cursor()

        # 检查是否已有管理员
        cursor.execute("SELECT COUNT(*) FROM admins")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (
                'haozhihan', 'Haozhihan010922！'
            ))
            print("✓ 默认管理员账户已创建")
        else:
            print("✓ 管理员账户已存在")

        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("✓ 数据库连接已关闭")

def main():
    """主函数"""
    print("=" * 50)
    print(f"数据库迁移脚本 - {self.timestamp}")
    print("=" * 50)

    # 配置路径
    db_path = os.environ.get('DATABASE_PATH', 'new_questions.db')
    migration_dir = os.path.dirname(__file__)

    # 查找最新的迁移文件
    schema_files = [f for f in os.listdir(migration_dir) if f.startswith('schema_') and f.endswith('.json')]
    if not schema_files:
        print("✗ 未找到schema文件")
        return False

    latest_schema = max(schema_files)
    schema_file = os.path.join(migration_dir, latest_schema)

    # 查找对应的数据文件
    timestamp = latest_schema.replace('schema_', '').replace('.json', '')
    data_files = [f for f in os.listdir(migration_dir)
                 if f.endswith(f'_{{timestamp}}.csv') and not f.startswith('schema_')]

    data_file_paths = [os.path.join(migration_dir, f) for f in data_files]

    print(f"找到迁移文件:")
    print(f"  Schema: {{latest_schema}}")
    print(f"  数据文件: {{len(data_files)}} 个")

    try:
        # 执行迁移
        restorer = DatabaseRestorer(db_path, migration_dir)
        restorer.connect()
        restorer.restore_schema(schema_file)
        restorer.restore_data(data_file_paths)
        restorer.initialize_admin()
        restorer.close()

        print("✓ 数据库迁移完成！")
        return True

    except Exception as e:
        print(f"✗ 迁移失败: {{e}}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
'''

        script_file = os.path.join(self.output_dir, f'migrate_{self.timestamp}.py')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        print(f"✓ 迁移脚本已生成: {script_file}")
        return script_file

    def create_archive(self):
        """创建迁移文件归档"""
        print("正在创建迁移文件归档...")

        archive_name = f'database_migration_{self.timestamp}.zip'
        archive_path = os.path.join(self.output_dir, archive_name)

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有迁移文件
            for file in os.listdir(self.output_dir):
                if file.startswith(('schema_', 'migrate_')) or file.endswith(f'_{self.timestamp}.csv'):
                    file_path = os.path.join(self.output_dir, file)
                    zipf.write(file_path, file)
                    print(f"  添加文件: {file}")

        print(f"✓ 迁移归档已创建: {archive_path}")
        return archive_path

    def generate_report(self):
        """生成迁移报告"""
        print("正在生成迁移报告...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 获取数据库统计信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        report = {
            'migration_time': self.timestamp,
            'database_info': {},
            'tables': {}
        }

        total_records = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count

            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            report['tables'][table_name] = {
                'record_count': count,
                'column_count': len(columns),
                'columns': [col[1] for col in columns]
            }

        report['database_info'] = {
            'total_tables': len(tables),
            'total_records': total_records,
            'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }

        conn.close()

        # 保存报告
        report_file = os.path.join(self.output_dir, f'migration_report_{self.timestamp}.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✓ 迁移报告已生成: {report_file}")
        return report_file

def main():
    """主函数"""
    print("=" * 50)
    print("数据库迁移工具")
    print("=" * 50)

    # 检查数据库文件是否存在
    if not os.path.exists('new_questions.db'):
        print("✗ 数据库文件不存在: new_questions.db")
        return False

    try:
        migrator = DatabaseMigrator()

        # 执行迁移步骤
        schema_file = migrator.export_schema()
        data_files = migrator.export_data()
        script_file = migrator.create_migration_script()
        archive_file = migrator.create_archive()
        report_file = migrator.generate_report()

        print("\n" + "=" * 50)
        print("迁移完成！生成的文件:")
        print(f"  📁 迁移目录: {migrator.output_dir}")
        print(f"  📄 Schema文件: {os.path.basename(schema_file)}")
        print(f"  📊 数据文件: {len(data_files)} 个")
        print(f"  🔧 迁移脚本: {os.path.basename(script_file)}")
        print(f"  📦 归档文件: {os.path.basename(archive_file)}")
        print(f"  📋 报告文件: {os.path.basename(report_file)}")
        print("=" * 50)

        print("\n部署说明:")
        print("1. 将归档文件上传到服务器")
        print("2. 在服务器上解压归档文件")
        print("3. 运行迁移脚本: python migrate_*.py")
        print("4. 验证数据库是否正确恢复")

        return True

    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
