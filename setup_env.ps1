# ============================================
# 乳腺超声 AI 诊断系统 - 虚拟环境设置脚本
# 适用于 Windows PowerShell, Python 3.13+
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  乳腺超声 AI 诊断系统 - 环境设置" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 版本
Write-Host "[1/5] 检查 Python 版本..." -ForegroundColor Yellow
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    $pythonVersion = & python --version
    Write-Host "  $pythonVersion"
    
    # 验证版本 >= 3.13
    $versionInfo = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([version]$versionInfo -lt [version]"3.13") {
        Write-Host "错误：需要 Python 3.13 或更高版本，当前版本：$versionInfo" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Python 版本检查通过" -ForegroundColor Green
} catch {
    Write-Host "错误：未找到 Python，请安装 Python 3.13+" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 创建虚拟环境
Write-Host "[2/5] 创建虚拟环境..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "警告：venv 已存在，将删除并重新创建" -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

& python -m venv venv
Write-Host "✓ 虚拟环境创建完成" -ForegroundColor Green
Write-Host ""

# 激活虚拟环境
Write-Host "[3/5] 激活虚拟环境..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ 虚拟环境已激活" -ForegroundColor Green
Write-Host ""

# 升级 pip
Write-Host "[4/5] 升级 pip 和构建工具..." -ForegroundColor Yellow
& python -m pip install --upgrade pip setuptools wheel
Write-Host "✓ pip 升级完成" -ForegroundColor Green
Write-Host ""

# 安装依赖
Write-Host "[5/5] 安装项目依赖..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    & pip install -r requirements.txt
} elseif (Test-Path "pyproject.toml") {
    & pip install -e .
} else {
    Write-Host "错误：未找到 requirements.txt 或 pyproject.toml" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 依赖安装完成" -ForegroundColor Green
Write-Host ""

# 验证安装
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  验证安装" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

& python -c "import fastapi; print(f'✓ FastAPI {fastapi.__version__}')"
& python -c "import torch; print(f'✓ PyTorch {torch.__version__}')"
& python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')"
& python -c "import cv2; print(f'✓ OpenCV {cv2.__version__}')"
Write-Host ""

Write-Host "============================================" -ForegroundColor Green
Write-Host "  环境设置完成!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "后续步骤:" -ForegroundColor Yellow
Write-Host "  1. 激活虚拟环境：.\venv\Scripts\Activate.ps1"
Write-Host "  2. 配置环境变量：copy .env.example .env"
Write-Host "  3. 启动服务：python -m uvicorn app.main:app --reload"
Write-Host ""
Write-Host "退出虚拟环境：deactivate"
Write-Host ""
