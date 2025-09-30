#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查员工数据
"""

import sqlite3

def check_employee_data():
    """检查员工数据"""
    conn = sqlite3.connect('new_questions.db')
    c = conn.cursor()
    
    print("🔍 检查员工数据...")
    
    # 检查所有员工数据
    c.execute('SELECT 工号, 姓名, 管理能力, 性格特质分数, 行为模式分数, 通用能力 FROM employees ORDER BY 创建时间 DESC')
    employees = c.fetchall()
    
    print("员工数据详情:")
    for emp in employees:
        工号, 姓名, 管理能力, 性格特质, 行为模式, 通用能力 = emp
        print(f"  {工号} ({姓名}):")
        print(f"    管理能力: {管理能力}")
        print(f"    性格特质: {性格特质}")
        print(f"    行为模式: {行为模式}")
        print(f"    通用能力: {通用能力}")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_employee_data()

