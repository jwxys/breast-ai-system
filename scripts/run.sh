#!/bin/bash

# =======================================
# 乳腺 AI 诊断系统 - 启动脚本
# =======================================

echo "========================================"
echo "  🏥 乳腺 AI 辅助诊断系统"
echo "  Version 3.0.0"
echo "========================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo "⚠️  警告：未找到 Node.js，前端可能无法启动"
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告：.env 文件不存在"
    echo "正在从 .env.example 创建..."
    cp .env.example .env 2>/dev/null || echo "❌ .env.example 不存在，请手动创建 .env 文件"
fi

# 检查依赖
echo "📦 检查 Python 依赖..."
pip3 list | grep -q "fastapi" || echo "⚠️  FastAPI 未安装，请运行：pip install -r requirements.txt"

# 启动后端服务 (后台)
echo "🚀 启动后端服务..."
cd /workspace/breast-ai-system
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 检查后端状态
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能启动失败，请查看 backend.log"
fi

# 启动前端服务 (如果有 Node.js)
if command -v node &> /dev/null; then
    echo "🚀 启动前端服务..."
    cd /workspace/breast-ai-system/frontend
    nohup npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
else
    echo "⚠️  跳过前端启动 (Node.js 未安装)"
fi

echo ""
echo "========================================"
echo "  ✅ 服务启动完成!"
echo "========================================"
echo ""
echo "访问地址:"
echo "  前端：http://localhost:3000"
echo "  API 文档：http://localhost:8000/api/docs"
echo "  健康检查：http://localhost:8000/health"
echo ""
echo "停止服务:"
echo "  kill $BACKEND_PID  # 停止后端"
echo "  kill $FRONTEND_PID 2>/dev/null  # 停止前端"
echo ""

# 保持脚本运行
wait
