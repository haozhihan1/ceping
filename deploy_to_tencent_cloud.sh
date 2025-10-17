#!/bin/bash
# 
# 腾讯云服务器自动部署脚本
# 员工能力测评系统 - Git部署版本
# 
# 使用方法：
# 1. 在本地运行此脚本上传代码到Git仓库
# 2. 在腾讯云服务器上运行远程部署命令
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 配置变量
SERVER_IP="124.223.40.219"
SERVER_USER="root"
PROJECT_NAME="employee-assessment-system"
REMOTE_DIR="/home/www/flask_project"
GIT_REPO_URL="https://github.com/haozhihan1/ceping.git"  # 使用GitHub仓库地址

# 检查必要工具
check_requirements() {
    log_info "检查部署环境..."
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        log_error "Git未安装，请先安装Git"
        exit 1
    fi
    
    # 检查SSH
    if ! command -v ssh &> /dev/null; then
        log_error "SSH客户端未安装"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 准备本地代码
prepare_local_code() {
    log_info "准备本地代码..."
    
    # 检查是否在Git仓库中
    if [ ! -d ".git" ]; then
        log_info "初始化Git仓库..."
        git init
        git branch -M main
        
        # 创建.gitignore文件
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
app.log
*.db
backup/
uploads/
logs/

# Environment files
.env
production.env

# Temporary files
*.tmp
*.temp
EOF
    fi
    
    # 添加文件到Git
    git add .
    git commit -m "准备生产环境部署 - $(date '+%Y-%m-%d %H:%M:%S')" || log_info "没有新的更改需要提交"
    
    log_success "本地代码准备完成"
}

# 上传代码到Git仓库
upload_to_git() {
    log_info "上传代码到Git仓库..."
    
    if [ -z "$GIT_REPO_URL" ]; then
        log_warning "请设置Git仓库地址变量 GIT_REPO_URL"
        read -p "请输入Git仓库地址: " GIT_REPO_URL
    fi
    
    # 添加远程仓库
    if ! git remote get-url origin &> /dev/null; then
        git remote add origin "$GIT_REPO_URL"
    else
        git remote set-url origin "$GIT_REPO_URL"
    fi
    
    # 推送代码
    git push -u origin main
    
    log_success "代码已上传到Git仓库"
}

# 连接服务器并部署
deploy_to_server() {
    log_info "开始部署到腾讯云服务器..."
    
    # 生成部署脚本
    cat > /tmp/remote_deploy.sh << 'REMOTE_SCRIPT'
#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查是否为CentOS
    if ! grep -q "CentOS" /etc/os-release 2>/dev/null; then
        log_warning "系统不是CentOS，请注意兼容性"
    fi
    
    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$total_mem" -lt 1024 ]; then
        log_warning "系统内存${total_mem}MB，建议至少1GB"
    fi
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 更新系统
    yum update -y
    
    # 安装基础工具
    yum install -y wget curl git unzip vim
    
    # 安装Python3
    if ! command -v python3 &> /dev/null; then
        yum install -y python3 python3-pip python3-devel
    fi
    
    # 安装Nginx
    if ! command -v nginx &> /dev/null; then
        yum install -y nginx
        systemctl enable nginx
    fi
    
    # 安装Supervisor
    if ! command -v supervisord &> /dev/null; then
        yum install -y supervisor
        systemctl enable supervisord
    fi
    
    log_success "系统依赖安装完成"
}

# 创建用户和目录
setup_user_and_dirs() {
    log_info "设置用户和目录..."
    
    # 创建www用户
    if ! id -u www &>/dev/null; then
        useradd -m -s /bin/bash www
    fi
    
    # 创建项目目录
    mkdir -p /home/www/flask_project/{data,logs,uploads,backup,static}
    
    # 设置权限
    chown -R www:www /home/www/flask_project
    
    log_success "用户和目录设置完成"
}

# 配置Python环境
setup_python_env() {
    log_info "配置Python环境..."
    
    cd /home/www/flask_project
    
    # 配置pip镜像
    sudo -u www mkdir -p ~/.pip
    sudo -u www cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.tencent.com/pypi/simple/
trusted-host = mirrors.tencent.com
timeout = 30
EOF
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        sudo -u www python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    sudo -u www bash -c "source venv/bin/activate && pip install --upgrade pip"
    
    log_success "Python环境配置完成"
}

# 克隆项目代码
clone_project() {
    log_info "克隆项目代码..."
    
    cd /home/www
    
    # 备份现有项目
    if [ -d "flask_project_old" ]; then
        rm -rf flask_project_old
    fi
    
    if [ -d "flask_project" ] && [ -d "flask_project/.git" ]; then
        log_info "更新现有项目..."
        cd flask_project
        sudo -u www git pull origin main
    else
        log_info "首次克隆项目..."
        if [ -d "flask_project" ]; then
            mv flask_project flask_project_old
        fi
        
        read -p "请输入Git仓库地址: " GIT_REPO_URL
        sudo -u www git clone "$GIT_REPO_URL" flask_project
        cd flask_project
    fi
    
    # 设置权限
    chown -R www:www /home/www/flask_project
    
    log_success "项目代码克隆完成"
}

# 安装项目依赖
install_project_deps() {
    log_info "安装项目依赖..."
    
    cd /home/www/flask_project
    
    # 安装Python依赖
    sudo -u www bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    log_success "项目依赖安装完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    cd /home/www/flask_project
    
    # 如果存在迁移文件，导入数据
    if [ -f "database_migration.sql" ]; then
        log_info "发现数据库迁移文件，正在导入数据..."
        sudo -u www sqlite3 data/new_questions.db < database_migration.sql
        log_success "数据库迁移完成"
    else
        # 初始化新数据库
        log_info "初始化新数据库..."
        sudo -u www bash -c "source venv/bin/activate && python init_database.py"
        mv new_questions.db data/ 2>/dev/null || true
    fi
    
    # 设置数据库权限
    chown www:www data/new_questions.db
    chmod 664 data/new_questions.db
    
    log_success "数据库配置完成"
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    cd /home/www/flask_project
    
    if [ ! -f ".env" ]; then
        if [ -f "production.env" ]; then
            sudo -u www cp production.env .env
            log_warning "请编辑 .env 文件设置正确的密钥和配置"
            log_warning "特别注意: SECRET_KEY 和 DEEPSEEK_API_KEY 必须设置"
        else
            log_error "未找到环境配置模板文件"
            exit 1
        fi
    fi
    
    log_success "环境变量配置完成"
}

# 配置服务
setup_services() {
    log_info "配置系统服务..."
    
    cd /home/www/flask_project
    
    # 配置Nginx
    if [ -f "production_nginx.conf" ]; then
        cp production_nginx.conf /etc/nginx/nginx.conf
        nginx -t
    fi
    
    # 配置Supervisor
    if [ -f "production_supervisor.conf" ]; then
        cp production_supervisor.conf /etc/supervisord.d/flask_app.ini
    fi
    
    # 重启服务
    systemctl restart nginx
    systemctl restart supervisord
    
    # 启动应用
    supervisorctl reread
    supervisorctl update
    supervisorctl start employee_assessment
    
    log_success "系统服务配置完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if command -v firewall-cmd &> /dev/null; then
        systemctl start firewalld
        systemctl enable firewalld
        
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --reload
        
        log_success "防火墙配置完成"
    else
        log_warning "firewalld未安装，跳过防火墙配置"
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    sleep 10
    
    if curl -f http://localhost/health &> /dev/null; then
        log_success "应用运行正常"
    else
        log_error "应用健康检查失败，请检查日志"
        supervisorctl status employee_assessment
        exit 1
    fi
}

# 显示部署结果
show_result() {
    echo "====================================="
    echo "部署完成！"
    echo "====================================="
    echo "访问地址: http://124.223.40.219"
    echo "管理后台: http://124.223.40.219/manage"
    echo ""
    echo "重要提醒:"
    echo "1. 请编辑 /home/www/flask_project/.env 文件"
    echo "2. 设置正确的 SECRET_KEY 和 DEEPSEEK_API_KEY"
    echo "3. 修改默认管理员密码"
    echo ""
    echo "服务管理命令:"
    echo "supervisorctl status employee_assessment"
    echo "supervisorctl restart employee_assessment"
    echo "systemctl status nginx"
    echo "====================================="
}

# 主函数
main() {
    log_info "开始自动部署员工能力测评系统..."
    
    check_system
    install_dependencies
    setup_user_and_dirs
    setup_python_env
    clone_project
    install_project_deps
    setup_database
    setup_env
    setup_services
    setup_firewall
    health_check
    show_result
    
    log_success "部署完成！"
}

# 执行部署
main
REMOTE_SCRIPT

    # 上传并执行部署脚本
    log_info "上传部署脚本到服务器..."
    scp /tmp/remote_deploy.sh ${SERVER_USER}@${SERVER_IP}:/tmp/
    
    log_info "在服务器上执行部署..."
    ssh ${SERVER_USER}@${SERVER_IP} "chmod +x /tmp/remote_deploy.sh && /tmp/remote_deploy.sh"
    
    # 清理临时文件
    rm -f /tmp/remote_deploy.sh
    
    log_success "部署完成！"
}

# 显示使用说明
show_usage() {
    echo "腾讯云自动部署脚本"
    echo ""
    echo "使用方法："
    echo "  $0 [选项]"
    echo ""
    echo "选项："
    echo "  prepare     - 只准备本地代码"
    echo "  upload      - 上传代码到Git仓库"
    echo "  deploy      - 部署到服务器"
    echo "  full        - 完整部署流程（默认）"
    echo "  help        - 显示帮助信息"
    echo ""
    echo "环境变量："
    echo "  SERVER_IP       - 服务器IP地址（默认：124.223.40.219）"
    echo "  SERVER_USER     - 服务器用户名（默认：root）"
    echo "  GIT_REPO_URL    - Git仓库地址"
    echo ""
}

# 主函数
main() {
    case "${1:-full}" in
        "prepare")
            check_requirements
            prepare_local_code
            ;;
        "upload")
            check_requirements
            prepare_local_code
            upload_to_git
            ;;
        "deploy")
            deploy_to_server
            ;;
        "full")
            check_requirements
            prepare_local_code
            upload_to_git
            deploy_to_server
            ;;
        "help")
            show_usage
            ;;
        *)
            log_error "未知选项: $1"
            show_usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
