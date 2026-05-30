.PHONY: help dev build test lint clean

# 默认目标
help:
	@echo "乳腺 AI 系统 - Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make dev        - 启动开发环境"
	@echo "  make build      - 构建生产版本"
	@echo "  make test       - 运行测试"
	@echo "  make lint       - 代码检查"
	@echo "  make clean      - 清理构建文件"
	@echo "  make docker-up  - 启动 Docker 环境"
	@echo "  make docker-down- 停止 Docker 环境"
	@echo ""

# 开发环境
dev:
	@echo "启动开发环境..."
	@pnpm dev

# 构建
build:
	@echo "构建前端..."
	@cd frontend && pnpm build
	@echo "构建后端..."
	@cd backend && python -m compileall .

# 测试
test:
	@echo "运行前端测试..."
	@cd frontend && pnpm test --run
	@echo "运行后端测试..."
	@cd backend && pytest

# 代码检查
lint:
	@echo "检查前端代码..."
	@cd frontend && pnpm lint
	@echo "检查后端代码..."
	@cd backend && flake8 .

# 清理
clean:
	@echo "清理构建文件..."
	@rm -rf frontend/dist
	@rm -rf frontend/node_modules
	@rm -rf backend/__pycache__
	@rm -rf backend/**/__pycache__
	@rm -rf backend/*.egg-info
	@echo "清理完成"

# Docker 环境
docker-up:
	@echo "启动 Docker 环境..."
	@docker-compose up -d
	@echo "服务已启动:"
	@echo "  前端：http://localhost:3000"
	@echo "  后端：http://localhost:8000"
	@echo "  API 文档：http://localhost:8000/docs"

docker-down:
	@echo "停止 Docker 环境..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f

docker-restart:
	@docker-compose restart

# 数据库迁移
db-migrate:
	@echo "执行数据库迁移..."
	@cd backend && alembic upgrade head

# 数据库初始化
db-init:
	@echo "初始化数据库..."
	@docker-compose exec -T backend python scripts/init_db.py

# 初始化
init: docker-up db-init
	@echo "初始化完成"
