#!/bin/bash
# ============================================
# 快速启动脚本
# ============================================

set -e

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    ./setup_env.sh
fi

# 激活虚拟环境
source venv/bin/activate

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "创建环境变量配置..."
    cp .env.example .env 2>/dev/null || echo "请手动创建 .env 文件"
fi

# 启动服务
echo "启动乳腺超声 AI 诊断系统..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
