#!/bin/bash

# 员工能力测评系统部署脚本
# 支持腾讯云CentOS服务器自动部署

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令未找到，请先安装"
        exit 1
    fi
}

# 系统要求检查
check_system() {
    log_info "检查系统要求..."

    # 检查是否为CentOS
    if [[ ! -f /etc/os-release ]] || ! grep -q "CentOS" /etc/os-release; then
        log_warning "建议在CentOS系统上运行此脚本"
    fi

    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [[ $total_mem -lt 1024 ]]; then
        log_warning "系统内存${total_mem}MB，建议至少1GB内存"
    fi

    log_success "系统检查完成"
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."

    # 更新包管理器
    yum update -y

    # 安装基础工具
    yum install -y wget curl git unzip

    # 安装Python3和pip
    if ! command -v python3 &> /dev/null; then
        yum install -y python3 python3-pip python3-devel
    fi

    # 安装Docker
    if ! command -v docker &> /dev/null; then
        log_info "安装Docker..."
        yum install -y yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

        # 启动Docker服务
        systemctl start docker
        systemctl enable docker

        # 将当前用户添加到docker组
        usermod -aG docker $(whoami)
    fi

    # 安装Nginx
    if ! command -v nginx &> /dev/null; then
        yum install -y nginx
        systemctl enable nginx
    fi

    log_success "系统依赖安装完成"
}

# 配置Python环境
setup_python_environment() {
    log_info "配置Python环境..."

    # 升级pip
    python3 -m pip install --upgrade pip

    # 配置pip使用腾讯云镜像
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.tencent.com/pypi/simple/
trusted-host = mirrors.tencent.com
timeout = 30
retries = 3
EOF

    log_success "Python环境配置完成"
}

# 创建项目目录结构
create_project_structure() {
    log_info "创建项目目录结构..."

    # 创建主目录
    mkdir -p /opt/employee-assessment
    cd /opt/employee-assessment

    # 创建子目录
    mkdir -p data logs uploads ssl backup

    # 设置权限
    chmod -R 755 /opt/employee-assessment
    chown -R $(whoami):$(whoami) /opt/employee-assessment

    log_success "项目目录结构创建完成"
}

# 备份现有部署
backup_existing_deployment() {
    if [[ -d "/opt/employee-assessment" ]] && [[ -f "/opt/employee-assessment/docker-compose.yml" ]]; then
        log_info "备份现有部署..."

        backup_dir="/opt/employee-assessment/backup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p $backup_dir

        # 备份数据库
        if [[ -f "/opt/employee-assessment/data/new_questions.db" ]]; then
            cp /opt/employee-assessment/data/new_questions.db $backup_dir/
        fi

        # 备份配置文件
        if [[ -f "/opt/employee-assessment/.env" ]]; then
            cp /opt/employee-assessment/.env $backup_dir/
        fi

        log_success "备份完成: $backup_dir"
    fi
}

# 部署应用
deploy_application() {
    log_info "部署应用..."

    cd /opt/employee-assessment

    # 停止现有服务
    if [[ -f "docker-compose.yml" ]]; then
        docker-compose down || true
    fi

    # 停止Nginx
    systemctl stop nginx || true

    # 复制项目文件（假设已上传到服务器）
    # 这里需要手动上传项目文件或使用git clone

    # 安装Python依赖
    if [[ -f "requirements.txt" ]]; then
        pip3 install -r requirements.txt
    fi

    # 配置环境变量
    if [[ ! -f ".env" ]]; then
        cp env.example .env
        log_warning "请编辑 .env 文件配置环境变量"
    fi

    # 初始化数据库
    if [[ -f "new_questions.db" ]]; then
        log_info "检测到数据库文件，移动到数据目录..."
        mv new_questions.db data/
    elif [[ -f "init_database.py" ]]; then
        log_info "初始化数据库..."
        python3 init_database.py
        mv new_questions.db data/
    fi

    # 构建和启动Docker容器
    if [[ -f "docker-compose.yml" ]]; then
        log_info "启动Docker容器..."
        docker-compose up -d --build
    else
        log_info "启动Flask应用..."
        # 创建systemd服务
        cat > /etc/systemd/system/employee-assessment.service << EOF
[Unit]
Description=Employee Assessment Service
After=network.target

[Service]
Type=exec
User=$(whoami)
WorkingDirectory=/opt/employee-assessment
ExecStart=/usr/bin/python3 new_app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

        systemctl daemon-reload
        systemctl start employee-assessment
        systemctl enable employee-assessment
    fi

    # 配置Nginx
    if [[ -f "nginx.conf" ]]; then
        cp nginx.conf /etc/nginx/nginx.conf
        nginx -t
        systemctl start nginx
        systemctl enable nginx
    fi

    log_success "应用部署完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."

    # 检查firewalld状态
    if command -v firewall-cmd &> /dev/null; then
        systemctl start firewalld
        systemctl enable firewalld

        # 开放端口
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --reload

        log_success "防火墙配置完成"
    else
        log_warning "未检测到firewalld，跳过防火墙配置"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."

    # 等待服务启动
    sleep 10

    # 检查端口
    if curl -f http://localhost:5000/ &> /dev/null; then
        log_success "应用服务运行正常"
    else
        log_error "应用服务检查失败"
        exit 1
    fi

    if curl -f http://localhost/ &> /dev/null; then
        log_success "Nginx代理运行正常"
    else
        log_error "Nginx代理检查失败"
        exit 1
    fi

    log_success "健康检查完成"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署信息:"

    echo "======================================"
    echo "员工能力测评系统部署完成！"
    echo "======================================"
    echo "访问地址: http://124.223.40.219"
    echo "管理后台: http://124.223.40.219/manage"
    echo "API文档: http://124.223.40.219/api/"
    echo ""
    echo "重要文件位置:"
    echo "项目目录: /opt/employee-assessment"
    echo "数据库: /opt/employee-assessment/data/new_questions.db"
    echo "日志: /opt/employee-assessment/logs/"
    echo "上传文件: /opt/employee-assessment/uploads/"
    echo ""
    echo "服务状态检查:"
    echo "sudo systemctl status employee-assessment"
    echo "sudo systemctl status nginx"
    echo "sudo docker-compose ps"
    echo "======================================"
}

# 主函数
main() {
    log_info "开始部署员工能力测评系统..."

    # 检查是否为root用户
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi

    # 执行部署步骤
    check_system
    install_system_dependencies
    setup_python_environment
    backup_existing_deployment
    create_project_structure
    deploy_application
    configure_firewall
    health_check
    show_deployment_info

    log_success "部署完成！请访问 http://124.223.40.219 查看应用"
}

# 参数处理
case "${1:-}" in
    "check")
        check_system
        ;;
    "install-deps")
        install_system_dependencies
        ;;
    "deploy")
        deploy_application
        ;;
    "backup")
        backup_existing_deployment
        ;;
    *)
        main
        ;;
esac
