# 员工能力测评系统部署指南

## 📋 概述

本指南将帮助您将员工能力测评系统部署到腾讯云CentOS服务器上。系统包含Flask后端、SQLite数据库、DeepSeek AI报告生成功能。

## 🚀 快速开始

### 服务器要求

- **操作系统**: CentOS 7.x/8.x
- **内存**: 至少1GB
- **磁盘**: 至少5GB可用空间
- **网络**: 已开放80、443、3306、6379端口

### 一键部署

```bash
# 1. 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/deploy.sh
chmod +x deploy.sh

# 2. 运行部署脚本
./deploy.sh

# 3. 按照提示配置环境变量
```

## 📁 项目结构

```
Project -new/
├── new_app.py              # 主应用文件
├── config.py               # 配置文件
├── db_migration.py         # 数据库迁移工具
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker构建文件
├── docker-compose.yml     # Docker编排配置
├── nginx.conf            # Nginx配置文件
├── deploy.sh             # 部署脚本
├── env.example           # 环境变量示例
├── templates/            # HTML模板
├── static/               # 静态文件
├── data/                 # 数据库文件目录
├── logs/                 # 日志文件目录
└── uploads/             # 上传文件目录
```

## 🔧 详细部署步骤

### 步骤1: 服务器准备

```bash
# 更新系统
sudo yum update -y

# 安装基础工具
sudo yum install -y wget curl git unzip

# 配置防火墙
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### 步骤2: 上传项目文件

```bash
# 方法1: 使用SCP上传
scp -r Project-new root@124.223.40.219:/opt/

# 方法2: 使用Git克隆
cd /opt
git clone https://github.com/your-repo/Project-new.git
cd Project-new
```

### 步骤3: 配置环境变量

```bash
cd /opt/Project-new
cp env.example .env

# 编辑环境变量文件
vim .env
```

关键配置项：
```bash
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
DEEPSEEK_API_KEY=sk-your-api-key
DATABASE_PATH=/opt/Project-new/data/new_questions.db
```

### 步骤4: 数据库迁移

如果您有现有的数据库需要迁移：

```bash
# 1. 在本地运行迁移脚本
python3 db_migration.py

# 2. 上传生成的迁移文件
scp migration_files/database_migration_*.zip root@124.223.40.219:/opt/

# 3. 在服务器上恢复数据库
cd /opt
unzip database_migration_*.zip
cd migration_files
python3 migrate_*.py
```

### 步骤5: Docker部署（推荐）

```bash
cd /opt/Project-new

# 构建并启动服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

### 步骤6: 传统部署（备选）

```bash
cd /opt/Project-new

# 安装Python依赖
pip3 install -r requirements.txt

# 初始化数据库
python3 init_database.py

# 配置Nginx
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx

# 启动应用
python3 new_app.py
```

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_ENV | 运行环境 | production |
| SECRET_KEY | Flask密钥 | 必须设置 |
| PORT | 监听端口 | 5000 |
| DATABASE_PATH | 数据库路径 | /app/data/new_questions.db |
| DEEPSEEK_API_KEY | AI API密钥 | 必须设置 |
| LOG_LEVEL | 日志级别 | INFO |

### Nginx配置

系统使用Nginx作为反向代理，支持：
- 静态文件缓存
- Gzip压缩
- SSL重定向（可选）
- 安全头设置

### 数据库配置

- **类型**: SQLite
- **位置**: `/opt/Project-new/data/new_questions.db`
- **备份**: 自动创建每日备份

## 🔍 监控和维护

### 查看服务状态

```bash
# Docker部署
docker-compose ps
docker-compose logs -f

# 传统部署
sudo systemctl status employee-assessment
sudo systemctl status nginx
```

### 日志查看

```bash
# 应用日志
tail -f /opt/Project-new/logs/app.log

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker日志
docker-compose logs -f employee-assessment
```

### 备份策略

```bash
# 数据库备份
cp /opt/Project-new/data/new_questions.db /opt/backup/$(date +%Y%m%d).db

# 完整备份
tar -czf /opt/backup/full_$(date +%Y%m%d).tar.gz /opt/Project-new
```

## 🚨 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
sudo netstat -tulpn | grep :5000

# 杀死进程
sudo kill -9 <PID>
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件权限
ls -la /opt/Project-new/data/new_questions.db

# 修复权限
chmod 644 /opt/Project-new/data/new_questions.db
```

#### 3. Docker服务无法启动
```bash
# 检查Docker状态
sudo systemctl status docker

# 重启Docker服务
sudo systemctl restart docker
```

#### 4. 内存不足
```bash
# 查看内存使用
free -h

# 增加交换空间
sudo dd if=/dev/zero of=/swapfile bs=1G count=2
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 性能优化

#### 1. Gunicorn配置优化
```bash
# 调整worker数量
gunicorn --workers=4 --threads=2 --bind=0.0.0.0:5000 new_app:app
```

#### 2. 数据库优化
```bash
# 创建索引
sqlite3 new_questions.db "CREATE INDEX IF NOT EXISTS idx_timestamp ON employees(创建时间);"
```

#### 3. Nginx优化
```nginx
worker_processes auto;
worker_connections 1024;
```

## 🔐 安全配置

### 1. 更新系统
```bash
sudo yum update -y
```

### 2. 配置防火墙
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. SSL证书（可选）
```bash
# 使用Let's Encrypt
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 124.223.40.219
```

### 4. 定期更新
```bash
# 设置自动更新
sudo yum install -y yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

## 📞 支持和帮助

### 访问地址
- **主应用**: http://124.223.40.219
- **管理后台**: http://124.223.40.219/manage
- **健康检查**: http://124.223.40.219/health

### 技术支持
- 查看日志文件了解详细错误信息
- 检查网络连接和端口开放状态
- 验证API密钥和数据库连接

### 更新部署
```bash
# 停止服务
docker-compose down

# 拉取新代码
git pull origin main

# 重新部署
docker-compose up -d --build
```

---

## 📝 版本信息

- **应用版本**: v1.0.0
- **Python版本**: 3.11
- **Flask版本**: 2.3.3
- **数据库**: SQLite 3.x

## 🎯 后续计划

- [ ] 添加监控面板
- [ ] 实现自动备份
- [ ] 支持MySQL数据库
- [ ] 添加单元测试
- [ ] 实现CI/CD流程
