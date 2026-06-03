#!/bin/bash
# ============================================
# 乳腺超声 AI 诊断系统 - 虚拟环境设置脚本
# 适用于 Linux/macOS, Python 3.13+
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "  乳腺超声 AI 诊断系统 - 环境设置"
echo "============================================"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}[1/5] 检查 Python 版本...${NC}"
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    # 验证版本 >= 3.13
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$PYTHON_VERSION" < "3.13" ]]; then
        echo -e "${RED}错误：需要 Python 3.13 或更高版本，当前版本：$PYTHON_VERSION${NC}"
        exit 1
    fi
else
    echo -e "${RED}错误：未找到 Python，请安装 Python 3.13+${NC}"
    exit 1
fi

$PYTHON_CMD --version
echo -e "${GREEN}✓ Python 版本检查通过${NC}"
echo ""

# 创建虚拟环境
echo -e "${YELLOW}[2/5] 创建虚拟环境...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}警告：venv 已存在，将删除并重新创建${NC}"
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
echo -e "${GREEN}✓ 虚拟环境创建完成${NC}"
echo ""

# 激活虚拟环境
echo -e "${YELLOW}[3/5] 激活虚拟环境...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 升级 pip
echo -e "${YELLOW}[4/5] 升级 pip 和构建工具...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip 升级完成${NC}"
echo ""

# 安装依赖
echo -e "${YELLOW}[5/5] 安装项目依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
    pip install -e .
else
    echo -e "${RED}错误：未找到 requirements.txt 或 pyproject.toml${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

# 验证安装
echo "============================================"
echo "  验证安装"
echo "============================================"
echo ""

python -c "import fastapi; print(f'✓ FastAPI {fastapi.__version__}')"
python -c "import torch; print(f'✓ PyTorch {torch.__version__}')"
python -c "import numpy; print(f'✓ NumPy {numpy.__version__}')"
python -c "import cv2; print(f'✓ OpenCV {cv2.__version__}')"
echo ""

echo "============================================"
echo -e "${GREEN}  环境设置完成!${NC}"
echo "============================================"
echo ""
echo "后续步骤:"
echo "  1. 激活虚拟环境：source venv/bin/activate"
echo "  2. 配置环境变量：cp .env.example .env"
echo "  3. 启动服务：python -m uvicorn app.main:app --reload"
echo ""
echo "退出虚拟环境：deactivate"
echo ""
