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

app = Flask(__name__)
CORS(app)

# 生产环境配置
class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key-change-this')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'your-api-key-here')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-this-password')

# 设置配置
app.config.from_object(Config)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect('new_questions.db')
    c = conn.cursor()
    
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
        管理能力 INTEGER DEFAULT 0,
        战略思维 INTEGER DEFAULT 0,
        团队领导 INTEGER DEFAULT 0,
        执行管控 INTEGER DEFAULT 0,
        跨部门协作 INTEGER DEFAULT 0,
        职业兴趣 INTEGER DEFAULT 0,
        外向性 INTEGER DEFAULT 0,
        宜人性 INTEGER DEFAULT 0,
        开放性 INTEGER DEFAULT 0,
        责任心 INTEGER DEFAULT 0,
        行为模式类型 TEXT,
        行为模式分数 INTEGER DEFAULT 0,
        职业兴趣类型 TEXT,
        职业兴趣分数 INTEGER DEFAULT 0,
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
            app.config['ADMIN_USERNAME'], app.config['ADMIN_PASSWORD']
        ))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

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
        
        conn = sqlite3.connect('new_questions.db')
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
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        c.execute('SELECT id, 题目, 选项, 题目类型, 正确答案 FROM questions ORDER BY id')
        
        all_data = []
        for row in c.fetchall():
            # 处理选项格式 - 优先使用分号，然后是逗号
            if ';' in row[2]:
                options = row[2].split(';')
            elif '，' in row[2]:
                options = row[2].split('，')
            else:
                options = row[2].split(',')
            
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

@app.route('/api/submit', methods=['POST'])
def submit_answers():
    """提交答案并计算得分"""
    try:
        data = request.json
        answers = data.get('answers', [])
        员工工号 = data.get('员工工号', '')
        
        if not answers or not 员工工号:
            return jsonify({"msg": "缺少必要参数"}), 400
        
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        
        # 获取题目信息
        question_info = {}
        c.execute('SELECT id, 题目类型, 正确答案 FROM questions')
        for row in c.fetchall():
            question_info[row[0]] = {
                'type': row[1],
                'correct': row[2]
            }
        
        # 定义维度映射
        dimension_maps = {
            '管理能力': {
                '战略思维': list(range(1, 21)),
                '团队领导': list(range(21, 41)),
                '执行管控': list(range(41, 61)),
                '跨部门协作': list(range(61, 81))
            },
            '性格特质': {
                '外向性': [87, 88, 89],
                '宜人性': [90, 92, 99],
                '开放性': [81, 83, 97],
                '责任心': [82, 84, 85, 86, 91, 95, 98]
            },
            '行为模式': {
                '支配型': [101, 102, 103, 104, 105],
                '影响型': [106, 107, 108, 109, 110],
                '稳健型': [111, 112, 113, 114, 115],
                '谨慎型': [116, 117, 118, 119, 120]
            },
            '职业兴趣': {
                '现实型': list(range(121, 131)),
                '研究型': list(range(131, 141)),
                '艺术型': list(range(141, 151)),
                '社会型': list(range(151, 161)),
                '企业型': list(range(161, 171)),
                '常规型': list(range(171, 181))
            },
            '通用能力': {
                '言语理解': list(range(181, 196)),
                '数量分析': list(range(196, 211)),
                '逻辑推理': list(range(211, 225)),
                '空间认知': list(range(225, 240))
            }
        }
        
        # 计算各维度得分
        scores = {}
        for category, dims in dimension_maps.items():
            cat_scores = {}
            category_total_score = 0
            category_max_score = 0
            
            for dim, ids in dims.items():
                dim_score = 0
                dim_max = 0
                
                for ans in answers:
                    q_id = ans['id']
                    if q_id not in ids:
                        continue
                    
                    q_info = question_info.get(q_id)
                    if not q_info:
                        continue
                    
                    if q_info['type'] == '评分':
                        # 评分题：1-5分
                        try:
                            answer_value = int(ans['answer'])
                            dim_score += max(1, min(5, answer_value))
                            dim_max += 5
                        except (ValueError, TypeError):
                            continue
                    elif q_info['type'] == '单选':
                        # 单选题：正确得1分，错误得0分
                        user_ans = str(ans['answer']).strip().upper()
                        correct_ans = str(q_info['correct']).strip().upper()
                        if user_ans == correct_ans:
                            dim_score += 1
                        dim_max += 1
                
                # 计算百分比
                dim_percent = round((dim_score / dim_max * 100) if dim_max > 0 else 0)
                cat_scores[dim] = dim_percent
                category_total_score += dim_score
                category_max_score += dim_max
            
            # 计算类别总得分率
            category_total_percent = round((category_total_score / category_max_score * 100) if category_max_score > 0 else 0)
            cat_scores['total'] = category_total_percent
            scores[category] = cat_scores
        
        # 确定类型（取最高分）
        def get_max_type(data_dict):
            max_value = max(data_dict.values())
            max_types = [k for k, v in data_dict.items() if v == max_value and k != 'total']
            return '/'.join(max_types) if max_types else '未知'
        
        # 更新数据库
        c.execute('''UPDATE employees SET 
            管理能力 = ?, 战略思维 = ?, 团队领导 = ?, 执行管控 = ?, 跨部门协作 = ?,
            外向性 = ?, 宜人性 = ?, 开放性 = ?, 责任心 = ?,
            行为模式类型 = ?, 行为模式分数 = ?,
            职业兴趣类型 = ?, 职业兴趣分数 = ?,
            通用能力 = ?, 言语理解 = ?, 数量分析 = ?, 逻辑推理 = ?, 空间认知 = ?
            WHERE 工号 = ?''', (
            scores['管理能力']['total'],
            scores['管理能力']['战略思维'],
            scores['管理能力']['团队领导'],
            scores['管理能力']['执行管控'],
            scores['管理能力']['跨部门协作'],
            scores['性格特质']['外向性'],
            scores['性格特质']['宜人性'],
            scores['性格特质']['开放性'],
            scores['性格特质']['责任心'],
            get_max_type(scores['行为模式']),
            scores['行为模式']['total'],
            get_max_type(scores['职业兴趣']),
            scores['职业兴趣']['total'],
            scores['通用能力']['total'],
            scores['通用能力']['言语理解'],
            scores['通用能力']['数量分析'],
            scores['通用能力']['逻辑推理'],
            scores['通用能力']['空间认知'],
            员工工号
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "msg": "提交成功",
            "scores": scores
        })
        
    except Exception as e:
        logger.error(f"提交答案失败: {str(e)}")
        return jsonify({"msg": "提交失败", "error": str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """生成报告"""
    try:
        data = request.json
        员工工号 = data.get('员工工号', '')
        
        if not 员工工号:
            return jsonify({"msg": "缺少员工工号"}), 400
        
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        
        # 获取员工信息
        c.execute('''SELECT * FROM employees WHERE 工号 = ?''', (员工工号,))
        employee = c.fetchone()
        
        if not employee:
            return jsonify({"msg": "员工不存在"}), 404
        
        # 获取字段名
        columns = [description[0] for description in c.description]
        employee_data = dict(zip(columns, employee))
        
        conn.close()
        
        # 调用DeepSeek API生成报告
        def call_deepseek_api(data):
            api_key = app.config['DEEPSEEK_API_KEY']
            api_url = "https://api.deepseek.com/v1/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": data
                    }
                ]
            }
            
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        # 读取报告模板
        try:
            with open('templates/report.template.md', 'r', encoding='utf-8') as file:
                template_content = file.read()
        except FileNotFoundError:
            template_content = """
员工个人特征和能力综合分析报告
一、员工基本信息
姓名：{姓名}
工号：{工号}
公司名称：{公司名称}

二、能力评估结果
管理能力：{管理能力}分
战略思维：{战略思维}分
团队领导：{团队领导}分
执行管控：{执行管控}分
跨部门协作：{跨部门协作}分
外向性：{外向性}分
宜人性：{宜人性}分
开放性：{开放性}分
责任心：{责任心}分
行为模式类型：{行为模式类型}
职业兴趣类型：{职业兴趣类型}
通用能力：{通用能力}分
言语理解：{言语理解}分
数量分析：{数量分析}分
逻辑推理：{逻辑推理}分
空间认知：{空间认知}分

请根据以上数据生成详细的分析报告。
"""
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y年%m月%d日")
        
        # 准备数据
        data_text = f"""
员工信息：
姓名：{employee_data['姓名']}
工号：{employee_data['工号']}
公司名称：{employee_data['公司名称']}
测评时间：{current_time}

能力评估结果：
管理能力：{employee_data['管理能力']}分
战略思维：{employee_data['战略思维']}分
团队领导：{employee_data['团队领导']}分
执行管控：{employee_data['执行管控']}分
跨部门协作：{employee_data['跨部门协作']}分
外向性：{employee_data['外向性']}分
宜人性：{employee_data['宜人性']}分
开放性：{employee_data['开放性']}分
责任心：{employee_data['责任心']}分
行为模式类型：{employee_data['行为模式类型']}
职业兴趣类型：{employee_data['职业兴趣类型']}
通用能力：{employee_data['通用能力']}分
言语理解：{employee_data['言语理解']}分
数量分析：{employee_data['数量分析']}分
逻辑推理：{employee_data['逻辑推理']}分
空间认知：{employee_data['空间认知']}分
"""
        
        # 替换模板中的时间占位符
        template_with_time = template_content.replace("[测评时间]", current_time).replace("[生成时间]", current_time)
        
        input_data = f"现在我需要你来按以下模板，生成报告：{data_text}\n\n模板：{template_with_time}"
        result = call_deepseek_api(input_data)
        
        # 将Markdown清洗为纯文本
        def strip_markdown(md: str) -> str:
            if not isinstance(md, str):
                return ''
            text = md
            text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            text = re.sub(r"\*(.*?)\*", r"\1", text)
            text = re.sub(r"_(.*?)_", r"\1", text)
            text = re.sub(r"(?m)^\s*[-•]\s*", "", text)
            text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)
            text = re.sub(r"(?s)```.*?```", "", text)
            text = re.sub(r"(?m)^---+$", "", text)
            text = re.sub(r"\r", "", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()
        
        if isinstance(result, dict) and result.get('choices'):
            raw = result['choices'][0]['message'].get('content', '')
            clean = strip_markdown(raw)
            return jsonify({"content": clean, "raw": raw})
        else:
            return jsonify({"msg": "调用DeepSeek失败", "error": str(result)}), 500
        
    except Exception as e:
        logger.error(f"生成报告失败: {str(e)}")
        return jsonify({"msg": "生成报告失败", "error": str(e)}), 500

# 管理员登录
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json or {}
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if not username or not password:
            return jsonify({"msg": "缺少账号或密码"}), 400
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        c.execute('SELECT id FROM admins WHERE username=? AND password=?', (username, password))
        row = c.fetchone()
        conn.close()
        if row:
            return jsonify({"msg": "登录成功"})
        return jsonify({"msg": "账号或密码错误"}), 401
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        return jsonify({"msg": "登录失败", "error": str(e)}), 500

# 列出员工
@app.route('/api/admin/employees', methods=['GET'])
def admin_list_employees():
    try:
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        c.execute('SELECT id, 工号, 姓名, 职业兴趣分数, 通用能力, 管理能力, 宜人性, 外向性, 开放性, 责任心, 行为模式分数 FROM employees ORDER BY 创建时间 DESC')
        cols = [d[0] for d in c.description]
        rows = [dict(zip(cols, r)) for r in c.fetchall()]
        conn.close()
        return jsonify(rows)
    except Exception as e:
        logger.error(f"获取员工列表失败: {e}")
        return jsonify({"msg": "获取失败", "error": str(e)}), 500

# 管理员生成报告（复用现有逻辑，但只允许此接口）
@app.route('/api/admin/generate-report', methods=['POST'])
def admin_generate_report():
    try:
        data = request.json or {}
        emp_no = data.get('员工工号', '').strip()
        if not emp_no:
            return jsonify({"msg": "缺少员工工号"}), 400
        # 直接复用原 /api/generate-report 的主体逻辑
        # 复制其内部实现，避免用户端调用
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        c.execute('''SELECT * FROM employees WHERE 工号 = ?''', (emp_no,))
        employee = c.fetchone()
        if not employee:
            return jsonify({"msg": "员工不存在"}), 404
        columns = [d[0] for d in c.description]
        employee_data = dict(zip(columns, employee))
        conn.close()

        def call_deepseek_api(data):
            api_key = app.config['DEEPSEEK_API_KEY']
            api_url = "https://api.deepseek.com/v1/chat/completions"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": data}]}
            response = requests.post(api_url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            return f"Error: {response.status_code} - {response.text}"

        try:
            with open('templates/report.template.md', 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            template_content = "一、员工基本信息\n姓名：{姓名}\n工号：{工号}\n公司名称：{公司名称}\n"

        current_time = datetime.now().strftime("%Y年%m月%d日")
        data_text = f"""
员工信息：
姓名：{employee_data['姓名']}
工号：{employee_data['工号']}
公司名称：{employee_data['公司名称']}
测评时间：{current_time}

能力评估结果：
管理能力：{employee_data['管理能力']}分
战略思维：{employee_data['战略思维']}分
团队领导：{employee_data['团队领导']}分
执行管控：{employee_data['执行管控']}分
跨部门协作：{employee_data['跨部门协作']}分
外向性：{employee_data['外向性']}分
宜人性：{employee_data['宜人性']}分
开放性：{employee_data['开放性']}分
责任心：{employee_data['责任心']}分
行为模式类型：{employee_data['行为模式类型']}
职业兴趣类型：{employee_data['职业兴趣类型']}
通用能力：{employee_data['通用能力']}分
言语理解：{employee_data['言语理解']}分
数量分析：{employee_data['数量分析']}分
逻辑推理：{employee_data['逻辑推理']}分
空间认知：{employee_data['空间认知']}分
"""
        template_with_time = template_content.replace("[测评时间]", current_time).replace("[生成时间]", current_time)
        input_data = f"现在我需要你来按以下模板，生成报告：{data_text}\n\n模板：{template_with_time}"
        result = call_deepseek_api(input_data)

        def strip_markdown(md: str) -> str:
            if not isinstance(md, str):
                return ''
            text = md
            text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
            text = re.sub(r"\*(.*?)\*", r"\1", text)
            text = re.sub(r"_(.*?)_", r"\1", text)
            text = re.sub(r"(?m)^\s*[-•]\s*", "", text)
            text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)
            text = re.sub(r"(?s)```.*?```", "", text)
            text = re.sub(r"(?m)^---+$", "", text)
            text = re.sub(r"\r", "", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()

        if isinstance(result, dict) and result.get('choices'):
            raw = result['choices'][0]['message'].get('content', '')
            clean = strip_markdown(raw)
            return jsonify({"content": clean, "raw": raw})
        return jsonify({"msg": "调用DeepSeek失败", "error": str(result)}), 500
    except Exception as e:
        logger.error(f"管理员生成报告失败: {e}")
        return jsonify({"msg": "生成报告失败", "error": str(e)}), 500

# 导出Excel
@app.route('/api/admin/export', methods=['GET'])
def admin_export():
    try:
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        c.execute('''SELECT 工号, 姓名, 职业兴趣分数, 通用能力, 管理能力, 责任心, 行为模式分数 FROM employees''')
        headers = ['工号','姓名','职业兴趣得分','通用能力得分','管理能力得分','职业性格得分','行为模式得分']
        rows = c.fetchall()
        conn.close()

        # 创建DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # 创建Excel文件到内存
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='员工测评数据', index=False)
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='员工测评数据.xlsx'
        )
    except Exception as e:
        logger.error(f"导出失败: {e}")
        return jsonify({"msg": "导出失败", "error": str(e)}), 500

# 清空数据
@app.route('/api/admin/clear', methods=['POST'])
def admin_clear():
    try:
        conn = sqlite3.connect('new_questions.db')
        c = conn.cursor()
        c.execute('DELETE FROM employees')
        conn.commit()
        conn.close()
        return jsonify({"msg": "已清空"})
    except Exception as e:
        logger.error(f"清空失败: {e}")
        return jsonify({"msg": "清空失败", "error": str(e)}), 500

@app.route('/manage')
def manage():
    return render_template('manage.html')

if __name__ == '__main__':
    init_db()
    # 生产环境使用环境变量配置端口
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 