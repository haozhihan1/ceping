# 腾讯云CentOS部署指南

## 项目概述

本项目是一个基于Flask的员工能力测评系统，包含前端界面、后端API、SQLite数据库和AI报告生成功能。

## 服务器配置

- **操作系统**: CentOS 7/8 (腾讯云)
- **Python版本**: 3.8+
- **Web服务器**: Nginx + Gunicorn
- **进程管理**: Supervisor
- **公网IP**: 124.223.40.219
- **开放端口**: 80, 443, 3306, 6379 (已配置)

## 部署前准备

### 1. 本地环境准备

```bash
# 1. 导出数据库迁移文件
python database_migration.py

# 2. 验证导出文件
ls -la database_migration.sql database_backup.json
```

### 2. 服务器环境准备

连接到腾讯云服务器：

```bash
ssh root@124.223.40.219
```

## 服务器部署步骤

### 第一步：系统环境配置

```bash
# 1. 更新系统并配置腾讯云镜像源
yum update -y

# 备份原yum源
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup

# 配置腾讯云镜像源
curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.tencent.com/repo/centos7_base.repo

# 清理缓存并更新
yum clean all
yum makecache
yum update -y

# 2. 安装必要软件
yum install -y python3 python3-pip nginx supervisor git vim

# 3. 创建项目目录
mkdir -p /home/www/flask_project
cd /home/www

# 4. 创建www用户
useradd -m www
chown -R www:www /home/www
```

### 第二步：Python环境配置

```bash
# 1. 配置Python pip使用腾讯云镜像
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.tencent.com/pypi/simple/
trusted-host = mirrors.tencent.com
EOF

# 2. 创建虚拟环境
cd /home/www/flask_project
python3 -m venv venv
source venv/bin/activate

# 3. 升级pip
pip install --upgrade pip

# 4. 安装项目依赖
pip install flask flask-cors requests gunicorn pandas openpyxl
```

### 第三步：项目部署

```bash
# 1. 上传项目文件到服务器
# 使用scp或rz命令上传项目文件
# 或者使用git clone (推荐)

# 示例：使用git上传（需先在本地提交代码）
git init
git add .
git commit -m "Initial commit for production deployment"
# 然后在服务器上克隆

# 或者直接上传压缩包
# tar -czf project.tar.gz .
# 上传到服务器后解压

# 2. 设置项目权限
chown -R www:www /home/www/flask_project

# 3. 配置环境变量
cd /home/www/flask_project
cp env_template.txt .env
vim .env  # 编辑配置文件，填入实际值
```

### 第四步：数据库迁移

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 初始化数据库
python init_database.py

# 3. 如果有现有数据，使用迁移脚本恢复
# sqlite3 new_questions.db < database_migration.sql
```

### 第五步：Web服务器配置

```bash
# 1. 配置Nginx
cp nginx.conf /etc/nginx/conf.d/flask_app.conf
nginx -t  # 测试配置
systemctl enable nginx
systemctl start nginx

# 2. 配置Supervisor
cp supervisord.conf /etc/supervisord.d/flask_app.ini
systemctl enable supervisord
systemctl start supervisord

# 3. 启动应用
supervisorctl start flask_app
```

### 第六步：防火墙配置

```bash
# 1. 配置firewalld
systemctl start firewalld
systemctl enable firewalld

# 2. 开放端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload

# 3. 验证端口状态
netstat -tlnp | grep :80
```

## 环境变量配置

在 `.env` 文件中配置以下变量：

```bash
# Flask应用配置
SECRET_KEY=your-production-secret-key-change-this-to-random-string
PORT=8000
HOST=0.0.0.0
WORKERS=4

# DeepSeek API配置
DEEPSEEK_API_KEY=your-actual-deepseek-api-key

# 管理员账号配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## 安全配置

### 1. SSL证书配置（推荐）

```bash
# 安装certbot
yum install -y certbot python-certbot-nginx

# 获取免费证书
certbot --nginx -d your-domain.com

# 配置自动续期
crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. 定期备份

```bash
# 创建备份脚本
cat > /home/www/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/www/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /home/www/flask_project/new_questions.db $BACKUP_DIR/database_$DATE.db

# 备份日志
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/supervisor/ /var/log/nginx/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: $DATE"
EOF

chmod +x /home/www/backup.sh

# 添加定时任务
crontab -e
# 添加：0 2 * * * /home/www/backup.sh
```

## 监控和维护

### 1. 应用监控

```bash
# 检查应用状态
supervisorctl status

# 查看应用日志
tail -f /var/log/supervisor/flask_app.log

# 重启应用
supervisorctl restart flask_app
```

### 2. 系统监控

```bash
# 安装监控工具
yum install -y htop iotop ncdu

# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看网络连接
netstat -tlnp
```

### 3. 日志轮转

```bash
# 配置logrotate
cat > /etc/logrotate.d/flask_app << EOF
/var/log/supervisor/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 www www
    postrotate
        supervisorctl reload
    endscript
}
EOF
```

## 故障排除

### 常见问题

1. **应用无法启动**
   ```bash
   # 检查日志
   tail -f /var/log/supervisor/flask_app.log

   # 检查环境变量
   source venv/bin/activate && python -c "import os; print(os.environ.get('DEEPSEEK_API_KEY'))"

   # 手动测试启动
   python start_production.py
   ```

2. **数据库连接问题**
   ```bash
   # 检查数据库文件权限
   ls -la /home/www/flask_project/new_questions.db

   # 验证数据库完整性
   sqlite3 new_questions.db "SELECT name FROM sqlite_master WHERE type='table';"
   ```

3. **Nginx代理错误**
   ```bash
   # 检查Nginx状态
   systemctl status nginx

   # 测试配置
   nginx -t

   # 查看错误日志
   tail -f /var/log/nginx/error.log
   ```

4. **端口占用问题**
   ```bash
   # 查看端口占用
   netstat -tlnp | grep :8000
   netstat -tlnp | grep :80

   # 杀死占用进程
   kill -9 PID
   ```

## 性能优化

### 1. Gunicorn优化

```python
# 在start_production.py中调整参数
workers = int(os.environ.get('WORKERS', 2 * multiprocessing.cpu_count() + 1))
worker_class = 'gevent'  # 或 'eventlet'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
```

### 2. Nginx优化

```nginx
# 在nginx.conf中添加
worker_processes auto;
worker_connections 1024;

# 启用gzip压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### 3. 数据库优化

```bash
# 为数据库添加索引
sqlite3 new_questions.db "CREATE INDEX IF NOT EXISTS idx_employees_gonghao ON employees(工号);"

# 定期清理和优化
sqlite3 new_questions.db "VACUUM;"
```

## 更新部署

```bash
# 1. 备份当前版本
cp -r /home/www/flask_project /home/www/flask_project_backup_$(date +%Y%m%d)

# 2. 停止应用
supervisorctl stop flask_app

# 3. 更新代码
cd /home/www/flask_project
# 上传新版本文件或git pull

# 4. 更新依赖（如果需要）
source venv/bin/activate
pip install -r requirements.txt

# 5. 启动应用
supervisorctl start flask_app

# 6. 测试新版本
curl http://localhost/health
```

## 总结

按照以上步骤，您应该能够成功将Flask项目部署到腾讯云CentOS服务器。部署完成后，通过浏览器访问 `http://124.223.40.219` 即可使用系统。

如有问题，请检查日志文件并参考故障排除部分。
