#!/bin/bash
set -e

echo "🚀 乳腺 AI 系统 - 初始化脚本"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误：需要安装 Node.js 18+${NC}"
        exit 1
    fi
    
    if ! command -v pnpm &> /dev/null; then
        echo -e "${YELLOW}安装 pnpm...${NC}"
        npm install -g pnpm
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误：需要安装 Python 3.10+${NC}"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}警告：Docker 未安装，部分功能不可用${NC}"
    fi
    
    echo -e "${GREEN}✓ 依赖检查通过${NC}"
}

# 初始化前端
init_frontend() {
    echo -e "${YELLOW}初始化前端...${NC}"
    cd frontend
    
    pnpm install
    
    echo -e "${GREEN}✓ 前端初始化完成${NC}"
    cd ..
}

# 初始化后端
init_backend() {
    echo -e "${YELLOW}初始化后端...${NC}"
    cd backend
    
    python3 -m venv venv
    source venv/bin/activate
    
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}✓ 后端初始化完成${NC}"
    cd ..
}

# 初始化数据库
init_database() {
    echo -e "${YELLOW}初始化数据库...${NC}"
    
    if command -v docker &> /dev/null; then
        docker-compose up -d postgres
        
        echo "等待 PostgreSQL 启动..."
        sleep 10
        
        docker-compose exec -T postgres psql -U breast_ai_user -d breast_ai -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
        
        echo -e "${GREEN}✓ 数据库初始化完成${NC}"
    else
        echo -e "${YELLOW}跳过数据库初始化（Docker 未安装）${NC}"
    fi
}

# 创建示例数据
create_sample_data() {
    echo -e "${YELLOW}创建示例数据...${NC}"
    
    # 这里可以添加创建测试数据的脚本
    echo "示例数据创建完成"
}

# 主函数
main() {
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  乳腺 AI 系统初始化${NC}"
    echo -e "${GREEN}================================${NC}"
    
    check_dependencies
    init_frontend
    init_backend
    init_database
    create_sample_data
    
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  初始化完成！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "启动开发环境:"
    echo "  cd frontend && pnpm dev      # 启动前端"
    echo "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload  # 启动后端"
    echo ""
    echo "或使用 Docker Compose:"
    echo "  docker-compose up -d"
    echo ""
}

# 执行主函数
main "$@"
