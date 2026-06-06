# 安装指南

## 系统要求

- Python 3.11+
- Node.js 18+
- Git

## 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/jwxys/breast-ai-system.git
cd breast-ai-system
```

### 2. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 配置环境变量

```bash
# 复制环境配置示例
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 5. 启动服务

```bash
# 使用启动脚本
./scripts/run.sh

# 或手动启动
# 终端 1: 后端
python -m uvicorn app.main:app --reload --port 8005

# 终端 2: 前端  
cd frontend && npm run dev
```

## 访问服务

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:3000 |
| 后端 API | http://localhost:8005 |
| API 文档 | http://localhost:8005/api/docs |

## 验证安装

```bash
# 测试后端 API
curl http://localhost:8005/api/health

# 预期输出: {"status": "ok"}
```

---

**问题？** 查看 [开发指南](DEVELOPMENT.md)
