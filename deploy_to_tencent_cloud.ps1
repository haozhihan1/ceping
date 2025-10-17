# 员工能力测评系统 - PowerShell 部署脚本
# 适用于腾讯云CentOS服务器部署

param(
    [string]$ServerIP = "124.223.40.219",
    [string]$ServerUser = "root",
    [string]$GitRepoUrl = "https://github.com/haozhihan1/ceping.git"
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$ForegroundColor = "White"
    )
    Write-Host $Message -ForegroundColor $ForegroundColor
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" -ForegroundColor "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" -ForegroundColor "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" -ForegroundColor "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" -ForegroundColor "Red"
}

# 检查必要工具
function Test-Requirements {
    Write-Info "检查部署环境..."
    
    $requirements = @("git", "ssh")
    $missing = @()
    
    foreach ($req in $requirements) {
        if (-not (Get-Command $req -ErrorAction SilentlyContinue)) {
            $missing += $req
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Error "缺少必要工具: $($missing -join ', ')"
        Write-Info "请安装Git for Windows: https://git-scm.com/download/win"
        return $false
    }
    
    Write-Success "环境检查通过"
    return $true
}

# 准备本地代码
function Invoke-PrepareLocalCode {
    Write-Info "准备本地代码..."
    
    # 检查Git仓库状态
    if (-not (Test-Path ".git")) {
        Write-Info "初始化Git仓库..."
        git init
        git branch -M main
    }
    
    # 检查Git状态
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Info "提交代码更改..."
        git add .
        git commit -m "准备生产环境部署 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    }
    
    Write-Success "本地代码准备完成"
}

# 上传代码到Git仓库
function Invoke-UploadToGit {
    Write-Info "上传代码到Git仓库: $GitRepoUrl"
    
    # 设置远程仓库
    $currentRemote = git remote get-url origin 2>$null
    if ($LASTEXITCODE -ne 0) {
        git remote add origin $GitRepoUrl
    } else {
        git remote set-url origin $GitRepoUrl
    }
    
    # 推送代码
    Write-Info "推送代码到远程仓库..."
    git push -u origin main --force
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "代码已成功上传到Git仓库"
    } else {
        Write-Error "代码推送失败，请检查网络连接和Git凭据"
        return $false
    }
    
    return $true
}

# 生成服务器部署脚本
function New-ServerDeployScript {
    $deployScript = @'
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

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 更新系统
    yum update -y
    
    # 安装基础工具
    yum install -y wget curl git unzip vim python3 python3-pip python3-devel
    
    # 安装Web服务
    yum install -y nginx supervisor
    systemctl enable nginx supervisord
    
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
    
    # 升级pip并安装依赖
    sudo -u www bash -c "source venv/bin/activate && pip install --upgrade pip"
    
    log_success "Python环境配置完成"
}

# 克隆项目代码
clone_project() {
    log_info "克隆项目代码..."
    
    cd /home/www
    
    if [ -d "flask_project/.git" ]; then
        log_info "更新现有项目..."
        cd flask_project
        sudo -u www git pull origin main
    else
        log_info "首次克隆项目..."
        if [ -d "flask_project" ]; then
            mv flask_project flask_project_backup_$(date +%Y%m%d)
        fi
        sudo -u www git clone "GIT_REPO_URL_PLACEHOLDER" flask_project
        cd flask_project
    fi
    
    chown -R www:www /home/www/flask_project
    log_success "项目代码克隆完成"
}

# 安装项目依赖
install_project_deps() {
    log_info "安装项目依赖..."
    
    cd /home/www/flask_project
    sudo -u www bash -c "source venv/bin/activate && pip install -r requirements.txt"
    
    log_success "项目依赖安装完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    cd /home/www/flask_project
    
    if [ -f "database_migration.sql" ]; then
        log_info "导入数据库迁移文件..."
        sudo -u www sqlite3 data/new_questions.db < database_migration.sql
        log_success "数据库迁移完成"
    else
        log_info "初始化新数据库..."
        sudo -u www bash -c "source venv/bin/activate && python init_database.py"
        mv new_questions.db data/ 2>/dev/null || true
    fi
    
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
            log_warning "请编辑 .env 文件设置正确的密钥"
        else
            log_error "未找到环境配置文件"
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
    systemctl restart nginx supervisord
    supervisorctl reread && supervisorctl update
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
        log_error "应用健康检查失败"
        supervisorctl status employee_assessment
        exit 1
    fi
}

# 显示结果
show_result() {
    echo "====================================="
    echo "部署完成！"
    echo "====================================="
    echo "访问地址: http://124.223.40.219"
    echo "管理后台: http://124.223.40.219/manage"
    echo "健康检查: http://124.223.40.219/health"
    echo ""
    echo "重要提醒:"
    echo "1. 请编辑 /home/www/flask_project/.env 文件"
    echo "2. 设置正确的 SECRET_KEY 和 DEEPSEEK_API_KEY"
    echo "3. 修改默认管理员密码"
    echo "====================================="
}

# 主函数
main() {
    log_info "开始自动部署员工能力测评系统..."
    
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
}

# 执行部署
main
'@

    # 替换Git仓库地址占位符
    $deployScript = $deployScript -replace "GIT_REPO_URL_PLACEHOLDER", $GitRepoUrl
    
    return $deployScript
}

# 部署到服务器
function Invoke-DeployToServer {
    Write-Info "开始部署到腾讯云服务器..."
    
    # 生成部署脚本
    $deployScript = New-ServerDeployScript
    $tempScriptPath = [System.IO.Path]::GetTempFileName() + ".sh"
    
    # 写入脚本文件（使用UTF-8无BOM编码）
    $utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
    [System.IO.File]::WriteAllText($tempScriptPath, $deployScript, $utf8NoBomEncoding)
    
    try {
        Write-Info "上传部署脚本到服务器..."
        scp $tempScriptPath "${ServerUser}@${ServerIP}:/tmp/deploy.sh"
        
        Write-Info "在服务器上执行部署..."
        ssh "${ServerUser}@${ServerIP}" "chmod +x /tmp/deploy.sh && /tmp/deploy.sh"
        
        Write-Success "部署完成！"
        Write-Info "访问地址: http://$ServerIP"
        
    } catch {
        Write-Error "部署失败: $($_.Exception.Message)"
        return $false
    } finally {
        # 清理临时文件
        if (Test-Path $tempScriptPath) {
            Remove-Item $tempScriptPath -Force
        }
    }
    
    return $true
}

# 主函数
function Main {
    param([string]$Action = "full")
    
    Write-Info "========================================"
    Write-Info "员工能力测评系统 - 腾讯云部署脚本"
    Write-Info "========================================"
    Write-Info "服务器: $ServerIP"
    Write-Info "Git仓库: $GitRepoUrl"
    Write-Info "========================================"
    
    switch ($Action.ToLower()) {
        "check" {
            Test-Requirements
        }
        "prepare" {
            if (Test-Requirements) {
                Invoke-PrepareLocalCode
            }
        }
        "upload" {
            if (Test-Requirements) {
                Invoke-PrepareLocalCode
                Invoke-UploadToGit
            }
        }
        "deploy" {
            Invoke-DeployToServer
        }
        "full" {
            if (-not (Test-Requirements)) {
                return
            }
            
            Invoke-PrepareLocalCode
            
            if (-not (Invoke-UploadToGit)) {
                return
            }
            
            Invoke-DeployToServer
        }
        default {
            Write-Error "未知操作: $Action"
            Write-Info "可用操作: check, prepare, upload, deploy, full"
        }
    }
}

# 执行主函数
Main -Action "full"
