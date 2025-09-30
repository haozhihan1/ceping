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
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-d7f98fb5f40d4e669906aa439bfa1e74')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

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
    
    # 创建人员表 - 更新为新结构，移除职业兴趣
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
        行为模式类型 TEXT,
        行为模式分数 REAL DEFAULT 0,
        性格特质类型 TEXT,
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
        
        # 反向题列表
        reverse_questions = [4, 5, 15, 18, 22, 24, 27, 29, 32, 35, 37, 42, 45, 48, 50, 53, 55, 58, 62, 65, 67, 70, 73, 76, 82, 84, 88, 91, 94, 96, 104, 109, 110, 111, 114, 116, 119, 183, 199, 212, 215, 228]
        
        all_data = []
        for row in c.fetchall():
            # 处理选项格式 - 优先使用分号，然后是逗号
            if ';' in row[2]:
                options = row[2].split(';')
            elif '，' in row[2]:
                options = row[2].split('，')
            else:
                options = row[2].split(',')
            
            # 对反向题的选项进行反转处理
            if row[0] in reverse_questions and row[3] == '评分':
                # 反转选项顺序：原来是1=不符合...5=符合，现在变为1=符合...5=不符合
                reversed_options = []
                for i, option in enumerate(options):
                    # 提取选项的描述部分
                    if '=' in option:
                        score, desc = option.split('=', 1)
                        # 反转分值对应的描述
                        if score.strip() == '1':
                            reversed_options.append('1=' + options[4].split('=', 1)[1])  # 使用原来5的描述
                        elif score.strip() == '2':
                            reversed_options.append('2=' + options[3].split('=', 1)[1])  # 使用原来4的描述
                        elif score.strip() == '3':
                            reversed_options.append('3=' + options[2].split('=', 1)[1])  # 保持3不变
                        elif score.strip() == '4':
                            reversed_options.append('4=' + options[1].split('=', 1)[1])  # 使用原来2的描述
                        elif score.strip() == '5':
                            reversed_options.append('5=' + options[0].split('=', 1)[1])  # 使用原来1的描述
                options = reversed_options
            
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
    """提交答案并计算得分 - 简化版本"""
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
                'correct': row[2] if row[2] and row[2].strip() else 'A'
            }
        
        logger.info(f"开始处理 {len(answers)} 个答案")
        
        # 完整的维度映射 - 根据question.md要求
        dimension_maps = {
            '管理能力': {
                '战略思维': list(range(1, 21)),
                '团队领导': list(range(21, 41)),
                '执行管控': list(range(41, 61)),
                '跨部门协作': list(range(61, 81))
            },
            '性格特质': {
                '外向性': list(range(81, 86)),
                '宜人性': list(range(86, 91)),
                '开放性': list(range(91, 96)),
                '责任心': list(range(96, 101))
            },
            'DISC行为模式': {
                'D型支配型': list(range(101, 106)),
                'I型影响型': list(range(106, 111)),
                'S型稳健型': list(range(111, 116)),
                'C型谨慎型': list(range(116, 121))
            },
            '通用能力': {
                '言语理解': list(range(181, 196)),
                '数量分析': list(range(196, 211)),
                '逻辑推理': list(range(211, 225)),
                '空间认知': list(range(225, 241))
            }
        }
        
        # 反向题列表
        reverse_questions = [4, 5, 15, 18, 22, 24, 27, 29, 32, 35, 37, 42, 45, 48, 50, 53, 55, 58, 62, 65, 67, 70, 73, 76, 82, 84, 88, 91, 94, 96, 104, 109, 110, 111, 114, 116, 119, 183, 199, 212, 215, 228]
        
        # 计算各维度得分
        scores = {}
        
        def calculate_score(q_id, answer_value, q_info):
            """根据题目类型计算得分"""
            if q_info.get('type') == '评分':
                try:
                    score = int(answer_value)
                    score = max(1, min(5, score))
                    
                    # 反向题处理：选项显示已反转，但计分也需要反转
                    # 用户选择1（高分表现）应该得到5分，选择5（低分表现）应该得到1分
                    if q_id in reverse_questions:
                        score = 6 - score
                    return score
                except:
                    return 3  # 默认分数
                    
            elif q_info.get('type') == '单选':
                try:
                    user_ans = str(answer_value).strip().upper()
                    correct_ans = str(q_info.get('correct', 'A')).strip().upper()
                    return 1 if user_ans == correct_ans else 0
                except:
                    return 0
            return 0
        
        for category, dims in dimension_maps.items():
            cat_scores = {}
            all_scores = []
            
            for dim, ids in dims.items():
                dim_scores = []
                
                for ans in answers:
                    q_id = ans['id']
                    if q_id in ids:
                        q_info = question_info.get(q_id, {})
                        score = calculate_score(q_id, ans['answer'], q_info)
                        dim_scores.append(score)
                        all_scores.append(score)
                
                # 计算维度平均分
                if dim_scores:
                    if category == '通用能力':
                        # 通用能力使用百分制
                        dim_avg = round((sum(dim_scores) / len(dim_scores)) * 100, 2)
                    else:
                        # 其他使用1-5分制
                        dim_avg = round(sum(dim_scores) / len(dim_scores), 2)
                else:
                    dim_avg = 0
                    
                cat_scores[dim] = dim_avg
            
            # 计算类别总分
            if all_scores:
                if category == '通用能力':
                    total_score = round((sum(all_scores) / len(all_scores)) * 100, 2)
                else:
                    total_score = round(sum(all_scores) / len(all_scores), 2)
            else:
                total_score = 0
                
            cat_scores['total'] = total_score
            scores[category] = cat_scores
            logger.info(f"{category}: {total_score}分")
        
        # 确定DISC行为类型（取最高分）
        def get_max_type(data_dict):
            """确定最高分的维度类型"""
            try:
                if not data_dict:
                    return '综合型'
                # 只考虑数值类型的键值对
                numeric_items = {}
                for k, v in data_dict.items():
                    if k != 'total' and isinstance(v, (int, float)):
                        numeric_items[k] = v
                
                if not numeric_items:
                    return '综合型'
                
                max_val = max(numeric_items.values())
                max_keys = [k for k, v in numeric_items.items() if v == max_val]
                return '/'.join(max_keys[:2]) if max_keys else '综合型'
            except:
                return '综合型'
        
        # 更新数据库 - 包含详细子维度
        c.execute('''UPDATE employees SET 
            管理能力 = ?, 战略思维 = ?, 团队领导 = ?, 执行管控 = ?, 跨部门协作 = ?,
            性格特质分数 = ?, 外向性 = ?, 宜人性 = ?, 开放性 = ?, 责任心 = ?, 性格特质类型 = ?,
            行为模式类型 = ?, 行为模式分数 = ?,
            通用能力 = ?, 言语理解 = ?, 数量分析 = ?, 逻辑推理 = ?, 空间认知 = ?
            WHERE 工号 = ?''', (
            scores['管理能力']['total'],
            scores['管理能力']['战略思维'],
            scores['管理能力']['团队领导'],
            scores['管理能力']['执行管控'],
            scores['管理能力']['跨部门协作'],
            scores['性格特质']['total'],
            scores['性格特质']['外向性'],
            scores['性格特质']['宜人性'],
            scores['性格特质']['开放性'],
            scores['性格特质']['责任心'],
            get_max_type(scores['性格特质']),
            get_max_type(scores['DISC行为模式']),
            scores['DISC行为模式']['total'],
            scores['通用能力']['total'],
            scores['通用能力']['言语理解'],
            scores['通用能力']['数量分析'],
            scores['通用能力']['逻辑推理'],
            scores['通用能力']['空间认知'],
            员工工号
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("评分计算完成")
        
        return jsonify({
            "msg": "提交成功",
            "scores": {
                "管理能力": scores['管理能力']['total'],
                "性格特质": scores['性格特质']['total'],
                "DISC行为模式": scores['DISC行为模式']['total'],
                "通用能力": scores['通用能力']['total']
            }
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"提交答案失败: {str(e)}")
        logger.error(f"错误堆栈: {error_trace}")
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
            
            logger.info(f"开始调用DeepSeek API，数据长度: {len(data)}")
            logger.info(f"API Key: {api_key[:20]}...")
            
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
            
            try:
                response = requests.post(api_url, json=payload, headers=headers, timeout=180)
                logger.info(f"DeepSeek API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("DeepSeek API调用成功")
                    return result
                else:
                    error_msg = f"API调用失败，状态码: {response.status_code}, 响应: {response.text}"
                    logger.error(error_msg)
                    return f"Error: {response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                error_msg = "DeepSeek API调用超时"
                logger.error(error_msg)
                return f"Error: Timeout - {error_msg}"
            except requests.exceptions.RequestException as e:
                error_msg = f"DeepSeek API网络请求异常: {str(e)}"
                logger.error(error_msg)
                return f"Error: Network - {error_msg}"
            except Exception as e:
                error_msg = f"DeepSeek API调用异常: {str(e)}"
                logger.error(error_msg)
                return f"Error: Exception - {error_msg}"
        
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
通用能力：{通用能力}分
言语理解：{言语理解}分
数量分析：{数量分析}分
逻辑推理：{逻辑推理}分
空间认知：{空间认知}分

请根据以上数据生成详细的分析报告。
"""
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y年%m月%d日")
        
        # 准备数据 - 更新为新结构
        data_text = f"""
员工信息：
姓名：{employee_data['姓名']}
工号：{employee_data['工号']}
公司名称：{employee_data['公司名称']}
测评时间：{current_time}

能力评估结果：
管理能力总分：{employee_data['管理能力']}分
- 战略思维：{employee_data['战略思维']}分
- 团队领导：{employee_data['团队领导']}分  
- 执行管控：{employee_data['执行管控']}分
- 跨部门协作：{employee_data['跨部门协作']}分

性格特质总分：{employee_data['性格特质分数']}分
- 外向性：{employee_data['外向性']}分
- 宜人性：{employee_data['宜人性']}分
- 开放性：{employee_data['开放性']}分
- 责任心：{employee_data['责任心']}分

DISC行为模式：
- 类型：{employee_data['行为模式类型']}
- 总分：{employee_data['行为模式分数']}分

通用能力总分：{employee_data['通用能力']}分
- 言语理解：{employee_data['言语理解']}分
- 数量分析：{employee_data['数量分析']}分
- 逻辑推理：{employee_data['逻辑推理']}分
- 空间认知：{employee_data['空间认知']}分
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
        c.execute('SELECT id, 工号, 姓名, 管理能力, 战略思维, 团队领导, 执行管控, 跨部门协作, 性格特质分数, 外向性, 宜人性, 开放性, 责任心, 性格特质类型, 行为模式类型, 行为模式分数, 通用能力, 言语理解, 数量分析, 逻辑推理, 空间认知 FROM employees ORDER BY 创建时间 DESC')
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
            
            logger.info(f"管理员开始调用DeepSeek API，数据长度: {len(data)}")
            logger.info(f"API Key: {api_key[:20]}...")
            
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": data}]}
            
            try:
                response = requests.post(api_url, json=payload, headers=headers, timeout=180)
                logger.info(f"DeepSeek API响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("DeepSeek API调用成功")
                    return result
                else:
                    error_msg = f"API调用失败，状态码: {response.status_code}, 响应: {response.text}"
                    logger.error(error_msg)
                    return f"Error: {response.status_code} - {response.text}"
                    
            except requests.exceptions.Timeout:
                error_msg = "DeepSeek API调用超时"
                logger.error(error_msg)
                return f"Error: Timeout - {error_msg}"
            except requests.exceptions.RequestException as e:
                error_msg = f"DeepSeek API网络请求异常: {str(e)}"
                logger.error(error_msg)
                return f"Error: Network - {error_msg}"
            except Exception as e:
                error_msg = f"DeepSeek API调用异常: {str(e)}"
                logger.error(error_msg)
                return f"Error: Exception - {error_msg}"

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
管理能力总分：{employee_data['管理能力']}分
- 战略思维：{employee_data['战略思维']}分
- 团队领导：{employee_data['团队领导']}分  
- 执行管控：{employee_data['执行管控']}分
- 跨部门协作：{employee_data['跨部门协作']}分

性格特质总分：{employee_data['性格特质分数']}分
- 外向性：{employee_data['外向性']}分
- 宜人性：{employee_data['宜人性']}分
- 开放性：{employee_data['开放性']}分
- 责任心：{employee_data['责任心']}分

DISC行为模式：
- 类型：{employee_data['行为模式类型']}
- 总分：{employee_data['行为模式分数']}分

通用能力总分：{employee_data['通用能力']}分
- 言语理解：{employee_data['言语理解']}分
- 数量分析：{employee_data['数量分析']}分
- 逻辑推理：{employee_data['逻辑推理']}分
- 空间认知：{employee_data['空间认知']}分
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
        c.execute('''SELECT 工号, 姓名, 管理能力, 性格特质分数, 行为模式分数, 通用能力 FROM employees''')
        headers = ['工号','姓名','管理能力得分','性格特质得分','行为模式得分','通用能力得分']
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