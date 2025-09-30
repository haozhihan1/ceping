#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移数据库，添加性格特质详细字段
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = 'new_questions.db'

def migrate_personality_fields():
    """添加性格特质详细字段"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    logger.info("开始添加性格特质详细字段...")
    
    try:
        # 检查字段是否已存在
        c.execute("PRAGMA table_info(employees)")
        columns = [col[1] for col in c.fetchall()]
        
        # 添加新字段
        new_fields = ['外向性', '宜人性', '开放性', '责任心']
        
        for field in new_fields:
            if field not in columns:
                c.execute(f"ALTER TABLE employees ADD COLUMN {field} REAL DEFAULT 0")
                logger.info(f"已添加字段: {field}")
            else:
                logger.info(f"字段已存在: {field}")
        
        conn.commit()
        logger.info("性格特质字段迁移完成!")
        
    except sqlite3.Error as e:
        logger.error(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_personality_fields()

