#!/bin/bash
set -e

echo "============================================"
echo "Breast AI System - Docker 部署"
echo "============================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="breast-ai"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  建议使用 docker compose (v2)${NC}"
fi

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo ""
echo "Docker 版本:"
docker --version

echo ""
echo "Docker Compose 版本:"
docker-compose --version || docker compose version

echo ""
echo "============================================"
echo "启动服务"
echo "============================================"

# 构建并启动
if command -v docker-compose &> /dev/null; then
    docker-compose -p $PROJECT_NAME -f $COMPOSE_FILE up -d --build
else
    docker compose -p $PROJECT_NAME -f $COMPOSE_FILE up -d --build
fi

echo ""
echo -e "${GREEN}✅ 服务启动完成${NC}"
echo ""
echo "服务列表:"
if command -v docker-compose &> /dev/null; then
    docker-compose -p $PROJECT_NAME ps
else
    docker compose -p $PROJECT_NAME ps
fi

echo ""
echo "============================================"
echo "访问地址"
echo "============================================"
echo "前端：http://localhost:3000"
echo "后端：http://localhost:8000"
echo "API 文档：http://localhost:8000/api/docs"
echo ""
echo "============================================"
echo "常用命令"
echo "============================================"
echo "查看日志：      docker-compose -p $PROJECT_NAME logs -f"
echo "停止服务：      docker-compose -p $PROJECT_NAME down"
echo "重启服务：      docker-compose -p $PROJECT_NAME restart"
echo "重新构建：      docker-compose -p $PROJECT_NAME build"
echo "进入后端容器：docker-compose -p $PROJECT_NAME exec backend sh"
echo "进入前端容器：docker-compose -p $PROJECT_NAME exec frontend sh"
echo ""
