#!/bin/bash
set -e

# ============================================
# Kimi K2.5 微调项目快速启动脚本
# ============================================

echo "=============================================="
echo "Kimi K2.5 超声前问诊微调项目"
echo "=============================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo "1️⃣  检查 Python 环境"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 Python3${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   ✅ Python $PYTHON_VERSION"

# 检查 GPU
echo ""
echo "2️⃣  检查 GPU 资源"
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1)
    echo "   ✅ GPU: $GPU_INFO"
else
    echo -e "${YELLOW}⚠️  未检测到 GPU，将使用规则引擎模式${NC}"
fi

# 安装依赖
echo ""
echo "3️⃣  安装 Python 依赖"
cd "$(dirname "$0")"

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 错误：requirements.txt 不存在${NC}"
    exit 1
fi

pip3 install -r requirements.txt -q
echo "   ✅ 依赖安装完成"

# 下载模型（可选）
echo ""
echo "4️⃣  模型下载（可选步骤）"
read -p "是否需要下载 Kimi K2.5 模型？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if ! command -v huggingface-cli &> /dev/null; then
        echo "   安装 huggingface_hub..."
        pip3 install huggingface_hub -q
    fi
    
    MODEL_DIR="${MODEL_DIR:-/workspace/models/kimi-k2-5-1.8bit}"
    echo "   下载目录：$MODEL_DIR"
    
    if [ ! -d "$MODEL_DIR" ]; then
        huggingface-cli download moonshot/Kimi-K2.5 \
            --revision unsloth-1.8bit \
            --local-dir "$MODEL_DIR"
        echo "   ✅ 模型下载完成"
    else
        echo "   ✅ 模型已存在"
    fi
fi

# 生成训练数据
echo ""
echo "5️⃣  检查训练数据"
DATA_FILE="data/training_conversations.jsonl"
if [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}❌ 错误：训练数据文件不存在${NC}"
    exit 1
fi

SAMPLE_COUNT=$(wc -l < "$DATA_FILE")
echo "   ✅ 训练数据：$SAMPLE_COUNT 条对话"

# 启动训练（可选）
echo ""
echo "6️⃣  开始训练（可选步骤）"
read -p "是否立即开始微调训练？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   启动训练脚本..."
    python3 scripts/finetune_kimi_k2.py
else
    echo "   跳过训练步骤"
fi

# 启动后端服务（可选）
echo ""
echo "7️⃣  启动后端服务（可选步骤）"
read -p "是否启动后端 API 服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   启动后端服务..."
    cd ../backend
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "   ✅ 后端服务已启动 (PID: $BACKEND_PID)"
fi

# 启动前端服务（可选）
echo ""
echo "8️⃣  启动前端服务（可选步骤）"
read -p "是否启动前端开发服务器？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   启动前端服务..."
    cd ../frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "   ✅ 前端服务已启动 (PID: $FRONTEND_PID)"
fi

# 完成
echo ""
echo "=============================================="
echo -e "${GREEN}✅ 所有步骤完成!${NC}"
echo "=============================================="
echo ""
echo "📚 下一步:"
echo "   1. 访问 http://localhost:3000/inquiry 体验问诊功能"
echo "   2. 查看 API 文档：http://localhost:8000/api/docs"
echo "   3. 阅读详细文档：README.md"
echo ""

# 清理函数
cleanup() {
    echo ""
    echo "正在关闭服务..."
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    echo "再见！"
}

trap cleanup EXIT
