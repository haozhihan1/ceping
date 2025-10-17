# 员工能力测评系统 - Git部署到腾讯云指南

## 概述

本文档提供了将员工能力测评系统通过Git从本地开发环境部署到腾讯云CentOS服务器的完整指南。

## 服务器信息

- **服务器IP**: 124.223.40.219
- **操作系统**: CentOS 7/8 (TencentOS)
- **Python版本**: 3.8+
- **架构**: Nginx + Gunicorn + Supervisor

## 部署前准备

### 1. 本地环境要求

- Git 客户端
- SSH 客户端
- Python 3.8+
- 项目源码

### 2. 生成数据库迁移文件

在本地项目目录运行：

```bash
python database_migration.py
```

这将生成两个重要文件：
- `database_migration.sql` - SQL格式的完整数据库迁移文件
- `database_backup.json` - JSON格式的数据库备份文件

### 3. 创建Git仓库

如果您还没有Git仓库，可以使用以下平台之一：

- **GitHub**: https://github.com
- **Gitee (码云)**: https://gitee.com (国内访问更快)
- **Coding**: https://coding.net
- **自建GitLab**

### 4. 配置环境变量

编辑 `production.env` 文件，设置生产环境配置：

```bash
# 必须修改的配置
SECRET_KEY=your-random-secret-key-at-least-32-characters-long
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key-here
ADMIN_PASSWORD=YourSecurePassword123!

# 服务器配置
HOST=0.0.0.0
PORT=8000
WORKERS=4
DATABASE_PATH=/home/www/flask_project/data/new_questions.db
```

## 自动部署方法（推荐）

### 1. 使用部署脚本

```bash
# 给脚本执行权限
chmod +x deploy_to_tencent_cloud.sh

# 设置Git仓库地址（选择一个）
export GIT_REPO_URL="https://github.com/yourusername/your-repo.git"
export GIT_REPO_URL="https://gitee.com/yourusername/your-repo.git"

# 执行完整部署
./deploy_to_tencent_cloud.sh

# 或者分步执行
./deploy_to_tencent_cloud.sh prepare   # 准备本地代码
./deploy_to_tencent_cloud.sh upload    # 上传到Git
./deploy_to_tencent_cloud.sh deploy    # 部署到服务器
```

### 2. 部署过程说明

脚本将自动完成以下步骤：

1. **本地准备**
   - 初始化Git仓库
   - 添加适当的.gitignore文件
   - 提交代码更改

2. **上传代码**
   - 推送代码到Git仓库

3. **服务器部署**
   - 安装系统依赖
   - 创建用户和目录
   - 克隆项目代码
   - 配置Python环境
   - 导入数据库
   - 配置服务
   - 启动应用

## 手动部署方法

如果自动部署脚本有问题，可以按以下步骤手动部署：

### 第一步：本地代码准备

```bash
# 1. 初始化Git仓库
git init
git branch -M main

# 2. 创建.gitignore文件
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
venv/
.env
*.db
logs/
backup/
uploads/
app.log
EOF

# 3. 添加并提交代码
git add .
git commit -m "Initial commit for production"

# 4. 添加远程仓库并推送
git remote add origin https://your-git-repo-url.git
git push -u origin main
```

### 第二步：服务器环境准备

连接到腾讯云服务器：

```bash
ssh root@124.223.40.219
```

安装系统依赖：

```bash
# 更新系统
yum update -y

# 安装基础工具
yum install -y wget curl git unzip vim python3 python3-pip python3-devel

# 安装Web服务
yum install -y nginx supervisor

# 启用服务
systemctl enable nginx supervisord
```

### 第三步：项目部署

```bash
# 1. 创建用户和目录
useradd -m www
mkdir -p /home/www/flask_project/{data,logs,uploads,backup}
chown -R www:www /home/www/flask_project

# 2. 克隆项目
cd /home/www
sudo -u www git clone https://your-git-repo-url.git flask_project
cd flask_project

# 3. 配置Python环境
sudo -u www python3 -m venv venv
sudo -u www bash -c "source venv/bin/activate && pip install -r requirements.txt"

# 4. 配置环境变量
sudo -u www cp production.env .env
sudo -u www vim .env  # 编辑配置

# 5. 导入数据库
sudo -u www sqlite3 data/new_questions.db < database_migration.sql

# 6. 配置服务
cp production_nginx.conf /etc/nginx/nginx.conf
cp production_supervisor.conf /etc/supervisord.d/flask_app.ini

# 7. 启动服务
nginx -t
systemctl restart nginx supervisord
supervisorctl reread
supervisorctl update
supervisorctl start employee_assessment
```

### 第四步：防火墙配置

```bash
# 启动防火墙
systemctl start firewalld
systemctl enable firewalld

# 开放端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

## 部署验证

### 1. 检查服务状态

```bash
# 检查Nginx
systemctl status nginx

# 检查Supervisor
systemctl status supervisord

# 检查应用进程
supervisorctl status employee_assessment

# 检查端口
netstat -tlnp | grep :80
netstat -tlnp | grep :8000
```

### 2. 健康检查

```bash
# 健康检查接口
curl http://localhost/health
curl http://124.223.40.219/health

# 主页面
curl http://124.223.40.219/
```

### 3. 查看日志

```bash
# 应用日志
tail -f /var/log/supervisor/flask_app_stdout.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Gunicorn日志
tail -f /home/www/flask_project/logs/gunicorn_error.log
```

## 更新部署

当需要更新代码时：

```bash
# 在本地提交新代码
git add .
git commit -m "Update features"
git push origin main

# 在服务器更新
ssh root@124.223.40.219
cd /home/www/flask_project
sudo -u www git pull origin main
sudo -u www bash -c "source venv/bin/activate && pip install -r requirements.txt"
supervisorctl restart employee_assessment
```

## 常见问题排查

### 1. 应用无法启动

```bash
# 查看详细错误信息
supervisorctl tail -f employee_assessment stderr

# 检查环境变量
cd /home/www/flask_project
sudo -u www bash -c "source venv/bin/activate && python -c 'import os; print(os.environ.get(\"SECRET_KEY\"))'"

# 手动测试
sudo -u www bash -c "source venv/bin/activate && python production_app.py"
```

### 2. 数据库问题

```bash
# 检查数据库文件
ls -la /home/www/flask_project/data/new_questions.db

# 测试数据库连接
sqlite3 /home/www/flask_project/data/new_questions.db "SELECT COUNT(*) FROM questions;"

# 重新导入数据库
cd /home/www/flask_project
sudo -u www sqlite3 data/new_questions.db < database_migration.sql
```

### 3. 权限问题

```bash
# 修复文件权限
chown -R www:www /home/www/flask_project
chmod -R 755 /home/www/flask_project
chmod 664 /home/www/flask_project/data/new_questions.db
```

### 4. 网络连接问题

```bash
# 检查防火墙状态
firewall-cmd --list-all

# 检查端口占用
netstat -tlnp | grep :80
netstat -tlnp | grep :8000

# 测试内网连接
curl http://127.0.0.1:8000/health
```

## 安全建议

### 1. 必须修改的配置

- `SECRET_KEY`: 使用随机生成的32位以上字符串
- `ADMIN_PASSWORD`: 使用强密码
- `DEEPSEEK_API_KEY`: 使用有效的API密钥

### 2. SSL证书配置（推荐）

```bash
# 安装certbot
yum install -y certbot python3-certbot-nginx

# 申请免费SSL证书
certbot --nginx -d your-domain.com

# 配置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 3. 定期备份

```bash
# 创建备份脚本
cat > /home/www/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/www/backup"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
cp /home/www/flask_project/data/new_questions.db $BACKUP_DIR/database_$DATE.db

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz -C /home/www/flask_project .env

# 清理旧备份
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/www/backup.sh

# 添加定时任务
echo "0 2 * * * /home/www/backup.sh" | crontab -
```

## 监控和维护

### 1. 系统监控

```bash
# 安装监控工具
yum install -y htop iotop

# 查看系统资源
htop
df -h
free -h
```

### 2. 日志管理

```bash
# 配置日志轮转
cat > /etc/logrotate.d/flask_app << EOF
/var/log/supervisor/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 www www
}
EOF
```

## 总结

按照本指南，您应该能够成功将员工能力测评系统部署到腾讯云服务器。关键点：

1. **数据完整性**: 确保数据库迁移文件正确生成和导入
2. **安全配置**: 修改默认密钥和密码
3. **服务监控**: 定期检查服务状态和日志
4. **定期备份**: 设置自动备份机制

部署完成后，可通过 http://124.223.40.219 访问系统。

如遇问题，请参考常见问题排查部分或联系技术支持。
